
import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import xlsxwriter

# --- CONFIGURACIÓN GENERAL ---
st.set_page_config(page_title="Auditoría de Gastos - FarmaValue", layout="wide")

st.markdown("<h2 style='text-align: center;'>🔐 Acceso a la Auditoría de Gastos</h2>", unsafe_allow_html=True)
password = st.text_input("Ingresa la contraseña para acceder a la aplicación:", type="password")
if password != "Herson2025":
    st.warning("🔒 Acceso restringido. Por favor, ingresa la contraseña correcta.")
    st.stop()

st.markdown("<h1 style='text-align: center; color: white;'>Auditoría a Gastos por País - Grupo FarmaValue_Herson Hernández</h1>", unsafe_allow_html=True)
archivo = st.file_uploader("Selecciona tu archivo de gastos", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df['Mes'] = df['Fecha'].dt.strftime('%B').astype(str)
    df['Descripcion'] = df['Descripcion'].astype(str)
    meses_orden = ['January', 'February', 'March', 'April']
    df['Mes'] = pd.Categorical(df['Mes'], categories=meses_orden, ordered=True)

    # --- CÁLCULO DE PARTICIPACIÓN Y TOTAL POR SUCURSAL ---
    df['Gasto Total Sucursal Mes'] = df.groupby(['Sucursales', 'Mes'])['Monto'].transform('sum')
    df['% Participación'] = round((df['Monto'] / df['Gasto Total Sucursal Mes']) * 100, 2)

    # --- DETECCIÓN DE REPETIDOS ---
    df['Clave Mes Descripción'] = df['Mes'].astype(str) + "|" + df['Descripcion'].str.lower()
    repeticiones = df['Clave Mes Descripción'].value_counts()
    df['Repeticiones'] = df['Clave Mes Descripción'].map(repeticiones)

    # --- DETECCIÓN DE DESCRIPCIONES SOSPECHOSAS ---
    palabras_clave = ["recuperación", "seguro", "diferencia", "no cobrados", "ajuste",
                      "reclasificación", "ars", "senasa", "mapfre", "afiliado", "asegurado", "cxc"]
    df['Descripcion Sospechosa'] = df['Descripcion'].str.lower().apply(
        lambda x: any(pal in x for pal in palabras_clave)
    )

    # --- EVALUACIÓN FINAL: ¿REVISAR? ---
    df['¿Revisar?'] = np.where(
        (df['Monto'] >= 2_000_000) |
        (df['% Participación'] >= 15) |
        (df['Repeticiones'] >= 3) |
        (df['Descripcion Sospechosa']),
        'Sí', 'No'
    )

    # --- FORMATO FINAL PARA EXPORTACIÓN ---
    df['Monto del Gasto'] = df['Monto'].round(0)
    df['Gasto Total de la Sucursal'] = df['Gasto Total Sucursal Mes'].round(0)
    df['Fecha'] = df['Fecha'].dt.strftime('%d/%m/%Y')
    df['Verificado (☐)'] = '☐'
    df['No Verificado (☐)'] = '☐'
    df['Comentario del Auditor'] = ''

    columnas_finales = [
        'Sucursales', 'Categoria', 'Descripcion', 'Fecha',
        'Monto del Gasto', 'Gasto Total de la Sucursal', '% Participación',
        '¿Revisar?', 'Verificado (☐)', 'No Verificado (☐)', 'Comentario del Auditor'
    ]

    df_final = df[columnas_finales].rename(columns={
        'Sucursales': 'Sucursal',
        'Categoria': 'Categoría',
        'Descripcion': 'Descripción'
    })

    # --- DESCARGA DEL ARCHIVO EXCEL ---
    def generar_excel(df_final):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_final.to_excel(writer, sheet_name="Cédula Auditor", startrow=5, index=False)
            workbook = writer.book
            ws = writer.sheets["Cédula Auditor"]

            header = workbook.add_format({'bold': True, 'font_size': 28, 'font_color': 'red'})
            sub = workbook.add_format({'font_size': 12})
            rojo = workbook.add_format({'font_color': 'red'})
            miles = workbook.add_format({'num_format': '#,##0', 'align': 'center'})
            center = workbook.add_format({'align': 'center'})

            ws.write("A1", "Auditoría grupo Farmavalue", header)
            ws.write("A2", "Reporte de gastos del 01 de Enero al 20 de abril del 2025", sub)
            ws.write("A3", "Auditor Asignado:", sub)
            ws.write("A4", "Fecha de la Auditoría", sub)

            for col in range(4, 11):
                ws.set_column(col, col, 20, center)
            for col in [5, 6]:
                ws.set_column(col, col, 20, miles)

            for row_num, value in enumerate(df_final['Descripción'], start=5):
                if any(p in str(value).lower() for p in palabras_clave):
                    ws.write(row_num, 2, value, rojo)

        output.seek(0)
        return output

    st.download_button(
        label="📥 Descargar Excel Cédula Auditor",
        data=generar_excel(df_final),
        file_name="Cedula_Trabajo_3Hojas_OK.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
