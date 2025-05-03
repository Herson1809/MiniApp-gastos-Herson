# app.py - MiniApp Auditoría Final Grupo FarmaValue
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from datetime import datetime
import xlsxwriter

# --- TÍTULO PRINCIPAL ---
st.markdown("""
<h1 style='text-align: center; color: white;'>Auditoría a Gastos por País - Grupo FarmaValue_Herson Hernández</h1>
""", unsafe_allow_html=True)

# --- BLOQUE 1: CARGA DE ARCHIVO ---
st.markdown("### ▶️ Sube tu archivo Excel (.xlsx)")
archivo = st.file_uploader("Selecciona tu archivo de gastos", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)

    # --- PREPARACIÓN DE CAMPOS ---
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df['Mes'] = df['Fecha'].dt.strftime('%B')
    df['Año'] = df['Fecha'].dt.year

    resumen_mes = df.groupby('Mes')['Monto'].sum().reindex(['January', 'February', 'March', 'April'])

    # --- BLOQUE 2: VISUALIZACIÓN GRAFICA Y METRICAS ---
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### 📊 Gasto por Mes")
        fig, ax = plt.subplots(figsize=(6, 4))
        colores = ['#3498db', '#f39c12', '#2ecc71', '#9b59b6']
        resumen_mes.dropna().plot(kind='bar', ax=ax, color=colores)
        ax.set_xlabel("Mes")
        ax.set_ylabel("Monto")
        ax.set_title("Gasto Mensual")
        ax.set_xticklabels(resumen_mes.dropna().index, rotation=0)
        ax.get_yaxis().set_visible(False)
        st.pyplot(fig)

    with col2:
        st.markdown("### 🧾 Totales por Mes")
        for mes, valor in resumen_mes.dropna().items():
            st.metric(label=mes, value=f"RD${valor:,.0f}")
        st.markdown("---")
        st.metric(label="Gran Total", value=f"RD${resumen_mes.sum():,.0f}")

    # --- BLOQUE 3: ANÁLISIS POR RIESGO ---
    st.markdown("## 🛑 Tabla de Umbrales de Riesgo")
    st.markdown("""
    <table style='width:100%; text-align:center;'>
        <tr><th>🔴 Crítico</th><th>🟡 Moderado</th><th>🟢 Bajo</th></tr>
        <tr><td>≥ RD$6,000,000</td><td>≥ RD$3,000,000 y < RD$6,000,000</td><td>< RD$3,000,000</td></tr>
    </table>
    """, unsafe_allow_html=True)

    def clasificar_riesgo(monto):
        if monto >= 6000000:
            return '🔴 Crítico'
        elif monto >= 3000000:
            return '🟡 Moderado'
        else:
            return '🟢 Bajo'

    resumen_categoria = df.groupby('Categoria')['Monto'].sum().reset_index()
    resumen_categoria['Grupo de Riesgo'] = resumen_categoria['Monto'].apply(clasificar_riesgo)
    detalle_por_mes = df.pivot_table(index='Categoria', columns='Mes', values='Monto', aggfunc='sum', fill_value=0).reset_index()
    resumen_final = pd.merge(resumen_categoria, detalle_por_mes, on='Categoria', how='left')
    resumen_final['Total general'] = resumen_final.loc[:, ['January', 'February', 'March', 'April']].sum(axis=1)
    resumen_final = resumen_final.sort_values(by='Total general', ascending=False)

    # --- BLOQUE 4: AUDITORÍA SUCURSALES DETALLE ---
    df['Grupo de Riesgo'] = df.groupby('Categoria')['Monto'].transform('sum').apply(clasificar_riesgo)
    total_sucursal = df.groupby('Sucursales')['Monto'].transform('sum')
    df['Gasto Total Sucursal'] = total_sucursal
    df['% Participación'] = df['Monto'] / df['Gasto Total Sucursal']
    df['Prioridad para Revisión'] = df['Descripcion'].apply(
        lambda x: '✅ Sí' if any(p in str(x).lower() for p in ['otros', 'misc', 'vuelto']) else '🔍 No'
    )
    df['Verificado'] = '☐'
    df['No Verificado'] = '☐'
    df['Comentario del Auditor'] = ''

    auditoria_final = df[['Sucursales', 'Grupo de Riesgo', 'Categoria', 'Descripcion', 'Fecha', 'Monto',
                          'Gasto Total Sucursal', '% Participación', 'Prioridad para Revisión',
                          'Verificado', 'No Verificado', 'Comentario del Auditor']]
    auditoria_final = auditoria_final.sort_values(by=['Grupo de Riesgo', '% Participación'], ascending=[True, False])
    auditoria_final['% Participación'] = auditoria_final['% Participación'].apply(lambda x: round(x * 100, 2))

    # --- BLOQUE 5: EXPORTACIÓN ---
    st.markdown("## 📤 Descargar Reporte de Auditoría Completo")
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        wb = writer.book

        # HOJA 1: Resumen por Categoría
        resumen_final_formateado = resumen_final.copy()
        for col in ['January', 'February', 'March', 'April', 'Total general']:
            resumen_final_formateado[col] = resumen_final_formateado[col].apply(lambda x: round(x / 1000, 2))

        resumen_final_formateado.insert(0, 'No', range(1, len(resumen_final_formateado) + 1))
        resumen_final_formateado.to_excel(writer, sheet_name='Resumen por Categoría', index=False, startrow=5)
        ws1 = writer.sheets['Resumen por Categoría']
        ws1.write('A1', "Auditoría grupo Farmavalue", wb.add_format({'bold': True, 'font_color': 'red', 'font_size': 28}))
        ws1.write('A2', "Reporte de gastos del 01 de Enero al 20 de abril del 2025", wb.add_format({'font_size': 12}))
        ws1.write('A3', "Auditor Asignado:", wb.add_format({'font_size': 12}))
        ws1.write('A4', "Fecha de la Auditoría", wb.add_format({'font_size': 12}))

        # HOJA 2: Auditoría Sucursales
        auditoria_final_formateada = auditoria_final.copy()
        auditoria_final_formateada['Monto'] = auditoria_final_formateada['Monto'].apply(lambda x: round(x / 1000, 2))
        auditoria_final_formateada['Gasto Total Sucursal'] = auditoria_final_formateada['Gasto Total Sucursal'].apply(lambda x: round(x / 1000, 2))
        auditoria_final_formateada['Fecha'] = auditoria_final_formateada['Fecha'].dt.strftime('%d-%b-%Y')
        auditoria_final_formateada.to_excel(writer, sheet_name='Auditoría Sucursales', index=False, startrow=5)
        ws2 = writer.sheets['Auditoría Sucursales']
        ws2.write('A1', "Auditoría grupo Farmavalue", wb.add_format({'bold': True, 'font_color': 'red', 'font_size': 28}))
        ws2.write('A2', "Reporte de gastos del 01 de Enero al 20 de abril del 2025", wb.add_format({'font_size': 12}))
        ws2.write('A3', "Auditor Asignado:", wb.add_format({'font_size': 12}))
        ws2.write('A4', "Fecha de la Auditoría", wb.add_format({'font_size': 12}))

    output.seek(0)
    b64 = base64.b64encode(output.read()).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="Cedula_de_Trabajo_de_Auditoria_FINAL_OK.xlsx">📥 Descargar Cedula de Trabajo de Auditoría</a>'
    st.markdown(href, unsafe_allow_html=True)

else:
    st.info("📥 Sube un archivo Excel para comenzar.")
