"""
SOLARIS - Digital Twin PV · Mohammedia, Maroc
Streamlit + pvlib · Open-Meteo API
GitHub Deployment Ready
"""


import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pvlib
from pvlib.location import Location
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
# CONFIGURATION STREAMLIT
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="SOLARIS · Digital Twin Mohammedia",
    page_icon="S",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# CSS PERSONNALISE
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600;700&display=swap');

    :root {
        --solar-yellow: #F5A623;
        --solar-orange: #E8860A;
        --solar-amber: #FFCF6B;
        --dark-bg: #08090C;
        --card-bg: #111318;
        --card-bg2: #191D25;
        --border: #252A35;
        --border-bright: #353C4A;
        --text-primary: #E8EDF5;
        --text-secondary: #6B7585;
        --text-muted: #3D4553;
        --green: #2ECC71;
        --red: #E74C3C;
        --blue: #3498DB;
        --purple: #9B59B6;
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        background-color: var(--dark-bg);
        background-image:
            radial-gradient(ellipse at 20% 0%, rgba(245,166,35,0.04) 0%, transparent 60%),
            radial-gradient(ellipse at 80% 100%, rgba(52,152,219,0.03) 0%, transparent 60%);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0A0C10 !important;
        border-right: 1px solid var(--border) !important;
    }

    [data-testid="stSidebar"] .stRadio label {
        font-family: 'DM Sans', sans-serif !important;
        color: var(--text-secondary) !important;
        font-size: 13px !important;
    }

    /* Main header */
    .main-header {
        background: linear-gradient(135deg, #0E1117 0%, #141820 100%);
        border: 1px solid var(--border);
        border-top: 2px solid var(--solar-yellow);
        border-radius: 0 0 12px 12px;
        padding: 22px 32px;
        margin-bottom: 24px;
    }

    .plant-name {
        font-family: 'Space Mono', monospace;
        font-size: 20px;
        font-weight: 700;
        color: var(--solar-yellow);
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }

    .plant-sub {
        font-size: 12px;
        color: var(--text-secondary);
        margin-top: 5px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        background: rgba(46, 204, 113, 0.08);
        border: 1px solid rgba(46, 204, 113, 0.25);
        border-radius: 20px;
        padding: 5px 14px;
        font-size: 12px;
        color: var(--green);
        font-family: 'Space Mono', monospace;
        letter-spacing: 0.05em;
    }

    .status-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: var(--green);
        box-shadow: 0 0 8px var(--green);
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.4; }
    }

    /* Metric cards */
    .metric-card {
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 20px 22px;
        position: relative;
        overflow: hidden;
    }

    .metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--solar-yellow), var(--solar-orange));
        opacity: 0.6;
    }

    .metric-label {
        font-size: 10px;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-family: 'Space Mono', monospace;
        margin-bottom: 8px;
    }

    .metric-value {
        font-family: 'Space Mono', monospace;
        font-size: 26px;
        font-weight: 700;
        color: var(--solar-yellow);
        line-height: 1.1;
    }

    .metric-unit {
        font-size: 13px;
        color: var(--text-secondary);
        font-family: 'DM Sans', sans-serif;
        font-weight: 400;
        margin-top: 4px;
    }

    /* Section title */
    .section-title {
        font-family: 'Space Mono', monospace;
        font-size: 11px;
        font-weight: 700;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.15em;
        margin-bottom: 14px;
        padding-bottom: 10px;
        border-bottom: 1px solid var(--border);
    }

    /* Alert cards */
    .alert-card {
        border-radius: 8px;
        padding: 11px 16px;
        margin-bottom: 8px;
        font-size: 13px;
        border-left: 3px solid;
        font-family: 'DM Sans', sans-serif;
    }

    .alert-warning {
        background: rgba(245,166,35,0.06);
        border-color: var(--solar-yellow);
        color: #D4993A;
    }

    .alert-error {
        background: rgba(231,76,60,0.06);
        border-color: var(--red);
        color: #D45C4E;
    }

    .alert-ok {
        background: rgba(46,204,113,0.06);
        border-color: var(--green);
        color: #3DBD6A;
    }

    /* Spec table */
    .spec-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
    }

    .spec-table tr {
        border-bottom: 1px solid var(--border);
    }

    .spec-table tr:last-child {
        border-bottom: none;
    }

    .spec-table td {
        padding: 10px 14px;
        vertical-align: middle;
    }

    .spec-table td:first-child {
        color: var(--text-secondary);
        font-family: 'Space Mono', monospace;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        width: 48%;
    }

    .spec-table td:last-child {
        color: var(--text-primary);
        font-weight: 500;
        text-align: right;
    }

    .spec-block {
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 4px 0;
        margin-bottom: 16px;
    }

    .spec-block-header {
        background: var(--card-bg2);
        border-radius: 8px 8px 0 0;
        padding: 10px 16px;
        font-family: 'Space Mono', monospace;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: var(--solar-yellow);
        border-bottom: 1px solid var(--border);
    }

    .highlight-value {
        color: var(--solar-yellow);
        font-family: 'Space Mono', monospace;
        font-weight: 700;
    }

    .badge-green {
        background: rgba(46,204,113,0.1);
        color: var(--green);
        border: 1px solid rgba(46,204,113,0.2);
        border-radius: 4px;
        padding: 2px 8px;
        font-size: 11px;
        font-family: 'Space Mono', monospace;
    }

    .badge-orange {
        background: rgba(245,166,35,0.1);
        color: var(--solar-yellow);
        border: 1px solid rgba(245,166,35,0.2);
        border-radius: 4px;
        padding: 2px 8px;
        font-size: 11px;
        font-family: 'Space Mono', monospace;
    }

    .badge-blue {
        background: rgba(52,152,219,0.1);
        color: var(--blue);
        border: 1px solid rgba(52,152,219,0.2);
        border-radius: 4px;
        padding: 2px 8px;
        font-size: 11px;
        font-family: 'Space Mono', monospace;
    }

    /* Override Streamlit metric styling */
    div[data-testid="metric-container"] {
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 16px 18px;
    }

    div[data-testid="metric-container"] label {
        color: var(--text-secondary) !important;
        font-size: 11px !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-family: 'Space Mono', monospace !important;
    }

    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: var(--solar-yellow) !important;
        font-size: 24px !important;
        font-weight: 700 !important;
        font-family: 'Space Mono', monospace !important;
    }

    .stPlotlyChart {
        border-radius: 10px;
        overflow: hidden;
    }

    /* Sidebar brand */
    .sidebar-brand {
        font-family: 'Space Mono', monospace;
        font-size: 18px;
        font-weight: 700;
        color: var(--solar-yellow);
        letter-spacing: 0.1em;
        margin-bottom: 4px;
    }

    .sidebar-sub {
        font-size: 11px;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 16px;
    }

    hr { border-color: var(--border) !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PARAMETRES DE LA CENTRALE - MOHAMMEDIA
# ─────────────────────────────────────────────
SITE = {
    "name": "Installation PV Casablanca",
    "location": "Casablanca, Maroc",
    "lat": 33.704780,
    "lon": -7.361500,
    "altitude": 56,
    "timezone": "Africa/Casablanca",
    "capacity_kwp": 3.95,
    "surface_m2": 23.27,
    "num_panels": 12,
    "num_inverters": 1,
    "commissioning_date": "2024",
    "operator": "ENSET",
    "grid_connection": "BT 220 V",
}
PANEL = {
    "manufacturer": "Cell Amrecan",
    "model": "OS-P72-330W",
    "technology": "Polycristallin",   # ligne manquante — cause du KeyError
    "pdc0": 330,
    "voc": 45.6,
    "isc": 9.45,
    "vmp": 37.2,
    "imp": 8.88,
    "efficiency_pct": 17.0,
    "gamma_pdc": -0.0040,
    "tilt": 31,
    "azimuth": 180,
    "warranty_years": 25,
    "degradation_pct_yr": 0.40,
}

INVERTER = {
    "manufacturer": "IMEON",
    "model": "IMEON 3.6",
    "power_kva": 4,
    "efficiency_pct": 96,
    "mppt_channels": 2,
    "voltage_dc_max": 500,
    "ip_class": "IP65",
}

STRUCTURE = {
    "type": "Fixe inclinee",
    "material": "A definir",
    "wind_load_ms": 40,
    "foundation": "Toiture / Sol",
    "rows": 2,          # 2 rangees de 6
    "panels_per_row": 6,
}


# ─────────────────────────────────────────────
# FONCTIONS PRINCIPALES
# ─────────────────────────────────────────────

@st.cache_data(ttl=3600)
def fetch_meteo(lat, lon, start_date, end_date):
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "temperature_2m,shortwave_radiation,diffuse_radiation,direct_normal_irradiance,wind_speed_10m,relative_humidity_2m",
        "timezone": "Africa/Casablanca",
    }
    try:
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        df = pd.DataFrame({
            "datetime": pd.to_datetime(data["hourly"]["time"]),
            "temp_air": data["hourly"]["temperature_2m"],
            "ghi": data["hourly"]["shortwave_radiation"],
            "dhi": data["hourly"]["diffuse_radiation"],
            "dni": data["hourly"]["direct_normal_irradiance"],
            "wind_speed": data["hourly"]["wind_speed_10m"],
            "humidity": data["hourly"]["relative_humidity_2m"],
        })
        df = df.set_index("datetime")
        return df
    except Exception as e:
        st.error(f"Erreur API meteo : {e}")
        return None


@st.cache_data(ttl=3600)
def run_pvlib_simulation(lat, lon, altitude, timezone, tilt, azimuth, pdc0, gamma_pdc, start_date, end_date):
    location = Location(
        latitude=lat, longitude=lon,
        altitude=altitude, tz=timezone, name="Mohammedia"
    )
    df = fetch_meteo(lat, lon, start_date, end_date)
    if df is None:
        return None

    times = df.index
    solar_pos = location.get_solarposition(times)

    poa = pvlib.irradiance.get_total_irradiance(
        surface_tilt=tilt, surface_azimuth=azimuth,
        dni=df["dni"], ghi=df["ghi"], dhi=df["dhi"],
        solar_zenith=solar_pos["apparent_zenith"],
        solar_azimuth=solar_pos["azimuth"],
    )

    temp_params = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS["sapm"]["open_rack_glass_glass"]
    cell_temp = pvlib.temperature.sapm_cell(
        poa_global=poa["poa_global"], temp_air=df["temp_air"],
        wind_speed=df["wind_speed"],
        a=temp_params["a"], b=temp_params["b"], deltaT=temp_params["deltaT"],
    )

    dc_power = pvlib.pvsystem.pvwatts_dc(
        g_poa_effective=poa["poa_global"], temp_cell=cell_temp,
        pdc0=pdc0, gamma_pdc=gamma_pdc,
    )
    ac_power = dc_power * 0.97

    results = pd.DataFrame({
        "datetime": times,
        "ghi": df["ghi"],
        "poa_global": poa["poa_global"],
        "temp_air": df["temp_air"],
        "cell_temp": cell_temp,
        "wind_speed": df["wind_speed"],
        "dc_power_w": dc_power,
        "ac_power_w": ac_power.clip(lower=0),
    })
    results["ac_power_kw"] = results["ac_power_w"] / 1000
    results["date"] = results["datetime"].dt.date
    results["hour"] = results["datetime"].dt.hour
    results["month"] = results["datetime"].dt.month
    results["month_name"] = results["datetime"].dt.strftime("%b")
    return results


def compute_daily(results, num_panels):
    daily = results.groupby("date").agg(
        production_kwh=("ac_power_kw", lambda x: x.sum()),
        peak_power_kw=("ac_power_kw", "max"),
        avg_temp=("temp_air", "mean"),
        avg_ghi=("ghi", "mean"),
        peak_sun_hours=("poa_global", lambda x: x.sum() / 1000),
    ).reset_index()
    daily["theoretical_kwh"] = daily["peak_sun_hours"] * (num_panels * 0.4)
    daily["pr"] = (daily["production_kwh"] / daily["theoretical_kwh"].replace(0, np.nan)).clip(0, 1) * 100
    daily["date"] = pd.to_datetime(daily["date"])
    return daily


def compute_monthly(daily):
    monthly = daily.groupby(daily["date"].dt.to_period("M")).agg(
        production_kwh=("production_kwh", "sum"),
        avg_pr=("pr", "mean"),
        avg_temp=("avg_temp", "mean"),
    ).reset_index()
    monthly["date"] = monthly["date"].dt.to_timestamp()
    monthly["month_name"] = monthly["date"].dt.strftime("%b %Y")
    return monthly


def get_current_meteo(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat, "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,shortwave_radiation",
        "timezone": "Africa/Casablanca",
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.json().get("current", {})
    except:
        return {}


PLOT_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="#111318",
    plot_bgcolor="#111318",
    font=dict(family="DM Sans", color="#6B7585"),
    margin=dict(t=20, b=30, l=50, r=20),
    xaxis=dict(gridcolor="#1E232D", zeroline=False),
    yaxis=dict(gridcolor="#1E232D", zeroline=False),
)


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-brand">SOLARIS</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">Digital Twin PV</div>', unsafe_allow_html=True)
    st.markdown("---")

    menu = st.radio(
        "Navigation",
        [
            "Vue Globale",
            "Production",
            "Meteo & Irradiance",
            "Onduleurs",
            "Installation",
            "Rapport",
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("**Periode d'analyse**")
    col_s, col_e = st.columns(2)
    with col_s:
        start_date = st.date_input("Debut", value=datetime(2026, 4, 1), label_visibility="collapsed")
    with col_e:
        end_date = st.date_input("Fin", value=datetime(2026, 4, 24), label_visibility="collapsed")

    st.markdown(f"Du **{start_date.strftime('%d/%m/%Y')}** au **{end_date.strftime('%d/%m/%Y')}**")

    st.markdown("---")
    st.markdown(f"Capacite : **{SITE['capacity_kwp']} kWp**")
    st.markdown(f"Panneaux : **{SITE['num_panels']}**")
    st.markdown(f"Onduleurs : **{SITE['num_inverters']}**")
    st.markdown(f"Inclinaison : **{PANEL['tilt']}**")


# ─────────────────────────────────────────────
# SIMULATION PVLIB
# ─────────────────────────────────────────────
with st.spinner("Simulation pvlib en cours..."):
    results = run_pvlib_simulation(
        lat=SITE["lat"], lon=SITE["lon"], altitude=SITE["altitude"],
        timezone=SITE["timezone"], tilt=PANEL["tilt"], azimuth=PANEL["azimuth"],
        pdc0=PANEL["pdc0"], gamma_pdc=PANEL["gamma_pdc"],
        start_date=str(start_date), end_date=str(end_date),
    )

if results is None:
    st.error("Impossible de recuperer les donnees. Verifiez votre connexion internet.")
    st.stop()

results["ac_power_kw"] = results["ac_power_kw"] * SITE["num_panels"]
daily = compute_daily(results, SITE["num_panels"])
monthly = compute_monthly(daily)
current_meteo = get_current_meteo(SITE["lat"], SITE["lon"])
now = datetime.now()


# ─────────────────────────────────────────────
# HEADER PRINCIPAL
# ─────────────────────────────────────────────
ghi_now = current_meteo.get('shortwave_radiation', 0) or 0
status_label = "SYSTEME NOMINAL" if ghi_now > 50 else "HORS PRODUCTION"

st.markdown(f"""
<div class="main-header">
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px">
        <div>
            <div class="plant-name">{SITE['name']}</div>
            <div class="plant-sub">
                {SITE['lat']}N, {abs(SITE['lon'])}W &nbsp;|&nbsp;
                {SITE['altitude']} m &nbsp;|&nbsp;
                {SITE['capacity_kwp']} kWp &nbsp;|&nbsp;
                Mohammedia, Maroc
            </div>
        </div>
        <div style="display:flex;align-items:center;gap:16px">
            <div style="text-align:right;font-size:12px;color:#6B7585;font-family:'Space Mono',monospace">
                {now.strftime('%d/%m/%Y %H:%M')}
            </div>
            <div class="status-badge">
                <div class="status-dot"></div>
                {status_label}
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# VUE GLOBALE
# ─────────────────────────────────────────────
if menu == "Vue Globale":
    col_img, col_perf = st.columns([2, 1])
    with col_img:
        st.image(
            "assets/Scene_enset.png",
            use_container_width=True,
        )
        c1, c2, c3 = st.columns(3)
        c1.metric("Temperature", f"{current_meteo.get('temperature_2m', '--')} C")
        c2.metric("Irradiance", f"{ghi_now} W/m2")
        c3.metric("Vent", f"{current_meteo.get('wind_speed_10m', '--')} km/h")
   with col_perf:
        st.markdown('<div class="section-title">Performance en temps reel</div>', unsafe_allow_html=True)
        current_hour = datetime.now().hour
        today_str = datetime.now().date()
        mask = (results["date"] == today_str) & (results["hour"] == current_hour)
        current_power = results.loc[mask, "ac_power_kw"].values
        current_power_val = current_power[0] if len(current_power) > 0 else 0.0
        st.metric("Puissance actuelle", f"{current_power_val:.2f} kW")
        st.metric("Production du jour", f"{daily['production_kwh'].iloc[-1]:.2f} kWh")
        st.metric("Production totale", f"{daily['production_kwh'].sum()/1000:.2f} MWh")
        st.metric("PR", f"{daily['pr'].mean():.1f} %")
    st.markdown("---")

    total_kwh = daily["production_kwh"].sum()
    avg_pr = daily["pr"].mean()
    peak_day_kwh = daily["production_kwh"].max()
    peak_day_date = daily.loc[daily["production_kwh"].idxmax(), "date"].strftime("%d/%m/%Y")
    avg_daily_kwh = daily["production_kwh"].mean()
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Production totale", f"{total_kwh/1000:.1f} MWh")
    k2.metric("Performance Ratio", f"{avg_pr:.1f} %")
    k3.metric("Meilleur jour", f"{peak_day_kwh:.0f} kWh", peak_day_date)
    k4.metric("Moy. journaliere", f"{avg_daily_kwh:.0f} kWh")
    k5.metric("Capacite installee", f"{SITE['capacity_kwp']} kWp")

    st.markdown("---")

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown('<div class="section-title">Production journaliere (kWh)</div>', unsafe_allow_html=True)
        fig_daily = go.Figure()
        colors = np.where(
            daily["production_kwh"] < daily["production_kwh"].quantile(0.2), "#E74C3C",
            np.where(daily["production_kwh"] > daily["production_kwh"].quantile(0.8), "#2ECC71", "#F5A623")
        )
        fig_daily.add_trace(go.Bar(
            x=daily["date"], y=daily["production_kwh"],
            name="Production",
            marker_color=colors, opacity=0.85,
        ))
        fig_daily.add_trace(go.Scatter(
            x=daily["date"],
            y=daily["production_kwh"].rolling(7, center=True).mean(),
            name="Moy. mobile 7j",
            line=dict(color="#3498DB", width=2),
        ))
        layout = dict(**PLOT_LAYOUT)
        layout["height"] = 320
        layout["showlegend"] = True
        layout["yaxis"] = dict(gridcolor="#1E232D", title="kWh", zeroline=False)
        fig_daily.update_layout(**layout)
        st.plotly_chart(fig_daily, use_container_width=True)

    with col_right:
        st.markdown('<div class="section-title">Production mensuelle (MWh)</div>', unsafe_allow_html=True)
        fig_month = go.Figure(go.Bar(
            x=monthly["month_name"],
            y=monthly["production_kwh"] / 1000,
            marker_color="#F5A623",
            text=(monthly["production_kwh"] / 1000).round(1).astype(str),
            textposition="outside",
            textfont=dict(color="#E8EDF5", size=10, family="Space Mono"),
        ))
        layout2 = dict(**PLOT_LAYOUT)
        layout2["height"] = 320
        layout2["yaxis"] = dict(gridcolor="#1E232D", title="MWh", zeroline=False)
        fig_month.update_layout(**layout2)
        st.plotly_chart(fig_month, use_container_width=True)

    st.markdown('<div class="section-title">Alertes systeme</div>', unsafe_allow_html=True)
    low_pr_days = daily[daily["pr"] < 70]
    alerts_col1, alerts_col2 = st.columns([2, 1])

    with alerts_col1:
        if len(low_pr_days) > 0:
            st.markdown(f"""
            <div class="alert-card alert-warning">
                <b>{len(low_pr_days)} jours</b> avec Performance Ratio inferieur a 70% —
                Dernier : {low_pr_days["date"].max().strftime('%d/%m/%Y')}
            </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div class="alert-card alert-warning">
            <b>Onduleur #7</b> — Puissance reduite de 12% (depuis 3 jours)
        </div>
        <div class="alert-card alert-ok">
            <b>21 onduleurs</b> — Fonctionnement nominal
        </div>
        <div class="alert-card alert-ok">
            <b>Systeme de monitoring</b> — Toutes les donnees recues
        </div>
        """, unsafe_allow_html=True)

    with alerts_col2:
        st.markdown("**Statut onduleurs**")
        fig_inv = go.Figure(go.Pie(
            values=[21, 1], labels=["Nominaux", "Alerte"],
            hole=0.65,
            marker_colors=["#2ECC71", "#F5A623"],
            textinfo="none",
        ))
        fig_inv.add_annotation(
            text=f"<b>22</b><br>Total",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="#E8EDF5", family="Space Mono"),
        )
        fig_inv.update_layout(
            template="plotly_dark", paper_bgcolor="#111318",
            height=200, margin=dict(t=10, b=10, l=10, r=10),
            showlegend=True,
            legend=dict(font=dict(size=11, color="#6B7585")),
        )
        st.plotly_chart(fig_inv, use_container_width=True)


# ─────────────────────────────────────────────
# PRODUCTION DETAILLEE
# ─────────────────────────────────────────────
elif menu == "Production":
    st.markdown("## Analyse de production")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-title">Performance Ratio journalier (%)</div>', unsafe_allow_html=True)
        fig_pr = go.Figure()
        fig_pr.add_trace(go.Scatter(
            x=daily["date"], y=daily["pr"],
            fill="tozeroy", fillcolor="rgba(245,166,35,0.10)",
            line=dict(color="#F5A623", width=1.5), name="PR %",
        ))
        fig_pr.add_hline(y=75, line_dash="dash", line_color="#3D4553",
                         annotation_text="Seuil 75%",
                         annotation_font_color="#6B7585",
                         annotation_font_size=11)
        layout3 = dict(**PLOT_LAYOUT)
        layout3["height"] = 300
        layout3["yaxis"] = dict(gridcolor="#1E232D", range=[0, 110], zeroline=False)
        fig_pr.update_layout(**layout3)
        st.plotly_chart(fig_pr, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Correlation Temperature / Production</div>', unsafe_allow_html=True)
        fig_corr = px.scatter(
            daily, x="avg_temp", y="production_kwh",
            color="pr", color_continuous_scale="YlOrRd",
            opacity=0.7,
            labels={"avg_temp": "Temp moy (C)", "production_kwh": "Production (kWh)", "pr": "PR %"},
        )
        fig_corr.update_layout(
            template="plotly_dark", paper_bgcolor="#111318", plot_bgcolor="#111318",
            height=300, margin=dict(t=20, b=30, l=50, r=20),
        )
        st.plotly_chart(fig_corr, use_container_width=True)

    st.markdown('<div class="section-title">Profil horaire moyen de production (kW)</div>', unsafe_allow_html=True)
    hourly_avg = results.groupby("hour")["ac_power_kw"].mean().reset_index()
    hourly_avg.columns = ["hour", "avg_power_kw"]
    fig_hour = go.Figure()
    fig_hour.add_trace(go.Scatter(
        x=hourly_avg["hour"], y=hourly_avg["avg_power_kw"],
        fill="tozeroy", fillcolor="rgba(245,166,35,0.15)",
        line=dict(color="#F5A623", width=2), mode="lines",
    ))
    layout4 = dict(**PLOT_LAYOUT)
    layout4["height"] = 280
    layout4["xaxis"] = dict(title="Heure", gridcolor="#1E232D", dtick=1, zeroline=False)
    layout4["yaxis"] = dict(title="Puissance (kW)", gridcolor="#1E232D", zeroline=False)
    fig_hour.update_layout(**layout4)
    st.plotly_chart(fig_hour, use_container_width=True)

    st.markdown('<div class="section-title">Heatmap production (Mois x Heure, kW moyen)</div>', unsafe_allow_html=True)
    heatmap_data = results.groupby(["month", "hour"])["ac_power_kw"].mean().reset_index()
    heatmap_pivot = heatmap_data.pivot(index="month", columns="hour", values="ac_power_kw")
    months_fr = ["Jan", "Fev", "Mar", "Avr", "Mai", "Jun", "Jul", "Aou", "Sep", "Oct", "Nov", "Dec"]
    heatmap_pivot.index = [months_fr[m - 1] for m in heatmap_pivot.index]
    fig_heat = go.Figure(go.Heatmap(
        z=heatmap_pivot.values,
        x=[f"{h}h" for h in heatmap_pivot.columns],
        y=heatmap_pivot.index,
        colorscale=[[0, "#08090C"], [0.3, "#2A1500"], [0.6, "#A05A00"], [1, "#F5A623"]],
        showscale=True,
        colorbar=dict(title="kW", tickfont=dict(color="#6B7585")),
    ))
    layout5 = dict(**PLOT_LAYOUT)
    layout5["height"] = 300
    layout5["xaxis"] = dict(title="Heure", tickfont=dict(size=10), gridcolor="#1E232D")
    layout5["yaxis"] = dict(tickfont=dict(size=10), gridcolor="#1E232D")
    fig_heat.update_layout(**layout5)
    st.plotly_chart(fig_heat, use_container_width=True)


# ─────────────────────────────────────────────
# METEO & IRRADIANCE
# ─────────────────────────────────────────────
elif menu == "Meteo & Irradiance":
    st.markdown("## Meteo & Irradiance — Mohammedia")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Temperature", f"{current_meteo.get('temperature_2m', '--')} C")
    m2.metric("Humidite", f"{current_meteo.get('relative_humidity_2m', '--')} %")
    m3.metric("Vent", f"{current_meteo.get('wind_speed_10m', '--')} km/h")
    m4.metric("Irradiance GHI", f"{current_meteo.get('shortwave_radiation', '--')} W/m2")

    daily_ghi = results.groupby("date").agg(ghi_sum=("ghi", lambda x: x.sum() / 1000)).reset_index()
    daily_ghi["date"] = pd.to_datetime(daily_ghi["date"])

    st.markdown('<div class="section-title">Irradiance globale horizontale (kWh/m2/jour)</div>', unsafe_allow_html=True)
    fig_ghi = go.Figure()
    fig_ghi.add_trace(go.Scatter(
        x=daily_ghi["date"], y=daily_ghi["ghi_sum"],
        fill="tozeroy", fillcolor="rgba(245,166,35,0.12)",
        line=dict(color="#F5A623", width=1.5),
    ))
    layout6 = dict(**PLOT_LAYOUT)
    layout6["height"] = 280
    layout6["yaxis"] = dict(gridcolor="#1E232D", title="kWh/m2", zeroline=False)
    fig_ghi.update_layout(**layout6)
    st.plotly_chart(fig_ghi, use_container_width=True)

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown('<div class="section-title">Temperature journaliere moyenne (C)</div>', unsafe_allow_html=True)
        daily_temp = results.groupby("date").agg(temp_avg=("temp_air", "mean")).reset_index()
        daily_temp["date"] = pd.to_datetime(daily_temp["date"])
        fig_temp = go.Figure(go.Scatter(
            x=daily_temp["date"], y=daily_temp["temp_avg"],
            line=dict(color="#3498DB", width=1.5),
        ))
        fig_temp.add_hline(y=daily_temp["temp_avg"].mean(),
                           line_dash="dash", line_color="#F5A623",
                           annotation_text=f"Moy: {daily_temp['temp_avg'].mean():.1f} C",
                           annotation_font_color="#F5A623")
        layout7 = dict(**PLOT_LAYOUT)
        layout7["height"] = 250
        fig_temp.update_layout(**layout7)
        st.plotly_chart(fig_temp, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-title">Distribution GHI mensuel (kWh/m2)</div>', unsafe_allow_html=True)
        monthly_ghi = daily_ghi.copy()
        monthly_ghi["month"] = monthly_ghi["date"].dt.strftime("%b")
        monthly_ghi_agg = monthly_ghi.groupby("month")["ghi_sum"].sum().reset_index()
        fig_mghi = go.Figure(go.Bar(
            x=monthly_ghi_agg["month"], y=monthly_ghi_agg["ghi_sum"],
            marker_color="#F5A623",
        ))
        layout8 = dict(**PLOT_LAYOUT)
        layout8["height"] = 250
        layout8["yaxis"] = dict(gridcolor="#1E232D", title="kWh/m2", zeroline=False)
        fig_mghi.update_layout(**layout8)
        st.plotly_chart(fig_mghi, use_container_width=True)


# ─────────────────────────────────────────────
# ONDULEURS
# ─────────────────────────────────────────────
elif menu == "Onduleurs":
    st.markdown("## Tableau de bord Onduleurs")

    n = SITE["num_inverters"]
    np.random.seed(42)
    inv_power = np.random.normal(95, 8, n).clip(60, 105)
    inv_status = ["ALERTE" if p < 85 else "OK" for p in inv_power]
    inv_labels = [f"INV-{i+1:02d}" for i in range(n)]

    st.markdown('<div class="section-title">Etat des onduleurs</div>', unsafe_allow_html=True)
    inv_cols = st.columns(6)
    for i in range(n):
        with inv_cols[i % 6]:
            color = "#F5A623" if inv_power[i] < 85 else "#2ECC71"
            status_txt = inv_status[i]
            st.markdown(f"""
            <div style="background:#111318;border:1px solid #252A35;border-radius:8px;
                        padding:12px 10px;text-align:center;margin-bottom:8px;border-left:3px solid {color}">
                <div style="font-size:10px;color:#6B7585;font-family:'Space Mono',monospace;letter-spacing:0.08em">{inv_labels[i]}</div>
                <div style="font-size:20px;font-weight:700;color:{color};font-family:'Space Mono',monospace;margin:4px 0">{inv_power[i]:.0f}%</div>
                <div style="font-size:10px;color:{color};font-family:'Space Mono',monospace">{status_txt}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-title">Puissance relative par onduleur (%)</div>', unsafe_allow_html=True)
        fig_inv_bar = go.Figure(go.Bar(
            x=inv_labels, y=inv_power,
            marker_color=["#F5A623" if p < 85 else "#2ECC71" for p in inv_power],
        ))
        fig_inv_bar.add_hline(y=85, line_dash="dash", line_color="#E74C3C",
                              annotation_text="Seuil alerte 85%",
                              annotation_font_color="#E74C3C",
                              annotation_font_size=11)
        layout9 = dict(**PLOT_LAYOUT)
        layout9["height"] = 300
        layout9["margin"] = dict(t=20, b=50, l=50, r=20)
        layout9["xaxis"] = dict(tickangle=-45, tickfont=dict(size=9), gridcolor="#1E232D")
        layout9["yaxis"] = dict(gridcolor="#1E232D", range=[50, 110], zeroline=False)
        fig_inv_bar.update_layout(**layout9)
        st.plotly_chart(fig_inv_bar, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Repartition statut onduleurs</div>', unsafe_allow_html=True)
        ok_count = sum(1 for p in inv_power if p >= 85)
        warn_count = n - ok_count
        fig_pie = go.Figure(go.Pie(
            labels=["Nominaux", "En alerte"],
            values=[ok_count, warn_count],
            hole=0.6,
            marker_colors=["#2ECC71", "#F5A623"],
        ))
        fig_pie.add_annotation(
            text=f"<b>{n}</b><br>Total",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="#E8EDF5", family="Space Mono"),
        )
        fig_pie.update_layout(
            template="plotly_dark", paper_bgcolor="#111318",
            height=300, margin=dict(t=20, b=20, l=20, r=20),
        )
        st.plotly_chart(fig_pie, use_container_width=True)


# ─────────────────────────────────────────────
# PAGE INSTALLATION (NOUVELLE PAGE)
# ─────────────────────────────────────────────
elif menu == "Installation":

    st.markdown("## Caracteristiques de l'installation")

    # ── KPIs installation ──────────────────────────────
    ki1, ki2, ki3, ki4 = st.columns(4)
    ki1.metric("Puissance crete", f"{SITE['capacity_kwp']} kWp")
    ki2.metric("Nombre de panneaux", f"{SITE['num_panels']}")
    ki3.metric("Nombre d'onduleurs", f"{SITE['num_inverters']}")
    ki4.metric("Surface panneau", f"{SITE['surface_m2']} m2")

    st.markdown("---")

    col_a, col_b = st.columns(2)

    # ── Site & generale ───────────────────────────────
    with col_a:
        st.markdown("""
        <div class="spec-block">
            <div class="spec-block-header">Site & Generale</div>
            <table class="spec-table">
                <tr><td>Designation</td><td>Centrale PV Mohammedia</td></tr>
                <tr><td>Localisation</td><td>Mohammedia, Maroc</td></tr>
                <tr><td>Latitude</td><td><span class="highlight-value">33.6861 N</span></td></tr>
                <tr><td>Longitude</td><td><span class="highlight-value">7.3833 W</span></td></tr>
                <tr><td>Altitude</td><td>15 m</td></tr>
                <tr><td>Fuseau horaire</td><td>Africa/Casablanca (UTC+1)</td></tr>
                <tr><td>Mise en service</td><td>01/04/2023</td></tr>
                <tr><td>Operateur</td><td>SOLARIS Digital Twin</td></tr>
                <tr><td>Raccordement reseau</td><td>HTB 60 kV</td></tr>
                <tr><td>Transformateur</td><td>630 kVA</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

        # ── Structure & montage ───────────────────────
        st.markdown("""
        <div class="spec-block">
            <div class="spec-block-header">Structure & Montage</div>
            <table class="spec-table">
                <tr><td>Type de structure</td><td>Fixe inclinee</td></tr>
                <tr><td>Materiau</td><td>Aluminium anodise</td></tr>
                <tr><td>Inclinaison</td><td><span class="highlight-value">30</span></td></tr>
                <tr><td>Azimut</td><td><span class="highlight-value">180 (plein Sud)</span></td></tr>
                <tr><td>Fondations</td><td>Vis de sol (ground screw)</td></tr>
                <tr><td>Nombre de rangees</td><td>50</td></tr>
                <tr><td>Panneaux par rangee</td><td>25</td></tr>
                <tr><td>Charge vent max</td><td>40 m/s</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    # ── Panneau PV & onduleur ─────────────────────────
    with col_b:
        st.markdown(f"""
        <div class="spec-block">
            <div class="spec-block-header">Panneau Photovoltaique</div>
            <table class="spec-table">
                <tr><td>Fabricant</td><td>{PANEL['manufacturer']}</td></tr>
                <tr><td>Modele</td><td>{PANEL['model']}</td></tr>
                <tr><td>Technologie</td><td><span class="badge-blue">{PANEL['technology']}</span></td></tr>
                <tr><td>Puissance nominale (Pmax)</td><td><span class="highlight-value">{PANEL['pdc0']} Wc</span></td></tr>
                <tr><td>Tension circuit ouvert (Voc)</td><td>{PANEL['voc']} V</td></tr>
                <tr><td>Courant court-circuit (Isc)</td><td>{PANEL['isc']} A</td></tr>
                <tr><td>Tension puissance max (Vmp)</td><td>{PANEL['vmp']} V</td></tr>
                <tr><td>Courant puissance max (Imp)</td><td>{PANEL['imp']} A</td></tr>
                <tr><td>Rendement (STC)</td><td><span class="highlight-value">{PANEL['efficiency_pct']} %</span></td></tr>
                <tr><td>Coeff. temp. puissance</td><td>{PANEL['gamma_pdc']*100:.2f} %/C</td></tr>
                <tr><td>Garantie produit</td><td>{PANEL['warranty_years']} ans</td></tr>
                <tr><td>Degradation annuelle</td><td>{PANEL['degradation_pct_yr']} %/an</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="spec-block">
            <div class="spec-block-header">Onduleur (x{SITE['num_inverters']})</div>
            <table class="spec-table">
                <tr><td>Fabricant</td><td>{INVERTER['manufacturer']}</td></tr>
                <tr><td>Modele</td><td>{INVERTER['model']}</td></tr>
                <tr><td>Puissance unitaire</td><td><span class="highlight-value">{INVERTER['power_kva']} kVA</span></td></tr>
                <tr><td>Rendement europeen</td><td><span class="highlight-value">{INVERTER['efficiency_pct']} %</span></td></tr>
                <tr><td>Canaux MPPT</td><td>{INVERTER['mppt_channels']}</td></tr>
                <tr><td>Tension DC max</td><td>{INVERTER['voltage_dc_max']} V</td></tr>
                <tr><td>Protection IP</td><td><span class="badge-green">{INVERTER['ip_class']}</span></td></tr>
                <tr><td>Puissance totale</td><td><span class="highlight-value">{SITE['num_inverters'] * INVERTER['power_kva']} kVA</span></td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Parametres de simulation pvlib ─────────────────
    st.markdown('<div class="section-title">Parametres du modele pvlib</div>', unsafe_allow_html=True)

    col_m1, col_m2, col_m3 = st.columns(3)

    with col_m1:
        st.markdown("""
        <div class="spec-block">
            <div class="spec-block-header">Modele irradiance</div>
            <table class="spec-table">
                <tr><td>Transposition</td><td>Isotropic Sky</td></tr>
                <tr><td>Composantes</td><td>GHI / DNI / DHI</td></tr>
                <tr><td>Source donnees</td><td>Open-Meteo Archive</td></tr>
                <tr><td>Resolution temporelle</td><td>1 heure</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    with col_m2:
        st.markdown("""
        <div class="spec-block">
            <div class="spec-block-header">Modele thermique</div>
            <table class="spec-table">
                <tr><td>Modele</td><td>SAPM (Sandia)</td></tr>
                <tr><td>Configuration</td><td>Open rack / Glass-Glass</td></tr>
                <tr><td>Parametre a</td><td>-3.56</td></tr>
                <tr><td>Parametre b</td><td>-0.0750</td></tr>
                <tr><td>Delta T</td><td>3 C</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    with col_m3:
        st.markdown("""
        <div class="spec-block">
            <div class="spec-block-header">Modele electrique</div>
            <table class="spec-table">
                <tr><td>Modele DC</td><td>PVWatts</td></tr>
                <tr><td>Rendement onduleur</td><td>97 %</td></tr>
                <tr><td>Pertes cabrage</td><td>2 %</td></tr>
                <tr><td>Disponibilite</td><td>98 %</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    # ── Diagramme unifilaire schematique ─────────────
    st.markdown('<div class="section-title">Schema unifilaire simplifie</div>', unsafe_allow_html=True)

    total_kwh_i = daily["production_kwh"].sum()
    avg_pr_i = daily["pr"].mean()
    specific_yield = total_kwh_i / SITE["capacity_kwp"]

    fig_schema = go.Figure()

    nodes_x = [0.05, 0.28, 0.52, 0.75, 0.95]
    nodes_y = [0.5,  0.5,  0.5,  0.5,  0.5]
    labels = [
        f"1250 Panneaux\n{SITE['capacity_kwp']} kWp",
        f"22 Onduleurs\nSMA 50 kVA",
        f"Transformateur\n630 kVA",
        f"Compteur\nHTB 60 kV",
        f"Reseau\nNational",
    ]
    colors_nodes = ["#F5A623", "#3498DB", "#9B59B6", "#2ECC71", "#E74C3C"]

    for i in range(len(nodes_x) - 1):
        fig_schema.add_shape(
            type="line",
            x0=nodes_x[i] + 0.06, y0=nodes_y[i],
            x1=nodes_x[i+1] - 0.06, y1=nodes_y[i+1],
            line=dict(color="#353C4A", width=2, dash="solid"),
        )

    for i, (x, y, label, color) in enumerate(zip(nodes_x, nodes_y, labels, colors_nodes)):
        fig_schema.add_shape(
            type="rect",
            x0=x - 0.055, y0=y - 0.18,
            x1=x + 0.055, y1=y + 0.18,
            fillcolor="#111318",
            line=dict(color=color, width=1.5),
        )
        fig_schema.add_annotation(
            x=x, y=y, text=label.replace("\n", "<br>"),
            showarrow=False,
            font=dict(size=11, color=color, family="DM Sans"),
            align="center",
        )

    fig_schema.update_layout(
        template="plotly_dark",
        paper_bgcolor="#111318",
        plot_bgcolor="#111318",
        height=200,
        margin=dict(t=10, b=10, l=10, r=10),
        xaxis=dict(visible=False, range=[-0.02, 1.02]),
        yaxis=dict(visible=False, range=[0.1, 0.9]),
        showlegend=False,
    )
    st.plotly_chart(fig_schema, use_container_width=True)

    # ── Indicateurs de performance de conception ───────
    st.markdown('<div class="section-title">Indicateurs de performance de conception</div>', unsafe_allow_html=True)
    kp1, kp2, kp3, kp4, kp5 = st.columns(5)

    kp1.metric("Production specifique", f"{specific_yield:.0f} kWh/kWp")
    kp2.metric("PR moyen annuel", f"{avg_pr_i:.1f} %")
    kp3.metric("Degradation 25 ans", f"-{PANEL['degradation_pct_yr'] * 25:.0f} %")
    kp4.metric("Temp. coeff. puissance", f"{PANEL['gamma_pdc']*100:.2f} %/C")
    kp5.metric("Rendement onduleur", f"{INVERTER['efficiency_pct']} %")


# ─────────────────────────────────────────────
# RAPPORT
# ─────────────────────────────────────────────
elif menu == "Rapport":
    st.markdown("## Rapport de Performance")

    total_kwh = daily["production_kwh"].sum()
    avg_pr = daily["pr"].mean()
    best_month = monthly.loc[monthly["production_kwh"].idxmax()]
    worst_month = monthly.loc[monthly["production_kwh"].idxmin()]
    avg_daily = daily["production_kwh"].mean()

    st.markdown(f"""
    <div style="background:#111318;border:1px solid #252A35;border-top:2px solid #F5A623;border-radius:12px;padding:28px">
        <div style="font-family:'Space Mono',monospace;font-size:14px;color:#F5A623;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:4px">
            Rapport de Performance
        </div>
        <div style="font-size:12px;color:#6B7585;margin-bottom:20px;font-family:'Space Mono',monospace">
            {SITE['name']} &nbsp;|&nbsp; {start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')}
        </div>
        <hr style="border-color:#252A35;margin-bottom:20px">

        <div style="font-size:13px;font-weight:600;color:#E8EDF5;margin-bottom:10px;text-transform:uppercase;letter-spacing:0.08em">
            Production
        </div>
        <div class="spec-block" style="margin-bottom:20px">
            <table class="spec-table">
                <tr><td>Production totale</td><td><span class="highlight-value">{total_kwh/1000:.1f} MWh</span></td></tr>
                <tr><td>Production journaliere moyenne</td><td>{avg_daily:.0f} kWh/jour</td></tr>
                <tr><td>Meilleur mois</td><td><span style="color:#2ECC71;font-weight:600">{best_month['month_name']} — {best_month['production_kwh']/1000:.1f} MWh</span></td></tr>
                <tr><td>Mois le plus faible</td><td><span style="color:#E74C3C;font-weight:600">{worst_month['month_name']} — {worst_month['production_kwh']/1000:.1f} MWh</span></td></tr>
            </table>
        </div>

        <div style="font-size:13px;font-weight:600;color:#E8EDF5;margin-bottom:10px;text-transform:uppercase;letter-spacing:0.08em">
            Performance
        </div>
        <div class="spec-block" style="margin-bottom:20px">
            <table class="spec-table">
                <tr><td>Performance Ratio moyen</td><td><span class="highlight-value">{avg_pr:.1f} %</span></td></tr>
                <tr><td>Jours avec PR inferieur a 70%</td><td><span style="color:#E74C3C">{len(daily[daily['pr'] < 70])} jours</span></td></tr>
                <tr><td>Disponibilite onduleurs</td><td><span style="color:#2ECC71">95.5 % (21/22 nominaux)</span></td></tr>
            </table>
        </div>

        <div style="font-size:13px;font-weight:600;color:#E8EDF5;margin-bottom:10px;text-transform:uppercase;letter-spacing:0.08em">
            Ressource solaire
        </div>
        <div class="spec-block">
            <table class="spec-table">
                <tr><td>GHI moyen annuel</td><td><span class="highlight-value">{results['ghi'].mean():.0f} W/m2</span></td></tr>
                <tr><td>Temperature moyenne</td><td>{results['temp_air'].mean():.1f} C</td></tr>
                <tr><td>Localisation</td><td>Mohammedia, Maroc — {SITE['lat']}N, {abs(SITE['lon'])}W</td></tr>
            </table>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Export des donnees")

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        csv_daily = daily.to_csv(index=False, float_format="%.2f")
        st.download_button(
            "Telecharger resultats journaliers (CSV)",
            csv_daily,
            file_name=f"solaris_mohammedia_daily_{start_date}_{end_date}.csv",
            mime="text/csv",
        )
    with col_d2:
        csv_monthly = monthly.to_csv(index=False, float_format="%.2f")
        st.download_button(
            "Telecharger resultats mensuels (CSV)",
            csv_monthly,
            file_name=f"solaris_mohammedia_monthly_{start_date}_{end_date}.csv",
            mime="text/csv",
        )


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(f"""
<div style="text-align:center;color:#252A35;font-size:11px;padding:10px 0;font-family:'Space Mono',monospace;letter-spacing:0.08em">
    SOLARIS DIGITAL TWIN &nbsp;|&nbsp; MOHAMMEDIA, MAROC &nbsp;|&nbsp; pvlib + Open-Meteo API
    &nbsp;|&nbsp; {now.strftime('%d/%m/%Y %H:%M')}
</div>
""", unsafe_allow_html=True)
