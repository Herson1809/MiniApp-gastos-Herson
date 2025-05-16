
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
st.markdown("### 📥 Sube tu archivo Excel")
archivo = st.file_uploader("Selecciona tu archivo de gastos", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df['Mes'] = df['Fecha'].dt.strftime('%B').astype(str)

    meses_orden = ['January', 'February', 'March', 'April']
    df['Mes'] = pd.Categorical(df['Mes'], categories=meses_orden, ordered=True)

    resumen_mes = df.groupby('Mes')['Monto'].sum().reindex(meses_orden)
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### 📊 Gasto por Mes")
        fig, ax = plt.subplots()
        colores = ['#3498db', '#f39c12', '#2ecc71', '#9b59b6']
        resumen_mes.plot(kind='bar', ax=ax, color=colores)
        ax.set_title("Gasto Mensual")
        ax.set_ylabel("")
        st.pyplot(fig)

    with col2:
        st.markdown("### 🧾 Totales por Mes")
        for mes, valor in resumen_mes.items():
            st.metric(label=mes, value=f"RD${valor:,.0f}")
        st.markdown("---")
        st.metric(label="Gran Total", value=f"RD${resumen_mes.sum():,.0f}")

    def detectar_sospechoso(texto):
        if pd.isna(texto):
            return False
        patrones = ["recuperación", "seguro", "diferencia", "no cobrados", "ajuste", "reclasificación", "cxc", "aseguradora", "seguro médico"]
        return any(pat in str(texto).lower() for pat in patrones)

    df['% Participación'] = df.groupby(['Sucursales', 'Mes'])['Monto'].transform(lambda x: x / x.sum() * 100)
    df['Monto del Gasto'] = df['Monto']
    df['Gasto Total de la Sucursal'] = df.groupby(['Sucursales', 'Mes'])['Monto'].transform('sum')
    df['% Participación'] = df['% Participación'].round(2)

    df['¿Revisar?'] = "No"
    df.loc[(df['Monto'] >= 2_000_000) | (df['% Participación'] >= 12), '¿Revisar?'] = "Sí"

    sospechosos = df['Descripcion'].apply(detectar_sospechoso)
    df['Advertencia'] = ""
    df.loc[sospechosos, '¿Revisar?'] = "Sí"
    df.loc[sospechosos, 'Advertencia'] = "⚠ Posible encubrimiento - revisar origen del gasto"
    df['Verificado (☐)'] = ""
    df['No Verificado (☐)'] = ""
    df['Comentario del Auditor'] = ""
    df['Fecha'] = df['Fecha'].dt.strftime('%d/%m/%Y')

    df = df.sort_values(by=['% Participación', '¿Revisar?'], ascending=[False, True])
    columnas = ['Sucursales', 'Grupo_Riesgo', 'Categoria', 'Descripcion', 'Fecha',
                'Monto del Gasto', 'Gasto Total de la Sucursal', '% Participación',
                '¿Revisar?', 'Verificado (☐)', 'No Verificado (☐)', 'Comentario del Auditor', 'Advertencia']
    cedula = df[columnas]

    def generar_excel():
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            wb = writer.book
            formato_titulo = wb.add_format({'bold': True, 'font_size': 28, 'font_color': 'red'})
            formato_sub = wb.add_format({'font_size': 12})
            cedula.to_excel(writer, sheet_name="Cédula Auditor", startrow=5, index=False)
            ws = writer.sheets["Cédula Auditor"]
            ws.write("A1", "Auditoría grupo Farmavalue", formato_titulo)
            ws.write("A2", "Reporte de gastos del 01 de Enero al 20 de abril del 2025", formato_sub)
            ws.write("A3", "Auditor Asignado:", formato_sub)
            ws.write("A4", "Fecha de la Auditoría", formato_sub)
        output.seek(0)
        return output

    st.download_button(
        label="📄 Descargar Excel Cédula Auditor",
        data=generar_excel(),
        file_name="Cedula_Trabajo_Criticos_OK.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("📥 Por favor, sube un archivo Excel para comenzar.")
