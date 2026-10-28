import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="App de Reparto - MediPort", page_icon="📦", layout="wide")

st.markdown("<h1>📦 App de Reparto - MediPort</h1>", unsafe_allow_html=True)
st.markdown("<span>Control de Flota, Ruteo por Zonas (Norte/Sur) y Formato FOR-23</span>", unsafe_allow_html=True)
st.divider()

# --- INICIALIZAR MEMORIA GLOBAL ---
if "df_conductores" not in st.session_state:
    st.session_state.df_conductores = pd.DataFrame(columns=["Nombres", "Apellidos", "DNI"])

if "df_flota" not in st.session_state:
    st.session_state.df_flota = pd.DataFrame(columns=["Placa", "Capacidad Cajas", "Capacidad (m3)"])

if "df_pedidos" not in st.session_state:
    st.session_state.df_pedidos = None


# --- MENÚ LATERAL ---
st.sidebar.title("⚙️ Menú Principal")
menu = st.sidebar.selectbox("Navegación", [
    "1. Panel de Control (Personal y Flota)", 
    "2. Ruteo por Zonas (Norte / Sur)", 
    "3. Control de Reparto en Ruta (FOR-23)"
])


# =================
