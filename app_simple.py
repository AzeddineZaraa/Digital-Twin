import streamlit as st
import requests
import pandas as pd
import time
import yaml

from model import PVModel

# =========================
# CONFIG LOAD
# =========================
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

model = PVModel(config)

# =========================
# STREAMLIT CONFIG
# =========================
st.set_page_config(page_title="Digital Twin PV", layout="wide")

# =========================
# THEME TOGGLE
# =========================
if "dark" not in st.session_state:
    st.session_state.dark = False

if st.button("🌙 / ☀️ Mode"):
    st.session_state.dark = not st.session_state.dark

if st.session_state.dark:
    st.markdown("""
        <style>
        body {background-color: #0e1117; color: white;}
        .stApp {background-color: #0e1117;}
        </style>
    """, unsafe_allow_html=True)

# =========================
# WEATHER (MOHAMMEDIA)
# =========================
def get_weather():
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": config["site"]["latitude"],
        "longitude": config["site"]["longitude"],
        "current": "temperature_2m,shortwave_radiation",
        "timezone": config["site"]["tz"]
    }

    try:
        r = requests.get(url)
        data = r.json()["current"]

        temp = data["temperature_2m"]
        ghi = data["shortwave_radiation"]

        return ghi, temp
    except:
        return 500, 25

# =========================
# BLYNK (REAL DATA)
# =========================
def get_real_power():
    try:
        url = f"{config['blynk']['server']}/external/api/get?token={config['blynk']['token']}&V2"
        return float(requests.get(url).text)
    except:
        return 0

def control_relay(pin, state):
    try:
        url = f"{config['blynk']['server']}/external/api/update?token={config['blynk']['token']}&{pin}={state}"
        requests.get(url)
    except:
        pass

# =========================
# TITLE
# =========================
st.title("⚡ Digital Twin PV - Simple Dashboard")

# =========================
# MODEL CALCULATION
# =========================
irradiance, temp = get_weather()

result = model.compute(irradiance, temp)

model_power = result["p_ac_kw"] * 1000  # W
real_power = get_real_power()

# =========================
# KPI
# =========================
col1, col2, col3, col4 = st.columns(4)

col1.metric("Température", f"{temp} °C")
col2.metric("Irradiance", f"{irradiance} W/m²")
col3.metric("Puissance modèle", f"{model_power:.0f} W")
col4.metric("Puissance réelle", f"{real_power} W")

# =========================
# GRAPH
# =========================
if "data" not in st.session_state:
    st.session_state.data = []

st.session_state.data.append({
    "model": model_power,
    "real": real_power
})

df = pd.DataFrame(st.session_state.data)

st.subheader("📈 Puissance (Modèle vs Réel)")
st.line_chart(df)

# =========================
# EMS SIMPLE
# =========================
st.subheader("⚙️ EMS (Gestion des charges)")

if model_power > real_power:
    st.success("Surplus PV → possibilité d'activer charge")
else:
    st.warning("Déficit → éviter d'activer charge")

# =========================
# RELAYS CONTROL
# =========================
col5, col6 = st.columns(2)

with col5:
    if st.button("ON Charge 1"):
        control_relay("V3", 1)
    if st.button("OFF Charge 1"):
        control_relay("V3", 0)

with col6:
    if st.button("ON Charge 2"):
        control_relay("V4", 1)
    if st.button("OFF Charge 2"):
        control_relay("V4", 0)

# =========================
# AUTO REFRESH
# =========================
time.sleep(2)
st.rerun()
