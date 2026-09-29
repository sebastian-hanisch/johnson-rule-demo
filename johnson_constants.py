"""Konstanten der Johnson-Regel-Demo: beide Vehikel (Neutral, Werkstatt/Logistik), Regler, Messreihen-Seeds."""

N_MIN, N_MAX, DEFAULT_N, N_STEP = 2, 60, 20, 1
SEED_MAX = 999999
DEFAULT_SEED = 50
SWEEP_SEEDS = tuple(range(100000, 100005))
SWEEP_CHAINS = 3

# Bearbeitungszeiten auf beiden Maschinen (unabhängig voneinander)
P_MIN, P_MAX = 1, 100

# Brute-Force-Vollaufzählung nur bis zu dieser Größe live in der App (F2||Cmax ist polynomial lösbar - dieses
# Limit gilt nur für die unabhängige GEGENPROBE, nicht für Johnson selbst)
BRUTE_FORCE_MAX_N = 9
BRUTE_FORCE_SWEEP_N = (2, 3, 4, 5, 6, 7, 8, 9)

# --- Vehikel B "Werkstatt/Logistik" ---------------------------------------------------------------------------
N_FAMILIES_MIN, N_FAMILIES_MAX, DEFAULT_N_FAMILIES = 2, 6, 3
SETUP_TIME_MIN, SETUP_TIME_MAX, DEFAULT_SETUP_TIME = 0, 60, 15

VEHICLE_LABELS = {"neutral": "Neutral", "logistik": "Werkstatt/Logistik"}
DEFAULT_VEHICLE = "neutral"


def _preset(n=DEFAULT_N, vehicle=DEFAULT_VEHICLE, setup_time=DEFAULT_SETUP_TIME, n_families=DEFAULT_N_FAMILIES):
    return {"n": n, "seed": DEFAULT_SEED, "chain_seed": 0, "vehicle": vehicle, "setup_time": setup_time, "n_families": n_families}


PRESETS = {
    "Standardfall (Voreinstellung)": _preset(),
    "Kleine Instanz (Brute-Force sichtbar)": _preset(n=BRUTE_FORCE_MAX_N),
    "Große Instanz (Skalierung)": _preset(n=N_MAX),
    "Werkstatt/Logistik-Vehikel": _preset(vehicle="logistik"),
    "Hohe Rüstlast (Werkstatt)": _preset(vehicle="logistik", setup_time=SETUP_TIME_MAX),
}
# Werte in PRESET_HELP nach der Messreihe (johnson_evaluation.run_config) final eingetragen.
PRESET_HELP = {
    "Standardfall (Voreinstellung)": "20 Aufträge, zwei Maschinen: Johnson misst sich gegen naives SPT (Gesamtzeit) und eine zufällige Reihenfolge.",
    "Kleine Instanz (Brute-Force sichtbar)": f"{BRUTE_FORCE_MAX_N} Aufträge: hier läuft die Vollaufzählung aller {BRUTE_FORCE_MAX_N}! Reihenfolgen live mit - Johnson trifft auf jeder getesteten Instanz exakt das Minimum.",
    "Große Instanz (Skalierung)": f"{N_MAX} Aufträge: Johnson bleibt weiterhin beweisbar optimal und braucht nur eine Sortierung (O(n log n)).",
    "Werkstatt/Logistik-Vehikel": "Dieselben Aufträge, aber in Familien mit Rüstzeit beim Wechsel auf BEIDEN Maschinen - Johnson kennt diese Rüstzeiten nicht.",
    "Hohe Rüstlast (Werkstatt)": f"Rüstzeit {SETUP_TIME_MAX} Minuten je Familienwechsel: Johnson liegt messbar über dem echten Optimum.",
}
