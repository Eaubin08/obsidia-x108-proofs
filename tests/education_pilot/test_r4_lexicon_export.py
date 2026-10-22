"""Tests of the deterministic R4 lexicon export (preregistration §7). No exam data is used.

Skipped when the private corpus database is absent (it is not tracked by git).
"""
from __future__ import annotations

import json
import pathlib

import pytest

from tests.education_pilot import r4_lexicon_export as X

pytestmark = pytest.mark.skipif(not X.DB.is_file(), reason="HOLD_CORPUS_MISSING: data/linguistic_corpus/lexicon.db absent")


@pytest.fixture(scope="module")
def exported(tmp_path_factory):
    out = tmp_path_factory.mktemp("lexicon_export")
    return out, X.export(out)


def _rows(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def test_export_refuses_to_write_inside_the_repository():
    with pytest.raises(SystemExit):
        X.export(X.ROOT / "tmp_should_not_exist")
    assert not (X.ROOT / "tmp_should_not_exist").exists()


def test_export_is_byte_identical_when_regenerated(exported, tmp_path):
    _, first = exported
    second = X.export(tmp_path / "again")
    assert first["files"] == second["files"]
    out, _ = exported
    assert (out / "MANIFEST.json").read_bytes() == (tmp_path / "again" / "MANIFEST.json").read_bytes()


def test_export_uses_only_the_preregistered_sources_and_rules(exported):
    out, m = exported
    assert m["source_db"]["sha256"] == X.DB_SHA256
    assert set(m["sources"]) == {"thes_fr", "morphalou_3_1"}
    assert {"xmlittre_fr", "unimorph_fra"} <= set(m["excluded_sources"])
    thes = _rows(out / "thes_fr.jsonl")
    assert all(set(r) == {"lemma", "pos", "sense_id", "synonyms"} for r in thes)
    assert all(r["sense_id"].startswith("thes_fr_") for r in thes)
    assert "definition" not in (out / "thes_fr.jsonl").read_text(encoding="utf-8")[:10000]


def test_export_files_are_canonically_sorted(exported):
    out, _ = exported
    thes = _rows(out / "thes_fr.jsonl")
    morph = _rows(out / "morphalou_fr.jsonl")
    assert thes == sorted(thes, key=lambda r: (r["lemma"], r["pos"], r["sense_id"]))
    assert morph == sorted(morph, key=lambda r: (r["surface_form"], r["lemma"], r["pos"]))
    assert all(r["synonyms"] == sorted(set(r["synonyms"])) for r in thes)


def test_ambiguous_forms_keep_every_candidate_lemma(exported):
    out, m = exported
    by_form = {}
    for r in _rows(out / "morphalou_fr.jsonl"):
        by_form.setdefault(r["surface_form"], set()).add(r["lemma"])
    assert m["counts"]["ambiguous_forms"] == sum(1 for v in by_form.values() if len(v) > 1) > 0


def test_mcible_variant_masks_targets_and_their_forms_only(exported):
    out, m = exported
    targets = set(m["mcible_targets"])
    forms = {r["surface_form"] for r in _rows(out / "morphalou_fr.jsonl") if r["lemma"] in targets} | targets
    full = _rows(out / "thes_fr.jsonl")
    masked = _rows(out / "thes_fr_mcible.jsonl")
    assert not any(r["lemma"] in targets for r in masked)
    assert not any(set(r["synonyms"]) & forms for r in masked)
    kept = [r for r in full if r["lemma"] not in targets]
    assert [(r["lemma"], r["sense_id"]) for r in kept] == [(r["lemma"], r["sense_id"]) for r in masked]
