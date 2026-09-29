"""Johnson-Regel für F2||Cmax: n Aufträge, jeder mit ZWEI Operationen (erst Maschine 1, dann Maschine 2, auf
beiden Maschinen dieselbe Reihenfolge - ein Flow-Shop), Ziel ist die Gesamtdurchlaufzeit Cmax (Fertigstellung
des letzten Auftrags auf Maschine 2) zu minimieren. Johnson (1954) ist dafür beweisbar optimal: Aufträge mit
p1ⱼ ≤ p2ⱼ aufsteigend nach p1ⱼ, danach Aufträge mit p1ⱼ > p2ⱼ absteigend nach p2ⱼ.

Anders als Stück 1-5 dieser Linie ist das die erste Erweiterung auf ZWEI Maschinen - eine neue Dimension
(Reihenfolge UND welche Maschine zuerst), nicht nur ein neues Ziel oder eine neue Nebenbedingung. Johnsons
eigener Beweis (1954, "Optimal two- and three-stage production schedules WITH SETUP TIMES INCLUDED") deckt
bereits feste, auftragsEIGENE Rüstzeiten ab (die man einfach zu pⱼ addiert) - was den Beweis bricht, sind
SEQUENZABHÄNGIGE Rüstzeiten (Familienwechsel, wie in jedem Vehikel B dieser Linie), die Johnson NICHT behandelt.

Hier zusätzlich: Brute-Force-Vollaufzählung als unabhängige Gegenprobe (nur für kleine n praktikabel, wie
Stück 1-4 - F2||Cmax ist selbst polynomial lösbar, CP-SAT ist hier NICHT nötig), sowie die Rüstzeit-Variante
für Vehikel B (Werkstatt/Logistik, Rüstzeit auf BEIDEN Maschinen bei Familienwechsel)."""

import itertools
from dataclasses import dataclass

import numpy as np


@dataclass
class Result:
    order: np.ndarray
    c1: np.ndarray          # Fertigstellungszeiten auf Maschine 1
    c2: np.ndarray          # Fertigstellungszeiten auf Maschine 2
    cmax: float             # Zielgröße: c2 des letzten Auftrags


def completion_times(p1, p2, order, family=None, setup=None):
    """Standard-Flow-Shop-Rekursion: c1ⱼ = c1_{j-1} + p1ⱼ, c2ⱼ = max(c1ⱼ, c2_{j-1}) + p2ⱼ - Maschine 2 muss
    sowohl auf die eigene Vorgängerin als auch auf Maschine 1 warten. Mit Familien/Rüstzeit (Vehikel B) kostet
    ein Familienwechsel dieselbe Rüstzeit auf BEIDEN Maschinen, bevor die jeweilige Bearbeitung beginnt."""
    order = np.asarray(order)
    n = len(order)
    c1 = np.empty(n, dtype=np.float64)
    c2 = np.empty(n, dtype=np.float64)
    t1 = t2 = 0.0
    prev_family = None
    for i, j in enumerate(order):
        s = float(setup[prev_family, family[j]]) if family is not None and prev_family is not None else 0.0
        t1 = t1 + s + float(p1[j])
        t2 = max(t1, t2 + s) + float(p2[j])
        c1[i], c2[i] = t1, t2
        prev_family = family[j] if family is not None else None
    return c1, c2


def evaluate_order(p1, p2, order, family=None, setup=None):
    c1, c2 = completion_times(p1, p2, order, family, setup)
    return Result(np.asarray(order), c1, c2, float(c2[-1]))


def johnson_order(p1, p2):
    """Johnson (1954): Menge A (p1ⱼ ≤ p2ⱼ) aufsteigend nach p1ⱼ, dann Menge B (p1ⱼ > p2ⱼ) absteigend nach p2ⱼ.
    Stabile Sortierung, damit Gleichstände reproduzierbar sind."""
    n = len(p1)
    idx = np.arange(n)
    in_a = p1 <= p2
    a = idx[in_a][np.argsort(p1[in_a], kind="stable")]
    b_idx = idx[~in_a]
    b = b_idx[np.argsort(-p2[b_idx], kind="stable")]
    return np.concatenate([a, b])


def johnson(p1, p2):
    return evaluate_order(p1, p2, johnson_order(p1, p2))


def naive_spt_order(p1, p2):
    """Die falsche Regel hier: SPT auf die Gesamtzeit p1+p2 angewendet, als hätte man nur eine Maschine -
    ignoriert, dass die REIHENFOLGE der beiden Bearbeitungszeiten zueinander zählt, nicht nur ihre Summe."""
    return np.argsort(p1 + p2, kind="stable")


def random_order(n, rng):
    order = np.arange(n)
    rng.shuffle(order)
    return order


def brute_force_optimal(p1, p2, family=None, setup=None):
    """Volle Aufzählung aller n! Reihenfolgen - unabhängige Gegenprobe, nur für kleine n (siehe
    johnson_constants.BRUTE_FORCE_MAX_N). F2||Cmax ist polynomial lösbar (Johnson), CP-SAT ist hier nicht nötig -
    dieselbe Brute-Force-Disziplin wie Stück 1-4."""
    n = len(p1)
    best_order, best_cmax = None, np.inf
    for perm in itertools.permutations(range(n)):
        order = np.array(perm)
        _, c2 = completion_times(p1, p2, order, family, setup)
        cmax = float(c2[-1])
        if cmax < best_cmax:
            best_cmax, best_order = cmax, order
    return evaluate_order(p1, p2, best_order, family, setup)
