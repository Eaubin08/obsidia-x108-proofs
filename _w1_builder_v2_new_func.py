def build_context_packet_v2(
    query: str,
    language: str = "en",
    context_items: list[str] | None = None,
    source_refs: list[str] | None = None,
    packet_id: str | None = None,
    dominant_trees: list[int] | None = None,
    memory_status: str | None = None,
    risk_flags: list[str] | None = None,
    unknowns: list[str] | None = None,
    contradictions: list[str] | None = None,
) -> ContextPacketV2:
    items = context_items or []
    forbidden: list[str] = []
    for item in items:
        for word in item.split():
            if word.strip(".,;:!?\"'").upper() in _FORBIDDEN_TOKENS:
                forbidden.append(word.strip(".,;:!?\"'").upper())
    hashes = []
    for ref in (source_refs or []):
        hashes.append(hashlib.sha256(ref.encode()).hexdigest()[:16])
    return ContextPacketV2(
        packet_id=packet_id or uuid.uuid4().hex,
        query=query,
        language=language,
        context_items=items,
        source_refs=source_refs or [],
        source_hashes=hashes,
        dominant_trees=dominant_trees or [],
        memory_status=memory_status or "CANDIDATE_ONLY",
        risk_flags=risk_flags or [],
        unknowns=unknowns or [],
        contradictions=contradictions or [],
        forbidden_tokens_detected=list(set(forbidden)),
        readonly=True,
        context_signal_only=True,
        decision_authority="KX108_ONLY",
        allowed_to_decide=False,
        allowed_to_act=False,
        kernel_mutation=False,
        memory_write=False,
    )
