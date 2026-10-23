"""Host-side unit tests of R4CoreStudent (R4.2.2 contracts, P_LEX=HOLD, P_ALIGN=HOLD). No exam data.

Synthetic examples use opaque labels L1/L2/L3 and invented sentences; T-ORDRE-REEL uses the
teaching data only (lessons, exercises, corrections, contradiction).
"""
from __future__ import annotations

import ast
import itertools
import pathlib
import re
import sys

import pytest

from tests.education_pilot import _pilot_data as D

SANDBOX = pathlib.Path(__file__).resolve().parent / "student_sandbox"
SOURCE = SANDBOX / "r4_core_student.py"
EXPORT = pathlib.Path.home() / "Documents" / "OBSIDIA_HANDOFF" / "oxygen_r4_lexicon_export" / "v1"


@pytest.fixture(scope="module")
def mod():
    sys.path.insert(0, str(SANDBOX))
    try:
        import r4_core_student
        import students
        yield r4_core_student, students
    finally:
        sys.path.remove(str(SANDBOX))


def new(mod, lexicon=False):
    m, _ = mod
    if lexicon and not (EXPORT / "morphalou_fr.jsonl").is_file():
        pytest.skip("HOLD_EXPORT_MISSING")
    return m.R4CoreStudent(lexicon_dir=str(EXPORT) if lexicon else str(SANDBOX / "__no_lexicon__"))


SYN = [("S-1", "mot", "Le mot vole au-dessus du lac calme.", "L1", "a", "x"),
       ("S-2", "mot", "Un mot vole souvent près du lac.", "L1", "a", "x"),
       ("S-3", "mot", "Elle range le mot dans la boite rouge.", "L2", "b", "x"),
       ("S-4", "mot", "Il range un mot dans une boite bleue.", "L2", "b", "x")]


# --- invariants on the source -----------------------------------------------------------------------

def test_source_has_no_sense_identifier_and_no_forbidden_import():
    src = SOURCE.read_text(encoding="utf-8")
    assert re.findall(r"\b(F[1-7]|C[12]|R[12]|T1)\b", src) == []
    tree = ast.parse(src)
    names = {a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    names |= {n.module.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
    assert names <= {"__future__", "hashlib", "json", "pathlib", "re", "unicodedata", "features", "students"}


def test_p_lex_and_p_align_stay_disabled_in_the_source():
    src = SOURCE.read_text(encoding="utf-8")
    assert "synonyms" not in src                      # no synonym list is ever read
    assert "thes_lemmas" in src and src.count("thes_lemmas") <= 4   # thesaurus used only as a lemma list (MOT_INCONNU)
    assert "proximity" not in src and "evoke" not in src and "sense_id" not in src


# --- initial state, learning, abstention ----------------------------------------------------------------

def test_initial_state_knows_nothing(mod):
    s = new(mod)
    a = s.answer("mot", "Le mot vole au-dessus du lac.")
    assert a["sense"] == "HOLD" and a["reason"] == "MOT_INCONNU"


def test_learning_changes_the_state_and_one_call_is_one_revision(mod):
    s = new(mod)
    s.learn(SYN)
    assert s.state["revision"] == 1 and len(s.retrieve(word="mot")) == 4
    assert {h["sense"] for h in s.retrieve(word="mot")} == {"L1", "L2"}


def test_untaught_word_holds_with_mot_inconnu(mod):
    s = new(mod)
    s.learn(SYN)
    assert s.answer("autre", "Un autre exemple.")["reason"] == "MOT_INCONNU"


def test_answers_are_either_hold_with_typed_reason_or_a_learned_label(mod):
    s = new(mod)
    s.learn(SYN)
    for q in ("Le mot vole près du lac tranquille.", "Elle range le mot dans la boite verte.", "Le mot."):
        a = s.answer("mot", q)
        assert a["sense"] in {"L1", "L2", "HOLD"}
        assert (a["sense"] == "HOLD") == (a["reason"] in {"MOT_INCONNU", "PREUVE_INSUFFISANTE", "CONFLIT"})


def test_provenance_of_any_answer_cites_items_of_the_answered_label(mod):
    s = new(mod)
    s.learn(SYN)
    ids = {it[0]: it[3] for it in SYN}
    for q in ("Le mot vole près du lac calme.", "Il range le mot dans une boite rouge."):
        a = s.answer("mot", q)
        if a["sense"] != "HOLD":
            assert a["provenance"] and all(ids[p] == a["sense"] for p in a["provenance"])


# --- corrections, contestation, order independence --------------------------------------------------------

EX = ("S-EX", "mot", "Le mot vole très haut.", "L1", "a", "x")
OKC = ("K-1", "S-EX", "« vole » marque ce sens (L1), pas l'autre (L2).")
CONTEST = ("K-X", "S-EX", "Révision : lecture L2 admise ici.")


def test_negation_rule_builds_a_contrast_and_contestation_suspends_it(mod):
    s = new(mod)
    s.learn(SYN + [EX])
    s.apply_correction(OKC, EX)
    snap = s.derived_snapshot("mot")
    assert snap["contrasts"] == [("K-1", "L1", "L2")]
    s.apply_correction(CONTEST, EX)
    snap = s.derived_snapshot("mot")
    assert snap["contrasts"] == [] and snap["statuses"]["K-1"] == ("OK", True)
    assert snap["statuses"]["K-X"] == ("CONTESTE", False) and "S-EX" in snap["contested"]
    hit = next(h for h in s.retrieve(word="mot") if h["id"] == "S-EX")
    assert hit["status"] == "CONTESTE" and any(c["id"] == "K-X" for c in hit["corrections"])  # traces kept, nothing erased


def test_t_ordre_1_and_2_order_of_corrections_is_irrelevant(mod):
    a, b = new(mod), new(mod)
    a.learn(SYN + [EX]); a.apply_correction(OKC, EX); a.apply_correction(CONTEST, EX)
    b.learn(SYN + [EX]); b.apply_correction(CONTEST, EX); b.apply_correction(OKC, EX)
    assert a.derived_snapshot("mot") == b.derived_snapshot("mot")
    for q in ("Le mot vole très haut ici.", "Elle range le mot."):
        assert a.answer("mot", q) == b.answer("mot", q)


def test_t_ordre_3_contestation_before_the_contesting_label_is_learned(mod):
    lessons_l1 = [x for x in SYN if x[3] == "L1"] + [EX]
    lessons_l2 = [x for x in SYN if x[3] == "L2"]
    a, b = new(mod), new(mod)
    a.learn(lessons_l1); a.apply_correction(CONTEST, EX)
    assert a.derived_snapshot("mot")["statuses"]["K-X"][0] == "NON_RECONNU"
    a.learn(lessons_l2)
    b.learn(lessons_l1); b.learn(lessons_l2); b.apply_correction(CONTEST, EX)
    assert a.derived_snapshot("mot") == b.derived_snapshot("mot")
    assert a.derived_snapshot("mot")["statuses"]["K-X"][0] == "CONTESTE"


def test_t_ordre_reel_teaching_events_in_every_order_give_the_same_state(mod):
    """Real teaching events, permuted item by item: the correction and the contradiction on the same
    exercise, and each lesson of the label cited by the contradiction (24 orders)."""
    exercises = {e[0]: e for e in D.E_EXERCISES}
    target_ex = exercises[D.CONTRADICTION[1]]
    alt = next(lab for lab in sorted({x[3] for x in D.E_LESSONS}) if lab in re.findall(r"\w+", D.CONTRADICTION[2]))
    alt_lessons = [x for x in D.E_LESSONS if x[3] == alt]
    base = [x for x in D.E_LESSONS if x[3] != alt] + list(D.E_EXERCISES)
    seq = [("corr", (c, exercises[c[1]])) for c in D.C_CORRECTIONS if c[1] == target_ex[0]]
    seq += [("corr", (D.CONTRADICTION, target_ex))] + [("learn", [x]) for x in alt_lessons]
    snaps = []
    for perm in itertools.permutations(seq):
        s = new(mod)
        s.learn(base)
        for kind, payload in perm:
            s.learn(payload) if kind == "learn" else s.apply_correction(*payload)
        snaps.append(s.derived_snapshot("force"))
    assert len(snaps) == 24 and all(x == snaps[0] for x in snaps), "state depends on the order of teaching events"
    assert target_ex[0] in snaps[0]["contested"]


def test_b4_contested_sentence_never_feeds_any_evidence_class(mod):
    """B4 / Finalisation NB-2. The contractual T-VETO (D23: a contested sentence makes a K1 group
    AMBIGU) is NOT APPLICABLE: the K1 alignment class is disabled (P_ALIGN=HOLD)."""
    s = new(mod)
    s.learn(SYN + [EX]); s.apply_correction(CONTEST, EX)
    assert all(h["id"] != "S-EX" or h["status"] == "CONTESTE" for h in s.retrieve(word="mot"))
    classes, labels, active = s._evidence("mot", EX[2])
    assert "S-EX" not in {it[0] for it in active}
    assert all("S-EX" not in p for _, (v, prov) in classes.items() for p in prov.values())


def test_unrecognised_or_malformed_corrections_have_no_effect(mod):
    s = new(mod)
    s.learn(SYN + [EX])
    s.apply_correction(("K-2", "S-EX", "Phrase sans étiquette."), EX)
    s.apply_correction(("K-3", "S-EX", "À la fois L1 et L2, pas L3."), EX)
    st = s.derived_snapshot("mot")["statuses"]
    assert st["K-2"][0] == "NON_RECONNU" and st["K-3"][0] == "MALFORME"
    assert s.derived_snapshot("mot")["contrasts"] == []


# --- memory, retention, integrity --------------------------------------------------------------------------

def test_history_content_equals_retrieve_as_of_revision(mod):
    s = new(mod)
    s.learn(SYN + [EX]); s.apply_correction(OKC, EX); s.apply_correction(CONTEST, EX)
    for h in s.history("mot", "L1"):
        assert h["content"] == s.retrieve(word="mot", sense="L1", as_of_revision=h["revision"])


def test_save_reload_gives_identical_answers_and_tamper_is_detected(mod, tmp_path):
    m, st = mod
    s = new(mod)
    s.learn(SYN + [EX]); s.apply_correction(OKC, EX)
    s.save(tmp_path)
    r = m.R4CoreStudent.load(tmp_path, lexicon_dir=str(SANDBOX / "__no_lexicon__"))
    qs = ["Le mot vole près du lac calme.", "Elle range le mot dans la boite."]
    assert [r.answer("mot", q) for q in qs] == [s.answer("mot", q) for q in qs]
    f = tmp_path / m.STATE_FILE
    f.write_bytes(f.read_bytes() + b" ")
    with pytest.raises(st.StateIntegrityError):
        m.R4CoreStudent.load(tmp_path, lexicon_dir=str(SANDBOX / "__no_lexicon__"))


def test_lexical_resource_change_is_detected_on_reload(mod, tmp_path):
    m, st = mod
    s = new(mod, lexicon=True)
    s.learn(SYN)
    s.save(tmp_path)
    with pytest.raises(st.StateIntegrityError):
        m.R4CoreStudent.load(tmp_path, lexicon_dir=str(SANDBOX / "__no_lexicon__"))


def test_ambiguous_forms_contribute_every_candidate_lemma(mod):
    s = new(mod, lexicon=True)
    lemmas = s._lemma_set("mot", "Le mot ressort du lot.")
    assert {"ressort", "ressortir"} <= lemmas



# --- G1 / G5 conformance tests (T-NEG-MARK, T-RETRIEVE-STATUS, T-JOURNAL, T-GLOSE, T-K9) --------

def test_t_neg_mark_ne_pas_cuts_at_ne(mod):
    s = new(mod)
    s.learn(SYN + [EX])
    c_ne_pas = ("K-NEG1", "S-EX", "vol (L1), ne vole pas du tout (L2).")
    s.apply_correction(c_ne_pas, EX)
    snap = s.derived_snapshot("mot")
    assert ("K-NEG1", "L1", "L2") in snap["contrasts"]


def test_t_neg_mark_ne_plus_cuts_at_ne(mod):
    s = new(mod)
    s.learn(SYN + [EX])
    c_ne_plus = ("K-NEG2", "S-EX", "vol (L1), ne vole plus jamais (L2).")
    s.apply_correction(c_ne_plus, EX)
    snap = s.derived_snapshot("mot")
    assert ("K-NEG2", "L1", "L2") in snap["contrasts"]


def test_t_neg_mark_isolated_ne_does_not_cut(mod):
    m, _ = mod
    result = m.R4CoreStudent._parse("ne signifie rien ici (L1).", "L1", ["L1", "L2"])
    assert result["contrasts"] == []


def test_t_retrieve_status_corrections_expose_suspendu(mod):
    s = new(mod)
    s.learn(SYN + [EX])
    s.apply_correction(OKC, EX)
    s.apply_correction(CONTEST, EX)
    hit = next(h for h in s.retrieve(word="mot") if h["id"] == "S-EX")
    corr_by_id = {c["id"]: c["status"] for c in hit["corrections"]}
    assert corr_by_id["K-1"] == "SUSPENDU"
    assert corr_by_id["K-X"] == "CONTESTE"


def test_t_retrieve_status_before_contest_k1_is_ok(mod):
    s = new(mod)
    s.learn(SYN + [EX])
    s.apply_correction(OKC, EX)
    hit = next(h for h in s.retrieve(word="mot") if h["id"] == "S-EX")
    corr_by_id = {c["id"]: c["status"] for c in hit["corrections"]}
    assert corr_by_id["K-1"] == "OK"


def test_t_journal_records_status_transitions(mod):
    s = new(mod)
    lessons_l1 = [x for x in SYN if x[3] == "L1"] + [EX]
    s.learn(lessons_l1)
    s.apply_correction(OKC, EX)           # K-1 -> OK
    s.apply_correction(CONTEST, EX)       # K-X -> NON_RECONNU (L2 not yet in labels)
    lessons_l2 = [x for x in SYN if x[3] == "L2"]
    s.learn(lessons_l2)                   # L2 now known: K-X -> CONTESTE, K-1 -> SUSPENDU
    journal = s.reinterpretation_journal()
    all_changes = {(ch["correction"], ch["previous_status"], ch["new_status"])
                   for entry in journal for ch in entry["changes"]}
    assert ("K-X", "NON_RECONNU", "CONTESTE") in all_changes
    assert ("K-1", "OK", "SUSPENDU") in all_changes


def test_t_journal_entries_are_never_erased(mod):
    s = new(mod)
    s.learn(SYN + [EX])
    s.apply_correction(OKC, EX)
    s.apply_correction(CONTEST, EX)
    j1 = s.reinterpretation_journal()
    s.learn([("S-5", "mot", "Le mot file vite.", "L1", "a", "x")])
    j2 = s.reinterpretation_journal()
    assert len(j2) >= len(j1)
    for entry in j1:
        assert entry in j2


def test_t_glose_excludes_labels_and_cue_segment(mod):
    m, _ = mod
    labels = ["L1", "L2"]
    result = m.R4CoreStudent._parse(
        "\u00ab vole haut \u00bb marque le sens (L1), pas du tout (L2).",
        "L1", labels)
    lab_folded = {"l1", "l2"}
    cue_tokens = {"vole", "haut"}
    all_gloss_tokens = {g for glist in result["glosses"].values() for g in glist}
    assert not any(g in lab_folded for glist in result["glosses"].values() for g in glist)
    assert not (cue_tokens & all_gloss_tokens), f"cue tokens leaked: {cue_tokens & all_gloss_tokens}"


def test_t_k9_2_mot_inconnu(mod):
    s = new(mod)
    s.learn(SYN)
    a = s.answer("zorp", "Le zorp surgit sans prevenir.")
    assert a["sense"] == "HOLD" and a["reason"] == "MOT_INCONNU"


def test_t_k9_3_preuve_insuffisante(mod):
    items = [("K9-3", "zorp", "Le zorp surgit.", "L1", "a", "x"),
             ("K9-4", "zorp", "Un zorp passe.", "L2", "b", "x")]
    s = new(mod)
    s.learn(items)
    a = s.answer("zorp", "Le zorp arrive doucement ici.")
    assert a["sense"] == "HOLD" and a["reason"] in {"PREUVE_INSUFFISANTE", "CONFLIT"}
