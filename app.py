import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import time

st.set_page_config(
    page_title="SOLARIS – Digital Twin",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS GLOBAL ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Import font */
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}

/* Dark background */
.stApp {
    background-color: #0d1117;
    color: #e8edf5;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #161b22 !important;
    border-right: 1px solid #2a3547;
}
[data-testid="stSidebar"] .stRadio label {
    color: #8fa3bf !important;
    font-size: 13px;
}
[data-testid="stSidebar"] .stRadio label:hover {
    color: #e8edf5 !important;
}

/* Hide default streamlit elements */
#MainMenu, footer, header {visibility: hidden;}
.block-container {padding-top: 1rem; padding-bottom: 0.5rem;}

/* Metric cards */
[data-testid="metric-container"] {
    background-color: #161b22;
    border: 1px solid #2a3547;
    border-radius: 10px;
    padding: 14px 16px !important;
}
[data-testid="metric-container"] label {
    color: #8fa3bf !important;
    font-size: 11px !important;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #e8edf5 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 22px !important;
    font-weight: 500 !important;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-size: 11px !important;
}

/* Section titles */
.section-title {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 1.4px;
    color: #5a7494;
    font-weight: 500;
    margin-bottom: 8px;
    margin-top: 4px;
    border-bottom: 1px solid #2a3547;
    padding-bottom: 6px;
}

/* Alert cards */
.alert-warn {
    background: rgba(234,179,8,0.08);
    border-left: 3px solid #eab308;
    border-radius: 6px;
    padding: 8px 12px;
    margin-bottom: 6px;
}
.alert-err {
    background: rgba(239,68,68,0.08);
    border-left: 3px solid #ef4444;
    border-radius: 6px;
    padding: 8px 12px;
    margin-bottom: 6px;
}
.alert-name-warn { color: #eab308; font-size: 12px; font-weight: 500; }
.alert-name-err  { color: #ef4444; font-size: 12px; font-weight: 500; }
.alert-time { color: #5a7494; font-size: 10px; font-family: 'IBM Plex Mono', monospace; float: right; }
.alert-desc { color: #8fa3bf; font-size: 11px; margin-top: 2px; }

/* Weather card */
.weather-card {
    background: #161b22;
    border: 1px solid #2a3547;
    border-radius: 10px;
    padding: 14px 16px;
}
.weather-temp {
    font-size: 34px;
    font-weight: 300;
    font-family: 'IBM Plex Mono', monospace;
    color: #e8edf5;
    line-height: 1;
}
.weather-row {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    padding: 4px 0;
    border-bottom: 1px solid #2a3547;
}
.weather-label { color: #5a7494; }
.weather-val { color: #e8edf5; font-family: 'IBM Plex Mono', monospace; font-weight: 500; }

/* Status header */
.status-header {
    background: #161b22;
    border: 1px solid #2a3547;
    border-radius: 10px;
    padding: 10px 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;
}
.status-ok { color: #22c55e; font-size: 12px; font-weight: 500; }
.status-dot { width: 8px; height: 8px; border-radius: 50%; background: #22c55e; display: inline-block; margin-right: 6px; }

/* Inverter legend rows */
.inv-row {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    padding: 3px 0;
}
.inv-dot {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    display: inline-block;
}
</style>
""", unsafe_allow_html=True)


# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;padding:8px 0 20px;">
        <svg width="32" height="32" viewBox="0 0 32 32">
            <circle cx="16" cy="16" r="14" fill="#f59e0b" opacity=".15"/>
            <circle cx="16" cy="16" r="8" fill="#f59e0b" opacity=".85"/>
            <line x1="16" y1="1" x2="16" y2="6" stroke="#f59e0b" stroke-width="2.5" stroke-linecap="round"/>
            <line x1="16" y1="26" x2="16" y2="31" stroke="#f59e0b" stroke-width="2.5" stroke-linecap="round"/>
            <line x1="1" y1="16" x2="6" y2="16" stroke="#f59e0b" stroke-width="2.5" stroke-linecap="round"/>
            <line x1="26" y1="16" x2="31" y2="16" stroke="#f59e0b" stroke-width="2.5" stroke-linecap="round"/>
        </svg>
        <div>
            <div style="font-size:18px;font-weight:600;color:#e8edf5;letter-spacing:0.5px">
                SOLAR<span style="color:#f59e0b">IS</span>
            </div>
            <div style="font-size:9px;color:#5a7494;letter-spacing:1.5px;text-transform:uppercase">Digital Twin</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    menu = st.radio(
        "",
        ["🔲  Vue d'ensemble", "📈  Monitoring", "📊  Analyse",
         "🔧  Maintenance", "🔔  Alertes", "📄  Rapports", "⚙️  Paramètres"],
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("<hr style='border-color:#2a3547;margin:16px 0'>", unsafe_allow_html=True)
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;padding:4px 0">
        <div style="width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,#1e40af,#3b82f6);
             display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:600;color:#fff;flex-shrink:0">Ad</div>
        <div>
            <div style="font-size:13px;font-weight:500;color:#e8edf5">Admin</div>
            <div style="font-size:11px;color:#5a7494">Administrateur</div>
        </div>
    </div>
    <div style="margin-top:12px;font-size:11px;color:#5a7494">
        <span style="cursor:pointer">☾ Thème sombre</span>
    </div>
    """, unsafe_allow_html=True)


# ── HEADER ────────────────────────────────────────────────────────────────────
now = datetime.now().strftime("%d/%m/%Y  %H:%M:%S")
st.markdown(f"""
<div class="status-header">
    <div>
        <div style="font-size:16px;font-weight:600;color:#e8edf5;letter-spacing:.3px">
            ⚡ Centrale Photovoltaïque — Sunfield 1
        </div>
        <div style="font-size:11px;color:#5a7494;margin-top:3px">
            Lieu: Toulouse, France &nbsp;|&nbsp; Puissance installée: 2.35 MWc &nbsp;|&nbsp; Mise en service: 04/2023
        </div>
    </div>
    <div style="display:flex;align-items:center;gap:24px">
        <div style="font-size:13px;color:#e8edf5">☀️ 23°C</div>
        <div style="font-size:12px;color:#8fa3bf;font-family:'IBM Plex Mono',monospace">{now}</div>
        <div class="status-ok"><span class="status-dot"></span>Système normal</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── TOP METRICS ───────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("⚡ Puissance actuelle", "1.65 MW", "+0.12 MW")
with c2:
    st.metric("📅 Production du jour", "7.48 MWh", "+0.3 MWh")
with c3:
    st.metric("📦 Production totale", "1.25 GWh", "+7.48 MWh")
with c4:
    st.metric("🎯 PR (Performance Ratio)", "82.6 %", "-1.2 %")

st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)


# ── MAIN AREA: Image + Bottom Panels ─────────────────────────────────────────
# Aerial photo with overlay chips
st.markdown("""
<div style="position:relative;border-radius:10px;overflow:hidden;border:1px solid #2a3547;margin-bottom:12px">
    <img src="https://images.unsplash.com/photo-1509395176047-4a66953fd231?w=1200&q=80"
         style="width:100%;height:240px;object-fit:cover;opacity:.8;display:block"/>
    <div style="position:absolute;top:10px;left:10px;display:flex;gap:8px;flex-wrap:wrap">
        <div style="background:rgba(13,17,23,.82);border:1px solid #3a4d66;border-radius:8px;
             padding:5px 12px;font-size:12px;color:#e8edf5;display:flex;align-items:center;gap:6px;backdrop-filter:blur(4px)">
            🌡️ 23.4 °C
        </div>
        <div style="background:rgba(13,17,23,.82);border:1px solid #3a4d66;border-radius:8px;
             padding:5px 12px;font-size:12px;color:#e8edf5;display:flex;align-items:center;gap:6px;backdrop-filter:blur(4px)">
            ☀️ Irradiance 812 W/m²
        </div>
        <div style="background:rgba(13,17,23,.82);border:1px solid #3a4d66;border-radius:8px;
             padding:5px 12px;font-size:12px;color:#22c55e;display:flex;align-items:center;gap:6px;backdrop-filter:blur(4px)">
            🔌 Onduleur 2 — 98.6 %
        </div>
    </div>
    <div style="position:absolute;bottom:10px;right:10px;background:rgba(13,17,23,.7);
         border-radius:6px;padding:4px 10px;font-size:10px;color:#5a7494">
        Vue 3D · Toulouse, France
    </div>
</div>
""", unsafe_allow_html=True)


# ── BOTTOM PANELS ────────────────────────────────────────────────────────────
col_weather, col_inv, col_prod = st.columns(3)

# -- Météo
with col_weather:
    st.markdown('<div class="section-title">Météo locale</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="weather-card">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px">
            <div style="font-size:36px">☀️</div>
            <div>
                <div class="weather-temp">23°C</div>
                <div style="font-size:11px;color:#5a7494">Ensoleillé</div>
            </div>
        </div>
        <div class="weather-row">
            <span class="weather-label">Irradiance</span>
            <span class="weather-val">812 W/m²</span>
        </div>
        <div class="weather-row">
            <span class="weather-label">Vitesse du vent</span>
            <span class="weather-val">12 km/h</span>
        </div>
        <div class="weather-row">
            <span class="weather-label">Humidité</span>
            <span class="weather-val">45 %</span>
        </div>
        <div class="weather-row" style="border-bottom:none">
            <span class="weather-label">Température module</span>
            <span class="weather-val">34.2 °C</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# -- Onduleurs
with col_inv:
    st.markdown('<div class="section-title">État des onduleurs</div>', unsafe_allow_html=True)
    fig_inv = go.Figure(go.Pie(
        values=[22, 1, 1, 0],
        labels=["En fonctionnement", "Avertissement", "Hors ligne", "Maintenance"],
        hole=0.68,
        marker=dict(colors=["#22c55e", "#eab308", "#ef4444", "#3a4d66"],
                    line=dict(color="#0d1117", width=2)),
        textinfo="none",
        hovertemplate="<b>%{label}</b>: %{value}<extra></extra>",
        sort=False,
    ))
    fig_inv.add_annotation(text="24", x=0.5, y=0.55, font=dict(size=26, color="#e8edf5",
                           family="IBM Plex Mono"), showarrow=False)
    fig_inv.add_annotation(text="Total", x=0.5, y=0.38, font=dict(size=11, color="#5a7494",
                           family="IBM Plex Sans"), showarrow=False)
    fig_inv.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        height=150,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_inv, use_container_width=True, config={"displayModeBar": False})
    st.markdown("""
    <div style="display:flex;flex-direction:column;gap:5px;margin-top:-10px">
        <div class="inv-row"><span class="inv-dot" style="background:#22c55e"></span>
            <span style="color:#e8edf5;font-weight:500">22</span>
            <span style="color:#5a7494">En fonctionnement</span></div>
        <div class="inv-row"><span class="inv-dot" style="background:#eab308"></span>
            <span style="color:#e8edf5;font-weight:500">1</span>
            <span style="color:#5a7494">Avertissement</span></div>
        <div class="inv-row"><span class="inv-dot" style="background:#ef4444"></span>
            <span style="color:#e8edf5;font-weight:500">1</span>
            <span style="color:#5a7494">Hors ligne</span></div>
        <div class="inv-row"><span class="inv-dot" style="background:#3a4d66"></span>
            <span style="color:#e8edf5;font-weight:500">0</span>
            <span style="color:#5a7494">Maintenance</span></div>
    </div>
    """, unsafe_allow_html=True)

# -- Répartition production
with col_prod:
    st.markdown('<div class="section-title">Répartition de la production</div>', unsafe_allow_html=True)
    fig_donut = go.Figure(go.Pie(
        values=[693, 627, 330],
        labels=["Champ 1", "Champ 2", "Champ 3"],
        hole=0.6,
        marker=dict(colors=["#378add", "#22c55e", "#eab308"],
                    line=dict(color="#0d1117", width=2)),
        textinfo="none",
        hovertemplate="<b>%{label}</b>: %{value} kW (%{percent})<extra></extra>",
        sort=False,
    ))
    fig_donut.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        height=140,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})

    for name, pct, kw, color in [("Champ 1","42 %","693 kW","#378add"),
                                   ("Champ 2","38 %","627 kW","#22c55e"),
                                   ("Champ 3","20 %","330 kW","#eab308")]:
        st.markdown(f"""
        <div style="display:flex;align-items:center;justify-content:space-between;
             font-size:12px;padding:4px 0;border-bottom:1px solid #2a3547">
            <div style="display:flex;align-items:center;gap:7px">
                <span style="width:9px;height:9px;border-radius:2px;background:{color};display:inline-block"></span>
                <span style="color:#8fa3bf">{name}</span>
            </div>
            <div style="display:flex;gap:12px">
                <span style="font-family:'IBM Plex Mono',monospace;color:#e8edf5;font-weight:500">{pct}</span>
                <span style="font-family:'IBM Plex Mono',monospace;color:#5a7494">{kw}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ── PRODUCTION CURVE + ALERTS ────────────────────────────────────────────────
st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)
col_chart, col_alerts = st.columns([2, 1])

with col_chart:
    st.markdown('<div class="section-title">Courbe de production du jour</div>', unsafe_allow_html=True)

    hours = list(range(25))
    labels_h = [f"{h:02d}:00" for h in hours]
    actual = [0,0,0,0,0,0,0.05,0.3,0.7,1.1,1.5,1.8,2.0,1.85,1.6,1.3,0.9,0.5,0.2,0.05,0,0,0,0,0]
    forecast=[0,0,0,0,0,0,0.04,0.25,0.65,1.05,1.45,1.75,1.95,1.8,1.55,1.25,0.85,0.45,0.15,0.02,0,0,0,0,0]

    fig_prod = go.Figure()
    fig_prod.add_trace(go.Scatter(
        x=labels_h, y=actual, name="Production",
        line=dict(color="#3b82f6", width=2),
        fill="tozeroy", fillcolor="rgba(59,130,246,0.12)",
        mode="lines"
    ))
    fig_prod.add_trace(go.Scatter(
        x=labels_h, y=forecast, name="Prévision",
        line=dict(color="#5a7494", width=1.5, dash="dash"),
        mode="lines"
    ))
    fig_prod.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=200,
        margin=dict(l=32, r=8, t=8, b=32),
        legend=dict(orientation="h", y=-0.25, x=0,
                    font=dict(color="#8fa3bf", size=11),
                    bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(tickfont=dict(color="#5a7494", size=9), gridcolor="#2a3547",
                   tickmode="array",
                   tickvals=[labels_h[i] for i in [0,4,8,12,16,20,24]],
                   linecolor="#2a3547"),
        yaxis=dict(tickfont=dict(color="#5a7494", size=9), gridcolor="#2a3547",
                   ticksuffix=" MW", range=[0, 2.6], linecolor="#2a3547"),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#161b22", bordercolor="#3a4d66",
                        font=dict(color="#e8edf5", size=11)),
    )
    st.plotly_chart(fig_prod, use_container_width=True, config={"displayModeBar": False})

with col_alerts:
    st.markdown('<div class="section-title">Alertes récentes</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="alert-warn">
        <div>
            <span class="alert-name-warn">⚠ Onduleur 7 — Avertissement</span>
            <span class="alert-time">09:47</span>
        </div>
        <div class="alert-desc">Puissance réduite</div>
    </div>
    <div class="alert-err">
        <div>
            <span class="alert-name-err">⚠ Station météo — Communication perdue</span>
            <span class="alert-time">08:15</span>
        </div>
        <div class="alert-desc">Vérifier la connexion</div>
    </div>
    <div class="alert-warn">
        <div>
            <span class="alert-name-warn">⚠ Nettoyage champ 2 recommandé</span>
            <span class="alert-time">Hier 14:32</span>
        </div>
        <div class="alert-desc">Perte estimée: 2.3 %</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)
    if st.button("Voir toutes les alertes →", use_container_width=True):
        st.info("Navigation vers la page Alertes…")

# ── AUTO-REFRESH (optionnel) ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<hr style='border-color:#2a3547;margin:8px 0'>", unsafe_allow_html=True)
    auto_refresh = st.checkbox("⟳  Actualisation automatique", value=False)
    if auto_refresh:
        refresh_rate = st.slider("Intervalle (sec)", 5, 60, 10)
        st.caption(f"Prochaine actualisation dans {refresh_rate}s")
        time.sleep(refresh_rate)
        st.rerun()
