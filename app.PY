import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración visual para el celular del conductor
st.set_page_config(page_title="MediPort - Reparto", page_icon="🚚", layout="centered")

st.title("📱 App de Reparto - MediPort")
st.caption("Reemplazo Digital FOR-23 (Medicamentos / Roxfarma)")

# 1. Cargar el reporte del sistema
@st.cache_data
def load_data():
    # Carga tu Excel original
    df = pd.read_excel("Reporte_guías_local_1793122189.xlsx")
    
    # Crea las columnas de seguimiento si no existen
    if 'ESTADO_REPARTO' not in df.columns:
        df['ESTADO_REPARTO'] = 'ER' # Por defecto: En Ruta
    if 'HORA_LLEGADA' not in df.columns:
        df['HORA_LLEGADA'] = ''
    if 'HORA_ENTREGA' not in df.columns:
        df['HORA_ENTREGA'] = ''
    if 'FOTO_GUIA' not in df.columns:
        df['FOTO_GUIA'] = 'No'
    return df

if 'df' not in st.session_state:
    st.session_state.df = load_data()

# 2. Cabecera (Reemplaza los datos generales del FOR-23)
with st.expander("1️⃣ Registro de Personal y Vehículo", expanded=True):
    # Extraemos los datos únicos de tu mismo Excel
    conductores = st.session_state.df['CONDUCTOR'].dropna().unique().tolist()
    vehiculos = st.session_state.df['VEHICULO'].dropna().unique().tolist()
    
    conductor = st.selectbox("Conductor:", conductores)
    auxiliar1 = st.text_input("Auxiliar de Transporte 1:")
    auxiliar2 = st.text_input("Auxiliar de Transporte 2:")
    placa = st.selectbox("Placa del Vehículo:", vehiculos)

# 3. Resumen de KPIs en tiempo real
st.markdown("### 📊 Estado de la Ruta")
pedidos_ruta = st.session_state.df[st.session_state.df['CONDUCTOR'] == conductor]

er_count = len(pedidos_ruta[pedidos_ruta['ESTADO_REPARTO'] == 'ER'])
en_count = len(pedidos_ruta[pedidos_ruta['ESTADO_REPARTO'] == 'EN'])
fh_count = len(pedidos_ruta[pedidos_ruta['ESTADO_REPARTO'] == 'FH'])

c1, c2, c3 = st.columns(3)
c1.metric("ER (En Ruta)", er_count)
c2.metric("EN (Entregados)", en_count)
c3.metric("FH (Fuera de Hora)", fh_count)
st.divider()

# 4. Flujo de Trabajo del Auxiliar/Conductor
st.markdown("### 2️⃣ Gestión de Pedidos")
pendientes = pedidos_ruta[pedidos_ruta['ESTADO_REPARTO'] == 'ER']

if pendientes.empty:
    st.success("🎉 ¡Todos los pedidos de este conductor han sido gestionados!")
else:
    # Selector de guía pendiente
    opciones = pendientes.apply(lambda r: f"Guía: {r['GUIA REMISIÓN']} - {r['DESTINATARIO']}", axis=1).to_dict()
    seleccion = st.selectbox("Seleccione el pedido a entregar:", options=list(opciones.keys()), format_func=lambda x: opciones[x])
    
    if seleccion is not None:
        fila = st.session_state.df.loc[seleccion]
        st.info(f"📍 **Destino:** {fila['DIRECCIÓN DESTINO']} ({fila['UBIGEO DESTINO']})\n"
                f"📦 **Cajas a entregar:** {fila['CANT. CAJAS']}\n"
                f"🏢 **Cliente:** {fila['CLIENTE']}")
        
        # Paso 1: Marcar Llegada
        if not fila['HORA_LLEGADA']:
            if st.button("📍 Llegué al Punto (Registrar Hora)", use_container_width=True):
                st.session_state.df.at[seleccion, 'HORA_LLEGADA'] = datetime.now().strftime("%H:%M:%S")
                st.rerun()
        else:
            st.success(f"✅ Llegada registrada a las: {fila['HORA_LLEGADA']}")
            
            # Paso 2: Foto y Entrega
            st.write("Tomar foto de la guía con V°B° del cliente:")
            foto = st.camera_input("📸 Cámara")
            fuera_de_hora = st.checkbox("⚠️ Marcar como Pedido Fuera de Hora (FH)")
            
            if st.button("✅ Confirmar Entrega y Salida", type="primary", use_container_width=True):
                if foto is None:
                    st.error("Es obligatorio tomar la foto de la guía sellada para finalizar.")
                else:
                    # Registra la hora de partida/entrega y cambia el KPI
                    st.session_state.df.at[seleccion, 'HORA_ENTREGA'] = datetime.now().strftime("%H:%M:%S")
                    st.session_state.df.at[seleccion, 'ESTADO_REPARTO'] = 'FH' if fuera_de_hora else 'EN'
                    st.session_state.df.at[seleccion, 'FOTO_GUIA'] = "Foto Capturada"
                    st.rerun()

st.divider()

# 5. Emisión del Reporte
st.markdown("### 3️⃣ Cierre y Reporte")
if st.button("📄 Emitir Reporte (Reemplazo FOR-23)", use_container_width=True):
    archivo_final = f"Reporte_Ruta_{conductor.split()[0]}_{datetime.now().strftime('%d%m%Y')}.xlsx"
    
    # Filtramos la data del conductor y la exportamos
    df_export = st.session_state.df[st.session_state.df['CONDUCTOR'] == conductor].copy()
    
    # Agregamos los auxiliares al reporte
    df_export['AUXILIAR 1'] = auxiliar1
    df_export['AUXILIAR 2'] = auxiliar2
    
    df_export.to_excel(archivo_final, index=False)
    
    with open(archivo_final, "rb") as f:
        st.download_button(
            label="📥 Descargar Excel con Tiempos y KPIs",
            data=f,
            file_name=archivo_final,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )