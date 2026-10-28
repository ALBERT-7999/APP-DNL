import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Control de Reparto - Roxfarma", page_icon="🚚", layout="wide")

st.markdown("<h1>🚚 Sistema de Control de Reparto y Ruteo</h1>", unsafe_allow_html=True)
st.markdown("<span>Gestión simplificada: Carga de Data, Ruteo y Control de Entregas</span>", unsafe_allow_html=True)
st.divider()

# --- MEMORIA DE LA SESIÓN ---
if "df_operaciones" not in st.session_state:
    st.session_state.df_operaciones = None

# --- MENÚ DE NAVEGACIÓN ---
menu = st.sidebar.radio("📌 Menú de Operaciones", [
    "1. Carga de Data", 
    "2. Ruteo y Asignación", 
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
            
            # Inicializar columnas por defecto si no existen
            if "ESTADO_ENTREGA" not in df.columns:
                df["ESTADO_ENTREGA"] = "ER"  # En Ruta por defecto
            if "HORA_LLEGADA" not in df.columns:
                df["HORA_LLEGADA"] = ""
                
            st.session_state.df_operaciones = df
            st.success("¡Archivo cargado correctamente en el sistema!")
            
            st.markdown("### 📊 Mapeo de Campos Obligatorios")
            st.write("Selecciona las columnas correspondientes de tu Excel para que el sistema las organice:")
            
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
# MÓDULO 2: RUTEO Y ASIGNACIÓN
# ==========================================
elif menu == "2. Ruteo y Asignación":
    st.subheader("🗺️ 2. Ruteo y Organiación de Entregas")
    
    if st.session_state.df_operaciones is not None:
        df = st.session_state.df_operaciones
        
        # Obtener nombres de columnas mapeadas
        col_cli = st.session_state.get("c_cliente", df.columns[0])
        col_dir = st.session_state.get("c_direccion", df.columns[0])
        col_caj = st.session_state.get("c_cajas", df.columns[0])
        col_gtda = st.session_state.get("c_guia_tda", df.columns[0])
        col_ubi = st.session_state.get("c_ubicacion", df.columns[0])
        
        st.markdown("### 🚛 Configuración de la Ruta")
        c_asg1, c_asg2, c_asg3 = st.columns(3)
        with c_asg1:
            conductor = st.text_input("Nombre del Conductor", value="Kaique Chuquipiondo")
        with c_asg2:
            placa = st.text_input("Placa del Vehículo", value="AUG-728")
        with c_asg3:
            total_cajas = pd.to_numeric(df[col_caj], errors="coerce").sum()
            st.metric("Total Cajas en Carga", f"{int(total_cajas) if not pd.isna(total_cajas) else 0} Cajas")

        st.divider()
        st.markdown("### 📋 Listado Consolidado para Despacho")
        
        df_ruteo = pd.DataFrame({
            "Guía TDA": df[col_gtda],
            "Cliente": df[col_cli],
            "Dirección": df[col_dir],
            "Cajas": df[col_caj],
            "Ubicación": df[col_ubi]
        })
        
        st.dataframe(df_ruteo, use_container_width=True)
        
    else:
        st.warning("⚠️ Primero debes subir el archivo Excel en el módulo '1. Carga de Data'.")


# ==========================================
# MÓDULO 3: CONTROL DE REPARTO (VISTA CONDUCTOR)
# ==========================================
elif menu == "3. Control de Reparto (Vista Conductor)":
    st.subheader("📱 3. Control de Entregas en Ruta")
    
    if st.session_state.df_operaciones is not None:
        df = st.session_state.df_operaciones
        
        # Mapeo de columnas
        col_cli = st.session_state.get("c_cliente", df.columns[0])
        col_dir = st.session_state.get("c_direccion", df.columns[0])
        col_ubi = st.session_state.get("c_ubicacion", df.columns[0])
        col_caj = st.session_state.get("c_cajas", df.columns[0])
        col_ped = st.session_state.get("c_pedido", df.columns[0])
        col_gcli = st.session_state.get("c_guia_cli", df.columns[0])
        col_gtda = st.session_state.get("c_guia_tda", df.columns[0])
        
        # Métricas de avance
        total = len(df)
        entregados = len(df[df["ESTADO_ENTREGA"] == "EN"])
        st.progress(entregados / total if total > 0 else 0)
        st.caption(f"Progreso de entrega: **{entregados} de {total} atendidos**")
        
        st.divider()
        
        # Vista individual por Tarjeta
        for idx, row in df.iterrows():
            cliente_nom = str(row[col_cli])
            direccion_nom = str(row[col_dir])
            ubicacion_url = str(row[col_ubi])
            cajas_cant = str(row[col_caj])
            ped_num = str(row[col_ped])
            guia_cli_num = str(row[col_gcli])
            guia_tda_num = str(row[col_gtda])
            estado_curr = str(row["ESTADO_ENTREGA"])
            
            with st.container():
                c_idx, c_det, c_act = st.columns([1, 5, 2])
                
                with c_idx:
                    st.markdown(f"### **#{idx + 1}**")
                
                with c_det:
                    st.markdown(f"### **{cliente_nom}**")
                    st.write(f"📍 **Dirección:** {direccion_nom}")
                    st.write(f"📦 **Cajas:** {cajas_cant} | 📄 **Pedido:** {ped_num}")
                    st.write(f"🔖 **G.R. Cliente:** {guia_cli_num} | 🚚 **G.R. TDA:** {guia_tda_num}")
                    
                    if "http" in ubicacion_url.lower():
                        st.markdown(f"🗺️ [Ver Ubicación en Mapa / GPS]({ubicacion_url})")
                    else:
                        st.caption(f"📌 **Ubicación/Ref:** {ubicacion_url}")
                        
                with c_act:
                    # Selector de estado directo por pedido
                    nuevo_est = st.selectbox(
                        "Estado", 
                        ["ER (En Ruta)", "EN (Entregado)", "FH (Fuera de Hora)"],
                        index=0 if estado_curr == "ER" else (1 if estado_curr == "EN" else 2),
                        key=f"st_sel_{idx}"
                    )
                    
                    if st.button("Guardar Cambios", key=f"btn_save_{idx}"):
                        cod_est = "EN" if "EN" in nuevo_est else ("FH" if "FH" in nuevo_est else "ER")
                        df.loc[idx, "ESTADO_ENTREGA"] = cod_est
                        st.success(f"¡Pedido #{idx+1} actualizado!")
                        st.rerun()
            st.divider()

        # Exportar Reporte Final
        if st.button("📥 Descargar Reporte Final de Entregas (Excel)"):
            archivo_final = f"Reporte_Entregas_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
            df.to_excel(archivo_final, index=False)
            with open(archivo_final, "rb") as f:
                st.download_button("⬇️ Guardar Archivo Excel", f, file_name=archivo_final)
    else:
        st.warning("⚠️ No hay data cargada. Sube el Excel en el módulo '1. Carga de Data'.")
