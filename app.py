
import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import xlsxwriter

# Configuración de página
st.set_page_config(layout="wide", page_title="Auditoría a Gastos por País - Grupo FarmaValue_Herson Hernández")

# Estilos
st.markdown("""<style>
    .main {background-color: #111111;}
    h1, h2, h3, h4, h5, h6, .stTextInput, .stSelectbox, .stSlider {
        color: white;
    }
    .stButton>button {
        color: white;
        background-color: #4CAF50;
    }
</style>""", unsafe_allow_html=True)

# Encabezado
st.title("🔐 Acceso a la Auditoría de Gastos")
password = st.text_input("Ingresa la contraseña para acceder a la aplicación:", type="password")
if password != "admin":
    st.stop()

st.markdown("## Auditoría a Gastos por País - Grupo FarmaValue_Herson Hernández")
uploaded_file = st.file_uploader("Selecciona tu archivo de gastos", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name=0)

    # Normalización de columnas esperadas
    df.columns = [str(col).strip() for col in df.columns]
    df.columns = df.columns.str.replace("Monto", "Monto", regex=False)

    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
    df['Mes'] = df['Fecha'].dt.strftime('%B')
    df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce')

    # Total por mes
    resumen = df.groupby('Mes')['Monto'].sum().reindex(['January', 'February', 'March', 'April'])

    st.bar_chart(resumen)

    # --- ALGORITMO DE EVALUACIÓN ---

    base = df.copy()
    base['Total x Sucursal'] = base.groupby('Sucursal')['Monto'].transform('sum')
    base['% Participación'] = (base['Monto'] / base['Total x Sucursal'] * 100).round(2)

    # Reglas
    base['¿Revisar?'] = "No"

    base.loc[base['Monto'] >= 2_000_000, '¿Revisar?'] = "Sí"
    base.loc[base['% Participación'] >= 15, '¿Revisar?'] = "Sí"

    # Gasto hormiga (3 o más repeticiones de descripción en el mismo mes)
    repetidos = base.groupby(['Mes', 'Descripción']).transform('count')
    base.loc[repetidos['Monto'] >= 3, '¿Revisar?'] = "Sí"

    # Descripciones sospechosas
    palabras_clave = ['recuperación', 'seguro', 'diferencia', 'no cobrados', 'ajuste', 'reclasificación', 'ARS', 'SENASA', 'MAPFRE', 'AFILIADO', 'ASEGURADO', 'CxC']
    def es_sospechoso(texto):
        texto = str(texto).lower()
        return any(palabra.lower() in texto for palabra in palabras_clave)

    base['Descripción_sospechosa'] = base['Descripción'].apply(es_sospechoso)
    base.loc[base['Descripción_sospechosa'], '¿Revisar?'] = "Sí"

    # Formato miles
    base['Monto del Gasto'] = base['Monto'].round(0).map('{:,.0f}'.format)
    base['Gasto Total de la Sucursal'] = base['Total x Sucursal'].round(0).map('{:,.0f}'.format)

    # Formato de fecha
    base['Fecha'] = pd.to_datetime(base['Fecha'], errors='coerce').dt.strftime('%d/%m/%Y')

    # Columnas finales
    columnas_finales = ['Sucursal', 'Categoría', 'Descripción', 'Fecha', 'Monto del Gasto', 'Gasto Total de la Sucursal',
                        '% Participación', '¿Revisar?']
    cedula = base[columnas_finales].copy()
    cedula['Verificado (☐)'] = ''
    cedula['No Verificado (☐)'] = ''
    cedula['Comentario del Auditor'] = ''

    # Descargar Excel
    def generar_excel(df_cedula):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_cedula.to_excel(writer, index=False, sheet_name='Cédula Auditoría')
            workbook = writer.book
            worksheet = writer.sheets['Cédula Auditoría']

            title_format = workbook.add_format({'bold': True, 'font_color': 'red', 'font_size': 28})
            subtitle_format = workbook.add_format({'bold': False, 'font_color': 'black', 'font_size': 12})
            header_format = workbook.add_format({'bold': True, 'bg_color': '#C5D9F1', 'border': 1})

            # Insertar encabezado
            worksheet.merge_range('A1:L1', 'Auditoría grupo Farmavalue', title_format)
            worksheet.merge_range('A2:L2', 'Reporte de gastos del 01 de Enero al 20 de abril del 2025', subtitle_format)
            worksheet.merge_range('A3:L3', 'Auditor Asignado:', subtitle_format)
            worksheet.merge_range('A4:L4', 'Fecha de la Auditoría', subtitle_format)

            for col_num, value in enumerate(df_cedula.columns.values):
                worksheet.write(4, col_num, value, header_format)

            worksheet.set_column('A:L', 22)
        output.seek(0)
        return output

    excel_bytes = generar_excel(cedula)

    st.download_button(
        label="📄 Descargar Excel Cédula Auditor",
        data=excel_bytes,
        file_name="Cedula_Trabajo_3Hojas_OK.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
