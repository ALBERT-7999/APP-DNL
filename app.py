import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="MEDIPORT - Reparto", page_icon="🚚", layout="centered")

# Archivo de persistencia local para compartir data entre distintos dispositivos/celulares
RUTA_STORAGE = "data_ruta_activa.csv"

# --- ESTILOS VISUALES Y BRANDING MEDIPORT ---
st.markdown("""
<style>
    .mediport-logo {
        text-align: center;
        background-color: #004d5a;
        color: white;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    .mediport-logo h1 {
        color: white !important;
        font-weight: 900;
        font-size: 28px;
        margin: 0;
        letter-spacing: 2px;
    }
    .mediport-logo p {
        color: #83b2b8;
        margin: 5px 0 0 0;
        font-size: 13px;
        font-weight: 600;
    }
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

# --- USUARIOS Y CONTRASEÑAS REGISTRADAS ---
USUARIOS = {
    "admin": {"pass": "mediport2026", "rol": "admin", "nombre": "Administrador Operaciones"},
    "kaique": {"pass": "1234", "rol": "conductor", "nombre": "KAIQUE CHUQUIPIONDO CARDENAS"},
    "conductor1": {"pass": "1234", "rol": "conductor", "nombre": "CONDUCTOR MEDIPORT 1"}
}

# --- FUNCIONES DE ALMACENAMIENTO PERSISTENTE ---
def cargar_ruta_disco():
    if os.path.exists(RUTA_STORAGE):
        try:
            return pd.read_csv(RUTA_STORAGE, dtype=str)
        except Exception:
            return None
    return None

def guardar_ruta_disco(df):
    df.to_csv(RUTA_STORAGE, index=False)

# --- MEMORIA DE LA SESIÓN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = None
if "ruta_iniciada" not in st.session_state:
    st.session_state.ruta_iniciada = False


# ==========================================
# PANTALLA DE LOGIN
# ==========================================
if not st.session_state.autenticado:
    st.markdown("""
    <div class="mediport-logo">
        <h1>MEDIPORT</h1>
        <p>SISTEMA DE CONTROL DE REPARTO Y LOGÍSTICA</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("🔑 Iniciar Sesión")
    
    with st.form("form_login"):
        user_input = st.text_input("Usuario", placeholder="Ingresa tu usuario").strip().lower()
        pass_input = st.text_input("Contraseña", type="password", placeholder="Ingresa tu contraseña")
        btn_login = st.form_submit_button("Ingresar al Sistema", type="primary", use_container_width=True)
        
        if btn_login:
            if user_input in USUARIOS and USUARIOS[user_input]["pass"] == pass_input:
                st.session_state.autenticado = True
                st.session_state.usuario_actual = USUARIOS[user_input]
                st.success("¡Acceso correcto!")
                st.rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos.")

else:
    user_info = st.session_state.usuario_actual
    
    st.sidebar.markdown(f"👤 **Usuario:** {user_info['nombre']}")
    st.sidebar.markdown(f"🔰 **Rol:** {user_info['rol'].upper()}")
    
    if st.sidebar.button("🔒 Cerrar Sesión"):
        st.session_state.autenticado = False
        st.session_state.usuario_actual = None
        st.rerun()
        
    st.sidebar.divider()
    
    if user_info["rol"] == "admin":
        menu = st.sidebar.radio("📌 Opciones de Menú", ["1. Cargar Data de Reparto", "2. Vista de Ruta (Conductor)"])
    else:
        menu = "2. Vista de Ruta (Conductor)"

    # ==========================================
    # 1. CARGA DE DATA (ADMIN)
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
                    
                if st.button("🚀 Cargar y Publicar Ruta para Conductores", type="primary", use_container_width=True):
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
                    
                    guardar_ruta_disco(df_normal)
                    st.session_state.ruta_iniciada = False
                    st.success("¡Data publicada con éxito! Todos los conductores ya pueden ver su ruta desde su celular.")
                    
            except Exception as e:
                st.error(f"Error al procesar el Excel: {e}")
                
        df_act = cargar_ruta_disco()
        if df_act is not None:
            st.success(f"Hay una ruta activa publicada con {len(df_act)} pedidos.")
            st.dataframe(df_act.head(5), use_container_width=True)

    # ==========================================
    # 2. VISTA DE RUTA (CONDUCTOR / AUXILIARES)
    # ==========================================
    elif menu == "2. Vista de Ruta (Conductor)":
        df = cargar_ruta_disco()
        
        if df is not None:
            fecha_hoy = datetime.now().strftime("%Y-%m-%d")
            nombre_cond_defecto = user_info["nombre"] if user_info["rol"] == "conductor" else "KAIQUE CHUQUIPIONDO CARDENAS"
            
            st.markdown("### 🚛 Configuración de Cabecera")
            c_head1, c_head2 = st.columns(2)
            with c_head1:
                conductor = st.text_input("Conductor", value=nombre_cond_defecto)
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
                    st.success("¡Ruta Iniciada! Puedes gestionar cada entrega.")
                    st.rerun()
            else:
                st.info("🟢 Ruta en curso. Gestiona entregas, cambia orden, adjunta fotos u observaciones.")

            st.markdown("---")
            
            # --- LISTADO DE PEDIDOS EN TARJETAS ---
            for idx in range(len(df)):
                row = df.iloc[idx]
                num_item = idx + 1
                
                st.markdown(f"#### **#{num_item} · {row['Cliente']}**")
                st.caption(f"📍 {row['Distrito']} · 📄 {row['Guia']} · 📦 {row['Bultos']} bultos")
                
                if "http" in str(row['Ubicacion']).lower():
                    st.markdown(f"🗺️ [Abrir en GPS / Maps]({row['Ubicacion']})")
                
                c_est, c_ord1, c_ord2 = st.columns([2, 1, 1])
                
                with c_est:
                    opciones = ["ER (En Ruta)", "EN (Entregado)", "FH (Fuera de Hora)", "CE (Cerrado)"]
                    map_idx = {"ER": 0, "EN": 1, "FH": 2, "CE": 3}
                    curr_idx = map_idx.get(str(row['Estado']), 0)
                    
                    nuevo_estado = st.selectbox(
                        "Estado",
                        opciones,
                        index=curr_idx,
                        key=f"est_{idx}"
                    )
                    cod_est = nuevo_estado.split(" ")[0]
                    if cod_est != str(row['Estado']):
                        df.at[idx, "Estado"] = cod_est
                        guardar_ruta_disco(df)
                        st.rerun()
                        
                with c_ord1:
                    if idx > 0:
                        if st.button("▲ Subir", key=f"up_{idx}"):
                            df.iloc[idx], df.iloc[idx-1] = df.iloc[idx-1].copy(), df.iloc[idx].copy()
                            guardar_ruta_disco(df)
                            st.rerun()
                            
                with c_ord2:
                    if idx < len(df) - 1:
                        if st.button("▼ Bajar", key=f"dn_{idx}"):
                            df.iloc[idx], df.iloc[idx+1] = df.iloc[idx+1].copy(), df.iloc[idx].copy()
                            guardar_ruta_disco(df)
                            st.rerun()
                
                # --- CARGA DE FOTO DE EVIDENCIA ---
                foto_subida = st.file_uploader(
                    f"📷 Foto Evidencia Guía #{num_item}", 
                    type=["png", "jpg", "jpeg"], 
                    key=f"foto_{idx}"
                )
                
                if foto_subida is not None:
                    df.at[idx, "Foto_Estado"] = "Foto Registrada"
                    guardar_ruta_disco(df)
                
                # --- OBSERVACIÓN ---
                obs_actual = str(row["Observaciones"]) if pd.notna(row["Observaciones"]) else ""
                obs = st.text_input("Observación", value=obs_actual, key=f"obs_{idx}", placeholder="Comentario opcional...")
                if obs != obs_actual:
                    df.at[idx, "Observaciones"] = obs
                    guardar_ruta_disco(df)

                st.divider()

            # --- REPORTES Y CIERRE ---
            if st.button("📄 Finalizar Ruta y Descargar Reporte Excel", use_container_width=True):
                archivo_out = f"Reporte_FOR23_{placa}_{fecha_hoy}.xlsx"
                df.to_excel(archivo_out, index=False)
                with open(archivo_out, "rb") as f:
                    st.download_button("⬇️ Descargar Reporte Consolidado", f, file_name=archivo_out)

        else:
            st.warning("⚠️ Todavía no hay una ruta cargada en el sistema. El administrador debe cargar el Excel del día.")
