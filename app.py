
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

# --- CONFIGURACIÓN DE LA APP ---
st.markdown("<h1 style='text-align: center; color: white;'>Auditoría a Gastos por País - Grupo FarmaValue_Herson Hernández</h1>", unsafe_allow_html=True)
st.markdown("### 📥 Sube tu archivo Excel")
archivo = st.file_uploader("Selecciona tu archivo de gastos", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    df.columns = ['Sucursal', 'Grupo_Riesgo', 'Categoría', 'Descripción', 'Fecha', 'Monto del Gasto',
                  'Gasto Total de la Sucursal', '% Participación', '¿Revisar?', 'Verificado (☐)', 'No Verificado (☐)', 'Comentario del Auditor']

    df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True).dt.strftime('%d/%m/%Y')
    df['% Participación'] = df['% Participación'].round(2)
    df['Monto del Gasto'] = df['Monto del Gasto'].apply(lambda x: f"{x:,.0f}")
    df['Gasto Total de la Sucursal'] = df['Gasto Total de la Sucursal'].apply(lambda x: f"{x:,.0f}")

    df = df.sort_values(by=['% Participación', '¿Revisar?'], ascending=[False, True]).reset_index(drop=True)

    st.dataframe(df)

    def exportar_excel(dataframe):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            wb = writer.book
            formato_encabezado = wb.add_format({'bold': True, 'font_size': 28, 'font_color': 'red'})
            formato_sub = wb.add_format({'font_size': 12})
            formato_fecha = wb.add_format({'num_format': 'dd/mm/yyyy', 'align': 'center'})
            formato_miles = wb.add_format({'num_format': '#,##0', 'align': 'center'})
            formato_centrado = wb.add_format({'align': 'center'})

            dataframe.to_excel(writer, sheet_name="Cédula Auditor", startrow=5, index=False)
            ws = writer.sheets["Cédula Auditor"]

            ws.write("A1", "Auditoría grupo Farmavalue", formato_encabezado)
            ws.write("A2", "Reporte de gastos del 01 de Enero al 20 de abril del 2025", formato_sub)
            ws.write("A3", "Auditor Asignado:", formato_sub)
            ws.write("A4", "Fecha de la Auditoría", formato_sub)

            for col_num, value in enumerate(dataframe.columns.values):
                col_letter = chr(65 + col_num)
                if value == 'Fecha':
                    ws.set_column(f'{col_letter}:{col_letter}', 12, formato_fecha)
                elif value in ['Monto del Gasto', 'Gasto Total de la Sucursal']:
                    ws.set_column(f'{col_letter}:{col_letter}', 18, formato_miles)
                else:
                    ws.set_column(f'{col_letter}:{col_letter}', 18, formato_centrado)

        output.seek(0)
        return output

    st.download_button(
        label="📄 Descargar Cedula Auditoría",
        data=exportar_excel(df),
        file_name="Cedula_Auditoria_Validada_OK.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("📥 Por favor, sube un archivo Excel para comenzar.")
