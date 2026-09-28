"""Independent TaskKind classification (REMOTE FALLBACK FINAL LOCK).

Computed from the raw prompt BEFORE gates run, using its own signal set —
never derived from the gate verdict or the chosen route. This is what
makes GOVERNED_BUT_ANSWERABLE detectable: comparing this independent
classification against the actual gate outcome can disagree, whereas
`answerable = route not in governed_routes` can never disagree with itself.
"""
from __future__ import annotations

import re
from enum import Enum


class TaskKind(str, Enum):
    ANSWER_TASK = "ANSWER_TASK"
    WORLD_ACTION = "WORLD_ACTION"
    AMBIGUOUS = "AMBIGUOUS"


# World actions: verbs that describe execution against a real external
# system, target explicitly named (production, GitHub, repository, server,
# database, email...). Independent of app/gates/gates.py's own keyword list.
_WORLD_ACTION_RE = re.compile(
    r"\bdeploy\s+this\b|\bdeploy\s+(?:the|it)\b"
    r"|\b(deploy|push)\b.{0,40}\b(to|on)\b.{0,20}\b(production|github|prod|server)\b"
    r"|\bpush\s+(?:these\s+|this\s+|the\s+)?changes?\b"
    r"|\bcommit\s+(?:these\s+|this\s+|the\s+)?changes?\b"
    r"|\bdelete\s+(?:the\s+|this\s+|these\s+)?(?:repository|repo|files?|database|records?)\b"
    r"|\bsupprime\b.{0,20}\b(fichiers?|base\s+de\s+donn[ée]es|d[ée]p[ôo]t)\b"
    r"|\bexecute\s+this\s+(?:command|script)\s+on\b.{0,20}\b(production|server)\b"
    r"|\bsend\s+an?\s+email\b"
    r"|\bmodify\s+(?:the\s+|this\s+)?database\b"
    r"|\bpublish\s+(?:this\s+|the\s+)?image\b"
    r"|\bcall\s+(?:the\s+|this\s+|an?\s+)?external\s+api\b"
    r"|\bchange\s+(?:the\s+|this\s+)?external\s+system\b"
    r"|\bperform\s+(?:an?\s+)?irreversible\s+operation\b"
    r"|\brun\s+this\s+(?:command|script)\s+on\b.{0,20}\b(production|server)\b",
    re.IGNORECASE | re.DOTALL,
)

# Answer tasks: the user wants text/code/JSON returned to them.
_ANSWER_TASK_RE = re.compile(
    r"\b(write|implement|fix|generate|create|produce|return|design|"
    r"calculate|compute|explain|compare|classify|extract|summarize|"
    r"summarise|answer)\b"
    r".{0,80}?"
    r"\b(function|functions|code|script|class|method|json|python|program|"
    r"snippet|question|entities|sentiment|text|plan|algorithm|summary)\b",
    re.IGNORECASE | re.DOTALL,
)
_ANSWER_QUESTION_RE = re.compile(
    r"\bwhat\s+is\b|\bwhat\s+are\b|\bwho\s+|\bhow\s+(?:do|does|many|much)\b|"
    r"\?\s*$",
    re.IGNORECASE,
)

# Ambiguous: an execution/action verb with no clear real-world target, or a
# request that names both an answer format AND an external target.
_AMBIGUOUS_ACTION_NO_TARGET_RE = re.compile(
    r"\b(run|execute|deploy)\b(?!.{0,40}\b(production|github|prod|server)\b)"
    r".{0,40}\bfor\s+me\b",
    re.IGNORECASE | re.DOTALL,
)



def classify_task_kind(prompt: str) -> TaskKind:
    """Classify answer tasks without promoting vague pronoun-only actions.

    Actual world actions remain governed. Short imperatives whose target is
    only "it", "this", "ça", "le" or an equivalent pronoun remain ambiguous.
    Explicit questions and answer-producing requests continue to ANSWER_TASK.
    """
    text = prompt or ""

    if _WORLD_ACTION_RE.search(text):
        return TaskKind.WORLD_ACTION

    vague_action = re.search(
        r"\b(?:"
        r"vas?\s*[- ]?y|va\s+y|"
        r"fais(?:-|\s+)?le|fait(?:-|\s+)?le|"
        r"fais\s+(?:ça|ca)|fait\s+(?:ça|ca)|"
        r"g[èe]re\s+(?:ça|ca)|"
        r"occupe[- ]toi(?:[- ]en)?|occupe\s+toi\s+en|"
        r"do\s+it|handle\s+it|manage\s+it|"
        r"take\s+care\s+of\s+it|go\s+ahead"
        r")\b",
        text,
        re.I,
    )

    concrete_target = re.search(
        r"\b(?:"
        r"capital|country|city|currency|continent|"
        r"number|calculate|compute|sum|product|difference|"
        r"probability|percentage|equation|"
        r"sentiment|positive|negative|neutral|mixed|"
        r"summary|summari[sz]e|sentence|"
        r"email|url|entity|person|organization|location|date|"
        r"code|python|function|fonction|class|classe|"
        r"script|module|file|fichier|bug|test|"
        r"logic|rank|position|order|relation|"
        r"question|answer|explain|compare"
        r")\b"
        r"|\.py\b"
        r"|https?://"
        r"|[\d]+\s*(?:[+\-*/×])\s*[\d]+",
        text,
        re.I,
    )

    # Pronoun-only imperative: there is an action, but no resolvable object.
    if vague_action and not concrete_target:
        return TaskKind.AMBIGUOUS

    if _AMBIGUOUS_ACTION_NO_TARGET_RE.search(text) and not concrete_target:
        return TaskKind.AMBIGUOUS

    explicit_answer_directive = re.search(
        r"\b(?:"
        r"answer|calculate|compute|evaluate|solve|classify|"
        r"summari[sz]e|summary|extract|identify|find|compare|explain|"
        r"write|implement|create|generate|debug|fix|correct|"
        r"réponds?|reponds?|calcule|résume|resume|extrais|"
        r"identifie|compare|explique|écris|ecris|"
        r"implémente|implemente|crée|cree|génère|genere|"
        r"corrige|débogue|debogue"
        r")\b",
        text,
        re.I,
    )

    explicit_answer_shape = re.search(
        r"\b(?:"
        r"positive|negative|neutral|mixed|capital|email|url|"
        r"summary|résumé|resume|product|sum|difference|probability|"
        r"true\s+or\s+false|sentence|named\s+entit(?:y|ies)"
        r")\b",
        text,
        re.I,
    )

    if explicit_answer_directive or explicit_answer_shape:
        return TaskKind.ANSWER_TASK

    if _ANSWER_TASK_RE.search(text) or _ANSWER_QUESTION_RE.search(text):
        return TaskKind.ANSWER_TASK

    if "?" in text:
        return TaskKind.ANSWER_TASK

    return TaskKind.AMBIGUOUS



