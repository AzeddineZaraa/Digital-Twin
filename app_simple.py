import streamlit as st
import requests
import pandas as pd
import numpy as np
import time
import yaml
from datetime import datetime

# =========================
# PAGE CONFIG (must be first)
# =========================
st.set_page_config(
    page_title="Digital Twin PV",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# CONFIG LOAD
# =========================
try:
    with open("config.yaml", "r") as f:
        import yaml
        config = yaml.safe_load(f)
    from model import PVModel
    model = PVModel(config)
    USE_MODEL = True
except Exception:
    USE_MODEL = False
    config = {
        "site": {"latitude": 33.6, "longitude": -7.6, "tz": "Africa/Casablanca",
                 "altitude": 56, "tilt": 31, "azimuth": 180},
        "blynk": {"server": "", "token": ""},
        "installation": {"panels": 12, "dc_power_kwc": 3.96, "inverter_kw": 4.0,
                         "strings": 2, "technology": "Monocristallin"}
    }

# =========================
# CUSTOM CSS — match image design exactly
# =========================
st.markdown("""
<style>
/* ---- Google Fonts ---- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ---- Root variables ---- */
:root {
    --bg: #f5f6fa;
    --card: #ffffff;
    --border: #e8eaed;
    --text: #1a1d23;
    --muted: #6b7280;
    --blue: #3b82f6;
    --green: #10b981;
    --orange: #f97316;
    --yellow: #eab308;
    --purple: #8b5cf6;
    --sidebar-bg: #ffffff;
    --sidebar-active: #eff6ff;
    --sidebar-active-color: #3b82f6;
    --radius: 12px;
    --shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04);
    --shadow-md: 0 4px 6px rgba(0,0,0,0.07), 0 2px 4px rgba(0,0,0,0.05);
}

/* ---- Base reset ---- */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

/* ---- Hide default streamlit elements ---- */
#MainMenu, footer, header { display: none !important; }
.stDeployButton { display: none !important; }
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ---- Sidebar ---- */
[data-testid="stSidebar"] {
    background: var(--sidebar-bg) !important;
    border-right: 1px solid var(--border) !important;
    width: 230px !important;
    min-width: 230px !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
}

/* ---- Main content wrapper ---- */
.main-wrapper {
    padding: 0;
    background: var(--bg);
}

/* ---- Top header bar ---- */
.top-header {
    background: #ffffff;
    border-bottom: 1px solid var(--border);
    padding: 14px 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: var(--shadow);
}
.top-header-left {
    display: flex;
    align-items: center;
    gap: 14px;
}
.brand-title {
    font-size: 22px;
    font-weight: 700;
    color: var(--text);
    letter-spacing: -0.5px;
}
.brand-title span { color: var(--blue); }
.brand-sub {
    font-size: 11px;
    color: var(--muted);
    font-weight: 500;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}
.top-header-right {
    display: flex;
    align-items: center;
    gap: 18px;
    font-size: 14px;
    color: var(--muted);
}
.time-block {
    text-align: right;
}
.time-block .time { font-size: 20px; font-weight: 700; color: var(--text); }
.time-block .date { font-size: 12px; color: var(--muted); }
.mode-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 7px 14px;
    border: 1px solid var(--border);
    border-radius: 8px;
    background: #fff;
    font-size: 13px;
    font-weight: 500;
    color: var(--text);
    cursor: pointer;
}

/* ---- KPI Cards ---- */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 20px;
}
.kpi-card {
    background: var(--card);
    border-radius: var(--radius);
    padding: 18px 20px;
    box-shadow: var(--shadow);
    border: 1px solid var(--border);
    position: relative;
    overflow: hidden;
}
.kpi-card.orange { border-top: 3px solid var(--orange); }
.kpi-card.yellow { border-top: 3px solid var(--yellow); }
.kpi-card.blue   { border-top: 3px solid var(--blue); }
.kpi-card.green  { border-top: 3px solid var(--green); }

.kpi-label {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 10px;
}
.kpi-row {
    display: flex;
    align-items: center;
    gap: 12px;
}
.kpi-icon { font-size: 28px; }
.kpi-value {
    font-size: 30px;
    font-weight: 700;
    color: var(--text);
    line-height: 1;
}
.kpi-unit { font-size: 16px; font-weight: 400; color: var(--muted); }
.kpi-badge {
    font-size: 11px;
    font-weight: 600;
    margin-top: 6px;
}
.kpi-badge.orange { color: var(--orange); }
.kpi-badge.yellow { color: var(--yellow); }
.kpi-badge.blue   { color: var(--blue); }
.kpi-badge.green  { color: var(--green); }

/* ---- Section cards ---- */
.section-card {
    background: var(--card);
    border-radius: var(--radius);
    padding: 20px 24px;
    box-shadow: var(--shadow);
    border: 1px solid var(--border);
    margin-bottom: 20px;
}
.section-title {
    font-size: 14px;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 16px;
    letter-spacing: -0.2px;
}
.section-title .blue  { color: var(--blue); }
.section-title .green { color: var(--green); }

/* ---- Performance indicators ---- */
.perf-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 16px;
}
.perf-item {
    text-align: center;
}
.perf-label {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 8px;
}
.perf-value {
    font-size: 24px;
    font-weight: 700;
    color: var(--text);
}
.perf-sub {
    font-size: 11px;
    color: var(--muted);
    margin-top: 2px;
}
.perf-green { color: var(--green) !important; }
.perf-blue  { color: var(--blue)  !important; }
.perf-orange{ color: var(--orange)!important; }

/* ---- EMS Panel ---- */
.ems-card {
    background: var(--card);
    border-radius: var(--radius);
    padding: 20px;
    box-shadow: var(--shadow);
    border: 1px solid var(--border);
}
.ems-title {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    color: var(--text);
    margin-bottom: 14px;
}
.ems-status {
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 16px;
}
.ems-status.surplus {
    background: #d1fae5;
    border: 1px solid #6ee7b7;
}
.ems-status.deficit {
    background: #fef3c7;
    border: 1px solid #fcd34d;
}
.ems-status-title {
    font-size: 13px;
    font-weight: 700;
    color: #065f46;
    display: flex;
    align-items: center;
    gap: 6px;
}
.ems-status-sub {
    font-size: 11px;
    color: #047857;
    margin-top: 4px;
}

/* ---- Relay controls ---- */
.relay-item {
    margin-bottom: 14px;
    padding-bottom: 14px;
    border-bottom: 1px solid var(--border);
}
.relay-item:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
.relay-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}
.relay-name {
    font-size: 13px;
    font-weight: 700;
    color: var(--text);
    display: flex;
    align-items: center;
    gap: 6px;
}
.relay-tag {
    font-size: 10px;
    background: var(--bg);
    color: var(--muted);
    padding: 2px 7px;
    border-radius: 4px;
    font-weight: 600;
}
.relay-state {
    font-size: 11px;
    margin-top: 5px;
    font-weight: 500;
}
.relay-state.on  { color: var(--green); }
.relay-state.off { color: #ef4444; }

/* ---- Sidebar nav ---- */
.sidebar-logo {
    padding: 20px 16px 10px;
    border-bottom: 1px solid var(--border);
}
.sidebar-brand { font-size: 15px; font-weight: 700; color: var(--text); }
.sidebar-brand span { color: var(--blue); }
.sidebar-city { font-size: 10px; text-transform: uppercase; letter-spacing: 0.8px; color: var(--muted); }
.sidebar-nav { padding: 10px 8px; }
.sidebar-nav-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 9px 12px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 500;
    color: var(--muted);
    cursor: pointer;
    margin-bottom: 2px;
    transition: all 0.15s;
}
.sidebar-nav-item.active {
    background: var(--sidebar-active);
    color: var(--sidebar-active-color);
    font-weight: 600;
}
.sidebar-section-title {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    color: var(--muted);
    padding: 14px 12px 6px;
}
.info-row {
    display: flex;
    align-items: flex-start;
    gap: 7px;
    font-size: 12px;
    color: var(--muted);
    margin-bottom: 5px;
    padding: 0 12px;
}
.info-label { color: var(--text); font-weight: 500; }
.status-pill {
    display: flex;
    align-items: center;
    gap: 7px;
    padding: 8px 12px;
    background: #d1fae5;
    border-radius: 8px;
    margin: 6px 12px;
}
.status-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--green); flex-shrink: 0; }
.status-label { font-size: 12px; font-weight: 700; color: #065f46; }
.status-sub { font-size: 10px; color: #047857; }

/* ---- Footer ---- */
.dash-footer {
    padding: 12px 28px;
    border-top: 1px solid var(--border);
    background: #fff;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 11px;
    color: var(--muted);
}

/* ---- Streamlit overrides ---- */
div[data-testid="metric-container"] { display: none; }
.stButton > button {
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    height: 38px !important;
    transition: all 0.15s !important;
}
.btn-on > button {
    background: var(--green) !important;
    color: white !important;
    border: none !important;
}
.btn-off > button {
    background: #f3f4f6 !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
}
.stPlotlyChart, .stAltairChart { border-radius: 8px; overflow: hidden; }

/* ---- Date picker style ---- */
.date-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 12px;
    font-weight: 500;
    color: var(--text);
    background: #fff;
}

/* Donut placeholder */
.donut-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# WEATHER & POWER
# =========================
def get_weather():
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": config["site"]["latitude"],
            "longitude": config["site"]["longitude"],
            "current": ["temperature_2m", "shortwave_radiation"],
            "timezone": config["site"].get("tz", "Africa/Casablanca")
        }
        r = requests.get(url, params=params, timeout=5)
        data = r.json()["current"]
        return float(data.get("temperature_2m", 25)), float(data.get("shortwave_radiation", 742))
    except:
        return 23.4, 742.0

def get_real_power():
    try:
        url = f"{config['blynk']['server']}/external/api/get?token={config['blynk']['token']}&V2"
        return float(requests.get(url, timeout=3).text)
    except:
        return 2650.0

def control_relay(pin, state):
    try:
        url = f"{config['blynk']['server']}/external/api/update?token={config['blynk']['token']}&{pin}={state}"
        requests.get(url, timeout=3)
    except:
        pass

# =========================
# SESSION STATE
# =========================
if "relay1" not in st.session_state: st.session_state.relay1 = True
if "relay2" not in st.session_state: st.session_state.relay2 = False
if "history" not in st.session_state: st.session_state.history = []
if "dark" not in st.session_state: st.session_state.dark = False

# =========================
# FETCH DATA
# =========================
temp, irradiance = get_weather()
real_power = get_real_power()

# Model calculation
if USE_MODEL:
    result = model.compute(irradiance, temp)
    model_power = result["p_ac_kw"]
else:
    # Demo: simple estimation
    model_power = round((irradiance / 1000) * 3.96 * 0.82 * 0.962, 3)  # kW

real_power_kw = real_power / 1000 if real_power > 100 else real_power
model_power_kw = model_power if model_power < 20 else model_power / 1000

# Performance metrics
perf_ratio = real_power_kw / max(model_power_kw, 0.01)
rendement_sys = (real_power_kw / max(3.96, 0.01)) * 100
rendement_onduleur = 96.2
temp_cell = temp + (irradiance * 0.03)
energy_day = real_power_kw * 3.67  # rough kWh estimate

# Build history
st.session_state.history.append({
    "model_w": model_power_kw * 1000,
    "real_w":  real_power_kw  * 1000
})
if len(st.session_state.history) > 200:
    st.session_state.history = st.session_state.history[-200:]

now = datetime.now()

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-logo">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;">
            <span style="font-size:28px;">☀️</span>
            <div>
                <div class="sidebar-brand">DIGITAL TWIN <span>PV</span></div>
                <div class="sidebar-city">MOHAMMEDIA, MAROC</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-nav">
        <div class="sidebar-nav-item active">🏠 Dashboard</div>
        <div class="sidebar-nav-item">📊 Données</div>
        <div class="sidebar-nav-item">📈 Graphiques</div>
        <div class="sidebar-nav-item">⚡ EMS &amp; Relais</div>
        <div class="sidebar-nav-item">⚙️ Paramètres</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section-title">État du Système</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="status-pill">
        <div class="status-dot"></div>
        <div>
            <div class="status-label">SYSTÈME ACTIF</div>
            <div class="status-sub">Tout fonctionne normalement</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section-title">Site</div>', unsafe_allow_html=True)
    lat = config["site"]["latitude"]
    lon = config["site"]["longitude"]
    alt = config["site"].get("altitude", 56)
    tilt = config["site"].get("tilt", 31)
    az = config["site"].get("azimuth", 180)
    st.markdown(f"""
    <div class="info-row">📍 <span class="info-label">Mohammedia, Maroc</span></div>
    <div class="info-row">📐 <span class="info-label">{lat}° N, {abs(lon)}° W</span></div>
    <div class="info-row">⛰️ <span class="info-label">Altitude {alt} m</span></div>
    <div class="info-row">🔭 <span class="info-label">Tilt: {tilt}° | Azimuth: {az}°</span></div>
    """, unsafe_allow_html=True)

    panels = config.get("installation", {}).get("panels", 12)
    dc_kw  = config.get("installation", {}).get("dc_power_kwc", 3.96)
    inv_kw = config.get("installation", {}).get("inverter_kw", 4.0)
    strings= config.get("installation", {}).get("strings", 2)
    tech   = config.get("installation", {}).get("technology", "Monocristallin")

    st.markdown('<div class="sidebar-section-title">Installation</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="info-row">⊞ <span class="info-label">{panels} Panneaux</span></div>
    <div class="info-row">⚡ <span class="info-label">Puissance DC: {dc_kw} kWc</span></div>
    <div class="info-row">🔁 <span class="info-label">Onduleur: {inv_kw} kW</span></div>
    <div class="info-row">🔗 <span class="info-label">Strings/MPPT: {strings}</span></div>
    <div class="info-row">🔬 <span class="info-label">Technologie: {tech}</span></div>
    """, unsafe_allow_html=True)

# =========================
# MAIN CONTENT
# =========================
main = st.container()
with main:
    # ---- TOP HEADER ----
    mode_icon = "🌙" if not st.session_state.dark else "☀️"
    mode_label = "Mode Clair" if not st.session_state.dark else "Mode Sombre"
    st.markdown(f"""
    <div class="top-header">
        <div class="top-header-left">
            <span style="font-size:36px;">☀️</span>
            <div>
                <div class="brand-title">DIGITAL TWIN <span>PV</span></div>
                <div class="brand-sub">MOHAMMEDIA, MAROC</div>
            </div>
        </div>
        <div class="top-header-right">
            <div>👤</div>
            <div class="time-block">
                <div class="time">{now.strftime('%H:%M:%S')}</div>
                <div class="date">{now.strftime('%d %b %Y')}</div>
            </div>
            <div class="mode-btn">{mode_icon} {mode_label}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # ---- CONTENT AREA with padding ----
    st.markdown("<div style='padding:0 24px'>", unsafe_allow_html=True)

    # ---- KPI CARDS ----
    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-card orange">
            <div class="kpi-label">Température Ambiante</div>
            <div class="kpi-row">
                <span class="kpi-icon">🌡️</span>
                <div>
                    <div class="kpi-value">{temp:.1f} <span class="kpi-unit">°C</span></div>
                    <div class="kpi-badge orange">En temps réel</div>
                </div>
            </div>
        </div>
        <div class="kpi-card yellow">
            <div class="kpi-label">Irradiance (GHI)</div>
            <div class="kpi-row">
                <span class="kpi-icon">☀️</span>
                <div>
                    <div class="kpi-value">{irradiance:.0f} <span class="kpi-unit">W/m²</span></div>
                    <div class="kpi-badge yellow">En temps réel</div>
                </div>
            </div>
        </div>
        <div class="kpi-card blue">
            <div class="kpi-label">Puissance Modèle (AC)</div>
            <div class="kpi-row">
                <span class="kpi-icon">📈</span>
                <div>
                    <div class="kpi-value">{model_power_kw:.2f} <span class="kpi-unit">kW</span></div>
                    <div class="kpi-badge blue">Simulation</div>
                </div>
            </div>
        </div>
        <div class="kpi-card green">
            <div class="kpi-label">Puissance Réelle (AC)</div>
            <div class="kpi-row">
                <span class="kpi-icon">⚡</span>
                <div>
                    <div class="kpi-value">{real_power_kw:.2f} <span class="kpi-unit">kW</span></div>
                    <div class="kpi-badge green">Mesurée (Blynk)</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ---- TWO COLUMNS: Chart + EMS ----
    col_chart, col_ems = st.columns([2.6, 1], gap="large")

    with col_chart:
        st.markdown("""
        <div class="section-card" style="margin-bottom:16px">
            <div class="section-title">
                PUISSANCE : <span class="blue">MODÈLE</span> vs <span class="green">RÉEL</span>
            </div>
        """, unsafe_allow_html=True)

        # Build dataframe for chart
        if len(st.session_state.history) > 1:
            df = pd.DataFrame(st.session_state.history)
            df.columns = ["Puissance Modèle (W)", "Puissance Réelle (W)"]
        else:
            # Synthetic bell curve for demo (mimics solar day)
            hours = np.linspace(0, 24, 200)
            bell = np.maximum(0, 3800 * np.exp(-((hours - 12.5) ** 2) / 18))
            real  = bell * 0.87 + np.random.normal(0, 60, 200)
            real  = np.clip(real, 0, None)
            df = pd.DataFrame({
                "Puissance Modèle (W)": bell,
                "Puissance Réelle (W)": real
            })

        import altair as alt
        df_reset = df.reset_index().rename(columns={"index": "t"})
        df_melt = df_reset.melt("t", var_name="Série", value_name="Puissance (W)")

        color_scale = alt.Scale(
            domain=["Puissance Modèle (W)", "Puissance Réelle (W)"],
            range=["#3b82f6", "#10b981"]
        )
        chart = (
            alt.Chart(df_melt)
            .mark_area(opacity=0.15, interpolate="monotone")
            .encode(
                x=alt.X("t:Q", axis=alt.Axis(title=None, labelFontSize=11, grid=False, tickCount=6)),
                y=alt.Y("Puissance (W):Q", axis=alt.Axis(title="Puissance (W)", labelFontSize=11, grid=True, gridColor="#f0f0f0")),
                color=alt.Color("Série:N", scale=color_scale, legend=alt.Legend(orient="top", title=None, labelFontSize=12))
            )
        ) + (
            alt.Chart(df_melt)
            .mark_line(interpolate="monotone", strokeWidth=2)
            .encode(
                x="t:Q",
                y="Puissance (W):Q",
                color=alt.Color("Série:N", scale=color_scale, legend=None)
            )
        )
        chart = chart.properties(height=260).configure_view(strokeWidth=0).configure_axis(labelFont="Inter", titleFont="Inter")
        st.altair_chart(chart, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # ---- PERFORMANCE INDICATORS ----
        st.markdown(f"""
        <div class="section-card">
            <div class="section-title">INDICATEURS DE PERFORMANCE</div>
            <div class="perf-grid">
                <div class="perf-item">
                    <div class="perf-label">Performance Ratio (DC)</div>
                    <div class="perf-value">{min(perf_ratio, 1.0):.2f}</div>
                    <div class="perf-sub perf-green">{min(perf_ratio*100,100):.1f}%</div>
                </div>
                <div class="perf-item">
                    <div class="perf-label">Rendement Système (AC)</div>
                    <div class="perf-value perf-blue">{min(rendement_sys,100):.1f}%</div>
                    <div class="perf-sub">En temps réel</div>
                </div>
                <div class="perf-item">
                    <div class="perf-label">Rendement Onduleur</div>
                    <div class="perf-value">{rendement_onduleur:.1f}%</div>
                    <div class="perf-sub">En temps réel</div>
                </div>
                <div class="perf-item">
                    <div class="perf-label">Température Cellule</div>
                    <div class="perf-value perf-orange">{temp_cell:.1f}°C</div>
                    <div class="perf-sub">Calculée</div>
                </div>
                <div class="perf-item">
                    <div class="perf-label">Énergie du Jour (AC)</div>
                    <div class="perf-value perf-green">{energy_day:.2f} kWh</div>
                    <div class="perf-sub">Depuis 00:00</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_ems:
        surplus = model_power_kw > real_power_kw

        if surplus:
            ems_html = """
            <div class="ems-status surplus">
                <div class="ems-status-title">✅ SURPLUS PV</div>
                <div class="ems-status-sub">Production suffisante<br>Charges peuvent être activées</div>
            </div>
            """
        else:
            ems_html = """
            <div class="ems-status deficit">
                <div class="ems-status-title">⚠️ DÉFICIT PV</div>
                <div class="ems-status-sub">Production insuffisante<br>Éviter d'activer des charges</div>
            </div>
            """

        r1_state = "ON" if st.session_state.relay1 else "OFF"
        r2_state = "ON" if st.session_state.relay2 else "OFF"
        r1_color = "on" if st.session_state.relay1 else "off"
        r2_color = "on" if st.session_state.relay2 else "off"

        st.markdown(f"""
        <div class="ems-card">
            <div class="ems-title">EMS — GESTION DES CHARGES</div>
            {ems_html}
            <div class="relay-item">
                <div class="relay-header">
                    <div class="relay-name">🔌 CHARGE 1 <span class="relay-tag">RELAIS V3</span></div>
                </div>
        """, unsafe_allow_html=True)

        c1a, c1b = st.columns(2)
        with c1a:
            st.markdown('<div class="btn-on">', unsafe_allow_html=True)
            if st.button("⏻ ON", key="r1on"):
                st.session_state.relay1 = True
                control_relay("V3", 1)
            st.markdown('</div>', unsafe_allow_html=True)
        with c1b:
            st.markdown('<div class="btn-off">', unsafe_allow_html=True)
            if st.button("OFF", key="r1off"):
                st.session_state.relay1 = False
                control_relay("V3", 0)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f"""
                <div class="relay-state {r1_color}">État actuel: <b>{r1_state}</b></div>
            </div>
            <div class="relay-item">
                <div class="relay-header">
                    <div class="relay-name">🖥️ CHARGE 2 <span class="relay-tag">RELAIS V4</span></div>
                </div>
        """, unsafe_allow_html=True)

        c2a, c2b = st.columns(2)
        with c2a:
            st.markdown('<div class="btn-on">', unsafe_allow_html=True)
            if st.button("⏻ ON", key="r2on"):
                st.session_state.relay2 = True
                control_relay("V4", 1)
            st.markdown('</div>', unsafe_allow_html=True)
        with c2b:
            st.markdown('<div class="btn-off">', unsafe_allow_html=True)
            if st.button("OFF", key="r2off"):
                st.session_state.relay2 = False
                control_relay("V4", 0)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f"""
                <div class="relay-state {r2_color}">État actuel: <b>{r2_state}</b></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ---- FOOTER ----
    st.markdown(f"""
    <div class="dash-footer">
        <span>🔄 Mise à jour: {now.strftime('%H:%M:%S')}</span>
        <span>☁️ Source Météo: Open-Meteo</span>
        <span>☀️ Digital Twin PV — Mohammedia</span>
    </div>
    """, unsafe_allow_html=True)

# =========================
# AUTO-REFRESH (every 30s)
# =========================
time.sleep(30)
st.rerun()
