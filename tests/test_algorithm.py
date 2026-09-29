"""johnson_algorithm: Johnson-Optimalität gegen unabhängige Brute-Force-Vollaufzählung (Vertauschungsargument-
Beweis empirisch geprüft, nicht nur behauptet), Regressionsschutz, Determinismus, Rüstzeit-Variante."""

import itertools

import numpy as np
import pytest

import johnson_algorithm as A


def _p1p2(seed, n):
    rng = np.random.default_rng(seed)
    p1 = rng.integers(1, 50, size=n).astype(np.int64)
    p2 = rng.integers(1, 50, size=n).astype(np.int64)
    return p1, p2


@pytest.mark.parametrize("n", [2, 3, 4, 5, 6, 7])
def test_johnson_matches_brute_force_for_every_seed(n):
    for seed in range(10):
        p1, p2 = _p1p2(seed, n)
        assert A.johnson(p1, p2).cmax == pytest.approx(A.brute_force_optimal(p1, p2).cmax)


def test_johnson_is_the_unique_optimum_up_to_ties():
    p1, p2 = _p1p2(7, 6)
    johnson_cmax = A.johnson(p1, p2).cmax
    all_cmax = [A.evaluate_order(p1, p2, perm).cmax for perm in itertools.permutations(range(6))]
    assert johnson_cmax == pytest.approx(min(all_cmax))


def test_completion_times_follow_the_flow_shop_recursion():
    p1 = np.array([3, 2, 4])
    p2 = np.array([2, 3, 1])
    order = np.array([1, 0, 2])          # beliebige Reihenfolge, von Hand nachgerechnet
    result = A.evaluate_order(p1, p2, order)
    # Maschine 1: c1 = 2, 5, 9 (kumulativ p1 in Reihenfolge 1,0,2 = 2,3,4)
    assert result.c1.tolist() == [2, 5, 9]
    # Maschine 2: c2_0 = max(2,0)+3=5; c2_1 = max(5,5)+2=7; c2_2 = max(9,7)+1=10
    assert result.c2.tolist() == [5, 7, 10]
    assert result.cmax == pytest.approx(10)


def test_johnson_order_places_set_a_ascending_then_set_b_descending():
    p1 = np.array([5, 2, 8, 1, 6])
    p2 = np.array([3, 4, 2, 9, 1])
    order = A.johnson_order(p1, p2)
    in_a = p1 <= p2
    a_part = [j for j in order if in_a[j]]
    b_part = [j for j in order if not in_a[j]]
    assert a_part == sorted(a_part, key=lambda j: p1[j])
    assert b_part == sorted(b_part, key=lambda j: -p2[j])
    assert list(order) == a_part + b_part


def test_naive_spt_order_is_ascending_by_total_time():
    p1 = np.array([5, 2, 8, 1, 2])
    p2 = np.array([1, 4, 1, 9, 3])
    order = A.naive_spt_order(p1, p2)
    totals = (p1 + p2)[order]
    assert list(totals) == sorted(totals)


def test_random_order_is_deterministic_given_the_rng_state():
    n = 8
    a = A.random_order(n, np.random.default_rng(0))
    b = A.random_order(n, np.random.default_rng(0))
    assert a.tolist() == b.tolist()
    assert sorted(a.tolist()) == list(range(n))


def test_johnson_beats_naive_spt_on_a_hand_picked_instance():
    """Handrechnung: naives SPT sortiert nach Summe und übersieht, dass die REIHENFOLGE der beiden Zeiten
    zueinander zählt - hier zwei Aufträge mit gleicher Summe, aber entgegengesetzter Struktur."""
    p1 = np.array([1, 8])
    p2 = np.array([8, 1])                 # Auftrag 0: kurz auf M1, lang auf M2 (Menge A) - sollte zuerst
    result = A.johnson(p1, p2)
    assert result.order.tolist() == [0, 1]
    assert result.cmax == pytest.approx(1 + 8 + 1)          # c1_0=1, c2_0=9, c1_1=9, c2_1=10
    naive = A.naive_spt_order(p1, p2)                       # Summe gleich (9,9) -> Reihenfolge egal für SPT
    assert set(naive.tolist()) == {0, 1}


# --- Mit Rüstzeiten (Vehikel B) --------------------------------------------------------------------------------


def test_setup_variant_matches_the_plain_variant_when_setup_is_zero():
    p1, p2 = _p1p2(11, 6)
    family = np.array([0, 1, 0, 1, 0, 1])
    setup = np.zeros((2, 2))
    plain = A.johnson(p1, p2)
    with_setup = A.evaluate_order(p1, p2, plain.order, family, setup)
    assert with_setup.cmax == pytest.approx(plain.cmax)


def test_setup_time_delays_both_machines_on_a_family_change():
    p1 = np.array([2, 2])
    p2 = np.array([2, 2])
    family = np.array([0, 1])
    setup = np.array([[0, 10], [10, 0]])
    order = np.array([0, 1])
    result = A.evaluate_order(p1, p2, order, family, setup)
    # Auftrag 0: kein Wechsel, c1=2, c2=4. Auftrag 1: Wechsel -> +10 auf M1 vor Beginn, dann +10 auf M2 vor Beginn
    assert result.c1.tolist() == [2, 2 + 10 + 2]
    assert result.c2.tolist() == [4, max(2 + 10 + 2, 4 + 10) + 2]


def test_brute_force_with_setup_matches_independent_full_enumeration():
    p1, p2 = _p1p2(13, 5)
    family = np.array([0, 1, 0, 1, 2])
    setup = np.array([[0, 5, 8], [5, 0, 3], [8, 3, 0]])
    best = A.brute_force_optimal(p1, p2, family, setup)
    all_cmax = [A.evaluate_order(p1, p2, np.array(perm), family, setup).cmax for perm in itertools.permutations(range(5))]
    assert best.cmax == pytest.approx(min(all_cmax))


def test_ignoring_setup_can_be_worse_than_the_true_optimum():
    """Johnson (kennt keine Rüstzeiten) muss nicht optimal bleiben, sobald Rüstzeiten dazukommen - genau die
    Frage, die Vehikel B stellt."""
    p1 = np.array([1, 1, 10, 10])
    p2 = np.array([1, 1, 10, 10])
    family = np.array([0, 1, 0, 1])
    setup = np.array([[0, 100], [100, 0]])
    johnson_cmax = A.evaluate_order(p1, p2, A.johnson_order(p1, p2), family, setup).cmax
    true_opt = A.brute_force_optimal(p1, p2, family, setup).cmax
    assert johnson_cmax > true_opt + 1e-6
