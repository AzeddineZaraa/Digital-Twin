import streamlit as st
import random
import pandas as pd
import time

st.set_page_config(layout="wide")

# SIDEBAR
st.sidebar.title("☀️ SOLARIS")
menu = st.sidebar.radio("Menu", ["Vue globale", "Monitoring", "Analyse", "Maintenance"])

# HEADER
st.title("⚡ Centrale Photovoltaïque - Digital Twin")

# METRICS TOP
col1, col2, col3, col4 = st.columns(4)

col1.metric("Puissance actuelle", f"{random.randint(1000,3000)} W")
col2.metric("Production du jour", f"{random.randint(5,10)} kWh")
col3.metric("Production totale", f"{random.randint(100,200)} MWh")
col4.metric("PR", f"{random.randint(80,95)} %")

# IMAGE CENTRALE
st.image("https://images.unsplash.com/photo-1509395176047-4a66953fd231", use_column_width=True)

# GRAPHIQUE
st.subheader("📈 Production du jour")

data = pd.DataFrame({
    "Heure": list(range(24)),
    "Production": [random.randint(0, 3000) for _ in range(24)]
})

st.line_chart(data.set_index("Heure"))

# BAS
col5, col6, col7 = st.columns(3)

with col5:
    st.subheader("🌤️ Météo")
    st.write("Température: 23°C")
    st.write("Irradiance: 800 W/m²")

with col6:
    st.subheader("🔌 Onduleurs")
    st.write("✔️ 22 OK")
    st.write("⚠️ 1 Warning")

with col7:
    st.subheader("🚨 Alertes")
    st.warning("Onduleur 7 : puissance réduite")
