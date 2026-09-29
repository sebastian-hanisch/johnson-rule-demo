"""Auswertung der Johnson-Regel-Demo: Johnson gegen naives SPT (die falsche Regel hier - ignoriert die
Zwei-Stufen-Struktur) und gegen zufällige Reihenfolgen, gegen die Brute-Force-Vollaufzählung (nur kleine n),
und das Vehikel-B-Experiment (bleibt Johnson nahe am Optimum, sobald Rüstzeiten dazukommen)."""

import time
from dataclasses import dataclass, replace
from functools import lru_cache

import numpy as np

import johnson_algorithm as A
import johnson_constants as C
import johnson_scenario as S
import johnson_scenario_logistik as SL


@dataclass(frozen=True)
class Settings:
    n: int = C.DEFAULT_N
    seed: int = C.DEFAULT_SEED
    chain_seed: int = 0
    vehicle: str = C.DEFAULT_VEHICLE
    setup_time: int = C.DEFAULT_SETUP_TIME
    n_families: int = C.DEFAULT_N_FAMILIES


@lru_cache(maxsize=512)
def instance(n, seed):
    return S.generate(n, seed)


@lru_cache(maxsize=512)
def logistik_instance(n, seed, n_families, setup_time):
    return SL.generate(n, seed, n_families=n_families, setup_time=setup_time)


@dataclass
class Analysis:
    settings: Settings
    inst: object
    johnson: object
    naive_spt: object          # die falsche Regel hier: ignoriert die Zwei-Stufen-Struktur
    random_mean: float
    random_runs: int
    optimal: object            # None, wenn n > BRUTE_FORCE_MAX_N

    @property
    def gap_spt(self):
        return _gap(self.naive_spt.cmax, self.johnson.cmax)

    @property
    def gap_random(self):
        return _gap(self.random_mean, self.johnson.cmax)

    @property
    def johnson_matches_optimum(self):
        return self.optimal is not None and abs(self.johnson.cmax - self.optimal.cmax) < 1e-6


def _gap(value, baseline):
    """Prozent-Abstand von `value` zu `baseline` - generisch: Vergleichsregel gegen Johnson (Haupt-Kennzahl),
    ODER Johnson gegen das echte Optimum (Vehikel-B-Härtetest)."""
    if baseline <= 1e-9:
        return 0.0 if value <= 1e-9 else float(value)
    return 100.0 * (value - baseline) / baseline


def analyse(settings, random_draws=20):
    """Wertet Johnson auf dem gewählten Vehikel aus - Neutral oder Werkstatt/Logistik (Rüstzeit beim
    Familienwechsel zählt auf BEIDEN Maschinen mit). Johnson selbst bleibt in beiden Fällen dieselbe Regel
    (sortiert nur nach p1/p2, kennt keine Rüstzeiten) - nur die BEWERTUNG der Reihenfolgen (und damit auch der
    Vollaufzählung) wechselt mit dem Vehikel, von Anfang an vehikel-bewusst gebaut (Lehre aus Stück 1-5, siehe
    [[feedback_vehicle_toggle_must_drive_primary_metrics]])."""
    if settings.vehicle == "logistik":
        inst = logistik_instance(settings.n, settings.seed, settings.n_families, settings.setup_time)
        p1, p2, family, setup = inst.p1, inst.p2, inst.family, inst.setup

        def ev(order):
            return A.evaluate_order(p1, p2, order, family, setup)

        optimal = A.brute_force_optimal(p1, p2, family, setup) if settings.n <= C.BRUTE_FORCE_MAX_N else None
    else:
        inst = instance(settings.n, settings.seed)
        p1, p2 = inst.p1, inst.p2

        def ev(order):
            return A.evaluate_order(p1, p2, order)

        optimal = A.brute_force_optimal(p1, p2) if settings.n <= C.BRUTE_FORCE_MAX_N else None

    johnson = ev(A.johnson_order(p1, p2))
    naive_spt = ev(A.naive_spt_order(p1, p2))
    rng = np.random.default_rng(settings.chain_seed)
    random_totals = [ev(A.random_order(settings.n, rng)).cmax for _ in range(random_draws)]
    return Analysis(settings, inst, johnson, naive_spt, float(np.mean(random_totals)), random_draws, optimal)


# --- Sweeps und Tabellen -----------------------------------------------------------------------------------------------------------------------


def _mean(rows, key):
    return float(np.mean([r[key] for r in rows]))


def run_config(base, seeds=C.SWEEP_SEEDS, chains=C.SWEEP_CHAINS, **changes):
    s0 = replace(base, **changes)
    rows = []
    for seed in seeds:
        for ch in range(chains):
            a = analyse(replace(s0, seed=seed, chain_seed=ch))
            rows.append({"gap_spt": a.gap_spt, "gap_random": a.gap_random})
    out = {k: _mean(rows, k) for k in rows[0]}
    out["n_runs"] = len(rows)
    return out


SWEEP_VALUES = {"n": (2, 5, 10, 20, 40, 60)}
SWEEP_LABELS = {"n": "Aufträge"}


def sweep(param, base=Settings(), values=None):
    values = SWEEP_VALUES[param] if values is None else values
    return [{"value": v, **run_config(base, **{param: v})} for v in values]


def optimality_check(ns=C.BRUTE_FORCE_SWEEP_N, seeds=C.SWEEP_SEEDS):
    """Johnson gegen Brute-Force-Vollaufzählung über mehrere n und Instanzen - Anteil exakter Treffer (muss
    100 % sein, sonst ist der Beweis oder die Implementierung falsch)."""
    rows = []
    for n in ns:
        matches = 0
        for seed in seeds:
            inst = instance(n, seed)
            j_cmax = A.johnson(inst.p1, inst.p2).cmax
            opt_cmax = A.brute_force_optimal(inst.p1, inst.p2).cmax
            if abs(j_cmax - opt_cmax) < 1e-6:
                matches += 1
        rows.append({"value": n, "match_rate": matches / len(seeds)})
    return rows


def timing_sweep(ns=C.BRUTE_FORCE_SWEEP_N, seed=C.DEFAULT_SEED):
    """Gemessene Rechenzeit: Brute-Force-Vollaufzählung (O(n!)) gegen Johnson (O(n log n))."""
    rows = []
    for n in ns:
        inst = instance(n, seed)
        t0 = time.perf_counter()
        A.brute_force_optimal(inst.p1, inst.p2)
        t_bf = time.perf_counter() - t0
        t0 = time.perf_counter()
        for _ in range(100):
            A.johnson(inst.p1, inst.p2)
        t_j = (time.perf_counter() - t0) / 100
        rows.append({"value": n, "brute_force_seconds": t_bf, "johnson_seconds": t_j})
    return rows


def setup_gap(n=8, seeds=C.SWEEP_SEEDS, n_families=C.DEFAULT_N_FAMILIES, setup_time=C.DEFAULT_SETUP_TIME):
    """Vehikel-B-Härtetest: Johnson (kennt keine Rüstzeiten) gegen die echte Optimallösung MIT Rüstzeiten
    (Brute-Force, deshalb kleines n). Der Abstand ist eine echte Messfrage, kein behaupteter Befund."""
    gaps = []
    for seed in seeds:
        linst = SL.generate(n, seed, n_families=n_families, setup_time=setup_time)
        j_order = A.johnson_order(linst.p1, linst.p2)
        j_cmax = A.evaluate_order(linst.p1, linst.p2, j_order, linst.family, linst.setup).cmax
        opt_cmax = A.brute_force_optimal(linst.p1, linst.p2, linst.family, linst.setup).cmax
        gaps.append(_gap(j_cmax, opt_cmax))
    return {"gap_mean": float(np.mean(gaps)), "gap_min": float(np.min(gaps)), "gap_max": float(np.max(gaps)), "n_runs": len(gaps)}


def setup_gap_sweep(setup_times=(0, 5, 15, 30, 60), n=8, seeds=C.SWEEP_SEEDS, n_families=C.DEFAULT_N_FAMILIES):
    return [{"value": s, **setup_gap(n=n, seeds=seeds, n_families=n_families, setup_time=s)} for s in setup_times]
