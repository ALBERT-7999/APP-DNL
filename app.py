import streamlit as st
import pandas as pd
import os
from datetime import datetime
import streamlit.components.v1 as components

st.set_page_config(page_title="MEDIPORT - Reparto", page_icon="🚚", layout="centered")

RUTA_STORAGE = "data_ruta_activa.csv"

# --- ESTILOS VISUALES MÓVILES Y DE TARJETAS DINÁMICAS ---
st.markdown("""
<style>
    .stButton>button {
        border-radius: 10px !important;
        font-weight: bold !important;
        height: 3em !important;
        width: 100% !important;
    }
    
    .card-pedido {
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.06);
    }
    
    .card-er { background-color: #fff9e6; border: 1px solid #ffe599; border-left: 8px solid #f1c40f; }
    .card-er .card-title { color: #b78103; }
    
    .card-en { background-color: #eef9f1; border: 1px solid #b7e4c7; border-left: 8px solid #27ae60; }
    .card-en .card-title { color: #1e7e34; }
    
    .card-fh { background-color: #fdf2f2; border: 1px solid #f5c6cb; border-left: 8px solid #e74c3c; }
    .card-fh .card-title { color: #bd2130; }
    
    .card-ce { background-color: #f2f2f2; border: 1px solid #d6d6d6; border-left: 8px solid #7f8c8d; }
    .card-ce .card-title { color: #495057; }

    .card-title { font-size: 18px; font-weight: bold; margin-bottom: 5px; }
    .card-info { font-size: 14px; color: #333333; margin-bottom: 3px; }
    
    .metric-box {
        background-color: #f4f6f8;
        border-radius: 10px;
        padding: 12px;
        text-align: center;
        border: 1px solid #dcdcdc;
    }
    .metric-value { font-size: 22px; font-weight: bold; color: #004d5a; }
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

# --- USUARIOS REGISTRADOS ---
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
                    
                    # Opción con verificación de Placa
                    opciones_placa = ["[USAR PLACA POR DEFECTO: AUG-728]"] + cols
                    col_plc_sel = st.selectbox("Placa del Vehículo (Opcional)", opciones_placa, index=0)
                    
                if st.button("🚀 Publicar Rutas para el Día", type="primary"):
                    cond_serie = df[col_cond].astype(str).str.replace(r'\s+', ' ', regex=True).str.strip().str.upper()
                    
                    if col_plc_sel == "[USAR PLACA POR DEFECTO: AUG-728]":
                        placa_serie = "AUG-728"
                    else:
                        placa_serie = df[col_plc_sel].astype(str).str.replace(r'\s+', ' ', regex=True).str.strip().str.upper()
                        # Si la columna seleccionada tiene datos tipo comprobante (cambian fila a fila), forzar valor agrupado
                        if df[col_plc_sel].nunique() == len(df):
                            placa_serie = "AUG-728"
                    
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
                        "Hora_Partida": "",
                        "Observaciones": "",
                        "Foto_Estado": "Sin Foto"
                    })
                    
                    guardar_ruta_disco(df_normal)
                    st.success("¡Data cargada y agrupada correctamente!")
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Error al procesar el Excel: {e}")
                
        df_act = cargar_ruta_disco()
        if df_act is not None and not df_act.empty:
            num_unidades = df_act.groupby(["Placa", "Conductor"]).ngroups
            st.success(f"Carga Activa: {len(df_act)} pedidos registrados en {num_unidades} ruta(s) de vehículo.")
            
            # Tabla de resumen agrupada
            st.markdown("#### 📊 Resumen Consolidado de Rutas Activas:")
            resumen_df = df_act.groupby(["Placa", "Conductor"]).size().reset_index(name="Cant. Pedidos")
            st.dataframe(resumen_df, use_container_width=True)

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
            conductor_sel = sel_unidad.split(" - ")[1] if " - " in sel_unidad else ""
            
            indices_ruta = df_global[(df_global["Placa"] == placa_activa) & (df_global["Conductor"] == conductor_sel)].index.tolist()
            if not indices_ruta:
                indices_ruta = df_global[df_global["Placa"] == placa_activa].index.tolist()
            
            if indices_ruta:
                conductor_nombre = df_global.loc[indices_ruta[0], "Conductor"]
                
                total_p = len(indices_ruta)
                atendidos = (df_global.loc[indices_ruta, "Estado"].isin(["EN", "FH", "CE"])).sum()
                porcentaje = int((atendidos / total_p) * 100) if total_p > 0 else 0

                st.markdown(f"""
                <div class="for23-header">
                    <div style="font-size:11px; color:#83b2b8; font-weight:bold;">FOR-23 · {fecha_hoy} · {placa_activa}</div>
                    <div style="font-size:18px; font-weight:bold; margin:4px 0;">{conductor_nombre}</div>
                    <div style="font-size:14px; font-weight:bold; margin-top:5px;">
                        Avance General: {atendidos} de {total_p} gestionados ({porcentaje}%)
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.progress(atendidos / total_p if total_p > 0 else 0.0)

                c_aux1, c_aux2 = st.columns(2)
                with c_aux1:
                    aux1_val = st.text_input("Auxiliar de Transporte 1", value="", key=f"aux1_{placa_activa}", placeholder="Nombre Auxiliar 1")
                with c_aux2:
                    aux2_val = st.text_input("Auxiliar de Transporte 2", value="", key=f"aux2_{placa_activa}", placeholder="Nombre Auxiliar 2")

                st.divider()

                # --- TARJETAS MÓVILES POR PEDIDO ---
                for pos, real_idx in enumerate(indices_ruta):
                    row = df_global.loc[real_idx]
                    num_item = pos + 1
                    
                    cliente = str(row['Cliente'])
                    distrito = str(row['Distrito'])
                    guia = str(row['Guia'])
                    bultos = str(row['Bultos'])
                    ubi_url = str(row['Ubicacion'])
                    estado_actual = str(row['Estado']).lower()
                    
                    card_class = f"card-{estado_actual}" if estado_actual in ["er", "en", "fh", "ce"] else "card-er"
                    
                    st.markdown(f"""
                    <div class="card-pedido {card_class}">
                        <div class="card-title">#{num_item} · {cliente}</div>
                        <div class="card-info">📍 <b>Distrito:</b> {distrito}</div>
                        <div class="card-info">📄 <b>Guía:</b> {guia} | 📦 <b>Bultos:</b> {bultos}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if "http" in ubi_url.lower():
                        st.markdown(f"🗺️ [**Abrir en GPS / Maps**]({ubi_url})")

                    c_h1, c_h2 = st.columns(2)
                    with c_h1:
                        key_hl = f"txt_hl_{real_idx}"
                        hl_val = str(row["Hora_Llegada"])
                        
                        if st.button(f"⏱️ LLEGADA", key=f"btn_hl_{real_idx}"):
                            hora_actual = datetime.now().strftime("%H:%M")
                            df_global.at[real_idx, "Hora_Llegada"] = hora_actual
                            st.session_state[key_hl] = hora_actual
                            guardar_ruta_disco(df_global)
                            st.rerun()
                        
                        input_hl = st.text_input("Hora Llegada", value=hl_val, key=key_hl, label_visibility="collapsed", placeholder="Llegada HH:MM")
                        if input_hl != hl_val:
                            df_global.at[real_idx, "Hora_Llegada"] = input_hl
                            guardar_ruta_disco(df_global)

                    with c_h2:
                        key_he = f"txt_he_{real_idx}"
                        he_val = str(row["Hora_Entrega"])
                        
                        if st.button(f"✅ ENTREGA", key=f"btn_he_{real_idx}"):
                            hora_actual = datetime.now().strftime("%H:%M")
                            df_global.at[real_idx, "Hora_Entrega"] = hora_actual
                            df_global.at[real_idx, "Hora_Partida"] = hora_actual
                            df_global.at[real_idx, "Estado"] = "EN"
                            st.session_state[key_he] = hora_actual
                            guardar_ruta_disco(df_global)
                            st.rerun()
                            
                        input_he = st.text_input("Hora Entrega", value=he_val, key=key_he, label_visibility="collapsed", placeholder="Entrega HH:MM")
                        if input_he != he_val:
                            df_global.at[real_idx, "Hora_Entrega"] = input_he
                            guardar_ruta_disco(df_global)

                    c_est, c_up, c_dn = st.columns([2, 1, 1])
                    with c_est:
                        opciones = ["ER (En Ruta)", "EN (Entregado)", "FH (Fuera de Hora)", "CE (Cerrado)"]
                        map_idx = {"ER": 0, "EN": 1, "FH": 2, "CE": 3}
                        curr_st_idx = map_idx.get(str(row['Estado']), 0)
                        
                        st_sel = st.selectbox("Estado", opciones, index=curr_st_idx, key=f"st_{real_idx}")
                        cod_st = st_sel.split(" ")[0]
                        if cod_st != str(row['Estado']):
                            df_global.at[real_idx, "Estado"] = cod_st
                            guardar_ruta_disco(df_global)
                            st.rerun()
                            
                    with c_up:
                        if pos > 0:
                            if st.button("▲ Subir", key=f"up_{real_idx}"):
                                prev_idx = indices_ruta[pos - 1]
                                df_global.iloc[real_idx], df_global.iloc[prev_idx] = df_global.iloc[prev_idx].copy(), df_global.iloc[real_idx].copy()
                                guardar_ruta_disco(df_global)
                                st.rerun()
                    with c_dn:
                        if pos < len(indices_ruta) - 1:
                            if st.button("▼ Bajar", key=f"dn_{real_idx}"):
                                next_idx = indices_ruta[pos + 1]
                                df_global.iloc[real_idx], df_global.iloc[next_idx] = df_global.iloc[next_idx].copy(), df_global.iloc[real_idx].copy()
                                guardar_ruta_disco(df_global)
                                st.rerun()

                    obs_val = str(row["Observaciones"]) if pd.notna(row["Observaciones"]) else ""
                    txt_obs = st.text_input("Observación", value=obs_val, key=f"obs_{real_idx}", placeholder="Escribir observación...")
                    if txt_obs != obs_val:
                        df_global.at[real_idx, "Observaciones"] = txt_obs
                        guardar_ruta_disco(df_global)

                    foto_file = st.file_uploader(f"📷 Adjuntar Foto (#{num_item})", type=["png", "jpg", "jpeg"], key=f"foto_{real_idx}")
                    if foto_file is not None:
                        df_global.at[real_idx, "Foto_Estado"] = "Foto Carga Ok"
                        guardar_ruta_disco(df_global)

                    st.divider()

                # BOTÓN DE FINALIZAR RUTA E IMPRESIÓN OFICIAL FOR-23
                st.markdown("---")
                if st.button("🏁 FINALIZAR RUTA Y GENERAR FOR-23 OFICIAL", type="primary", use_container_width=True):
                    st.session_state[f"mostrar_impresion_{placa_activa}"] = True

                if st.session_state.get(f"mostrar_impresion_{placa_activa}", False):
                    st.success("¡Ruta finalizada! A continuación se presenta la vista de impresión del FOR-23:")
                    
                    filas_html = ""
                    for pos, real_idx in enumerate(indices_ruta):
                        r = df_global.loc[real_idx]
                        obs_txt = str(r['Observaciones']) if r['Observaciones'] else (r['Estado'] if r['Estado'] != "ER" else "")
                        filas_html += f"""
                        <tr>
                          <td>{fecha_hoy}</td>
                          <td>TDA-08{pos+1:02d}</td>
                          <td>{r['Guia']}</td>
                          <td>{r['Guia']}</td>
                          <td>{r['Bultos']}</td>
                          <td>PF</td>
                          <td>15 - 25 °C</td>
                          <td>NO</td>
                          <td>-</td>
                          <td>{r['Distrito']}</td>
                          <td>08:00</td>
                          <td>{r['Hora_Llegada']}</td>
                          <td>10</td>
                          <td>{r['Hora_Entrega']}</td>
                          <td>{obs_txt}</td>
                          <td>V°B°</td>
                        </tr>
                        """
                        
                    html_for23 = f"""
                    <!DOCTYPE html><html><head><meta charset="UTF-8">
                    <style>
                        body {{ font-family: Arial, sans-serif; font-size: 8pt; color: #000; margin: 0; padding: 10px; }}
                        table {{ width: 100%; border-collapse: collapse; margin-bottom: 5px; table-layout: fixed; }}
                        td, th {{ border: 1px solid #000; padding: 3px 2px; text-align: center; font-size: 6.5pt; word-wrap: break-word; }}
                        th {{ background-color: #f2f2f2; font-weight: bold; }}
                        .header-title {{ font-size: 10pt; font-weight: bold; text-align: center; }}
                        .meta-td {{ text-align: left; font-size: 8pt; font-weight: bold; padding: 4px; }}
                        .leyenda {{ border: 1px solid #000; padding: 4px; font-size: 7pt; font-weight: bold; margin: 5px 0; }}
                        .btn-print {{ background-color: #004d5a; color: white; border: none; padding: 10px 18px; font-weight: bold; border-radius: 6px; cursor: pointer; margin-bottom: 10px; width: 100%; font-size: 11pt; }}
                        @media print {{ .btn-print {{ display: none; }} }}
                    </style>
                    </head><body>
                    <button class="btn-print" onclick="window.print()">🖨️ IMPRIMIR HOJA DE RUTA FOR-23 (PDF)</button>

                    <table>
                      <tr>
                        <td style="width:25%; font-weight:bold; font-size:9pt;">MEDIPORT-TDA</td>
                        <td style="width:50%;" class="header-title">PLANIFICACION Y REGISTRO DE HOJA DE RUTA</td>
                        <td style="width:25%; text-align:left; font-size:7pt;">Código: FOR-23<br>Versión/Revisión: 01.2<br>Fecha: 15-12-2025</td>
                      </tr>
                    </table>

                    <table>
                      <tr>
                        <td class="meta-td" style="width:60%;">CONDUCTOR SUPERVISOR: {conductor_nombre}</td>
                        <td class="meta-td" style="width:40%;">PLACA DEL VEHICULO: {placa_activa}</td>
                      </tr>
                      <tr>
                        <td class="meta-td">AUXILIAR DE TRANSPORTE 1: {aux1_val}</td>
                        <td class="meta-td">AUXILIAR DE TRANSPORTE 2: {aux2_val}</td>
                      </tr>
                    </table>

                    <table>
                      <thead>
                        <tr>
                          <th colspan="10">PLANIFICACION DE LA HOJA DE RUTA</th>
                          <th colspan="6">REGISTRO DE LA HOJA DE RUTA</th>
                        </tr>
                        <tr>
                          <th style="width:6%;">FECHA</th>
                          <th style="width:6%;">GR. TDA</th>
                          <th style="width:8%;">DOC. REF.</th>
                          <th style="width:7%;">GR. CLIENTE</th>
                          <th style="width:5%;">BULTOS</th>
                          <th style="width:5%;">TIPO PROD.</th>
                          <th style="width:9%;">TEMP. (°C)</th>
                          <th style="width:6%;">EMBALAJE</th>
                          <th style="width:6%;">TIEMPO EMB.</th>
                          <th style="width:8%;">DISTRITO</th>
                          <th style="width:6%;">H. SALIDA</th>
                          <th style="width:6%;">H. LLEGADA</th>
                          <th style="width:5%;">ESPERA</th>
                          <th style="width:6%;">H. PARTIDA</th>
                          <th style="width:11%;">OBSERVACIONES</th>
                          <th style="width:4%;">V°B°</th>
                        </tr>
                      </thead>
                      <tbody>
                        {filas_html}
                      </tbody>
                    </table>

                    <div class="leyenda">
                        LEYENDA: PF:PRODUCTO FARMACEUTICO / DM: DISPOSITIVO MEDICO / PS: PRODUCTO SANITARIO / OTR: OTROS
                    </div>

                    <table style="margin-top:15px;">
                      <tr>
                        <td style="height:35px; vertical-align:bottom;"><b>CONDUCTOR SUPERVISOR</b></td>
                        <td style="height:35px; vertical-align:bottom;"><b>AUXILIAR DE TRANSPORTE 1</b></td>
                        <td style="height:35px; vertical-align:bottom;"><b>AUXILIAR DE TRANSPORTE 2</b></td>
                      </tr>
                    </table>
                    </body></html>
                    """
                    
                    components.html(html_for23, height=650, scrolling=True)

            else:
                st.warning("⚠️ No hay pedidos asignados a esta unidad.")
        else:
            st.warning("⚠️ No hay una ruta activa en el sistema. El administrador debe cargar el Excel.")

    # ==========================================
    # 3. DASHBOARD / ESTADO DE LA RUTA
    # ==========================================
    elif menu == "3. Dashboard / Avance de Ruta":
        st.title("📊 Resumen y Porcentaje de Ruta")
        
        df_global = cargar_ruta_disco()
        if df_global is not None and not df_global.empty:
            df_unidades = df_global[["Placa", "Conductor"]].drop_duplicates()
            opciones_unidades = [f"{row['Placa']} - {row['Conductor']}" for _, row in df_unidades.iterrows()]
            
            sel_unidad_dash = st.selectbox("Seleccionar Vehículo a Monitorear:", opciones_unidades)
            placa_dash = sel_unidad_dash.split(" - ")[0]
            
            df_dash = df_global[df_global["Placa"] == placa_dash]
            
            total_pedidos = len(df_dash)
            cant_en = (df_dash["Estado"] == "EN").sum()
            cant_er = (df_dash["Estado"] == "ER").sum()
            cant_fh = (df_dash["Estado"] == "FH").sum()
            cant_ce = (df_dash["Estado"] == "CE").sum()
            
            cant_gestionados = cant_en + cant_fh + cant_ce
            porcentaje_avance = int((cant_gestionados / total_pedidos) * 100) if total_pedidos > 0 else 0
            
            pct_en = round((cant_en / total_pedidos) * 100, 1) if total_pedidos > 0 else 0
            pct_er = round((cant_er / total_pedidos) * 100, 1) if total_pedidos > 0 else 0
            pct_fh = round((cant_fh / total_pedidos) * 100, 1) if total_pedidos > 0 else 0
            pct_ce = round((cant_ce / total_pedidos) * 100, 1) if total_pedidos > 0 else 0

            st.markdown(f"### Avance Total de Ruta: **{porcentaje_avance}% Completado** ({cant_gestionados} de {total_pedidos})")
            st.progress(porcentaje_avance / 100)
            
            st.divider()
            
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.markdown(f"""<div class="metric-box"><div style="color:#27ae60;" class="metric-value">{cant_en}</div><div style="font-size:12px;"><b>ENTREGADOS (EN)</b><br>{pct_en}%</div></div>""", unsafe_allow_html=True)
            with m2:
                st.markdown(f"""<div class="metric-box"><div style="color:#f1c40f;" class="metric-value">{cant_er}</div><div style="font-size:12px;"><b>EN RUTA (ER)</b><br>{pct_er}%</div></div>""", unsafe_allow_html=True)
            with m3:
                st.markdown(f"""<div class="metric-box"><div style="color:#e74c3c;" class="metric-value">{cant_fh}</div><div style="font-size:12px;"><b>FUERA HORA (FH)</b><br>{pct_fh}%</div></div>""", unsafe_allow_html=True)
            with m4:
                st.markdown(f"""<div class="metric-box"><div style="color:#7f8c8d;" class="metric-value">{cant_ce}</div><div style="font-size:12px;"><b>CERRADOS (CE)</b><br>{pct_ce}%</div></div>""", unsafe_allow_html=True)

            st.divider()
            st.markdown("### 📋 Detalle Consolidado de la Ruta:")
            st.dataframe(df_dash[["Cliente", "Distrito", "Guia", "Estado", "Hora_Llegada", "Hora_Entrega", "Observaciones"]], use_container_width=True)
            
        else:
            st.warning("⚠️ No hay datos cargados actualmente.")
