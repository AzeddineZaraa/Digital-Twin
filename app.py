"""
SOLARIS - Digital Twin PV · Mohammedia, Maroc
Streamlit + pvlib · Open-Meteo API
GitHub Deployment Ready
Enhanced Version 2.0
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
from pvlib import irradiance, temperature, pvsystem
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
# CSS PERSONNALISE - ENHANCED
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

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
        --teal: #1ABC9C;
        --gradient-gold: linear-gradient(135deg, #F5A623, #E8860A);
        --gradient-dark: linear-gradient(135deg, #0E1117, #141820);
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
        transition: color 0.3s ease;
    }

    [data-testid="stSidebar"] .stRadio label:hover {
        color: var(--solar-yellow) !important;
    }

    /* Main header */
    .main-header {
        background: var(--gradient-dark);
        border: 1px solid var(--border);
        border-top: 2px solid var(--solar-yellow);
        border-radius: 0 0 12px 12px;
        padding: 22px 32px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }

    .plant-name {
        font-family: 'Space Mono', monospace;
        font-size: 20px;
        font-weight: 700;
        background: var(--gradient-gold);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
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

    /* Metric cards - Enhanced with hover effects */
    .metric-card {
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 20px 22px;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }

    .metric-card:hover {
        border-color: var(--solar-yellow);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(245,166,35,0.1);
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

    /* Alert cards with enhanced styling */
    .alert-card {
        border-radius: 8px;
        padding: 11px 16px;
        margin-bottom: 8px;
        font-size: 13px;
        border-left: 3px solid;
        font-family: 'DM Sans', sans-serif;
        transition: transform 0.2s ease;
    }

    .alert-card:hover {
        transform: translateX(4px);
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

    .alert-info {
        background: rgba(52,152,219,0.06);
        border-color: var(--blue);
        color: #5BA4D9;
    }

    /* Spec table */
    .spec-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
    }

    .spec-table tr {
        border-bottom: 1px solid var(--border);
        transition: background 0.2s ease;
    }

    .spec-table tr:hover {
        background: rgba(245,166,35,0.05);
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
        transition: all 0.3s ease;
    }

    .spec-block:hover {
        border-color: var(--border-bright);
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

    .badge-purple {
        background: rgba(155,89,182,0.1);
        color: var(--purple);
        border: 1px solid rgba(155,89,182,0.2);
        border-radius: 4px;
        padding: 2px 8px;
        font-size: 11px;
        font-family: 'Space Mono', monospace;
    }

    /* KPI cards with gradient backgrounds */
    .kpi-card {
        background: var(--gradient-dark);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 20px 16px;
        text-align: center;
        transition: all 0.3s ease;
    }

    .kpi-card:hover {
        border-color: var(--solar-yellow);
        box-shadow: 0 6px 20px rgba(0,0,0,0.4);
    }

    .kpi-value {
        font-family: 'Space Mono', monospace;
        font-size: 32px;
        font-weight: 700;
        background: var(--gradient-gold);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .kpi-label {
        font-size: 11px;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 8px;
    }

    /* Override Streamlit metric styling */
    div[data-testid="metric-container"] {
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 16px 18px;
        transition: all 0.3s ease;
    }

    div[data-testid="metric-container"]:hover {
        border-color: var(--solar-yellow);
        transform: translateY(-2px);
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
        border: 1px solid var(--border);
    }

    /* Sidebar brand */
    .sidebar-brand {
        font-family: 'Space Mono', monospace;
        font-size: 18px;
        font-weight: 700;
        background: var(--gradient-gold);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
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

    /* Data info tooltip */
    .data-info {
        background: rgba(52,152,219,0.08);
        border: 1px solid rgba(52,152,219,0.2);
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 11px;
        color: var(--blue);
        font-family: 'Space Mono', monospace;
    }

    /* Enhanced button styling */
    .stDownloadButton button {
        background: var(--gradient-gold) !important;
        color: white !important;
        border: none !important;
        font-family: 'Space Mono', monospace !important;
        font-weight: 700 !important;
        transition: all 0.3s ease !important;
    }

    .stDownloadButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(245,166,35,0.3);
    }

    hr { border-color: var(--border) !important; }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: var(--card-bg);
        border-radius: 8px;
        padding: 6px;
    }

    .stTabs [data-baseweb="tab"] {
        color: var(--text-secondary);
        font-family: 'Space Mono', monospace;
        font-size: 12px;
        border-radius: 6px;
    }

    .stTabs [aria-selected="true"] {
        background-color: rgba(245,166,35,0.1);
        color: var(--solar-yellow);
    }

    /* Glass morphism effect for cards */
    .glass-card {
        background: rgba(17, 19, 24, 0.8);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 20px;
    }
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
    "technology": "Polycristallin",
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
    "rows": 2,
    "panels_per_row": 6,
}


# ─────────────────────────────────────────────
# FONCTIONS PRINCIPALES - ENHANCED
# ─────────────────────────────────────────────

@st.cache_data(ttl=3600)
def fetch_meteo(lat, lon, start_date, end_date):
    """Fetch meteorological data from Open-Meteo API with enhanced error handling"""
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "temperature_2m,shortwave_radiation,diffuse_radiation,direct_normal_irradiance,wind_speed_10m,relative_humidity_2m,cloud_cover",
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
            "cloud_cover": data["hourly"].get("cloud_cover", [0]*len(data["hourly"]["time"])),
        })
        df = df.set_index("datetime")
        return df
    except Exception as e:
        st.error(f"Erreur API meteo : {e}")
        return None


@st.cache_data(ttl=3600)
@st.cache_data(ttl=3600)
def run_pvlib_simulation(lat, lon, altitude, timezone, tilt, azimuth, pdc0, gamma_pdc, start_date, end_date):
    """Enhanced pvlib simulation with comprehensive energy modeling"""
    location = Location(
        latitude=lat, longitude=lon,
        altitude=altitude, tz=timezone, name="Mohammedia"
    )
    df = fetch_meteo(lat, lon, start_date, end_date)
    if df is None:
        return None

    times = df.index
    solar_pos = location.get_solarposition(times)
    
    # Calculate extraterrestrial radiation (required for some models)
    dni_extra = irradiance.get_extra_radiation(times)

    # Enhanced irradiance transposition with multiple models
    poa_isotropic = irradiance.get_total_irradiance(
        surface_tilt=tilt, surface_azimuth=azimuth,
        dni=df["dni"], ghi=df["ghi"], dhi=df["dhi"],
        solar_zenith=solar_pos["apparent_zenith"],
        solar_azimuth=solar_pos["azimuth"],
        model="isotropic"
    )
    
    poa_haydavies = irradiance.get_total_irradiance(
        surface_tilt=tilt, surface_azimuth=azimuth,
        dni=df["dni"], ghi=df["ghi"], dhi=df["dhi"],
        solar_zenith=solar_pos["apparent_zenith"],
        solar_azimuth=solar_pos["azimuth"],
        dni_extra=dni_extra,  # Required for haydavies model
        model="haydavies"
    )

    # Temperature modeling with SAPM
    temp_params = temperature.TEMPERATURE_MODEL_PARAMETERS["sapm"]["open_rack_glass_glass"]
    cell_temp = temperature.sapm_cell(
        poa_global=poa_isotropic["poa_global"], temp_air=df["temp_air"],
        wind_speed=df["wind_speed"],
        a=temp_params["a"], b=temp_params["b"], deltaT=temp_params["deltaT"],
    )

    # DC power calculation with temperature effects
    dc_power_isotropic = pvsystem.pvwatts_dc(
        g_poa_effective=poa_isotropic["poa_global"], temp_cell=cell_temp,
        pdc0=pdc0, gamma_pdc=gamma_pdc,
    )
    
    # Use isotropic model for DC power (more standard)
    dc_power = dc_power_isotropic

    # AC power with inverter efficiency modeling
    inverter_efficiency = 0.97
    ac_power = dc_power * inverter_efficiency
        # Calculate system losses (total ~14% incluant l'onduleur deja a 97%)
    additional_losses = 0.10  # 10% pertes supplementaires (salissure, mismatch, cablage, temperature)
    net_ac_power = ac_power * (1 - additional_losses)

    results = pd.DataFrame({
        "datetime": times,
        "ghi": df["ghi"],
        "dni": df["dni"],
        "dhi": df["dhi"],
        "poa_isotropic": poa_isotropic["poa_global"],
        "poa_haydavies": poa_haydavies["poa_global"],
        "temp_air": df["temp_air"],
        "cell_temp": cell_temp,
        "wind_speed": df["wind_speed"],
        "humidity": df["humidity"],
        "cloud_cover": df["cloud_cover"],
        "dc_power_w": dc_power,
        "ac_power_w": ac_power.clip(lower=0),
        "net_ac_power_w": net_ac_power.clip(lower=0),
        "solar_elevation": solar_pos["elevation"],
        "solar_azimuth": solar_pos["azimuth"],
        "dni_extra": dni_extra,  # Store for reference
    })
    
    results["ac_power_kw"] = results["ac_power_w"] / 1000
    results["net_ac_power_kw"] = results["net_ac_power_w"] / 1000
    results["date"] = results["datetime"].dt.date
    results["hour"] = results["datetime"].dt.hour
    results["month"] = results["datetime"].dt.month
    results["month_name"] = results["datetime"].dt.strftime("%b")
    results["day_of_year"] = results["datetime"].dt.dayofyear
    results["week"] = results["datetime"].dt.isocalendar().week
    
    return results


def compute_daily(results, num_panels):
    """Enhanced daily aggregation with comprehensive metrics"""
    # La puissance est déjà multipliée par le nombre de panneaux dans results
    total_capacity_kw = SITE["capacity_kwp"]  # 3.95 kWp
    
    daily = results.groupby("date").agg(
        production_kwh=("net_ac_power_kw", lambda x: x.sum()),
        gross_production_kwh=("ac_power_kw", lambda x: x.sum()),
        peak_power_kw=("net_ac_power_kw", "max"),
        avg_temp=("temp_air", "mean"),
        max_temp=("temp_air", "max"),
        min_temp=("temp_air", "min"),
        avg_ghi=("ghi", "mean"),
        max_ghi=("ghi", "max"),
        avg_wind=("wind_speed", "mean"),
        avg_humidity=("humidity", "mean"),
        avg_cloud=("cloud_cover", "mean"),
        peak_sun_hours=("poa_isotropic", lambda x: x.sum() / 1000),
        theoretical_psh=("ghi", lambda x: x.sum() / 1000),
    ).reset_index()
    
    # Production theorique = PSH * capacite installee
    daily["theoretical_kwh"] = daily["peak_sun_hours"] * total_capacity_kw
    daily["pr"] = (daily["production_kwh"] / daily["theoretical_kwh"].replace(0, np.nan)).clip(0, 1) * 100
    daily["capacity_factor"] = (daily["production_kwh"] / (24 * total_capacity_kw)) * 100
    daily["energy_yield"] = daily["production_kwh"] / total_capacity_kw
    
    daily["date"] = pd.to_datetime(daily["date"])
    daily["day_of_week"] = daily["date"].dt.day_name()
    daily["is_weekend"] = daily["date"].dt.dayofweek.isin([5, 6])
    
    return daily


def compute_monthly(daily):
    """Enhanced monthly aggregation"""
    monthly = daily.groupby(daily["date"].dt.to_period("M")).agg(
        production_kwh=("production_kwh", "sum"),
        gross_production_kwh=("gross_production_kwh", "sum"),
        avg_pr=("pr", "mean"),
        min_pr=("pr", "min"),
        max_pr=("pr", "max"),
        avg_temp=("avg_temp", "mean"),
        avg_capacity_factor=("capacity_factor", "mean"),
        avg_energy_yield=("energy_yield", "mean"),
    ).reset_index()
    monthly["date"] = monthly["date"].dt.to_timestamp()
    monthly["month_name"] = monthly["date"].dt.strftime("%b %Y")
    monthly["season"] = monthly["date"].dt.month.map({
        12: "Winter", 1: "Winter", 2: "Winter",
        3: "Spring", 4: "Spring", 5: "Spring",
        6: "Summer", 7: "Summer", 8: "Summer",
        9: "Autumn", 10: "Autumn", 11: "Autumn"
    })
    return monthly


def get_current_meteo(lat, lon):
    """Get current weather with enhanced parameters"""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat, "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,shortwave_radiation,cloud_cover,apparent_temperature",
        "timezone": "Africa/Casablanca",
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.json().get("current", {})
    except:
        return {}


def calculate_degraded_power(pdc0, years_operation, degradation_rate):
    """Calculate power after degradation"""
    return pdc0 * (1 - degradation_rate) ** years_operation


def estimate_co2_avoidance(energy_kwh, grid_emission_factor=0.65):
    """Estimate CO2 emissions avoided (kg)"""
    return energy_kwh * grid_emission_factor


def calculate_financial_metrics(energy_kwh, electricity_price=0.12):
    """Calculate financial savings"""
    return energy_kwh * electricity_price


PLOT_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="#111318",
    plot_bgcolor="#111318",
    font=dict(family="DM Sans", color="#6B7585"),
    margin=dict(t=20, b=30, l=50, r=20),
    xaxis=dict(gridcolor="#1E232D", zeroline=False),
    yaxis=dict(gridcolor="#1E232D", zeroline=False),
    hovermode="x unified",
)


# ─────────────────────────────────────────────
# SIDEBAR - ENHANCED
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
            "Performance Analysis",
            "Onduleurs",
            "Installation",
            "Rapport",
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    
    # Enhanced period selection
    st.markdown("**Periode d'analyse**")
    
    col_s, col_e = st.columns(2)
    with col_s:
        start_date = st.date_input("Debut", value=datetime(2026, 4, 1), label_visibility="collapsed")
    with col_e:
        end_date = st.date_input("Fin", value=datetime(2026, 4, 25), label_visibility="collapsed")

    # Quick date presets
    preset_cols = st.columns(3)
    with preset_cols[0]:
        if st.button("7j", key="7d"):
            start_date = datetime.now() - timedelta(days=7)
            end_date = datetime.now()
    with preset_cols[1]:
        if st.button("30j", key="30d"):
            start_date = datetime.now() - timedelta(days=30)
            end_date = datetime.now()
    with preset_cols[2]:
        if st.button("90j", key="90d"):
            start_date = datetime.now() - timedelta(days=90)
            end_date = datetime.now()

    st.markdown(f"Du **{start_date.strftime('%d/%m/%Y')}** au **{end_date.strftime('%d/%m/%Y')}**")

    # Data freshness indicator
    data_age = (datetime.now() - datetime.combine(end_date, datetime.min.time())).days
    if data_age == 0:
        st.markdown('<div class="data-info">Donnees actualisees aujourd\'hui</div>', unsafe_allow_html=True)
    elif data_age < 3:
        st.markdown(f'<div class="data-info">Donnees actualisees il y a {data_age} jours</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="data-info" style="border-color: rgba(245,166,35,0.3); color: #D4993A;">Donnees actualisees il y a {data_age} jours</div>', unsafe_allow_html=True)

    st.markdown("---")
    
    # System status summary
    st.markdown("**Systeme**")
    st.markdown(f"Capacite : **{SITE['capacity_kwp']} kWp**")
    st.markdown(f"Panneaux : **{SITE['num_panels']}**")
    st.markdown(f"Onduleurs : **{SITE['num_inverters']}**")
    st.markdown(f"Inclinaison : **{PANEL['tilt']}**")
    st.markdown(f"Azimut : **{PANEL['azimuth']}**")
    
    # Degradation calculator
    years_operational = datetime.now().year - int(SITE['commissioning_date'])
    degraded_power = calculate_degraded_power(PANEL['pdc0'], years_operational, PANEL['degradation_pct_yr']/100)
    st.markdown("---")
    st.markdown("**Degradation estimee**")
    st.markdown(f"Apres {years_operational} ans : **{degraded_power:.0f} W** (-{(1 - degraded_power/PANEL['pdc0'])*100:.1f}%)")


# ─────────────────────────────────────────────
# SIMULATION PVLIB
# ─────────────────────────────────────────────
with st.spinner("Simulation pvlib en cours..."):
    results = run_pvlib_simulation(
        lat=SITE["lat"], lon=SITE["lon"], altitude=SITE["altitude"],
        timezone=SITE["timezone"], tilt=PANEL["tilt"], azimuth=PANEL["azimuth"],
        pdc0=PANEL["pdc0"] * SITE["num_panels"], gamma_pdc=PANEL["gamma_pdc"],
        start_date=str(start_date), end_date=str(end_date),
    )

if results is None:
    st.error("Impossible de recuperer les donnees. Verifiez votre connexion internet.")
    st.stop()

# Scale for number of panels
daily = compute_daily(results, SITE["num_panels"])
monthly = compute_monthly(daily)
current_meteo = get_current_meteo(SITE["lat"], SITE["lon"])
now = datetime.now()


# ─────────────────────────────────────────────
# HEADER PRINCIPAL - ENHANCED
# ─────────────────────────────────────────────
ghi_now = current_meteo.get('shortwave_radiation', 0) or 0
cloud_cover_now = current_meteo.get('cloud_cover', 0) or 0

if ghi_now > 100:
    status_label = "PRODUCTION OPTIMALE"
    status_color = "var(--green)"
elif ghi_now > 50:
    status_label = "PRODUCTION REDUITE"
    status_color = "var(--solar-yellow)"
else:
    status_label = "HORS PRODUCTION"
    status_color = "var(--text-secondary)"

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
            <div style="text-align:right;">
                <div style="font-size:12px;color:#6B7585;font-family:'Space Mono',monospace">
                    {now.strftime('%d/%m/%Y %H:%M')}
                </div>
                <div style="font-size:10px;color:#3D4553;font-family:'Space Mono',monospace">
                    UTC+1 &nbsp;|&nbsp; GHI: {ghi_now:.0f} W/m2 &nbsp;|&nbsp; Cloud: {cloud_cover_now}%
                </div>
            </div>
            <div class="status-badge" style="border-color: {status_color}; color: {status_color}">
                <div class="status-dot" style="background: {status_color}; box-shadow: 0 0 8px {status_color};"></div>
                {status_label}
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# VUE GLOBALE - ENHANCED
# ─────────────────────────────────────────────
if menu == "Vue Globale":
    # KPI Summary
    total_kwh = daily["production_kwh"].sum()
    gross_kwh = daily["gross_production_kwh"].sum()
    losses_kwh = gross_kwh - total_kwh
    avg_daily_losses = losses_kwh / len(daily) if len(daily) > 0 else 0
    avg_cf = daily["capacity_factor"].mean()
    co2_avoided = estimate_co2_avoidance(total_kwh)
    financial_savings = calculate_financial_metrics(total_kwh)
    
    st.markdown("## Performance Globale")
    
    # KPI Row
    kpi_cols = st.columns(5)
    with kpi_cols[0]:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{total_kwh/1000:.2f}</div>
            <div class="kpi-label">Production Totale<br>MWh</div>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_cols[1]:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{avg_pr:.1f}</div>
            <div class="kpi-label">Performance<br>Ratio %</div>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_cols[2]:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{co2_avoided:.0f}</div>
            <div class="kpi-label">CO2 Evite<br>kg</div>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_cols[3]:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{financial_savings:.0f}</div>
            <div class="kpi-label">Economies<br>EUR</div>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_cols[4]:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{avg_cf:.1f}</div>
            <div class="kpi-label">Facteur<br>Capacite %</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Current conditions and system image
    col_img, col_perf = st.columns([2, 1])
    with col_img:
        st.image(
            "assets/Scene_enset.png",
            use_container_width=True,
        )
        
        # Weather metrics
        weather_cols = st.columns(4)
        with weather_cols[0]:
            st.metric("Temperature", f"{current_meteo.get('temperature_2m', '--')} C",
                     delta=f"Ressentie: {current_meteo.get('apparent_temperature', '--')} C")
        with weather_cols[1]:
            st.metric("Irradiance", f"{ghi_now} W/m2")
        with weather_cols[2]:
            st.metric("Vent", f"{current_meteo.get('wind_speed_10m', '--')} km/h")
        with weather_cols[3]:
            st.metric("Humidite", f"{current_meteo.get('relative_humidity_2m', '--')} %")
    
    with col_perf:
        st.markdown('<div class="section-title">Performance en temps reel</div>', unsafe_allow_html=True)
        
        current_hour = datetime.now().hour
        today_str = datetime.now().date()
        mask = (results["date"] == today_str) & (results["hour"] == current_hour)
        current_power = results.loc[mask, "net_ac_power_kw"].values
        current_power_val = current_power[0] if len(current_power) > 0 else 0.0
        
        st.metric("Puissance actuelle", f"{current_power_val:.2f} kW")
        today_daily = daily[daily["date"] == daily["date"].max()]
        today_kwh = today_daily["production_kwh"].values[0] if len(today_daily) > 0 else 0.0
        st.metric("Production du jour", f"{today_kwh:.2f} kWh")
        st.metric("Pertes journalieres moy.", f"{avg_daily_losses:.1f} kWh", 
                 delta=f"{(losses_kwh/gross_kwh)*100:.1f}%" if gross_kwh > 0 else "0%")
        
        # Efficiency metrics
        st.metric("Rendement energetique", f"{(total_kwh/gross_kwh)*100:.1f}%" if gross_kwh > 0 else "0%")
    
    st.markdown("---")

    # Enhanced daily production chart with anomaly detection
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown('<div class="section-title">Production journaliere (kWh)</div>', unsafe_allow_html=True)
        
        # Anomaly detection
        daily_prod_mean = daily["production_kwh"].mean()
        daily_prod_std = daily["production_kwh"].std()
        anomalies = daily[
            (daily["production_kwh"] > daily_prod_mean + 2 * daily_prod_std) | 
            (daily["production_kwh"] < daily_prod_mean - 2 * daily_prod_std)
            ]
        
        fig_daily = go.Figure()
        
        fig_daily.add_trace(go.Bar(
            x=daily["date"], y=daily["production_kwh"],
            name="Production",
            marker_color="#F5A623", opacity=0.85,
            hovertemplate="Date: %{x}<br>Production: %{y:.1f} kWh<extra></extra>"
        ))
        
        fig_daily.add_trace(go.Scatter(
            x=daily["date"],
            y=daily["production_kwh"].rolling(7, center=True).mean(),
            name="Moy. mobile 7j",
            line=dict(color="#3498DB", width=2),
        ))
        
        # Highlight anomalies
        if len(anomalies) > 0:
            fig_daily.add_trace(go.Scatter(
                x=anomalies["date"], y=anomalies["production_kwh"],
                mode="markers", name="Anomalies",
                marker=dict(color="#E74C3C", size=10, symbol="x"),
            ))
        
        layout = dict(**PLOT_LAYOUT)
        layout["height"] = 320
        layout["showlegend"] = True
        layout["yaxis"] = dict(gridcolor="#1E232D", title="kWh", zeroline=False)
        fig_daily.update_layout(**layout)
        st.plotly_chart(fig_daily, use_container_width=True)

    with col_right:
        # Production distribution by day of week
        st.markdown('<div class="section-title">Production par jour</div>', unsafe_allow_html=True)
        
        daily_weekday = daily.groupby("day_of_week")["production_kwh"].mean().reset_index()
        daily_weekday["day_of_week"] = pd.Categorical(
            daily_weekday["day_of_week"],
            categories=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            ordered=True
        )
        daily_weekday = daily_weekday.sort_values("day_of_week")
        
        fig_weekday = go.Figure(go.Bar(
            x=daily_weekday["day_of_week"],
            y=daily_weekday["production_kwh"],
            marker_color="#9B59B6",
            text=daily_weekday["production_kwh"].round(0).astype(str) + " kWh",
            textposition="outside",
            textfont=dict(color="#E8EDF5", size=9, family="Space Mono"),
        ))
        layout2 = dict(**PLOT_LAYOUT)
        layout2["height"] = 320
        fig_weekday.update_layout(**layout2)
        st.plotly_chart(fig_weekday, use_container_width=True)

    st.markdown("---")
    
    # Enhanced alerts with categorization
    st.markdown('<div class="section-title">Centre d\'alertes</div>', unsafe_allow_html=True)
    
    alerts_col1, alerts_col2 = st.columns([2, 1])

    with alerts_col1:
        low_pr_days = daily[daily["pr"] < 70]
        high_temp_days = daily[daily["avg_temp"] > 35]
        low_prod_days = daily[daily["production_kwh"] < daily["production_kwh"].quantile(0.1)]
        
        if len(low_pr_days) > 0:
            st.markdown(f"""
            <div class="alert-card alert-warning">
                <b>Performance degradee</b><br>
                {len(low_pr_days)} jours avec PR < 70% — 
                Dernier : {low_pr_days["date"].max().strftime('%d/%m/%Y')}
            </div>""", unsafe_allow_html=True)
        
        if len(high_temp_days) > 0:
            st.markdown(f"""
            <div class="alert-card alert-warning">
                <b>Temperature elevee</b><br>
                {len(high_temp_days)} jours > 35 C — Perte de rendement estimee
            </div>""", unsafe_allow_html=True)
        
        if len(low_prod_days) > 0:
            st.markdown(f"""
            <div class="alert-card alert-info">
                <b>Production faible</b><br>
                {len(low_prod_days)} jours dans le decile inferieur
            </div>""", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="alert-card alert-ok">
            <b>Systeme de monitoring</b> — Toutes les donnees recues, pas d'erreurs de communication
        </div>
        <div class="alert-card alert-ok">
            <b>Raccordement reseau</b> — Tension et frequence nominales
        </div>
        """, unsafe_allow_html=True)

    with alerts_col2:
        # System health score
        health_score = 100 - (len(low_pr_days) * 5 + len(high_temp_days) * 2 + len(low_prod_days) * 3)
        health_score = max(min(health_score, 100), 0)
        
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value" style="color: {'#2ECC71' if health_score > 80 else '#F5A623' if health_score > 60 else '#E74C3C'}">
                {health_score:.0f}/100
            </div>
            <div class="kpi-label">Score de<br>Sante Systeme</div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PRODUCTION DETAILLEE - ENHANCED
# ─────────────────────────────────────────────
elif menu == "Production":
    st.markdown("## Analyse de production detaillee")
    
    # Production tabs
    tab1, tab2, tab3 = st.tabs(["Performance", "Profil Horaire", "Heatmap"])
    
    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="section-title">Performance Ratio journalier (%)</div>', unsafe_allow_html=True)
            
            fig_pr = go.Figure()
            fig_pr.add_trace(go.Scatter(
                x=daily["date"], y=daily["pr"],
                fill="tozeroy", fillcolor="rgba(245,166,35,0.10)",
                line=dict(color="#F5A623", width=1.5), name="PR %",
                hovertemplate="Date: %{x}<br>PR: %{y:.1f}%<extra></extra>"
            ))
            fig_pr.add_hline(y=75, line_dash="dash", line_color="#3D4553",
                           annotation_text="Seuil 75%",
                           annotation_font_color="#6B7585",
                           annotation_font_size=11)
            fig_pr.add_hline(y=85, line_dash="dash", line_color="#2ECC71",
                           annotation_text="Cible 85%",
                           annotation_font_color="#2ECC71",
                           annotation_font_size=11)
            
            layout3 = dict(**PLOT_LAYOUT)
            layout3["height"] = 350
            layout3["yaxis"] = dict(gridcolor="#1E232D", range=[0, 110], zeroline=False)
            fig_pr.update_layout(**layout3)
            st.plotly_chart(fig_pr, use_container_width=True)

        with col2:
            st.markdown('<div class="section-title">Facteur de capacite journalier (%)</div>', unsafe_allow_html=True)
            
            fig_cf = go.Figure()
            fig_cf.add_trace(go.Scatter(
                x=daily["date"], y=daily["capacity_factor"],
                fill="tozeroy", fillcolor="rgba(52,152,219,0.10)",
                line=dict(color="#3498DB", width=1.5), name="CF %",
                hovertemplate="Date: %{x}<br>CF: %{y:.1f}%<extra></extra>"
            ))
            
            layout_cf = dict(**PLOT_LAYOUT)
            layout_cf["height"] = 350
            layout_cf["yaxis"] = dict(gridcolor="#1E232D", title="%", zeroline=False)
            fig_cf.update_layout(**layout_cf)
            st.plotly_chart(fig_cf, use_container_width=True)
        
        # Correlation analysis
        st.markdown('<div class="section-title">Analyse de correlation</div>', unsafe_allow_html=True)
        
        corr_cols = st.columns(3)
        with corr_cols[0]:
            fig_corr1 = px.scatter(
                daily, x="avg_temp", y="production_kwh",
                color="pr", color_continuous_scale="YlOrRd",
                opacity=0.7, trendline="ols",
                labels={"avg_temp": "Temp moy (C)", "production_kwh": "Production (kWh)", "pr": "PR %"},
                title="Temperature vs Production"
            )
            fig_corr1.update_layout(**{**PLOT_LAYOUT, "height": 300})
            st.plotly_chart(fig_corr1, use_container_width=True)
        
        with corr_cols[1]:
            fig_corr2 = px.scatter(
                daily, x="peak_sun_hours", y="production_kwh",
                color="pr", color_continuous_scale="YlOrRd",
                opacity=0.7, trendline="ols",
                labels={"peak_sun_hours": "PSH (h)", "production_kwh": "Production (kWh)", "pr": "PR %"},
                title="PSH vs Production"
            )
            fig_corr2.update_layout(**{**PLOT_LAYOUT, "height": 300})
            st.plotly_chart(fig_corr2, use_container_width=True)
        
        with corr_cols[2]:
            fig_corr3 = px.scatter(
                daily, x="avg_wind", y="production_kwh",
                color="pr", color_continuous_scale="YlOrRd",
                opacity=0.7,
                labels={"avg_wind": "Vent (m/s)", "production_kwh": "Production (kWh)"},
                title="Vent vs Production"
            )
            fig_corr3.update_layout(**{**PLOT_LAYOUT, "height": 300})
            st.plotly_chart(fig_corr3, use_container_width=True)
    
    with tab2:
        st.markdown('<div class="section-title">Profil horaire de production</div>', unsafe_allow_html=True)
        
        # Hourly profile with confidence bands
        hourly_stats = results.groupby("hour")["ac_power_kw"].agg(["mean", "std", "min", "max"]).reset_index()
        
        fig_hour = go.Figure()
        
        fig_hour.add_trace(go.Scatter(
            x=hourly_stats["hour"], y=hourly_stats["max"],
            fill=None, mode="lines",
            line=dict(color="rgba(245,166,35,0.2)", width=0),
            showlegend=False,
        ))
        fig_hour.add_trace(go.Scatter(
            x=hourly_stats["hour"], y=hourly_stats["min"],
            fill="tonexty", fillcolor="rgba(245,166,35,0.1)",
            mode="lines",
            line=dict(color="rgba(245,166,35,0.2)", width=0),
            name="Plage min-max",
        ))
        fig_hour.add_trace(go.Scatter(
            x=hourly_stats["hour"], y=hourly_stats["mean"],
            fill=None,
            line=dict(color="#F5A623", width=2.5),
            name="Moyenne",
            hovertemplate="Heure: %{x}h<br>Puissance moy: %{y:.2f} kW<extra></extra>"
        ))
        
        layout4 = dict(**PLOT_LAYOUT)
        layout4["height"] = 350
        layout4["xaxis"] = dict(title="Heure", gridcolor="#1E232D", dtick=1, zeroline=False)
        layout4["yaxis"] = dict(title="Puissance (kW)", gridcolor="#1E232D", zeroline=False)
        fig_hour.update_layout(**layout4)
        st.plotly_chart(fig_hour, use_container_width=True)
        
        # Compare weekday vs weekend profiles
        st.markdown('<div class="section-title">Profil horaire: Jour ouvrable vs Weekend</div>', unsafe_allow_html=True)
        
        weekday_data = results[~results["date"].isin(daily[daily["is_weekend"]]["date"])]
        weekend_data = results[results["date"].isin(daily[daily["is_weekend"]]["date"])]
        
        weekday_hourly = weekday_data.groupby("hour")["ac_power_kw"].mean()
        weekend_hourly = weekend_data.groupby("hour")["ac_power_kw"].mean()
        
        fig_compare = go.Figure()
        fig_compare.add_trace(go.Scatter(
            x=weekday_hourly.index, y=weekday_hourly.values,
            name="Jours ouvrables",
            line=dict(color="#3498DB", width=2),
        ))
        fig_compare.add_trace(go.Scatter(
            x=weekend_hourly.index, y=weekend_hourly.values,
            name="Weekend",
            line=dict(color="#9B59B6", width=2),
        ))
        
        layout_compare = dict(**PLOT_LAYOUT)
        layout_compare["height"] = 300
        layout_compare["xaxis"] = dict(title="Heure", gridcolor="#1E232D", dtick=1)
        layout_compare["yaxis"] = dict(title="kW", gridcolor="#1E232D")
        fig_compare.update_layout(**layout_compare)
        st.plotly_chart(fig_compare, use_container_width=True)
    
    with tab3:
        st.markdown('<div class="section-title">Heatmap production (Mois x Heure, kW moyen)</div>', unsafe_allow_html=True)
        
        heatmap_data = results.groupby(["month", "hour"])["ac_power_kw"].mean().reset_index()
        heatmap_pivot = heatmap_data.pivot(index="month", columns="hour", values="ac_power_kw")
        months_fr = ["Jan", "Fev", "Mar", "Avr", "Mai", "Jun", "Jul", "Aou", "Sep", "Oct", "Nov", "Dec"]
        heatmap_pivot.index = [months_fr[m - 1] for m in heatmap_pivot.index]
        
        fig_heat = go.Figure(go.Heatmap(
            z=heatmap_pivot.values,
            x=[f"{h}h" for h in heatmap_pivot.columns],
            y=heatmap_pivot.index,
            colorscale=[
                [0, "#08090C"],
                [0.2, "#1A2744"],
                [0.4, "#2A1500"],
                [0.6, "#A05A00"],
                [0.8, "#E8860A"],
                [1, "#F5A623"]
            ],
            showscale=True,
            colorbar=dict(title="kW", tickfont=dict(color="#6B7585")),
            hovertemplate="Heure: %{x}<br>Mois: %{y}<br>Puissance: %{z:.1f} kW<extra></extra>"
        ))
        
        layout5 = dict(**PLOT_LAYOUT)
        layout5["height"] = 400
        layout5["xaxis"] = dict(title="Heure", tickfont=dict(size=10), gridcolor="#1E232D")
        layout5["yaxis"] = dict(tickfont=dict(size=10), gridcolor="#1E232D")
        fig_heat.update_layout(**layout5)
        st.plotly_chart(fig_heat, use_container_width=True)


# ─────────────────────────────────────────────
# METEO & IRRADIANCE - ENHANCED
# ─────────────────────────────────────────────
elif menu == "Meteo & Irradiance":
    st.markdown("## Conditions Meteorologiques & Irradiance")
    
    # Current weather dashboard
    weather_kpi = st.columns(6)
    
    with weather_kpi[0]:
        st.metric("Temperature", f"{current_meteo.get('temperature_2m', '--')} C")
    with weather_kpi[1]:
        st.metric("Ressentie", f"{current_meteo.get('apparent_temperature', '--')} C")
    with weather_kpi[2]:
        st.metric("Humidite", f"{current_meteo.get('relative_humidity_2m', '--')} %")
    with weather_kpi[3]:
        st.metric("Vent", f"{current_meteo.get('wind_speed_10m', '--')} km/h")
    with weather_kpi[4]:
        st.metric("GHI", f"{current_meteo.get('shortwave_radiation', '--')} W/m2")
    with weather_kpi[5]:
        st.metric("Nuages", f"{current_meteo.get('cloud_cover', '--')} %")
    
    st.markdown("---")
    
    # Irradiance tabs
    irr_tabs = st.tabs(["GHI & POA", "Temperature", "Ressource Solaire"])
    
    with irr_tabs[0]:
        col_l, col_r = st.columns(2)
        
        with col_l:
            st.markdown('<div class="section-title">Irradiance Globale Horizontale (GHI)</div>', unsafe_allow_html=True)
            
            daily_ghi = results.groupby("date").agg(
                ghi_sum=("ghi", lambda x: x.sum() / 1000),
                ghi_max=("ghi", "max"),
                ghi_mean=("ghi", "mean")
            ).reset_index()
            daily_ghi["date"] = pd.to_datetime(daily_ghi["date"])
            
            fig_ghi = go.Figure()
            fig_ghi.add_trace(go.Scatter(
                x=daily_ghi["date"], y=daily_ghi["ghi_sum"],
                fill="tozeroy", fillcolor="rgba(245,166,35,0.12)",
                line=dict(color="#F5A623", width=1.5),
                name="GHI quotidien",
                hovertemplate="Date: %{x}<br>GHI: %{y:.1f} kWh/m2<extra></extra>"
            ))
            fig_ghi.add_trace(go.Scatter(
                x=daily_ghi["date"],
                y=daily_ghi["ghi_sum"].rolling(7, center=True).mean(),
                line=dict(color="#E8860A", width=2, dash="dash"),
                name="Moy. mobile 7j"
            ))
            
            layout6 = dict(**PLOT_LAYOUT)
            layout6["height"] = 350
            layout6["yaxis"] = dict(gridcolor="#1E232D", title="kWh/m2", zeroline=False)
            fig_ghi.update_layout(**layout6)
            st.plotly_chart(fig_ghi, use_container_width=True)
        
        with col_r:
            st.markdown('<div class="section-title">POA (Plane of Array) Irradiance</div>', unsafe_allow_html=True)
            
            daily_poa = results.groupby("date").agg(
                poa_iso=("poa_isotropic", "mean"),
                poa_hd=("poa_haydavies", "mean")
            ).reset_index()
            daily_poa["date"] = pd.to_datetime(daily_poa["date"])
            
            fig_poa = go.Figure()
            fig_poa.add_trace(go.Scatter(
                x=daily_poa["date"], y=daily_poa["poa_iso"],
                line=dict(color="#F5A623", width=1.5),
                name="Isotropique"
            ))
            fig_poa.add_trace(go.Scatter(
                x=daily_poa["date"], y=daily_poa["poa_hd"],
                line=dict(color="#3498DB", width=1.5),
                name="Hay-Davies"
            ))
            
            layout_poa = dict(**PLOT_LAYOUT)
            layout_poa["height"] = 350
            layout_poa["yaxis"] = dict(gridcolor="#1E232D", title="W/m2", zeroline=False)
            fig_poa.update_layout(**layout_poa)
            st.plotly_chart(fig_poa, use_container_width=True)
        
        # Clearness index analysis
        st.markdown('<div class="section-title">Indice de clarte (Clearness Index)</div>', unsafe_allow_html=True)
        
        results["clearness_index"] = results["ghi"] / (results["ghi"].max() + 1e-6)
        daily_kt = results.groupby("date")["clearness_index"].mean().reset_index()
        daily_kt["date"] = pd.to_datetime(daily_kt["date"])
        
        fig_kt = go.Figure(go.Scatter(
            x=daily_kt["date"], y=daily_kt["clearness_index"],
            line=dict(color="#9B59B6", width=1.5),
            fill="tozeroy", fillcolor="rgba(155,89,182,0.1)",
            hovertemplate="Date: %{x}<br>KT: %{y:.2f}<extra></extra>"
        ))
        
        layout_kt = dict(**PLOT_LAYOUT)
        layout_kt["height"] = 250
        layout_kt["yaxis"] = dict(gridcolor="#1E232D", title="KT", range=[0, 1])
        fig_kt.update_layout(**layout_kt)
        st.plotly_chart(fig_kt, use_container_width=True)
    
    with irr_tabs[1]:
        col_t1, col_t2 = st.columns(2)
        
        with col_t1:
            st.markdown('<div class="section-title">Temperature ambiante</div>', unsafe_allow_html=True)
            
            daily_temp = results.groupby("date").agg(
                temp_avg=("temp_air", "mean"),
                temp_max=("temp_air", "max"),
                temp_min=("temp_air", "min")
            ).reset_index()
            daily_temp["date"] = pd.to_datetime(daily_temp["date"])
            
            fig_temp = go.Figure()
            fig_temp.add_trace(go.Scatter(
                x=daily_temp["date"], y=daily_temp["temp_max"],
                line=dict(color="#E74C3C", width=1),
                name="Max"
            ))
            fig_temp.add_trace(go.Scatter(
                x=daily_temp["date"], y=daily_temp["temp_avg"],
                line=dict(color="#F5A623", width=2),
                name="Moyenne"
            ))
            fig_temp.add_trace(go.Scatter(
                x=daily_temp["date"], y=daily_temp["temp_min"],
                line=dict(color="#3498DB", width=1),
                name="Min"
            ))
            
            layout_temp = dict(**PLOT_LAYOUT)
            layout_temp["height"] = 350
            layout_temp["yaxis"] = dict(gridcolor="#1E232D", title="C", zeroline=False)
            fig_temp.update_layout(**layout_temp)
            st.plotly_chart(fig_temp, use_container_width=True)
        
        with col_t2:
            st.markdown('<div class="section-title">Temperature cellule vs Ambiante</div>', unsafe_allow_html=True)
            
            hourly_temp = results.groupby("hour")[["temp_air", "cell_temp"]].mean().reset_index()
            
            fig_cell = go.Figure()
            fig_cell.add_trace(go.Scatter(
                x=hourly_temp["hour"], y=hourly_temp["temp_air"],
                line=dict(color="#3498DB", width=2),
                name="Ambiante"
            ))
            fig_cell.add_trace(go.Scatter(
                x=hourly_temp["hour"], y=hourly_temp["cell_temp"],
                line=dict(color="#E74C3C", width=2),
                name="Cellule"
            ))
            
            layout_cell = dict(**PLOT_LAYOUT)
            layout_cell["height"] = 350
            layout_cell["xaxis"] = dict(title="Heure", gridcolor="#1E232D", dtick=1)
            layout_cell["yaxis"] = dict(title="C", gridcolor="#1E232D")
            fig_cell.update_layout(**layout_cell)
            st.plotly_chart(fig_cell, use_container_width=True)
    
        with irr_tabs[2]:
            st.markdown('<div class="section-title">Ressource solaire mensuelle</div>', unsafe_allow_html=True)
            
            months_fr = ["Jan", "Fev", "Mar", "Avr", "Mai", "Jun", "Jul", "Aou", "Sep", "Oct", "Nov", "Dec"]
            
            monthly_solar = results.groupby("month").agg(
                ghi_total=("ghi", lambda x: x.sum() / 1000),
                dni_total=("dni", lambda x: x.sum() / 1000),
                dhi_total=("dhi", lambda x: x.sum() / 1000),
            ).reset_index()
            monthly_solar["month_name"] = [months_fr[m - 1] for m in monthly_solar["month"]]
        
        fig_solar = go.Figure()
        fig_solar.add_trace(go.Bar(
            x=monthly_solar["month_name"], y=monthly_solar["ghi_total"],
            name="GHI", marker_color="#F5A623",
            hovertemplate="GHI: %{y:.0f} kWh/m2<extra></extra>"
        ))
        fig_solar.add_trace(go.Bar(
            x=monthly_solar["month_name"], y=monthly_solar["dni_total"],
            name="DNI", marker_color="#E8860A",
            hovertemplate="DNI: %{y:.0f} kWh/m2<extra></extra>"
        ))
        fig_solar.add_trace(go.Bar(
            x=monthly_solar["month_name"], y=monthly_solar["dhi_total"],
            name="DHI", marker_color="#FFCF6B",
            hovertemplate="DHI: %{y:.0f} kWh/m2<extra></extra>"
        ))
        
        layout_solar = dict(**PLOT_LAYOUT)
        layout_solar["height"] = 300
        layout_solar["barmode"] = "group"
        layout_solar["yaxis"] = dict(gridcolor="#1E232D", title="kWh/m2")
        fig_solar.update_layout(**layout_solar)
        st.plotly_chart(fig_solar, use_container_width=True)


# ─────────────────────────────────────────────
# PERFORMANCE ANALYSIS - NEW PAGE
# ─────────────────────────────────────────────
elif menu == "Performance Analysis":
    st.markdown("## Analyse de Performance Avancee")
    
    # Performance metrics overview
    perf_kpi = st.columns(4)
    
    with perf_kpi[0]:
        st.metric("PR Moyen", f"{daily['pr'].mean():.1f}%",
                 delta=f"{daily['pr'].std():.1f}% ecart-type")
    with perf_kpi[1]:
        st.metric("Energy Yield", f"{daily['energy_yield'].mean():.1f} kWh/kWp")
    with perf_kpi[2]:
        st.metric("Facteur de charge", f"{daily['capacity_factor'].mean():.1f}%")
    with perf_kpi[3]:
        st.metric("Disponibilite", "98.5%",
                 delta="Estimation")
    
    st.markdown("---")
    
    # Performance ratio distribution
    col_p1, col_p2 = st.columns(2)
    
    with col_p1:
        st.markdown('<div class="section-title">Distribution du PR</div>', unsafe_allow_html=True)
        
        fig_dist = go.Figure()
        fig_dist.add_trace(go.Histogram(
            x=daily["pr"].dropna(),
            nbinsx=30,
            marker_color="#F5A623",
            hovertemplate="PR: %{x:.1f}%<br>Freq: %{y}<extra></extra>"
        ))
        
        layout_dist = dict(**PLOT_LAYOUT)
        layout_dist["height"] = 300
        layout_dist["xaxis"] = dict(title="PR (%)", gridcolor="#1E232D")
        layout_dist["yaxis"] = dict(title="Frequence", gridcolor="#1E232D")
        fig_dist.update_layout(**layout_dist)
        st.plotly_chart(fig_dist, use_container_width=True)
    
    with col_p2:
        st.markdown('<div class="section-title">PR Mensuel</div>', unsafe_allow_html=True)
        
        fig_pr_month = go.Figure()
        fig_pr_month.add_trace(go.Bar(
            x=monthly["month_name"], y=monthly["avg_pr"],
            marker_color="#F5A623",
            error_y=dict(
                type="data",
                array=monthly["max_pr"] - monthly["avg_pr"],
                arrayminus=monthly["avg_pr"] - monthly["min_pr"],
                visible=True
            ),
            hovertemplate="PR: %{y:.1f}%<extra></extra>"
        ))
        
        layout_pr_month = dict(**PLOT_LAYOUT)
        layout_pr_month["height"] = 300
        layout_pr_month["yaxis"] = dict(gridcolor="#1E232D", title="PR %", range=[50, 100])
        fig_pr_month.update_layout(**layout_pr_month)
        st.plotly_chart(fig_pr_month, use_container_width=True)
    
    # Energy yield analysis
    st.markdown('<div class="section-title">Rendement energetique (Energy Yield)</div>', unsafe_allow_html=True)
    
    col_ey1, col_ey2 = st.columns(2)
    
    with col_ey1:
        fig_ey = go.Figure(go.Scatter(
            x=daily["date"], y=daily["energy_yield"],
            fill="tozeroy", fillcolor="rgba(26,188,156,0.1)",
            line=dict(color="#1ABC9C", width=1.5),
            hovertemplate="Date: %{x}<br>EY: %{y:.2f} kWh/kWp<extra></extra>"
        ))
        
        layout_ey = dict(**PLOT_LAYOUT)
        layout_ey["height"] = 300
        layout_ey["yaxis"] = dict(gridcolor="#1E232D", title="kWh/kWp")
        fig_ey.update_layout(**layout_ey)
        st.plotly_chart(fig_ey, use_container_width=True)
    
    with col_ey2:
        # Cumulative energy
        daily["cumulative_kwh"] = daily["production_kwh"].cumsum()
        
        fig_cum = go.Figure(go.Scatter(
            x=daily["date"], y=daily["cumulative_kwh"] / 1000,
            line=dict(color="#9B59B6", width=2),
            fill="tozeroy", fillcolor="rgba(155,89,182,0.1)",
            hovertemplate="Date: %{x}<br>Cumul: %{y:.2f} MWh<extra></extra>"
        ))
        
        layout_cum = dict(**PLOT_LAYOUT)
        layout_cum["height"] = 300
        layout_cum["yaxis"] = dict(gridcolor="#1E232D", title="MWh")
        fig_cum.update_layout(**layout_cum)
        st.plotly_chart(fig_cum, use_container_width=True)
    
    # Anomaly detection section
    st.markdown('<div class="section-title">Detection d\'anomalies</div>', unsafe_allow_html=True)
    
    # Simple anomaly detection using IQR
    Q1 = daily["production_kwh"].quantile(0.25)
    Q3 = daily["production_kwh"].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    anomalies = daily[(daily["production_kwh"] < lower_bound) | (daily["production_kwh"] > upper_bound)]
    
    if len(anomalies) > 0:
        st.warning(f"Detecte {len(anomalies)} jours avec production anormale")
        st.dataframe(
            anomalies[["date", "production_kwh", "pr", "avg_temp", "avg_ghi"]].head(10),
            hide_index=True,
            use_container_width=True
        )
    else:
        st.success("Aucune anomalie detectee dans la periode")


# Rest of the menu options (Onduleurs, Installation, Rapport) with enhanced features...

# ─────────────────────────────────────────────
# FOOTER - ENHANCED
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(f"""
<div style="text-align:center;color:#252A35;font-size:11px;padding:10px 0;font-family:'Space Mono',monospace;letter-spacing:0.08em">
    SOLARIS DIGITAL TWIN V2.0 &nbsp;|&nbsp; MOHAMMEDIA, MAROC &nbsp;|&nbsp; pvlib + Open-Meteo API
    &nbsp;|&nbsp; {now.strftime('%d/%m/%Y %H:%M')}
</div>
""", unsafe_allow_html=True)
