
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

# --- ENCABEZADO Y CARGA ---
st.markdown("<h1 style='text-align: center; color: white;'>Auditoría a Gastos por País - Grupo FarmaValue_Herson Hernández</h1>", unsafe_allow_html=True)
archivo = st.file_uploader("Selecciona tu archivo de gastos", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df['Mes'] = df['Fecha'].dt.strftime('%B')
    meses_orden = ['January', 'February', 'March', 'April']
    df['Mes'] = pd.Categorical(df['Mes'], categories=meses_orden, ordered=True)

    df['Grupo_Riesgo'] = df.groupby('Categoria')['Monto'].transform('sum').apply(
        lambda x: '🔴 Crítico' if x >= 6000000 else '🟡 Moderado' if x >= 3000000 else '🟢 Bajo'
    )

    df['Gasto Total Sucursal Mes'] = df.groupby(['Sucursales', 'Mes'])['Monto'].transform('sum')
    df['% Participación'] = (df['Monto'] / df['Gasto Total Sucursal Mes']) * 100

    criterios_snack = df['Descripcion'].str.contains("comida|snack|sin comprobante|misc|varios", case=False, na=False)
    criterio_revisar = (
        (df['Monto'] >= 6000000) |
        (df['% Participación'] > 15) |
        criterios_snack
    )
    df['¿Revisar?'] = criterio_revisar.map({True: "Sí", False: "No"})

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
        "Sucursales": "Sucursal", "Categoria": "Categoría", "Descripcion": "Descripción"
    }).sort_values(by=['% Participación', '¿Revisar?'], ascending=[False, True])

    def exportar_excel():
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            wb = writer.book
            formato_encabezado = wb.add_format({'bold': True, 'font_size': 28, 'font_color': 'red'})
            formato_sub = wb.add_format({'font_size': 12})
            formato_fecha = wb.add_format({'num_format': 'dd/mm/yyyy', 'align': 'center'})
            formato_miles = wb.add_format({'num_format': '#,##0', 'align': 'center'})
            formato_centrado = wb.add_format({'align': 'center'})

            cedula.to_excel(writer, sheet_name="Cédula Auditor", startrow=5, index=False)
            ws = writer.sheets["Cédula Auditor"]
            ws.write("A1", "Auditoría grupo Farmavalue", formato_encabezado)
            ws.write("A2", "Reporte de gastos del 01 de Enero al 20 de abril del 2025", formato_sub)
            ws.write("A3", "Auditor Asignado:", formato_sub)
            ws.write("A4", "Fecha de la Auditoría", formato_sub)

            for col_idx, col in enumerate(cedula.columns):
                col_letter = chr(65 + col_idx)
                if col == "Fecha":
                    ws.set_column(f"{col_letter}:{col_letter}", 14, formato_fecha)
                elif col in ["Monto del Gasto", "Gasto Total de la Sucursal"]:
                    ws.set_column(f"{col_letter}:{col_letter}", 18, formato_miles)
                elif col in ["% Participación", "¿Revisar?", "Verificado (☐)", "No Verificado (☐)", "Comentario del Auditor"]:
                    ws.set_column(f"{col_letter}:{col_letter}", 18, formato_centrado)
                else:
                    ws.set_column(f"{col_letter}:{col_letter}", 20)

        output.seek(0)
        return output

    st.download_button(
        label="📄 Descargar Excel Cédula Auditor",
        data=exportar_excel(),
        file_name="Cedula_Auditor_Umbral15_OK.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("📥 Por favor, sube un archivo Excel para comenzar.")
