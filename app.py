
import streamlit as st
import pandas as pd
from io import BytesIO
import xlsxwriter
import matplotlib.pyplot as plt

# --- BLOQUE DE SEGURIDAD ---
st.set_page_config(page_title="Acceso Seguro - FarmaValue", layout="wide")
st.markdown("<h2 style='text-align: center;'>🔐 Acceso a la Auditoría de Gastos</h2>", unsafe_allow_html=True)
password = st.text_input("Ingresa la contraseña para acceder a la aplicación:", type="password")
if password != "Herson2025":
    st.warning("🔒 Acceso restringido. Por favor, ingresa la contraseña correcta.")
    st.stop()

# --- CARGA Y PROCESAMIENTO DE ARCHIVO ---
st.markdown("<h1 style='text-align: center; color: white;'>Auditoría a Gastos por País - Grupo FarmaValue_Herson Hernández</h1>", unsafe_allow_html=True)
archivo = st.file_uploader("Selecciona tu archivo de gastos", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df['Mes'] = df['Fecha'].dt.strftime('%B')
    meses_orden = ['January', 'February', 'March', 'April']
    df['Mes'] = pd.Categorical(df['Mes'], categories=meses_orden, ordered=True)

    resumen_mes = df.groupby('Mes')['Monto'].sum().reindex(meses_orden)
    st.bar_chart(resumen_mes)

    def clasificar_riesgo(monto):
        if monto >= 2000000:
            return "🔴 Crítico"
        elif monto >= 1000000:
            return "🟡 Moderado"
        else:
            return "🟢 Bajo"

    df['Grupo_Riesgo'] = df.groupby('Categoria')['Monto'].transform('sum').apply(clasificar_riesgo)
    df['Gasto Total Sucursal Mes'] = df.groupby(['Sucursales', 'Mes'])['Monto'].transform('sum')
    df['% Participación'] = (df['Monto'] / df['Gasto Total Sucursal Mes']) * 100
    df['% Participación'] = df['% Participación'].round(2)

    palabras_seguro = ["seguro", "aseguradora", "reclamo", "coaseguro", "autorización", "reembolso",
                       "no pagado", "rechazo", "diferencia", "ajuste", "reclasificación", "no reconocido",
                       "factura sin respuesta", "otros gastos", "medicamento sin cobertura", "error receta"]

    aseguradoras = ["Humano", "Universal", "Mapfre", "Asismed", "Senasa", "Palic", "Simag", "Colon", "Bupa", "ARS"]

    def contiene_seguro(texto):
        texto = str(texto).lower()
        return any(palabra in texto for palabra in palabras_seguro) or any(aseg.lower() in texto for aseg in aseguradoras)

    df['Repeticiones'] = df.groupby(['Mes', 'Descripcion'])['Descripcion'].transform('count')
    gastos_repetidos = df['Repeticiones'] >= 3

    criterios_snack = df['Descripcion'].str.contains("comida|snack|sin comprobante|misc|varios", case=False, na=False)
    criterio_revisar = (
        (df['Monto'] >= 2000000) |
        (df['% Participación'] >= 12) |
        criterios_snack |
        gastos_repetidos |
        df['Descripcion'].apply(contiene_seguro)
    )

    df['¿Revisar?'] = criterio_revisar.map({True: "Sí", False: "No"})
    df['Nota Auditoría'] = df['Descripcion'].apply(lambda x: "⚠ Posible encubrimiento por seguros" if contiene_seguro(x) else "")

    df['Monto del Gasto'] = df['Monto'].round(2)
    df['Gasto Total de la Sucursal'] = df['Gasto Total Sucursal Mes'].round(2)
    df['Verificado (☐)'] = "☐"
    df['No Verificado (☐)'] = "☐"
    df['Comentario del Auditor'] = ""
    df['Fecha'] = df['Fecha'].dt.strftime('%d/%m/%Y')

    columnas = [
        'Sucursales', 'Grupo_Riesgo', 'Categoria', 'Descripcion', 'Fecha',
        'Monto del Gasto', 'Gasto Total de la Sucursal', '% Participación',
        '¿Revisar?', 'Nota Auditoría', 'Verificado (☐)', 'No Verificado (☐)', 'Comentario del Auditor'
    ]
    cedula = df[columnas].rename(columns={
        "Sucursales": "Sucursal", "Categoria": "Categoría", "Descripcion": "Descripción"
    }).sort_values(by=['% Participación', '¿Revisar?'], ascending=[False, True])

    def generar_excel():
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            wb = writer.book
            formato_encabezado = wb.add_format({'bold': True, 'font_size': 28, 'font_color': 'red'})
            formato_sub = wb.add_format({'font_size': 12})
            formato_centro = wb.add_format({'align': 'center'})
            formato_miles = wb.add_format({'num_format': '#,##0', 'align': 'center'})

            cedula.to_excel(writer, sheet_name="Cédula Auditor", startrow=5, index=False)
            ws = writer.sheets["Cédula Auditor"]
            ws.write("A1", "Auditoría grupo Farmavalue", formato_encabezado)
            ws.write("A2", "Reporte de gastos del 01 de Enero al 20 de abril del 2025", formato_sub)
            ws.write("A3", "Auditor Asignado:", formato_sub)
            ws.write("A4", "Fecha de la Auditoría", formato_sub)

            for col_idx, col in enumerate(cedula.columns):
                if col in ['Monto del Gasto', 'Gasto Total de la Sucursal']:
                    ws.set_column(col_idx, col_idx, 18, formato_miles)
                elif col in ['% Participación', '¿Revisar?', 'Nota Auditoría', 'Verificado (☐)', 'No Verificado (☐)']:
                    ws.set_column(col_idx, col_idx, 16, formato_centro)
                elif col == 'Fecha':
                    ws.set_column(col_idx, col_idx, 14, formato_centro)
                else:
                    ws.set_column(col_idx, col_idx, 22)

        output.seek(0)
        return output

    st.download_button(
        label="📄 Descargar Excel Cédula Auditor",
        data=generar_excel(),
        file_name="Cedula_Auditor_Seguros_Repetidos_OK.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("📥 Por favor, sube un archivo Excel para comenzar.")
