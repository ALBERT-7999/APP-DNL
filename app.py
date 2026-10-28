import streamlit as st
import pandas as pd

st.sidebar.title("⚙️ Panel de Control")
menu = st.sidebar.selectbox("Navegación", ["Gestión de Reparto", "Gestión de Personal (Conductores)", "Gestión de Flota (Camiones)"])

# --- INICIALIZAR DATOS EN MEMORIA ---
if "df_conductores" not in st.session_state:
    st.session_state.df_conductores = pd.DataFrame(columns=["Nombres", "Apellidos", "DNI"])

if "df_flota" not in st.session_state:
    st.session_state.df_flota = pd.DataFrame(columns=["Placa", "Capacidad Cajas", "Capacidad (m3)"])


# --- MÓDULO 1: GESTIÓN DE CONDUCTORES ---
if menu == "Gestión de Personal (Conductores)":
    st.subheader("👥 Registro de Conductores y Auxiliares")
    
    with st.form("form_conductor"):
        col1, col2, col3 = st.columns(3)
        with col1:
            nombres = st.text_input("Nombres")
        with col2:
            apellidos = st.text_input("Apellidos")
        with col3:
            dni = st.text_input("Número de DNI", max_chars=8)
            
        submitted_c = st.form_submit_button("Registrar Conductor")
        
        if submitted_c:
            if nombres and apellidos and dni:
                nuevo_reg = pd.DataFrame([[nombres, apellidos, dni]], columns=["Nombres", "Apellidos", "DNI"])
                st.session_state.df_conductores = pd.concat([st.session_state.df_conductores, nuevo_reg], ignore_index=True)
                st.success(f"¡Conductor {nombres} {apellidos} registrado con éxito!")
            else:
                st.warning("Por favor completa todos los campos (Nombres, Apellidos y DNI).")

    st.markdown("### 📋 Personal Autorizado Actual")
    if not st.session_state.df_conductores.empty:
        st.dataframe(st.session_state.df_conductores, use_container_width=True)
    else:
        st.info("Aún no hay conductores registrados en esta sesión.")


# --- MÓDULO 2: GESTIÓN DE FLOTA (CAMIONES) ---
elif menu == "Gestión de Flota (Camiones)":
    st.subheader("🚚 Registro y Capacidades de Vehículos")
    
    with st.form("form_flota"):
        col1, col2, col3 = st.columns(3)
        with col1:
            placa = st.text_input("Placa del Vehículo (Ej. D2X-840)")
        with col2:
            cap_cajas = st.number_input("Capacidad Máxima de Cajas", min_value=1, step=1, value=50)
        with col3:
            cap_m3 = st.number_input("Capacidad en Volumen (m³)", min_value=0.1, step=0.5, value=10.0)
            
        submitted_f = st.form_submit_button("Registrar Vehículo")
        
        if submitted_f:
            if placa:
                nueva_placa = pd.DataFrame([[placa.upper(), cap_cajas, cap_m3]], columns=["Placa", "Capacidad Cajas", "Capacidad (m3)"])
                st.session_state.df_flota = pd.concat([st.session_state.df_flota, nueva_placa], ignore_index=True)
                st.success(f"¡Vehículo con placa {placa.upper()} registrado correctamente!")
            else:
                st.warning("Debes ingresar la placa del camión.")

    st.markdown("### 📋 Flota Registrada y Capacidades")
    if not st.session_state.df_flota.empty:
        st.dataframe(st.session_state.df_flota, use_container_width=True)
    else:
        st.info("Aún no hay vehículos registrados en esta sesión.")


# --- MÓDULO 3: GESTIÓN DE REPARTO ---
elif menu == "Gestión de Reparto":
    st.title("📦 Control de Despachos - Roxfarma")
    st.info("Utilice este panel para coordinar las guías, registrar horas de llegada y controlar los KPIs (ER, EN, FH).")
    
    # Aquí puedes usar los datos registrados para los selectboxes de tus despachos
    if not st.session_state.df_conductores.empty:
        lista_conductores = (st.session_state.df_conductores["Nombres"] + " " + st.session_state.df_conductores["Apellidos"]).tolist()
        conductor_asignado = st.selectbox("Conductor Asignado", lista_conductores)
    else:
        st.warning("⚠️ Primero registra al menos un conductor en el Panel de Control.")
        
    if not st.session_state.df_flota.empty:
        lista_placas = st.session_state.df_flota["Placa"].tolist()
        placa_asignada = st.selectbox("Placa del Vehículo", lista_placas)
    else:
        st.warning("⚠️ Primero registra al menos un camión en el Panel de Control.")
