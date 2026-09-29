"""Plotly-Abbildungen der Johnson-Regel-Demo: Streudiagramm der Aufträge (Menge A/B), Zwei-Maschinen-Gantt,
Cmax-Verlauf, Sweep, Timing. Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht zoomen."""

import numpy as np
import plotly.graph_objects as go

SET_A_COLOR = "#4c78a8"
SET_B_COLOR = "#e45756"
M1_COLOR = "#4c78a8"
M2_COLOR = "#54a24b"
SPT_COLOR = "#e45756"
RANDOM_COLOR = "#7f7f7f"
SETUP_COLOR = "#f58518"


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.15), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_jobs_chart(p1, p2):
    """Streudiagramm p1 gegen p2 mit der Diagonale p1=p2 - zeigt direkt, welche Aufträge zu Menge A (p1 ≤ p2,
    zuerst, aufsteigend nach p1) und welche zu Menge B (p1 > p2, danach, absteigend nach p2) gehören."""
    in_a = p1 <= p2
    fig = go.Figure()
    lim = max(int(p1.max()), int(p2.max())) + 5
    fig.add_trace(go.Scatter(x=[0, lim], y=[0, lim], mode="lines", line=dict(color="#bbbbbb", width=1, dash="dot"), name="p1 = p2", hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=p1[in_a].tolist(), y=p2[in_a].tolist(), mode="markers", marker=dict(color=SET_A_COLOR, size=9),
                              name="Menge A (p1 ≤ p2)", hovertemplate="p1 %{x}<br>p2 %{y}<extra></extra>"))
    fig.add_trace(go.Scatter(x=p1[~in_a].tolist(), y=p2[~in_a].tolist(), mode="markers", marker=dict(color=SET_B_COLOR, size=9),
                              name="Menge B (p1 > p2)", hovertemplate="p1 %{x}<br>p2 %{y}<extra></extra>"))
    fig.update_xaxes(title_text="Bearbeitungszeit Maschine 1 (p1)", range=[0, lim])
    fig.update_yaxes(title_text="Bearbeitungszeit Maschine 2 (p2)", range=[0, lim])
    return _base(fig, 320)


def build_flow_gantt(p1, p2, order, c1, c2, upto=None):
    """Zwei Maschinenzeilen - Lücken entstehen, wenn Maschine 2 auf Maschine 1 (oder ihre eigene Vorgängerin)
    warten muss, oder (Vehikel B) durch eine Rüstzeit beim Familienwechsel."""
    order = np.asarray(order)
    upto = len(order) if upto is None else upto
    starts1 = np.asarray(c1) - p1[order]
    starts2 = np.asarray(c2) - p2[order]
    fig = go.Figure()
    for i in range(upto):
        j = order[i]
        fig.add_trace(go.Bar(x=[float(p1[j])], y=["Maschine 1"], base=[float(starts1[i])], orientation="h",
                              marker=dict(color=M1_COLOR, line=dict(width=1, color="white")), showlegend=False,
                              hovertemplate=f"Auftrag {j}<br>Dauer {p1[j]}<extra></extra>"))
        fig.add_trace(go.Bar(x=[float(p2[j])], y=["Maschine 2"], base=[float(starts2[i])], orientation="h",
                              marker=dict(color=M2_COLOR, line=dict(width=1, color="white")), showlegend=False,
                              hovertemplate=f"Auftrag {j}<br>Dauer {p2[j]}<extra></extra>"))
    fig.update_xaxes(title_text="Zeit")
    fig.update_yaxes(autorange="reversed")
    return _base(fig, 200)


def build_cmax_curve(johnson_order, johnson_c2, spt_order, spt_c2):
    """Fertigstellung auf Maschine 2 je Position - Johnson gegen naives SPT."""
    x = np.arange(1, len(johnson_c2) + 1)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=johnson_c2, mode="lines+markers", line=dict(color=M2_COLOR, width=2.5), name="Johnson (Fertigstellung Maschine 2)"))
    fig.add_trace(go.Scatter(x=x, y=spt_c2, mode="lines+markers", line=dict(color=SPT_COLOR, width=2, dash="dash"), name="naives SPT (ignoriert die Zwei-Stufen-Struktur)"))
    fig.update_xaxes(title_text="Aufträge eingeplant")
    fig.update_yaxes(title_text="Fertigstellung auf Maschine 2 bisher")
    return _base(fig, 320)


def build_sweep(rows, param_label, value_key="value", y_keys=(("gap_spt", "Johnson gegen naives SPT", SPT_COLOR), ("gap_random", "Johnson gegen Zufall", RANDOM_COLOR))):
    xs = [r[value_key] for r in rows]
    fig = go.Figure()
    for key, name, color in y_keys:
        fig.add_trace(go.Scatter(x=xs, y=[r[key] for r in rows], mode="lines+markers", line=dict(color=color, width=2.5), name=name))
    fig.update_xaxes(title_text=param_label)
    fig.update_yaxes(title_text="Abstand zu Johnson (%)")
    fig.update_layout(legend=dict(orientation="h", y=-0.3))
    return _base(fig, 360)


def build_timing(rows):
    xs = [r["value"] for r in rows]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=[r["brute_force_seconds"] * 1000 for r in rows], mode="lines+markers", line=dict(color=SPT_COLOR, width=2.5), name="Brute-Force (O(n!))"))
    fig.add_trace(go.Scatter(x=xs, y=[r["johnson_seconds"] * 1000 for r in rows], mode="lines+markers", line=dict(color=M2_COLOR, width=2.5), name="Johnson (O(n log n))"))
    fig.update_xaxes(title_text="Aufträge")
    fig.update_yaxes(title_text="Rechenzeit (ms)", type="log")
    fig.update_layout(legend=dict(orientation="h", y=-0.3))
    return _base(fig, 340)


def build_setup_gap(rows):
    xs = [r["value"] for r in rows]
    upper = [r["gap_max"] for r in rows]
    lower = [r["gap_min"] for r in rows]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs + xs[::-1], y=upper + lower[::-1], fill="toself", fillcolor="rgba(245,133,24,0.15)", line=dict(width=0), showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=xs, y=[r["gap_mean"] for r in rows], mode="lines+markers", line=dict(color=SETUP_COLOR, width=2.5), name="Johnson (ignoriert Rüstzeiten) über dem echten Optimum"))
    fig.update_xaxes(title_text="Rüstzeit je Familienwechsel (Minuten)")
    fig.update_yaxes(title_text="Abstand zum Optimum mit Rüstzeiten (%)")
    return _base(fig, 340)
