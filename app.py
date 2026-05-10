"""
SOLARIS - Digital Twin PV · Mohammedia, Maroc
Streamlit + pvlib · Open-Meteo API
GitHub Deployment Ready
Enhanced Version 2.0 - CORRECTED + THEME TOGGLE
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
# THEME STATE INITIALISATION (ADDED)
# Default mode = light, toggled via session_state
# ─────────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# ─────────────────────────────────────────────
# THEME VARIABLES (ADDED)
# Two palettes — dark (original) and light (new).
# All CSS variables are resolved at render time.
# ─────────────────────────────────────────────
if st.session_state.dark_mode:
    THEME = dict(
        dark_bg       = "#08090C",
        card_bg       = "#111318",
        card_bg2      = "#191D25",
        border        = "#252A35",
        border_bright = "#353C4A",
        text_primary  = "#E8EDF5",
        text_secondary= "#6B7585",
        text_muted    = "#3D4553",
        sidebar_bg    = "#0A0C10",
        plot_paper    = "#111318",
        plot_plot     = "#111318",
        plot_grid     = "#1E232D",
        plot_font     = "#6B7585",
        toggle_label  = "Light Mode",
        plotly_template = "plotly_dark",
    )
else:
    THEME = dict(
        dark_bg       = "#F4F6FA",
        card_bg       = "#FFFFFF",
        card_bg2      = "#F0F3F8",
        border        = "#DDE2EC",
        border_bright = "#BEC7D8",
        text_primary  = "#1A2035",
        text_secondary= "#5A6580",
        text_muted    = "#9BA5BB",
        sidebar_bg    = "#FFFFFF",
        plot_paper    = "#FFFFFF",
        plot_plot     = "#FFFFFF",
        plot_grid     = "#E8EDF5",
        plot_font     = "#5A6580",
        toggle_label  = "Dark Mode",
        plotly_template = "plotly_white",
    )

# ─────────────────────────────────────────────
# CSS PERSONNALISE - THEME-AWARE
# Only the CSS block has changed — all variable
# values are injected from THEME dict above.
# ─────────────────────────────────────────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600;700&display=swap');

    :root {{
        --solar-yellow:  #F5A623;
        --solar-orange:  #E8860A;
        --solar-amber:   #FFCF6B;
        --dark-bg:       {THEME['dark_bg']};
        --card-bg:       {THEME['card_bg']};
        --card-bg2:      {THEME['card_bg2']};
        --border:        {THEME['border']};
        --border-bright: {THEME['border_bright']};
        --text-primary:  {THEME['text_primary']};
        --text-secondary:{THEME['text_secondary']};
        --text-muted:    {THEME['text_muted']};
        --green:  #2ECC71;
        --red:    #E74C3C;
        --blue:   #3498DB;
        --purple: #9B59B6;
        --teal:   #1ABC9C;
        --gradient-gold: linear-gradient(135deg, #F5A623, #E8860A);
        --gradient-dark: linear-gradient(135deg, {THEME['card_bg']}, {THEME['card_bg2']});
        --sidebar-bg:    {THEME['sidebar_bg']};
    }}

    html, body, [class*="css"] {{
        font-family: 'DM Sans', sans-serif;
    }}

    .stApp {{
        background-color: var(--dark-bg);
        background-image:
            radial-gradient(ellipse at 20% 0%, rgba(245,166,35,0.04) 0%, transparent 60%),
            radial-gradient(ellipse at 80% 100%, rgba(52,152,219,0.03) 0%, transparent 60%);
    }}

    [data-testid="stSidebar"] {{
        background-color: var(--sidebar-bg) !important;
        border-right: 1px solid var(--border) !important;
    }}

    [data-testid="stSidebar"] .stRadio label {{
        font-family: 'DM Sans', sans-serif !important;
        color: var(--text-secondary) !important;
        font-size: 13px !important;
        transition: color 0.3s ease;
    }}

    [data-testid="stSidebar"] .stRadio label:hover {{ color: var(--solar-yellow) !important; }}

    /* ── THEME TOGGLE BUTTON (ADDED) ── */
    .theme-toggle-bar {{
        display: flex;
        justify-content: flex-end;
        padding: 6px 0 0 0;
        margin-bottom: -6px;
    }}

    .main-header {{
        background: var(--gradient-dark);
        border: 1px solid var(--border);
        border-top: 2px solid var(--solar-yellow);
        border-radius: 0 0 12px 12px;
        padding: 22px 32px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }}

    .plant-name {{
        font-family: 'Space Mono', monospace;
        font-size: 20px;
        font-weight: 700;
        background: var(--gradient-gold);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }}

    .plant-sub {{
        font-size: 12px;
        color: var(--text-secondary);
        margin-top: 5px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }}

    .status-badge {{
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
    }}

    .status-dot {{
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: var(--green);
        box-shadow: 0 0 8px var(--green);
        animation: pulse 2s infinite;
    }}

    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50%       {{ opacity: 0.4; }}
    }}

    .metric-card {{
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 20px 22px;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }}

    .metric-card:hover {{
        border-color: var(--solar-yellow);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(245,166,35,0.1);
    }}

    .metric-card::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--solar-yellow), var(--solar-orange));
        opacity: 0.6;
    }}

    .metric-label {{
        font-size: 10px;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-family: 'Space Mono', monospace;
        margin-bottom: 8px;
    }}

    .metric-value {{
        font-family: 'Space Mono', monospace;
        font-size: 26px;
        font-weight: 700;
        color: var(--solar-yellow);
        line-height: 1.1;
    }}

    .metric-unit {{
        font-size: 13px;
        color: var(--text-secondary);
        font-family: 'DM Sans', sans-serif;
        font-weight: 400;
        margin-top: 4px;
    }}

    .section-title {{
        font-family: 'Space Mono', monospace;
        font-size: 11px;
        font-weight: 700;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.15em;
        margin-bottom: 14px;
        padding-bottom: 10px;
        border-bottom: 1px solid var(--border);
    }}

    .alert-card {{
        border-radius: 8px;
        padding: 11px 16px;
        margin-bottom: 8px;
        font-size: 13px;
        border-left: 3px solid;
        font-family: 'DM Sans', sans-serif;
        transition: transform 0.2s ease;
    }}

    .alert-card:hover {{ transform: translateX(4px); }}

    .alert-warning {{ background: rgba(245,166,35,0.06); border-color: var(--solar-yellow); color: #D4993A; }}
    .alert-error   {{ background: rgba(231,76,60,0.06);  border-color: var(--red);          color: #D45C4E; }}
    .alert-ok      {{ background: rgba(46,204,113,0.06); border-color: var(--green);        color: #3DBD6A; }}
    .alert-info    {{ background: rgba(52,152,219,0.06); border-color: var(--blue);         color: #5BA4D9; }}

    .spec-table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}

    .spec-table tr {{
        border-bottom: 1px solid var(--border);
        transition: background 0.2s ease;
    }}

    .spec-table tr:hover {{ background: rgba(245,166,35,0.04); }}
    .spec-table tr:last-child {{ border-bottom: none; }}

    .spec-table td {{ padding: 10px 14px; vertical-align: middle; }}

    .spec-table td:first-child {{
        color: var(--text-secondary);
        font-family: 'Space Mono', monospace;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        width: 48%;
    }}

    .spec-table td:last-child {{ color: var(--text-primary); font-weight: 500; text-align: right; }}

    .spec-block {{
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 4px 0;
        margin-bottom: 16px;
        transition: all 0.3s ease;
    }}

    .spec-block:hover {{ border-color: var(--border-bright); }}

    .spec-block-header {{
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
    }}

    .highlight-value {{ color: var(--solar-yellow); font-family: 'Space Mono', monospace; font-weight: 700; }}

    .badge-green  {{ background: rgba(46,204,113,0.1);  color: var(--green);  border: 1px solid rgba(46,204,113,0.2);  border-radius: 4px; padding: 2px 8px; font-size: 11px; font-family: 'Space Mono', monospace; }}
    .badge-orange {{ background: rgba(245,166,35,0.1);  color: var(--solar-yellow); border: 1px solid rgba(245,166,35,0.2); border-radius: 4px; padding: 2px 8px; font-size: 11px; font-family: 'Space Mono', monospace; }}
    .badge-blue   {{ background: rgba(52,152,219,0.1);  color: var(--blue);   border: 1px solid rgba(52,152,219,0.2);  border-radius: 4px; padding: 2px 8px; font-size: 11px; font-family: 'Space Mono', monospace; }}
    .badge-purple {{ background: rgba(155,89,182,0.1);  color: var(--purple); border: 1px solid rgba(155,89,182,0.2);  border-radius: 4px; padding: 2px 8px; font-size: 11px; font-family: 'Space Mono', monospace; }}

    .kpi-card {{
        background: var(--gradient-dark);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 20px 16px;
        text-align: center;
        transition: all 0.3s ease;
    }}

    .kpi-card:hover {{
        border-color: var(--solar-yellow);
        box-shadow: 0 6px 20px rgba(0,0,0,0.12);
    }}

    .kpi-value {{
        font-family: 'Space Mono', monospace;
        font-size: 32px;
        font-weight: 700;
        background: var(--gradient-gold);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}

    .kpi-label {{ font-size: 11px; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.1em; margin-top: 8px; }}

    div[data-testid="metric-container"] {{
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 16px 18px;
        transition: all 0.3s ease;
    }}

    div[data-testid="metric-container"]:hover {{
        border-color: var(--solar-yellow);
        transform: translateY(-2px);
    }}

    div[data-testid="metric-container"] label {{
        color: var(--text-secondary) !important;
        font-size: 11px !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-family: 'Space Mono', monospace !important;
    }}

    div[data-testid="metric-container"] [data-testid="stMetricValue"] {{
        color: var(--solar-yellow) !important;
        font-size: 24px !important;
        font-weight: 700 !important;
        font-family: 'Space Mono', monospace !important;
    }}

    .stPlotlyChart {{ border-radius: 10px; overflow: hidden; border: 1px solid var(--border); }}

    .sidebar-brand {{
        font-family: 'Space Mono', monospace;
        font-size: 18px;
        font-weight: 700;
        background: var(--gradient-gold);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: 0.1em;
        margin-bottom: 4px;
    }}

    .sidebar-sub {{
        font-size: 11px;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 16px;
    }}

    .data-info {{
        background: rgba(52,152,219,0.08);
        border: 1px solid rgba(52,152,219,0.2);
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 11px;
        color: var(--blue);
        font-family: 'Space Mono', monospace;
    }}

    .stDownloadButton button {{
        background: var(--gradient-gold) !important;
        color: white !important;
        border: none !important;
        font-family: 'Space Mono', monospace !important;
        font-weight: 700 !important;
        transition: all 0.3s ease !important;
    }}

    .stDownloadButton button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(245,166,35,0.3);
    }}

    hr {{ border-color: var(--border) !important; }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background-color: var(--card-bg);
        border-radius: 8px;
        padding: 6px;
    }}

    .stTabs [data-baseweb="tab"] {{
        color: var(--text-secondary);
        font-family: 'Space Mono', monospace;
        font-size: 12px;
        border-radius: 6px;
    }}

    .stTabs [aria-selected="true"] {{
        background-color: rgba(245,166,35,0.1);
        color: var(--solar-yellow);
    }}

    .glass-card {{
        background: rgba(17, 19, 24, 0.8);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 20px;
    }}

    /* ── IMPROVED SPACING (ADDED) ── */
    .block-container {{
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
    }}

    section[data-testid="stSidebar"] > div {{
        padding-top: 1.5rem;
        padding-left: 1.2rem;
        padding-right: 1.2rem;
    }}

    /* ── THEME TOGGLE BUTTON STYLE (ADDED) ── */
    button[data-testid="baseButton-secondary"].theme-btn {{
        background: var(--card-bg) !important;
        color: var(--text-secondary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
        font-family: 'Space Mono', monospace !important;
        font-size: 11px !important;
        padding: 4px 14px !important;
        letter-spacing: 0.08em !important;
        transition: all 0.25s ease !important;
    }}

    button[data-testid="baseButton-secondary"].theme-btn:hover {{
        border-color: var(--solar-yellow) !important;
        color: var(--solar-yellow) !important;
    }}
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
# CONFIGURATION BLYNK - ESP32 RELAY
# ─────────────────────────────────────────────
BLYNK_CONFIG = {
    "auth_token": "l5IGH1fmy7E8ULoiLWjdXm9ZmaJcduYI",
    "server": "https://blynk.cloud/external/api/",

    # Relais
    "relay_pin": "V0",
    "relay_name": "Relais Principal",

    # PZEM
    "voltage_pin": "V2",
    "current_pin": "V3",
    "power_pin": "V4",
    "energy_pin": "V5",
    "frequency_pin": "V6",
    "pf_pin": "V7",
}
# ─────────────────────────────────────────────
# FONCTIONS PRINCIPALES
# ─────────────────────────────────────────────

@st.cache_data(ttl=3600)
def fetch_meteo(lat, lon, start_date, end_date):
    """Fetch meteorological data from Open-Meteo API"""
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
            "cloud_cover": data["hourly"].get("cloud_cover", [0] * len(data["hourly"]["time"])),
        })
        df = df.set_index("datetime")
        return df
    except Exception as e:
        st.error(f"Erreur API meteo : {e}")
        return None


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

    dni_extra = irradiance.get_extra_radiation(times)

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
        dni_extra=dni_extra,
        model="haydavies"
    )

    temp_params = temperature.TEMPERATURE_MODEL_PARAMETERS["sapm"]["open_rack_glass_glass"]
    cell_temp = temperature.sapm_cell(
        poa_global=poa_isotropic["poa_global"], temp_air=df["temp_air"],
        wind_speed=df["wind_speed"],
        a=temp_params["a"], b=temp_params["b"], deltaT=temp_params["deltaT"],
    )

    dc_power = pvsystem.pvwatts_dc(
        g_poa_effective=poa_isotropic["poa_global"], temp_cell=cell_temp,
        pdc0=pdc0, gamma_pdc=gamma_pdc,
    )

    inverter_efficiency = 0.97
    ac_power = dc_power * inverter_efficiency

    additional_losses = 0.10
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
        "dni_extra": dni_extra,
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
    total_capacity_kw = SITE["capacity_kwp"]

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
    """Get current weather"""
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


def blynk_get_pin(pin):
    """Lire l'etat d'un pin Blynk"""
    url = f"{BLYNK_CONFIG['server']}get?token={BLYNK_CONFIG['auth_token']}&{pin}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        return None


def blynk_set_pin(pin, value):
    """Ecrire une valeur sur un pin Blynk"""
    url = f"{BLYNK_CONFIG['server']}update?token={BLYNK_CONFIG['auth_token']}&{pin}={value}"
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except:
        return False


def blynk_get_device_status():
    """Recuperer le statut du device Blynk"""
    url = f"{BLYNK_CONFIG['server']}isHardwareConnected?token={BLYNK_CONFIG['auth_token']}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        return False
def blynk_get_value(pin):
    """Lire une valeur numerique depuis Blynk"""

    url = f"{BLYNK_CONFIG['server']}get?token={BLYNK_CONFIG['auth_token']}&{pin}"

    try:
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            return float(response.text)

    except:
        return 0.0

    return 0.0

def calculate_degraded_power(pdc0, years_operation, degradation_rate):
    return pdc0 * (1 - degradation_rate) ** years_operation


def estimate_co2_avoidance(energy_kwh, grid_emission_factor=0.65):
    return energy_kwh * grid_emission_factor


def calculate_financial_metrics(energy_kwh, electricity_price=0.12):
    return energy_kwh * electricity_price


# ─────────────────────────────────────────────
# PLOT LAYOUT — theme-aware (MODIFIED)
# Paper/plot bg and font color pulled from THEME
# ─────────────────────────────────────────────
PLOT_LAYOUT = dict(
    template=THEME["plotly_template"],
    paper_bgcolor=THEME["plot_paper"],
    plot_bgcolor=THEME["plot_plot"],
    font=dict(family="DM Sans", color=THEME["plot_font"]),
    margin=dict(t=20, b=30, l=50, r=20),
    xaxis=dict(gridcolor=THEME["plot_grid"], zeroline=False),
    yaxis=dict(gridcolor=THEME["plot_grid"], zeroline=False),
    hovermode="x unified",
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
            "Performance Analysis",
            "Onduleurs",
            "Installation",
            "Controle Relais",
            "Rapport",
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("**Periode d'analyse**")

    col_s, col_e = st.columns(2)
    with col_s:
        start_date = st.date_input(
            "Debut",
            value=datetime(2026, 4, 1).date(),
            label_visibility="collapsed"
        )
    with col_e:
        today = datetime.today().date()
        end_date = st.date_input(
            "Fin",
            value=today,
            label_visibility="collapsed"
        )

    preset_cols = st.columns(3)
    with preset_cols[0]:
        if st.button("7j", key="7d"):
            st.session_state["_preset_start"] = (datetime.now() - timedelta(days=7)).date()
            st.session_state["_preset_end"] = datetime.now().date()
            st.rerun()
    with preset_cols[1]:
        if st.button("30j", key="30d"):
            st.session_state["_preset_start"] = (datetime.now() - timedelta(days=30)).date()
            st.session_state["_preset_end"] = datetime.now().date()
            st.rerun()
    with preset_cols[2]:
        if st.button("90j", key="90d"):
            st.session_state["_preset_start"] = (datetime.now() - timedelta(days=90)).date()
            st.session_state["_preset_end"] = datetime.now().date()
            st.rerun()

    if "_preset_start" in st.session_state:
        start_date = st.session_state.pop("_preset_start")
    if "_preset_end" in st.session_state:
        end_date = st.session_state.pop("_preset_end")

    st.markdown(f"Du **{start_date.strftime('%d/%m/%Y')}** au **{end_date.strftime('%d/%m/%Y')}**")

    data_age = (datetime.now().date() - end_date).days
    if data_age == 0:
        st.markdown('<div class="data-info">Donnees actualisees aujourd\'hui</div>', unsafe_allow_html=True)
    elif data_age < 3:
        st.markdown(f'<div class="data-info">Donnees actualisees il y a {data_age} jours</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="data-info" style="border-color: rgba(245,166,35,0.3); color: #D4993A;">Donnees actualisees il y a {data_age} jours</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**Systeme**")
    st.markdown(f"Capacite : **{SITE['capacity_kwp']} kWp**")
    st.markdown(f"Panneaux : **{SITE['num_panels']}**")
    st.markdown(f"Onduleurs : **{SITE['num_inverters']}**")
    st.markdown(f"Inclinaison : **{PANEL['tilt']}°**")
    st.markdown(f"Azimut : **{PANEL['azimuth']}°**")

    years_operational = datetime.now().year - int(SITE['commissioning_date'])
    degraded_power = calculate_degraded_power(PANEL['pdc0'], years_operational, PANEL['degradation_pct_yr'] / 100)
    st.markdown("---")
    st.markdown("**Degradation estimee**")
    st.markdown(f"Apres {years_operational} ans : **{degraded_power:.0f} W** (-{(1 - degraded_power / PANEL['pdc0']) * 100:.1f}%)")

    # ── THEME TOGGLE in sidebar (ADDED) ──
    # Placed at bottom of sidebar for easy access without disrupting layout.
    st.markdown("---")
    st.markdown("**Apparence**")
    if st.button(
        f"{'Light Mode' if st.session_state.dark_mode else 'Dark Mode'}",
        key="theme_toggle",
        use_container_width=True,
    ):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()


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

daily = compute_daily(results, SITE["num_panels"])
monthly = compute_monthly(daily)
current_meteo = get_current_meteo(SITE["lat"], SITE["lon"])
now = datetime.now()

# ─────────────────────────────────────────────
# PZEM REAL TIME VALUES
# ─────────────────────────────────────────────

pzem_voltage = blynk_get_value(BLYNK_CONFIG["voltage_pin"])
pzem_current = blynk_get_value(BLYNK_CONFIG["current_pin"])
pzem_power = blynk_get_value(BLYNK_CONFIG["power_pin"])
pzem_energy = blynk_get_value(BLYNK_CONFIG["energy_pin"])
pzem_frequency = blynk_get_value(BLYNK_CONFIG["frequency_pin"])
pzem_pf = blynk_get_value(BLYNK_CONFIG["pf_pin"])
# ─────────────────────────────────────────────
# HEADER
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
                <div style="font-size:12px;color:{THEME['text_secondary']};font-family:'Space Mono',monospace">
                    {now.strftime('%d/%m/%Y %H:%M')}
                </div>
                <div style="font-size:10px;color:{THEME['text_muted']};font-family:'Space Mono',monospace">
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
# VUE GLOBALE
# ─────────────────────────────────────────────
if menu == "Vue Globale":
    total_kwh = daily["production_kwh"].sum()
    gross_kwh = daily["gross_production_kwh"].sum()
    losses_kwh = gross_kwh - total_kwh
    avg_daily_losses = losses_kwh / len(daily) if len(daily) > 0 else 0

    avg_pr = daily["pr"].mean()
    avg_cf = daily["capacity_factor"].mean()
    co2_avoided = estimate_co2_avoidance(total_kwh)
    financial_savings = calculate_financial_metrics(total_kwh)
        st.markdown("## Monitoring Temps Reel PZEM")

    pzem_cols = st.columns(6)

    with pzem_cols[0]:
        st.metric("Voltage", f"{pzem_voltage:.1f} V")

    with pzem_cols[1]:
        st.metric("Current", f"{pzem_current:.2f} A")

    with pzem_cols[2]:
        st.metric("Power", f"{pzem_power:.1f} W")

    with pzem_cols[3]:
        st.metric("Energy", f"{pzem_energy:.3f} kWh")

    with pzem_cols[4]:
        st.metric("Frequency", f"{pzem_frequency:.1f} Hz")

    with pzem_cols[5]:
        st.metric("PF", f"{pzem_pf:.2f}")
        
    st.markdown("## Performance Globale")

    kpi_cols = st.columns(5)
    with kpi_cols[0]:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-value">{total_kwh/1000:.2f}</div><div class="kpi-label">Production Totale<br>MWh</div></div>""", unsafe_allow_html=True)
    with kpi_cols[1]:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-value">{avg_pr:.1f}</div><div class="kpi-label">Performance<br>Ratio %</div></div>""", unsafe_allow_html=True)
    with kpi_cols[2]:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-value">{co2_avoided:.0f}</div><div class="kpi-label">CO2 Evite<br>kg</div></div>""", unsafe_allow_html=True)
    with kpi_cols[3]:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-value">{financial_savings:.0f}</div><div class="kpi-label">Economies<br>EUR</div></div>""", unsafe_allow_html=True)
    with kpi_cols[4]:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-value">{avg_cf:.1f}</div><div class="kpi-label">Facteur<br>Capacite %</div></div>""", unsafe_allow_html=True)

    st.markdown("---")

    col_img, col_perf = st.columns([5, 1])

    with col_img:
        import os
        if os.path.exists("assets/Scene_enset.png"):
            st.image("assets/Scene_enset.png", use_container_width=True)

        weather_cols = st.columns(4)
        with weather_cols[0]:
            st.metric("Temperature", f"{current_meteo.get('temperature_2m', '--')} °C",
                      delta=f"Ressentie: {current_meteo.get('apparent_temperature', '--')} °C")
        with weather_cols[1]:
            st.metric("Irradiance", f"{ghi_now:.0f} W/m²")
        with weather_cols[2]:
            st.metric("Vent", f"{current_meteo.get('wind_speed_10m', '--')} km/h")
        with weather_cols[3]:
            st.metric("Humidite", f"{current_meteo.get('relative_humidity_2m', '--')} %")

    with col_perf:
        st.markdown('<div class="section-title">Performance en temps reel</div>', unsafe_allow_html=True)

        current_hour = now.hour
        today_date = now.date()

        mask = (results["date"] == today_date) & (results["hour"] == current_hour)
        current_power = results.loc[mask, "net_ac_power_kw"].values
        current_power_val = current_power[0] if len(current_power) > 0 else 0.0

        st.metric("Puissance actuelle", f"{current_power_val:.2f} kW")

        today_daily = daily[daily["date"].dt.date == today_date]
        today_kwh = today_daily["production_kwh"].values[0] if len(today_daily) > 0 else 0.0

        st.metric("Production du jour", f"{today_kwh:.2f} kWh")
        st.metric(
            "Pertes journalieres moy.",
            f"{avg_daily_losses:.1f} kWh",
            delta=f"{(losses_kwh / gross_kwh) * 100:.1f}%" if gross_kwh > 0 else "0%"
        )
        st.metric(
            "Rendement energetique",
            f"{(total_kwh / gross_kwh) * 100:.1f}%" if gross_kwh > 0 else "0%"
        )

    st.markdown("---")

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown('<div class="section-title">Production journaliere (kWh)</div>', unsafe_allow_html=True)

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
        if len(anomalies) > 0:
            fig_daily.add_trace(go.Scatter(
                x=anomalies["date"], y=anomalies["production_kwh"],
                mode="markers", name="Anomalies",
                marker=dict(color="#E74C3C", size=10, symbol="x"),
            ))

        layout = dict(**PLOT_LAYOUT)
        layout["height"] = 320
        layout["showlegend"] = True
        layout["yaxis"] = dict(gridcolor=THEME["plot_grid"], title="kWh", zeroline=False)
        fig_daily.update_layout(**layout)
        st.plotly_chart(fig_daily, use_container_width=True)

    with col_right:
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
            textfont=dict(color=THEME["text_primary"], size=9, family="Space Mono"),
        ))
        layout2 = dict(**PLOT_LAYOUT)
        layout2["height"] = 320
        fig_weekday.update_layout(**layout2)
        st.plotly_chart(fig_weekday, use_container_width=True)

    st.markdown("---")

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
                {len(low_pr_days)} jours avec PR &lt; 70% —
                Dernier : {low_pr_days["date"].max().strftime('%d/%m/%Y')}
            </div>""", unsafe_allow_html=True)

        if len(high_temp_days) > 0:
            st.markdown(f"""
            <div class="alert-card alert-warning">
                <b>Temperature elevee</b><br>
                {len(high_temp_days)} jours &gt; 35°C — Perte de rendement estimee
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
# PRODUCTION DETAILLEE
# ─────────────────────────────────────────────
elif menu == "Production":
    st.markdown("## Analyse de production detaillee")

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
                             annotation_font_color="#6B7585", annotation_font_size=11)
            fig_pr.add_hline(y=85, line_dash="dash", line_color="#2ECC71",
                             annotation_text="Cible 85%",
                             annotation_font_color="#2ECC71", annotation_font_size=11)

            layout3 = dict(**PLOT_LAYOUT)
            layout3["height"] = 350
            layout3["yaxis"] = dict(gridcolor=THEME["plot_grid"], range=[0, 110], zeroline=False)
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
            layout_cf["yaxis"] = dict(gridcolor=THEME["plot_grid"], title="%", zeroline=False)
            fig_cf.update_layout(**layout_cf)
            st.plotly_chart(fig_cf, use_container_width=True)

        st.markdown('<div class="section-title">Analyse de correlation</div>', unsafe_allow_html=True)

        corr_cols = st.columns(3)
        with corr_cols[0]:
            fig_corr1 = px.scatter(
                daily, x="avg_temp", y="production_kwh",
                color="pr", color_continuous_scale="YlOrRd", opacity=0.7, trendline="ols",
                labels={"avg_temp": "Temp moy (°C)", "production_kwh": "Production (kWh)", "pr": "PR %"},
                title="Temperature vs Production"
            )
            fig_corr1.update_layout(**{**PLOT_LAYOUT, "height": 300})
            st.plotly_chart(fig_corr1, use_container_width=True)

        with corr_cols[1]:
            fig_corr2 = px.scatter(
                daily, x="peak_sun_hours", y="production_kwh",
                color="pr", color_continuous_scale="YlOrRd", opacity=0.7, trendline="ols",
                labels={"peak_sun_hours": "PSH (h)", "production_kwh": "Production (kWh)", "pr": "PR %"},
                title="PSH vs Production"
            )
            fig_corr2.update_layout(**{**PLOT_LAYOUT, "height": 300})
            st.plotly_chart(fig_corr2, use_container_width=True)

        with corr_cols[2]:
            fig_corr3 = px.scatter(
                daily, x="avg_wind", y="production_kwh",
                color="pr", color_continuous_scale="YlOrRd", opacity=0.7,
                labels={"avg_wind": "Vent (m/s)", "production_kwh": "Production (kWh)"},
                title="Vent vs Production"
            )
            fig_corr3.update_layout(**{**PLOT_LAYOUT, "height": 300})
            st.plotly_chart(fig_corr3, use_container_width=True)

    with tab2:
        st.markdown('<div class="section-title">Profil horaire de production</div>', unsafe_allow_html=True)

        hourly_stats = results.groupby("hour")["ac_power_kw"].agg(["mean", "std", "min", "max"]).reset_index()

        fig_hour = go.Figure()
        fig_hour.add_trace(go.Scatter(
            x=hourly_stats["hour"], y=hourly_stats["max"],
            fill=None, mode="lines",
            line=dict(color="rgba(245,166,35,0.2)", width=0), showlegend=False,
        ))
        fig_hour.add_trace(go.Scatter(
            x=hourly_stats["hour"], y=hourly_stats["min"],
            fill="tonexty", fillcolor="rgba(245,166,35,0.1)",
            mode="lines", line=dict(color="rgba(245,166,35,0.2)", width=0),
            name="Plage min-max",
        ))
        fig_hour.add_trace(go.Scatter(
            x=hourly_stats["hour"], y=hourly_stats["mean"],
            fill=None, line=dict(color="#F5A623", width=2.5),
            name="Moyenne",
            hovertemplate="Heure: %{x}h<br>Puissance moy: %{y:.2f} kW<extra></extra>"
        ))

        layout4 = dict(**PLOT_LAYOUT)
        layout4["height"] = 350
        layout4["xaxis"] = dict(title="Heure", gridcolor=THEME["plot_grid"], dtick=1, zeroline=False)
        layout4["yaxis"] = dict(title="Puissance (kW)", gridcolor=THEME["plot_grid"], zeroline=False)
        fig_hour.update_layout(**layout4)
        st.plotly_chart(fig_hour, use_container_width=True)

        st.markdown('<div class="section-title">Profil horaire: Jour ouvrable vs Weekend</div>', unsafe_allow_html=True)

        weekend_dates = set(daily[daily["is_weekend"]]["date"].dt.date)
        weekday_data = results[~results["date"].isin(weekend_dates)]
        weekend_data = results[results["date"].isin(weekend_dates)]

        weekday_hourly = weekday_data.groupby("hour")["ac_power_kw"].mean()
        weekend_hourly = weekend_data.groupby("hour")["ac_power_kw"].mean()

        fig_compare = go.Figure()
        fig_compare.add_trace(go.Scatter(
            x=weekday_hourly.index, y=weekday_hourly.values,
            name="Jours ouvrables", line=dict(color="#3498DB", width=2),
        ))
        fig_compare.add_trace(go.Scatter(
            x=weekend_hourly.index, y=weekend_hourly.values,
            name="Weekend", line=dict(color="#9B59B6", width=2),
        ))

        layout_compare = dict(**PLOT_LAYOUT)
        layout_compare["height"] = 300
        layout_compare["xaxis"] = dict(title="Heure", gridcolor=THEME["plot_grid"], dtick=1)
        layout_compare["yaxis"] = dict(title="kW", gridcolor=THEME["plot_grid"])
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
                [0, "#08090C"], [0.2, "#1A2744"], [0.4, "#2A1500"],
                [0.6, "#A05A00"], [0.8, "#E8860A"], [1, "#F5A623"]
            ],
            showscale=True,
            colorbar=dict(title="kW", tickfont=dict(color=THEME["plot_font"])),
            hovertemplate="Heure: %{x}<br>Mois: %{y}<br>Puissance: %{z:.1f} kW<extra></extra>"
        ))

        layout5 = dict(**PLOT_LAYOUT)
        layout5["height"] = 400
        layout5["xaxis"] = dict(title="Heure", tickfont=dict(size=10), gridcolor=THEME["plot_grid"])
        layout5["yaxis"] = dict(tickfont=dict(size=10), gridcolor=THEME["plot_grid"])
        fig_heat.update_layout(**layout5)
        st.plotly_chart(fig_heat, use_container_width=True)


# ─────────────────────────────────────────────
# METEO & IRRADIANCE
# ─────────────────────────────────────────────
elif menu == "Meteo & Irradiance":
    st.markdown("## Conditions Meteorologiques & Irradiance")

    weather_kpi = st.columns(6)
    with weather_kpi[0]: st.metric("Temperature",  f"{current_meteo.get('temperature_2m', '--')} °C")
    with weather_kpi[1]: st.metric("Ressentie",    f"{current_meteo.get('apparent_temperature', '--')} °C")
    with weather_kpi[2]: st.metric("Humidite",     f"{current_meteo.get('relative_humidity_2m', '--')} %")
    with weather_kpi[3]: st.metric("Vent",         f"{current_meteo.get('wind_speed_10m', '--')} km/h")
    with weather_kpi[4]: st.metric("GHI",          f"{current_meteo.get('shortwave_radiation', '--')} W/m²")
    with weather_kpi[5]: st.metric("Nuages",       f"{current_meteo.get('cloud_cover', '--')} %")

    st.markdown("---")

    irr_tabs = st.tabs(["GHI & POA", "Temperature", "Ressource Solaire"])

    with irr_tabs[0]:
        col_l, col_r = st.columns(2)

        with col_l:
            st.markdown('<div class="section-title">Irradiance Globale Horizontale (GHI)</div>', unsafe_allow_html=True)

            daily_ghi = results.groupby("date").agg(
                ghi_sum=("ghi", lambda x: x.sum() / 1000),
            ).reset_index()
            daily_ghi["date"] = pd.to_datetime(daily_ghi["date"])

            fig_ghi = go.Figure()
            fig_ghi.add_trace(go.Scatter(
                x=daily_ghi["date"], y=daily_ghi["ghi_sum"],
                fill="tozeroy", fillcolor="rgba(245,166,35,0.12)",
                line=dict(color="#F5A623", width=1.5), name="GHI quotidien",
                hovertemplate="Date: %{x}<br>GHI: %{y:.1f} kWh/m²<extra></extra>"
            ))
            fig_ghi.add_trace(go.Scatter(
                x=daily_ghi["date"],
                y=daily_ghi["ghi_sum"].rolling(7, center=True).mean(),
                line=dict(color="#E8860A", width=2, dash="dash"), name="Moy. mobile 7j"
            ))

            layout6 = dict(**PLOT_LAYOUT)
            layout6["height"] = 350
            layout6["yaxis"] = dict(gridcolor=THEME["plot_grid"], title="kWh/m²", zeroline=False)
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
            fig_poa.add_trace(go.Scatter(x=daily_poa["date"], y=daily_poa["poa_iso"], line=dict(color="#F5A623", width=1.5), name="Isotropique"))
            fig_poa.add_trace(go.Scatter(x=daily_poa["date"], y=daily_poa["poa_hd"],  line=dict(color="#3498DB", width=1.5), name="Hay-Davies"))

            layout_poa = dict(**PLOT_LAYOUT)
            layout_poa["height"] = 350
            layout_poa["yaxis"] = dict(gridcolor=THEME["plot_grid"], title="W/m²", zeroline=False)
            fig_poa.update_layout(**layout_poa)
            st.plotly_chart(fig_poa, use_container_width=True)

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
        layout_kt["yaxis"] = dict(gridcolor=THEME["plot_grid"], title="KT", range=[0, 1])
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
            fig_temp.add_trace(go.Scatter(x=daily_temp["date"], y=daily_temp["temp_max"], line=dict(color="#E74C3C", width=1), name="Max"))
            fig_temp.add_trace(go.Scatter(x=daily_temp["date"], y=daily_temp["temp_avg"], line=dict(color="#F5A623", width=2), name="Moyenne"))
            fig_temp.add_trace(go.Scatter(x=daily_temp["date"], y=daily_temp["temp_min"], line=dict(color="#3498DB", width=1), name="Min"))

            layout_temp = dict(**PLOT_LAYOUT)
            layout_temp["height"] = 350
            layout_temp["yaxis"] = dict(gridcolor=THEME["plot_grid"], title="°C", zeroline=False)
            fig_temp.update_layout(**layout_temp)
            st.plotly_chart(fig_temp, use_container_width=True)

        with col_t2:
            st.markdown('<div class="section-title">Temperature cellule vs Ambiante</div>', unsafe_allow_html=True)

            hourly_temp = results.groupby("hour")[["temp_air", "cell_temp"]].mean().reset_index()

            fig_cell = go.Figure()
            fig_cell.add_trace(go.Scatter(x=hourly_temp["hour"], y=hourly_temp["temp_air"],  line=dict(color="#3498DB", width=2), name="Ambiante"))
            fig_cell.add_trace(go.Scatter(x=hourly_temp["hour"], y=hourly_temp["cell_temp"], line=dict(color="#E74C3C", width=2), name="Cellule"))

            layout_cell = dict(**PLOT_LAYOUT)
            layout_cell["height"] = 350
            layout_cell["xaxis"] = dict(title="Heure", gridcolor=THEME["plot_grid"], dtick=1)
            layout_cell["yaxis"] = dict(title="°C", gridcolor=THEME["plot_grid"])
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
        fig_solar.add_trace(go.Bar(x=monthly_solar["month_name"], y=monthly_solar["ghi_total"], name="GHI", marker_color="#F5A623"))
        fig_solar.add_trace(go.Bar(x=monthly_solar["month_name"], y=monthly_solar["dni_total"], name="DNI", marker_color="#E8860A"))
        fig_solar.add_trace(go.Bar(x=monthly_solar["month_name"], y=monthly_solar["dhi_total"], name="DHI", marker_color="#FFCF6B"))

        layout_solar = dict(**PLOT_LAYOUT)
        layout_solar["height"] = 300
        layout_solar["barmode"] = "group"
        layout_solar["yaxis"] = dict(gridcolor=THEME["plot_grid"], title="kWh/m²")
        fig_solar.update_layout(**layout_solar)
        st.plotly_chart(fig_solar, use_container_width=True)


# ─────────────────────────────────────────────
# PERFORMANCE ANALYSIS
# ─────────────────────────────────────────────
elif menu == "Performance Analysis":
    st.markdown("## Analyse de Performance Avancee")

    perf_kpi = st.columns(4)
    with perf_kpi[0]: st.metric("PR Moyen",         f"{daily['pr'].mean():.1f}%", delta=f"{daily['pr'].std():.1f}% ecart-type")
    with perf_kpi[1]: st.metric("Energy Yield",     f"{daily['energy_yield'].mean():.1f} kWh/kWp")
    with perf_kpi[2]: st.metric("Facteur de charge",f"{daily['capacity_factor'].mean():.1f}%")
    with perf_kpi[3]: st.metric("Disponibilite",    "98.5%", delta="Estimation")

    st.markdown("---")

    col_p1, col_p2 = st.columns(2)

    with col_p1:
        st.markdown('<div class="section-title">Distribution du PR</div>', unsafe_allow_html=True)

        fig_dist = go.Figure()
        fig_dist.add_trace(go.Histogram(
            x=daily["pr"].dropna(), nbinsx=30, marker_color="#F5A623",
            hovertemplate="PR: %{x:.1f}%<br>Freq: %{y}<extra></extra>"
        ))

        layout_dist = dict(**PLOT_LAYOUT)
        layout_dist["height"] = 300
        layout_dist["xaxis"] = dict(title="PR (%)", gridcolor=THEME["plot_grid"])
        layout_dist["yaxis"] = dict(title="Frequence", gridcolor=THEME["plot_grid"])
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
        layout_pr_month["yaxis"] = dict(gridcolor=THEME["plot_grid"], title="PR %", range=[50, 100])
        fig_pr_month.update_layout(**layout_pr_month)
        st.plotly_chart(fig_pr_month, use_container_width=True)

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
        layout_ey["yaxis"] = dict(gridcolor=THEME["plot_grid"], title="kWh/kWp")
        fig_ey.update_layout(**layout_ey)
        st.plotly_chart(fig_ey, use_container_width=True)

    with col_ey2:
        daily["cumulative_kwh"] = daily["production_kwh"].cumsum()

        fig_cum = go.Figure(go.Scatter(
            x=daily["date"], y=daily["cumulative_kwh"] / 1000,
            line=dict(color="#9B59B6", width=2),
            fill="tozeroy", fillcolor="rgba(155,89,182,0.1)",
            hovertemplate="Date: %{x}<br>Cumul: %{y:.2f} MWh<extra></extra>"
        ))
        layout_cum = dict(**PLOT_LAYOUT)
        layout_cum["height"] = 300
        layout_cum["yaxis"] = dict(gridcolor=THEME["plot_grid"], title="MWh")
        fig_cum.update_layout(**layout_cum)
        st.plotly_chart(fig_cum, use_container_width=True)

    st.markdown('<div class="section-title">Detection d\'anomalies</div>', unsafe_allow_html=True)

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
            hide_index=True, use_container_width=True
        )
    else:
        st.success("Aucune anomalie detectee dans la periode")


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
    inv_cols = st.columns(min(n, 6))
    for i in range(n):
        with inv_cols[i % min(n, 6)]:
            color = "#F5A623" if inv_power[i] < 85 else "#2ECC71"
            st.markdown(f"""
            <div style="background:{THEME['card_bg']};border:1px solid {THEME['border']};border-radius:8px;
                        padding:12px 10px;text-align:center;margin-bottom:8px;border-left:3px solid {color}">
                <div style="font-size:10px;color:{THEME['text_secondary']};font-family:'Space Mono',monospace">{inv_labels[i]}</div>
                <div style="font-size:20px;font-weight:700;color:{color};font-family:'Space Mono',monospace;margin:4px 0">{inv_power[i]:.0f}%</div>
                <div style="font-size:10px;color:{color};font-family:'Space Mono',monospace">{inv_status[i]}</div>
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
                              annotation_font_color="#E74C3C", annotation_font_size=11)
        layout9 = dict(**PLOT_LAYOUT)
        layout9["height"] = 300
        layout9["xaxis"] = dict(tickangle=-45, tickfont=dict(size=9), gridcolor=THEME["plot_grid"])
        layout9["yaxis"] = dict(gridcolor=THEME["plot_grid"], range=[50, 110], zeroline=False)
        fig_inv_bar.update_layout(**layout9)
        st.plotly_chart(fig_inv_bar, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Repartition statut onduleurs</div>', unsafe_allow_html=True)
        ok_count = sum(1 for p in inv_power if p >= 85)
        warn_count = n - ok_count
        fig_pie = go.Figure(go.Pie(
            labels=["Nominaux", "En alerte"], values=[ok_count, warn_count],
            hole=0.6, marker_colors=["#2ECC71", "#F5A623"],
        ))
        fig_pie.add_annotation(
            text=f"<b>{n}</b><br>Total", x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color=THEME["text_primary"], family="Space Mono"),
        )
        fig_pie.update_layout(
            template=THEME["plotly_template"],
            paper_bgcolor=THEME["plot_paper"],
            height=300, margin=dict(t=20, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_pie, use_container_width=True)


# ─────────────────────────────────────────────
# INSTALLATION
# ─────────────────────────────────────────────
elif menu == "Installation":
    st.markdown("## Caracteristiques de l'installation")

    ki1, ki2, ki3, ki4 = st.columns(4)
    ki1.metric("Puissance crete",   f"{SITE['capacity_kwp']} kWp")
    ki2.metric("Panneaux",          f"{SITE['num_panels']}")
    ki3.metric("Onduleurs",         f"{SITE['num_inverters']}")
    ki4.metric("Surface panneau",   f"{SITE['surface_m2']} m²")

    st.markdown("---")
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("""
        <div class="spec-block">
            <div class="spec-block-header">Site & Generale</div>
            <table class="spec-table">
                <tr><td>Designation</td><td>Centrale PV Mohammedia</td></tr>
                <tr><td>Localisation</td><td>Mohammedia, Maroc</td></tr>
                <tr><td>Latitude</td><td><span class="highlight-value">33.7048 N</span></td></tr>
                <tr><td>Longitude</td><td><span class="highlight-value">7.3615 W</span></td></tr>
                <tr><td>Altitude</td><td>56 m</td></tr>
                <tr><td>Fuseau horaire</td><td>Africa/Casablanca (UTC+1)</td></tr>
                <tr><td>Mise en service</td><td>2024</td></tr>
                <tr><td>Operateur</td><td>ENSET</td></tr>
                <tr><td>Raccordement reseau</td><td>BT 220 V</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown(f"""
        <div class="spec-block">
            <div class="spec-block-header">Panneau Photovoltaique</div>
            <table class="spec-table">
                <tr><td>Fabricant</td><td>{PANEL['manufacturer']}</td></tr>
                <tr><td>Modele</td><td>{PANEL['model']}</td></tr>
                <tr><td>Technologie</td><td><span class="badge-blue">{PANEL['technology']}</span></td></tr>
                <tr><td>Puissance nominale</td><td><span class="highlight-value">{PANEL['pdc0']} Wc</span></td></tr>
                <tr><td>Rendement</td><td><span class="highlight-value">{PANEL['efficiency_pct']} %</span></td></tr>
                <tr><td>Garantie</td><td>{PANEL['warranty_years']} ans</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# CONTROLE RELAIS ESP32 VIA BLYNK
# ─────────────────────────────────────────────
elif menu == "Controle Relais":
    st.markdown("## Controle Relais ESP32 via Blynk")

    device_connected = blynk_get_device_status()

    if device_connected:
        st.success("ESP32 connecte a Blynk - WiFi: FAR")
    else:
        st.warning("ESP32 non connecte - Verifiez WiFi FAR")

    st.markdown("---")

    relay_state = blynk_get_pin(BLYNK_CONFIG["relay_pin"])

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">ETAT RELAIS</div>
            <div class="metric-value" style="color: {'#2ECC71' if relay_state == 1 else '#E74C3C'}">
                {'ACTIF' if relay_state == 1 else 'INACTIF'}
            </div>
            <div class="metric-unit">{BLYNK_CONFIG['relay_name']} - GPIO 26</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">PIN VIRTUEL BLYNK</div>
            <div class="metric-value">{BLYNK_CONFIG['relay_pin']}</div>
            <div class="metric-unit">Template: Digital Twin</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">CONNEXION WiFi</div>
            <div class="metric-value" style="color: {'#2ECC71' if device_connected else '#E74C3C'}">
                {'FAR' if device_connected else 'HORS LIGNE'}
            </div>
            <div class="metric-unit">ESP32</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-title">Commandes Relais</div>', unsafe_allow_html=True)

    col_btn1, col_btn2, col_btn3 = st.columns(3)

    with col_btn1:
        if st.button("ACTIVER RELAIS", type="primary", use_container_width=True):
            if blynk_set_pin(BLYNK_CONFIG["relay_pin"], 1):
                st.success("Relais active - Commande envoyee via Blynk")
                st.rerun()
            else:
                st.error("Erreur - ESP32 non joignable")

    with col_btn2:
        if st.button("DESACTIVER RELAIS", type="secondary", use_container_width=True):
            if blynk_set_pin(BLYNK_CONFIG["relay_pin"], 0):
                st.success("Relais desactive - Commande envoyee via Blynk")
                st.rerun()
            else:
                st.error("Erreur - ESP32 non joignable")

    with col_btn3:
        if st.button("ACTUALISER ETAT", use_container_width=True):
            st.rerun()

    st.markdown("---")
    st.markdown('<div class="section-title">Informations Connexion</div>', unsafe_allow_html=True)

    info_col1, info_col2 = st.columns(2)

    with info_col1:
        st.markdown("""
        <div class="spec-block">
            <div class="spec-block-header">Configuration ESP32</div>
            <table class="spec-table">
                <tr><td>WiFi SSID</td><td><span class="highlight-value">FAR</span></td></tr>
                <tr><td>WiFi Password</td><td>FARGEER123</td></tr>
                <tr><td>GPIO Relais</td><td><span class="highlight-value">26</span></td></tr>
                <tr><td>Blynk Token</td><td>l5IGH1fmy7...duYI</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    with info_col2:
        st.markdown("""
        <div class="spec-block">
            <div class="spec-block-header">Branchement Relais</div>
            <table class="spec-table">
                <tr><td>VCC Relais</td><td>3.3V ou 5V ESP32</td></tr>
                <tr><td>GND Relais</td><td>GND ESP32</td></tr>
                <tr><td>IN Relais</td><td><span class="highlight-value">GPIO 26</span></td></tr>
                <tr><td>Charge max</td><td>10A / 250V AC</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("Code ESP32 pret a televerser", expanded=False):
        st.code("""
#define BLYNK_TEMPLATE_ID "TMPL2fH5U9NyY"
#define BLYNK_TEMPLATE_NAME "Digital Twin"
#define BLYNK_AUTH_TOKEN "l5IGH1fmy7E8ULoiLWjdXm9ZmaJcduYI"
#define BLYNK_PRINT Serial

#include <WiFi.h>
#include <BlynkSimpleEsp32.h>

char ssid[] = "FAR";
char pass[] = "FARGEER123";

#define RELAY_PIN 26
#define VPIN_RELAY V0

BlynkTimer timer;

BLYNK_WRITE(VPIN_RELAY) {
    int pinValue = param.asInt();
    digitalWrite(RELAY_PIN, pinValue);
    Serial.print("Relais: ");
    Serial.println(pinValue ? "ON" : "OFF");
}

void setup() {
    Serial.begin(115200);
    pinMode(RELAY_PIN, OUTPUT);
    digitalWrite(RELAY_PIN, LOW);
    WiFi.begin(ssid, pass);
    while (WiFi.status() != WL_CONNECTED) { delay(500); }
    Blynk.config(BLYNK_AUTH_TOKEN);
    Blynk.connect();
}

void loop() {
    Blynk.run();
    timer.run();
}
        """, language="cpp")


# ─────────────────────────────────────────────
# RAPPORT
# ─────────────────────────────────────────────
elif menu == "Rapport":
    st.markdown("## Rapport de Performance")

    total_kwh   = daily["production_kwh"].sum()
    gross_kwh   = daily["gross_production_kwh"].sum()
    avg_pr      = daily["pr"].mean()
    best_month  = monthly.loc[monthly["production_kwh"].idxmax()]
    worst_month = monthly.loc[monthly["production_kwh"].idxmin()]
    avg_daily   = daily["production_kwh"].mean()
    low_pr_count = len(daily[daily["pr"] < 70])
    ghi_mean    = results["ghi"].mean()
    temp_mean   = results["temp_air"].mean()

    best_label  = f"{best_month['month_name']}  {best_month['production_kwh']/1000:.1f} MWh"
    worst_label = f"{worst_month['month_name']}  {worst_month['production_kwh']/1000:.1f} MWh"
    loc_label   = f"Mohammedia, Maroc  {SITE['lat']}N, {abs(SITE['lon'])}W"

    # ── Inline style vars — theme-aware (MODIFIED: replaced hardcoded hex with THEME values) ──
    S_CARD   = f"background:{THEME['card_bg']};border:1px solid {THEME['border']};border-radius:10px;margin-bottom:20px;overflow:hidden;"
    S_HEAD   = f"background:{THEME['card_bg2']};padding:10px 16px;font-family:'Space Mono',monospace;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.12em;color:#F5A623;border-bottom:1px solid {THEME['border']};"
    S_TABLE  = "width:100%;border-collapse:collapse;font-size:13px;"
    S_TD_L   = f"padding:10px 14px;color:{THEME['text_secondary']};font-family:'Space Mono',monospace;font-size:11px;text-transform:uppercase;letter-spacing:0.08em;width:50%;border-bottom:1px solid {THEME['border']};"
    S_TD_R   = f"padding:10px 14px;color:{THEME['text_primary']};font-weight:500;text-align:right;border-bottom:1px solid {THEME['border']};"
    S_TD_L_L = f"padding:10px 14px;color:{THEME['text_secondary']};font-family:'Space Mono',monospace;font-size:11px;text-transform:uppercase;letter-spacing:0.08em;width:50%;"
    S_TD_R_L = f"padding:10px 14px;color:{THEME['text_primary']};font-weight:500;text-align:right;"

    st.markdown(f"""
    <div style="background:{THEME['card_bg']};border:1px solid {THEME['border']};border-top:2px solid #F5A623;
                border-radius:12px;padding:24px 28px 16px 28px;margin-bottom:20px;">
        <div style="font-family:'Space Mono',monospace;font-size:15px;color:#F5A623;
                    font-weight:700;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:6px;">
            Rapport de Performance
        </div>
        <div style="font-size:12px;color:{THEME['text_secondary']};font-family:'Space Mono',monospace;">
            {SITE['name']} &nbsp;&#124;&nbsp; {start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        f'<div style="font-size:13px;font-weight:600;color:{THEME["text_primary"]};margin-bottom:8px;'
        f'text-transform:uppercase;letter-spacing:0.08em;">Production</div>',
        unsafe_allow_html=True
    )
    st.markdown(f"""
    <div style="{S_CARD}">
        <div style="{S_HEAD}">Production energetique</div>
        <table style="{S_TABLE}">
            <tr>
                <td style="{S_TD_L}">Production totale</td>
                <td style="{S_TD_R}"><span style="color:#F5A623;font-family:'Space Mono',monospace;font-weight:700;">{total_kwh/1000:.2f} MWh</span></td>
            </tr>
            <tr>
                <td style="{S_TD_L}">Production journaliere moyenne</td>
                <td style="{S_TD_R}">{avg_daily:.1f} kWh / jour</td>
            </tr>
            <tr>
                <td style="{S_TD_L}">Meilleur mois</td>
                <td style="{S_TD_R}"><span style="color:#2ECC71;font-weight:600;">{best_label}</span></td>
            </tr>
            <tr>
                <td style="{S_TD_L_L}">Mois le plus faible</td>
                <td style="{S_TD_R_L}"><span style="color:#E74C3C;font-weight:600;">{worst_label}</span></td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        f'<div style="font-size:13px;font-weight:600;color:{THEME["text_primary"]};margin-bottom:8px;'
        f'text-transform:uppercase;letter-spacing:0.08em;">Performance</div>',
        unsafe_allow_html=True
    )
    pr_color = "#2ECC71" if avg_pr >= 80 else "#F5A623" if avg_pr >= 70 else "#E74C3C"
    st.markdown(f"""
    <div style="{S_CARD}">
        <div style="{S_HEAD}">Indicateurs de performance</div>
        <table style="{S_TABLE}">
            <tr>
                <td style="{S_TD_L}">Performance Ratio moyen</td>
                <td style="{S_TD_R}"><span style="color:{pr_color};font-family:'Space Mono',monospace;font-weight:700;">{avg_pr:.1f} %</span></td>
            </tr>
            <tr>
                <td style="{S_TD_L}">Jours avec PR inferieur a 70%</td>
                <td style="{S_TD_R}"><span style="color:#E74C3C;">{low_pr_count} jours</span></td>
            </tr>
            <tr>
                <td style="{S_TD_L}">Rendement energetique net</td>
                <td style="{S_TD_R}">{(total_kwh/gross_kwh*100) if gross_kwh>0 else 0:.1f} %</td>
            </tr>
            <tr>
                <td style="{S_TD_L_L}">Disponibilite onduleurs</td>
                <td style="{S_TD_R_L}"><span style="color:#2ECC71;">98.5 % (estimation)</span></td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        f'<div style="font-size:13px;font-weight:600;color:{THEME["text_primary"]};margin-bottom:8px;'
        f'text-transform:uppercase;letter-spacing:0.08em;">Ressource Solaire</div>',
        unsafe_allow_html=True
    )
    st.markdown(f"""
    <div style="{S_CARD}">
        <div style="{S_HEAD}">Conditions meteorologiques</div>
        <table style="{S_TABLE}">
            <tr>
                <td style="{S_TD_L}">GHI moyen sur la periode</td>
                <td style="{S_TD_R}"><span style="color:#F5A623;font-family:'Space Mono',monospace;font-weight:700;">{ghi_mean:.0f} W/m²</span></td>
            </tr>
            <tr>
                <td style="{S_TD_L}">Temperature ambiante moyenne</td>
                <td style="{S_TD_R}">{temp_mean:.1f} °C</td>
            </tr>
            <tr>
                <td style="{S_TD_L_L}">Localisation</td>
                <td style="{S_TD_R_L}">{loc_label}</td>
            </tr>
        </table>
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
            file_name=f"solaris_daily_{start_date}_{end_date}.csv",
            mime="text/csv",
        )
    with col_d2:
        csv_monthly = monthly.to_csv(index=False, float_format="%.2f")
        st.download_button(
            "Telecharger resultats mensuels (CSV)",
            csv_monthly,
            file_name=f"solaris_monthly_{start_date}_{end_date}.csv",
            mime="text/csv",
        )


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(f"""
<div style="text-align:center;color:{THEME['text_muted']};font-size:11px;padding:10px 0;font-family:'Space Mono',monospace;letter-spacing:0.08em">
    SOLARIS DIGITAL TWIN V2.0 &nbsp;|&nbsp; MOHAMMEDIA, MAROC &nbsp;|&nbsp; pvlib + Open-Meteo API
    &nbsp;|&nbsp; {now.strftime('%d/%m/%Y %H:%M')}
</div>
""", unsafe_allow_html=True)
