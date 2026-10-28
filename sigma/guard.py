from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass

from .contracts import (
    CanonicalDecisionEnvelope, DomainAggregate, Severity, X108Gate, SourceTag,
    AuthorityLevel, ObligationDirective, RULE_CONTRACT_REGISTRY, RuleContract
)


@dataclass
class GuardConfig:
    min_confidence_allow: float = 0.72
    hold_confidence_floor: float = 0.45
    max_unknowns_before_hold: int = 1
    max_contradictions_before_block: int = 2




# --- P3I_MAX_CONSENSUS_SURFACE_HELPERS_START ---
def _x108_safe_attr(obj, name, default=None):
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def _x108_safe_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _x108_severity_value(value):
    try:
        return value.value
    except Exception:
        return str(value) if value is not None else None




def _x108_json_scalar(value):
    """
    Convertit les Enum / Domain / Severity / objets simples en valeurs JSON-safe.
    Ne modifie aucune d?cision.
    """
    if value is None:
        return None

    if isinstance(value, (str, int, float, bool)):
        return value

    if hasattr(value, "value"):
        try:
            inner = value.value
            if isinstance(inner, (str, int, float, bool)):
                return inner
        except Exception:
            pass

    if hasattr(value, "name"):
        try:
            return str(value.name)
        except Exception:
            pass

    return str(value)


def _x108_is_domain_like(value):
    s = str(value or "").upper()
    return s.startswith("DOMAIN.") or s in {
        "BANK",
        "TRADING",
        "ECOM",
        "GPS_DEFENSE_AVIATION",
        "GPS",
        "AVIATION",
    }


def _x108_is_trusted_act_source(layer_raw) -> bool:
    """
    True only if vote layer is KERNEL (6) or higher (PROOF=7, SCELLAGE=8).
    Votes from OBSERVATION/INTERPRETATION/CONTRADICTION/PERIPHERAL/SIGMA
    are NOT trusted to produce ACT on the aggregate4 proof surface.
    DECISION_AUTHORITY=KX108_ONLY  ACT=NO  PROOF_SURFACE_ONLY
    """
    if layer_raw is None:
        return False
    try:
        layer_int = int(layer_raw)
        return layer_int >= 6
    except (ValueError, TypeError):
        pass
    s = str(layer_raw).upper()
    return s in ("KERNEL", "PROOF", "SCELLAGE", "6", "7", "8")


def _x108_pick_vote(raw_vote, proposed_verdict):
    """
    Certains agents legacy passent Domain en deuxi?me argument.
    Dans ce cas, Domain peut se retrouver dans vote.
    On ne l'interpr?te pas comme d?cision.
    """
    candidates = [raw_vote, proposed_verdict, "HOLD"]

    for c in candidates:
        if c is None:
            continue
        if _x108_is_domain_like(c):
            continue
        normalized = _x108_normalize_vote_for_aggregate4(c)
        if normalized not in ("ERROR", "UNKNOWN"):
            return c

    return "HOLD"


def _x108_normalize_vote_for_aggregate4(value):
    """
    Normalisation strictement destin?e ? la surface de preuve.
    Ne modifie pas la d?cision Kernel/X108.
    """
    s = str(value or "").upper().strip()

    if s in ("ACT", "ALLOW", "AUTHORIZE", "AUTHORIZED", "VALID", "PASS", "PAY", "TRAJECTORY_VALID"):
        return "ACT"

    if s in ("HOLD", "ANALYZE", "REVIEW", "RECALC", "RECALC_TRAJECTORY", "WAIT", "DEFER"):
        return "HOLD"

    if s in ("BLOCK", "DENY", "REFUSE", "ABORT", "ABORT_TRAJECTORY", "REJECT"):
        return "BLOCK"

    if s in ("ERROR", "UNKNOWN", "", "NONE"):
        return "ERROR"

    return "UNKNOWN"


def _x108_count_values(values):
    counts = {}
    for v in values:
        key = str(v or "UNKNOWN")
        counts[key] = counts.get(key, 0) + 1
    return counts


def _x108_agent_vote_detail(v):
    raw_vote_raw = _x108_safe_attr(v, "vote", None)
    proposed_verdict_raw = _x108_safe_attr(v, "proposed_verdict", None)
    layer_raw = _x108_safe_attr(v, "layer", None)
    selected_vote_raw = _x108_pick_vote(raw_vote_raw, proposed_verdict_raw)

    raw_vote = _x108_json_scalar(raw_vote_raw)
    proposed_verdict = _x108_json_scalar(proposed_verdict_raw)
    selected_vote = _x108_json_scalar(selected_vote_raw)

    # V3: Validate ACT source trust before exposing on aggregate4 surface.
    # ACT-class votes from non-kernel layers are blocked; fallback is HOLD.
    # DECISION_AUTHORITY=KX108_ONLY  ACT=NO  PROOF_SURFACE_ONLY
    _normalized_raw = _x108_normalize_vote_for_aggregate4(selected_vote)
    _is_trusted = _x108_is_trusted_act_source(layer_raw)
    _is_domain_rejected = (
        _x108_is_domain_like(raw_vote_raw) or _x108_is_domain_like(proposed_verdict_raw)
    )

    if _normalized_raw == "ACT" and not _is_trusted:
        _normalized_final = "HOLD"
        _false_act_blocked = True
        _invalid_legacy = True
    else:
        _normalized_final = _normalized_raw
        _false_act_blocked = False
        _invalid_legacy = False

    detail = {
        "agent_id": _x108_json_scalar(_x108_safe_attr(v, "agent_id", "UNKNOWN_AGENT")),
        "vote": raw_vote,
        "proposed_verdict": proposed_verdict,
        "selected_vote": selected_vote,
        "normalized_vote_for_aggregate4": _normalized_final,
        "confidence": _x108_safe_attr(v, "confidence", None),
        "domain": _x108_json_scalar(_x108_safe_attr(v, "domain", "unknown")),
        "layer": _x108_json_scalar(layer_raw),
        "claim": _x108_json_scalar(_x108_safe_attr(v, "claim", None)),
        "severity_hint": _x108_json_scalar(_x108_safe_attr(v, "severity_hint", None)),
        "contradictions": [_x108_json_scalar(x) for x in _x108_safe_list(_x108_safe_attr(v, "contradictions", []))],
        "unknowns": [_x108_json_scalar(x) for x in _x108_safe_list(_x108_safe_attr(v, "unknowns", []))],
        "risk_flags": [_x108_json_scalar(x) for x in _x108_safe_list(_x108_safe_attr(v, "risk_flags", []))],
        "evidence_refs": [_x108_json_scalar(x) for x in _x108_safe_list(_x108_safe_attr(v, "evidence_refs", []))],
        "serialization_note": "json_safe_p3i7",
        # V3 audit flags — aggregate4 surface hardening
        "aggregate4_invalid_legacy_vote": _invalid_legacy,
        "aggregate4_domain_enum_rejected": _is_domain_rejected,
        "aggregate4_false_act_surface_blocked": _false_act_blocked,
        "aggregate4_selected_vote_source": "trusted_kernel" if _is_trusted else "non_trusted_peripheral",
        "aggregate4_proof_surface_only": True,
        "aggregate4_does_not_authorize_action": True,
    }

    try:
        detail["confidence"] = float(detail["confidence"]) if detail["confidence"] is not None else None
    except Exception:
        detail["confidence"] = None

    return detail


def _x108_aggregate4_result(normalized_votes):
    counts = _x108_count_values(normalized_votes)

    for decision in ("ACT", "HOLD", "BLOCK"):
        if counts.get(decision, 0) >= 3:
            return {
                "final_decision": decision,
                "votes": counts,
                "supermajority": True,
                "threshold": "3/4",
                "fail_closed": False,
                "reason": "3/4 supermajority reached",
            }

    return {
        "final_decision": "BLOCK",
        "votes": counts,
        "supermajority": False,
        "threshold": "3/4",
        "fail_closed": True,
        "reason": "No 3/4 supermajority ? fail-closed applies",
    }


def _x108_consensus_surface(agent_votes):
    details = [_x108_agent_vote_detail(v) for v in _x108_safe_list(agent_votes)]
    normalized_votes = [d["normalized_vote_for_aggregate4"] for d in details]
    observed_count = len(details)

    raw_vote_counts = _x108_count_values([d.get("vote") for d in details])
    proposed_verdict_counts = _x108_count_values([d.get("proposed_verdict") for d in details])
    normalized_vote_counts = _x108_count_values(normalized_votes)

    observation = {
        "display_only": True,
        "authority": "NONE",
        "warning": "Observation ratio is not a Kernel decision and not a Lean aggregate4 proof.",
        "threshold_ratio": 0.75,
        "voters_observed": observed_count,
        "max_decision": None,
        "max_count": 0,
        "ratio": None,
        "ratio_threshold_met": False,
    }

    if observed_count:
        best_decision, best_count = max(normalized_vote_counts.items(), key=lambda item: item[1])
        observation.update({
            "max_decision": best_decision,
            "max_count": best_count,
            "ratio": round(best_count / observed_count, 4),
            "ratio_threshold_met": (best_count / observed_count) >= 0.75,
        })

    consensus = {
        "rule": "aggregate4",
        "threshold": "3/4",
        "voters_expected": 4,
        "supermajority_min": 3,
        "source": "P3G_MAX_CONSENSUS_SCORE_CONTRACT",
        "proof_scope": "aggregate4 over exactly 4 voters",
        "authority": "PROOF_SURFACE_ONLY",
        "does_not_override_x108_gate": True,
        "does_not_authorize_action": True,
        "agent_vote_details_exposed": True,
        "agent_vote_source": "AgentVote.vote / AgentVote.proposed_verdict / AgentVote.confidence",
        "voters_observed": observed_count,
        "raw_vote_counts": raw_vote_counts,
        "proposed_verdict_counts": proposed_verdict_counts,
        "normalized_vote_counts": normalized_vote_counts,
        "observation_ratio": observation,
    }

    if observed_count == 4:
        formal_result = _x108_aggregate4_result(normalized_votes)
        consensus.update({
            "formal_result_status": "APPLIED_EXACTLY_4_VOTERS",
            "formal_result": formal_result,
        })
    else:
        consensus.update({
            "formal_result_status": "NOT_APPLIED_REQUIRES_4_VOTERS",
            "formal_result": None,
            "reason": "aggregate4 proof scope is exactly 4 voters; live agent count differs.",
        })

    # V3: aggregate4 surface hardening — collect per-vote audit counts
    _v3_blocked = sum(1 for d in details if d.get("aggregate4_false_act_surface_blocked"))
    _v3_invalid = sum(1 for d in details if d.get("aggregate4_invalid_legacy_vote"))
    _v3_domain_rej = sum(1 for d in details if d.get("aggregate4_domain_enum_rejected"))
    consensus["aggregate4_proof_surface_only"] = True
    consensus["aggregate4_does_not_authorize_action"] = True
    consensus["aggregate4_false_act_surface_blocked_count"] = _v3_blocked
    consensus["aggregate4_invalid_legacy_votes_count"] = _v3_invalid
    consensus["aggregate4_domain_enum_rejected_count"] = _v3_domain_rej

    return {
        "agent_vote_details": details,
        "consensus": consensus,
    }
# --- P3I_MAX_CONSENSUS_SURFACE_HELPERS_END ---


class GuardX108:
    def __init__(self, config: GuardConfig | None = None) -> None:
        self.config = config or GuardConfig()

    def decide(self, aggregate: DomainAggregate) -> CanonicalDecisionEnvelope:
        contradiction_count = len(aggregate.contradictions)
        unknown_count = len(aggregate.unknowns)
        risk_count = len(aggregate.risk_flags)
        market_v = str(getattr(aggregate, "market_verdict", "HOLD")).upper()
        domain_val = aggregate.domain.value if hasattr(aggregate.domain, "value") else str(aggregate.domain)

        # 1. Validation des mesures et qualification des règles contractuelles
        stale_or_invalid_measures = []
        mandatory_vetoes = []
        unresolved_blocks = []
        advisory_blocks = []
        falsified_alerts_rejected = []

        for v in getattr(aggregate, "agent_votes", []):
            rule_id = getattr(v, "rule_id", "") or ""
            if not rule_id:
                # Vote sans règle contractuelle : purement consultatif / d'observation
                # S'il a proposé BLOCK ou ABORT_TRAJECTORY, c'est consultatif (ne peut pas être un veto souverain)
                if v.proposed_verdict in ("BLOCK", "ABORT_TRAJECTORY"):
                    advisory_blocks.append((v, None))
                continue

            contract = RULE_CONTRACT_REGISTRY.get(rule_id)
            if contract is None:
                # Règle inconnue ou usurpée : ne peut conférer d'autorité impérative
                stale_or_invalid_measures.append((v, f"UNKNOWN_RULE_{rule_id}"))
                continue

            # Vérification de scope domaine (DOIT être faite AVANT l'évaluation de la mesure)
            rule_domain = contract.domain.value if hasattr(contract.domain, "value") else str(contract.domain)
            if rule_domain.lower() not in (domain_val.lower(), "meta", "cross_domain"):
                # Règle hors périmètre : ignorée pour la décision de ce domaine
                continue

            # Vérification de révocation ou version de règle
            if contract.is_revoked or getattr(v, "rule_version", "1.0") != contract.version:
                stale_or_invalid_measures.append((v, f"REVOKED_OR_WRONG_VERSION_{rule_id}"))
                continue

            # Vérification de qualification de la mesure (provenance, horodatage, validité, valeur observée)
            val = getattr(v, "observed_value", None)
            prov = getattr(v, "measure_provenance", None)
            age = getattr(v, "measure_age_s", None)
            is_valid = getattr(v, "measure_valid", None)

            is_qualified = (
                is_valid is True
                and prov is not None and len(str(prov).strip()) > 0
                and age is not None and 0.0 <= float(age) <= contract.max_allowed_age_s
                and val is not None
            )

            if not is_qualified:
                # Une mesure absente ou non qualifiée doit conserver explicitement son statut UNKNOWN
                # Elle ne peut pas satisfaire une contrainte
                stale_or_invalid_measures.append((v, f"UNQUALIFIED_MEASURE_{rule_id}"))
                continue

            # Si la règle est purement ADVISORY : elle ne peut jamais être souveraine
            if contract.authority_level == AuthorityLevel.ADVISORY:
                if v.proposed_verdict in ("BLOCK", "ABORT_TRAJECTORY"):
                    advisory_blocks.append((v, contract))
                continue

            # VÉRIFICATION INDÉPENDANTE DU PRÉDICAT DÉTERMINISTE PAR KX108 (MANDATORY & CONTRACT_UNRESOLVED)
            if contract.predicate is not None:
                try:
                    predicate_violated = bool(contract.predicate(val))
                except Exception:
                    predicate_violated = True
            else:
                predicate_violated = False

            # Détection d'alerte falsifiée : l'agent déclare une violation alors que le prédicat est nominal
            agent_claimed_violation = (
                getattr(v, "predicate_violated", None) is True
                or v.proposed_verdict in ("BLOCK", "ABORT_TRAJECTORY")
            )

            if agent_claimed_violation and not predicate_violated:
                # Alerte falsifiée rejetée par KX108 !
                falsified_alerts_rejected.append((v, contract))
                continue

            # Prédicat déterministe violé (indépendamment du signal déclaré par l'agent)
            if predicate_violated:
                if contract.authority_level == AuthorityLevel.MANDATORY_VETO:
                    mandatory_vetoes.append((v, contract))
                elif contract.authority_level == AuthorityLevel.CONTRACT_UNRESOLVED:
                    if contract.obligation == ObligationDirective.MUST_BLOCK:
                        unresolved_blocks.append((v, contract))
                    else:
                        advisory_blocks.append((v, contract))

        # 2. Arbitrage souverain KX108
        canonical_market_verdict = aggregate.market_verdict

        if mandatory_vetoes:
            # Obligation souveraine absolue : s'applique indépendamment de la gravité (même S1) et des scores
            v_mand, c_mand = mandatory_vetoes[0]
            gate = X108Gate.BLOCK
            reason = f"MANDATORY_RULE_VIOLATION_{c_mand.rule_id}"
            severity = Severity.S4
            if canonical_market_verdict in ("TRAJECTORY_VALID", "AUTHORIZE", "ALLOW"):
                canonical_market_verdict = v_mand.proposed_verdict if v_mand.proposed_verdict in ("BLOCK", "ABORT_TRAJECTORY") else "BLOCK"
        elif unresolved_blocks:
            # Traitement conservatoire fail-closed des règles non résolues (interdit ALLOW)
            v_unres, c_unres = unresolved_blocks[0]
            gate = X108Gate.BLOCK
            reason = f"CONSERVATIVE_UNRESOLVED_RULE_BLOCK_{c_unres.rule_id}"
            severity = Severity.S4
            if canonical_market_verdict in ("TRAJECTORY_VALID", "AUTHORIZE", "ALLOW"):
                canonical_market_verdict = v_unres.proposed_verdict if v_unres.proposed_verdict in ("BLOCK", "ABORT_TRAJECTORY") else "BLOCK"
        elif stale_or_invalid_measures:
            # Mesure absente, périmée, corrompue ou règle révoquée -> jamais ALLOW
            v_inv, r_code = stale_or_invalid_measures[0]
            gate = X108Gate.HOLD
            reason = f"INVALID_OR_STALE_MEASURE_{r_code}"
            severity = Severity.S2
            if canonical_market_verdict in ("TRAJECTORY_VALID", "AUTHORIZE", "ALLOW"):
                canonical_market_verdict = "HOLD"
        elif contradiction_count >= self.config.max_contradictions_before_block or "FRAUD_PATTERN" in aggregate.risk_flags:
            gate = X108Gate.BLOCK
            reason = "CONTRADICTION_THRESHOLD_REACHED"
            severity = Severity.S4
            if canonical_market_verdict not in ("BLOCK", "ABORT_TRAJECTORY"):
                canonical_market_verdict = "BLOCK"
        elif advisory_blocks:
            # RÈGLE FONDAMENTALE : un agent ADVISORY ne produit JAMAIS un BLOCK souverain
            gate = X108Gate.HOLD
            rule_id_tag = advisory_blocks[0][1].rule_id if advisory_blocks[0][1] else advisory_blocks[0][0].agent_id
            reason = f"ADVISORY_ALERT_HOLD_{rule_id_tag}"
            severity = Severity.S2
            if canonical_market_verdict in ("TRAJECTORY_VALID", "AUTHORIZE", "ALLOW"):
                canonical_market_verdict = "HOLD"
        elif market_v in ("BLOCK", "ABORT_TRAJECTORY", "REFUSE", "DENY"):
            falsified_votes = [f[0] for f in falsified_alerts_rejected]
            has_other_blocking_votes = any(
                v for v in getattr(aggregate, "agent_votes", [])
                if v not in falsified_votes and v.proposed_verdict in ("BLOCK", "ABORT_TRAJECTORY", "REFUSE", "DENY")
            )
            if falsified_alerts_rejected and not has_other_blocking_votes:
                # Les seuls votes de blocage étaient falsifiés et ont été formellement réfutés par vérification indépendante
                gate = X108Gate.ALLOW if (unknown_count <= self.config.max_unknowns_before_hold and aggregate.confidence >= self.config.hold_confidence_floor) else X108Gate.HOLD
                reason = "FALSIFIED_ALERTS_DISMISSED_ALLOW" if gate == X108Gate.ALLOW else "FALSIFIED_ALERTS_DISMISSED_HOLD"
                severity = Severity.S0 if gate == X108Gate.ALLOW else Severity.S2
                canonical_market_verdict = "TRAJECTORY_VALID" if "TRAJECTORY" in market_v else "AUTHORIZE"
            else:
                gate = X108Gate.BLOCK
                reason = f"MARKET_CONSENSUS_REJECT_{market_v}"
                severity = Severity.S4
        elif market_v in ("HOLD", "RECALC_TRAJECTORY", "DEGRADED_NAVIGATION", "DELAY"):
            gate = X108Gate.HOLD
            reason = f"MARKET_VERDICT_REQUIRES_HOLD_{market_v}"
            severity = Severity.S2
        elif unknown_count > self.config.max_unknowns_before_hold or aggregate.confidence < self.config.hold_confidence_floor:
            gate = X108Gate.HOLD
            reason = "UNKNOWNS_OR_CONFIDENCE_LOW"
            severity = Severity.S2
        elif risk_count >= 2:
            # Séparation stricte : un score élevé ne neutralise jamais deux alertes de risque
            gate = X108Gate.HOLD
            reason = "RISK_FLAGS_REQUIRE_DELAY"
            severity = Severity.S2
        elif market_v in ("AUTHORIZE", "TRAJECTORY_VALID", "ALLOW", "PAY", "EXECUTE_LONG", "EXECUTE_SHORT"):
            gate = X108Gate.ALLOW
            reason = "GUARD_ALLOW"
            severity = Severity.S0 if aggregate.confidence >= self.config.min_confidence_allow else Severity.S1
        else:
            gate = X108Gate.HOLD
            reason = f"CONSERVATIVE_HOLD_{market_v}"
            severity = Severity.S2

        domain_str = aggregate.domain.value if hasattr(aggregate.domain, "value") else str(aggregate.domain)
        decision_id = f"{domain_str}-{uuid.uuid4().hex[:12]}"
        trace_id = str(uuid.uuid4())
        ticket_required = gate == X108Gate.ALLOW
        ticket_id = uuid.uuid4().hex[:16] if ticket_required else None
        attestation_ref = hashlib.sha256("|".join(aggregate.evidence_refs).encode("utf-8")).hexdigest()[:24] if aggregate.evidence_refs else None

        consensus_surface = _x108_consensus_surface(aggregate.agent_votes)

        return CanonicalDecisionEnvelope(
            domain=domain_str,
            market_verdict=canonical_market_verdict,
            confidence=aggregate.confidence,
            contradictions=aggregate.contradictions,
            unknowns=aggregate.unknowns,
            risk_flags=aggregate.risk_flags,
            x108_gate=gate.value,
            reason_code=reason,
            severity=severity.value,
            decision_id=decision_id,
            trace_id=trace_id,
            ticket_required=ticket_required,
            ticket_id=ticket_id,
            attestation_ref=attestation_ref,
            source=SourceTag.CANONICAL_FRAMEWORK.value,
            evidence_refs=aggregate.evidence_refs,
            metrics=aggregate.extra_metrics,
            raw_engine={
                "domain": domain_str,
                "agent_votes": [v.agent_id for v in aggregate.agent_votes],
                "vote_count": len(aggregate.agent_votes),
                "agent_vote_details": consensus_surface["agent_vote_details"],
                "consensus": consensus_surface["consensus"],
            },
        )
