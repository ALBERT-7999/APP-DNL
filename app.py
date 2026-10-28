import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Control de Reparto - Roxfarma", page_icon="🚚", layout="wide")

st.markdown("<h1>🚚 Sistema de Control de Reparto y Ruteo por Flota</h1>", unsafe_allow_html=True)
st.markdown("<span>Gestión de Cargas Múltiples por Camión y Conductor - Roxfarma</span>", unsafe_allow_html=True)
st.divider()

# --- MEMORIA GLOBAL DE LA SESIÓN ---
if "df_operaciones" not in st.session_state:
    st.session_state.df_operaciones = None

# --- MENÚ DE NAVEGACIÓN ---
menu = st.sidebar.radio("📌 Menú de Operaciones", [
    "1. Carga de Data", 
    "2. Ruteo y Asignación por Camión", 
    "3. Control de Reparto (Vista Conductor)"
])


# ==========================================
# MÓDULO 1: CARGA DE DATA
# ==========================================
if menu == "1. Carga de Data":
    st.subheader("📁 1. Carga del Archivo Consolidado de Operaciones")
    st.info("Sube el archivo Excel con los datos completos de los despachos.")
    
    file_upload = st.file_uploader("Selecciona el archivo Excel (.xlsx / .xls)", type=["xlsx", "xls"])
    
    if file_upload is not None:
        try:
            df = pd.read_excel(file_upload)
            
            # Inicializar columnas operativas si no existen en el Excel
            if "ESTADO_ENTREGA" not in df.columns:
                df["ESTADO_ENTREGA"] = "ER"
            if "PLACA_ASIGNADA" not in df.columns:
                df["PLACA_ASIGNADA"] = "Sin Asignar"
            if "CONDUCTOR_ASIGNADO" not in df.columns:
                df["CONDUCTOR_ASIGNADO"] = "Sin Asignar"
            if "HORA_LLEGADA" not in df.columns:
                df["HORA_LLEGADA"] = ""
            if "OBSERVACIONES" not in df.columns:
                df["OBSERVACIONES"] = ""
                
            st.session_state.df_operaciones = df
            st.success("¡Archivo cargado correctamente en el sistema!")
            
            st.markdown("### 📊 Mapeo de Campos Obligatorios")
            st.write("Selecciona qué columna de tu Excel corresponde a cada campo operativo:")
            
            cols = df.columns.tolist()
            c1, c2, c3 = st.columns(3)
            with c1:
                st.session_state["c_cliente"] = st.selectbox("Nombre del Cliente", cols, key="m_cli")
                st.session_state["c_direccion"] = st.selectbox("Dirección del Cliente", cols, key="m_dir")
                st.session_state["c_ubicacion"] = st.selectbox("Ubicación / Waze / Maps", cols, key="m_ubi")
            with c2:
                st.session_state["c_cajas"] = st.selectbox("Cantidad de Cajas / Bultos", cols, key="m_caj")
                st.session_state["c_pedido"] = st.selectbox("Número de Pedido", cols, key="m_ped")
            with c3:
                st.session_state["c_guia_cli"] = st.selectbox("Guía de Remisión Cliente", cols, key="m_gcli")
                st.session_state["c_guia_tda"] = st.selectbox("Guía Transportista (TDA)", cols, key="m_gtda")
                
            st.divider()
            st.markdown("### Vista Previa de la Data Cargada")
            st.dataframe(df.head(5), use_container_width=True)
            
        except Exception as e:
            st.error(f"Error al leer el archivo Excel: {e}")
    else:
        if st.session_state.df_operaciones is not None:
            st.success("Actualmente hay un archivo cargado en memoria.")
            st.dataframe(st.session_state.df_operaciones.head(3), use_container_width=True)


# ==========================================
# MÓDULO 2: RUTEO Y ASIGNACIÓN POR CAMIÓN
# ==========================================
elif menu == "2. Ruteo y Asignación por Camión":
    st.subheader("🗺️ 2. Asignación de Pedidos a Múltiples Camiones")
    
    if st.session_state.df_operaciones is not None:
        df = st.session_state.df_operaciones
        
        col_cli = st.session_state.get("c_cliente", df.columns[0])
        col_dir = st.session_state.get("c_direccion", df.columns[0])
        col_caj = st.session_state.get("c_cajas", df.columns[0])
        col_gtda = st.session_state.get("c_guia_tda", df.columns[0])
        
        st.markdown("### 🚛 Configurar una Carga / Camión")
        c_asg1, c_asg2 = st.columns(2)
        with c_asg1:
            placa_input = st.text_input("Placa del Camión", value="AUG-728")
        with c_asg2:
            conductor_input = st.text_input("Nombre del Conductor", value="Kaique Chuquipiondo")
