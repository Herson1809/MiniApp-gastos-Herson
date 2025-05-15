
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import xlsxwriter

# --- BLOQUE DE SEGURIDAD ---
st.set_page_config(page_title="Acceso Seguro - FarmaValue", layout="wide")
st.markdown("<h2 style='text-align: center;'>🔐 Acceso a la Auditoría de Gastos</h2>", unsafe_allow_html=True)
password = st.text_input("Ingresa la contraseña para acceder a la aplicación:", type="password")

if password != "Herson2025":
    st.warning("🔒 Acceso restringido. Por favor, ingresa la contraseña correcta.")
    st.stop()

# --- CONFIGURACIÓN DE LA APP ---
st.markdown("<h1 style='text-align: center; color: white;'>Auditoría a Gastos por País - Grupo FarmaValue_Herson Hernández</h1>", unsafe_allow_html=True)
archivo = st.file_uploader("Selecciona tu archivo de gastos", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df['Mes'] = df['Fecha'].dt.strftime('%B').astype(str)
    meses_orden = ['January', 'February', 'March', 'April']
    df['Mes'] = pd.Categorical(df['Mes'], categories=meses_orden, ordered=True)

    resumen_mes = df.groupby('Mes')['Monto'].sum().reindex(meses_orden)
    st.bar_chart(resumen_mes)

    def clasificar_riesgo(monto):
        if monto >= 6000000:
            return "🔴 Crítico"
        elif monto >= 3000000:
            return "🟡 Moderado"
        else:
            return "🟢 Bajo"

    df['Grupo_Riesgo'] = df.groupby('Categoria')['Monto'].transform('sum').apply(clasificar_riesgo)
    df['Gasto Total Sucursal Mes'] = df.groupby(['Sucursales', 'Mes'])['Monto'].transform('sum')
    df['% Participación'] = (df['Monto'] / df['Gasto Total Sucursal Mes']) * 100
    df['¿Revisar?'] = (
        (df['Monto'] >= 6000000) |
        (df['% Participación'] > 25) |
        df['Descripcion'].str.contains("comida|snack|sin comprobante|misc|varios", case=False, na=False)
    ).map({True: "Sí", False: "No"})

    df['Monto del Gasto'] = df['Monto'].round(2)
    df['Gasto Total de la Sucursal'] = df['Gasto Total Sucursal Mes'].round(2)
    df['% Participación'] = df['% Participación'].round(2)
    df['Verificado (☐)'] = "☐"
    df['No Verificado (☐)'] = "☐"
    df['Comentario del Auditor'] = ""
    df['Fecha'] = df['Fecha'].dt.strftime('%d/%m/%Y')

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
    }).sort_values(by=['% Participación', '¿Revisar?'], ascending=[False, True])

    def generar_excel():
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            wb = writer.book
            formato_encabezado = wb.add_format({'bold': True, 'font_size': 28, 'font_color': 'red'})
            formato_sub = wb.add_format({'font_size': 12})
            formato_centrado = wb.add_format({'align': 'center'})
            formato_miles = wb.add_format({'num_format': '#,##0', 'align': 'center'})

            cedula.to_excel(writer, sheet_name="Cédula Auditor", startrow=5, index=False)
            ws = writer.sheets["Cédula Auditor"]
            ws.write("A1", "Auditoría grupo Farmavalue", formato_encabezado)
            ws.write("A2", "Reporte de gastos del 01 de Enero al 20 de abril del 2025", formato_sub)
            ws.write("A3", "Auditor Asignado:", formato_sub)
            ws.write("A4", "Fecha de la Auditoría", formato_sub)

            ws.set_column("E:E", 15, formato_centrado)
            ws.set_column("F:G", 18, formato_miles)
            ws.set_column("H:K", 16, formato_centrado)

        output.seek(0)
        return output

    st.download_button(
        label="📄 Descargar Excel Cédula Auditor",
        data=generar_excel(),
        file_name="Cedula_Auditor_Validado_OK.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
