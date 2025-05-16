
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import xlsxwriter
import numpy as np

# --- CONFIGURACION DE LA APP ---
st.set_page_config(page_title="Auditoría de Gastos - FarmaValue", layout="wide")
st.markdown("<h1 style='text-align: center; color: white;'>Auditoría a Gastos por País - Grupo FarmaValue_Herson Hernández</h1>", unsafe_allow_html=True)

archivo = st.file_uploader("Selecciona tu archivo de gastos", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df['Mes'] = df['Fecha'].dt.strftime('%B')
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

    st.markdown("## 🛑 Tabla de Umbrales de Riesgo")
    st.markdown("""
    <table style='width:100%; text-align:center;'>
        <tr><th>🔴 Crítico</th><th>🟡 Moderado</th><th>🟢 Bajo</th></tr>
        <tr><td>≥ RD$2,000,000 o ≥ 12%</td><td>≥ RD$1,000,000</td><td>Resto</td></tr>
    </table>
    """, unsafe_allow_html=True)

    df['Gasto Total Sucursal Mes'] = df.groupby(['Sucursales', 'Mes'])['Monto'].transform('sum')
    df['% Participación'] = (df['Monto'] / df['Gasto Total Sucursal Mes']) * 100

    sospechosas = ["recuperación", "seguro", "diferencia", "no cobrados", "ajuste", "reclasificación",
                   "ARS", "SENASA", "MAPFRE", "AFILIADO", "ASEGURADO", "CXC"]

    df['Repetido'] = df.groupby(['Mes', 'Descripcion'])['Descripcion'].transform('count')
    df['Relacionado Seguro'] = df['Descripcion'].str.lower().apply(lambda x: any(p in x for p in [s.lower() for s in sospechosas]))

    def clasificar_riesgo(row):
        if row['Monto'] >= 2000000 or row['% Participación'] >= 12:
            return "🔴 Crítico"
        elif row['Monto'] >= 1000000:
            return "🟡 Moderado"
        else:
            return "🟢 Bajo"
    df['Grupo_Riesgo'] = df.apply(clasificar_riesgo, axis=1)

    df['¿Revisar?'] = np.where(
        (df['Grupo_Riesgo'] == '🔴 Crítico') |
        (df['Repetido'] >= 3) |
        (df['Relacionado Seguro']),
        "Sí", "No"
    )

    df['Monto del Gasto'] = df['Monto'].round(2)
    df['Gasto Total de la Sucursal'] = df['Gasto Total Sucursal Mes'].round(2)
    df['% Participación'] = df['% Participación'].round(2)
    df['Verificado (☐)'] = ""
    df['No Verificado (☐)'] = ""
    df['Comentario del Auditor'] = ""

    columnas_exportar = ['Sucursales', 'Categoria', 'Descripcion', 'Fecha',
                         'Monto del Gasto', 'Gasto Total de la Sucursal', '% Participación',
                         '¿Revisar?', 'Verificado (☐)', 'No Verificado (☐)', 'Comentario del Auditor']
    cedula = df[columnas_exportar].rename(columns={
        "Sucursales": "Sucursal",
        "Categoria": "Categoría",
        "Descripcion": "Descripción"
    })

    def generar_excel():
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            wb = writer.book
            ws_name = "Cédula Auditor"
            cedula.to_excel(writer, sheet_name=ws_name, startrow=5, index=False)
            ws = writer.sheets[ws_name]
            title_format = wb.add_format({'bold': True, 'font_size': 28, 'font_color': 'red'})
            sub_format = wb.add_format({'font_size': 12})
            center = wb.add_format({'align': 'center'})
            miles = wb.add_format({'num_format': '#,##0', 'align': 'center'})
            red = wb.add_format({'font_color': 'red'})

            ws.write("A1", "Auditoría grupo Farmavalue", title_format)
            ws.write("A2", "Reporte de gastos del 01 de Enero al 20 de abril del 2025", sub_format)
            ws.write("A3", "Auditor Asignado:", sub_format)
            ws.write("A4", "Fecha de la Auditoría", sub_format)

            for col in range(4, 11):
                ws.set_column(col, col, 20, center)
            for col in [5, 6]:
                ws.set_column(col, col, 20, miles)

            desc_col = cedula.columns.get_loc("Descripción")
            for row_num, val in enumerate(cedula['Descripción'], start=5):
                if any(p.lower() in str(val).lower() for p in sospechosas):
                    ws.write(row_num, desc_col, val, red)

        output.seek(0)
        return output

    st.download_button(
        label="📥 Descargar Excel Cédula Auditor",
        data=generar_excel(),
        file_name="Cedula_Trabajo_3Hojas_OK.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
