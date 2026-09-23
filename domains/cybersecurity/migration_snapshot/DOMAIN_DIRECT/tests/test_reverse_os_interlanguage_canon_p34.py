"""P34 — Tests: REVERSE_OS_INTERLANGUAGE_CANON_V1 pack integrity.

Vérifie :
1. Pack canon existe (répertoire _source_packs/REVERSE_OS_INTERLANGUAGE_CANON_V1/).
2. MANIFEST_SHA256.json existe et a la structure correcte.
3. EVIDENCE_MAP.json existe et contient les concepts attendus.
4. IR_ALPHABET présent dans la map.
5. RECIPROQUE_MIROIR présent dans la map.
6. LCTU absent des concepts et marqué NOT_FOUND.
7. REVERSE_WINDOWS absent des concepts et marqué NOT_FOUND.
8. readonly=true dans la map.
9. runtime_allowed_now=false dans la map.
10. decision_authority=KX108_ONLY dans la map.
11. Aucun .py exécutable canonisé dans evidence/.
12. Fichier spec principal intègre (SHA256 vérifié).
"""
import hashlib
import json
import pathlib
import sys

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

_PACK_ROOT = _REPO_ROOT / "_source_packs" / "REVERSE_OS_INTERLANGUAGE_CANON_V1"
_MANIFEST = _PACK_ROOT / "MANIFEST_SHA256.json"
_EVIDENCE_MAP = _PACK_ROOT / "index" / "EVIDENCE_MAP.json"
_EVIDENCE_DIR = _PACK_ROOT / "evidence"
_CANON_SPEC = _EVIDENCE_DIR / "reverse_os_interlanguage_canon_v1.json"

EXPECTED_CANON_SHA256 = "5df672eeb8c354747dcece451c118e9654622a334d7cf9487929df24d657bded"


def test_p34_pack_exists():
    """Le répertoire du pack canon existe."""
    assert _PACK_ROOT.is_dir(), f"Pack canon manquant: {_PACK_ROOT}"


def test_p34_manifest_exists():
    """MANIFEST_SHA256.json existe."""
    assert _MANIFEST.is_file(), f"Manifest manquant: {_MANIFEST}"


def test_p34_manifest_structure():
    """MANIFEST_SHA256.json a la structure attendue."""
    data = json.loads(_MANIFEST.read_text(encoding="utf-8"))
    assert data["pack"] == "REVERSE_OS_INTERLANGUAGE_CANON_V1"
    assert data["readonly"] is True
    assert data["runtime_allowed_now"] is False
    assert data["decision_authority"] == "KX108_ONLY"
    assert "files" in data
    assert len(data["files"]) >= 8


def test_p34_evidence_map_exists():
    """index/EVIDENCE_MAP.json existe."""
    assert _EVIDENCE_MAP.is_file(), f"Evidence map manquante: {_EVIDENCE_MAP}"


def test_p34_evidence_map_authority():
    """La map d'évidence déclare readonly, no ACT, KX108_ONLY."""
    data = json.loads(_EVIDENCE_MAP.read_text(encoding="utf-8"))
    auth = data["authority"]
    assert auth["runtime_allowed_now"] is False
    assert auth["readonly"] is True
    assert auth["decision_authority"] == "KX108_ONLY"
    assert auth["emits_act"] is False
    assert auth["advisory_only"] is True


def test_p34_ir_alphabet_present():
    """IR_ALPHABET est présent dans la map d'évidence."""
    data = json.loads(_EVIDENCE_MAP.read_text(encoding="utf-8"))
    concepts = [c["concept"] for c in data["concepts"]]
    assert "IR_ALPHABET" in concepts, f"IR_ALPHABET manquant dans la map: {concepts}"
    ir = next(c for c in data["concepts"] if c["concept"] == "IR_ALPHABET")
    assert ir["core_parent_evidence_status"] == "CORE_PARENT_CANDIDATE"
    assert ir["runtime_allowed_now"] is False
    assert ir["readonly"] is True
    assert ir["decision_authority"] == "KX108_ONLY"


def test_p34_reciproque_miroir_present():
    """RECIPROQUE_MIROIR est présent dans la map d'évidence."""
    data = json.loads(_EVIDENCE_MAP.read_text(encoding="utf-8"))
    concepts = [c["concept"] for c in data["concepts"]]
    assert "RECIPROQUE_MIROIR" in concepts, f"RECIPROQUE_MIROIR manquant: {concepts}"
    rm = next(c for c in data["concepts"] if c["concept"] == "RECIPROQUE_MIROIR")
    assert rm["core_parent_evidence_status"] == "CORE_PARENT_CANDIDATE"
    assert rm["runtime_allowed_now"] is False
    assert rm["readonly"] is True


def test_p34_lctu_absent():
    """LCTU est absent des concepts actifs et marqué NOT_FOUND."""
    data = json.loads(_EVIDENCE_MAP.read_text(encoding="utf-8"))
    active_concepts = [c["concept"] for c in data["concepts"]]
    assert "LCTU" not in active_concepts, "LCTU ne doit pas être dans les concepts actifs"
    absent = [c for c in data.get("absent_concepts", []) if c["concept"] == "LCTU"]
    assert len(absent) == 1, "LCTU doit être dans absent_concepts"
    assert absent[0]["status"] == "NOT_FOUND"


def test_p34_reverse_windows_absent():
    """REVERSE_WINDOWS est absent des concepts actifs et marqué NOT_FOUND."""
    data = json.loads(_EVIDENCE_MAP.read_text(encoding="utf-8"))
    active_concepts = [c["concept"] for c in data["concepts"]]
    assert "REVERSE_WINDOWS" not in active_concepts, (
        "REVERSE_WINDOWS ne doit pas être dans les concepts actifs"
    )
    absent = [c for c in data.get("absent_concepts", []) if c["concept"] == "REVERSE_WINDOWS"]
    assert len(absent) == 1, "REVERSE_WINDOWS doit être dans absent_concepts"
    assert absent[0]["status"] == "NOT_FOUND"


def test_p34_no_executable_in_evidence():
    """Aucun fichier .py/.ps1/.sh/.bat/.exe dans evidence/."""
    exec_exts = {".py", ".pyc", ".ps1", ".sh", ".bat", ".exe"}
    for f in _EVIDENCE_DIR.iterdir():
        assert f.suffix.lower() not in exec_exts, (
            f"Exécutable interdit trouvé dans evidence/: {f.name}"
        )


def test_p34_canon_spec_integrity():
    """La spec canonique a le bon SHA256."""
    assert _CANON_SPEC.is_file(), f"Spec principale manquante: {_CANON_SPEC}"
    h = hashlib.sha256(_CANON_SPEC.read_bytes()).hexdigest()
    assert h == EXPECTED_CANON_SHA256, (
        f"SHA256 incorrect pour reverse_os_interlanguage_canon_v1.json: {h}"
    )


def test_p34_canon_spec_sovereignty():
    """La spec canonique déclare KX108_ONLY, allowed_to_decide=false, readonly."""
    data = json.loads(_CANON_SPEC.read_text(encoding="utf-8-sig"))
    auth = data["authority"]
    assert auth["decision_authority"] == "KX108_ONLY"
    assert auth["allowed_to_decide"] is False
    assert auth["readonly"] is True
    assert auth["advisory_only"] is True


def test_p34_canon_spec_has_ir_alphabet():
    """La spec canonique contient le concept alphabet_ir."""
    data = json.loads(_CANON_SPEC.read_text(encoding="utf-8-sig"))
    concept_ids = [c["id"] for c in data["concepts"]]
    assert "alphabet_ir" in concept_ids, f"alphabet_ir manquant dans la spec: {concept_ids[:5]}"
    ir = next(c for c in data["concepts"] if c["id"] == "alphabet_ir")
    assert ir["fr"] == "Alphabet IR"
    assert len(data["ir_alphabet"]) == 12


def test_p34_canon_spec_has_reciproque_miroir():
    """La spec canonique contient le concept reciproque_miroir."""
    data = json.loads(_CANON_SPEC.read_text(encoding="utf-8-sig"))
    concept_ids = [c["id"] for c in data["concepts"]]
    assert "reciproque_miroir" in concept_ids, (
        f"reciproque_miroir manquant dans la spec: {concept_ids[:5]}"
    )
    rm = next(c for c in data["concepts"] if c["id"] == "reciproque_miroir")
    assert "reverse_os" in rm["domain"]
    assert "f⁻¹" in rm["math"]


def test_p34_canon_spec_no_lctu():
    """La spec canonique ne contient pas de concept LCTU."""
    data = json.loads(_CANON_SPEC.read_text(encoding="utf-8-sig"))
    concept_ids = [c["id"].lower() for c in data["concepts"]]
    assert "lctu" not in concept_ids, "lctu ne doit pas être dans la spec canonique"


def test_p34_runtime_not_activated():
    """Le pack ne déclare pas runtime_allowed_now=true nulle part."""
    data = json.loads(_MANIFEST.read_text(encoding="utf-8"))
    assert data["runtime_allowed_now"] is False
    map_data = json.loads(_EVIDENCE_MAP.read_text(encoding="utf-8"))
    assert map_data["authority"]["runtime_allowed_now"] is False
    for concept in map_data["concepts"]:
        assert concept["runtime_allowed_now"] is False, (
            f"runtime_allowed_now=true trouvé dans concept {concept['concept']}"
        )
