
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import xlsxwriter

# Configuración de la app
st.set_page_config(page_title="Auditoría de Gastos", layout="wide")
st.markdown("<h1 style='text-align: center;'>Auditoría a Gastos por País - Grupo FarmaValue_Herson Hernández</h1>", unsafe_allow_html=True)

# Carga del archivo
archivo = st.file_uploader("Selecciona tu archivo de gastos", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
    df['Mes'] = df['Fecha'].dt.strftime('%B')
    meses_orden = ['January', 'February', 'March', 'April']
    df['Mes'] = pd.Categorical(df['Mes'], categories=meses_orden, ordered=True)

    # Gráfico de gasto mensual
    resumen_mes = df.groupby('Mes')['Monto'].sum().reindex(meses_orden)
    st.bar_chart(resumen_mes)

    # Evaluación de revisión
    df['Gasto Total Sucursal Mes'] = df.groupby(['Sucursales', 'Mes'])['Monto'].transform('sum')
    df['% Participación'] = (df['Monto'] / df['Gasto Total Sucursal Mes']) * 100

    # Condiciones del algoritmo de revisión
    sospechosas = ["comida", "snack", "sin comprobante", "misc", "varios"]
    seguros = ["recuperación", "seguro", "diferencia", "no cobrados", "ajuste", "reclasificación",
               "ARS", "SENASA", "MAPFRE", "AFILIADO", "ASEGURADO", "CxC"]

    df['Repetido'] = df.groupby(['Descripcion', 'Mes'])['Descripcion'].transform('count')
    df['¿Revisar?'] = df.apply(lambda row: (
        row['Monto'] >= 2000000 or
        row['% Participación'] >= 12 or
        any(palabra.lower() in str(row['Descripcion']).lower() for palabra in sospechosas) or
        row['Repetido'] >= 3 or
        any(palabra.lower() in str(row['Descripcion']).lower() for palabra in seguros)
    ), axis=1).map({True: "Sí", False: "No"})

    # Coloreado de texto sospechoso
    def pintar_desc(desc):
        if any(pal.lower() in str(desc).lower() for pal in seguros):
            return f'=HYPERLINK("","{desc}")'
        return desc

    df['Descripcion'] = df['Descripcion'].apply(pintar_desc)
    df['Monto del Gasto'] = df['Monto'].round(2)
    df['Gasto Total de la Sucursal'] = df['Gasto Total Sucursal Mes'].round(2)
    df['% Participación'] = df['% Participación'].round(2)
    df['Verificado (☐)'] = ""
    df['No Verificado (☐)'] = ""
    df['Comentario del Auditor'] = ""

    columnas = [
        'Sucursales', 'Grupo_Riesgo', 'Categoria', 'Descripcion', 'Fecha',
        'Monto del Gasto', 'Gasto Total de la Sucursal', '% Participación',
        '¿Revisar?', 'Verificado (☐)', 'No Verificado (☐)', 'Comentario del Auditor'
    ]
    columnas_existentes = [col for col in columnas if col in df.columns]
    cedula = df[columnas_existentes].rename(columns={
        "Sucursales": "Sucursal",
        "Categoria": "Categoría",
        "Descripcion": "Descripción"
    }).sort_values(by=['% Participación'], ascending=False)

    # Descargar Excel
    def generar_excel():
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            wb = writer.book
            ws_name = "Cédula Auditoría"
            cedula.to_excel(writer, sheet_name=ws_name, startrow=5, index=False)
            ws = writer.sheets[ws_name]
            encabezado = wb.add_format({'bold': True, 'font_size': 28, 'font_color': 'red'})
            sub = wb.add_format({'font_size': 12})
            centrar = wb.add_format({'align': 'center'})
            miles = wb.add_format({'num_format': '#,##0', 'align': 'center'})

            ws.write("A1", "Auditoría grupo Farmavalue", encabezado)
            ws.write("A2", "Reporte de gastos del 01 de Enero al 20 de abril del 2025", sub)
            ws.write("A3", "Auditor Asignado:", sub)
            ws.write("A4", "Fecha de la Auditoría", sub)

            for col in range(4, 11):
                ws.set_column(col, col, None, centrar)
            for col in [5, 6]:
                ws.set_column(col, col, None, miles)

        output.seek(0)
        return output

    st.download_button(
        label="📄 Descargar Excel Cédula Auditor",
        data=generar_excel(),
        file_name="Cedula_Trabajo_3Hojas_OK.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
