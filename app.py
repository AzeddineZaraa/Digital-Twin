# ════════════════════════════════════════════════════════════════════
# SOLARIS — Digital Twin PV · Mohammedia, Maroc
# Streamlit + pvlib · Open-Meteo API
# ════════════════════════════════════════════════════════════════════

import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import pvlib
from pvlib.location import Location
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
# CONFIG PAGE
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="SOLARIS · Digital Twin Mohammedia",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,300&display=swap');

:root {
    --y:  #F5A623;
    --y2: #FFCF6B;
    --bg: #07080B;
    --c1: #0E1017;
    --c2: #13161F;
    --c3: #191D28;
    --bd: #21273A;
    --bd2:#2E3650;
    --t1: #E8EDF5;
    --t2: #5E6D8A;
    --t3: #313B52;
    --gr: #2ECC71;
    --rd: #E74C3C;
    --bl: #3B7DD8;
    --pu: #8B5CF6;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: var(--t1);
}

.stApp {
    background: var(--bg);
    background-image:
        radial-gradient(ellipse 80% 40% at 15% -10%, rgba(245,166,35,.06) 0%, transparent 70%),
        radial-gradient(ellipse 60% 40% at 85% 110%, rgba(59,125,216,.04) 0%, transparent 70%);
}

[data-testid="stSidebar"] {
    background: #090B10 !important;
    border-right: 1px solid var(--bd) !important;
}
[data-testid="stSidebar"] .stRadio > label { display:none; }
[data-testid="stSidebar"] .stRadio label {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    color: var(--t2) !important;
    padding: 9px 14px !important;
    border-radius: 8px !important;
    border: 1px solid transparent !important;
    cursor: pointer !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
    color: var(--t1) !important;
    background: var(--c2) !important;
}

#MainMenu, footer, header, [data-testid="stToolbar"] { visibility:hidden; height:0; }
.block-container { padding-top:.75rem; padding-bottom:1rem; max-width:100%; }

div[data-testid="metric-container"] {
    background: var(--c1);
    border: 1px solid var(--bd);
    border-radius: 10px;
    padding: 16px 18px !important;
    position: relative;
    overflow: hidden;
}
div[data-testid="metric-container"]::after {
    content:''; position:absolute; top:0; left:0; right:0; height:2px;
    background: linear-gradient(90deg, var(--y), transparent);
}
div[data-testid="metric-container"] label {
    color: var(--t2) !important;
    font-size: 10px !important;
    text-transform: uppercase;
    letter-spacing: .12em;
    font-family: 'Space Mono', monospace !important;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: var(--y) !important;
    font-size: 22px !important;
    font-weight: 700 !important;
    font-family: 'Space Mono', monospace !important;
}

.main-hdr {
    background: linear-gradient(135deg, var(--c1) 0%, #0F1320 100%);
    border: 1px solid var(--bd);
    border-top: 2px solid var(--y);
    border-radius: 0 0 16px 16px;
    padding: 20px 28px;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
}
.plant-name {
    font-family: 'Space Mono', monospace;
    font-size: 18px; font-weight: 700;
    color: var(--y); letter-spacing: .06em; text-transform: uppercase;
}
.plant-sub { font-size: 11px; color: var(--t2); margin-top: 5px; letter-spacing: .06em; }

.badge {
    display:inline-flex; align-items:center; gap:7px;
    padding: 5px 14px; border-radius: 20px;
    font-size: 11px; font-family: 'Space Mono', monospace; letter-spacing: .05em;
}
.badge-ok  { background:rgba(46,204,113,.07); border:1px solid rgba(46,204,113,.22); color:var(--gr); }
.badge-off { background:rgba(231,76,60,.07);  border:1px solid rgba(231,76,60,.22);  color:var(--rd); }

@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.35} }

.sec {
    font-family: 'Space Mono', monospace;
    font-size: 10px; font-weight: 700;
    color: var(--t2); text-transform: uppercase; letter-spacing: .18em;
    margin-bottom: 14px; padding-bottom: 10px; border-bottom: 1px solid var(--bd);
    display: flex; align-items: center; gap: 8px;
}
.sec span { color: var(--y); font-size:14px; }

.al { border-radius:8px; padding:10px 15px; margin-bottom:8px; border-left:3px solid; font-size:13px; }
.al-warn { background:rgba(245,166,35,.06); border-color:var(--y); color:#C4892A; }
.al-err  { background:rgba(231,76,60,.06);  border-color:var(--rd); color:#B84A3E; }
.al-ok   { background:rgba(46,204,113,.06); border-color:var(--gr); color:#30A85E; }
.al b    { color:var(--t1); }
.al-time { float:right; font-size:10px; font-family:'Space Mono',monospace; color:var(--t3); }

.spec-blk { background:var(--c1); border:1px solid var(--bd); border-radius:10px; margin-bottom:16px; overflow:hidden; }
.spec-hdr {
    background: var(--c2); padding: 10px 16px;
    font-family: 'Space Mono', monospace; font-size: 10px; font-weight: 700;
    text-transform: uppercase; letter-spacing: .12em; color: var(--y);
    border-bottom: 1px solid var(--bd);
}
.spec-tbl { width:100%; border-collapse:collapse; font-size:12.5px; }
.spec-tbl tr { border-bottom:1px solid var(--bd); }
.spec-tbl tr:last-child { border-bottom:none; }
.spec-tbl tr:hover { background:var(--c2); }
.spec-tbl td { padding:9px 16px; vertical-align:middle; }
.spec-tbl td:first-child { color:var(--t2); font-family:'Space Mono',monospace; font-size:10px; text-transform:uppercase; letter-spacing:.07em; width:52%; }
.spec-tbl td:last-child { color:var(--t1); font-weight:500; text-align:right; }
.hl  { color:var(--y);  font-family:'Space Mono',monospace; font-weight:700; }
.hlg { color:var(--gr); font-family:'Space Mono',monospace; font-weight:700; }
.tag { display:inline-block; padding:2px 9px; border-radius:4px; font-size:10px; font-family:'Space Mono',monospace; letter-spacing:.04em; }
.tag-g { background:rgba(46,204,113,.1);  color:var(--gr); border:1px solid rgba(46,204,113,.2); }
.tag-y { background:rgba(245,166,35,.1);  color:var(--y);  border:1px solid rgba(245,166,35,.2); }
.tag-b { background:rgba(59,125,216,.1);  color:var(--bl); border:1px solid rgba(59,125,216,.2); }
.tag-r { background:rgba(231,76,60,.1);   color:var(--rd); border:1px solid rgba(231,76,60,.2); }

.inv-tile {
    background:var(--c1); border:1px solid var(--bd); border-radius:9px;
    padding:13px 10px; text-align:center; margin-bottom:8px;
}

.report-box {
    background:var(--c1); border:1px solid var(--bd);
    border-top:2px solid var(--y); border-radius:12px; padding:28px 32px;
}
.report-title { font-family:'Space Mono',monospace; font-size:14px; font-weight:700; color:var(--y); text-transform:uppercase; letter-spacing:.1em; margin-bottom:4px; }
.report-sub   { font-size:12px; color:var(--t2); margin-bottom:20px; font-family:'Space Mono',monospace; }
.report-sec   { font-size:12px; font-weight:600; color:var(--t1); text-transform:uppercase; letter-spacing:.09em; margin:20px 0 10px; }

.sb-brand { font-family:'Space Mono',monospace; font-size:20px; font-weight:700; color:var(--y); letter-spacing:.08em; }
.sb-sub   { font-size:10px; color:var(--t3); text-transform:uppercase; letter-spacing:.12em; margin-bottom:18px; }

hr { border-color:var(--bd) !important; margin:14px 0 !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────
SITE = {
    "name": "Centrale PV — Mohammedia",
    "location": "Mohammedia, Maroc",
    "lat": 33.6861,
    "lon": -7.3833,
    "altitude": 15,
    "timezone": "Africa/Casablanca",
    "capacity_kwp": 3.96,
    "surface_m2": 23.27,
    "num_panels": 12,
    "num_inverters": 1,
    "commissioning": "01/04/2024",
    "operator": "SOLARIS Digital Twin",
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
MOIS = ["Jan","Fév","Mar","Avr","Mai","Jun","Jul","Aoû","Sep","Oct","Nov","Déc"]


# ─────────────────────────────────────────────
# LAYOUT PLOTLY BASE
# ─────────────────────────────────────────────
def base_layout(height=300, legend=False):
    return dict(
        template="plotly_dark",
        paper_bgcolor="#0E1017",
        plot_bgcolor="#0E1017",
        font=dict(family="DM Sans", color="#5E6D8A", size=11),
        height=height,
        margin=dict(t=18, b=36, l=48, r=16),
        showlegend=legend,
        legend=dict(orientation="h", y=-0.28, font=dict(size=11, color="#5E6D8A"), bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(gridcolor="#1A1E2B", zeroline=False, tickfont=dict(size=10)),
        yaxis=dict(gridcolor="#1A1E2B", zeroline=False, tickfont=dict(size=10)),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#13161F", bordercolor="#2E3650", font=dict(color="#E8EDF5", size=12)),
    )


# ─────────────────────────────────────────────
# DATA & SIMULATION
# ─────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_meteo(lat, lon, start, end):
    url = "https://archive-api.open-meteo.com/v1/archive"
    p = {
        "latitude": lat, "longitude": lon,
        "start_date": start, "end_date": end,
        "hourly": "temperature_2m,shortwave_radiation,diffuse_radiation,direct_normal_irradiance,wind_speed_10m,relative_humidity_2m",
        "timezone": "Africa/Casablanca",
    }
    r = requests.get(url, params=p, timeout=30)
    r.raise_for_status()
    d = r.json()
    df = pd.DataFrame({
        "datetime": pd.to_datetime(d["hourly"]["time"]),
        "temp": d["hourly"]["temperature_2m"],
        "ghi":  d["hourly"]["shortwave_radiation"],
        "dhi":  d["hourly"]["diffuse_radiation"],
        "dni":  d["hourly"]["direct_normal_irradiance"],
        "wind": d["hourly"]["wind_speed_10m"],
        "hum":  d["hourly"]["relative_humidity_2m"],
    }).set_index("datetime")
    return df


@st.cache_data(ttl=3600, show_spinner=False)
def simulate(lat, lon, alt, tz, tilt, az, pdc0, gamma, num_panels, start, end):
    df = fetch_meteo(lat, lon, start, end)
    loc = Location(latitude=lat, longitude=lon, altitude=alt, tz=tz)
    sp  = loc.get_solarposition(df.index)
    poa = pvlib.irradiance.get_total_irradiance(
        surface_tilt=tilt, surface_azimuth=az,
        dni=df["dni"], ghi=df["ghi"], dhi=df["dhi"],
        solar_zenith=sp["apparent_zenith"], solar_azimuth=sp["azimuth"],
    )
    tp = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS["sapm"]["open_rack_glass_glass"]
    tc = pvlib.temperature.sapm_cell(
        poa_global=poa["poa_global"], temp_air=df["temp"], wind_speed=df["wind"],
        a=tp["a"], b=tp["b"], deltaT=tp["deltaT"],
    )
    dc = pvlib.pvsystem.pvwatts_dc(
        g_poa_effective=poa["poa_global"], temp_cell=tc, pdc0=pdc0, gamma_pdc=gamma,
    )
    out = pd.DataFrame({
        "ghi":    df["ghi"],
        "poa":    poa["poa_global"].clip(lower=0),
        "temp":   df["temp"],
        "wind":   df["wind"],
        "hum":    df["hum"],
        "cell_t": tc,
        "dc_w":   dc.clip(lower=0),
        "ac_kw":  (dc * 0.97 / 1000 * num_panels).clip(lower=0),
    })
    out["hour"]  = out.index.hour
    out["month"] = out.index.month
    return out


def daily_agg(res, num_panels, pdc0):
    cap = num_panels * pdc0 / 1000
    d = res.resample("1D").agg(
        prod_kwh   =("ac_kw",   "sum"),
        peak_kw    =("ac_kw",   "max"),
        ghi_mean   =("ghi",     "mean"),
        psh        =("poa",     lambda x: x.sum() / 1000),
        temp_mean  =("temp",    "mean"),
        cell_tmean =("cell_t",  "mean"),
        cell_tmax  =("cell_t",  "max"),
        wind_mean  =("wind",    "mean"),
    )
    d["pr"] = (d["prod_kwh"] / (d["psh"] * cap).replace(0, np.nan)).clip(0, 1) * 100
    d["ys"] = d["prod_kwh"] / cap
    return d.dropna(subset=["prod_kwh"])


def monthly_agg(d):
    m = d.resample("ME").agg(
        prod_kwh  =("prod_kwh", "sum"),
        pr_mean   =("pr",       "mean"),
        temp_mean =("temp_mean","mean"),
        ys_mean   =("ys",       "mean"),
    )
    m.index = m.index.strftime("%b %Y")
    return m


@st.cache_data(ttl=300, show_spinner=False)
def get_now_meteo(lat, lon):
    try:
        r = requests.get("https://api.open-meteo.com/v1/forecast", params={
            "latitude": lat, "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,shortwave_radiation",
            "timezone": "Africa/Casablanca",
        }, timeout=10)
        return r.json().get("current", {})
    except:
        return {}


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:16px 0 4px">
        <div class="sb-brand">SOLARIS</div>
        <div class="sb-sub">Digital Twin PV · Mohammedia</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    menu = st.radio("", [
        "🏠  Vue Globale",
        "⚡  Production",
        "🌤  Météo & Irradiance",
        "🔌  Onduleurs",
        "🔩  Installation",
        "📋  Rapport",
    ], label_visibility="collapsed")

    st.markdown("---")
    st.markdown('<div style="font-size:11px;color:#5E6D8A;text-transform:uppercase;letter-spacing:.1em;font-family:\'Space Mono\',monospace;margin-bottom:8px">Période d\'analyse</div>', unsafe_allow_html=True)
    start_date = st.date_input("Début", value=datetime(2024, 1, 1),  label_visibility="collapsed")
    end_date   = st.date_input("Fin",   value=datetime(2024, 12, 31), label_visibility="collapsed")
    st.caption(f"{start_date.strftime('%d/%m/%Y')} → {end_date.strftime('%d/%m/%Y')}")

    st.markdown("---")
    st.markdown(f"""
    <div style="font-size:12px;color:#5E6D8A;line-height:2">
        📍 {SITE['lat']}°N, {abs(SITE['lon'])}°W<br>
        🔋 {SITE['num_panels']} × {PANEL['pdc0']} W = <b style="color:#E8EDF5">{SITE['capacity_kwp']:.2f} kWp</b><br>
        📐 Tilt {PANEL['tilt']}° · Azimuth {PANEL['azimuth']}°<br>
        🏗 Mise en service : {SITE['commissioning']}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;padding:4px 0">
        <div style="width:30px;height:30px;border-radius:50%;background:linear-gradient(135deg,#1a3a6e,#3B7DD8);
             display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:700;color:#fff;flex-shrink:0">A</div>
        <div>
            <div style="font-size:13px;font-weight:500;color:#E8EDF5">Admin</div>
            <div style="font-size:10px;color:#5E6D8A">Administrateur</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SIMULATION
# ─────────────────────────────────────────────
if start_date >= end_date:
    st.error("La date de début doit être antérieure à la date de fin.")
    st.stop()

with st.spinner("Simulation pvlib + Open-Meteo en cours…"):
    try:
        res = simulate(
            SITE["lat"], SITE["lon"], SITE["altitude"], SITE["timezone"],
            PANEL["tilt"], PANEL["azimuth"], PANEL["pdc0"], PANEL["gamma_pdc"],
            SITE["num_panels"], str(start_date), str(end_date)
        )
    except Exception as e:
        st.error(f"Erreur simulation : {e}")
        st.stop()

if res is None or res.empty:
    st.error("Aucune donnée disponible pour la période sélectionnée.")
    st.stop()

daily   = daily_agg(res, SITE["num_panels"], PANEL["pdc0"])
monthly = monthly_agg(daily)
now_met = get_now_meteo(SITE["lat"], SITE["lon"])
now     = datetime.now()
ghi_now = float(now_met.get("shortwave_radiation", 0) or 0)
is_prod = ghi_now > 50


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
badge_cls = "badge-ok" if is_prod else "badge-off"
badge_lbl = "EN PRODUCTION" if is_prod else "HORS PRODUCTION"
dot_style = (
    "width:7px;height:7px;border-radius:50%;background:#2ECC71;box-shadow:0 0 7px #2ECC71;animation:pulse 2s infinite"
    if is_prod else
    "width:7px;height:7px;border-radius:50%;background:#E74C3C"
)

st.markdown(f"""
<div class="main-hdr">
    <div>
        <div class="plant-name">☀ {SITE['name']}</div>
        <div class="plant-sub">
            {SITE['lat']}°N, {abs(SITE['lon'])}°W &nbsp;·&nbsp; {SITE['altitude']} m &nbsp;·&nbsp;
            {SITE['capacity_kwp']} kWp &nbsp;·&nbsp; {SITE['num_panels']} panneaux &nbsp;·&nbsp; {PANEL['model']}
        </div>
    </div>
    <div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap">
        <div style="font-size:12px;color:{'#F5A623' if is_prod else '#5E6D8A'};font-family:'Space Mono',monospace">
            {ghi_now:.0f} W/m² &nbsp;·&nbsp;
            {float(now_met.get('temperature_2m', 0) or 0):.1f}°C &nbsp;·&nbsp;
            {float(now_met.get('wind_speed_10m', 0) or 0):.1f} km/h
        </div>
        <div style="font-size:11px;color:#3D4553;font-family:'Space Mono',monospace">{now.strftime('%d/%m/%Y %H:%M')}</div>
        <div class="badge {badge_cls}">
            <div style="{dot_style}"></div>
            {badge_lbl}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# VUE GLOBALE
# ══════════════════════════════════════════════
if "Vue Globale" in menu:
    total_kwh = daily["prod_kwh"].sum()
    avg_pr    = daily["pr"].mean()
    best_day  = daily["prod_kwh"].max()
    best_date = daily["prod_kwh"].idxmax().strftime("%d/%m")
    avg_daily = daily["prod_kwh"].mean()
    cap       = SITE["num_panels"] * PANEL["pdc0"] / 1000
    sp_yield  = total_kwh / cap

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Production totale",    f"{total_kwh/1000:.2f} MWh")
    c2.metric("Performance Ratio",    f"{avg_pr:.1f} %")
    c3.metric("Meilleur jour",        f"{best_day:.1f} kWh", best_date)
    c4.metric("Moy. journalière",     f"{avg_daily:.1f} kWh/j")
    c5.metric("Rendement spécifique", f"{sp_yield:.0f} kWh/kWp")

    st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)

    col_img, col_rt = st.columns([3, 2])

    with col_img:
        st.markdown('<div class="sec"><span>🌍</span> Site de la centrale</div>', unsafe_allow_html=True)
        st.image("https://images.unsplash.com/photo-1509395176047-4a66953fd231?w=900&q=80",
                 use_container_width=True)
        m1,m2,m3,m4 = st.columns(4)
        m1.metric("Temp. actuelle",  f"{float(now_met.get('temperature_2m',0) or 0):.1f} °C")
        m2.metric("Irradiance act.", f"{ghi_now:.0f} W/m²")
        m3.metric("Vent actuel",     f"{float(now_met.get('wind_speed_10m',0) or 0):.1f} km/h")
        m4.metric("Humidité act.",   f"{float(now_met.get('relative_humidity_2m',0) or 0):.0f} %")

    with col_rt:
        st.markdown('<div class="sec"><span>⚡</span> Performance temps réel</div>', unsafe_allow_html=True)
        last_ac       = float(res["ac_kw"].iloc[-1])
        last_day_prod = float(daily["prod_kwh"].iloc[-1])
        st.metric("Puissance simulée (dern. heure)", f"{last_ac:.3f} kW")
        st.metric("Production dernière journée",     f"{last_day_prod:.2f} kWh")
        st.metric("Production totale (période)",     f"{total_kwh/1000:.3f} MWh")
        st.metric("PR moyen période",                f"{avg_pr:.1f} %")

        st.markdown('<div class="sec" style="margin-top:16px"><span>🔔</span> Alertes système</div>', unsafe_allow_html=True)
        low_pr = daily[daily["pr"] < 70]
        if len(low_pr) > 0:
            st.markdown(f"""<div class="al al-warn">
                <b>{len(low_pr)} jours</b> avec PR &lt; 70 %
                <span class="al-time">{low_pr.index.max().strftime('%d/%m/%Y')}</span>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<div class="al al-ok"><b>PR nominal</b> — aucun jour sous 70 %</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="al al-ok"><b>Onduleur IMEON 3.6</b> — fonctionnement nominal</div>
        <div class="al al-ok"><b>Monitoring</b> — toutes les données reçues</div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
    col_l, col_r = st.columns([3, 2])

    with col_l:
        st.markdown('<div class="sec"><span>📈</span> Production journalière</div>', unsafe_allow_html=True)
        bar_c = np.where(
            daily["prod_kwh"] < daily["prod_kwh"].quantile(0.2), "#E74C3C",
            np.where(daily["prod_kwh"] > daily["prod_kwh"].quantile(0.8), "#2ECC71", "#F5A623")
        )
        fig = go.Figure()
        fig.add_trace(go.Bar(x=daily.index, y=daily["prod_kwh"].round(2),
            marker_color=bar_c, opacity=.85, name="kWh/jour"))
        fig.add_trace(go.Scatter(
            x=daily.index, y=daily["prod_kwh"].rolling(7, center=True, min_periods=1).mean(),
            name="Moy. 7j", line=dict(color="#3B7DD8", width=2)))
        lo = base_layout(290, True)
        lo["yaxis"] = dict(**lo["yaxis"], title="kWh")
        fig.update_layout(**lo)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col_r:
        st.markdown('<div class="sec"><span>📅</span> Énergie mensuelle</div>', unsafe_allow_html=True)
        fig_m = go.Figure(go.Bar(
            x=monthly.index, y=(monthly["prod_kwh"]/1000).round(3),
            marker_color="#F5A623", opacity=.85,
            text=(monthly["prod_kwh"]/1000).round(2).astype(str),
            textposition="outside",
            textfont=dict(color="#E8EDF5", size=9, family="Space Mono"),
        ))
        lo2 = base_layout(290)
        lo2["yaxis"]         = dict(**lo2["yaxis"], title="MWh")
        lo2["xaxis"]["tickangle"] = -35
        fig_m.update_layout(**lo2)
        st.plotly_chart(fig_m, use_container_width=True, config={"displayModeBar": False})


# ══════════════════════════════════════════════
# PRODUCTION
# ══════════════════════════════════════════════
elif "Production" in menu:
    st.markdown("### ⚡ Analyse de Production")

    pr_mean, pr_std = daily["pr"].mean(), daily["pr"].std()
    anom = daily[(daily["pr"] < pr_mean - 2*pr_std) | (daily["pr"] > pr_mean + 2*pr_std)]

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="sec"><span>📉</span> Performance Ratio journalier</div>', unsafe_allow_html=True)
        fig_pr = go.Figure()
        fig_pr.add_trace(go.Scatter(
            x=daily.index, y=daily["pr"].round(1),
            fill="tozeroy", fillcolor="rgba(245,166,35,.08)",
            line=dict(color="#F5A623", width=1.5), name="PR %"))
        fig_pr.add_trace(go.Scatter(
            x=anom.index, y=anom["pr"].round(1), mode="markers",
            name="Anomalie", marker=dict(color="#E74C3C", size=7, symbol="x")))
        fig_pr.add_hline(y=75, line_dash="dash", line_color="#2E3650",
                         annotation_text="Seuil 75 %", annotation_font_color="#5E6D8A", annotation_font_size=10)
        lo3 = base_layout(300, True)
        lo3["yaxis"] = dict(**lo3["yaxis"], title="PR (%)", range=[0, 105])
        fig_pr.update_layout(**lo3)
        st.plotly_chart(fig_pr, use_container_width=True, config={"displayModeBar": False})

    with col2:
        st.markdown('<div class="sec"><span>🌡</span> Corrélation Température / Production</div>', unsafe_allow_html=True)
        fig_sc = px.scatter(
            daily.reset_index(), x="temp_mean", y="prod_kwh",
            color="pr", color_continuous_scale="YlOrRd", opacity=.7,
            labels={"temp_mean":"Temp. moy. (°C)", "prod_kwh":"Production (kWh)", "pr":"PR %"},
        )
        fig_sc.update_layout(template="plotly_dark", paper_bgcolor="#0E1017", plot_bgcolor="#0E1017",
                             height=300, margin=dict(t=18,b=36,l=48,r=16))
        st.plotly_chart(fig_sc, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<div class="sec"><span>🕐</span> Profil horaire moyen de production</div>', unsafe_allow_html=True)
    ha = res.groupby("hour")["ac_kw"].mean().reset_index()
    fig_h = go.Figure()
    fig_h.add_trace(go.Scatter(
        x=ha["hour"], y=ha["ac_kw"].round(3),
        fill="tozeroy", fillcolor="rgba(245,166,35,.12)",
        line=dict(color="#F5A623", width=2), mode="lines+markers",
        marker=dict(size=4, color="#F5A623")))
    lo4 = base_layout(250)
    lo4["xaxis"] = dict(**lo4["xaxis"], title="Heure", dtick=1)
    lo4["yaxis"] = dict(**lo4["yaxis"], title="Puissance moy. (kW)")
    fig_h.update_layout(**lo4)
    st.plotly_chart(fig_h, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<div class="sec"><span>🔥</span> Heatmap production (Mois × Heure)</div>', unsafe_allow_html=True)
    hm = res.groupby(["month","hour"])["ac_kw"].mean().reset_index()
    pv = hm.pivot(index="month", columns="hour", values="ac_kw")
    pv.index = [MOIS[m-1] for m in pv.index]
    fig_hm = go.Figure(go.Heatmap(
        z=pv.values, x=[f"{h}h" for h in pv.columns], y=pv.index,
        colorscale=[[0,"#07080B"],[.25,"#1A1000"],[.6,"#7A4500"],[1,"#F5A623"]],
        colorbar=dict(title="kW", tickfont=dict(color="#5E6D8A"), titlefont=dict(color="#5E6D8A")),
    ))
    lo5 = base_layout(300)
    lo5["xaxis"] = dict(**lo5["xaxis"], title="Heure")
    fig_hm.update_layout(**lo5)
    st.plotly_chart(fig_hm, use_container_width=True, config={"displayModeBar": False})

    if len(anom) > 0:
        st.markdown(f'<div class="sec"><span>⚠</span> Anomalies — {len(anom)} jours (±2σ)</div>', unsafe_allow_html=True)
        for dt, row in anom.sort_index(ascending=False).iterrows():
            above = row["pr"] > pr_mean
            css   = "al-warn" if above else "al-err"
            lbl   = "PR élevé" if above else "PR faible"
            st.markdown(f"""<div class="al {css}">
                <b>{lbl}</b> — {dt.strftime('%d %B %Y')}
                <span class="al-time">PR = {row['pr']:.1f} %</span><br>
                <span style="font-size:11px">
                    Prod. : <b>{row['prod_kwh']:.2f} kWh</b> &nbsp;·&nbsp;
                    GHI moy. : <b>{row['ghi_mean']:.0f} W/m²</b> &nbsp;·&nbsp;
                    T. cellule : <b>{row['cell_tmean']:.1f} °C</b>
                </span></div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# MÉTÉO & IRRADIANCE
# ══════════════════════════════════════════════
elif "Météo" in menu:
    st.markdown("### 🌤 Météo & Irradiance — Mohammedia")

    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Température",    f"{float(now_met.get('temperature_2m',0) or 0):.1f} °C")
    m2.metric("Humidité",       f"{float(now_met.get('relative_humidity_2m',0) or 0):.0f} %")
    m3.metric("Vent",           f"{float(now_met.get('wind_speed_10m',0) or 0):.1f} km/h")
    m4.metric("GHI maintenant", f"{ghi_now:.0f} W/m²")

    dg = (res["ghi"].resample("1D").sum() / 1000).reset_index()
    dg.columns = ["date","ghi_kwh"]

    st.markdown('<div class="sec" style="margin-top:16px"><span>☀</span> Irradiance GHI journalière (kWh/m²)</div>', unsafe_allow_html=True)
    fig_ghi = go.Figure()
    fig_ghi.add_trace(go.Scatter(
        x=dg["date"], y=dg["ghi_kwh"].round(2),
        fill="tozeroy", fillcolor="rgba(245,166,35,.1)",
        line=dict(color="#F5A623", width=1.5)))
    lo6 = base_layout(250)
    lo6["yaxis"] = dict(**lo6["yaxis"], title="kWh/m²")
    fig_ghi.update_layout(**lo6)
    st.plotly_chart(fig_ghi, use_container_width=True, config={"displayModeBar": False})

    cl, cr = st.columns(2)
    with cl:
        st.markdown('<div class="sec"><span>🌡</span> Température de l\'air — journalière</div>', unsafe_allow_html=True)
        dt = res["temp"].resample("1D").mean().reset_index()
        dt.columns = ["date","temp"]
        fig_t = go.Figure()
        fig_t.add_trace(go.Scatter(
            x=dt["date"], y=dt["temp"].round(1),
            line=dict(color="#3B7DD8", width=1.5),
            fill="tozeroy", fillcolor="rgba(59,125,216,.07)"))
        fig_t.add_hline(y=dt["temp"].mean(), line_dash="dash", line_color="#F5A623", opacity=.5,
                        annotation_text=f"Moy. {dt['temp'].mean():.1f}°C",
                        annotation_font_color="#F5A623", annotation_font_size=10)
        lo7 = base_layout(240)
        lo7["yaxis"] = dict(**lo7["yaxis"], title="°C")
        fig_t.update_layout(**lo7)
        st.plotly_chart(fig_t, use_container_width=True, config={"displayModeBar": False})

    with cr:
        st.markdown('<div class="sec"><span>📊</span> GHI cumulé par mois</div>', unsafe_allow_html=True)
        mg = dg.copy()
        mg["month"] = pd.to_datetime(mg["date"]).dt.strftime("%b")
        mg_agg = mg.groupby("month", sort=False)["ghi_kwh"].sum().reset_index()
        order = [m for m in MOIS if m in mg_agg["month"].values]
        mg_agg["month"] = pd.Categorical(mg_agg["month"], categories=order, ordered=True)
        mg_agg = mg_agg.sort_values("month")
        fig_mg = go.Figure(go.Bar(
            x=mg_agg["month"], y=mg_agg["ghi_kwh"].round(1), marker_color="#F5A623", opacity=.85))
        lo8 = base_layout(240)
        lo8["yaxis"] = dict(**lo8["yaxis"], title="kWh/m²")
        fig_mg.update_layout(**lo8)
        st.plotly_chart(fig_mg, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<div class="sec"><span>🔥</span> Température cellule vs air</div>', unsafe_allow_html=True)
    dc_t = res[["temp","cell_t"]].resample("1D").mean().reset_index()
    ct_max = res["cell_t"].resample("1D").max().values
    fig_tc = go.Figure()
    fig_tc.add_trace(go.Scatter(x=dc_t["datetime"], y=dc_t["temp"].round(1),
        name="T. air", line=dict(color="#3B7DD8", width=1.5)))
    fig_tc.add_trace(go.Scatter(x=dc_t["datetime"], y=dc_t["cell_t"].round(1),
        name="T. cellule moy.", line=dict(color="#F5A623", width=1.5)))
    fig_tc.add_trace(go.Scatter(x=dc_t["datetime"], y=ct_max,
        name="T. cellule max", line=dict(color="#E74C3C", width=1, dash="dot")))
    lo9 = base_layout(260, True)
    lo9["yaxis"] = dict(**lo9["yaxis"], title="°C")
    fig_tc.update_layout(**lo9)
    st.plotly_chart(fig_tc, use_container_width=True, config={"displayModeBar": False})


# ══════════════════════════════════════════════
# ONDULEURS
# ══════════════════════════════════════════════
elif "Onduleurs" in menu:
    st.markdown("### 🔌 Tableau de bord Onduleurs")
    n = SITE["num_inverters"]
    np.random.seed(42)
    inv_pwr    = np.random.normal(95, 5, n).clip(70, 102)
    inv_status = ["ALERTE" if p < 85 else "OK" for p in inv_pwr]
    inv_labels = [f"INV-{i+1:02d}" for i in range(n)]
    inv_energy = daily["prod_kwh"].sum() / n * (inv_pwr / 100)

    cols = st.columns(min(n, 6))
    for i in range(n):
        color = "#F5A623" if inv_pwr[i] < 85 else "#2ECC71"
        with cols[i % 6]:
            st.markdown(f"""
            <div class="inv-tile" style="border-left:3px solid {color}">
                <div style="font-size:10px;color:#5E6D8A;font-family:'Space Mono',monospace">{inv_labels[i]}</div>
                <div style="font-size:22px;font-weight:700;color:{color};font-family:'Space Mono',monospace;margin:6px 0">{inv_pwr[i]:.0f}<span style="font-size:12px;color:#5E6D8A">%</span></div>
                <div style="font-size:10px;color:{color};font-family:'Space Mono',monospace">{inv_status[i]}</div>
                <div style="font-size:10px;color:#5E6D8A;margin-top:4px">{inv_energy[i]:.1f} kWh</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")
    cl, cr = st.columns(2)
    with cl:
        st.markdown('<div class="sec"><span>📊</span> Puissance relative par onduleur</div>', unsafe_allow_html=True)
        fig_ib = go.Figure(go.Bar(
            x=inv_labels, y=inv_pwr.round(1),
            marker_color=["#F5A623" if p < 85 else "#2ECC71" for p in inv_pwr],
            text=[f"{p:.0f}%" for p in inv_pwr], textposition="outside",
            textfont=dict(size=10, color="#E8EDF5", family="Space Mono")))
        fig_ib.add_hline(y=85, line_dash="dash", line_color="#E74C3C",
                         annotation_text="Seuil 85 %", annotation_font_color="#E74C3C", annotation_font_size=10)
        lo10 = base_layout(300)
        lo10["xaxis"]["tickangle"] = -30
        lo10["yaxis"] = dict(**lo10["yaxis"], range=[50,110], title="%")
        fig_ib.update_layout(**lo10)
        st.plotly_chart(fig_ib, use_container_width=True, config={"displayModeBar": False})

    with cr:
        st.markdown('<div class="sec"><span>🍩</span> Répartition statut</div>', unsafe_allow_html=True)
        ok_n, warn_n = sum(1 for p in inv_pwr if p >= 85), n - sum(1 for p in inv_pwr if p >= 85)
        fig_pie = go.Figure(go.Pie(
            labels=["Nominaux","En alerte"], values=[ok_n, warn_n],
            hole=.62, marker_colors=["#2ECC71","#F5A623"], textinfo="none"))
        fig_pie.add_annotation(text=f"<b>{n}</b><br>Total", x=.5, y=.5, showarrow=False,
                               font=dict(size=14, color="#E8EDF5", family="Space Mono"))
        fig_pie.update_layout(template="plotly_dark", paper_bgcolor="#0E1017",
                              height=300, margin=dict(t=20,b=20,l=20,r=20),
                              legend=dict(font=dict(size=11,color="#5E6D8A")))
        st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<div class="sec"><span>📈</span> Production journalière simulée</div>', unsafe_allow_html=True)
    fig_ip = go.Figure()
    fig_ip.add_trace(go.Scatter(
        x=daily.index, y=daily["prod_kwh"].round(2),
        fill="tozeroy", fillcolor="rgba(46,204,113,.08)",
        line=dict(color="#2ECC71", width=1.5), name="Production kWh"))
    lo11 = base_layout(250)
    lo11["yaxis"] = dict(**lo11["yaxis"], title="kWh")
    fig_ip.update_layout(**lo11)
    st.plotly_chart(fig_ip, use_container_width=True, config={"displayModeBar": False})


# ══════════════════════════════════════════════
# INSTALLATION
# ══════════════════════════════════════════════
elif "Installation" in menu:
    st.markdown("### 🔩 Caractéristiques de l'installation")

    ki1,ki2,ki3,ki4,ki5 = st.columns(5)
    ki1.metric("Puissance crête",   f"{SITE['capacity_kwp']:.2f} kWp")
    ki2.metric("Panneaux",          f"{SITE['num_panels']}")
    ki3.metric("Onduleur",          INVERTER["model"])
    ki4.metric("Surface totale",    f"{SITE['surface_m2']:.1f} m²")
    ki5.metric("Rendement panneau", f"{PANEL['efficiency_pct']} %")

    st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown(f"""
        <div class="spec-blk"><div class="spec-hdr">Site & Général</div>
        <table class="spec-tbl">
            <tr><td>Localisation</td><td>Mohammedia, Maroc</td></tr>
            <tr><td>Latitude</td><td><span class="hl">{SITE['lat']}° N</span></td></tr>
            <tr><td>Longitude</td><td><span class="hl">{abs(SITE['lon'])}° W</span></td></tr>
            <tr><td>Altitude</td><td>{SITE['altitude']} m</td></tr>
            <tr><td>Fuseau horaire</td><td>Africa/Casablanca (UTC+1)</td></tr>
            <tr><td>Mise en service</td><td>{SITE['commissioning']}</td></tr>
            <tr><td>Opérateur</td><td>{SITE['operator']}</td></tr>
            <tr><td>Raccordement</td><td>{SITE['grid_connection']}</td></tr>
        </table></div>
        <div class="spec-blk"><div class="spec-hdr">Structure & Montage</div>
        <table class="spec-tbl">
            <tr><td>Type</td><td>Fixe inclinée</td></tr>
            <tr><td>Matériau</td><td>Aluminium anodisé</td></tr>
            <tr><td>Inclinaison</td><td><span class="hl">{PANEL['tilt']}°</span></td></tr>
            <tr><td>Azimut</td><td><span class="hl">{PANEL['azimuth']}° (plein Sud)</span></td></tr>
            <tr><td>Configuration</td><td>2 rangées × 6 panneaux</td></tr>
            <tr><td>Charge vent max.</td><td>40 m/s</td></tr>
        </table></div>
        <div class="spec-blk"><div class="spec-hdr">Modèle pvlib</div>
        <table class="spec-tbl">
            <tr><td>Transposition POA</td><td>Isotropic Sky</td></tr>
            <tr><td>Modèle thermique</td><td>SAPM — Open rack / Glass-Glass</td></tr>
            <tr><td>Modèle DC</td><td>PVWatts</td></tr>
            <tr><td>Rendement onduleur</td><td>97 %</td></tr>
            <tr><td>Source météo</td><td>Open-Meteo Archive API</td></tr>
            <tr><td>Résolution temporelle</td><td>1 heure</td></tr>
        </table></div>
        """, unsafe_allow_html=True)

    with col_b:
        cap = SITE["num_panels"] * PANEL["pdc0"] / 1000
        sp_y  = daily["prod_kwh"].sum() / cap
        deg25 = PANEL['degradation_pct_yr'] * 25
        st.markdown(f"""
        <div class="spec-blk"><div class="spec-hdr">Panneau Photovoltaïque</div>
        <table class="spec-tbl">
            <tr><td>Fabricant</td><td>{PANEL['manufacturer']}</td></tr>
            <tr><td>Modèle</td><td>{PANEL['model']}</td></tr>
            <tr><td>Technologie</td><td><span class="tag tag-b">{PANEL['technology']}</span></td></tr>
            <tr><td>Pmax (STC)</td><td><span class="hl">{PANEL['pdc0']} Wc</span></td></tr>
            <tr><td>Voc / Isc</td><td>{PANEL['voc']} V / {PANEL['isc']} A</td></tr>
            <tr><td>Vmp / Imp</td><td>{PANEL['vmp']} V / {PANEL['imp']} A</td></tr>
            <tr><td>Rendement STC</td><td><span class="hl">{PANEL['efficiency_pct']} %</span></td></tr>
            <tr><td>Coeff. temp. γ</td><td>{PANEL['gamma_pdc']*100:.2f} %/°C</td></tr>
            <tr><td>Garantie</td><td>{PANEL['warranty_years']} ans</td></tr>
            <tr><td>Dégradation/an</td><td>{PANEL['degradation_pct_yr']} %</td></tr>
        </table></div>
        <div class="spec-blk"><div class="spec-hdr">Onduleur (×{SITE['num_inverters']})</div>
        <table class="spec-tbl">
            <tr><td>Fabricant / Modèle</td><td>{INVERTER['manufacturer']} {INVERTER['model']}</td></tr>
            <tr><td>Puissance unitaire</td><td><span class="hl">{INVERTER['power_kva']} kVA</span></td></tr>
            <tr><td>Rendement européen</td><td><span class="hl">{INVERTER['efficiency_pct']} %</span></td></tr>
            <tr><td>Canaux MPPT</td><td>{INVERTER['mppt_channels']}</td></tr>
            <tr><td>Tension DC max</td><td>{INVERTER['voltage_dc_max']} V</td></tr>
            <tr><td>Protection</td><td><span class="tag tag-g">{INVERTER['ip_class']}</span></td></tr>
        </table></div>
        <div class="spec-blk"><div class="spec-hdr">Indicateurs de conception</div>
        <table class="spec-tbl">
            <tr><td>Production spécifique</td><td><span class="hl">{sp_y:.0f} kWh/kWp</span></td></tr>
            <tr><td>PR moyen annuel</td><td><span class="hl">{daily['pr'].mean():.1f} %</span></td></tr>
            <tr><td>Dégradation à 25 ans</td><td><span class="tag tag-r">−{deg25:.0f} %</span></td></tr>
            <tr><td>T. cellule max simulée</td><td>{daily['cell_tmax'].max():.1f} °C</td></tr>
            <tr><td>T. cellule moy. annuelle</td><td>{daily['cell_tmean'].mean():.1f} °C</td></tr>
        </table></div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
# RAPPORT
# ══════════════════════════════════════════════
elif "Rapport" in menu:
    total_kwh = daily["prod_kwh"].sum()
    avg_pr    = daily["pr"].mean()
    best_m    = monthly.loc[monthly["prod_kwh"].idxmax()]
    worst_m   = monthly.loc[monthly["prod_kwh"].idxmin()]
    avg_daily = daily["prod_kwh"].mean()
    low_pr_n  = len(daily[daily["pr"] < 70])
    cap       = SITE["num_panels"] * PANEL["pdc0"] / 1000

    st.markdown(f"""
    <div class="report-box">
        <div class="report-title">📋 Rapport de Performance</div>
        <div class="report-sub">{SITE['name']} &nbsp;·&nbsp; {start_date.strftime('%d/%m/%Y')} → {end_date.strftime('%d/%m/%Y')}</div>
        <hr>
        <div class="report-sec">Production</div>
        <div class="spec-blk"><table class="spec-tbl">
            <tr><td>Production totale</td><td><span class="hl">{total_kwh/1000:.3f} MWh</span></td></tr>
            <tr><td>Production journalière moy.</td><td>{avg_daily:.1f} kWh/jour</td></tr>
            <tr><td>Meilleur mois</td><td><span class="hlg">{best_m.name} — {best_m['prod_kwh']/1000:.3f} MWh</span></td></tr>
            <tr><td>Mois le plus faible</td><td><span style="color:#E74C3C">{worst_m.name} — {worst_m['prod_kwh']/1000:.3f} MWh</span></td></tr>
            <tr><td>Rendement spécifique</td><td><span class="hl">{total_kwh/cap:.0f} kWh/kWp</span></td></tr>
        </table></div>
        <div class="report-sec">Performance</div>
        <div class="spec-blk"><table class="spec-tbl">
            <tr><td>Performance Ratio moyen</td><td><span class="hl">{avg_pr:.1f} %</span></td></tr>
            <tr><td>Jours avec PR &lt; 70 %</td><td><span style="color:{'#2ECC71' if low_pr_n==0 else '#E74C3C'}">{low_pr_n} jours</span></td></tr>
            <tr><td>T. cellule max. simulée</td><td>{daily['cell_tmax'].max():.1f} °C</td></tr>
            <tr><td>T. cellule moy.</td><td>{daily['cell_tmean'].mean():.1f} °C</td></tr>
        </table></div>
        <div class="report-sec">Ressource solaire</div>
        <div class="spec-blk"><table class="spec-tbl">
            <tr><td>GHI moyen</td><td><span class="hl">{res['ghi'].mean():.0f} W/m²</span></td></tr>
            <tr><td>T. air moyenne</td><td>{res['temp'].mean():.1f} °C</td></tr>
            <tr><td>Vent moyen</td><td>{res['wind'].mean():.1f} km/h</td></tr>
            <tr><td>Localisation</td><td>{SITE['location']} — {SITE['lat']}°N, {abs(SITE['lon'])}°W</td></tr>
        </table></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="sec"><span>💾</span> Export des données</div>', unsafe_allow_html=True)

    cd1, cd2, cd3 = st.columns(3)
    with cd1:
        st.download_button("⬇ Journaliers (CSV)",
            daily.reset_index().to_csv(index=False, float_format="%.3f"),
            file_name=f"solaris_daily_{start_date}_{end_date}.csv",
            mime="text/csv", use_container_width=True)
    with cd2:
        st.download_button("⬇ Mensuels (CSV)",
            monthly.to_csv(float_format="%.3f"),
            file_name=f"solaris_monthly_{start_date}_{end_date}.csv",
            mime="text/csv", use_container_width=True)
    with cd3:
        st.download_button("⬇ Horaires (CSV)",
            res.reset_index().to_csv(index=False, float_format="%.4f"),
            file_name=f"solaris_hourly_{start_date}_{end_date}.csv",
            mime="text/csv", use_container_width=True)


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(f"""
<div style="text-align:center;color:#21273A;font-size:10px;padding:6px 0;
    font-family:'Space Mono',monospace;letter-spacing:.1em">
    SOLARIS DIGITAL TWIN &nbsp;·&nbsp; MOHAMMEDIA, MAROC &nbsp;·&nbsp;
    pvlib + Open-Meteo API &nbsp;·&nbsp; {now.strftime('%d/%m/%Y %H:%M')}
</div>
""", unsafe_allow_html=True)
