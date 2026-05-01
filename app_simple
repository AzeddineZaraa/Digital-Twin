import streamlit as st
import requests
import pandas as pd
import time

# =====================
# CONFIG
# =====================
BLYNK_TOKEN = "TON_TOKEN"
POWER_PIN = "V0"
RELAY1 = "V1"
RELAY2 = "V2"

st.set_page_config(page_title="PV Dashboard", layout="wide")

# =====================
# THEME TOGGLE
# =====================
if "dark" not in st.session_state:
    st.session_state.dark = False

if st.button("🌙 / ☀️ Mode"):
    st.session_state.dark = not st.session_state.dark

if st.session_state.dark:
    st.markdown("<style>body{background:#0e1117;color:white}</style>", unsafe_allow_html=True)

# =====================
# FUNCTIONS
# =====================
def get_power():
    try:
        url = f"https://blynk.cloud/external/api/get?token={BLYNK_TOKEN}&{POWER_PIN}"
        return float(requests.get(url).text)
    except:
        return 0

def model_power():
    return 800  # simple model

def relay(pin, state):
    requests.get(f"https://blynk.cloud/external/api/update?token={BLYNK_TOKEN}&{pin}={state}")

# =====================
# UI
# =====================
st.title("Digital Twin PV - Simple")

real = get_power()
model = model_power()

col1, col2 = st.columns(2)
col1.metric("Puissance réelle", f"{real} W")
col2.metric("Puissance modèle", f"{model} W")

# =====================
# GRAPH
# =====================
if "data" not in st.session_state:
    st.session_state.data = []

st.session_state.data.append({"real": real, "model": model})

df = pd.DataFrame(st.session_state.data)

st.line_chart(df)

# =====================
# RELAYS
# =====================
st.subheader("Contrôle")

c1, c2 = st.columns(2)

with c1:
    if st.button("ON Charge 1"):
        relay(RELAY1, 1)
    if st.button("OFF Charge 1"):
        relay(RELAY1, 0)

with c2:
    if st.button("ON Charge 2"):
        relay(RELAY2, 1)
    if st.button("OFF Charge 2"):
        relay(RELAY2, 0)

time.sleep(2)
st.rerun()
