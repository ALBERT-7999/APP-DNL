import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="App de Reparto - MediPort", page_icon="📦", layout="wide")

st.markdown("<h1>📦 App de Reparto - MediPort</h1>", unsafe_allow_html=True)
st.markdown("<span>Control de Flota, Ruteo por Zonas (Norte/Sur/Este) y Formato FOR-23</span>", unsafe_allow_html=True)
st.divider()

# --- INICIALIZAR MEMORIA GLOBAL ---
if "df_conductores" not in st.session_state:
    st.session_state.df_conductores = pd.DataFrame(columns=["Nombres", "Apellidos", "DNI"])

if "df_flota" not in st.session_state:
    st.session_state.df_flota = pd.DataFrame(columns=["Placa", "Capacidad Cajas", "Capacidad (m3)"])

if "df_cliente" not in st.session_state:
    st.session_state.df_cliente = None

if "df_final" not in st.session_state:
    st.session_state.df_final = None


# --- MENÚ LATERAL ---
st.sidebar.title("⚙️ Menú Principal")
menu = st.sidebar.selectbox("Navegación", [
    "1. Panel de Control (Personal y Flota)", 
    "2. Ruteo por Zonas (Norte/Sur/Este)", 
    "3. Control de Reparto en Ruta (FOR-23)"
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
# MÓDULO 2: RUTEO POR ZONAS (NORTE / SUR / ESTE) Y ARCHIVOS
# ==========================================
elif menu == "2. Ruteo por Zonas (Norte/Sur/Este)":
    st.subheader("📁 Carga de Documentación y Ruteo por Zonas (Norte / Sur / Este)")
    
    col_up1, col_up2 = st.columns(2)
    
    with col_up1:
        st.markdown("### 📄 1. Archivo del Cliente")
        file_cliente = st.file_uploader("Sube el Excel base del cliente", type=["xlsx", "xls"], key="cli")
        if file_cliente is not None:
            try:
                st.session_state.df_cliente = pd.read_excel(file_cliente)
                st.success("¡Archivo del cliente cargado!")
            except Exception as e:
                st.error(f"Error: {e}")
                
    with col_up2:
        st.markdown("### 📊 2. Archivo Final (Guía Cliente + TDA)")
        file_final = st.file_uploader("Sube el Excel final (Guía Cliente y Guía TDA)", type=["xlsx", "xls"], key="fin")
        if file_final is not None:
            try:
                st.session_state.df_final = pd.read_excel(file_final)
                if "ESTADO_REPARTO" not in st.session_state.df_final.columns:
                    st.session_state.df_final["ESTADO_REPARTO"] = "En Ruta (ER)"
                if "HORA_LLEGADA" not in st.session_state.df_final.columns:
                    st.session_state.df_final["HORA_LLEGADA"] = ""
                st.success("¡Archivo Final cargado con éxito!")
            except Exception as e:
                st.error(f"Error: {e}")

    st.divider()

    if st.session_state.df_final is not None:
        df = st.session_state.df_final
        st.markdown("### 📊 Vista Previa del Archivo Final")
        st.dataframe(df.head(3), use_container_width=True)
        
        columnas_disponibles = df.columns.tolist()
        col_distrito = st.selectbox("Selecciona la columna que indica el DISTRITO en el Archivo Final", columnas_disponibles)
        
        if col_distrito:
            st.markdown("---")
            st.markdown("### 🧭 Selección de Macrozona de Salida (Siguiente Día)")
            
            zona_seleccionada = st.radio("Selecciona la Zona de Reparto:", ["NORTE", "SUR", "ESTE"], horizontal=True)
            
            fecha_manana = (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y")
            st.info(f"📅 Despacho programado para la **Zona {zona_seleccionada}** el día: **{fecha_manana}**")
            
            distritos_unicos = df[col_distrito].dropna().unique().tolist()
            distrito_elegido = st.selectbox(f"Selecciona el Distrito específico (Zona {zona_seleccionada})", distritos_unicos)
            
            if distrito_elegido:
                pedidos_zona = df[df[col_distrito] == distrito_elegido]
                st.write(f"Se encontraron **{len(pedidos_zona)}** registros para el distrito **{distrito_elegido}** (Zona **{zona_seleccionada}**).")
                
                col_asg1, col_asg2 = st.columns(2)
                
                with col_asg1:
                    if not st.session_state.df_flota.empty:
                        placas_disponibles = st.session_state.df_flota["Placa"].tolist()
                        placa_asignada = st.selectbox("Asignar Placa de Camión", placas_disponibles)
                    else:
                        placa_asignada = "Sin vehículo"
                        st.warning("⚠️ Registra vehículos en el Panel de Control.")
                        
                with col_asg2:
                    if not st.session_state.df_conductores.empty:
                        conductores_disponibles = (st.session_state.df_conductores["Nombres"] + " " + st.session_state.df_conductores["Apellidos"]).tolist()
                        conductor_asignado = st.selectbox("Asignar Conductor", conductores_disponibles)
                    else:
                        conductor_asignado = "Sin conductor"
                        st.warning("⚠️ Registra conductores en el Panel de Control.")
                
                if st.button(f"Confirmar Asignación - Zona {zona_seleccionada} (Siguiente Día)"):
                    st.success(f"¡Ruta de la **Zona {zona_seleccionada}** asignada al camión **{placa_asignada}** (Conductor: {conductor_asignado}) para el distrito **{distrito_elegido}** el {fecha_manana}!")
    else:
        st.info("👆 Sube obligatoriamente el **Archivo Final** para habilitar la distribución por Zonas (Norte, Sur y Este).")


# ==========================================
# MÓDULO 3: CONTROL DE REPARTO EN RUTA (FOR-23)
# ==========================================
elif menu == "3. Control de Reparto en Ruta (FOR-23)":
    st.subheader("📋 Formato Digital de Ruta y Control de Entregas (FOR-23)")
    st.info("Vista para conductores: Visualización estricta de N° de Guía (TDA), Cliente y N° de Pedido.")
    
    if st.session_state.df_final is not None:
        df = st.session_state.df_final
        
        c1, c2, c3 = st.columns(3)
        with c1:
            col_guia = st.selectbox("Columna de N° de Guía (TDA / Transportista)", df.columns, key="sel_guia")
        with c2:
            col_cliente = st.selectbox("Columna de Cliente / Farmacia", df.columns, key="sel_cli")
        with c3:
            col_pedido = st.selectbox("Columna de N° de Pedido", df.columns, key="sel_ped")
            
        st.divider()
        st.markdown("### 🔍 Listado de Guías Asignadas en Ruta")
        
        # Extracción segura garantizando que no existan nombres repetidos en pandas
        serie_guia = df[col_guia].astype(str)
        serie_cliente = df[col_cliente].astype(str)
        serie_pedido = df[col_pedido].astype(str)

        df_vista = pd.DataFrame({
            "N° Guía (TDA)": serie_guia.values,
            "Cliente / Farmacia": serie_cliente.values,
            "N° Pedido": serie_pedido.values,
            "Estado Actual": df["ESTADO_REPARTO"].values,
            "Hora Llegada": df["HORA_LLEGADA"].values
        })
        
        st.dataframe(df_vista, use_container_width=True)
        
        st.markdown("---")
        st.markdown("### ✍️ Registrar Gestión de Entrega por Guía")
        
        guia_seleccionada = st.selectbox("Seleccione el N° de Guía a Gestionar", df[col_guia].tolist(), key="sel_gest_guia")
        
        if guia_seleccionada:
            idx = df[df[col_guia] == guia_seleccionada].index[0]
            cliente_info = df.loc[idx, col_cliente]
            pedido_info = df.loc[idx, col_pedido]
            
            st.write(f"**Cliente / Farmacia:** {cliente_info} | **N° Pedido:** {pedido_info}")
            
            col_reg1, col_reg2 = st.columns(2)
            with col_reg1:
                nuevo_estado = st.selectbox("Estado de Entrega", ["En Ruta (ER)", "Entregado (EN)", "Fuera de Hora (FH)"], index=1, key="sel_est")
                hora_ingresada = st.text_input("Hora de Llegada / Entrega (Ej. 14:30)", value=datetime.now().strftime("%H:%M"), key="txt_hora")
            with col_reg2:
                foto_guia = st.file_uploader("Subir Foto de Guía con Sello y V°B° del Cliente", type=["png", "jpg", "jpeg"], key="up_foto")
                
            if st.button("Guardar Registro de Entrega", key="btn_guardar"):
                df.loc[idx, "ESTADO_REPARTO"] = nuevo_estado
                df.loc[idx, "HORA_LLEGADA"] = hora_ingresada
                st.success(f"¡Guía {guia_seleccionada} actualizada correctamente como **{nuevo_estado}** a las **{hora_ingresada}**!")
                
        st.divider()
        if st.button("📥 Generar y Descargar Reporte Final en Excel (FOR-23)", key="btn_descarga"):
            archivo_reporte = f"Reporte_FOR23_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
            df.to_excel(archivo_reporte, index=False)
            with open(archivo_reporte, "rb") as f:
                st.download_button(
                    label="⬇️ Descargar Archivo Excel Consolidado",
                    data=f,
                    file_name=archivo_reporte,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="dl_btn_final"
                )
    else:
        st.warning("⚠️ Primero debes subir el **Archivo Final** en el módulo '2. Ruteo por Zonas (Norte/Sur/Este)'.")
