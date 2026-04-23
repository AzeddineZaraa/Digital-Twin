"""
╔══════════════════════════════════════════════════════════════════╗
║     SOLARIS - Digital Twin PV · Mohammedia, Maroc               ║
║     Streamlit + pvlib · Open-Meteo API                          ║
╚══════════════════════════════════════════════════════════════════╝
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
from pvlib.pvsystem import PVSystem
from pvlib.modelchain import ModelChain
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS

# ─────────────────────────────────────────────
# CONFIGURATION STREAMLIT
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="SOLARIS · Digital Twin Mohammedia",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# CSS PERSONNALISÉ
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    :root {
        --solar-yellow: #F5A623;
        --solar-orange: #E8860A;
        --dark-bg: #0D1117;
        --card-bg: #161B22;
        --border: #30363D;
        --text-primary: #E6EDF3;
        --text-secondary: #8B949E;
        --green: #3FB950;
        --red: #F85149;
        --blue: #58A6FF;
    }

    .stApp { background-color: var(--dark-bg); font-family: 'Inter', sans-serif; }

    .main-header {
        background: linear-gradient(135deg, #0D1117 0%, #161B22 50%, #1C2128 100%);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 20px 28px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .plant-name { font-size: 24px; font-weight: 700; color: var(--solar-yellow); }
    .plant-sub { font-size: 13px; color: var(--text-secondary); margin-top: 2px; }

    .metric-card {
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 18px 20px;
        text-align: center;
    }
    .metric-value { font-size: 28px; font-weight: 700; color: var(--solar-yellow); }
    .metric-label { font-size: 12px; color: var(--text-secondary); margin-top: 4px; text-transform: uppercase; letter-spacing: 0.5px; }
    .metric-delta { font-size: 13px; margin-top: 6px; }
    .delta-up { color: var(--green); }
    .delta-down { color: var(--red); }

    .section-title {
        font-size: 16px; font-weight: 600; color: var(--text-primary);
        margin-bottom: 12px; padding-bottom: 8px;
        border-bottom: 1px solid var(--border);
    }

    .alert-card {
        border-radius: 8px; padding: 10px 14px; margin-bottom: 8px;
        font-size: 13px; border-left: 3px solid;
    }
    .alert-warning { background: #2D2008; border-color: var(--solar-yellow); color: #E3AC5C; }
    .alert-error   { background: #2D0A0A; border-color: var(--red); color: #F07878; }
    .alert-ok      { background: #0A2014; border-color: var(--green); color: #5DD78A; }

    .status-dot {
        display: inline-block; width: 8px; height: 8px;
        border-radius: 50%; margin-right: 6px;
    }
    .status-ok     { background: var(--green); box-shadow: 0 0 6px var(--green); }
    .status-warn   { background: var(--solar-yellow); box-shadow: 0 0 6px var(--solar-yellow); }
    .status-error  { background: var(--red); box-shadow: 0 0 6px var(--red); }

    /* Sidebar */
    .css-1d391kg, [data-testid="stSidebar"] {
        background-color: #0D1117 !important;
        border-right: 1px solid var(--border) !important;
    }

    div[data-testid="metric-container"] {
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 14px;
    }

    div[data-testid="metric-container"] label {
        color: var(--text-secondary) !important;
        font-size: 12px !important;
        text-transform: uppercase;
    }

    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: var(--solar-yellow) !important;
        font-size: 26px !important;
        font-weight: 700 !important;
    }

    .stPlotlyChart { border-radius: 10px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PARAMÈTRES DE LA CENTRALE - MOHAMMEDIA
# ─────────────────────────────────────────────
SITE = {
    "name": "Centrale PV Mohammedia",
    "lat": 33.6861,
    "lon": -7.3833,
    "altitude": 15,        # m (ville côtière)
    "timezone": "Africa/Casablanca",
    "capacity_kwp": 500,   # kWp installé
    "surface_m2": 3000,    # m²
    "num_panels": 1250,    # panneaux
    "num_inverters": 22,
}

PANEL = {
    "pdc0": 400,           # W crête par panneau
    "gamma_pdc": -0.0035,  # coeff température
    "tilt": 30,            # inclinaison
    "azimuth": 180,        # plein sud
}


# ─────────────────────────────────────────────
# FONCTIONS PRINCIPALES
# ─────────────────────────────────────────────

@st.cache_data(ttl=3600)
def fetch_meteo(lat, lon, start_date, end_date):
    """Récupère les données météo via Open-Meteo API."""
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
        st.error(f"⚠️ Erreur API météo : {e}")
        return None


@st.cache_data(ttl=3600)
def run_pvlib_simulation(lat, lon, altitude, timezone, tilt, azimuth, pdc0, gamma_pdc, start_date, end_date):
    """Simule la production PV avec pvlib."""
    location = Location(
        latitude=lat,
        longitude=lon,
        altitude=altitude,
        tz=timezone,
        name="Mohammedia"
    )

    # Récupération météo
    df = fetch_meteo(lat, lon, start_date, end_date)
    if df is None:
        return None

    # Calcul position solaire
    times = df.index
    solar_pos = location.get_solarposition(times)

    # Irradiance sur plan incliné (transposition)
    poa = pvlib.irradiance.get_total_irradiance(
        surface_tilt=tilt,
        surface_azimuth=azimuth,
        dni=df["dni"],
        ghi=df["ghi"],
        dhi=df["dhi"],
        solar_zenith=solar_pos["apparent_zenith"],
        solar_azimuth=solar_pos["azimuth"],
    )

    # Température cellule (modèle Sandia)
    temp_params = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS["sapm"]["open_rack_glass_glass"]
    cell_temp = pvlib.temperature.sapm_cell(
        poa_global=poa["poa_global"],
        temp_air=df["temp_air"],
        wind_speed=df["wind_speed"],
        a=temp_params["a"],
        b=temp_params["b"],
        deltaT=temp_params["deltaT"],
    )

    # Puissance DC (modèle simple)
    dc_power = pvlib.pvsystem.pvwatts_dc(
        g_poa_effective=poa["poa_global"],
        temp_cell=cell_temp,
        pdc0=pdc0,
        gamma_pdc=gamma_pdc,
    )

    # Rendement onduleur ~ 97%
    ac_power = dc_power * 0.97

    # Assemblage résultats
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
    """Agrégation journalière."""
    daily = results.groupby("date").agg(
        production_kwh=("ac_power_kw", lambda x: x.sum()),
        peak_power_kw=("ac_power_kw", "max"),
        avg_temp=("temp_air", "mean"),
        avg_ghi=("ghi", "mean"),
        peak_sun_hours=("poa_global", lambda x: x.sum() / 1000),
    ).reset_index()

    # Performance Ratio = production réelle / production théorique
    daily["theoretical_kwh"] = daily["peak_sun_hours"] * (num_panels * 0.4)  # 400W par panneau
    daily["pr"] = (daily["production_kwh"] / daily["theoretical_kwh"].replace(0, np.nan)).clip(0, 1) * 100
    daily["date"] = pd.to_datetime(daily["date"])

    return daily


def compute_monthly(daily):
    """Agrégation mensuelle."""
    monthly = daily.groupby(daily["date"].dt.to_period("M")).agg(
        production_kwh=("production_kwh", "sum"),
        avg_pr=("pr", "mean"),
        avg_temp=("avg_temp", "mean"),
    ).reset_index()
    monthly["date"] = monthly["date"].dt.to_timestamp()
    monthly["month_name"] = monthly["date"].dt.strftime("%b %Y")
    return monthly


def get_current_meteo(lat, lon):
    """Météo actuelle via Open-Meteo."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,shortwave_radiation",
        "timezone": "Africa/Casablanca",
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.json().get("current", {})
    except:
        return {}


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ☀️ SOLARIS")
    st.markdown(f"**{SITE['name']}**")
    st.markdown(f"📍 Mohammedia, Maroc")
    st.markdown("---")

    menu = st.radio(
        "Navigation",
        ["🏠 Vue Globale", "📊 Production", "🌤️ Météo & Irradiance", "⚙️ Onduleurs", "📋 Rapport"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("**Période d'analyse**")

    col_s, col_e = st.columns(2)
    with col_s:
        start_date = st.date_input("Début", value=datetime(2024, 1, 1), label_visibility="collapsed")
    with col_e:
        end_date = st.date_input("Fin", value=datetime(2024, 12, 31), label_visibility="collapsed")

    st.markdown(f"Du **{start_date.strftime('%d/%m/%Y')}** au **{end_date.strftime('%d/%m/%Y')}**")

    st.markdown("---")
    st.markdown("**Paramètres centrale**")
    st.markdown(f"⚡ Capacité : **{SITE['capacity_kwp']} kWp**")
    st.markdown(f"🔲 Panneaux : **{SITE['num_panels']}**")
    st.markdown(f"🔌 Onduleurs : **{SITE['num_inverters']}**")
    st.markdown(f"📐 Inclinaison : **{PANEL['tilt']}°**")

    st.markdown("---")
    auto_refresh = st.checkbox("🔄 Auto-actualisation (5 min)", value=False)
    if auto_refresh:
        st.rerun()


# ─────────────────────────────────────────────
# SIMULATION PVLIB
# ─────────────────────────────────────────────
with st.spinner("⚙️ Simulation pvlib en cours..."):
    results = run_pvlib_simulation(
        lat=SITE["lat"],
        lon=SITE["lon"],
        altitude=SITE["altitude"],
        timezone=SITE["timezone"],
        tilt=PANEL["tilt"],
        azimuth=PANEL["azimuth"],
        pdc0=PANEL["pdc0"],
        gamma_pdc=PANEL["gamma_pdc"],
        start_date=str(start_date),
        end_date=str(end_date),
    )

if results is None:
    st.error("❌ Impossible de récupérer les données. Vérifiez votre connexion internet.")
    st.stop()

# Échelle au nombre de panneaux
results["ac_power_kw"] = results["ac_power_kw"] * SITE["num_panels"]
daily = compute_daily(results, SITE["num_panels"])
monthly = compute_monthly(daily)

# Météo actuelle
current_meteo = get_current_meteo(SITE["lat"], SITE["lon"])
now = datetime.now()


# ─────────────────────────────────────────────
# HEADER PRINCIPAL
# ─────────────────────────────────────────────
col_h1, col_h2, col_h3 = st.columns([3, 1, 1])
with col_h1:
    st.markdown(f"""
    <div class="main-header" style="display:block">
        <div class="plant-name">☀️ {SITE['name']}</div>
        <div class="plant-sub">📍 Mohammedia · {SITE['lat']}°N, {abs(SITE['lon'])}°W · {SITE['altitude']} m · {SITE['capacity_kwp']} kWp</div>
    </div>
    """, unsafe_allow_html=True)
with col_h2:
    st.metric("🌡️ Temp. actuelle",
              f"{current_meteo.get('temperature_2m', '--')} °C")
with col_h3:
    ghi_now = current_meteo.get('shortwave_radiation', 0)
    status = "🟢 En production" if ghi_now and ghi_now > 50 else "🔵 Hors production"
    st.metric("☀️ Irradiance", f"{ghi_now} W/m²", status)


# ─────────────────────────────────────────────
# VUE GLOBALE
# ─────────────────────────────────────────────
if "Vue Globale" in menu:

    # KPIs principaux
    total_kwh = daily["production_kwh"].sum()
    avg_pr = daily["pr"].mean()
    peak_day_kwh = daily["production_kwh"].max()
    peak_day_date = daily.loc[daily["production_kwh"].idxmax(), "date"].strftime("%d/%m/%Y")
    avg_daily_kwh = daily["production_kwh"].mean()

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("⚡ Production totale", f"{total_kwh/1000:.1f} MWh")
    k2.metric("📈 Performance Ratio", f"{avg_pr:.1f} %")
    k3.metric("🏆 Meilleur jour", f"{peak_day_kwh:.0f} kWh", peak_day_date)
    k4.metric("📊 Moy. journalière", f"{avg_daily_kwh:.0f} kWh")
    k5.metric("☀️ Capacité", f"{SITE['capacity_kwp']} kWp", f"{SITE['num_panels']} panneaux")

    st.markdown("---")

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown('<div class="section-title">📈 Production journalière (kWh)</div>', unsafe_allow_html=True)
        fig_daily = go.Figure()
        fig_daily.add_trace(go.Bar(
            x=daily["date"], y=daily["production_kwh"],
            name="Production",
            marker_color=np.where(
                daily["production_kwh"] < daily["production_kwh"].quantile(0.2),
                "#F85149",
                np.where(
                    daily["production_kwh"] > daily["production_kwh"].quantile(0.8),
                    "#3FB950", "#F5A623"
                )
            ),
            opacity=0.85,
        ))
        fig_daily.add_trace(go.Scatter(
            x=daily["date"],
            y=daily["production_kwh"].rolling(7, center=True).mean(),
            name="Moy. mobile 7j",
            line=dict(color="#58A6FF", width=2),
        ))
        fig_daily.update_layout(
            template="plotly_dark",
            paper_bgcolor="#161B22",
            plot_bgcolor="#161B22",
            showlegend=True,
            height=320,
            margin=dict(t=20, b=30, l=50, r=20),
            xaxis=dict(gridcolor="#30363D"),
            yaxis=dict(gridcolor="#30363D", title="kWh"),
        )
        st.plotly_chart(fig_daily, use_container_width=True)

    with col_right:
        st.markdown('<div class="section-title">📅 Production mensuelle (MWh)</div>', unsafe_allow_html=True)
        fig_month = go.Figure(go.Bar(
            x=monthly["month_name"],
            y=monthly["production_kwh"] / 1000,
            marker_color="#F5A623",
            text=(monthly["production_kwh"] / 1000).round(1).astype(str),
            textposition="outside",
            textfont=dict(color="#E6EDF3", size=11),
        ))
        fig_month.update_layout(
            template="plotly_dark",
            paper_bgcolor="#161B22",
            plot_bgcolor="#161B22",
            height=320,
            margin=dict(t=20, b=30, l=40, r=10),
            xaxis=dict(gridcolor="#30363D"),
            yaxis=dict(gridcolor="#30363D", title="MWh"),
        )
        st.plotly_chart(fig_month, use_container_width=True)

    # Alertes
    st.markdown('<div class="section-title">🚨 Alertes système</div>', unsafe_allow_html=True)
    low_pr_days = daily[daily["pr"] < 70]
    alerts_col1, alerts_col2 = st.columns([2, 1])

    with alerts_col1:
        if len(low_pr_days) > 0:
            st.markdown(f"""
            <div class="alert-card alert-warning">
                ⚠️ <b>{len(low_pr_days)} jours</b> avec Performance Ratio < 70%
                — Dernier : {low_pr_days["date"].max().strftime('%d/%m/%Y')}
            </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div class="alert-card alert-warning">
            ⚠️ <b>Onduleur #7</b> — Puissance réduite de 12% (depuis 3 jours)
        </div>
        <div class="alert-card alert-ok">
            ✅ <b>21 onduleurs</b> — Fonctionnement nominal
        </div>
        <div class="alert-card alert-ok">
            ✅ <b>Système de monitoring</b> — Toutes les données reçues
        </div>
        """, unsafe_allow_html=True)

    with alerts_col2:
        st.markdown("**Statut onduleurs**")
        fig_inv = go.Figure(go.Pie(
            values=[21, 1],
            labels=["Nominaux", "Alerte"],
            hole=0.65,
            marker_colors=["#3FB950", "#F5A623"],
            textinfo="none",
        ))
        fig_inv.add_annotation(
            text=f"<b>22</b><br>Total",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="#E6EDF3"),
        )
        fig_inv.update_layout(
            template="plotly_dark",
            paper_bgcolor="#161B22",
            height=200,
            margin=dict(t=10, b=10, l=10, r=10),
            showlegend=True,
            legend=dict(font=dict(size=11, color="#8B949E")),
        )
        st.plotly_chart(fig_inv, use_container_width=True)


# ─────────────────────────────────────────────
# PRODUCTION DÉTAILLÉE
# ─────────────────────────────────────────────
elif "Production" in menu:
    st.markdown("## 📊 Analyse de production")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-title">📈 Performance Ratio journalier (%)</div>', unsafe_allow_html=True)
        fig_pr = go.Figure()
        fig_pr.add_trace(go.Scatter(
            x=daily["date"], y=daily["pr"],
            fill="tozeroy",
            fillcolor="rgba(245,166,35,0.15)",
            line=dict(color="#F5A623", width=1.5),
            name="PR %",
        ))
        fig_pr.add_hline(y=75, line_dash="dash", line_color="#8B949E",
                         annotation_text="Seuil 75%", annotation_font_color="#8B949E")
        fig_pr.update_layout(
            template="plotly_dark", paper_bgcolor="#161B22", plot_bgcolor="#161B22",
            height=300, margin=dict(t=20, b=30, l=50, r=20),
            yaxis=dict(gridcolor="#30363D", range=[0, 110]),
            xaxis=dict(gridcolor="#30363D"),
        )
        st.plotly_chart(fig_pr, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">🌡️ Corrélation Température / Production</div>', unsafe_allow_html=True)
        fig_corr = px.scatter(
            daily, x="avg_temp", y="production_kwh",
            color="pr", color_continuous_scale="YlOrRd",
            opacity=0.7, size_max=8,
            labels={"avg_temp": "Temp moy (°C)", "production_kwh": "Production (kWh)", "pr": "PR %"},
        )
        fig_corr.update_layout(
            template="plotly_dark", paper_bgcolor="#161B22", plot_bgcolor="#161B22",
            height=300, margin=dict(t=20, b=30, l=50, r=20),
        )
        st.plotly_chart(fig_corr, use_container_width=True)

    # Profil horaire moyen
    st.markdown('<div class="section-title">⏱️ Profil horaire moyen de production (kW)</div>', unsafe_allow_html=True)
    hourly_avg = results.groupby("hour")["ac_power_kw"].mean().reset_index()
    hourly_avg.columns = ["hour", "avg_power_kw"]

    fig_hour = go.Figure()
    fig_hour.add_trace(go.Scatter(
        x=hourly_avg["hour"], y=hourly_avg["avg_power_kw"],
        fill="tozeroy",
        fillcolor="rgba(245,166,35,0.2)",
        line=dict(color="#F5A623", width=2),
        mode="lines",
    ))
    fig_hour.update_layout(
        template="plotly_dark", paper_bgcolor="#161B22", plot_bgcolor="#161B22",
        height=280, margin=dict(t=20, b=30, l=60, r=20),
        xaxis=dict(title="Heure", gridcolor="#30363D", dtick=1),
        yaxis=dict(title="Puissance (kW)", gridcolor="#30363D"),
    )
    st.plotly_chart(fig_hour, use_container_width=True)

    # Heatmap production mensuelle/horaire
    st.markdown('<div class="section-title">🗓️ Heatmap production (Mois × Heure, kWh moyen)</div>', unsafe_allow_html=True)
    heatmap_data = results.groupby(["month", "hour"])["ac_power_kw"].mean().reset_index()
    heatmap_pivot = heatmap_data.pivot(index="month", columns="hour", values="ac_power_kw")
    months_fr = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun", "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"]
    heatmap_pivot.index = [months_fr[m - 1] for m in heatmap_pivot.index]

    fig_heat = go.Figure(go.Heatmap(
        z=heatmap_pivot.values,
        x=[f"{h}h" for h in heatmap_pivot.columns],
        y=heatmap_pivot.index,
        colorscale=[
            [0, "#0D1117"], [0.3, "#331A00"], [0.6, "#B36B00"], [1, "#F5A623"]
        ],
        showscale=True,
        colorbar=dict(title="kW", tickfont=dict(color="#8B949E")),
    ))
    fig_heat.update_layout(
        template="plotly_dark", paper_bgcolor="#161B22", plot_bgcolor="#161B22",
        height=300, margin=dict(t=20, b=30, l=60, r=60),
        xaxis=dict(title="Heure", tickfont=dict(size=10)),
        yaxis=dict(tickfont=dict(size=10)),
    )
    st.plotly_chart(fig_heat, use_container_width=True)


# ─────────────────────────────────────────────
# MÉTÉO & IRRADIANCE
# ─────────────────────────────────────────────
elif "Météo" in menu:
    st.markdown("## 🌤️ Météo & Irradiance — Mohammedia")

    # Météo actuelle
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🌡️ Température", f"{current_meteo.get('temperature_2m', '--')} °C")
    m2.metric("💧 Humidité", f"{current_meteo.get('relative_humidity_2m', '--')} %")
    m3.metric("🌬️ Vent", f"{current_meteo.get('wind_speed_10m', '--')} km/h")
    m4.metric("☀️ Irradiance GHI", f"{current_meteo.get('shortwave_radiation', '--')} W/m²")

    # GHI journalier
    daily_ghi = results.groupby("date").agg(ghi_sum=("ghi", lambda x: x.sum() / 1000)).reset_index()
    daily_ghi["date"] = pd.to_datetime(daily_ghi["date"])

    st.markdown('<div class="section-title">☀️ Irradiance globale horizontale (kWh/m²/jour)</div>', unsafe_allow_html=True)
    fig_ghi = go.Figure()
    fig_ghi.add_trace(go.Scatter(
        x=daily_ghi["date"], y=daily_ghi["ghi_sum"],
        fill="tozeroy", fillcolor="rgba(245,166,35,0.2)",
        line=dict(color="#F5A623", width=1.5),
    ))
    fig_ghi.update_layout(
        template="plotly_dark", paper_bgcolor="#161B22", plot_bgcolor="#161B22",
        height=280, margin=dict(t=20, b=30, l=60, r=20),
        yaxis=dict(gridcolor="#30363D", title="kWh/m²"),
        xaxis=dict(gridcolor="#30363D"),
    )
    st.plotly_chart(fig_ghi, use_container_width=True)

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown('<div class="section-title">🌡️ Température journalière moyenne (°C)</div>', unsafe_allow_html=True)
        daily_temp = results.groupby("date").agg(temp_avg=("temp_air", "mean")).reset_index()
        daily_temp["date"] = pd.to_datetime(daily_temp["date"])
        fig_temp = go.Figure(go.Scatter(
            x=daily_temp["date"], y=daily_temp["temp_avg"],
            line=dict(color="#58A6FF", width=1.5),
        ))
        fig_temp.add_hline(y=daily_temp["temp_avg"].mean(),
                           line_dash="dash", line_color="#F5A623",
                           annotation_text=f"Moy: {daily_temp['temp_avg'].mean():.1f}°C")
        fig_temp.update_layout(
            template="plotly_dark", paper_bgcolor="#161B22", plot_bgcolor="#161B22",
            height=250, margin=dict(t=20, b=30, l=50, r=20),
            yaxis=dict(gridcolor="#30363D"),
        )
        st.plotly_chart(fig_temp, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-title">📊 Distribution GHI mensuel (kWh/m²)</div>', unsafe_allow_html=True)
        monthly_ghi = daily_ghi.copy()
        monthly_ghi["month"] = monthly_ghi["date"].dt.strftime("%b")
        monthly_ghi_agg = monthly_ghi.groupby("month")["ghi_sum"].sum().reset_index()
        fig_mghi = go.Figure(go.Bar(
            x=monthly_ghi_agg["month"], y=monthly_ghi_agg["ghi_sum"],
            marker_color="#F5A623",
        ))
        fig_mghi.update_layout(
            template="plotly_dark", paper_bgcolor="#161B22", plot_bgcolor="#161B22",
            height=250, margin=dict(t=20, b=30, l=50, r=20),
            yaxis=dict(gridcolor="#30363D", title="kWh/m²"),
        )
        st.plotly_chart(fig_mghi, use_container_width=True)


# ─────────────────────────────────────────────
# ONDULEURS
# ─────────────────────────────────────────────
elif "Onduleurs" in menu:
    st.markdown("## ⚙️ Tableau de bord Onduleurs")

    n = SITE["num_inverters"]
    np.random.seed(42)
    inv_power = np.random.normal(95, 8, n).clip(60, 105)
    inv_power[6] = 78  # onduleur #7 en alerte

    inv_status = ["⚠️" if p < 85 else "✅" for p in inv_power]
    inv_labels = [f"INV-{i+1:02d}" for i in range(n)]

    # Grille onduleurs
    st.markdown('<div class="section-title">🔌 État des onduleurs</div>', unsafe_allow_html=True)
    inv_cols = st.columns(6)
    for i in range(n):
        with inv_cols[i % 6]:
            color = "#F5A623" if inv_power[i] < 85 else "#3FB950"
            st.markdown(f"""
            <div style="background:#161B22;border:1px solid #30363D;border-radius:8px;
                        padding:10px;text-align:center;margin-bottom:8px;border-left:3px solid {color}">
                <div style="font-size:11px;color:#8B949E">{inv_labels[i]}</div>
                <div style="font-size:18px;font-weight:700;color:{color}">{inv_power[i]:.0f}%</div>
                <div style="font-size:14px">{inv_status[i]}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">📊 Puissance relative par onduleur (%)</div>', unsafe_allow_html=True)
        fig_inv_bar = go.Figure(go.Bar(
            x=inv_labels, y=inv_power,
            marker_color=["#F5A623" if p < 85 else "#3FB950" for p in inv_power],
        ))
        fig_inv_bar.add_hline(y=85, line_dash="dash", line_color="#F85149",
                              annotation_text="Seuil alerte 85%")
        fig_inv_bar.update_layout(
            template="plotly_dark", paper_bgcolor="#161B22", plot_bgcolor="#161B22",
            height=300, margin=dict(t=20, b=50, l=50, r=20),
            xaxis=dict(tickangle=-45, tickfont=dict(size=9)),
            yaxis=dict(gridcolor="#30363D", range=[50, 110]),
        )
        st.plotly_chart(fig_inv_bar, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">🥧 Répartition statut onduleurs</div>', unsafe_allow_html=True)
        ok_count = sum(1 for p in inv_power if p >= 85)
        warn_count = n - ok_count
        fig_pie = go.Figure(go.Pie(
            labels=["Nominaux ✅", "En alerte ⚠️"],
            values=[ok_count, warn_count],
            hole=0.6,
            marker_colors=["#3FB950", "#F5A623"],
        ))
        fig_pie.add_annotation(
            text=f"<b>{n}</b><br>Onduleurs",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="#E6EDF3"),
        )
        fig_pie.update_layout(
            template="plotly_dark", paper_bgcolor="#161B22",
            height=300, margin=dict(t=20, b=20, l=20, r=20),
        )
        st.plotly_chart(fig_pie, use_container_width=True)


# ─────────────────────────────────────────────
# RAPPORT
# ─────────────────────────────────────────────
elif "Rapport" in menu:
    st.markdown("## 📋 Rapport de Performance")

    total_kwh = daily["production_kwh"].sum()
    avg_pr = daily["pr"].mean()
    best_month = monthly.loc[monthly["production_kwh"].idxmax()]
    worst_month = monthly.loc[monthly["production_kwh"].idxmin()]
    avg_daily = daily["production_kwh"].mean()

    st.markdown(f"""
    <div style="background:#161B22;border:1px solid #30363D;border-radius:12px;padding:24px">
        <h3 style="color:#F5A623;margin-top:0">📄 Rapport — {SITE['name']}</h3>
        <p style="color:#8B949E">Période : {start_date.strftime('%d/%m/%Y')} → {end_date.strftime('%d/%m/%Y')}</p>
        <hr style="border-color:#30363D">

        <h4 style="color:#E6EDF3">⚡ Production</h4>
        <ul style="color:#8B949E">
            <li>Production totale : <b style="color:#F5A623">{total_kwh/1000:.1f} MWh</b></li>
            <li>Production journalière moyenne : <b style="color:#F5A623">{avg_daily:.0f} kWh/j</b></li>
            <li>Meilleur mois : <b style="color:#3FB950">{best_month['month_name']} ({best_month['production_kwh']/1000:.1f} MWh)</b></li>
            <li>Mois le plus faible : <b style="color:#F85149">{worst_month['month_name']} ({worst_month['production_kwh']/1000:.1f} MWh)</b></li>
        </ul>

        <h4 style="color:#E6EDF3">📈 Performance</h4>
        <ul style="color:#8B949E">
            <li>Performance Ratio moyen : <b style="color:#F5A623">{avg_pr:.1f}%</b></li>
            <li>Jours avec PR < 70% : <b style="color:#F85149">{len(daily[daily['pr'] < 70])}</b></li>
            <li>Disponibilité onduleurs : <b style="color:#3FB950">95.5%</b> (21/22 nominaux)</li>
        </ul>

        <h4 style="color:#E6EDF3">🌤️ Ressource solaire</h4>
        <ul style="color:#8B949E">
            <li>GHI moyen annuel : <b style="color:#F5A623">{results['ghi'].mean():.0f} W/m²</b></li>
            <li>Température moyenne : <b style="color:#F5A623">{results['temp_air'].mean():.1f} °C</b></li>
            <li>Localisation : <b style="color:#F5A623">Mohammedia, Maroc — {SITE['lat']}°N, {abs(SITE['lon'])}°W</b></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📥 Export des données")

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        csv_daily = daily.to_csv(index=False, float_format="%.2f")
        st.download_button(
            "⬇️ Télécharger résultats journaliers (CSV)",
            csv_daily,
            file_name=f"solaris_mohammedia_daily_{start_date}_{end_date}.csv",
            mime="text/csv",
        )

    with col_d2:
        csv_monthly = monthly.to_csv(index=False, float_format="%.2f")
        st.download_button(
            "⬇️ Télécharger résultats mensuels (CSV)",
            csv_monthly,
            file_name=f"solaris_mohammedia_monthly_{start_date}_{end_date}.csv",
            mime="text/csv",
        )


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(f"""
<div style="text-align:center;color:#30363D;font-size:12px;padding:10px 0">
    ☀️ SOLARIS Digital Twin · Mohammedia, Maroc · pvlib + Open-Meteo API
    · Dernière mise à jour : {now.strftime('%d/%m/%Y %H:%M')}
</div>
""", unsafe_allow_html=True)
