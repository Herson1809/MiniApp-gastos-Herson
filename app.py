import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import xlsxwriter

# --- BLOQUE DE SEGURIDAD ---
st.set_page_config(page_title="Acceso Seguro - FarmaValue", layout="wide")
st.markdown("<h2 style='text-align: center;'>\U0001f512 Acceso a la Auditoría de Gastos</h2>", unsafe_allow_html=True)
password = st.text_input("Ingresa la contraseña para acceder a la aplicación:", type="password")
if password != "Herson2025":
    st.warning("\U0001f512 Acceso restringido. Por favor, ingresa la contraseña correcta.")
    st.stop()

# --- ENCABEZADO DE LA APP ---
st.markdown("<h1 style='text-align: center; color: white;'>Auditoría a Gastos por País - Grupo FarmaValue_Herson Hernández</h1>", unsafe_allow_html=True)
archivo = st.file_uploader("\U0001f4c5 Sube tu archivo Excel", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df['Mes'] = df['Fecha'].dt.strftime('%B').astype(str)
    meses_orden = ['January', 'February', 'March', 'April']
    df['Mes'] = pd.Categorical(df['Mes'], categories=meses_orden, ordered=True)

    resumen_mes = df.groupby('Mes')['Monto'].sum().reindex(meses_orden)
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### \U0001f4ca Gasto por Mes")
        fig, ax = plt.subplots()
        colores = ['#3498db', '#f39c12', '#2ecc71', '#9b59b6']
        resumen_mes.plot(kind='bar', ax=ax, color=colores)
        ax.set_title("Gasto Mensual")
        ax.set_ylabel("")
        st.pyplot(fig)

    with col2:
        st.markdown("### \U0001f9be Totales por Mes")
        for mes, valor in resumen_mes.items():
            st.metric(label=mes, value=f"RD${valor:,.0f}")
        st.markdown("---")
        st.metric(label="Gran Total", value=f"RD${resumen_mes.sum():,.0f}")

    # --- UMBRALES DE RIESGO ---
    st.markdown("---")
    st.markdown("## \U0001f6d1 Tabla de Umbrales de Riesgo")
    st.markdown("""
    <table style='width:100%; text-align:center;'>
        <tr><th>\U0001f534 Crítico</th><th>\U0001f7e1 Moderado</th><th>\U0001f7e2 Bajo</th></tr>
        <tr><td>≥ RD$2,000,000</td><td>≥ RD$1,000,000 y < RD$2,000,000</td><td>< RD$1,000,000</td></tr>
    </table>
    """, unsafe_allow_html=True)

    def clasificar_riesgo(monto):
        if monto >= 2000000:
            return "\U0001f534 Crítico"
        elif monto >= 1000000:
            return "\U0001f7e1 Moderado"
        else:
            return "\U0001f7e2 Bajo"

    df['Grupo_Riesgo'] = df.groupby('Categoria')['Monto'].transform('sum').apply(clasificar_riesgo)

    df['Gasto Total Sucursal Mes'] = df.groupby(['Sucursales', 'Mes'])['Monto'].transform('sum')
    df['% Participación'] = (df['Monto'] / df['Gasto Total Sucursal Mes']) * 100
    df['% Participación'] = df['% Participación'].round(2)

    criterios_snack = df['Descripcion'].str.contains("comida|snack|sin comprobante|misc|varios", case=False, na=False)
    sospechoso = df['Descripcion'].str.contains("recuperación|seguro|diferencia|no cobrados|ajuste|reclasificación|ARS|SENASA|MAPFRE|AFILIADO|ASEGURADO|CXC", case=False, na=False)

    criterio_revisar = (
        (df['Monto'] >= 2000000) |
        (df['% Participación'] > 15) |
        criterios_snack |
        sospechoso
    )

    df['¿Revisar?'] = criterio_revisar.map({True: "Sí", False: "No"})
    df['Monto del Gasto'] = df['Monto'].round(2)
    df['Gasto Total de la Sucursal'] = df['Gasto Total Sucursal Mes'].round(2)
    df['Verificado (☐)'] = "☐"
    df['No Verificado (☐)'] = "☐"
    df['Comentario del Auditor'] = ""

    df['Color'] = df['Descripcion'].apply(
        lambda x: 'color: red;' if isinstance(x, str) and
        any(palabra in x.lower() for palabra in [
            'recuperación', 'seguro', 'diferencia', 'no cobrados', 'ajuste',
            'reclasificación', 'ars', 'senasa', 'mapfre', 'afiliado', 'asegurado', 'cxc']) else ''
    )

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
    }).sort_values(by=['% Participación'], ascending=False)

    cedula['Fecha'] = pd.to_datetime(cedula['Fecha']).dt.strftime('%d/%m/%Y')

    # --- DESCARGA EXCEL ---
    def generar_excel():
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            cedula_out = cedula[[
                'Sucursal', 'Categoría', 'Grupo_Riesgo', 'Descripción', 'Fecha',
                'Monto del Gasto', 'Gasto Total de la Sucursal', '% Participación',
                '¿Revisar?', 'Verificado (☐)', 'No Verificado (☐)', 'Comentario del Auditor']]
            cedula_out.to_excel(writer, sheet_name="Cédula Auditor", index=False)
        output.seek(0)
        return output

    st.markdown("---")
    st.download_button(
        label="\U0001f4c4 Descargar Excel Cédula Auditor",
        data=generar_excel(),
        file_name="Cedula_Trabajo_3Hojas_OK.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("\U0001f4c5 Por favor, sube un archivo Excel para comenzar.")
