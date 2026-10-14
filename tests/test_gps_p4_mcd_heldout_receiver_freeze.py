from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GPS = ROOT / "hackathons" / "nativebuilder-gps-defense"

UTD = GPS / "gnss_sdr_fgi_ut_dfmc_l1e1_full_real8_runtime.conf"
MCD = GPS / "gnss_sdr_fgi_meaconing_dfmc_l1e1_full_real8_runtime.conf"


def _kv(path: Path):
    result = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith(";") or line.startswith("[") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        result[key.strip()] = value.strip()
    return result


def test_mcd_heldout_receiver_semantics_match_frozen_utd_receiver():
    utd = _kv(UTD)
    mcd = _kv(MCD)

    ignored = {
        "SignalSource.filename",
        "Tracking_1C.dump_filename",
        "Observables.dump_filename",
        "PVT.dump_filename",
        "PVT.nmea_dump_filename",
    }

    assert set(utd) == set(mcd)
    for key in sorted(set(utd) - ignored):
        assert mcd[key] == utd[key], key

    assert mcd["SignalSource.filename"].endswith("case_mcd_l1e1_real8.dat")
    assert mcd["SignalSource.item_type"] == "byte"
    assert mcd["SignalSource.sampling_frequency"] == "26000000"
    assert mcd["SignalSource.samples"] == "0"
    assert mcd["DataTypeAdapter.implementation"] == "Pass_Through"
    assert mcd["InputFilter.input_item_type"] == "byte"
    assert mcd["InputFilter.output_item_type"] == "gr_complex"
    assert mcd["InputFilter.IF"] == "6390000"
