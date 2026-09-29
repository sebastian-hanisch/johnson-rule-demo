"""Vehikel A (Neutral) und Vehikel B (Werkstatt/Logistik): Erzeugung, Determinismus; Auswertung: Kennzahlen,
Sweep, Optimalitäts- und Timing-Messreihe, Vehikel-B-Härtetest (Rüstzeiten)."""

from dataclasses import replace

import numpy as np
import pytest

import johnson_algorithm as A
import johnson_constants as C
import johnson_evaluation as ev
import johnson_scenario as S
import johnson_scenario_logistik as SL


# --- Vehikel A ----------------------------------------------------------------------------------------------------------------------------------


def test_instance_shape_and_bounds():
    inst = S.generate(20, 3)
    assert inst.n == 20 and inst.p1.shape == (20,) and inst.p2.shape == (20,)
    assert inst.p1.min() >= C.P_MIN and inst.p1.max() <= C.P_MAX
    assert inst.p2.min() >= C.P_MIN and inst.p2.max() <= C.P_MAX


def test_instance_is_deterministic_and_seed_dependent():
    a, b, c = S.generate(30, 5), S.generate(30, 5), S.generate(30, 6)
    assert np.array_equal(a.p1, b.p1) and np.array_equal(a.p2, b.p2)
    assert not np.array_equal(a.p1, c.p1)


# --- Vehikel B ------------------------------------------------------------------------------------------------------------------------------


def test_logistik_instance_shares_the_same_processing_times_as_neutral():
    neutral = S.generate(20, 7)
    logistik = SL.generate(20, 7)
    assert np.array_equal(neutral.p1, logistik.p1) and np.array_equal(neutral.p2, logistik.p2)


def test_logistik_instance_is_deterministic():
    a, b = SL.generate(10, 2), SL.generate(10, 2)
    assert np.array_equal(a.family, b.family) and np.array_equal(a.setup, b.setup)


# --- Analyse --------------------------------------------------------------------------------------------------------------------------------


def test_analysis_fields_are_consistent():
    a = ev.analyse(ev.Settings(n=20))
    assert a.johnson.cmax <= a.naive_spt.cmax
    assert a.gap_spt >= -1e-6 and a.gap_random >= -1e-6           # neutrales Vehikel: Johnson bewiesen optimal
    assert a.optimal is None


def test_analysis_matches_the_optimum_for_small_n():
    a = ev.analyse(ev.Settings(n=6))
    assert a.optimal is not None
    assert a.johnson_matches_optimum


# --- Vehikel-Bewusstsein der Hauptanalyse (von Anfang an, siehe [[feedback_vehicle_toggle_must_drive_primary_metrics]]) ----------------------


def test_analyse_on_the_logistik_vehicle_actually_uses_setup_aware_completion_times():
    settings = ev.Settings(n=8, seed=100000, vehicle="logistik", setup_time=30, n_families=3)
    a = ev.analyse(settings)
    linst = ev.logistik_instance(8, 100000, 3, 30)
    independent_johnson = A.evaluate_order(linst.p1, linst.p2, a.johnson.order, linst.family, linst.setup)
    assert a.johnson.cmax == pytest.approx(independent_johnson.cmax)
    assert not np.array_equal(a.johnson.c1, np.cumsum(linst.p1[a.johnson.order]))  # Rüstzeiten verschieben die Fertigstellung


def test_analyse_on_the_logistik_vehicle_can_show_johnson_missing_the_optimum():
    settings = ev.Settings(n=6, seed=3, vehicle="logistik", setup_time=60, n_families=2)
    a = ev.analyse(settings)
    assert a.optimal is not None
    assert a.johnson.cmax >= a.optimal.cmax - 1e-6


def test_analyse_on_the_neutral_vehicle_is_unaffected_by_logistik_only_settings():
    a1 = ev.analyse(ev.Settings(n=10, seed=5, vehicle="neutral", setup_time=5))
    a2 = ev.analyse(ev.Settings(n=10, seed=5, vehicle="neutral", setup_time=60))
    assert a1.johnson.cmax == pytest.approx(a2.johnson.cmax)


def test_switching_vehicle_actually_changes_the_johnson_cmax():
    a_neutral = ev.analyse(ev.Settings(n=10, seed=7, vehicle="neutral"))
    a_logistik = ev.analyse(ev.Settings(n=10, seed=7, vehicle="logistik", setup_time=60, n_families=2))
    assert a_neutral.johnson.cmax != pytest.approx(a_logistik.johnson.cmax)


def test_gap_spt_can_go_negative_on_the_logistik_vehicle():
    """Echter Fund (Browser-Recherche, wie beim analogen Fall in wspt-demo/weighted-tardiness-demo): auf dem
    Werkstatt-Vehikel ist Johnson nicht mehr bewiesen optimal - naives SPT kann hier zufällig eine Reihenfolge
    mit weniger Familienwechseln treffen und Johnson schlagen."""
    a = ev.analyse(ev.Settings(n=10, seed=0, vehicle="logistik", setup_time=15, n_families=3))
    assert a.gap_spt < 0.0


def test_analysis_is_deterministic_given_the_chain_seed():
    s = ev.Settings(n=20, seed=1, chain_seed=0)
    a, b, c = ev.analyse(s), ev.analyse(s), ev.analyse(replace(s, chain_seed=1))
    assert a.gap_random == pytest.approx(b.gap_random)
    assert a.gap_random != pytest.approx(c.gap_random)


# --- Sweep und Messreihe -------------------------------------------------------------------------------------------------------------------


def test_run_config_counts_runs_and_aggregates():
    r = ev.run_config(ev.Settings(n=15))
    assert r["n_runs"] == len(C.SWEEP_SEEDS) * C.SWEEP_CHAINS
    assert r["gap_spt"] >= 0.0


def test_sweep_values_labels_and_ordering():
    assert set(ev.SWEEP_VALUES) == set(ev.SWEEP_LABELS)
    rows = ev.sweep("n", ev.Settings(), (5, 40))
    assert [r["value"] for r in rows] == [5, 40]


def test_optimality_check_always_matches():
    rows = ev.optimality_check(ns=(3, 4, 5), seeds=C.SWEEP_SEEDS)
    assert all(r["match_rate"] == 1.0 for r in rows)


def test_timing_sweep_shows_brute_force_growing_far_faster_than_johnson():
    rows = ev.timing_sweep(ns=(4, 8))
    small, large = rows[0], rows[1]
    assert large["brute_force_seconds"] > small["brute_force_seconds"] * 10
    assert large["johnson_seconds"] < large["brute_force_seconds"] / 100


def test_setup_gap_is_zero_when_setup_time_is_zero():
    row = ev.setup_gap(n=6, setup_time=0)
    assert row["gap_mean"] == pytest.approx(0.0, abs=1e-6)


def test_setup_gap_grows_with_the_setup_time():
    small = ev.setup_gap(n=6, setup_time=5)
    large = ev.setup_gap(n=6, setup_time=60)
    assert large["gap_mean"] > small["gap_mean"]
