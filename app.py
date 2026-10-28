import streamlit as st
import pandas as pd
import os
from datetime import datetime
import streamlit.components.v1 as components

st.set_page_config(page_title="MEDIPORT - Reparto", page_icon="🚚", layout="centered")

RUTA_STORAGE = "data_ruta_activa.csv"

# ... existing code ...
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

                # AUXILIARES DE TRANSPORTE
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

                    # REGISTRO DE HORAS PERSISTENTES
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

                    # ESTADO Y SECUENCIA
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

                    # OBSERVACIONES Y FOTO
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
                    
                    # Generar filas dinámicas de la tabla a partir de la data capturada
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
                    
                    # Mostrar la vista de hoja previa e imprimible en pantalla
                    components.html(html_for23, height=650, scrolling=True)

            else:
                st.warning("⚠️ No hay pedidos asignados a esta unidad.")
        else:
            st.warning("⚠️ No hay una ruta activa en el sistema. El administrador debe cargar el Excel.")
# ... existing code ...
