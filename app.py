import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import xlsxwriter

# --- CONFIGURACION DE LA APP ---
st.set_page_config(page_title="Auditoría de Gastos - FarmaValue", layout="wide")
st.title("Auditoría a Gastos por País - Grupo FarmaValue_Herson Hernández")

# --- CARGA DEL ARCHIVO ---
archivo = st.file_uploader("Selecciona tu archivo de gastos", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
    df['Mes'] = df['Fecha'].dt.strftime('%B')
    
    meses_orden = ['January', 'February', 'March', 'April']
    df['Mes'] = pd.Categorical(df['Mes'], categories=meses_orden, ordered=True)

    # --- GRAFICO DE GASTOS POR MES ---
    resumen_mes = df.groupby('Mes')['Monto'].sum().reindex(meses_orden)
    st.bar_chart(resumen_mes)

    # --- CRITERIOS DE REVISION ---
    df['Gasto Total Sucursal Mes'] = df.groupby(['Sucursales', 'Mes'])['Monto'].transform('sum')
    df['% Participacion'] = (df['Monto'] / df['Gasto Total Sucursal Mes']) * 100
    df['Conteo'] = df.groupby(['Descripcion', 'Mes'])['Descripcion'].transform('count')

    palabras_sospechosas = ["recuperacion", "seguro", "diferencia", "no cobrados", "ajuste", "reclasificacion", "ars", "senasa", "mapfre", "afiliado", "asegurado", "cxc"]

    df['Descripcion_lower'] = df['Descripcion'].astype(str).str.lower()

    df['Sospechoso'] = df['Descripcion_lower'].apply(lambda x: any(p in x for p in palabras_sospechosas))

    df['¿Revisar?'] = ((df['Monto'] >= 2000000) |
                       (df['% Participacion'] >= 12) |
                       (df['Conteo'] >= 3) |
                       (df['Sospechoso'])).map({True: 'Sí', False: 'No'})

    df['Grupo_Riesgo'] = df.apply(lambda row: '🔴 Crítico' if row['Monto'] >= 2000000 or row['% Participacion'] >= 12 
                                    else '🟡 Moderado' if row['Monto'] >= 1000000
                                    else '🟢 Bajo', axis=1)

    df['Verificado (☐)'] = ''
    df['No Verificado (☐)'] = ''
    df['Comentario del Auditor'] = ''

    columnas_exportar = ['Sucursales', 'Grupo_Riesgo', 'Categoria', 'Descripcion', 'Fecha',
                         'Monto', 'Gasto Total Sucursal Mes', '% Participacion', '¿Revisar?',
                         'Verificado (☐)', 'No Verificado (☐)', 'Comentario del Auditor']

    cedula = df[columnas_exportar].sort_values(by=['% Participacion'], ascending=False).copy()
    cedula['Fecha'] = cedula['Fecha'].dt.strftime('%d/%m/%Y')

    # --- DESCARGA DEL ARCHIVO ---
    def generar_excel():
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            cedula.to_excel(writer, sheet_name="Cédula Auditor", index=False, startrow=5)
            workbook  = writer.book
            worksheet = writer.sheets["Cédula Auditor"]

            header_format = workbook.add_format({'bold': True, 'font_size': 28, 'font_color': 'red'})
            sub_format = workbook.add_format({'font_size': 12})
            worksheet.write("A1", "Auditoría grupo Farmavalue", header_format)
            worksheet.write("A2", "Reporte de gastos del 01 de Enero al 20 de abril del 2025", sub_format)
            worksheet.write("A3", "Auditor Asignado:", sub_format)
            worksheet.write("A4", "Fecha de la Auditoría", sub_format)

            red_text = workbook.add_format({'font_color': 'red'})
            desc_col = cedula.columns.get_loc("Descripcion")
            for row_num, value in enumerate(cedula['Descripcion'], start=5):
                if any(p in str(value).lower() for p in palabras_sospechosas):
                    worksheet.write(row_num, desc_col, value, red_text)

            for col in range(len(cedula.columns)):
                worksheet.set_column(col, col, 20)

        output.seek(0)
        return output

    st.download_button(
        label="📄 Descargar Excel Cédula Auditor",
        data=generar_excel(),
        file_name="Cedula_Auditor_OK.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

