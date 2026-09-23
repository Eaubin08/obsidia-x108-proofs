"""
apps/obsidia_api/brody_repair_reasoning.py
==========================================
BRODY — provider de raisonnement de réparation (route PRINCIPALE).

Ce module donne à Brody la seule chose qui manquait au cycle : la capacité de
consommer un RepairRequest et d'en tirer soit un RepairProposal testable, soit
un état explicite disant pourquoi il n'y en a pas.

CE QUE BRODY SAIT FAIRE ICI, HONNÊTEMENT
    1. Diagnostiquer réellement : parse AST de chaque cible, inventaire des
       symboles définis / importés / utilisés, corrélation avec les signaux
       d'erreur portés par le RepairRequest.
    2. Décider si l'information est suffisante. Si le défaut fonctionnel n'est
       pas défini, il retourne NEEDS_DIAGNOSTIC_CONTEXT et dit précisément ce
       qui manque. Il n'invente rien.
    3. Réparer une classe de défaut mécaniquement décidable :
       UNRESOLVED_NAME — un symbole signalé par un NameError observé, confirmé
       absent par l'AST, et exporté par un module du repo → insertion de
       l'import manquant.

CE QUE BRODY NE FAIT PAS
    Réparer sémantiquement du code arbitraire. Aucun moteur du runtime n'en est
    capable, et le prétendre produirait de faux correctifs. Pour tout défaut
    hors de la classe traitée, le statut est NEEDS_EXTERNAL_ENGINE — le
    fallback EXTERNAL_REASONING reste déclaré et non automatique.

Aucune logique spécifique à un fichier, un domaine ou un problème : l'analyse
est purement structurelle.

FRONTIÈRES : decision_authority=KX108_ONLY, emits_act=False,
kernel_mutation=False, memory_write=False, auto_apply=False.
"""
from __future__ import annotations

import ast
import builtins
import hashlib
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from periphery.agents.obsidure_reasoning_provider import (  # noqa: E402
    DiagnosisStatus,
    ReasoningProvider,
    RepairDiagnosis,
)
from periphery.agents.obsidure_repair_contract import (  # noqa: E402
    ALLOWED_REPAIR_PREFIXES,
    RepairCandidateFile,
    RepairProposal,
    RepairRequest,
    is_protected_repair_path,
)

__all__ = [
    "BrodyReasoningProvider",
    "analyze_module_symbols",
    "extract_unresolved_names_from_errors",
    "ModuleAnalysis",
]

_BUILTIN_NAMES: Set[str] = set(dir(builtins))

# Un NameError observé nomme explicitement le symbole manquant. C'est le seul
# déclencheur accepté : on répare un défaut CONSTATÉ, jamais un défaut supposé.
_NAME_ERROR_PATTERNS: Tuple[str, ...] = (
    r"NameError:\s*name\s*['\"](?P<name>\w+)['\"]\s*is not defined",
    r"NameError:\s*global name\s*['\"](?P<name>\w+)['\"]\s*is not defined",
    r"\bundefined name\s*['\"](?P<name>\w+)['\"]",
)

_MAX_MODULES_SCANNED = 4000


@dataclass
class ModuleAnalysis:
    """Inventaire structurel d'un module Python."""

    path: str = ""
    parsed: bool = False
    syntax_error: str = ""
    defined: Set[str] = None          # type: ignore[assignment]
    imported: Set[str] = None         # type: ignore[assignment]
    used: Set[str] = None             # type: ignore[assignment]
    import_anchor_line: int = 0       # ligne (1-based) après laquelle insérer un import

    def __post_init__(self) -> None:
        self.defined = self.defined or set()
        self.imported = self.imported or set()
        self.used = self.used or set()

    @property
    def unresolved(self) -> Set[str]:
        """Noms utilisés mais ni définis, ni importés, ni builtins."""
        return {
            n for n in self.used
            if n not in self.defined and n not in self.imported and n not in _BUILTIN_NAMES
        }


def analyze_module_symbols(source: str, path: str = "") -> ModuleAnalysis:
    """
    Inventorie les symboles d'un module par AST.

    Purement structurel : aucune heuristique de nommage, aucun motif métier.
    """
    analysis = ModuleAnalysis(path=path)

    try:
        tree = ast.parse(source, filename=path or "<repair-target>")
    except SyntaxError as exc:
        analysis.syntax_error = f"line {exc.lineno}: {exc.msg}"
        return analysis
    except Exception as exc:  # pragma: no cover — parse non-syntaxique
        analysis.syntax_error = f"{type(exc).__name__}: {exc}"
        return analysis

    analysis.parsed = True
    anchor = 0

    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            anchor = max(anchor, getattr(node, "end_lineno", node.lineno) or node.lineno)
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) \
                and isinstance(node.value.value, str) and anchor == 0:
            # docstring de module
            anchor = max(anchor, getattr(node, "end_lineno", node.lineno) or node.lineno)

    analysis.import_anchor_line = anchor

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            analysis.defined.add(node.name)
            for arg in getattr(getattr(node, "args", None), "args", []) or []:
                analysis.defined.add(arg.arg)
            for arg in getattr(getattr(node, "args", None), "kwonlyargs", []) or []:
                analysis.defined.add(arg.arg)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                analysis.imported.add(alias.asname or alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                analysis.imported.add(alias.asname or alias.name)
        elif isinstance(node, ast.Name):
            if isinstance(node.ctx, ast.Store):
                analysis.defined.add(node.id)
            else:
                analysis.used.add(node.id)
        elif isinstance(node, ast.arg):
            analysis.defined.add(node.arg)
        elif isinstance(node, (ast.ExceptHandler,)) and node.name:
            analysis.defined.add(node.name)
        elif isinstance(node, ast.Global):
            analysis.defined.update(node.names)

    return analysis


def extract_unresolved_names_from_errors(request: RepairRequest) -> Set[str]:
    """
    Extrait les noms explicitement signalés comme non définis par les erreurs
    portées par le RepairRequest.

    Sources inspectées : raw_details, first_error_line, build_stderr de chaque
    ErrorContext, plus le résumé. On ne lit PAS l'objectif : une phrase
    d'intention n'est pas une observation d'échec.
    """
    names: Set[str] = set()
    blobs: List[str] = [request.summary or ""]
    for ctx in request.error_contexts:
        blobs.extend([ctx.raw_details or "", ctx.first_error_line or "", ctx.build_stderr or ""])

    for blob in blobs:
        for pattern in _NAME_ERROR_PATTERNS:
            for match in re.finditer(pattern, blob):
                names.add(match.group("name"))
    return names


def _iter_repo_modules(repo_root: Path) -> List[Path]:
    """Modules Python candidats à l'export d'un symbole, dans les zones permises."""
    modules: List[Path] = []
    for prefix in ALLOWED_REPAIR_PREFIXES:
        base = repo_root / prefix.rstrip("/")
        if not base.is_dir():
            continue
        for f in base.rglob("*.py"):
            rel = f.relative_to(repo_root).as_posix()
            if is_protected_repair_path(rel) or "__pycache__" in rel:
                continue
            modules.append(f)
            if len(modules) >= _MAX_MODULES_SCANNED:
                return modules
    return modules


def _module_dotted_path(repo_root: Path, file_path: Path) -> str:
    rel = file_path.relative_to(repo_root).as_posix()
    return rel[:-3].replace("/", ".")


def _find_symbol_source(
    name: str,
    repo_root: Path,
    exclude: Optional[Path] = None,
) -> Optional[str]:
    """
    Cherche un module du repo qui définit `name` au niveau top-level.

    Retourne le chemin pointé (`periphery.math_core.x`) ou None. Si plusieurs
    modules le définissent, on retourne None : l'ambiguïté n'est pas résolue
    par devinette.
    """
    matches: List[str] = []
    for f in _iter_repo_modules(repo_root):
        if exclude and f.resolve() == exclude.resolve():
            continue
        try:
            src = f.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        if name not in src:
            continue  # pré-filtre bon marché
        try:
            tree = ast.parse(src, filename=str(f))
        except Exception:
            continue
        for node in tree.body:
            hit = (
                (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                 and node.name == name)
                or (isinstance(node, ast.Assign) and any(
                    isinstance(t, ast.Name) and t.id == name for t in node.targets))
            )
            if hit:
                matches.append(_module_dotted_path(repo_root, f))
                break
        if len(matches) > 1:
            return None
    return matches[0] if len(matches) == 1 else None


class BrodyReasoningProvider(ReasoningProvider):
    """
    Route principale du cycle de réparation.

    Diagnostique toujours. Ne propose que ce qu'il peut justifier.
    """

    name = "BRODY"

    # ── Diagnostic ────────────────────────────────────────────────────────

    def diagnose(
        self,
        request: RepairRequest,
        repo_root: Optional[Path] = None,
    ) -> RepairDiagnosis:
        root = Path(repo_root) if repo_root else _REPO_ROOT

        diagnosis = RepairDiagnosis(
            provider=self.name,
            request_id=request.request_id,
            inspected_targets=list(request.repo_targets),
        )

        sources = self._collect_sources(request, root)

        if not sources:
            diagnosis.status = DiagnosisStatus.NEEDS_DIAGNOSTIC_CONTEXT
            diagnosis.defect_class = "NO_INSPECTABLE_TARGET"
            diagnosis.missing_information = [
                "Aucun fichier source inspectable (repo_targets vide ou cibles introuvables).",
                "Fournir le ou les chemins de fichiers concernés par le défaut.",
            ]
            diagnosis.notes = "Rien à analyser — aucune réparation ne peut être justifiée."
            return diagnosis

        analyses: Dict[str, ModuleAnalysis] = {}
        for rel, src in sources.items():
            if not rel.endswith(".py"):
                continue
            analyses[rel] = analyze_module_symbols(src, rel)

        # ── Défaut structurel dur : le fichier ne parse pas ────────────────
        broken = {rel: a for rel, a in analyses.items() if a.syntax_error}
        for rel, a in broken.items():
            diagnosis.findings.append({
                "type": "SYNTAX_ERROR",
                "path": rel,
                "details": a.syntax_error,
            })
        if broken:
            diagnosis.status = DiagnosisStatus.NEEDS_EXTERNAL_ENGINE
            diagnosis.defect_class = "SYNTAX_ERROR"
            diagnosis.confidence = "HIGH"
            diagnosis.missing_information = [
                "Une erreur de syntaxe est localisée mais sa correction n'est pas "
                "mécaniquement décidable — elle demande un moteur de raisonnement.",
            ]
            diagnosis.notes = (
                "Le défaut est identifié avec certitude ; la réparation dépasse "
                "la capacité de Brody."
            )
            return diagnosis

        # ── Noms non résolus, CORROBORÉS par une erreur observée ──────────
        reported = extract_unresolved_names_from_errors(request)
        actionable: List[Dict[str, Any]] = []

        for rel, a in analyses.items():
            unresolved = a.unresolved
            for name in sorted(reported & unresolved):
                target_file = root / rel
                origin = _find_symbol_source(
                    name, root, exclude=target_file if target_file.is_file() else None
                )
                finding = {
                    "type": "UNRESOLVED_NAME",
                    "path": rel,
                    "name": name,
                    "resolved_from": origin or "",
                    # L'ancre voyage AVEC le finding : propose() relit
                    # diagnosis.findings et ne dispose pas de l'analyse AST.
                    "anchor": a.import_anchor_line,
                }
                diagnosis.findings.append(finding)
                if origin:
                    actionable.append(finding)

        if actionable:
            diagnosis.status = DiagnosisStatus.PROPOSAL_READY
            diagnosis.defect_class = "UNRESOLVED_NAME"
            diagnosis.confidence = "HIGH"
            diagnosis.notes = (
                f"{len(actionable)} symbole(s) non résolu(s), signalé(s) par une erreur "
                "observée et exporté(s) par un module du repo. Réparation par import."
            )
            return diagnosis

        # ── Défaut signalé mais non traitable ─────────────────────────────
        if reported:
            diagnosis.status = DiagnosisStatus.NEEDS_EXTERNAL_ENGINE
            diagnosis.defect_class = "UNRESOLVED_NAME_UNRESOLVABLE"
            diagnosis.confidence = "MEDIUM"
            diagnosis.missing_information = [
                f"Symbole(s) signalé(s) : {sorted(reported)}.",
                "Aucun module du repo ne les exporte de façon univoque — "
                "la provenance doit être précisée.",
            ]
            return diagnosis

        # ── Aucun défaut fonctionnel défini → on refuse d'inventer ────────
        diagnosis.status = DiagnosisStatus.NEEDS_DIAGNOSTIC_CONTEXT
        diagnosis.defect_class = "UNDETERMINED"
        diagnosis.confidence = "NONE"
        diagnosis.missing_information = self._missing_context(request, analyses)
        diagnosis.notes = (
            "Les cibles sont lisibles et parsent correctement, mais aucun défaut "
            "fonctionnel concret n'est décrit. Aucune réparation ne sera inventée."
        )
        return diagnosis

    # ── Proposition ───────────────────────────────────────────────────────

    def propose(
        self,
        request: RepairRequest,
        diagnosis: RepairDiagnosis,
        repo_root: Optional[Path] = None,
    ) -> Optional[RepairProposal]:
        if not diagnosis.can_propose or diagnosis.defect_class != "UNRESOLVED_NAME":
            return None

        root = Path(repo_root) if repo_root else _REPO_ROOT
        sources = self._collect_sources(request, root)

        # Regrouper les imports à insérer par fichier.
        by_path: Dict[str, List[Dict[str, Any]]] = {}
        for f in diagnosis.findings:
            if f.get("type") == "UNRESOLVED_NAME" and f.get("resolved_from"):
                by_path.setdefault(f["path"], []).append(f)

        candidates: List[RepairCandidateFile] = []
        for rel, findings in by_path.items():
            src = sources.get(rel)
            if src is None:
                continue
            patched = self._insert_imports(src, findings, rel)
            if patched is None or patched == src:
                continue

            base_file = root / rel
            candidates.append(RepairCandidateFile(
                path=rel,
                full_content=patched,
                change_kind="MODIFY" if base_file.is_file() else "CREATE",
                base_sha256=(
                    hashlib.sha256(base_file.read_bytes()).hexdigest()
                    if base_file.is_file() else ""
                ),
                rationale=(
                    "Import manquant pour "
                    + ", ".join(f"{f['name']} (depuis {f['resolved_from']})" for f in findings)
                ),
            ))

        if not candidates:
            # Rien de concret à proposer : on préfère None à une proposition creuse.
            return None

        return RepairProposal(
            request_id=request.request_id,
            engine=self.name,
            rationale=(
                "Réparation structurelle : insertion des imports manquants pour des "
                "symboles signalés par une erreur observée et localisés dans le repo. "
                "Aucune logique métier n'a été modifiée."
            ),
            candidate_files=candidates,
            tests_to_run=list(request.tests_hint),
            confidence=diagnosis.confidence,
        )

    # ── Internes ──────────────────────────────────────────────────────────

    @staticmethod
    def _collect_sources(request: RepairRequest, root: Path) -> Dict[str, str]:
        """
        Sources à analyser : les extraits joints au RepairRequest d'abord (ils
        représentent l'état au moment de l'échec), le disque en complément.
        """
        sources: Dict[str, str] = {}
        for rel, excerpt in (request.target_excerpts or {}).items():
            if excerpt:
                sources[rel] = excerpt
        for rel in request.repo_targets:
            if rel in sources:
                continue
            f = root / rel
            if f.is_file():
                try:
                    sources[rel] = f.read_text(encoding="utf-8", errors="replace")
                except Exception:
                    continue
        return sources

    @staticmethod
    def _missing_context(
        request: RepairRequest,
        analyses: Dict[str, ModuleAnalysis],
    ) -> List[str]:
        """Dit précisément ce qu'il faut fournir pour débloquer le diagnostic."""
        missing: List[str] = []
        if not request.error_contexts:
            missing.append(
                "Aucun contexte d'erreur : fournir une trace, un test en échec, "
                "une sortie de build ou un comportement attendu vs observé."
            )
        else:
            kinds = sorted({c.error_type for c in request.error_contexts})
            missing.append(
                f"Les contextes d'erreur présents ({kinds}) décrivent l'incapacité "
                "de la route interne, pas un défaut fonctionnel du code cible."
            )
        if not request.tests_hint:
            missing.append(
                "Aucun test de référence : fournir un test qui échoue et devra passer."
            )
        missing.append(
            "Décrire le comportement attendu, ou fournir une entrée reproduisant le défaut."
        )
        for rel, a in analyses.items():
            if a.parsed and not a.unresolved:
                missing.append(f"'{rel}' est syntaxiquement valide et sans symbole non résolu.")
        return missing

    @staticmethod
    def _insert_imports(
        source: str,
        findings: List[Dict[str, Any]],
        rel: str,
    ) -> Optional[str]:
        """
        Insère les imports manquants après le dernier import top-level.

        Retourne None si le résultat ne parse pas — on ne propose jamais un
        fichier cassé.
        """
        lines = source.splitlines(keepends=True)
        anchor = max((int(f.get("anchor") or 0) for f in findings), default=0)
        anchor = max(0, min(anchor, len(lines)))

        by_module: Dict[str, Set[str]] = {}
        for f in findings:
            by_module.setdefault(str(f["resolved_from"]), set()).add(str(f["name"]))

        new_lines = [
            f"from {module} import {', '.join(sorted(names))}\n"
            for module, names in sorted(by_module.items())
        ]
        if not new_lines:
            return None

        patched = "".join(lines[:anchor] + new_lines + lines[anchor:])
        # compile(..., "exec") et non ast.parse : seul le premier valide les
        # contraintes de placement, notamment `from __future__ import ...` qui
        # doit rester en tête. ast.parse laisse passer un fichier non exécutable.
        try:
            compile(patched, rel or "<repair-candidate>", "exec", dont_inherit=True)
        except SyntaxError:
            return None
        return patched
