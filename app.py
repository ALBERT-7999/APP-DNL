import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="App de Reparto - Roxfarma", page_icon="📦", layout="centered")

# Estilos CSS personalizados para la interfaz tipo FOR-23
st.markdown("""
<style>
    .for23-header {
        background-color: #004d5a;
        color: white;
        padding: 18px;
        border-radius: 12px;
        margin-bottom: 12px;
    }
    .for23-sub {
        font-size: 11px;
        color: #83b2b8;
        font-weight: bold;
        letter-spacing: 0.5px;
    }
    .for23-driver {
        font-size: 20px;
        font-weight: 800;
        margin: 4px 0;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

# --- ESTADOS DE LA SESIÓN ---
if "df_ruta" not in st.session_state:
    st.session_state.df_ruta = None
if "ruta_iniciada" not in st.session_state:
    st.session_state.ruta_iniciada = False

# --- NAVEGACIÓN ---
menu = st.sidebar.radio("📌 Menú Principal", ["1. Cargar Data de Reparto", "2. Vista de Ruta (Conductor)"])


# ==========================================
# 1. CARGA DE DATA
# ==========================================
if menu == "1. Cargar Data de Reparto":
    st.title("📁 Carga del Archivo de Reparto")
    st.info("Sube el Excel con las guías/pedidos del día para enviarlos directamente a la ruta.")
    
    archivo = st.file_uploader("Seleccionar Excel (.xlsx, .xls)", type=["xlsx", "xls"])
    
    if archivo is not None:
        try:
            df = pd.read_excel(archivo)
            
            st.markdown("### 📊 Seleccionar Columnas de la Data")
            cols = df.columns.tolist()
            
            c1, c2 = st.columns(2)
            with c1:
                col_cli = st.selectbox("Cliente", cols, index=0)
                col_dis = st.selectbox("Distrito / Zona", cols, index=min(1, len(cols)-1))
                col_gui = st.selectbox("N° Guía / Comprobante", cols, index=min(2, len(cols)-1))
            with c2:
                col_bul = st.selectbox("Bultos / Cajas", cols, index=min(3, len(cols)-1))
                col_ubi = st.selectbox("Ubicación GPS / Dirección", cols, index=min(4, len(cols)-1))
                
            if st.button("🚀 Cargar y Crear Ruta", type="primary"):
                df_normal = pd.DataFrame({
                    "Cliente": df[col_cli].astype(str),
                    "Distrito": df[col_dis].astype(str),
                    "Guia": df[col_gui].astype(str),
                    "Bultos": df[col_bul].astype(str),
                    "Ubicacion": df[col_ubi].astype(str),
                    "Estado": "ER",
                    "Observaciones": "",
                    "Foto_Estado": "Sin Foto"
                })
                
                st.session_state.df_ruta = df_normal
                st.session_state.ruta_iniciada = False
                st.success("¡Data cargada con éxito! Ve a la pestaña '2. Vista de Ruta (Conductor)'.")
                
        except Exception as e:
            st.error(f"Error al procesar el Excel: {e}")
            
    elif st.session_state.df_ruta is not None:
        st.success("Hay una ruta cargada en memoria lista para trabajar.")
        st.dataframe(st.session_state.df_ruta.head(5), use_container_width=True)


# ==========================================
# 2. VISTA DE RUTA (CONDUCTOR / AUXILIARES)
# ==========================================
elif menu == "2. Vista de Ruta (Conductor)":
    if st.session_state.df_ruta is not None:
        df = st.session_state.df_ruta
        
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        
        st.markdown("### 🚛 Configuración de Cabecera")
        c_head1, c_head2 = st.columns(2)
        with c_head1:
            conductor = st.text_input("Conductor", value="KAIQUE CHUQUIPIONDO CARDENAS")
            placa = st.text_input("Placa / Código", value="AUG-728")
        with c_head2:
            aux1 = st.text_input("Auxiliar 1", value="", placeholder="Nombre Auxiliar 1")
            aux2 = st.text_input("Auxiliar 2", value="", placeholder="Nombre Auxiliar 2")

        total_p = len(df)
        atendidos = (df["Estado"].isin(["EN", "CE"])).sum()
        progreso = atendidos / total_p if total_p > 0 else 0.0

        st.markdown(f"""
        <div class="for23-header">
            <div class="for23-sub">FOR-23 · {fecha_hoy} · {placa.upper()}</div>
            <div class="for23-driver">{conductor.upper()}</div>
            <div style="font-size: 13px; font-weight: bold; margin-top: 8px; margin-bottom: 6px;">
                {atendidos} de {total_p} atendidos
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.progress(progreso)
        st.divider()

        if not st.session_state.ruta_iniciada:
            if st.button("▶️ INICIAR RUTA", type="primary", use_container_width=True):
                st.session_state.ruta_iniciada = True
                st.success("¡Ruta Iniciada! Ahora puedes gestionar cada entrega.")
                st.rerun()
        else:
            st.info("🟢 Ruta en curso. Puedes reordenar pedidos, cambiar estado, adjuntar foto y registrar observaciones.")

        st.markdown("---")
        
        # --- LISTADO DE PEDIDOS ---
        for idx in range(len(df)):
            row = df.iloc[idx]
            num_item = idx + 1
            
            st.markdown(f"#### **#{num_item} · {row['Cliente']}**")
            st.caption(f"📍 {row['Distrito']} · 📄 {row['Guia']} · 📦 {row['Bultos']} bultos")
            
            if "http" in row['Ubicacion'].lower():
                st.markdown(f"🗺️ [Abrir en GPS / Maps]({row['Ubicacion']})")
            
            c_est, c_ord1, c_ord2 = st.columns([2, 1, 1])
            
            with c_est:
                opciones = ["ER (En Ruta)", "EN (Entregado)", "FH (Fuera de Hora)", "CE (Cerrado)"]
                map_idx = {"ER": 0, "EN": 1, "FH": 2, "CE": 3}
                curr_idx = map_idx.get(row['Estado'], 0)
                
                nuevo_estado = st.selectbox(
                    "Estado",
                    opciones,
                    index=curr_idx,
                    key=f"est_{idx}"
                )
                cod_est = nuevo_estado.split(" ")[0]
                if cod_est != row['Estado']:
                    st.session_state.df_ruta.at[idx, "Estado"] = cod_est
                    st.rerun()
                    
            with c_ord1:
                if idx > 0:
                    if st.button("▲ Subir", key=f"up_{idx}"):
                        st.session_state.df_ruta.iloc[idx], st.session_state.df_ruta.iloc[idx-1] = (
                            st.session_state.df_ruta.iloc[idx-1].copy(),
                            st.session_state.df_ruta.iloc[idx].copy()
                        )
                        st.rerun()
                        
            with c_ord2:
                if idx < len(df) - 1:
                    if st.button("▼ Bajar", key=f"dn_{idx}"):
                        st.session_state.df_ruta.iloc[idx], st.session_state.df_ruta.iloc[idx+1] = (
                            st.session_state.df_ruta.iloc[idx+1].copy(),
                            st.session_state.df_ruta.iloc[idx].copy()
                        )
                        st.rerun()
            
            # --- CARGA DE FOTO DE EVIDENCIA DE ENTREGA ---
            foto_subida = st.file_uploader(
                f"📷 Tomar/Subir Foto de Guía Sellada (#{num_item})", 
                type=["png", "jpg", "jpeg"], 
                key=f"foto_{idx}"
            )
            
            if foto_subida is not None:
                st.session_state.df_ruta.at[idx, "Foto_Estado"] = "Foto Registrada"
                st.success(f"¡Foto de evidencia cargada para #{num_item}!")
            
            # --- OBSERVACIÓN ---
            obs = st.text_input("Observación", value=row["Observaciones"], key=f"obs_{idx}", placeholder="Comentario opcional...")
            if obs != row["Observaciones"]:
                st.session_state.df_ruta.at[idx, "Observaciones"] = obs

            st.divider()

        # Botón de Cierre y Exportación de Reporte Final
        if st.button("📄 Finalizar Ruta y Descargar Reporte Excel", use_container_width=True):
            archivo_out = f"Reporte_FOR23_{placa}_{fecha_hoy}.xlsx"
            st.session_state.df_ruta.to_excel(archivo_out, index=False)
            with open(archivo_out, "rb") as f:
                st.download_button("⬇️ Descargar Reporte Consolidado", f, file_name=archivo_out)

    else:
        st.warning("⚠️ Primero sube el archivo de reparto en la pestaña '1. Cargar Data de Reparto'.")
