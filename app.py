
import streamlit as st
import pandas as pd
from io import BytesIO
import xlsxwriter

# --- BLOQUE DE SEGURIDAD ---
st.set_page_config(page_title="Acceso Seguro - FarmaValue", layout="wide")
st.markdown("<h2 style='text-align: center;'>🔐 Acceso a la Auditoría de Gastos</h2>", unsafe_allow_html=True)
password = st.text_input("Ingresa la contraseña para acceder a la aplicación:", type="password")
if password != "Herson2025":
    st.warning("🔒 Acceso restringido. Por favor, ingresa la contraseña correcta.")
    st.stop()

# --- CONFIGURACIÓN ---
st.markdown("<h1 style='text-align: center; color: white;'>Auditoría a Gastos por País - Grupo FarmaValue_Herson Hernández</h1>", unsafe_allow_html=True)
archivo = st.file_uploader("📥 Sube tu archivo Excel", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    df['Fecha'] = pd.to_datetime(df['Fecha'])

    df['% Participación'] = (df['Monto'] / df.groupby(['Sucursales', 'Mes'])['Monto'].transform('sum')) * 100
    criterios_snack = df['Descripcion'].str.contains("comida|snack|sin comprobante|misc|varios", case=False, na=False)
    criterio_revisar = (
        (df['Monto'] >= 6000000) |
        (df['% Participación'] > 25) |
        criterios_snack
    )
    df['¿Revisar?'] = criterio_revisar.map({True: "Sí", False: "No"})
    df['Monto del Gasto'] = df['Monto'].round(2)
    df['Gasto Total de la Sucursal'] = df.groupby(['Sucursales', 'Mes'])['Monto'].transform('sum').round(2)
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
    cedula = df[columnas_existentes]
    cedula = cedula.sort_values(by=['% Participación', '¿Revisar?'], ascending=[False, True])

    def generar_excel():
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter', datetime_format='dd/mm/yyyy') as writer:
            wb = writer.book
            formato_encabezado = wb.add_format({'bold': True, 'font_size': 28, 'font_color': 'red'})
            formato_sub = wb.add_format({'font_size': 12})
            formato_fecha = wb.add_format({'num_format': 'dd/mm/yyyy', 'align': 'center'})
            formato_miles = wb.add_format({'num_format': '#,##0', 'align': 'center'})
            formato_center = wb.add_format({'align': 'center', 'valign': 'vcenter'})

            cedula.to_excel(writer, sheet_name="Cédula Auditor", startrow=5, index=False)
            ws = writer.sheets["Cédula Auditor"]
            ws.write("A1", "Auditoría grupo Farmavalue", formato_encabezado)
            ws.write("A2", "Reporte de gastos del 01 de Enero al 20 de abril del 2025", formato_sub)
            ws.write("A3", "Auditor Asignado:", formato_sub)
            ws.write("A4", "Fecha de la Auditoría", formato_sub)

            for idx, col in enumerate(cedula.columns):
                col_letter = chr(65 + idx)
                if col == 'Fecha':
                    ws.set_column(f"{col_letter}:{col_letter}", 15, formato_fecha)
                elif col in ['Monto del Gasto', 'Gasto Total de la Sucursal']:
                    ws.set_column(f"{col_letter}:{col_letter}", 18, formato_miles)
                elif col in ['% Participación', '¿Revisar?', 'Verificado (☐)', 'No Verificado (☐)', 'Comentario del Auditor']:
                    ws.set_column(f"{col_letter}:{col_letter}", 20, formato_center)
                else:
                    ws.set_column(f"{col_letter}:{col_letter}", 18)

        output.seek(0)
        return output

    st.download_button(
        label="📄 Descargar Excel Cédula Auditor",
        data=generar_excel(),
        file_name="Cedula_Auditor_OK.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
