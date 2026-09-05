"""Lightweight offline tests for INCOIS ERDDAP query construction.

These tests do not access the network. They catch malformed projection syntax
before a CI workflow attempts a real download.
"""

from argparse import Namespace

from download_incois_erddap import DATASETS, build_query


def args_for(**overrides):
    values = {
        "min_lon": 68.0,
        "max_lon": 78.0,
        "min_lat": 8.0,
        "max_lat": 24.0,
        "min_depth": 5.0,
        "max_depth": 200.0,
    }
    values.update(overrides)
    return Namespace(**values)


def test_sst_projection():
    query = build_query(DATASETS["sst"], "2011-10-02T00:00:00Z", "2011-10-04T00:00:00Z", args_for())
    assert query.startswith("sst[")
    assert ",anom[" in query
    assert "[(2011-10-02T00:00:00Z):1:(2011-10-04T00:00:00Z)]" in query
    assert "[(0.0):1:(0.0)]" in query


def test_value_added_projection():
    query = build_query(DATASETS["value_added"], "2019-03-28T00:00:00Z", "2019-03-30T00:00:00Z", args_for())
    for variable in DATASETS["value_added"]["variables"]:
        assert f"{variable}[" in query


def test_argo_projection_includes_depth():
    query = build_query(DATASETS["argo_vam"], "2026-07-13T00:00:00Z", "2026-07-15T00:00:00Z", args_for(min_depth=5.0, max_depth=200.0))
    assert "TEMP[" in query
    assert "SAL[" in query
    assert "[(5.0):1:(200.0)]" in query


if __name__ == "__main__":
    test_sst_projection()
    test_value_added_projection()
    test_argo_projection_includes_depth()
    print("INCOIS query-builder tests passed")
