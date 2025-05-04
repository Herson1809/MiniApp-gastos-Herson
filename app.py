# app.py - Versión 85% MiniApp Auditoría a Gastos - Grupo FarmaValue

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import xlsxwriter

# ---- TÍTULO PRINCIPAL ----
st.markdown("<h1 style='text-align: center; color: white;'>Auditoría a Gastos por País - Grupo FarmaValue_Herson Hernández</h1>", unsafe_allow_html=True)

# ---- CARGA DE ARCHIVO ----
st.markdown("### ▶️ Sube tu archivo Excel base")
archivo = st.file_uploader("Selecciona tu archivo de gastos", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df['Mes'] = df['Fecha'].dt.strftime('%B')

    orden_meses = ['January', 'February', 'March', 'April']
    df['Mes'] = pd.Categorical(df['Mes'], categories=orden_meses, ordered=True)

    # ---- BLOQUE 1: GRAFICA Y TOTALES MENSUALES ----
    resumen_mes = df.groupby('Mes')['Monto'].sum().reindex(orden_meses)

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### 📊 Gasto mensual por categoría")
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

    # ---- BLOQUE 2: TABLA DE UMBRALES ----
    st.markdown("## 🛑 Tabla de Umbrales de Riesgo")
    st.markdown("""
    <table style='width:100%; text-align:center;'>
        <tr><th>🔴 Crítico</th><th>🟡 Moderado</th><th>🟢 Bajo</th></tr>
        <tr><td>≥ RD$6,000,000</td><td>≥ RD$3,000,000 y < RD$6,000,000</td><td>< RD$3,000,000</td></tr>
    </table>
    """, unsafe_allow_html=True)

    # ---- BLOQUE 3: ANÁLISIS POR RIESGO ----
    st.markdown("## 🔍 Análisis por Nivel de Riesgo")

    def clasificar_riesgo(monto_total):
        if monto_total >= 6000000:
            return "🔴 Crítico"
        elif monto_total >= 3000000:
            return "🟡 Moderado"
        else:
            return "🟢 Bajo"

    tabla = df.copy()
    tabla['Grupo_Riesgo'] = tabla.groupby('Categoria')['Monto'].transform('sum').apply(clasificar_riesgo)

    resumen = pd.pivot_table(tabla, index=['Categoria', 'Grupo_Riesgo'], columns='Mes', values='Monto', aggfunc='sum', fill_value=0).reset_index()
    resumen['Total general'] = resumen[orden_meses].sum(axis=1)
    resumen = resumen.sort_values(by='Total general', ascending=False).reset_index(drop=True)
    resumen.insert(0, 'No', resumen.index + 1)

    # ---- BLOQUE 4: FILTRO DE RIESGO ----
    opciones = ['Ver Todos'] + sorted(resumen['Grupo_Riesgo'].unique())
    riesgo_opcion = st.selectbox("Selecciona un grupo de riesgo:", options=opciones)

    if riesgo_opcion == 'Ver Todos':
        tabla_filtrada = resumen.copy()
    else:
        tabla_filtrada = resumen[resumen['Grupo_Riesgo'] == riesgo_opcion].copy()

    total_row = {
        'No': '',
        'Categoria': 'TOTAL GENERAL',
        'Grupo_Riesgo': '',
        'January': tabla_filtrada['January'].sum(),
        'February': tabla_filtrada['February'].sum(),
        'March': tabla_filtrada['March'].sum(),
        'April': tabla_filtrada['April'].sum(),
        'Total general': tabla_filtrada['Total general'].sum()
    }
    tabla_filtrada = pd.concat([tabla_filtrada, pd.DataFrame([total_row])], ignore_index=True)

    for col in orden_meses + ['Total general']:
        tabla_filtrada[col] = tabla_filtrada[col].apply(lambda x: f"{x:,.2f}" if pd.notna(x) and isinstance(x, (int, float)) else x)

    st.dataframe(tabla_filtrada[['No', 'Categoria', 'Grupo_Riesgo'] + orden_meses + ['Total general']], use_container_width=True)

    # ---- BLOQUE 5: DESCARGABLE FINAL ----
    st.markdown("## 📥 Descargar Cédula de Trabajo de Auditoría")

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        wb = writer.book

        # HOJA 1: RESUMEN POR CATEGORÍA
        ws1 = wb.add_worksheet('Resumen por Categoría')
        writer.sheets['Resumen por Categoría'] = ws1
        ws1.write('A1', 'Auditoría grupo Farmavalue', wb.add_format({'bold': True, 'font_size': 28, 'font_color': 'red'}))
        ws1.write('A2', 'Reporte de gastos del 01 de Enero al 20 de abril del 2025', wb.add_format({'font_size': 12}))
        ws1.write('A3', 'Auditor Asignado:', wb.add_format({'font_size': 12}))
        ws1.write('A4', 'Fecha de la Auditoría', wb.add_format({'font_size': 12}))

        resumen_final = resumen[['No', 'Categoria', 'Grupo_Riesgo'] + orden_meses + ['Total general']]
        resumen_final.to_excel(writer, sheet_name='Resumen por Categoría', startrow=5, index=False)

        formato_miles = wb.add_format({'num_format': '#,##0.00'})
        for col_idx in range(3, 8):
            ws1.set_column(col_idx, col_idx, 14, formato_miles)

        total_row = len(resumen_final) + 6
        ws1.write(total_row, 1, 'TOTAL GENERAL')
        for col_idx, col in enumerate(orden_meses + ['Total general'], start=3):
            letra = chr(65 + col_idx)
            ws1.write_formula(total_row, col_idx, f'=SUM({letra}7:{letra}{total_row})', formato_miles)

        # HOJA 2: CÉDULA AUDITORÍA
        ws2 = wb.add_worksheet('Cédula Auditoría')
        writer.sheets['Cédula Auditoría'] = ws2
        columnas = ['Sucursal', 'Grupo de Riesgo', 'Categoría', 'Descripción', 'Fecha',
                    'Monto del Gasto', 'Gasto Total de la Sucursal', '% Participación',
                    '¿Revisar?', 'Verificado (☐)', 'No Verificado (☐)', 'Comentario del Auditor']

        for idx, col in enumerate(columnas):
            ws2.write(0, idx, col)

        # Puedes insertar aquí los datos detallados si ya tienes ese dataframe construido.

    output.seek(0)
    b64 = base64.b64encode(output.read()).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="Cedula_Resumen_Categoria_FINAL_OK.xlsx">📄 Descargar Excel Consolidado</a>'
    st.markdown(href, unsafe_allow_html=True)

else:
    st.info("📥 Sube un archivo Excel para comenzar.")
