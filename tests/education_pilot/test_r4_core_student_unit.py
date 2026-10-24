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
    assert a1["sense"] == "HOLD" and a1 == a2 and s.state["revision"] == r0
    # the RAPPEL code itself (§3.8) is NOT_COVERED: the engine only refuses to corroborate the recall
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
