
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import xlsxwriter

# --- BLOQUE DE SEGURIDAD ---
st.set_page_config(page_title="Auditoría de Gastos - FarmaValue", layout="wide")
password = st.text_input("Ingresa la contraseña para acceder a la aplicación:", type="password")
if password != "Herson2025":
    st.warning("🔒 Acceso restringido. Contraseña incorrecta.")
    st.stop()

# --- INTERFAZ INICIAL ---
st.title("Auditoría a Gastos por País - Grupo FarmaValue_Herson Hernández")
archivo = st.file_uploader("Selecciona tu archivo de gastos", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df['Mes'] = df['Fecha'].dt.strftime('%B')
    meses_orden = ['January', 'February', 'March', 'April']
    df['Mes'] = pd.Categorical(df['Mes'], categories=meses_orden, ordered=True)

    resumen_mes = df.groupby('Mes')['Monto'].sum().reindex(meses_orden)
    st.bar_chart(resumen_mes)

    # --- LÓGICA DE REVISIÓN INTELIGENTE ---
    df['Gasto Total Sucursal Mes'] = df.groupby(['Sucursales', 'Mes'])['Monto'].transform('sum')
    df['% Participación'] = (df['Monto'] / df['Gasto Total Sucursal Mes']) * 100

    def clasificar_riesgo(row):
        if row['Monto'] >= 2000000 or row['% Participación'] >= 12:
            return "🔴 Crítico"
        elif row['Monto'] >= 1000000:
            return "🟡 Moderado"
        else:
            return "🟢 Bajo"

    df['Grupo_Riesgo'] = df.apply(clasificar_riesgo, axis=1)

    criterios_snack = df['Descripcion'].str.contains("comida|snack|sin comprobante|misc|varios", case=False, na=False)
    criterios_seguro = df['Descripcion'].str.contains("recuperación|seguro|diferencia|no cobrados|ajuste|reclasificación|cxc", case=False, na=False)

    frecuencia = df.groupby(['Sucursales', 'Descripcion'])['Monto'].transform('count')
    criterios_repetidos = frecuencia >= 3

    df['¿Revisar?'] = (
        (df['Monto'] >= 2000000) |
        (df['% Participación'] >= 12) |
        criterios_snack |
        criterios_seguro |
        criterios_repetidos
    ).map({True: "Sí", False: "No"})

    df['Monto del Gasto'] = df['Monto'].round(2)
    df['Gasto Total de la Sucursal'] = df['Gasto Total Sucursal Mes'].round(2)
    df['% Participación'] = df['% Participación'].round(2)
    df['Verificado (☐)'] = ""
    df['No Verificado (☐)'] = ""
    df['Comentario del Auditor'] = ""

    # Colorear seguros en rojo (solo visual en Excel)
    def formato_descripcion(val):
        if isinstance(val, str) and any(x in val.lower() for x in ["seguro", "cxc", "ars", "aseguradora", "reembolso"]):
            return 'color: red'
        return ''

    columnas = [
        'Sucursales', 'Grupo_Riesgo', 'Categoria', 'Descripcion', 'Fecha',
        'Monto del Gasto', 'Gasto Total de la Sucursal', '% Participación',
        '¿Revisar?', 'Verificado (☐)', 'No Verificado (☐)', 'Comentario del Auditor'
    ]
    columnas_existentes = [col for col in columnas if col in df.columns]

    if len(columnas_existentes) < len(columnas):
        st.error("❌ Algunas columnas necesarias no existen en el archivo.")
    else:
        cedula = df[columnas_existentes].sort_values(by='% Participación', ascending=False)

        # --- DESCARGA DEL ARCHIVO ---
        def generar_excel():
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                wb = writer.book
                format_title = wb.add_format({'bold': True, 'font_size': 28, 'font_color': 'red'})
                format_sub = wb.add_format({'font_size': 12})

                cedula.to_excel(writer, sheet_name="Cédula Auditor", startrow=5, index=False)
                ws = writer.sheets["Cédula Auditor"]
                ws.write("A1", "Auditoría grupo Farmavalue", format_title)
                ws.write("A2", "Reporte de gastos del 01 de Enero al 20 de abril del 2025", format_sub)
                ws.write("A3", "Auditor Asignado:", format_sub)
                ws.write("A4", "Fecha de la Auditoría", format_sub)

                # Colorear descripciones sospechosas
                format_red = wb.add_format({'font_color': 'red'})
                desc_idx = columnas_existentes.index('Descripcion')
                for row_idx, val in enumerate(cedula['Descripcion'], start=5):
                    if any(x in str(val).lower() for x in ["seguro", "cxc", "ars", "aseguradora", "reembolso"]):
                        ws.write(row_idx, desc_idx, val, format_red)

            output.seek(0)
            return output

        st.download_button(
            label="📥 Descargar Excel Cédula Auditor",
            data=generar_excel(),
            file_name="Cedula_Auditor_FINAL_OK.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
