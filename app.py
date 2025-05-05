import pandas as pd
import streamlit as st
from io import BytesIO
import xlsxwriter

# Cargar archivo
archivo = st.file_uploader("Sube el archivo Excel", type="xlsx")
if archivo:
    df = pd.read_excel(archivo)
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df['Mes'] = df['Fecha'].dt.strftime('%B')

    # Calcular el total de gasto por sucursal y mes
    df['Monto del Gasto'] = df['Monto']
    totales_sucursal_mes = df.groupby(['Sucursales', 'Mes'])['Monto'].transform('sum')

    # Calcular el % de participación basado en sucursal y mes
    df['% Participación'] = (df['Monto'] / totales_sucursal_mes) * 100
    df['% Participación'] = df['% Participación'].round(2)

    # Preparar la hoja Cédula Auditor con columnas clave
    df['Verificado (☐)'] = ""
    df['No Verificado (☐)'] = ""
    df['Comentario del Auditor'] = ""

    cedula = df[[
        'Sucursales', 'Categoria', 'Descripcion', 'Fecha', 'Monto del Gasto', 'Mes',
        '% Participación', 'Verificado (☐)', 'No Verificado (☐)', 'Comentario del Auditor'
    ]].rename(columns={
        "Sucursales": "Sucursal",
        "Categoria": "Categoría",
        "Descripcion": "Descripción"
    })

    # Exportar Excel
    def generar_excel():
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            cedula.to_excel(writer, sheet_name="Cédula Auditor", index=False, startrow=5)
            ws = writer.sheets["Cédula Auditor"]
            wb = writer.book
            encabezado = wb.add_format({'bold': True, 'font_size': 28, 'font_color': 'red'})
            subtitulo = wb.add_format({'font_size': 12})
            ws.write("A1", "Auditoría grupo Farmavalue", encabezado)
            ws.write("A2", "Reporte de gastos del 01 de Enero al 20 de abril del 2025", subtitulo)
            ws.write("A3", "Auditor Asignado:", subtitulo)
            ws.write("A4", "Fecha de la Auditoría", subtitulo)
        output.seek(0)
        return output

    st.download_button(
        label="📄 Descargar Cédula Auditor",
        data=generar_excel(),
        file_name="Cedula_Auditor_Corregida.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.warning("Por favor, sube un archivo Excel para continuar.")
