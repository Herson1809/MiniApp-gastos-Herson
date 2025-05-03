import streamlit as st
import pandas as pd
import base64
from io import BytesIO

# Título
st.markdown("<h1 style='text-align: center; color: white;'>Auditoría a Gastos por País - Grupo FarmaValue_Herson Hernández</h1>", unsafe_allow_html=True)

# Carga de archivo
st.markdown("### 📂 Sube el archivo base de gastos")
archivo = st.file_uploader("Selecciona tu archivo .xlsx", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)

    # Procesamiento base
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df['Mes'] = df['Fecha'].dt.strftime('%B')

    # Agrupación por categoría
    resumen = df.groupby('Categoria').agg({
        'Monto': 'sum',
        'Fecha': 'count'
    }).rename(columns={'Monto': 'Total general', 'Fecha': 'Cantidad Registros'}).reset_index()

    # Clasificación de riesgo
    def clasificar_riesgo(valor):
        if valor >= 60000:
            return '🔴 Crítico'
        elif valor >= 30000:
            return '🟡 Moderado'
        else:
            return '🟢 Bajo'

    resumen['Grupo de Riesgo'] = resumen['Total general'].apply(lambda x: clasificar_riesgo(x))
    resumen = resumen[['Categoria', 'Grupo de Riesgo', 'Cantidad Registros', 'Total general']]

    # Conversión a miles, sin decimales y separación por comas
    resumen['Total general'] = resumen['Total general'].apply(lambda x: round(x / 1000))
    resumen['Total general'] = resumen['Total general'].map('{:,.0f}'.format)

    # Ordenar de mayor a menor
    resumen = resumen.sort_values(by='Total general', ascending=False).reset_index(drop=True)
    resumen.index += 1
    resumen.insert(0, 'No', resumen.index)

    # Agregar línea de total
    total_row = {
        'No': '',
        'Categoria': 'TOTAL GENERAL',
        'Grupo de Riesgo': '',
        'Cantidad Registros': resumen['Cantidad Registros'].sum(),
        'Total general': resumen['Total general'].replace(',', '', regex=True).astype(int).sum()
    }
    total_row['Total general'] = '{:,.0f}'.format(round(total_row['Total general']))
    resumen = pd.concat([resumen, pd.DataFrame([total_row])], ignore_index=True)

    # Generación del Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        resumen.to_excel(writer, sheet_name='Resumen por Categoría', index=False, startrow=5)

        workbook = writer.book
        worksheet = writer.sheets['Resumen por Categoría']

        # Encabezado
        formato_titulo = workbook.add_format({'bold': True, 'font_size': 28, 'font_color': 'red'})
        formato_subtitulo = workbook.add_format({'font_size': 12, 'bold': False})
        worksheet.write('A1', 'Auditoría grupo Farmavalue', formato_titulo)
        worksheet.write('A2', 'Reporte de gastos del 01 de Enero al 20 de abril del 2025', formato_subtitulo)
        worksheet.write('A3', 'Auditor Asignado:', formato_subtitulo)
        worksheet.write('A4', 'Fecha de la Auditoría', formato_subtitulo)

    output.seek(0)
    b64 = base64.b64encode(output.read()).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="Resumen_por_Categoria.xlsx">📄 Descargar Resumen por Categoría</a>'
    st.markdown("### 📥 Descarga del Reporte")
    st.markdown(href, unsafe_allow_html=True)

else:
    st.info("📌 Esperando que subas el archivo base para generar el resumen.")
