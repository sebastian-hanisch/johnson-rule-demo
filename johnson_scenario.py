"""Vehikel A "Neutral" der Johnson-Regel-Demo: n Aufträge, jeder mit ZWEI unabhängigen Bearbeitungszeiten
p1ⱼ (Maschine 1) und p2ⱼ (Maschine 2) - die erste Instanz dieser Linie mit zwei Maschinen statt einer."""

from dataclasses import dataclass

import numpy as np

import johnson_constants as C


@dataclass(frozen=True)
class Instance:
    n: int
    p1: np.ndarray
    p2: np.ndarray
    seed: int


def generate(n, seed, p_min=C.P_MIN, p_max=C.P_MAX):
    rng = np.random.default_rng(seed)
    p1 = rng.integers(p_min, p_max + 1, size=n).astype(np.int64)
    p2 = rng.integers(p_min, p_max + 1, size=n).astype(np.int64)
    return Instance(n, p1, p2, seed)
