import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="App de Reparto - MediPort", page_icon="📦", layout="wide")

st.markdown("<h1>📦 App de Reparto - MediPort</h1>", unsafe_allow_html=True)
st.markdown("<span>Control de Flota, Ruteo por Distritos y Despachos - Roxfarma</span>", unsafe_allow_html=True)
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
    "2. Ruteo y Asignación por Distritos", 
    "3. Control de Reparto en Ruta"
])


# ==========================================
# MÓDULO 1: PANEL DE CONTROL (PERSONAL Y FLOTA)
# ==========================================
if menu == "1. Panel de Control (Personal y Flota)":
    st.subheader("👥 Registro de Conductores y 🚚 Flota de Camiones")
    
    col_c, col_f = st.columns(2)
    
    with col_c:
        st.markdown("### Registrar Conductor")
        with st.form("form_cond"):
            nom = st.text_input("Nombres")
            ape = st.text_input("Apellidos")
            dni = st.text_input("Número de DNI", max_chars=8)
            btn_c = st.form_submit_button("Guardar Conductor")
            if btn_c:
                if nom and ape and dni:
                    nuevo_c = pd.DataFrame([[nom, ape, dni]], columns=["Nombres", "Apellidos", "DNI"])
                    st.session_state.df_conductores = pd.concat([st.session_state.df_conductores, nuevo_c], ignore_index=True)
                    st.success(f"Conductor {nom} registrado.")
                else:
                    st.warning("Completa todos los campos del conductor.")
        
        st.markdown("**Personal Actual:**")
        if not st.session_state.df_conductores.empty:
            st.dataframe(st.session_state.df_conductores, use_container_width=True)
        else:
            st.info("Sin conductores registrados.")

    with col_f:
        st.markdown("### Registrar Camión / Vehículo")
        with st.form("form_veh"):
            placa = st.text_input("Placa (Ej. DFSK-2022)")
            cajas = st.number_input("Capacidad Máxima de Cajas", min_value=1, value=50)
            m3 = st.number_input("Capacidad en Volumen (m³)", min_value=0.1, value=10.0)
            btn_f = st.form_submit_button("Guardar Vehículo")
            if btn_f:
                if placa:
                    nuevo_v = pd.DataFrame([[placa.upper(), cajas, m3]], columns=["Placa", "Capacidad Cajas", "Capacidad (m3)"])
                    st.session_state.df_flota = pd.concat([st.session_state.df_flota, nuevo_v], ignore_index=True)
                    st.success(f"Vehículo {placa.upper()} registrado.")
                else:
                    st.warning("Ingresa la placa del vehículo.")
                    
        st.markdown("**Flota Actual:**")
        if not st.session_state.df_flota.empty:
            st.dataframe(st.session_state.df_flota, use_container_width=True)
        else:
            st.info("Sin vehículos registrados.")


# ==========================================
# MÓDULO 2: RUTEO Y ASIGNACIÓN POR DISTRITOS
# ==========================================
elif menu == "2. Ruteo y Asignación por Distritos":
    st.subheader("🗺️ Ruteo, Asignación de Placas y Programación (Siguiente Día)")
    
    # Cargar Excel de Guías
    uploaded_file = st.file_uploader("Sube tu archivo Excel de Guías de Roxfarma", type=["xlsx", "xls"])
    
    if uploaded_file is not None:
        try:
            st.session_state.df_pedidos = pd.read_excel(uploaded_file)
            st.success("¡Archivo Excel cargado exitosamente!")
        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")

    if st.session_state.df_pedidos is not None:
        df = st.session_state.df_pedidos
        st.markdown("### 📊 Vista previa de Pedidos Cargados")
        st.dataframe(df.head(), use_container_width=True)
        
        # Buscar columna de distrito de forma inteligente
        columnas_disponibles = df.columns.tolist()
        col_distrito = st.selectbox("Selecciona la columna que indica el DISTRITO en tu Excel", columnas_disponibles)
        
        if col_distrito:
            distritos_unicos = df[col_distrito].dropna().unique().tolist()
            
            st.markdown("---")
            st.markdown("### 🚚 Panel de Asignación por Distrito para el Siguiente Día")
            
            fecha_manana = (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y")
            st.info(f"📅 Fecha programada de despacho: **{fecha_manana}**")
            
            distrito_elegido = st.selectbox("Selecciona el Distrito a Rutear", distritos_unicos)
            
            if distrito_elegido:
                # Filtrar pedidos del distrito
                pedidos_distrito = df[df[col_distrito] == distrito_elegido]
                st.write(f"Se encontraron **{len(pedidos_distrito)}** pedidos/guías para el distrito: **{distrito_elegido}**")
                
                # Opciones de asignación
                col_asg1, col_asg2 = st.columns(2)
                
                with col_asg1:
                    if not st.session_state.df_flota.empty:
                        placas_disponibles = st.session_state.df_flota["Placa"].tolist()
                        placa_asignada = st.selectbox("Asignar Placa de Camión", placas_disponibles)
                    else:
                        placa_asignada = "Sin vehículo"
                        st.warning("Registra vehículos en el Panel de Control.")
                        
                with col_asg2:
                    if not st.session_state.df_conductores.empty:
                        conductores_disponibles = (st.session_state.df_conductores["Nombres"] + " " + st.session_state.df_conductores["Apellidos"]).tolist()
                        conductor_asignado = st.selectbox("Asignar Conductor", conductores_disponibles)
                    else:
                        conductor_asignado = "Sin conductor"
                        st.warning("Registra conductores en el Panel de Control.")
                
                if st.button("Confirmar Asignación para el Siguiente Día"):
                    st.success(f"¡Ruta asignada con éxito al camión **{placa_asignada}** (Conductor: {conductor_asignado}) para el distrito **{distrito_elegido}** el día {fecha_manana}!")
    else:
        st.info("👆 Por favor, sube un archivo Excel para habilitar el ruteo por distritos.")


# ==========================================
# MÓDULO 3: CONTROL DE REPARTO EN RUTA
# ==========================================
elif menu == "3. Control de Reparto en Ruta":
    st.subheader("📍 Seguimiento de Entregas (ER, EN, FH)")
    st.info("Aquí los conductores o el coordinador visualizan las guías asignadas en ruta, registran horas y toman fotos de V°B°.")
    
    if st.session_state.df_pedidos is not None:
        st.dataframe(st.session_state.df_pedidos, use_container_width=True)
    else:
        st.warning("No hay pedidos cargados. Sube el Excel en el módulo de Ruteo.")
