# ATLAS_TO_CONTEXTPACKET_MAP

| Atlas source object | Contract target | Allowed use | Forbidden use | Failure mode |
|---|---|---|---|---|
| scenario card | ContextPacket | readonly scenario context | real-world fact claim | fail_closed |
| branchable path | ContextPacket | hypothetical path context | autonomous execution | fail_closed |
| atlas map | ContextPacket | navigation/reference context | graph mutation | fail_closed |
| education scenario | ContextPacket | P7 learning scenario context | student action | fail_closed |
| scenario risk note | PeripheralSignalPacket | advisory risk signal | decision override | fail_closed |
| world action candidate | IntentEnvelope candidate only | requires X108 review | direct ACT | fail_closed |
| atlas evidence note | OS3EvidenceTicket reference | future evidence ref | proof claim | fail_closed |

Rule:
Atlas can contextualize.
Atlas cannot decide.
Atlas cannot act.
Atlas cannot claim reality.