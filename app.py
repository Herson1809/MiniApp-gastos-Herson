import streamlit as st
import pandas as pd
import plotly.express as px

# Título de la App
st.title("📈 Auditoría a Gastos por País - Grupo FarmaValue_Herson Hernández")

# Subida del archivo
st.subheader("📄 Sube tu archivo Excel base")
archivo = st.file_uploader("Selecciona el archivo de gastos", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)

    # Conversión y limpieza de datos
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce')

    # Calcular totales por Categoría y mes
    df['Mes'] = df['Fecha'].dt.month_name()
    tabla = pd.pivot_table(df, values='Monto', index=['Categoria', 'Grupo de Riesgo'], columns='Mes', aggfunc='sum', fill_value=0).reset_index()
    tabla['Total general'] = tabla.iloc[:, 2:].sum(axis=1)

    # Dar formato de miles con comas
    for col in tabla.columns[2:]:
        tabla[col] = tabla[col].apply(lambda x: f"RD${x:,.2f}")

    # Encabezado visual
    st.markdown("""
    <h2 style='color:#FF4B4B;'>🔴 Tabla de Umbrales de Riesgo</h2>
    <table style='width:100%; border-collapse: collapse;'>
        <tr>
            <th style='background-color:#FFCCCC; color:black;'>🔴 Crítico</th>
            <th style='background-color:#FFE599; color:black;'>🟡 Moderado</th>
            <th style='background-color:#C9DAF8; color:black;'>🔵 Bajo</th>
        </tr>
        <tr>
            <td style='text-align:center;'>&ge; RD$6,000,000</td>
            <td style='text-align:center;'>&ge; RD$3,000,000 y < RD$6,000,000</td>
            <td style='text-align:center;'>&lt; RD$3,000,000</td>
        </tr>
    </table>
    """, unsafe_allow_html=True)

    # Filtro por grupo de riesgo
    st.markdown("""
    <h2 style='color:#2EB2FF;'>🔍 Análisis por Nivel de Riesgo</h2>
    """, unsafe_allow_html=True)

    grupos = sorted(tabla['Grupo de Riesgo'].unique())
    grupo_seleccionado = st.selectbox("Selecciona el grupo de riesgo", grupos)

    df_filtrado = tabla[tabla['Grupo de Riesgo'] == grupo_seleccionado]

    st.dataframe(df_filtrado, use_container_width=True)

    # Exportar archivo Excel con hoja de resumen
    from io import BytesIO
    import xlsxwriter

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_filtrado.to_excel(writer, index=False, sheet_name='Resumen por Categoría')

        workbook = writer.book
        worksheet = writer.sheets['Resumen por Categoría']

        # Encabezado institucional
        worksheet.write('A1', "Auditoría grupo Farmavalue", workbook.add_format({'bold': True, 'font_color': 'red', 'font_size': 28}))
        worksheet.write('A2', "Reporte de gastos del 01 de Enero al 20 de abril del 2025")
        worksheet.write('A3', "Auditor Asignado:")
        worksheet.write('A4', "Fecha de la Auditoría:")

        # Ajustar tabla desde fila 5
        for idx, col in enumerate(df_filtrado.columns):
            worksheet.write(5, idx, col)
        for row_idx, row in enumerate(df_filtrado.itertuples(index=False), start=6):
            for col_idx, value in enumerate(row):
                worksheet.write(row_idx, col_idx, value)

    st.download_button(
        label="🔗 Descargar Cédula de Trabajo de Auditoría",
        data=output.getvalue(),
        file_name="Cedula_Trabajo_Auditoria.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
