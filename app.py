import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="MEDIPORT - Reparto", page_icon="🚚", layout="centered")

RUTA_STORAGE = "data_ruta_activa.csv"

# --- ESTILOS VISUALES MÓVILES CON DINAMISMO DE COLORES ---
st.markdown("""
<style>
    .stButton>button {
        border-radius: 10px !important;
        font-weight: bold !important;
        height: 3em !important;
        width: 100% !important;
    }
    
    /* Clases de Tarjetas Dinámicas por Estado */
    .card-pedido {
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.06);
    }
    
    /* EN RUTA (Amarillo / Naranja) */
    .card-er {
        background-color: #fff9e6;
        border: 1px solid #ffe599;
        border-left: 8px solid #f1c40f;
    }
    .card-er .card-title { color: #b78103; }
    
    /* ENTREGADO (Verde) */
    .card-en {
        background-color: #eef9f1;
        border: 1px solid #b7e4c7;
        border-left: 8px solid #27ae60;
    }
    .card-en .card-title { color: #1e7e34; }
    
    /* FUERA DE HORA (Rojo) */
    .card-fh {
        background-color: #fdf2f2;
        border: 1px solid #f5c6cb;
        border-left: 8px solid #e74c3c;
    }
    .card-fh .card-title { color: #bd2130; }
    
    /* CERRADO (Gris) */
    .card-ce {
        background-color: #f2f2f2;
        border: 1px solid #d6d6d6;
        border-left: 8px solid #7f8c8d;
    }
    .card-ce .card-title { color: #495057; }

    .card-title {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .card-info {
        font-size: 14px;
        color: #333333;
        margin-bottom: 3px;
    }
    .metric-box {
        background-color: #f4f6f8;
        border-radius: 10px;
        padding: 12px;
        text-align: center;
        border: 1px solid #dcdcdc;
    }
    .metric-value {
        font-size: 22px;
        font-weight: bold;
        color: #004d5a;
    }
    .for23-header {
        background-color: #004d5a;
        color: white;
        padding: 18px;
        border-radius: 12px;
        margin-bottom: 15px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- USUARIOS Y CONTRASEÑAS REGISTRADAS ---
USUARIOS = {
    "admin": {"pass": "mediport2026", "rol": "admin", "nombre": "Administrador Operaciones"},
    "kaique": {"pass": "1234", "rol": "conductor", "nombre": "KAIQUE CHUQUIPIONDO CARDENAS"},
    "conductor1": {"pass": "1234", "rol": "conductor", "nombre": "CONDUCTOR MEDIPORT 1"}
}

def cargar_ruta_disco():
    if os.path.exists(RUTA_STORAGE):
        try:
            return pd.read_csv(RUTA_STORAGE, dtype=str).fillna("")
        except Exception:
            return None
    return None

def guardar_ruta_disco(df):
    df.to_csv(RUTA_STORAGE, index=False)

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = None


# ==========================================
# PANTALLA DE LOGIN
# ==========================================
if not st.session_state.autenticado:
    st.markdown("""
    <div class="for23-header">
        <h1 style="margin:0; font-size:26px;">MEDIPORT</h1>
        <p style="margin:5px 0 0 0; color:#83b2b8; font-size:12px;">SISTEMA MÓVIL DE LOGÍSTICA Y REPARTO</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("🔑 Iniciar Sesión")
    
    with st.form("form_login"):
        user_input = st.text_input("Usuario", placeholder="Ej. kaique").strip().lower()
        pass_input = st.text_input("Contraseña", type="password", placeholder="••••••••")
        btn_login = st.form_submit_button("🚀 Ingresar", type="primary")
        
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
        menu = st.sidebar.radio("📌 Menú de Navegación", [
            "1. Cargar Data de Reparto", 
            "2. Mi Ruta en Campo (FOR-23)", 
            "3. Dashboard / Avance de Ruta"
        ])
    else:
        menu = st.sidebar.radio("📌 Menú Conductor", [
            "2. Mi Ruta en Campo (FOR-23)", 
            "3. Dashboard / Avance de Ruta"
        ])

    # ==========================================
    # 1. CARGA DE DATA (ADMINISTRADOR)
    # ==========================================
    if menu == "1. Cargar Data de Reparto":
        st.title("📁 Carga del Archivo Consolidado")
        st.info("Sube el Excel con el ruteo del día para ser compartido a los celulares.")
        
        archivo = st.file_uploader("Seleccionar Excel (.xlsx, .xls)", type=["xlsx", "xls"])
        
        if archivo is not None:
            try:
                df = pd.read_excel(archivo)
                st.markdown("### 📊 Mapeo de Columnas del Excel")
                cols = df.columns.tolist()
                
                c1, c2 = st.columns(2)
                with c1:
                    col_cli = st.selectbox("Nombre del Cliente", cols, index=0)
                    col_dis = st.selectbox("Distrito / Zona", cols, index=min(1, len(cols)-1))
                    col_gui = st.selectbox("N° Guía / Comprobante", cols, index=min(2, len(cols)-1))
                    col_cond = st.selectbox("Conductor Asignado", cols, index=min(3, len(cols)-1))
                with c2:
                    col_bul = st.selectbox("Bultos / Cajas", cols, index=min(4, len(cols)-1))
                    col_ubi = st.selectbox("Ubicación GPS / Dirección", cols, index=min(5, len(cols)-1))
                    col_plc = st.selectbox("Placa del Vehículo", cols, index=min(6, len(cols)-1))
                    
                if st.button("🚀 Publicar Rutas para el Día", type="primary"):
                    cond_serie = df[col_cond].astype(str).str.replace(r'\s+', ' ', regex=True).str.strip().str.upper()
                    placa_serie = df[col_plc].astype(str).str.replace(r'\s+', ' ', regex=True).str.strip().str.upper()
                    
                    df_normal = pd.DataFrame({
                        "Conductor": cond_serie,
                        "Placa": placa_serie,
                        "Cliente": df[col_cli].astype(str),
                        "Distrito": df[col_dis].astype(str),
                        "Guia": df[col_gui].astype(str),
                        "Bultos": df[col_bul].astype(str),
                        "Ubicacion": df[col_ubi].astype(str),
                        "Estado": "ER",
                        "Hora_Llegada": "",
                        "Hora_Entrega": "",
                        "Observaciones": "",
                        "Foto_Estado": "Sin Foto"
                    })
                    
                    guardar_ruta_disco(df_normal)
                    st.success("¡Data cargada correctamente! Todos los conductores ya pueden acceder.")
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Error al procesar el Excel: {e}")
                
        df_act = cargar_ruta_disco()
        if df_act is not None and not df_act.empty:
            st.success(f"Carga Activa: {len(df_act)} pedidos registrados en {df_act['Placa'].nunique()} vehículo(s).")
            st.dataframe(df_act[["Placa", "Conductor", "Cliente", "Guia"]].head(5), use_container_width=True)

    # ==========================================
    # 2. VISTA DE RUTA EN CAMPO (FOR-23 MÓVIL)
    # ==========================================
    elif menu == "2. Mi Ruta en Campo (FOR-23)":
        df_global = cargar_ruta_disco()
        
        if df_global is not None and not df_global.empty:
            fecha_hoy = datetime.now().strftime("%Y-%m-%d")
            
            df_unidades = df_global[["Placa", "Conductor"]].drop_duplicates()
            opciones_unidades = [f"{row['Placa']} - {row['Conductor']}" for _, row in df_unidades.iterrows()]
            
            sel_unidad = st.selectbox("🚚 Vehículo / Ruta Seleccionada:", opciones_unidades)
            placa_activa = sel_unidad.split(" - ")[0]
            
            indices_ruta = df_global[df_global["Placa"] == placa_activa].index.tolist()
            
            if indices_ruta:
                conductor_nombre = df_global.loc[indices_ruta[0], "Conductor"]
                
                total_p = len(indices_ruta)
                atendidos = (df_global.loc[indices_ruta, "Estado"].isin(["EN", "CE"])).sum()
                porcentaje = int((atendidos / total_p) * 100) if total_p > 0 else 0

                st.markdown(f"""
                <div class="for23-header">
                    <div style="font-size:11px; color:#83b2b8; font-weight:bold;">FOR-23 · {fecha_hoy} · {placa_activa}</div>
                    <div style="font-size:18px; font-weight:bold; margin:4px 0;">{conductor_nombre}</div>
                    <div style="font-
