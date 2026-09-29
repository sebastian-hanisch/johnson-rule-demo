"""Johnson-Regel - die erste Erweiterung dieser Linie auf zwei Maschinen - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Sechstes Stück der neuen Konzepte-Linie "Klassische Scheduling-Theorie": n Aufträge, jeder mit ZWEI Operationen
(erst Maschine 1, dann Maschine 2, ein Flow-Shop), Ziel ist die Gesamtdurchlaufzeit Cmax zu minimieren
(F2||Cmax in der α|β|γ-Notation). Johnson (1954) ist dafür BEWEISBAR optimal - dieselbe Regel, die
`doppelspiel-demo` bereits praktisch beim Kran-Doppelspiel einsetzt. Siehe README für die Einordnung in die Linie.

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import johnson_constants as C
from johnson_evaluation import Settings, SWEEP_LABELS, analyse, instance, optimality_check, run_config, setup_gap, setup_gap_sweep, sweep, timing_sweep
from johnson_presets import KEPT, apply_preset, bounds, init_session_state_defaults, load_permalink_settings, randomize_chain_seed, randomize_seed, seed_widget, sync_query_params
from johnson_visualization import build_cmax_curve, build_flow_gantt, build_jobs_chart, build_setup_gap, build_sweep, build_timing

st.set_page_config(page_title="Johnson-Regel – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner=False)
def _sweep(param, base):
    return sweep(param, base)


@st.cache_data(show_spinner=False)
def _optimality():
    return optimality_check()


@st.cache_data(show_spinner=False)
def _timing():
    return timing_sweep()


@st.cache_data(show_spinner=False)
def _setup_gap_sweep(n, n_families):
    return setup_gap_sweep(n=n, n_families=n_families)


def _fmt_int(x):
    return f"{int(round(x)):,}".replace(",", ".")


def _fmt_pct(x):
    return f"{x:+.1f} %"


st.title("🏭 Johnson-Regel – die erste Erweiterung auf zwei Maschinen")
st.markdown(
    r"""
**n Aufträge, jeder mit ZWEI Operationen (erst Maschine 1, dann Maschine 2, in dieser Reihenfolge), gesucht ist
die Reihenfolge, die die Gesamtdurchlaufzeit minimiert** ($F2||C_{\max}$). Die Antwort ist **Johnson** (1954):
Aufträge mit $p_{1j} \le p_{2j}$ aufsteigend nach $p_{1j}$, danach Aufträge mit $p_{1j} > p_{2j}$ absteigend nach
$p_{2j}$ - kein Suchverfahren, sondern **beweisbar optimal**. Dieselbe Regel setzt `doppelspiel-demo` bereits
praktisch beim Kran-Doppelspiel ein; hier ihr theoretisches Zuhause mit Beweis.
"""
)
st.caption(
    "Sechstes Stück der Konzepte-Linie „Klassische Scheduling-Theorie“ - die erste Erweiterung von einer auf "
    "zwei Maschinen. Zwei Vehikel: **Neutral** (Aufträge mit zwei unabhängigen Bearbeitungszeiten) und "
    "**Werkstatt/Logistik** (dieselben Aufträge, aber in Familien mit Rüstzeit beim Wechsel auf BEIDEN "
    "Maschinen) - der Umschalter ist in der Seitenleiste."
)

with st.expander("So funktioniert Johnson", expanded=True):
    st.markdown(
        r"""
1. **Zwei Mengen bilden.** Menge A: Aufträge mit $p_{1j} \le p_{2j}$. Menge B: die restlichen ($p_{1j} > p_{2j}$).
2. **Sortieren.** Menge A aufsteigend nach $p_{1j}$, Menge B absteigend nach $p_{2j}$, dann A vor B.
3. **Warum das optimal ist.** Ein Vertauschungsargument über beide Maschinen zugleich: Menge A drückt kurze erste Operationen früh durch, Menge B schiebt kurze zweite Operationen möglichst spät - jede andere Reihenfolge lässt sich so verbessern.
4. **Die Grenze der Annahme.** Johnsons eigener Beweis (1954) deckt feste, auftragseigene Rüstzeiten bereits ab - was ihn bricht, sind SEQUENZABHÄNGIGE Rüstzeiten (Familienwechsel). Das Vehikel „Werkstatt/Logistik“ prüft genau das.
        """
    )

st.caption("🎯 Schnellstart – ein Beispielszenario laden:")
preset_names = list(C.PRESETS.keys())
cols = st.columns(len(preset_names))
for col, name in zip(cols, preset_names):
    with col:
        st.button(name, width="stretch", on_click=apply_preset, args=(name,), help=C.PRESET_HELP[name], key=f"preset_{name}")

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    st.header("⚙️ Einstellungen")
    n_jobs = st.slider("Aufträge", *bounds("n_slider"), key="n_slider", step=C.N_STEP,
                        help=f"Anzahl der Aufträge. Bis {C.BRUTE_FORCE_MAX_N} läuft die Vollaufzählung aller n! Reihenfolgen live mit.")
    vehicle = st.radio("Vehikel", list(C.VEHICLE_LABELS), key="vehicle_radio", format_func=lambda k: C.VEHICLE_LABELS[k],
                        help="Neutral: nur Bearbeitungszeiten. Werkstatt/Logistik: dieselben Aufträge, zusätzlich in Familien mit Rüstzeit beim Wechsel (auf beiden Maschinen).")
    if vehicle == "logistik":
        seed_widget("setup_time_slider")
        setup_time = st.slider("Rüstzeit je Familienwechsel (Minuten)", *bounds("setup_time_slider"), key="setup_time_slider",
                                help="0 Minuten kollabiert exakt zum neutralen Vehikel (siehe Test/Messreihe).")
        st.session_state[KEPT["setup_time_slider"]] = setup_time
        seed_widget("n_families_slider")
        n_families = st.slider("Auftragsfamilien", *bounds("n_families_slider"), key="n_families_slider",
                                help="Weniger Familien bei gleicher Auftragszahl bedeutet mehr Wechsel und damit mehr Rüstzeit insgesamt.")
        st.session_state[KEPT["n_families_slider"]] = n_families
    else:
        setup_time = int(st.session_state.get(KEPT["setup_time_slider"], C.DEFAULT_SETUP_TIME))
        n_families = int(st.session_state.get(KEPT["n_families_slider"], C.DEFAULT_N_FAMILIES))
    seed = st.number_input("Zufalls-Seed der Instanz", *bounds("seed_input"), key="seed_input", step=1)
    st.button("🎲 Neue Instanz generieren", width="stretch", on_click=randomize_seed, help="Würfelt einen neuen Seed für beide Bearbeitungszeiten.")
    chain_seed = st.number_input("Zufalls-Seed der Kette", *bounds("chain_seed_input"), key="chain_seed_input", step=1,
                                  help="Steuert nur die zufällige Vergleichs-Reihenfolge - Johnson selbst ist deterministisch (kein Zufall im Kern).")
    st.button("🎲 Neue Kette würfeln", width="stretch", on_click=randomize_chain_seed, help="Würfelt einen neuen Seed für die Zufalls-Vergleichsreihenfolge.")

sync_query_params({"n_slider": int(n_jobs), "seed_input": int(seed), "chain_seed_input": int(chain_seed), "vehicle_radio": vehicle,
                    "setup_time_slider": int(setup_time), "n_families_slider": int(n_families)})

settings = Settings(int(n_jobs), int(seed), int(chain_seed), vehicle=vehicle, setup_time=int(setup_time), n_families=int(n_families))
with st.spinner("Rechne..."):
    a = _analysis(settings)
inst = a.inst
p1, p2 = inst.p1, inst.p2
data_key = settings

# --- Johnson in Aktion ---------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Johnson in Aktion")
STEP_LABELS = {1: "1 · Aufträge", 2: "2 · Einplanen", 3: "3 · Ergebnis"}
if "johnson_step" not in st.session_state or st.session_state.get("johnson_step_owner") != data_key:
    st.session_state["johnson_step"] = 1
    st.session_state["johnson_step_owner"] = data_key
step = st.select_slider("Schritt", options=list(STEP_LABELS), key="johnson_step", format_func=lambda s: STEP_LABELS[s])

if step == 2:
    it_col, itplay_col = st.columns([5, 2])
    with it_col:
        upto = st.slider("Eingeplante Aufträge", 1, int(n_jobs), value=int(n_jobs), key="johnson_upto")
else:
    upto = int(n_jobs)

view_slot = st.empty()
with view_slot.container():
    if step == 1:
        st.markdown(f"**{n_jobs} Aufträge, unsortiert** (Bearbeitungszeit auf Maschine 1 gegen Maschine 2)")
        st.plotly_chart(build_jobs_chart(p1, p2), width="stretch", key="s1_jobs")
    elif step == 2:
        st.markdown(f"**Johnson-Reihenfolge nach {upto} von {n_jobs} Aufträgen**")
        st.plotly_chart(build_flow_gantt(p1, p2, a.johnson.order, a.johnson.c1, a.johnson.c2, upto=upto), width="stretch", key=f"s2_sched_{upto}")
        st.caption(f"Fertigstellung Maschine 2 bisher: {_fmt_int(a.johnson.c2[upto - 1])}")
    else:
        st.markdown("**Johnson gegen naives SPT: Fertigstellung auf Maschine 2 über die Zeit**")
        st.plotly_chart(build_cmax_curve(a.johnson.order, a.johnson.c2, a.naive_spt.order, a.naive_spt.c2), width="stretch", key="s3_curve")

if step == 1:
    st.caption(f"Bearbeitungszeiten zwischen {int(min(p1.min(), p2.min()))} und {int(max(p1.max(), p2.max()))} Minuten (Seed {seed}). Blaue Punkte (Menge A) kommen zuerst, aufsteigend nach p1; rote Punkte (Menge B) danach, absteigend nach p2.")
elif step == 2:
    gap_note = " Lücken sind Wartezeit auf die andere Maschine oder (Werkstatt-Vehikel) Rüstzeit bei einem Familienwechsel." if vehicle == "logistik" else " Lücken auf Maschine 2 sind Wartezeit, bis Maschine 1 fertig ist."
    st.caption(f"Jeder Balken ist eine Operation; oben Maschine 1, unten Maschine 2.{gap_note}")
else:
    st.caption(f"Johnson: Cmax {_fmt_int(a.johnson.cmax)}. Naives SPT: {_fmt_int(a.naive_spt.cmax)} (Differenz {_fmt_pct(a.gap_spt)}).")

st.markdown("---")

# --- Ergebnis -------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Was Johnson bringt")
vehicle_note = " Auf dem Werkstatt/Logistik-Vehikel zählt die Rüstzeit auf beiden Maschinen mit - Johnson kennt sie nicht, alle Zahlen hier berücksichtigen sie trotzdem." if vehicle == "logistik" else ""
st.caption(f"**Abstand:** Cmax einer Reihenfolge gegenüber Johnson in Prozent. Johnson selbst ist deterministisch (kein Zufall im Kern) - nur die Zufalls-Vergleichsreihenfolge streut.{vehicle_note}")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Johnson (Cmax)", _fmt_int(a.johnson.cmax), help="Die Zielgröße: Gesamtdurchlaufzeit in Johnson-Reihenfolge, auf dem gewählten Vehikel.")
m2.metric("naives SPT", _fmt_pct(a.gap_spt), delta_color="off", help="Sortiert nur nach der Gesamtzeit p1+p2 - ignoriert, dass die Reihenfolge der beiden Bearbeitungszeiten zueinander zählt.")
m3.metric(f"Zufällige Reihenfolge (Mittel über {a.random_runs})", _fmt_pct(a.gap_random), delta_color="off", help="Mittel über mehrere zufällige Reihenfolgen derselben Instanz.")
if a.optimal is not None:
    m4.metric("Vollaufzählung (Gegenprobe)", "trifft Johnson exakt" if a.johnson_matches_optimum else "WEICHT AB", delta_color="off",
              help=f"Alle {n_jobs}! Reihenfolgen durchprobiert (auf dem gewählten Vehikel) - unabhängige Bestätigung bzw. Gegenprobe.")
else:
    m4.metric("Vollaufzählung", f"erst ab n ≤ {C.BRUTE_FORCE_MAX_N}", delta_color="off", help="Bei dieser Größe wäre die Vollaufzählung zu langsam - siehe das Timing-Experiment unten.")

if a.optimal is not None and not a.johnson_matches_optimum:
    if vehicle == "neutral":
        st.error("⚠️ Johnson weicht von der Vollaufzählung ab - das wäre ein Fehler im Beweis oder in der Implementierung, bitte melden.")
    else:
        gap = 100.0 * (a.johnson.cmax - a.optimal.cmax) / max(a.optimal.cmax, 1e-9)
        st.warning(f"⚠️ Johnson ist hier NICHT mehr optimal: {gap:.1f} % über dem echten Optimum MIT Rüstzeiten. Der Beweis oben setzt keine sequenzabhängigen Rüstzeiten voraus - siehe 🚧 unten.")
elif vehicle == "logistik" and (a.gap_spt < 0 or a.gap_random < 0):
    worse_than = "naives SPT" if a.gap_spt < 0 else "eine zufällige Reihenfolge"
    worst_gap = min(a.gap_spt, a.gap_random)
    st.warning(f"⚠️ Auf diesem Werkstatt-Vehikel schneidet Johnson hier sogar SCHLECHTER ab als {worse_than}: {abs(worst_gap):.1f} % mehr. Kein Fehler - Johnsons Beweis setzt keine sequenzabhängigen Rüstzeiten voraus, für diese Instanz zufällig ungünstig; genau die Grenze aus 🚧 unten.")
else:
    tail = " (auch mit Rüstzeiten - bei dieser Instanz trifft Johnson trotzdem das Optimum, das ist nicht garantiert)" if vehicle == "logistik" and a.optimal is not None else ""
    proof = "bei dieser Zielfunktion beweisbar die beste überhaupt" if vehicle == "neutral" else "auf diesem Vehikel nicht mehr bewiesen optimal, aber hier weiterhin besser als beide Vergleichsregeln"
    st.success(f"✅ Johnson ist {a.gap_spt:.1f} % besser als naives SPT und {a.gap_random:.1f} % besser als eine zufällige Reihenfolge - {proof}{tail}.")

st.markdown("---")

# --- Sweeps -----------------------------------------------------------------------------------------------------------------------------

st.subheader("📐 Wie stark hängt der Vorsprung von der Instanzgröße ab?")
sweep_param = st.selectbox("Welcher Regler soll durchgefahren werden?", list(SWEEP_LABELS), format_func=lambda k: SWEEP_LABELS[k], key="sweep_select")
if st.button("Sweep über 5 feste Instanzen berechnen (dauert wenige Sekunden)", key="sweep_start"):
    st.session_state["sweep_done"] = st.session_state.get("sweep_done", set()) | {sweep_param}
if sweep_param in st.session_state.get("sweep_done", set()):
    rows_sweep = _sweep(sweep_param, Settings())
    st.plotly_chart(build_sweep(rows_sweep, SWEEP_LABELS[sweep_param]), width="stretch", key="sweep_chart")
    st.caption("Mittel über 5 feste Instanzen (Seeds 100000–100004) mit je drei Zufalls-Ketten für die Vergleichsreihenfolge.")

st.markdown("---")

# --- Experimente ------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Stimmt der Beweis wirklich? Vollaufzählung gegen Johnson")
if st.button("Vollaufzählung über n = 2 bis 9 berechnen (dauert etwa 5 Sekunden)", key="opt_start"):
    st.session_state["opt_on"] = True
if st.session_state.get("opt_on"):
    rows_opt = _optimality()
    st.table({"Aufträge": [r["value"] for r in rows_opt], "Trefferquote": [f"{r['match_rate']:.0%}" for r in rows_opt]})
    st.caption("Für jede Instanzgröße 5 feste Instanzen: Johnson gegen die Vollaufzählung aller n! Reihenfolgen. Jede Abweichung von 100 % wäre ein Fehler im Beweis oder in der Implementierung.")

st.markdown("---")

st.subheader("🔬 Wie teuer ist eine Vollaufzählung wirklich?")
if st.button("Rechenzeit für n = 2 bis 9 messen (dauert etwa 1 Sekunde)", key="timing_start"):
    st.session_state["timing_on"] = True
if st.session_state.get("timing_on"):
    rows_t = _timing()
    st.plotly_chart(build_timing(rows_t), width="stretch", key="timing_chart")
    last = rows_t[-1]
    st.caption(f"Bei {last['value']} Aufträgen braucht die Vollaufzählung bereits {last['brute_force_seconds']*1000:.0f} ms, Johnson {last['johnson_seconds']*1000:.3f} ms - {last['brute_force_seconds']/max(last['johnson_seconds'],1e-9):.0f}-mal langsamer.")

st.markdown("---")

st.subheader("🔬 Werkstatt/Logistik: bleibt Johnson gut, wenn Rüstzeiten dazukommen?")
if st.button("Rüstzeit von 0 bis 60 Minuten durchfahren (dauert wenige Sekunden)", key="setup_start"):
    st.session_state["setup_on"] = True
if st.session_state.get("setup_on"):
    rows_s = _setup_gap_sweep(min(int(n_jobs), C.BRUTE_FORCE_MAX_N), int(n_families))
    st.plotly_chart(build_setup_gap(rows_s), width="stretch", key="setup_chart")
    st.caption("Johnson sortiert weiterhin ohne Rüstzeiten und ignoriert den Familienwechsel; verglichen mit der echten Optimallösung MIT Rüstzeiten (Vollaufzählung, deshalb kleine Instanz). Bei Rüstzeit 0 fallen beide exakt zusammen.")

st.markdown("---")

# --- Grenzen ----------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Rüstzeiten sind nicht sequenzabhängig** | Sobald ein Familienwechsel zusätzlich Zeit kostet (Vehikel „Werkstatt/Logistik“), ist Johnson nicht mehr beweisbar optimal - der Abstand zum echten Optimum wächst mit der Rüstzeit (siehe Experiment oben). Johnsons eigener Beweis (1954) deckt nur auftragseigene, feste Rüstzeiten ab. | Kein direkter Nachfolger in dieser Linie |
| **Es gibt nur zwei Maschinen** | Mit mehr als zwei Maschinen in Reihe gibt es (außer in Sonderfällen) keine einfache Regel mehr - Johnsons Beweis nutzt eine Struktur, die bei drei oder mehr Stufen nicht mehr trägt. | **LPT (parallele statt serielle Maschinen), Job Shop** (Folgestücke) |
| **Jeder Auftrag hat dieselbe Reihenfolge der Maschinen** | Ein Job Shop erlaubt jedem Auftrag eine eigene Maschinenreihenfolge - eine ganz andere, meist NP-schwere Struktur. | **Job Shop** (Folgestück) |
"""
)
st.caption(
    "Sechstes Stück der Linie „Klassische Scheduling-Theorie“: die erste Erweiterung auf zwei Maschinen. "
    "Verwandt: `doppelspiel-demo` (Johnson-Regel praktisch, Kran-Doppelspiel)."
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Problem** ($F2||C_{\max}$): $n$ Aufträge, jeder mit zwei Operationen $p_{1j}$ (Maschine 1) und $p_{2j}$
(Maschine 2), auf beiden Maschinen dieselbe Reihenfolge. Fertigstellung: $C_{1j} = C_{1,j-1} + p_{1j}$,
$C_{2j} = \max(C_{1j}, C_{2,j-1}) + p_{2j}$. Gesucht: die Reihenfolge, die $C_{\max} = C_{2n}$ minimiert.

**Satz (Johnson 1954).** Menge A ($p_{1j} \le p_{2j}$) aufsteigend nach $p_{1j}$, dann Menge B ($p_{1j} > p_{2j}$)
absteigend nach $p_{2j}$, minimiert $C_{\max}$.

**Warum das optimal ist.** Für jede Reihenfolge $\pi$ lässt sich zeigen: $C_{\max}$ hängt nur von den Summen
entlang eines "kritischen Pfads" durch die Operationen ab. Ein Vertauschungsargument über benachbarte Aufträge
$i, j$ zeigt: die Reihenfolge $(i, j)$ ist mindestens so gut wie $(j, i)$ genau dann, wenn
$\min(p_{1i}, p_{2j}) \le \min(p_{1j}, p_{2i})$ - das ist exakt die Bedingung, die Johnsons Sortierregel erfüllt.

**Kennzahl.** Abstand zu Johnson $= 100 \cdot (C_{\max} - C_{\max}^{\text{Johnson}}) / C_{\max}^{\text{Johnson}}$.
Für $n \le 9$ zusätzlich die Vollaufzählung aller $n!$ Reihenfolgen als unabhängige Gegenprobe.

**Grenzen.** (1) Sequenzabhängige Rüstzeiten (Familienwechsel) verletzen die Voraussetzung, dass $p_{1j}/p_{2j}$
unabhängig von der Reihenfolge sind - Johnson bleibt dann nur noch eine gute Heuristik (Vehikel B). (2) Mit mehr
als zwei Maschinen in Reihe gibt es i. A. keine einfache Regel mehr.

Implementiert in `johnson_algorithm.py` (Johnson, Brute-Force-Gegenprobe, Rüstzeit-Variante),
`johnson_scenario.py`/`johnson_scenario_logistik.py` (die zwei Vehikel), `johnson_evaluation.py` (Kennzahlen,
Sweep, Optimalitäts- und Timing-Messreihe, Rüstzeit-Härtetest).
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning. Interesse an einer maßgeschneiderten Lösung für "
    "Ihr Unternehmen? [Kontakt aufnehmen](https://sebastianhanisch.net/kontakt.html)"
)
