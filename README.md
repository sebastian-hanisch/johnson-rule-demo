# Johnson-Regel – die erste Erweiterung auf zwei Maschinen – Streamlit-Demo

**[→ Demo live ausprobieren](#) (Deploy offen)**

Sechstes Stück der **Klassische-Scheduling-Theorie-Linie** der "Konzepte"-Reihe für die Website "Sebastian Hanisch
– Operations Research und Machine Learning": $n$ Aufträge, jeder mit ZWEI Operationen (erst Maschine 1, dann
Maschine 2, ein Flow-Shop), Ziel ist die Gesamtdurchlaufzeit $C_{\max}$ zu minimieren ($F2||C_{\max}$ in der
α|β|γ-Notation).

**Einordnung in die Linie:** Die erste Erweiterung von einer auf **zwei Maschinen** - eine neue Dimension
(Reihenfolge UND welche Maschine zuerst), nicht nur ein neues Ziel oder eine neue Nebenbedingung wie in den
Stücken 2-5. **Johnson** (1954) ist dafür beweisbar optimal: Aufträge mit $p_{1j} \le p_{2j}$ aufsteigend nach
$p_{1j}$, danach Aufträge mit $p_{1j} > p_{2j}$ absteigend nach $p_{2j}$. Dieselbe Regel setzt `doppelspiel-demo`
bereits praktisch beim Kran-Doppelspiel ein (Goodchild & Daganzo 2006) - hier ihr theoretisches Zuhause mit
Beweis.
```
SPT (1||ΣCⱼ, Vertauschungsargument)                                              [Stück 1]
EDD (1||Lmax, dasselbe Beweismuster, andere Zielfunktion)                        [Stück 2]
Moore-Hodgson (1||ΣUⱼ, EDD + gezieltes Streichen)                                [Stück 3]
WSPT / Smith's Rule (1||ΣwⱼCⱼ, verallgemeinert SPT mit Gewichten)                [Stück 4]
ATC (1||ΣwⱼTⱼ, stark NP-schwer - erstes Stück ohne Beweis)                       [Stück 5]
 └─ Johnson-Regel (F2||Cmax, erste Erweiterung auf zwei Maschinen)               [dieses Stück]
LPT (Pm||Cmax, parallele Maschinen)                                              [Folgestück]
Job Shop (Konvergenzpunkt: Reihenfolge UND Maschinenwahl)                        [Folgestück]
```

Ergebnis in Kürze: **Johnson trifft auf jeder getesteten Instanz (n = 2 bis 9) exakt das Minimum der
Vollaufzählung.** Bei 20 Aufträgen liegt Johnson im Mittel **7,5 %** unter naivem SPT (sortiert nur nach der
Gesamtzeit $p_1+p_2$) und **8,9 %** unter einer zufälligen Reihenfolge - ein deutlich KLEINERER relativer
Vorsprung als in Stück 1-5, weil $C_{\max}$ (anders als eine Summe wie $\sum C_j$ oder $\sum w_jT_j$) nur vom
letzten kritischen Pfad abhängt, nicht von jeder einzelnen Position. **Der ehrliche Bruch:** sobald Rüstzeiten
zwischen Auftragsfamilien dazukommen (Vehikel Werkstatt/Logistik, Rüstzeit auf BEIDEN Maschinen), setzt der
Beweis nicht mehr - der Abstand wächst von **0 %** bei 0 Minuten auf **27,4 %** bei 60 Minuten je Familienwechsel,
und Johnson kann dort im Einzelfall sogar schlechter abschneiden als naives SPT (gemessen, siehe App).

| Frage | Ergebnis (Mittel über 5 feste Instanzen, Seeds 100000–100004, mit je 3 Ketten-Seeds) |
|---|---|
| Standardfall (20 Aufträge) | ✅ Johnson liegt **7,5 %** unter naivem SPT und **8,9 %** unter einer zufälligen Reihenfolge |
| **Beweis gegen Vollaufzählung** | ✅ **100 %** Trefferquote bei n = 2 bis 9 |
| **Rechenzeit** | ➖ Vollaufzählung bei n = 9 bereits über 1000 ms, Johnson im Mikrosekundenbereich |
| **Vehikel Werkstatt/Logistik** | ❌ Rüstzeit 0/5/15/30/60 Minuten: **0/2,3/7,1/13,9/27,4 %** über dem echten Optimum |

## Was die Demo zeigt

1. **Johnson in Aktion** (Schritt-Slider): **Aufträge** (Streudiagramm p1 gegen p2, Menge A/B farblich getrennt)
   → **Einplanen** (Regler "eingeplante Aufträge", Gantt mit ZWEI Maschinenzeilen) → **Ergebnis** (Fertigstellung
   auf Maschine 2 über die Zeit, Johnson gegen naives SPT).
2. **Was Johnson bringt:** Johnson, naives SPT (falsche Regel hier), zufällige Reihenfolge, Vollaufzählungs-
   Gegenprobe (n ≤ 9); auf dem Werkstatt/Logistik-Vehikel zusätzlich Johnson mit Rüstzeiten gegen das echte
   Optimum mit Rüstzeiten.
3. **📐 Sweep** über die Anzahl der Aufträge.
4. **🔬 Experimente auf Abruf:** Vollaufzählung gegen Johnson über n = 2 bis 9 (Beweis-Check); Rechenzeit $n!$
   gegen $n \log n$; Rüstzeit-Härtetest auf dem Werkstatt/Logistik-Vehikel.
5. **🚧 Grenzen:** Tabelle "Annahme – was passiert – wer setzt an" (sequenzabhängige Rüstzeiten, mehr als zwei
   Maschinen, jeder Auftrag dieselbe Maschinenreihenfolge) mit Verweisen auf die Folgestücke.

Regler: Aufträge (2–60), **Vehikel** (Neutral/Werkstatt-Logistik – bei Werkstatt zusätzlich Rüstzeit und Anzahl
Familien), Seed der Instanz (+ 🎲), Seed der Kette (+ 🎲, steuert nur die zufällige Vergleichsreihenfolge –
Johnson selbst ist deterministisch).

## Die zwei Vehikel (gelten für die ganze Linie)

- **Neutral** (`johnson_scenario.py`): $n$ Aufträge mit ZWEI unabhängigen Bearbeitungszeiten
  $p_{1j}, p_{2j} \sim U(1, 100)$ - die erste Instanz dieser Linie mit zwei Maschinen statt einer.
- **Werkstatt/Logistik** (`johnson_scenario_logistik.py`): dieselben Bearbeitungszeiten, aber jeder Auftrag
  gehört zu einer Familie; ein Familienwechsel kostet dieselbe feste Rüstzeit auf BEIDEN Maschinen (dieselbe
  Idee wie in `spt-scheduling-demo` usw.). Johnsons eigener Beweis (1954, "... with setup times included")
  deckt bereits feste, auftragseigene Rüstzeiten ab (einfach zu $p_j$ addierbar) - was ihn bricht, sind
  SEQUENZABHÄNGIGE Rüstzeiten, genau das Vehikel B. Rüstzeit 0 kollabiert exakt zum neutralen Vehikel (per Test
  belegt).

## Modell und Verfahren

- **Instanz** (`johnson_scenario.py`, `johnson_scenario_logistik.py`): zwei Bearbeitungszeiten, Familien und
  Rüstzeit-Matrix, Seed-erzeugt wie jede andere Konzepte-Linie dieser Website.
- **Johnson** (`johnson_algorithm.py`): Menge A/B bilden und sortieren, $O(n \log n)$. Die Fertigstellung folgt
  der Flow-Shop-Rekursion $C_{1j} = C_{1,j-1}+p_{1j}$, $C_{2j} = \max(C_{1j}, C_{2,j-1})+p_{2j}$. Dazu die
  Brute-Force-Vollaufzählung (nur für kleine $n$, $F2||C_{\max}$ ist selbst polynomial lösbar - CP-SAT ist hier
  NICHT nötig, anders als im vorigen, stark NP-schweren Stück) und die Rüstzeit-Variante für Vehikel B.
- **Auswertung** (`johnson_evaluation.py`): Kennzahlen, Sweep, Optimalitäts- und Timing-Messreihe,
  Rüstzeit-Härtetest.

## Was nicht funktioniert hat / Grenzen

- **Vorab-Erwartung: "der relative Vorsprung sieht aus wie in Stück 1-5"** – **widerlegt**: bei $C_{\max}$ hängt
  die Zielgröße nur vom kritischen Pfad ab, nicht von jeder Position wie bei $\sum C_j$/$\sum w_jT_j$ - der
  Standardfall-Vorsprung liegt bei nur 7,5-8,9 %, deutlich kleiner als in den Vorgängerstücken (49-1222 %).
  Kein Fehler, sondern eine ehrliche Eigenschaft der Zielfunktion selbst.
- **Vorab-Vermutung: "Johnson bleibt zumindest besser als naives SPT, auch mit Rüstzeiten"** – **widerlegt im
  Einzelfall**: bei bestimmten Werkstatt-Instanzen (Seed 0, n=10, Rüstzeit 15) schneidet Johnson schlechter ab
  als naives SPT - dasselbe Muster wie in `wspt-demo`/`weighted-tardiness-demo` gefunden, hier von Anfang an
  korrekt (vorzeichenrichtig, mit passender Warnmeldung) dargestellt statt nachträglich gefixt.
- **Die Vollaufzählung ist die einzige echte Gegenprobe**, praktisch nur bis $n \approx 9$ nutzbar.
- **Synthetische Instanzen:** beide Bearbeitungszeiten unabhängig gleichverteilt, keine Präzedenzen, jeder
  Auftrag hat genau zwei Operationen in fester Reihenfolge (Maschine 1 dann Maschine 2).

## Verifikation

- **Beweis gegen unabhängige Vollaufzählung:** für jede getestete Instanzgröße (n = 2 bis 9) und jede der 5
  festen Instanzen trifft Johnson exakt das Minimum aller $n!$ Reihenfolgen – 100 % Trefferquote.
- **Rüstzeit-Variante gegen unabhängige Vollaufzählung** und **Konsistenz-Test**: Rüstzeit 0 liefert exakt
  dasselbe Cmax wie das neutrale Vehikel.
- **Handrechnung:** eine kleine, von Hand nachgerechnete Instanz (2 Aufträge, entgegengesetzte Struktur bei
  gleicher Gesamtzeit) bestätigt, dass Johnson den Auftrag mit kurzer erster Operation zuerst einplant, obwohl
  naives SPT beide Reihenfolgen für gleich gut hält.
- **Alle Zahlen der App-Texte sind als Tests hinterlegt** (Standardfall, Optimalitäts-Trefferquote, Rechenzeit,
  Rüstzeit-Härtetest; positive **und** negative Aussagen inklusive des Falls, in dem Johnson schlechter als
  naives SPT abschneidet); alle 5 Presets geprüft; AppTest-Rauchtests (Voreinstellung, jedes Preset, jeder
  Schritt auf beiden Vehikeln, Würfel-Knöpfe, Permalink-Grenzen inkl. ungültigem Vehikel, Extremwerte,
  Experimente auf Abruf, Footer, korrekt formatierte negative Prozent-Abstände); eigener Test für die
  ausblendbaren Regler (kein verwaister Widget-Zustand nach Permalink/Preset - von Anfang an eingebaut).

## Dateistruktur

| Datei | Zweck |
|---|---|
| `app.py` | Streamlit-App: Schritte, Ergebnis, 📐 Sweep, 🔬 Experimente, 🚧 Grenzen, Mathe |
| `johnson_algorithm.py` | Johnson, Brute-Force-Gegenprobe, Rüstzeit-Variante |
| `johnson_scenario.py` | Vehikel Neutral |
| `johnson_scenario_logistik.py` | Vehikel Werkstatt/Logistik (Familien, Rüstzeit-Matrix) |
| `johnson_constants.py` | Konstanten, Presets |
| `johnson_evaluation.py` | Kennzahlen, Sweep, Optimalitäts- und Timing-Messreihe, Rüstzeit-Härtetest |
| `johnson_presets.py`, `johnson_visualization.py` | Permalink/Presets (inkl. `seed_widget`/`KEPT` für ausblendbare Regler), Plotly-Figuren (achsengesperrt) |
| `tests/` | Beweis gegen Vollaufzählung, Szenario und Auswertung, Aussagen der App, Presets, versteckter Widget-Zustand, AppTest |

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

---

Teil des [Operations-Research-Demo-Portfolios](https://sebastianhanisch.net/demos.html) von
[Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning.
Interesse an einer maßgeschneiderten Lösung? [Kontakt aufnehmen](https://sebastianhanisch.net/kontakt.html).
