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

# Variables de mapeo por defecto
for key in ["c_cliente", "c_direccion", "c_ubicacion", "c_cajas", "c_pedido", "c_guia_cli", "c_guia_tda"]:
    if key not in st.session_state:
        st.session_state[key] = None

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
            
            # Inicializar columnas operativas en la estructura base
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
            st.write("Selecciona la columna del Excel que corresponde a cada campo:")
            
            cols = df.columns.tolist()
            c1, c2, c3 = st.columns(3)
            with c1:
                st.session_state["c_cliente"] = st.selectbox("Nombre del Cliente", cols, index=0, key="m_cli")
                st.session_state["c_direccion"] = st.selectbox("Dirección del Cliente", cols, index=min(1, len(cols)-1), key="m_dir")
                st.session_state["c_ubicacion"] = st.selectbox("Ubicación / Waze / Maps", cols, index=min(2, len(cols)-1), key="m_ubi")
            with c2:
                st.session_state["c_cajas"] = st.selectbox("Cantidad de Cajas / Bultos", cols, index=min(3, len(cols)-1), key="m_caj")
                st.session_state["c_pedido"] = st.selectbox("Número de Pedido", cols, index=min(4, len(cols)-1), key="m_ped")
            with c3:
                st.session_state["c_guia_cli"] = st.selectbox("Guía de Remisión Cliente", cols, index=min(5, len(cols)-1), key="m_gcli")
                st.session_state["c_guia_tda"] = st.selectbox("Guía Transportista (TDA)", cols, index=min(6, len(cols)-1), key="m_gtda")
                
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
        
        col_cli = st.session_state["c_cliente"] or df.columns[0]
        col_dir = st.session_state["c_direccion"] or df.columns[0]
        col_caj = st.session_state["c_cajas"] or df.columns[0]
        col_gtda = st.session_state["c_guia_tda"] or df.columns[0]
        
        st.markdown("### 🚛 Configurar Vehículo y Conductor")
        c_asg1, c_asg2 = st.columns(2)
        with c_asg1:
            placa_input = st.text_input("Placa del Camión", value="AUG-728")
        with c_asg2:
            conductor_input = st.text_input("Nombre del Conductor", value="Kaique Chuquipiondo")
            
        # Obtener lista de guías no asignadas
        mask_pendientes = df["PLACA_ASIGNADA"] == "Sin Asignar"
        guias_disponibles = df[mask_pendientes][col_gtda].dropna().astype(str).unique().tolist()
        
        st.markdown("#### 📦 Seleccionar Guías a Cargar en este Camión")
        if guias_disponibles:
            guias_seleccionadas = st.multiselect(
                f"Selecciona las Guías TDA para asignar a la Placa {placa_input}:",
                options=guias_disponibles
            )
            
            if st.button("📌 Confirmar Asignación de Pedidos"):
                if guias_seleccionadas:
                    # Asignar directamente sobre el DataFrame global
                    mask = df[col_gtda].astype(str).isin(guias_seleccionadas)
                    st.session_state.df_operaciones.loc[mask, "PLACA_ASIGNADA"] = placa_input.strip().upper()
                    st.session_state.df_operaciones.loc[mask, "CONDUCTOR_ASIGNADO"] = conductor_input.strip()
                    st.success(f"¡Se asignaron {len(guias_seleccionadas)} pedidos a la Placa {placa_input.upper()} ({conductor_input})!")
                    st.rerun()
                else:
                    st.warning("Selecciona al menos una guía del listado.")
        else:
            st.info("🎉 ¡Todos los pedidos del archivo ya han sido asignados a un camión!")

        st.divider()
        st.markdown("### 📊 Resumen de Flota Asignada")
        
        resumen = df.groupby(["PLACA_ASIGNADA", "CONDUCTOR_ASIGNADO"]).size().reset_index(name="Cant. Pedidos")
        st.dataframe(resumen, use_container_width=True)
        
        st.markdown("#### Detalle Completo de Carga:")
        st.dataframe(df[[col_gtda, col_cli, col_dir, col_caj, "PLACA_ASIGNADA", "CONDUCTOR_ASIGNADO"]], use_container_width=True)
        
    else:
        st.warning("⚠️ Primero debes subir el archivo Excel en el módulo '1. Carga de Data'.")


# ==========================================
# MÓDULO 3: CONTROL DE REPARTO (VISTA CONDUCTOR)
# ==========================================
elif menu == "3. Control de Reparto (Vista Conductor)":
    st.subheader("📱 3. Control de Entregas por Camión")
    
    if st.session_state.df_operaciones is not None:
        df_global = st.session_state.df_operaciones
        
        col_cli = st.session_state["c_cliente"] or df_global.columns[0]
        col_dir = st.session_state["c_direccion"] or df_global.columns[0]
        col_ubi = st.session_state["c_ubicacion"] or df_global.columns[0]
        col_caj = st.session_state["c_cajas"] or df_global.columns[0]
        col_ped = st.session_state["c_pedido"] or df_global.columns[0]
        col_gcli = st.session_state["c_guia_cli"] or df_global.columns[0]
        col_gtda = st.session_state["c_guia_tda"] or df_global.columns[0]
        
        placas_disponibles = [p for p in df_global["PLACA_ASIGNADA"].unique() if p != "Sin Asignar"]
        
        if placas_disponibles:
            placa_filtrada = st.selectbox("🚚 Selecciona la Placa a visualizar en ruta:", placas_disponibles)
            
            # Obtener los índices originales de la masa de datos
            indices_camion = df_global[df_global["PLACA_ASIGNADA"] == placa_filtrada].index
            conductor_nom = df_global.loc[indices_camion[0], "CONDUCTOR_ASIGNADO"] if len(indices_camion) > 0 else "Sin Conductor"
            
            st.info(f"📋 Hoja de Ruta - Placa: **{placa_filtrada}** | Conductor: **{conductor_nom}**")
            
            # Avance de entregas
            atendidos = df_global.loc[indices_camion, "ESTADO_ENTREGA"].isin(["EN", "CE"]).sum()
            total_camion = len(indices_camion)
            st.progress(atendidos / total_camion if total_camion > 0 else 0)
            st.caption(f"Progreso en ruta: **{atendidos} de {total_camion} pedidos gestionados**")
            
            st.divider()
            
            opciones_estado = ["ER (En Ruta)", "EN (Entregado)", "FH (Fuera de Hora)", "CE (Cerrado)"]
            map_estado_idx = {"ER": 0, "EN": 1, "FH": 2, "CE": 3}
            
            # Generar tarjetas usando el índice real para asegurar guardado
            for item_num, real_idx in enumerate(indices_camion, start=1):
                row = df_global.loc[real_idx]
                
                cliente_nom = str(row[col_cli])
                direccion_nom = str(row[col_dir])
                ubicacion_url = str(row[col_ubi])
                cajas_cant = str(row[col_caj])
                ped_num = str(row[col_ped])
                guia_cli_num = str(row[col_gcli])
                guia_tda_num = str(row[col_gtda])
                estado_curr = str(row["ESTADO_ENTREGA"])
                obs_curr = str(row["OBSERVACIONES"]) if pd.notna(row["OBSERVACIONES"]) else ""

                with st.container():
                    c_idx, c_det, c_act = st.columns([1, 4, 3])
                    
                    with c_idx:
                        st.markdown(f"### **#{item_num}**")
                    
                    with c_det:
                        st.markdown(f"### **{cliente_nom}**")
                        st.write(f"📍 **Dirección:** {direccion_nom}")
                        st.write(f"📦 **Cajas:** {cajas_cant} | 📄 **Pedido:** {ped_num}")
                        st.write(f"🔖 **G.R. Cliente:** {guia_cli_num} | 🚚 **G.R. TDA:** {guia_tda_num}")
                        
                        if "http" in ubicacion_url.lower():
                            st.markdown(f"🗺️ [Abrir en Mapa / GPS]({ubicacion_url})")
                        else:
                            st.caption(f"📌 **Ubicación:** {ubicacion_url}")
                            
                    with c_act:
                        idx_sel = map_estado_idx.get(estado_curr, 0)
                        
                        nuevo_est = st.selectbox(
                            "Estado", 
                            opciones_estado,
                            index=idx_sel,
                            key=f"st_sel_{real_idx}"
                        )
                        
                        nueva_obs = st.text_input(
                            "Observación", 
                            value=obs_curr,
                            placeholder="Escribe aquí...",
                            key=f"obs_txt_{real_idx}"
                        )
                        
                        if st.button("💾 Guardar Cambios", key=f"btn_save_{real_idx}"):
                            cod_est = nuevo_est.split(" ")[0]
                            st.session_state.df_operaciones.loc[real_idx, "ESTADO_ENTREGA"] = cod_est
                            st.session_state.df_operaciones.loc[real_idx, "OBSERVACIONES"] = nueva_obs
                            st.success(f"¡Pedido #{item_num} guardado correctamente!")
                            st.rerun()
                st.divider()

            # Botón de Descarga Excel
            if st.button("📥 Descargar Reporte Consolidado (Excel)"):
                archivo_final = f"Reporte_{placa_filtrada}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
                df_camion = df_global.loc[indices_camion].copy()
                df_camion.to_excel(archivo_final, index=False)
                with open(archivo_final, "rb") as f:
                    st.download_button("⬇️ Guardar Archivo Excel", f, file_name=archivo_final)
        else:
            st.warning("⚠️ Aún no has asignado pedidos a ningún camión. Ve al Módulo 2 para realizar la asignación.")
    else:
        st.warning("⚠️ No hay data cargada. Sube el Excel en el módulo '1. Carga de Data'.")
