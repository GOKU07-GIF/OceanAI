from app.orca.tools.ocean import _canonical_variable, _requested_canonical_variables


def test_canonical_variable_aliases() -> None:
    assert _canonical_variable("sst") == "sst_c"
    assert _canonical_variable("VHM0") == "wave_height_m"
    assert _canonical_variable("VTM02") == "wave_period_s"
    assert _canonical_variable("CHL") == "chlorophyll_mg_m3"
    assert _canonical_variable("GEO_U") == "current_u_cm_s"


def test_requested_variables_expand_known_aliases() -> None:
    requested = _requested_canonical_variables(
        ["sst_c", "wave_height_m", "chlorophyll_mg_m3"]
    )
    assert requested == {
        "sst_c",
        "wave_height_m",
        "chlorophyll_mg_m3",
    }
