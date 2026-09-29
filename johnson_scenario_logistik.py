"""Vehikel B "Werkstatt/Logistik": dieselben Aufträge wie Vehikel A (p1, p2), zusätzlich eine Familie je Auftrag
und eine feste Rüstzeit beim Familienwechsel - auf BEIDEN Maschinen (dieselbe Idee wie in `spt-scheduling-demo`
usw., dort bereits Vepsalainen & Morton 1987 zitiert). Johnsons eigener Beweis (1954) deckt nur auftragseigene,
NICHT sequenzabhängige Rüstzeiten ab - Familienwechsel sind genau die Erweiterung, die den Beweis bricht."""

from dataclasses import dataclass

import numpy as np

import johnson_constants as C


@dataclass(frozen=True)
class LogistikInstance:
    n: int
    p1: np.ndarray
    p2: np.ndarray
    family: np.ndarray
    setup: np.ndarray
    seed: int


def generate(n, seed, n_families=C.DEFAULT_N_FAMILIES, setup_time=C.DEFAULT_SETUP_TIME, p_min=C.P_MIN, p_max=C.P_MAX):
    rng = np.random.default_rng(seed)
    p1 = rng.integers(p_min, p_max + 1, size=n).astype(np.int64)
    p2 = rng.integers(p_min, p_max + 1, size=n).astype(np.int64)
    family = rng.integers(0, n_families, size=n).astype(np.int64)
    setup = np.full((n_families, n_families), setup_time, dtype=np.int64)
    np.fill_diagonal(setup, 0)
    return LogistikInstance(n, p1, p2, family, setup, seed)
