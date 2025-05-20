import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import xlsxwriter

# --- BLOQUE DE SEGURIDAD ---
st.set_page_config(page_title="Acceso Seguro - FarmaValue", layout="wide")
st.markdown("<h2 style='text-align: center;'>🔐 Acceso a la Auditoría de Gastos</h2>", unsafe_allow_html=True)
password = st.text_input("Ingresa la contraseña para acceder a la aplicación:", type="password")
if password != "Herson2025":
    st.warning("🔒 Acceso restringido. Por favor, ingresa la contraseña correcta.")
    st.stop()

# --- ENCABEZADO ---
st.markdown("<h1 style='text-align: center; color: white;'>Auditoría a Gastos por País - Grupo FarmaValue_Herson Hernández</h1>", unsafe_allow_html=True)
archivo = st.file_uploader("📅 Sube tu archivo Excel", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df['Mes'] = df['Fecha'].dt.strftime('%B')
    meses_orden = ['January', 'February', 'March', 'April']
    df['Mes'] = pd.Categorical(df['Mes'], categories=meses_orden, ordered=True)

    df['Gasto Total Sucursal Mes'] = df.groupby(['Sucursales', 'Mes'])['Monto'].transform('sum')
    df['% Participación'] = (df['Monto'] / df['Gasto Total Sucursal Mes']) * 100
    df['% Participación'] = df['% Participación'].round(2)

    palabras_seguro = ['recuperación', 'seguro', 'diferencia', 'no cobrados', 'ajuste', 'reclasificación', 'ars', 'senasa', 'mapfre', 'afiliado', 'asegurado', 'cxc']
    sospechosas = df['Descripcion'].astype(str).str.lower().apply(lambda x: any(p in x for p in palabras_seguro))

    df['¿Revisar?'] = ((df['Monto'] >= 2000000) | (df['% Participación'] > 15) | sospechosas).map({True: 'Sí', False: 'No'})
    df['Descripcion'] = df.apply(lambda row: f"<span style='color:red'>{row['Descripcion']}</span>" if sospechosas[row.name] else row['Descripcion'], axis=1)

    # --- DESCARGA ---
    def generar_excel():
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            wb = writer.book
            header = wb.add_format({'bold': True, 'font_size': 28, 'font_color': 'red'})
            sub = wb.add_format({'font_size': 12})

            df_out = df.copy()
            df_out['Verificado (☑)'] = '☑'
            df_out['No Verificado (☑)'] = '☑'
            df_out['Comentario del Auditor'] = ''
            columnas = [
                'Sucursales', 'Grupo_Riesgo', 'Categoria', 'Descripcion', 'Fecha',
                'Monto', 'Gasto Total Sucursal Mes', '% Participación', '¿Revisar?',
                'Verificado (☑)', 'No Verificado (☑)', 'Comentario del Auditor'
            ]
            df_out = df_out[columnas]

            df_out.to_excel(writer, sheet_name="Cédula Auditor", startrow=5, index=False)
            ws = writer.sheets["Cédula Auditor"]
            ws.write("A1", "Auditoría grupo Farmavalue", header)
            ws.write("A2", "Reporte de gastos del 01 de Enero al 20 de abril del 2025", sub)
            ws.write("A3", "Auditor Asignado:", sub)
            ws.write("A4", "Fecha de la Auditoría", sub)

        output.seek(0)
        return output

    st.download_button(
        label="📄 Descargar Excel Cédula Auditor",
        data=generar_excel(),
        file_name="Cedula_Trabajo_3Hojas_OK.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
