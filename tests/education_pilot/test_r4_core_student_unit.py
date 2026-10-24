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
    classes, labels, active, _event_classes = s._evidence("mot", EX[2])
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

# --- P5-L2 first increment: event-level provenance, device pair corroboration ----------------------
#
# Scenario sentences (construction argmax vs exemplaires argmax):
#   PA1 = "Le mot vole souvent dans les nuages lointains."  -- construction argmax for L1 (event 1)
#   PA2 = "Un mot bondit depuis la branche haute."          -- L1 filler (event 1)
#   PA3 = "Ce mot plonge sous la surface froide."           -- L1 filler (event 1)
#   PB1 = "Ce mot vole souvent sur des arbres immenses aussi." -- exemplaires argmax for L1 (event 2)
#   PE1 = "La route du mot longe toute la colline."         -- L2 (event 1 or 2)
#   PE2 = "Quelle colline prend ce mot fragile."            -- L2 (event 1 or 2)
#   PQUERY = "Le mot vole souvent sur les arbres immenses." -- test query
#
# With n[L1]=4: voices_constr(PA1)=0.545>=TAU, voices_exem(PB1)=0.533>=TAU (verified analytically).
# PA1 and PB1 have disjoint prov sets; since V1.1 the device pair is informational and never answers.

PA1 = ("PA1", "mot", "Le mot vole souvent dans les nuages lointains.", "L1", "d", "x")
PA2 = ("PA2", "mot", "Un mot bondit depuis la branche haute.", "L1", "d", "x")
PA3 = ("PA3", "mot", "Ce mot plonge sous la surface froide.", "L1", "d", "x")
PB1 = ("PB1", "mot", "Ce mot vole souvent sur des arbres immenses aussi.", "L1", "d", "x")
PE1 = ("PE1", "mot", "La route du mot longe toute la colline.", "L2", "e", "x")
PE2 = ("PE2", "mot", "Quelle colline prend ce mot fragile.", "L2", "e", "x")
PQUERY = "Le mot vole souvent sur les arbres immenses."


def test_p5l2_source_event_tracks_item_revision(mod):
    s = new(mod)
    s.learn([PA1, PA2])
    s.learn([PB1])
    d = s._derive()
    assert d["items"]["PA1"]["revision"] == 1
    assert d["items"]["PA2"]["revision"] == 1
    assert d["items"]["PB1"]["revision"] == 2
    m, _ = mod
    assert m.R4CoreStudent._source_event(d, "PA1") == 1
    assert m.R4CoreStudent._source_event(d, "PB1") == 2
    assert m.R4CoreStudent._source_event(d, "MISSING") is None


def test_p5l2_evidence_returns_event_classes(mod):
    s = new(mod)
    s.learn([PA1, PA2, PA3, PE1, PE2])
    s.learn([PB1])
    classes, labels, active, event_classes = s._evidence("mot", PQUERY)
    assert "constructions" in event_classes and "exemplaires" in event_classes
    assert "L1" in event_classes["constructions"] and "L1" in event_classes["exemplaires"]
    assert isinstance(event_classes["constructions"]["L1"], frozenset)


def test_p5l2_independent_pair_rejects_same_event(mod):
    m, _ = mod
    entries = [("constructions", {"PA1"}), ("exemplaires", {"PB1"})]
    event_of_same = {"constructions": frozenset({1}), "exemplaires": frozenset({1})}
    assert not m.R4CoreStudent._independent_pair(entries, event_of=event_of_same)


def test_p5l2_independent_pair_accepts_different_events(mod):
    m, _ = mod
    entries = [("constructions", {"PA1"}), ("exemplaires", {"PB1"})]
    event_of_diff = {"constructions": frozenset({1}), "exemplaires": frozenset({2})}
    assert m.R4CoreStudent._independent_pair(entries, event_of=event_of_diff)


def test_p5l2_independent_pair_no_event_of_uses_item_level(mod):
    m, _ = mod
    entries_disjoint = [("constructions", {"PA1"}), ("exemplaires", {"PB1"})]
    entries_overlap = [("constructions", {"PA1"}), ("exemplaires", {"PA1"})]
    assert m.R4CoreStudent._independent_pair(entries_disjoint, event_of=None)
    assert not m.R4CoreStudent._independent_pair(entries_overlap, event_of=None)


def test_p5l2_same_event_returns_hold(mod):
    s = new(mod)
    s.learn([PA1, PA2, PA3, PB1, PE1, PE2])  # all in event 1 including PB1
    a = s.answer("mot", PQUERY)
    assert a["sense"] == "HOLD", f"expected HOLD (same event), got {a}"
    assert a["reason"] == "PREUVE_INSUFFISANTE"


def test_p5l2_suspended_correction_and_contested_item_feed_no_evidence(mod):
    ok_pb1 = ("K-OK", "PB1", "« vole » marque ce sens (L1), pas l’autre (L2).")
    contest_pb1 = ("K-C1", "PB1", "Révision : lecture L2 admise ici.")
    s = new(mod)
    s.learn([PA1, PA2, PA3, PE1, PE2]); s.learn([PB1])
    s.apply_correction(ok_pb1, PB1); s.apply_correction(contest_pb1, PB1)
    snap = s.derived_snapshot("mot")
    assert snap["statuses"]["K-OK"] == ("OK", True) and snap["statuses"]["K-C1"] == ("CONTESTE", False)
    assert snap["contrasts"] == [] and "PB1" in snap["contested"]
    _, _, active, _ = s._evidence("mot", PQUERY)
    assert "PB1" not in {it[0] for it in active}
    assert s.answer("mot", PQUERY)["sense"] == "HOLD"
    assert "PB1" not in sum(s._p5l2_status("mot", PQUERY)["argmax"].values(), [])


def test_p5l2_one_item_per_label_gives_the_same_argmax_in_both_devices(mod):
    s = new(mod)
    s.learn([PA1, PE1])
    classes, _, _, _ = s._evidence("mot", PQUERY)
    assert classes["constructions"][1]["L1"] == classes["exemplaires"][1]["L1"] == {"PA1"}
    assert s.answer("mot", PQUERY)["sense"] == "HOLD"
    assert not s._p5l2_status("mot", PQUERY)["candidate"]


# --- P5-L2 V1.1 corrective: no response authority, ex aequo sets, fail-closed dependency ------------
# Development tests derived from the consumed V1 audit scenarios; they validate nothing about RED.

PA4 = ("PA4", "mot", "Mon mot tombe dans la vallee sombre.", "L1", "d", "x")
PE3 = ("PE3", "mot", "Notre mot longe la rive.", "L2", "e", "x")
EXL2 = ("EXL2", "mot", "Le mot longe toute la colline.", "L2", "e", "x")
OKL2 = ("K-L2", "EXL2", "« longe » marque ce sens (L2), pas l’autre (L1).")
INJ = [("A", "mot", "Le mot vole souvent.", "L1", "d1", "r1"), ("B", "mot", "Un mot bondit.", "L1", "d2", "r2"),
       ("C", "mot", "La route du mot.", "L2", "d3", "r3"), ("D", "mot", "Ce mot longe.", "L2", "d4", "r4")]
EV_INJ = {"constructions": {"L1": frozenset({1}), "L2": frozenset({1})},
          "exemplaires": {"L1": frozenset({2}), "L2": frozenset({1})}}
HISTORICAL_KEYS = {"sense", "provenance", "reason", "origin", "corpus_hypotheses"}


def base(mod, *corrections):
    s = new(mod)
    s.learn([PA1, PA2, PA3, PE1, PE2]); s.learn([PB1])
    for c, ex in corrections:
        s.apply_correction(c, ex)
    return s


def injected(mod, classes, active=()):
    s = new(mod)
    s.learn(INJ)
    s._evidence = lambda w, q: (classes, ["L1", "L2"], list(active), EV_INJ)
    return s


def outcome(s, q):
    return s.answer("mot", q), s._p5l2_status("mot", q)


def test_v11_p5l2_has_no_response_authority(mod):
    a = base(mod).answer("mot", PQUERY)
    assert a["sense"] == "HOLD" and a["reason"] == "PREUVE_INSUFFISANTE" and set(a) == HISTORICAL_KEYS
    src = SOURCE.read_text(encoding="utf-8")
    assert "CORROBORATION_NIVEAU_2" not in src and "exploratory" not in src
    st = base(mod)._p5l2_status("mot", PQUERY)
    assert st["hypothesis"] == "L1" and st["candidate"] and st["admissible"] is False and st["response_authority"] is False
    assert st["argmax"] == {"constructions": ["PA1"], "exemplaires": ["PB1"]} and st["shared_cue_tokens"] == ["souvent", "vole"]
    assert st["missing_conditions"] == ["P2_NC_TPC", "CONTRE_PREUVE", "P3_FREQUENCE", "RAPPEL"]


def test_v11_g_tau_device_pair_cannot_bypass_the_aggregated_threshold(mod):
    s = base(mod, (OKL2, EXL2))
    a = s.answer("mot", PQUERY)
    assert a["sense"] == "HOLD" and a["reason"] == "PREUVE_INSUFFISANTE"
    classes, _, _, _ = s._evidence("mot", PQUERY)
    assert len(classes) == 3 and sum(c[0]["L1"] for c in classes.values()) / 3 < 0.5


def test_v11_g_delta_and_g_top_injected_evidence_cannot_trigger_an_answer(mod):
    margin = {"constructions": ({"L1": 0.55, "L2": 0.45}, {"L1": {"A"}, "L2": {"C"}}),
              "exemplaires": ({"L1": 0.52, "L2": 0.45}, {"L1": {"B"}, "L2": {"D"}})}
    top = {"constructions": ({"L1": 0.55, "L2": 0.54}, {"L1": {"A"}, "L2": {"C"}}),
           "exemplaires": ({"L1": 0.53, "L2": 0.52}, {"L1": {"B"}, "L2": {"D"}}),
           "contrastes": ({"L1": 0.0, "L2": 0.49}, {"L1": set(), "L2": {"K", "EX"}})}
    for classes in (margin, top):
        a = injected(mod, classes).answer("mot", "Le mot vole.")
        assert a["sense"] == "HOLD" and a["reason"] == "PREUVE_INSUFFISANTE"


def test_v11_historical_gate_still_answers_via_a_contrast_pair_and_enforces_delta(mod):
    ok = {"constructions": ({"L1": 0.6, "L2": 0.1}, {"L1": {"A"}, "L2": {"C"}}),
          "contrastes": ({"L1": 0.6, "L2": 0.0}, {"L1": {"K", "EX"}, "L2": set()})}
    a = injected(mod, ok, active=INJ[:1]).answer("mot", "Le mot vole.")
    assert a["sense"] == "L1" and a["origin"] == "CORRIGE" and a["provenance"] == ["A", "EX", "K"]
    thin = {"constructions": ({"L1": 0.6, "L2": 0.5}, {"L1": {"A"}, "L2": {"C"}}),
            "contrastes": ({"L1": 0.6, "L2": 0.45}, {"L1": {"K", "EX"}, "L2": {"K2", "EX2"}})}
    a = injected(mod, thin, active=INJ[:1]).answer("mot", "Le mot vole.")
    assert a["sense"] == "HOLD" and a["reason"] == "PREUVE_INSUFFISANTE"


def test_v11_one_lesson_split_into_several_learn_calls_is_not_declared_independent(mod):
    s = new(mod)
    for it in (PA1, PA2, PA3, PB1, PE1, PE2):
        s.learn([it])
    a = s.answer("mot", PQUERY)
    assert a["sense"] == "HOLD" and a["reason"] == "PREUVE_INSUFFISANTE"
    # distinct revisions only make the pair a candidate; event granularity itself is NOT_COVERED by the contract
    st = s._p5l2_status("mot", PQUERY)
    assert st["candidate"] and "SOURCE_AUTEUR_INCONNUS" in st["dependency"] and not st["admissible"]


def test_v11_exact_duplicate_in_two_events_is_an_ex_aequo_set(mod):
    s = new(mod)
    s.learn([PA1, PA2, PA3, PE1, PE2]); s.learn([("PA1-B",) + PA1[1:]])
    q = "Le mot vole souvent dans les nuages lointains ce soir."
    classes, _, _, _ = s._evidence("mot", q)
    assert classes["constructions"][1]["L1"] == classes["exemplaires"][1]["L1"] == {"PA1", "PA1-B"}
    assert s.answer("mot", q)["sense"] == "HOLD"
    st = s._p5l2_status("mot", q)
    assert not st["candidate"] and "ITEM_COMMUN" in st["dependency"]


def test_v11_near_duplicate_outcome_does_not_depend_on_identifier_order(mod):
    seen = []
    for rid in ("PA1-R", "PA0-R"):
        s = new(mod)
        s.learn([PA1, PA2, PA3, PE1, PE2])
        s.learn([(rid, "mot", "Le mot vole souvent dans les arbres immenses.", "L1", "d", "x")])
        a = s.answer("mot", PQUERY)
        assert a["sense"] == "HOLD" and a["reason"] == "PREUVE_INSUFFISANTE"
        assert s._evidence("mot", PQUERY)[0]["constructions"][1]["L1"] == {"PA1", rid}
        st = s._p5l2_status("mot", PQUERY)
        seen.append((a, st["candidate"], st["dependency"]))
    assert seen[0] == seen[1] and seen[0][1] is False


def test_v11_same_domain_and_register_is_reported_as_a_dependency(mod):
    a = base(mod).answer("mot", PQUERY)
    assert a["sense"] == "HOLD" and a["reason"] == "PREUVE_INSUFFISANTE"
    st = base(mod)._p5l2_status("mot", PQUERY)
    assert st["candidate"] and st["dependency"] == ["MEME_DOMAINE", "MEME_REGISTRE", "SOURCE_AUTEUR_INCONNUS"]
    s = new(mod)
    s.learn([PA1, PA2, PA3, PE1, PE2]); s.learn([PB1[:4] + ("f", "y")])
    assert s.answer("mot", PQUERY)["sense"] == "HOLD"
    # distinct domain and register: still undecidable, author and source are absent from the item schema
    assert s._p5l2_status("mot", PQUERY)["dependency"] == ["SOURCE_AUTEUR_INCONNUS"]


def test_v11_single_lexical_cue_repeated_across_lessons_is_not_corroboration(mod):
    cue = [("D1", "mot", "Le mot vole loin.", "L1", "d1", "r1"), ("D2", "mot", "Ce mot vole.", "L1", "d2", "r2"),
           ("D5", "mot", "Son mot vole haut.", "L1", "d5", "r5"), ("D3", "mot", "Un mot bondit.", "L1", "d3", "r3")]
    s = new(mod)
    for it in cue:
        s.learn([it])
    s.learn([PE1, PE2])
    a = s.answer("mot", "Le mot vole.")
    assert a["sense"] == "HOLD" and a["reason"] == "PREUVE_INSUFFISANTE"
    st = s._p5l2_status("mot", "Le mot vole.")
    assert st["argmax"] == {"constructions": ["D1"], "exemplaires": ["D2"]} and st["shared_cue_tokens"] == ["vole"]
    # held only because author and source are unknown: a lexical-dependency rule is NOT_COVERED by the contract
    assert st["dependency"] == ["SOURCE_AUTEUR_INCONNUS"]


def test_v11_recall_of_a_lesson_sentence_is_not_corroborated(mod):
    pa0 = ("PA0", "mot", "Le mot vole souvent dans la cour.", "L1", "d", "x")
    pz = ("PZ", "mot", "Le mot vole souvent dans les nuages lointains.", "L1", "d", "x")
    s = new(mod)
    s.learn([pa0, PA2, PA3, PE1, PE2]); s.learn([pz])
    r0 = s.state["revision"]
    a1, a2 = s.answer("mot", pz[2]), s.answer("mot", pz[2])
    assert (a1["sense"], a1["origin"], a1["provenance"]) == ("L1", "RAPPEL", ["PZ"]) and a1 == a2 and s.state["revision"] == r0
    # since V1.6 the recall is answered by RAPPEL (§3.8, TC-R1), never by inference corroboration
    st = s._p5l2_status("mot", pz[2])
    assert st["argmax"]["constructions"] == ["PA0", "PZ"] and not st["candidate"]


def test_v11_contradictory_devices_still_give_conflit(mod):
    s = new(mod)
    s.learn([PA1, PA2, PA3, PA4, PE1, PE2, PE3]); s.learn([PB1[:3] + ("L2", "e", "x")])
    assert s.answer("mot", PQUERY)["reason"] == "CONFLIT"
    s = new(mod)
    s.learn([("PI-1",) + PA1[1:], PA2, PA3, PE1, PE2]); s.learn([("PI-2", "mot", PA1[2], "L2", "e", "x")])
    assert s.answer("mot", "Le mot vole souvent dans les nuages lointains ce soir.")["reason"] == "CONFLIT"


def test_v11_no_active_corpus_or_single_device_holds(mod):
    ex2 = ("S-EX2", "mot", "Il range le mot ici.", "L2", "b", "x")
    s = new(mod)
    s.learn([EX, ex2]); s.apply_correction(CONTEST, EX)
    s.apply_correction(("K-Y", "S-EX2", "Révision : lecture L1 admise ici."), ex2)
    assert s._evidence("mot", "Le mot vole.")[2] == []
    a = s.answer("mot", "Le mot vole.")
    assert a["sense"] == "HOLD" and a["reason"] == "PREUVE_INSUFFISANTE"
    assert base(mod).answer("mot", "Le mot vole souvent.")["sense"] == "HOLD"
    assert s._p5l2_status("mot", "Le mot vole.")["hypothesis"] is None
    assert base(mod)._p5l2_status("mot", "Le mot vole souvent.")["hypothesis"] is None


def test_v11_exercise_introduced_by_a_correction_is_a_derived_observation(mod):
    ok_pb1 = ("K-OK", "PB1", "« vole » marque ce sens (L1), pas l’autre (L2).")
    s = new(mod)
    s.learn([PA1, PA2, PA3, PE1, PE2]); s.apply_correction(ok_pb1, PB1)
    assert s.answer("mot", PQUERY)["sense"] == "HOLD"
    st = s._p5l2_status("mot", PQUERY)
    assert st["argmax"]["exemplaires"] == ["PB1"] and "OBSERVATION_DERIVEE" in st["dependency"]


def test_v11_outcome_is_invariant_to_item_order_within_a_learn_call(mod):
    first = [PA1, PA2, PA3, PE1, PE2]
    outs = []
    for order in (first, first[::-1], first[2:] + first[:2]):
        s = new(mod)
        s.learn(order); s.learn([PB1])
        outs.append(outcome(s, PQUERY))
    assert outs[1] == outs[0] and outs[2] == outs[0]


def test_v11_outcome_is_invariant_to_the_order_of_learn_calls(mod):
    a, b = new(mod), new(mod)
    a.learn([PA1, PA2, PA3, PE1, PE2]); a.learn([PB1])
    b.learn([PB1]); b.learn([PA1, PA2, PA3, PE1, PE2])
    assert outcome(a, PQUERY) == outcome(b, PQUERY)


# --- R4.4 provenance (V1.2): observation records, pair relation, explicit device-pair policy ----------
# Development tests. Source independence is never inferred: the item schema has no author or source field.

PT = ("PT", "mot", "Le mot vole souvent sur les toits gris.", "L1", "d", "x")
EXC = ("EXC", "mot", "Le mot vole souvent dans les arbres immenses.", "L1", "d", "x")
OK_EXC = ("K-OKC", "EXC", "« vole » marque ce sens (L1), pas l’autre (L2).")
OK_PB1 = ("K-OK", "PB1", "« vole » marque ce sens (L1), pas l’autre (L2).")
RELATIONS = ("SAME_EVENT", "UNKNOWN_DEPENDENCY", "DISTINCT_PEDAGOGICAL_EVENTS", "VERIFIED_INDEPENDENT_SOURCES")


def device_relation(s, q=PQUERY):
    return s._p5l2_status("mot", q)["evidence_status"]


def test_v12_historical_items_carry_no_invented_provenance(mod, tmp_path):
    m, _ = mod
    s = new(mod)
    s.learn(SYN + [EX]); s.apply_correction(OKC, EX)
    d = s._derive()
    assert s._observation_provenance(d, "S-1") == {"observation_id": "S-1", "teaching_event_id": 1, "teaching_event_kind": "learn",
                                                   "lesson_id": None, "source_id": None, "derived_from": None}
    assert s._observation_provenance(d, "K-1") == {"observation_id": "K-1", "teaching_event_id": 2, "teaching_event_kind": "correction",
                                                   "lesson_id": None, "source_id": None, "derived_from": ["S-EX"]}
    s.save(tmp_path)
    r = m.R4CoreStudent.load(tmp_path, lexicon_dir=str(SANDBOX / "__no_lexicon__"))
    assert r._observation_provenance(r._derive(), "K-1") == s._observation_provenance(d, "K-1")


def test_v12_traits_of_a_single_lesson_never_count_twice(mod):
    s = new(mod)
    s.learn([PA1, PE1])
    assert s._pair_relation(s._derive(), {"PA1"}, {"PA1"}) == "SAME_EVENT"
    s = new(mod)
    s.learn([PA1, PA2, PA3, PB1, PE1, PE2])
    assert s._pair_relation(s._derive(), {"PA1"}, {"PB1"}) == "SAME_EVENT" == device_relation(s)
    assert s.answer("mot", PQUERY)["sense"] == "HOLD"


def test_v12_real_teaching_protocol_makes_every_device_pair_one_event(mod):
    s = new(mod)
    s.learn(D.E_LESSONS + D.E_EXERCISES)          # as Teacher.teach: one teaching set, one learn call
    d = s._derive()
    ids = [it[0] for it in D.E_LESSONS + D.E_EXERCISES]
    assert {s._observation_provenance(d, i)["teaching_event_id"] for i in ids} == {1}
    assert all(s._pair_relation(d, {a}, {b}) == "SAME_EVENT" for a in ids for b in ids)


def test_v12_lessons_without_a_recorded_teacher_or_source_are_not_verified_independent(mod):
    s = base(mod)
    d = s._derive()
    assert [s._observation_provenance(d, i)["source_id"] for i in ("PA1", "PB1")] == [None, None]
    assert device_relation(s) == "DISTINCT_PEDAGOGICAL_EVENTS"
    assert not s._device_pair_is_independent(device_relation(s)) and s.answer("mot", PQUERY)["sense"] == "HOLD"


def test_v12_distinct_events_of_one_curriculum_are_only_pedagogical_replication(mod):
    s = new(mod)
    for it in (PA1, PA2, PA3, PB1, PE1, PE2):
        s.learn([it])
    assert device_relation(s) == "DISTINCT_PEDAGOGICAL_EVENTS" and s.answer("mot", PQUERY)["sense"] == "HOLD"


def test_v12_common_parent_and_undeclared_parent_are_dependencies(mod):
    s = new(mod)
    s.learn(SYN + [EX]); s.apply_correction(OKC, EX)
    s.apply_correction(("K-2", "S-EX", "« haut » marque ce sens (L1), pas l’autre (L2)."), EX)
    assert s._pair_relation(s._derive(), {"K-1"}, {"K-2"}) == "SAME_EVENT"
    s = new(mod)
    s.learn([PA1, PA2, PA3, PE1, PE2]); s.apply_correction(OK_PB1, PB1)
    d = s._derive()
    assert s._observation_provenance(d, "PB1")["teaching_event_kind"] == "correction"
    assert s._pair_relation(d, {"PA1"}, {"PB1"}) == "UNKNOWN_DEPENDENCY" == device_relation(s)
    assert s.answer("mot", PQUERY)["sense"] == "HOLD"


def test_v12_recall_creates_no_new_evidential_event(mod):
    s = base(mod)
    before = (s.state["revision"], len(s.state["events"]), device_relation(s))
    s.answer("mot", PQUERY); s.answer("mot", PQUERY); s.retrieve(word="mot"); s.history("mot", "L1")
    assert (s.state["revision"], len(s.state["events"]), device_relation(s)) == before
    s.learn([PB1])
    assert s._observation_provenance(s._derive(), "PB1")["teaching_event_id"] == 2 and device_relation(s) == before[2]


def test_v12_invalidating_correction_withdraws_the_observation(mod):
    s = base(mod)
    assert device_relation(s) == "DISTINCT_PEDAGOGICAL_EVENTS"
    s.apply_correction(("K-C1", "PB1", "Révision : lecture L2 admise ici."), PB1)
    assert device_relation(s) is None and s.answer("mot", PQUERY)["sense"] == "HOLD"
    assert s._observation_provenance(s._derive(), "PB1")["teaching_event_id"] == 2
    assert next(h for h in s.retrieve(word="mot") if h["id"] == "PB1")["status"] == "CONTESTE"


def test_v12_contrast_pair_still_answers_corrige_on_real_sentences(mod):
    s = new(mod)
    s.learn([PT, EXC, PA2, PA3, PE1, PE2]); s.apply_correction(OK_EXC, EXC)
    a = s.answer("mot", PQUERY)
    assert (a["sense"], a["origin"], a["provenance"]) == ("L1", "CORRIGE", ["EXC", "K-OKC", "PT"])
    assert device_relation(s) == "SAME_EVENT"


def test_v12_device_pair_policy_never_promotes_unknown_or_replicated_evidence(mod):
    m, _ = mod
    assert [r for r in RELATIONS if m.R4CoreStudent._device_pair_is_independent(r)] == ["VERIFIED_INDEPENDENT_SOURCES"]
    s = new(mod)
    s.learn([PA1, PA2, PA3, PE1, PE2]); s.learn([PB1[:4] + ("f", "y")])
    assert device_relation(s) == "DISTINCT_PEDAGOGICAL_EVENTS" and s.answer("mot", PQUERY)["sense"] == "HOLD"


def test_v12_historical_gate_does_not_read_p5l2_dependency_causes(mod):
    s = base(mod)
    s._device_dependency = lambda *args: []
    a = s.answer("mot", PQUERY)
    assert a["sense"] == "HOLD" and a["reason"] == "PREUVE_INSUFFISANTE"


# --- R4.4 provenance (V1.3): optional teaching metadata, lesson identity, lineage --------------------
# Development tests. Metadata below is synthetic and attested by the caller; nothing is inferred.

def test_v13_several_items_of_one_lesson_are_one_pedagogical_source(mod):
    s = new(mod)
    s.learn([PA1, PA2, PA3, PE1, PE2], provenance={"PA1": {"lesson_id": "LEC-1"}})
    s.learn([PB1], provenance={"PB1": {"lesson_id": "LEC-1"}})
    assert device_relation(s) == "SAME_EVENT" and device_relation(base(mod)) == "DISTINCT_PEDAGOGICAL_EVENTS"
    st = s._p5l2_status("mot", PQUERY)
    assert not st["candidate"] and "MEME_LECON" in st["dependency"] and s.answer("mot", PQUERY)["sense"] == "HOLD"


def test_v13_two_lessons_in_one_learn_call_are_not_presumed_one_lesson(mod):
    batch = [PA1, PA2, PA3, PB1, PE1, PE2]
    s = new(mod)
    s.learn(batch, provenance={"PA1": {"lesson_id": "LEC-A"}, "PB1": {"lesson_id": "LEC-B"}})
    assert device_relation(s) == "DISTINCT_PEDAGOGICAL_EVENTS" and s.answer("mot", PQUERY)["sense"] == "HOLD"
    s = new(mod)
    s.learn(batch, provenance={"PA1": {"lesson_id": "LEC-A"}})
    # one lesson left undeclared: the shared delivery still counts as a dependency
    assert device_relation(s) == "SAME_EVENT" and s.answer("mot", PQUERY)["sense"] == "HOLD"


def test_v13_two_deliveries_of_the_same_lesson_create_no_new_source(mod):
    s = new(mod)
    s.learn([PA1, PA2, PA3, PE1, PE2])
    s.learn([PB1], provenance={"PB1": {"lesson_id": "LEC-B", "source_id": "SRC-1"}})
    s.learn([PB1], provenance={"PB1": {"lesson_id": "LEC-B", "source_id": "SRC-2"}})
    rec = s._provenance_record(s._derive(), "PB1")
    assert (rec["teaching_event_id"], rec["occurrences"], rec["source_id"]) == (2, [2, 3], "SRC-1")
    s.learn([("PB2",) + PB1[1:]], provenance={"PB2": {"lesson_id": "LEC-B"}})
    assert s._pair_relation(s._derive(), {"PB1"}, {"PB2"}) == "SAME_EVENT"
    assert s.answer("mot", PQUERY)["sense"] == "HOLD"


def test_v13_same_author_distinct_lessons_is_pedagogical_replication_only(mod):
    s = new(mod)
    s.learn([PA1, PA2, PA3, PE1, PE2], provenance={"PA1": {"lesson_id": "LEC-A", "author_id": "AUT-1"}})
    s.learn([PB1], provenance={"PB1": {"lesson_id": "LEC-B", "author_id": "AUT-1"}})
    st = s._p5l2_status("mot", PQUERY)
    assert st["evidence_status"] == "DISTINCT_PEDAGOGICAL_EVENTS" and "MEME_AUTEUR" in st["dependency"]
    assert st["admissible"] is False and s.answer("mot", PQUERY)["sense"] == "HOLD"


def test_v13_unknown_sources_stay_unknown_and_are_reported(mod):
    s = base(mod)
    rec = s._provenance_record(s._derive(), "PB1")
    assert (rec["lesson_id"], rec["source_id"], rec["author_id"]) == (None, None, None)
    assert "SOURCE_AUTEUR_INCONNUS" in s._p5l2_status("mot", PQUERY)["dependency"]


def test_v13_distinct_source_ids_never_prove_independence(mod):
    s = new(mod)
    s.learn([PA1, PA2, PA3, PE1, PE2], provenance={"PA1": {"lesson_id": "LEC-A", "source_id": "SRC-A", "author_id": "AUT-A"}})
    s.learn([PB1], provenance={"PB1": {"lesson_id": "LEC-B", "source_id": "SRC-B", "author_id": "AUT-B"}})
    st = s._p5l2_status("mot", PQUERY)
    assert st["evidence_status"] == "DISTINCT_PEDAGOGICAL_EVENTS" and not s._device_pair_is_independent(st["evidence_status"])
    assert "SOURCE_AUTEUR_INCONNUS" not in st["dependency"] and st["admissible"] is False and st["response_authority"] is False
    assert s.answer("mot", PQUERY) == base(mod).answer("mot", PQUERY)


def test_v13_correction_lineage_links_the_exercise_to_its_source_item(mod):
    ok_pb1 = ("K-OK", "PB1", "« vole » marque ce sens (L1), pas l’autre (L2).")
    s = new(mod)
    s.learn([PA1, PA2, PA3, PE1, PE2]); s.apply_correction(ok_pb1, PB1, provenance={"PB1": {"derived_from": ["PA1"]}})
    d = s._derive()
    assert s._provenance_record(d, "PB1")["derived_from"] == ["PA1"] and s._lineage(d, {"K-OK"}) == {"K-OK", "PB1", "PA1"}
    assert s._pair_relation(d, {"PA1"}, {"PB1"}) == "SAME_EVENT" == device_relation(s)
    s = new(mod)
    s.learn([PA1, PA2, PA3, PE1, PE2]); s.apply_correction(ok_pb1, PB1, provenance={"PB1": {"derived_from": ["E-SRC-9"]}})
    # the origin lesson is declared and not shared: the exercise is no longer an UNKNOWN_DEPENDENCY
    assert device_relation(s) == "DISTINCT_PEDAGOGICAL_EVENTS" and s.answer("mot", PQUERY)["sense"] == "HOLD"


def test_v13_duplicated_event_adds_occurrences_but_no_observation(mod):
    s = base(mod)
    before = (s.answer("mot", PQUERY), device_relation(s), sorted(s._derive()["items"]))
    s.learn([PA1, PA2, PA3, PE1, PE2])
    rec = s._provenance_record(s._derive(), "PA1")
    assert (rec["teaching_event_id"], rec["occurrences"]) == (1, [1, 3])
    assert (s.answer("mot", PQUERY), device_relation(s), sorted(s._derive()["items"])) == before


def test_v13_provenance_survives_save_reload_and_replay(mod, tmp_path):
    m, st = mod
    s = new(mod)
    s.learn([PA1, PA2, PA3, PE1, PE2], provenance={"PA1": {"lesson_id": "LEC-A", "author_id": "AUT-1"}})
    s.learn([PB1], provenance={"PB1": {"lesson_id": "LEC-B", "derived_from": ["PZZ", "PA9"]}})
    s.save(tmp_path)
    r = m.R4CoreStudent.load(tmp_path, lexicon_dir=str(SANDBOX / "__no_lexicon__"))
    assert all(r._provenance_record(r._derive(), i) == s._provenance_record(s._derive(), i) for i in ("PA1", "PB1"))
    assert r._provenance_record(r._derive(), "PB1")["derived_from"] == ["PA9", "PZZ"]
    assert r._provenance_record(r._derive(1), "PA1")["occurrences"] == [1] and "PB1" not in r._derive(1)["items"]
    f = tmp_path / m.STATE_FILE
    f.write_bytes(f.read_bytes().replace(b"LEC-A", b"LEC-X"))
    with pytest.raises(st.StateIntegrityError):
        m.R4CoreStudent.load(tmp_path, lexicon_dir=str(SANDBOX / "__no_lexicon__"))


def test_v13_historical_entries_keep_their_state_shape_and_unknown_metadata(mod):
    s = new(mod)
    s.learn(SYN + [EX]); s.apply_correction(OKC, EX)
    assert all(set(ev) == {"revision", "kind", "payload"} for ev in s.state["events"])
    d = s._derive()
    assert s._provenance_record(d, "S-EX") == {"observation_id": "S-EX", "item_id": "S-EX", "teaching_event_id": 1,
                                               "teaching_event_kind": "learn", "occurrences": [1, 2], "lesson_id": None,
                                               "source_id": None, "author_id": None, "derived_from": None}
    assert s._provenance_record(d, "K-1")["item_id"] == "S-EX"


def test_v13_metadata_never_changes_an_answer_or_grants_authority(mod):
    def full(batch):
        return {it[0]: {"lesson_id": "LEC-" + it[0], "source_id": "SRC-" + it[0], "author_id": "AUT-" + it[0]} for it in batch}
    cases = (([[PA1, PA2, PA3, PE1, PE2], [PB1]], None),
             ([[PT, EXC, PA2, PA3, PE1, PE2]], (OK_EXC, EXC)),
             ([[x] for x in (PA1, PA2, PA3, PB1, PE1, PE2)], None))
    for batches, corr in cases:
        plain, tagged = new(mod), new(mod)
        for b in batches:
            plain.learn(b); tagged.learn(b, provenance=full(b))
        if corr:
            plain.apply_correction(*corr); tagged.apply_correction(*corr)
        assert tagged.answer("mot", PQUERY) == plain.answer("mot", PQUERY)
        st = tagged._p5l2_status("mot", PQUERY)
        assert st["admissible"] is False and st["response_authority"] is False


def test_v13_provenance_is_validated_at_the_boundary(mod):
    s = new(mod)
    for bad in ({"ZZ": {"lesson_id": "LEC"}}, {"PA1": {"teacher": "T"}}, {"PA1": {"lesson_id": ""}},
                {"PA1": {"derived_from": "PA2"}}, {"PA1": "LEC"}):
        with pytest.raises(ValueError):
            s.learn([PA1], provenance=bad)
    assert s.state["revision"] == 0
    with pytest.raises(ValueError):
        s.apply_correction(OKC, EX, provenance={"S-1": {"lesson_id": "LEC"}})
    s.learn([PA1], provenance={"PA1": {"lesson_id": None}})
    assert set(s.state["events"][0]) == {"revision", "kind", "payload"}


# --- R4.4 RAPPEL (V1.6: preregistration §3.8, contract gaps closure, gap 4) -------------------------------
# Development tests. RAPPEL answers the label of an identical active exemplar: memory, never new evidence.

def test_v16_rappel_answers_the_label_of_the_identical_active_exemplar(mod):
    a = base(mod).answer("mot", PB1[2])
    assert (a["sense"], a["origin"], a["reason"], a["provenance"]) == ("L1", "RAPPEL", None, ["PB1"])


def test_v16_rappel_fingerprint_folds_case_accents_final_punctuation_and_spaces(mod):
    s = new(mod)
    s.learn(SYN + [EX])
    for q in ("LE MOT VOLE TRES HAUT !", "  Le  mot   vole très haut ?", "le mot vole très haut"):
        assert s.answer("mot", q)["origin"] == "RAPPEL", q
    # one extra word, an internal comma or one different word: not a recall, normal inference
    for q in ("Le mot vole très haut ici.", "Le mot vole, très haut.", "Le mot vole très bas."):
        assert s.answer("mot", q)["origin"] != "RAPPEL", q


def test_v16_repeated_rappel_creates_no_event_and_no_new_evidence(mod):
    m, _ = mod
    s = base(mod)
    state, evidence = m.canonical(s.state), s._evidence("mot", PQUERY)
    first = s.answer("mot", PB1[2])
    assert all(s.answer("mot", PB1[2]) == first for _ in range(3))
    assert m.canonical(s.state) == state and s._evidence("mot", PQUERY) == evidence
    assert s._provenance_record(s._derive(), "PB1")["occurrences"] == [2]


def test_v16_two_recalls_of_one_teaching_event_stay_separate_observations(mod):
    s = new(mod)
    s.learn([PA1, PA2, PA3, PB1, PE1, PE2])
    assert s.answer("mot", PA1[2])["provenance"] == ["PA1"] and s.answer("mot", PB1[2])["provenance"] == ["PB1"]
    ra, rb = s._recall("mot", PA1[2]), s._recall("mot", PB1[2])
    assert ra["provenance"][0]["teaching_event_id"] == rb["provenance"][0]["teaching_event_id"] == 1
    assert s.state["revision"] == 1


def test_v16_corrected_exercise_is_recalled_with_its_label_and_correction_filiation(mod):
    s = new(mod)
    s.learn(SYN + [EX]); s.apply_correction(OKC, EX)
    a = s.answer("mot", EX[2])
    assert (a["sense"], a["origin"], a["provenance"]) == ("L1", "RAPPEL", ["S-EX"])
    assert s._recall("mot", EX[2])["memory"][0]["corrections"] == [{"id": "K-1", "status": "OK"}]
    assert s._provenance_record(s._derive(), "K-1")["derived_from"] == ["S-EX"]


def test_v16_contested_or_suspended_exemplar_is_not_recalled(mod):
    s = new(mod)
    s.learn(SYN + [EX]); s.apply_correction(OKC, EX); s.apply_correction(CONTEST, EX)
    snap = s.derived_snapshot("mot")
    assert snap["statuses"]["K-1"] == ("OK", True) and "S-EX" in snap["contested"]
    assert s._recall("mot", EX[2])["status"] is None
    a = s.answer("mot", EX[2])
    assert a["origin"] != "RAPPEL" and a["sense"] == "HOLD"


def test_v16_identical_sentence_with_two_labels_is_conflit(mod):
    s = new(mod)
    s.learn([("PI-1",) + PA1[1:], PA2, PA3, PE1, PE2]); s.learn([("PI-2", "mot", PA1[2], "L2", "e", "x")])
    assert s._recall("mot", PA1[2])["status"] == "CONFLIT" and s.answer("mot", PA1[2])["reason"] == "CONFLIT"


def test_v16_historical_contradiction_survives_memory_recall_and_replay(mod):
    exercises = {e[0]: e for e in D.E_EXERCISES}
    target = exercises[D.CONTRADICTION[1]]
    s = new(mod)
    s.learn(D.E_LESSONS + D.E_EXERCISES)
    for c in D.C_CORRECTIONS:
        s.apply_correction(c, exercises[c[1]])
    assert (s.answer("force", target[2])["sense"], s.answer("force", target[2])["origin"]) == (target[3], "RAPPEL")
    s.apply_correction(D.CONTRADICTION, target)
    assert s._recall("force", target[2])["status"] is None and s.answer("force", target[2])["origin"] != "RAPPEL"
    assert s._recall("force", target[2], as_of=s.state["revision"] - 1)["status"] == "RAPPEL"
    assert any(entry["revision"] == s.state["revision"] for entry in s.reinterpretation_journal())


def test_v16_rappel_keeps_unknown_and_declared_provenance_unchanged(mod):
    s = new(mod)
    s.learn([PA1, PA2, PA3, PE1, PE2], provenance={"PA1": {"lesson_id": "LEC-A", "source_id": "SRC-A"}})
    s.learn([PB1])
    ra, rb = s._recall("mot", PA1[2])["provenance"][0], s._recall("mot", PB1[2])["provenance"][0]
    assert (ra["lesson_id"], ra["source_id"], ra["author_id"]) == ("LEC-A", "SRC-A", None)
    assert (rb["lesson_id"], rb["source_id"], rb["author_id"]) == (None, None, None)
    assert s._pair_relation(s._derive(), {"PA1"}, {"PB1"}) == "DISTINCT_PEDAGOGICAL_EVENTS"


def test_v16_rappel_survives_save_and_reload(mod, tmp_path):
    m, _ = mod
    s = base(mod)
    before = [s.answer("mot", it[2]) for it in (PA1, PB1, PE1)]
    s.save(tmp_path)
    r = m.R4CoreStudent.load(tmp_path, lexicon_dir=str(SANDBOX / "__no_lexicon__"))
    assert [r.answer("mot", it[2]) for it in (PA1, PB1, PE1)] == before and all(a["origin"] == "RAPPEL" for a in before)


def test_v16_exercise_received_with_a_correction_is_recalled_with_its_filiation(mod):
    s = new(mod)
    s.learn([PA1, PA2, PA3, PE1, PE2]); s.apply_correction(OK_PB1, PB1, provenance={"PB1": {"derived_from": ["PA1"]}})
    r = s._recall("mot", PB1[2])
    assert r["status"] == "RAPPEL" and r["provenance"][0]["teaching_event_kind"] == "correction"
    assert r["provenance"][0]["derived_from"] == ["PA1"] and s._lineage(s._derive(), {"K-OK"}) == {"K-OK", "PB1", "PA1"}


def test_v16_one_lesson_delivered_twice_is_recalled_once(mod):
    s = base(mod)
    s.learn([PB1])
    assert s.answer("mot", PB1[2])["provenance"] == ["PB1"]
    r = s._recall("mot", PB1[2])
    assert r["observations"] == ["PB1"] and r["provenance"][0]["occurrences"] == [2, 3]


def test_v16_rappel_never_changes_a_non_identical_answer(mod):
    s = new(mod)
    s.learn([PT, EXC, PA2, PA3, PE1, PE2]); s.apply_correction(OK_EXC, EXC)
    a = s.answer("mot", PQUERY)
    assert (a["sense"], a["origin"]) == ("L1", "CORRIGE") and base(mod).answer("mot", PQUERY)["sense"] == "HOLD"
    assert s._recall("mot", PQUERY)["status"] is None


def test_v16_rappel_takes_precedence_over_an_unknown_determinant(mod):
    s = new(mod, lexicon=True)
    s.learn([("Z-1", "mot", "Le mot zorbulique vole haut.", "L1", "a", "x"), ("Z-2", "mot", "Elle range le mot.", "L2", "b", "x")])
    assert s.answer("mot", "Le mot zorbulique vole haut.")["origin"] == "RAPPEL"
    assert s.answer("mot", "Le mot zorbulique vole bas.")["reason"] == "MOT_INCONNU"


# --- R4.4 P2 / LOO-CAL (V1.7): admissible LOO units only; class votes are blocked on P3 and C1 --------------
# Development tests. N_c / TP_c need the P3 and C1 filters recomputed per iteration (preregistration §3.4).

def plan_units(plan):
    return {u["observation_id"]: u for u in plan["units"]}


def test_v17_loo_cal_units_are_the_active_observations_with_their_b2_removal(mod):
    s = new(mod)
    s.learn(SYN + [EX]); s.apply_correction(OKC, EX)
    plan = s._loo_cal_plan("mot")
    units = plan_units(plan)
    assert sorted(units) == ["S-1", "S-2", "S-3", "S-4", "S-EX"] and plan["excluded"] == []
    assert units["S-EX"]["removed"] == ["K-1", "S-EX"] and units["S-1"]["removed"] == ["S-1"]
    assert {k: u["label"] for k, u in units.items()} == {it[0]: it[3] for it in SYN + [EX]}
    assert units["S-1"]["remaining"] == {"L1": 2, "L2": 2}


def test_v17_class_votes_are_blocked_on_p3_and_the_relevance_filter(mod):
    plan = base(mod)._loo_cal_plan("mot")
    assert plan["votes"] == "NOT_COMPUTED" and plan["missing"] == ["P3_FILTER", "C1_FILTER"]
    assert not any(k in plan for k in ("N_c", "TP_c", "r_c")) and not any(k in u for u in plan["units"] for k in ("N_c", "TP_c"))


def test_v17_untaught_word_has_no_loo_unit(mod):
    assert base(mod)._loo_cal_plan("zorp") == {"units": [], "excluded": [], "votes": "NOT_COMPUTED",
                                               "missing": ["P3_FILTER", "C1_FILTER"]}


def test_v17_label_with_a_single_observation_leaves_no_exemplar_of_its_label(mod):
    s = new(mod)
    s.learn([PA1, PA2, PE1])
    units = plan_units(s._loo_cal_plan("mot"))
    assert units["PE1"]["remaining"] == {"L1": 2} and units["PA1"]["remaining"] == {"L1": 1, "L2": 1}


def test_v17_label_without_admissible_observation_is_entirely_excluded(mod):
    ex2 = ("S-EX2", "mot", "Il range le mot ici.", "L2", "b", "x")
    s = new(mod)
    s.learn([EX, ex2]); s.apply_correction(CONTEST, EX)
    s.apply_correction(("K-Y", "S-EX2", "Révision : lecture L1 admise ici."), ex2)
    plan = s._loo_cal_plan("mot")
    assert plan["units"] == [] and plan["excluded"] == [{"observation_id": "S-EX", "reason": "CONTESTE"},
                                                        {"observation_id": "S-EX2", "reason": "CONTESTE"}]


def test_v17_contested_and_suspended_observations_are_not_units(mod):
    s = new(mod)
    s.learn(SYN + [EX]); s.apply_correction(OKC, EX); s.apply_correction(CONTEST, EX)
    assert s.derived_snapshot("mot")["statuses"]["K-1"] == ("OK", True)
    plan = s._loo_cal_plan("mot")
    assert "S-EX" not in plan_units(plan) and {"observation_id": "S-EX", "reason": "CONTESTE"} in plan["excluded"]
    assert all("K-1" not in u["removed"] for u in plan["units"])


def test_v17_a_duplicate_of_an_active_exemplar_is_excluded_as_rappel(mod):
    s = new(mod)
    s.learn([PA1, PA2, PE1, PE2]); s.learn([("PA1-B",) + PA1[1:]])
    plan = s._loo_cal_plan("mot")
    assert {"observation_id": "PA1", "reason": "RAPPEL"} in plan["excluded"]
    assert {"observation_id": "PA1-B", "reason": "RAPPEL"} in plan["excluded"]
    assert sorted(plan_units(plan)) == ["PA2", "PE1", "PE2"]


def test_v17_repeated_delivery_is_one_unit(mod):
    s = base(mod)
    s.learn([PB1])
    plan = s._loo_cal_plan("mot")
    assert [u["observation_id"] for u in plan["units"]].count("PB1") == 1 and plan["excluded"] == []


def test_v17_b2_removal_takes_every_correction_on_the_held_out_item(mod):
    exercises = {e[0]: e for e in D.E_EXERCISES}
    s = new(mod)
    s.learn(D.E_LESSONS + D.E_EXERCISES)
    for c in D.C_CORRECTIONS:
        s.apply_correction(c, exercises[c[1]])
    s.apply_correction(("C-Z", "EX-F1", "Phrase sans étiquette."), exercises["EX-F1"])     # NON_RECONNU: EX-F1 stays active
    units = plan_units(s._loo_cal_plan("force"))
    assert len(units) == 18 and units["EX-F1"]["removed"] == ["C-1", "C-Z", "EX-F1"]
    assert units["E-F1-1"]["removed"] == ["E-F1-1"]


def test_v17_declared_descendants_are_reported_not_silently_removed(mod):
    s = new(mod)
    s.learn([PA1, PA2, PA3, PE1, PE2]); s.apply_correction(OK_PB1, PB1, provenance={"PB1": {"derived_from": ["PA1"]}})
    units = plan_units(s._loo_cal_plan("mot"))
    assert units["PA1"]["declared_descendants"] == ["K-OK", "PB1"] and units["PA1"]["removed"] == ["PA1"]
    assert units["PB1"]["removed"] == ["K-OK", "PB1"] and units["PB1"]["declared_descendants"] == []


def test_v17_loo_cal_plan_survives_save_reload_and_replays_the_past(mod, tmp_path):
    m, _ = mod
    s = new(mod)
    s.learn(SYN + [EX]); s.apply_correction(OKC, EX); s.apply_correction(CONTEST, EX)
    plan = s._loo_cal_plan("mot")
    s.save(tmp_path)
    r = m.R4CoreStudent.load(tmp_path, lexicon_dir=str(SANDBOX / "__no_lexicon__"))
    assert r._loo_cal_plan("mot") == plan and "S-EX" in plan_units(r._loo_cal_plan("mot", as_of=2))


def test_v17_loo_cal_plan_does_not_depend_on_the_order_of_teaching(mod):
    a, b = new(mod), new(mod)
    a.learn(SYN + [EX]); a.apply_correction(OKC, EX); a.apply_correction(CONTEST, EX)
    b.learn([EX] + SYN[::-1]); b.apply_correction(CONTEST, EX); b.apply_correction(OKC, EX)
    assert a._loo_cal_plan("mot") == b._loo_cal_plan("mot")


def test_v17_loo_cal_plan_changes_no_answer_and_no_state(mod):
    m, _ = mod
    s = new(mod)
    s.learn([PT, EXC, PA2, PA3, PE1, PE2]); s.apply_correction(OK_EXC, EXC)
    state, before = m.canonical(s.state), [s.answer("mot", q) for q in (PQUERY, PT[2])]
    s._loo_cal_plan("mot")
    assert m.canonical(s.state) == state and [s.answer("mot", q) for q in (PQUERY, PT[2])] == before
    assert (before[0]["origin"], before[1]["origin"]) == ("CORRIGE", "RAPPEL")


# --- R4.4 V1.8: lexical relevance filter C1 (preregistration §3.6, D1/D2), informative input of LOO-CAL ----------
# Development tests. Gloss scope SENTENCE_PLUS_OK_GLOSSES (founder arbitration). P3, N_c and TP_c are not built.

GA = ("GA", "mot", "Le mot vole vers la falaise.", "L1", "a", "x")
GB = ("GB", "mot", "Un mot vole vers la plage.", "L1", "a", "x")
GC = ("GC", "mot", "Elle range le mot dans la barque.", "L2", "b", "x")
GD = ("GD", "mot", "Il range un mot dans la caisse.", "L2", "b", "x")
GE = ("GE", "mot", "On range ce mot sous la table.", "L2", "b", "x")
K_GA = ("K-GA", "GA", "« vole » marque ce sens (L1) malgré la rafale, pas l’autre (L2).")
K_GA2 = ("K-GA2", "GA", "« vole » garde ce sens (L1) sous la rafale et vers la falaise.")
K_GE = ("K-GE", "GE", "« range » marque ce sens (L2) près du quai, pas l’autre (L1).")
X_GE = ("X-GE", "GE", "Révision : lecture L1 admise ici.")


def gloss_student(mod, extra=(), drop=frozenset()):
    """GA carries two OK glosses; GE is contested, so its OK correction K-GE is SUSPENDU. drop = a B2 removal."""
    s = new(mod)
    s.learn([it for it in (GA, GB, GC, GD, GE) if it[0] not in drop])
    for c, ex in [(K_GA, GA), (K_GA2, GA), (K_GE, GE), (X_GE, GE), *extra]:
        if c[0] not in drop:
            s.apply_correction(c, ex)
    return s


def relevance_units(out):
    return {u["observation_id"]: u for u in out["units"]}


def item_traits(out):
    return {k: set(v["sentence"]).union(*map(set, v["glosses"].values())) for k, v in out["items"].items()}


def carried(m, n, f):
    """n training items, the first f of which carry the trait t; every item also carries a trait of its own."""
    return m.lexical_relevance({"I%d" % i: {"u%d" % i} | ({"t"} if i < f else set()) for i in range(n)})


def names_in(function):
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == function)
    return {n.id for n in ast.walk(fn) if isinstance(n, ast.Name)} | {n.attr for n in ast.walk(fn) if isinstance(n, ast.Attribute)}


def test_v18_threshold_is_strictly_greater_than_half(mod):
    m, _ = mod
    # TC-A1 (D1): M=6, F=3 is kept. TC-C4 (historical F >= M/2: excluded) is obsolete, kept in the deviation record.
    expected = {(6, 3): "kept", (6, 4): "excluded", (4, 2): "kept", (5, 3): "excluded", (3, 2): "excluded",
                (2, 2): "excluded", (2, 1): "kept"}
    for (n, f), side in expected.items():
        out = carried(m, n, f)
        assert (out["m"], out["bypass"], out["frequencies"]["t"]) == (n, False, f) and "t" in out[side], (n, f)


def test_v18_training_sets_of_at_most_one_item_bypass_the_filter(mod):
    m, _ = mod
    assert m.lexical_relevance({"I0": ["t", "u"]}) == {"m": 1, "bypass": True, "frequencies": {"t": 1, "u": 1},
                                                       "kept": ["t", "u"], "excluded": []}
    assert m.lexical_relevance({}) == {"m": 0, "bypass": True, "frequencies": {}, "kept": [], "excluded": []}


def test_v18_a_trait_carried_by_every_training_item_is_excluded(mod):
    m, _ = mod
    out = m.lexical_relevance({"I%d" % i: {"t", "u%d" % i} for i in range(4)})
    assert out["excluded"] == ["t"] and out["kept"] == ["u0", "u1", "u2", "u3"]


def test_v18_filter_is_pure_and_counts_each_item_once(mod):
    m, _ = mod
    traits = {"I0": ["t", "t", "u"], "I1": ("u",), "I2": {"v"}}
    out = m.lexical_relevance(traits)
    assert out["frequencies"] == {"t": 1, "u": 2, "v": 1} and out["excluded"] == ["u"]
    assert traits == {"I0": ["t", "t", "u"], "I1": ("u",), "I2": {"v"}}
    assert m.lexical_relevance(dict(reversed(list(traits.items())))) == out


def test_v18_item_traits_join_the_sentence_and_its_attached_ok_glosses(mod):
    out = gloss_student(mod)._loo_cal_relevance("mot")
    ga = out["items"]["GA"]
    assert sorted(out["items"]) == ["GA", "GB", "GC", "GD"] and ga["label"] == "L1"
    assert ga["sentence"] == ["falaise", "vole"] and sorted(ga["glosses"]) == ["K-GA", "K-GA2"]
    assert "rafale" in ga["glosses"]["K-GA"] and {"rafale", "falaise"} <= set(ga["glosses"]["K-GA2"])
    assert {r["id"]: (r["exercise"], r["status"], r["attached"], r["counted"]) for r in out["corrections"]} == {
        "K-GA": ("GA", "OK", True, True), "K-GA2": ("GA", "OK", True, True),
        "K-GE": ("GE", "SUSPENDU", True, False), "X-GE": ("GE", "CONTESTE", True, False)}


def test_v18_a_trait_in_the_sentence_and_in_several_glosses_counts_once_for_its_item(mod):
    freq = relevance_units(gloss_student(mod)._loo_cal_relevance("mot"))["GB"]["relevance"]["frequencies"]
    assert freq["falaise"] == 1 and freq["rafale"] == 1 and freq["sens"] == 1       # GA: sentence, K-GA and K-GA2
    assert not any("rafale" in it[2] for it in (GA, GB, GC, GD))                     # brought by the OK glosses alone


def test_v18_suspended_correction_and_contested_observation_bring_no_frequency(mod):
    out = gloss_student(mod)._loo_cal_relevance("mot")
    assert out["excluded"] == [{"observation_id": "GE", "reason": "CONTESTE"}] and "GE" not in out["items"]
    for u in out["units"]:
        assert "GE" not in u["training"] and not {"quai", "table"} & set(u["relevance"]["frequencies"])


def test_v18_an_unattachable_gloss_is_reported_and_never_assigned(mod):
    ga_alt = ("GA", "mot", "Le mot vole près du phare.", "L1", "a", "x")
    s = gloss_student(mod, extra=[(("K-U", "GB", "« vole » marque ce sens (L1) dans la tempête."), GA),
                                  (("K-V", "GA", "« vole » marque ce sens (L1) près du phare."), ga_alt)])
    out = s._loo_cal_relevance("mot")
    records = {r["id"]: (r["status"], r["attached"], r["counted"]) for r in out["corrections"]}
    assert records["K-U"] == records["K-V"] == ("OK", False, False)
    assert sorted(out["items"]["GA"]["glosses"]) == ["K-GA", "K-GA2"]
    assert not {"tempete", "phare"} & set().union(*item_traits(out).values())


def test_v18_b2_removal_takes_the_held_out_item_with_its_glosses(mod):
    ga = relevance_units(gloss_student(mod)._loo_cal_relevance("mot"))["GA"]
    assert ga["removed"] == ["GA", "K-GA", "K-GA2"] and ga["training"] == ["GB", "GC", "GD"] and ga["relevance"]["m"] == 3
    assert not {"falaise", "rafale", "marque", "malgre", "garde", "sens"} & set(ga["relevance"]["frequencies"])
    assert ga["relevance"]["frequencies"]["vole"] == 1                                # GB only: GA never counts for itself


def test_v18_filter_is_recomputed_on_each_iteration(mod):
    m, _ = mod
    out = gloss_student(mod)._loo_cal_relevance("mot")
    whole = m.lexical_relevance(item_traits(out))
    assert whole["m"] == 4 and {"vole", "range"} <= set(whole["kept"])                   # 2F = M: kept (D1)
    units = relevance_units(out)
    assert units["GC"]["relevance"]["excluded"] == units["GD"]["relevance"]["excluded"] == ["vole"]
    assert units["GA"]["relevance"]["excluded"] == ["range"] and "vole" in units["GA"]["relevance"]["kept"]


def test_v18_each_iteration_equals_a_student_that_never_saw_its_b2_removal(mod):
    m, _ = mod
    for u in gloss_student(mod)._loo_cal_relevance("mot")["units"]:
        alone = gloss_student(mod, drop=frozenset(u["removed"]))._loo_cal_relevance("mot")
        assert sorted(alone["items"]) == u["training"] and m.lexical_relevance(item_traits(alone)) == u["relevance"]


def test_v18_constructions_never_enter_the_lexical_filter(mod):
    s = gloss_student(mod)
    out = s._loo_cal_relevance("mot")
    traits = set().union(*item_traits(out).values(), *(u["relevance"]["frequencies"] for u in out["units"]))
    constructions = set().union(*(s._construction("mot", it[2]) for it in (GA, GB, GC, GD)))
    assert traits and constructions and not traits & constructions and not any(":" in t for t in traits)
    for function in ("lexical_relevance", "_lexical_traits", "_loo_cal_relevance"):
        assert not names_in(function) & {"_construction", "extract", "CONSTRUCTION_CLASSES"}, function


def test_v18_answer_path_never_uses_the_lexical_filter():
    for function in ("answer", "_evidence", "_concordant", "_p5l2_status", "_recall", "_loo_cal_plan"):
        assert not names_in(function) & {"lexical_relevance", "_lexical_traits", "_loo_cal_relevance"}, function


def test_v18_lexical_filter_changes_no_answer_no_plan_and_no_state(mod):
    m, _ = mod
    s = new(mod)
    s.learn([PT, EXC, PA2, PA3, PE1, PE2]); s.apply_correction(OK_EXC, EXC)
    state, plan, before = m.canonical(s.state), s._loo_cal_plan("mot"), [s.answer("mot", q) for q in (PQUERY, PT[2])]
    s._loo_cal_relevance("mot")
    assert m.canonical(s.state) == state and s._loo_cal_plan("mot") == plan
    assert [s.answer("mot", q) for q in (PQUERY, PT[2])] == before and [a["origin"] for a in before] == ["CORRIGE", "RAPPEL"]


def test_v18_no_vote_and_no_nc_tpc_is_computed(mod):
    out = gloss_student(mod)._loo_cal_relevance("mot")
    assert out["votes"] == "NOT_COMPUTED" and out["missing"] == ["P3_FILTER"]
    keys = set(out) | {k for u in out["units"] for k in [*u, *u["relevance"]]}
    assert not keys & {"N_c", "TP_c", "r_c"}


def test_v18_declared_descendants_left_in_training_are_reported(mod):
    s = new(mod)
    s.learn([PA1, PA2, PA3, PE1, PE2]); s.apply_correction(OK_PB1, PB1, provenance={"PB1": {"derived_from": ["PA1"]}})
    units = relevance_units(s._loo_cal_relevance("mot"))
    assert units["PA1"]["descendants_in_training"] == ["K-OK", "PB1"] and "PB1" in units["PA1"]["training"]
    assert units["PB1"]["descendants_in_training"] == [] and units["PB1"]["removed"] == ["K-OK", "PB1"]


def test_v18_lexical_filter_does_not_depend_on_the_order_of_teaching(mod):
    b = new(mod)
    b.learn([GE, GD, GC, GB, GA])
    for c, ex in ((X_GE, GE), (K_GA2, GA), (K_GE, GE), (K_GA, GA)):
        b.apply_correction(c, ex)
    assert b._loo_cal_relevance("mot") == gloss_student(mod)._loo_cal_relevance("mot")


def test_v18_lexical_filter_survives_save_reload_and_replays_the_past(mod, tmp_path):
    m, _ = mod
    s = gloss_student(mod)
    out = s._loo_cal_relevance("mot")
    s.save(tmp_path)
    r = m.R4CoreStudent.load(tmp_path, lexicon_dir=str(SANDBOX / "__no_lexicon__"))
    lessons = new(mod)
    lessons.learn([GA, GB, GC, GD, GE])
    assert r._loo_cal_relevance("mot") == out and r._loo_cal_relevance("mot", as_of=1) == lessons._loo_cal_relevance("mot")


def test_v18_v0_teaching_data_gives_sixteen_training_items_per_unit(mod):
    exercises = {e[0]: e for e in D.E_EXERCISES}
    s = new(mod)
    s.learn(D.E_LESSONS + D.E_EXERCISES)
    for c in D.C_CORRECTIONS + [D.CONTRADICTION]:
        s.apply_correction(c, exercises[c[1]])
    out = s._loo_cal_relevance("force")
    assert len(out["units"]) == 17 and out["excluded"] == [{"observation_id": "EX-F6", "reason": "CONTESTE"}]
    assert {u["relevance"]["m"] for u in out["units"]} == {16} and not any(u["relevance"]["bypass"] for u in out["units"])
    assert {r["id"]: (r["status"], r["counted"]) for r in out["corrections"]} == {
        "C-1": ("OK", True), "C-2": ("OK", True), "C-3": ("OK", True), "C-4": ("SUSPENDU", False), "C-X": ("CONTESTE", False)}
