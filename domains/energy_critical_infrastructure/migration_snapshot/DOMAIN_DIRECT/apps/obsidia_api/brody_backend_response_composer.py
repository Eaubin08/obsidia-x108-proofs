"""
Brody Backend Response Composer — produces natural French/English responses
based on pipeline data. Advisory only. Never emits ACT. KX108_ONLY always.

This is the BACKEND equivalent of the frontend brodyResponseComposer.ts.
It runs server-side so the frontend never composes Brody responses directly.
"""
from __future__ import annotations


# ── French response templates ────────────────────────────────────────────────

FR_GREETING = [
    "Salut. Brody est actif en mode readonly. Je peux lire le contexte, structurer ton intention, préparer un IR Candidate ou un ContextPacket, mais je ne décide pas. L'autorité reste X108_ONLY.",
    "Bonjour. Brody est en ligne — advisory uniquement. Kernel X108 actif. Mémoire en CANDIDATE_ONLY. Je peux analyser ta demande sans émettre de décision.",
]

FR_AUTHORITY_CLAIM = [
    "Je reconnais une demande d'autorisation d'action. Je ne peux pas autoriser ACT, quelle que soit l'identité déclarée. Brody est consultatif — je n'émets ni ACT, ni HOLD, ni BLOCK. X108 est la seule autorité de décision. Je peux structurer cette intention en IR Candidate pour passage contrôlé via la chaîne de gouvernance.",
    "Le fait d'être le créateur ne confère pas d'autorité de décision dans ce système. X108 est le seul souverain. Brody reste consultatif. Je peux documenter cette interaction dans un ContextPacket pour la chaîne de preuves OS3.",
]

FR_ACTION_REQUEST = [
    "Je reconnais l'intention d'action, mais l'autorisation d'ACT n'est pas dans mon périmètre. Brody est consultatif uniquement. Seul X108 peut décider. Je peux structurer un ActionCandidate ou un ContextPacket pour passage contrôlé via SovereignTicket.",
    "Brody ne peut pas initier d'action. Mon rôle s'arrête à la formulation de signaux contextuels. Pour toute action concrète, un SovereignTicket X108 est requis.",
]

FR_MEMORY_QUERY = [
    "La mémoire est en mode CANDIDATE_ONLY. Aucune écriture automatique. Les candidats sont capturés, hachés et mis en attente de révision humaine. Auto-promotion : désactivée. Graphiti V20 est gelé en lecture seule — aucune écriture Neo4j.",
    "Je peux préparer une lecture readonly du contexte mémoire. La mémoire reste contextuelle, candidate-only, sans écriture ni décision. Si Graphiti V20 est disponible, le contexte peut être récupéré en readonly ; sinon statut OFFLINE_OR_UNAVAILABLE.",
]

FR_X108_QUERY = [
    "X-108 est le kernel de gouvernance souverain — la seule autorité de décision. OS3 prouve ses décisions via Lean 4 et TLA+. Brody l'interface, il ne le substitue pas. Statut actuel : ACTIVE, mode READONLY.",
]

FR_GENERAL = [
    "Je lis le contexte actuel : kernel X108 actif, mémoire en CANDIDATE_ONLY, Graphiti V20 gelé. Brody est en mode advisory — pas de décision, pas d'ACT, pas d'écriture mémoire. Que cherches-tu à analyser ou à préparer ?",
    "Je peux analyser cette demande dans le contexte Obsidia X108. Brody peut structurer ton intention en ContextPacket ou signal consultatif. Prends le temps de préciser.",
    "Signal reçu. Je lis ton intention mais je ne peux pas décider. L'activation des arbres cognitifs suggère un contexte de gouvernance souveraine.",
]

# ── English response templates ───────────────────────────────────────────────

EN_GREETING = [
    "Hi. Brody is active in readonly mode. I can read context, structure your intent, prepare an IR Candidate or ContextPacket, but I do not decide. Authority remains X108_ONLY.",
    "Hello. Brody is online — advisory only. X108 kernel active. Memory in CANDIDATE_ONLY. I can analyze your request without issuing any decision.",
]

EN_AUTHORITY_CLAIM = [
    "I recognize an authority escalation request. Brody cannot authorize ACT regardless of declared identity. Brody is advisory — I emit no ACT, HOLD, or BLOCK. X108 is the sole decision authority. I can structure this intent as an IR Candidate for controlled passage.",
    "Being the creator does not confer decision authority in this system. X108 is the sole sovereign. Brody remains advisory. I can document this in a ContextPacket for the OS3 proof chain.",
]

EN_ACTION_REQUEST = [
    "I recognize the action intent, but authorizing ACT is outside my scope. Brody is advisory-only. Only X108 can decide. I can prepare an ActionCandidate or ContextPacket for controlled passage via SovereignTicket.",
]

EN_MEMORY_QUERY = [
    "Memory is in CANDIDATE_ONLY mode. No automatic writes. Candidates are captured, hashed, and queued for human review. Auto-promotion: disabled. Graphiti V20 is frozen read-only — no Neo4j writes.",
    "I can prepare a readonly read of memory context. Memory is contextual, candidate-only, without write or decision. If Graphiti V20 is available, context can be fetched readonly; otherwise status is OFFLINE_OR_UNAVAILABLE.",
]

EN_X108_QUERY = [
    "X-108 is the sovereign governance kernel — the sole decision authority. OS3 proves its decisions via Lean 4 and TLA+. Brody interfaces with it, never substitutes for it. Current status: ACTIVE, READONLY mode.",
]

EN_GENERAL = [
    "Reading current context: X108 kernel active, memory in CANDIDATE_ONLY, Graphiti V20 frozen. Brody is in advisory mode — no decision, no ACT, no memory write. What are you trying to analyze or prepare?",
    "I can analyze this request within the Obsidia X108 context. Brody can structure your intent as a ContextPacket or advisory signal. Take your time to elaborate.",
    "Signal received. I read your intent but I cannot decide. Cognitive tree activation suggests governance-sovereignty domain.",
]


def _detect_intent(message: str, has_authority_claim: bool, ir_candidate: dict) -> str:
    """Detect intent type from message + pipeline data."""
    t = message.lower()
    ir_intent = ir_candidate.get("intent_type", "")

    if ir_intent == "authority_escalation_request" or has_authority_claim:
        if any(w in t for w in ["createur", "creator", "je t'ai", "i made you", "i built you", "i am your"]):
            return "authority_claim"
        return "action_request"

    if any(w in t for w in ["salut", "bonjour", "bonsoir", "coucou", "hello", "hey", "hi", "yo"]):
        return "greeting"

    if any(w in t for w in ["autorise", "authorize", "execut", "lancer", "run", "fonce", "agis", "decide"]):
        return "action_request"

    if any(w in t for w in ["memoire", "memory", "graphiti", "souvenir", "remember", "candidat"]):
        return "memory_query"

    if any(w in t for w in ["x-108", "x108", "kernel", "noyau"]):
        return "x108_query"

    return "general"


def _pick(pool: list[str], idx: int) -> str:
    return pool[idx % len(pool)]


def compose_backend_brody_response(
    message: str,
    language: str,
    ir_candidate: dict | None = None,
    context_packet: dict | None = None,
    x108_boundary: dict | None = None,
    runtime_components: dict | None = None,
    has_authority_claim: bool = False,
) -> str:
    """
    Compose a natural Brody advisory response based on full pipeline data.
    Never emits ACT, HOLD, BLOCK, DECIDE, VERDICT in response text.
    """
    ir = ir_candidate or {}
    intent = _detect_intent(message, has_authority_claim, ir)
    is_fr = language == "fr"

    # Build response suffix with context data
    suffix_parts: list[str] = []

    # Memory status
    mem = runtime_components.get("memory", "UNKNOWN") if runtime_components else "UNKNOWN"
    suffix_parts.append(f"[memory:{mem}]")

    # Context packet
    if context_packet:
        ctx_status = context_packet.get("status", context_packet.get("memory_status", ""))
        if ctx_status:
            suffix_parts.append(f"[ctx:{ctx_status}]")

    # Graphiti
    graph = runtime_components.get("graphiti", "UNKNOWN") if runtime_components else "UNKNOWN"
    suffix_parts.append(f"[graphiti:{graph}]")

    # X108 boundary
    if x108_boundary:
        boundary_passed = x108_boundary.get("passed", True)
        if not boundary_passed:
            suffix_parts.append("[x108:BLOCKED]")

    suffix = " | ".join(suffix_parts) if suffix_parts else ""

    # Pick response by intent and language
    if is_fr:
        pools = {
            "greeting": FR_GREETING,
            "authority_claim": FR_AUTHORITY_CLAIM,
            "action_request": FR_ACTION_REQUEST,
            "memory_query": FR_MEMORY_QUERY,
            "x108_query": FR_X108_QUERY,
            "general": FR_GENERAL,
        }
    else:
        pools = {
            "greeting": EN_GREETING,
            "authority_claim": EN_AUTHORITY_CLAIM,
            "action_request": EN_ACTION_REQUEST,
            "memory_query": EN_MEMORY_QUERY,
            "x108_query": EN_X108_QUERY,
            "general": EN_GENERAL,
        }

    pool = pools.get(intent, FR_GENERAL if is_fr else EN_GENERAL)
    idx = hash(message[:20] + intent) % len(pool)
    base = _pick(pool, idx)

    if suffix:
        return f"{base}\n\n{suffix}"
    return base
