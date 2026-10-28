import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="App de Reparto - MediPort", page_icon="📦", layout="wide")

# Estilos CSS
st.markdown("""
<style>
    .for23-header { background-color: #004d5a; color: white; padding: 15px; border-radius: 12px; margin-bottom: 15px; }
    .for23-sub { font-size: 11px; color: #83b2b8; font-weight: bold; }
    .for23-driver { font-size: 20px; font-weight: 800; margin: 5px 0; }
    .badge-en { background-color: #00875a; color: white; padding: 4px 10px; border-radius: 6px; font-weight: bold; float: right; }
    .badge-er { background-color: #ff9900; color: white; padding: 4px 10px; border-radius: 6px; font-weight: bold; float: right; }
</style>
""", unsafe_allow_html=True)

# Memoria global
if "df_conductores" not in st.session_state:
    st.session_state.df_conductores = pd.DataFrame(columns=["Nombres", "Apellidos", "DNI"])
if "df_flota" not in st.session_state:
    st.session_state.df_flota = pd.DataFrame(columns=["Placa", "Capacidad Cajas", "Capacidad (m3)"])
if "df_final" not in st.session_state:
    st.session_state.df_final = None

st.sidebar.title("⚙️ Menú Principal")
menu = st.sidebar.selectbox("Navegación", [
    "1. Panel de Control (Personal y Flota)", 
    "2. Ruteo Ágil por Zonas (Norte/Sur/Este)", 
    "3. Control de Reparto en Ruta (Vista FOR-23)"
])

# Módulo 1: Control Flota y Conductores
if menu == "1. Panel de Control (Personal y Flota)":
    st.subheader("👥 Registro de Conductores y 🚚 Flota de Camiones")
    col_c, col_f = st.columns(2)
    with col_c:
        st.markdown("### Registrar Conductor")
        with st.form("form_cond"):
            nom, ape, dni = st.text_input("Nombres"), st.text_input("Apellidos"), st.text_input("DNI", max_chars=8)
            if st.form_submit_button("Guardar Conductor") and nom and ape and dni:
                st.session_state.df_conductores = pd.concat([st.session_state.df_conductores, pd.DataFrame([[nom, ape, dni]], columns=["Nombres", "Apellidos", "DNI"])], ignore_index=True)
                st.success(f"Conductor {nom} registrado.")
        st.dataframe(st.session_state.df_conductores, use_container_width=True)
    with col_f:
        st.markdown("### Registrar Camión")
        with st.form("form_veh"):
            placa, cajas, m3 = st.text_input("Placa"), st.number_input("Cajas", min_value=1, value=50), st.number_input("m³", min_value=0.1, value=10.0)
            if st.form_submit_button("Guardar Vehículo") and placa:
                st.session_state.df_flota = pd.concat([st.session_state.df_flota, pd.DataFrame([[placa.upper(), cajas, m3]], columns=["Placa", "Capacidad Cajas", "Capacidad (m3)"])], ignore_index=True)
                st.success(f"Vehículo {placa.upper()} registrado.")
        st.dataframe(st.session_state.df_flota, use_container_width=True)

# Módulo 2: Ruteo por Zonas
elif menu == "2. Ruteo Ágil por Zonas (Norte/Sur/Este)":
    st.subheader("📁 Carga de Documentación y Ruteo por Zonas")
    file_final = st.file_uploader("Sube el Excel Final (Guía Cliente + TDA)", type=["xlsx", "xls"], key="fin")
    if file_final is not None:
        st.session_state.df_final = pd.read_excel(file_final)
        if "ESTADO_REPARTO" not in st.session_state.df_final.columns:
            st.session_state.df_final["ESTADO_REPARTO"] = "ER"
        st.success("¡Archivo Final cargado con éxito!")

    if st.session_state.df_final is not None:
        df = st.session_state.df_final
        col_dist = st.selectbox("Columna de DISTRITO", df.columns)
        col_asg1, col_asg2 = st.columns(2)
        with col_asg1:
            st.session_state["placa_activa"] = st.selectbox("Asignar Camión", st.session_state.df_flota["Placa"].tolist() if not st.session_state.df_flota.empty else ["AUG-728"])
        with col_asg2:
            st.session_state["conductor_activo"] = st.selectbox("Asignar Conductor", (st.session_state.df_conductores["Nombres"] + " " + st.session_state.df_conductores["Apellidos"]).tolist() if not st.session_state.df_conductores.empty else ["KAIQUE CHUQUIPIONDO CARDENAS"])
        if st.button("Confirmar Ruta"):
            st.success("¡Ruta configurada con éxito!")

# Módulo 3: Formato FOR-23
elif menu == "3. Control de Reparto en Ruta (Vista FOR-23)":
    if st.session_state.df_final is not None:
        df = st.session_state.df_final
        conductor_nom = st.session_state.get("conductor_activo", "KAIQUE CHUQUIPIONDO CARDENAS")
        placa_cod = st.session_state.get("placa_activa", "AUG-728")
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        
        st.markdown(f"""
        <div class="for23-header">
            <div class="for23-sub">FOR-23 · {fecha_hoy} · {placa_cod}</div>
            <div class="for23-driver">{conductor_nom.upper()}</div>
        </div>
        """, unsafe_allow_html=True)
        
        ca1, ca2 = st.columns(2)
        aux1 = ca1.text_input("Auxiliar 1", value="FERNANDO MARTÍNEZ")
        aux2 = ca2.text_input("Auxiliar 2", value="RONALD CAJAVILCA")

        st.dataframe(df.head(10), use_container_width=True)

        if st.button("📄 Generar e Imprimir Formato FOR-23 Oficial"):
            archivo_out = f"Reporte_FOR23_{fecha_hoy}.xlsx"
            df.to_excel(archivo_out, index=False)
            st.success("¡Documento FOR-23 listo para impresión y envío!")
    else:
        st.warning("⚠️ Primero carga el archivo de operaciones en el Módulo 2.")
