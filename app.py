
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

# --- ENCABEZADO DE LA APP ---
st.markdown("<h1 style='text-align: center; color: white;'>Auditoría a Gastos por País - Grupo FarmaValue_Herson Hernández</h1>", unsafe_allow_html=True)
archivo = st.file_uploader("📥 Sube tu archivo Excel", type=["xlsx"])

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

    # --- UMBRALES DE RIESGO ---
    st.markdown("---")
    st.markdown("## 🛑 Tabla de Umbrales de Riesgo")
    st.markdown("""
    <table style='width:100%; text-align:center;'>
        <tr><th>🔴 Crítico</th><th>🟡 Moderado</th><th>🟢 Bajo</th></tr>
        <tr><td>≥ RD$2,000,000</td><td>≥ RD$1,000,000 y < RD$2,000,000</td><td>< RD$1,000,000</td></tr>
    </table>
    """, unsafe_allow_html=True)

    def clasificar_riesgo(monto):
        if monto >= 2000000:
            return "🔴 Crítico"
        elif monto >= 1000000:
            return "🟡 Moderado"
        else:
            return "🟢 Bajo"

    df['Grupo_Riesgo'] = df.groupby('Categoria')['Monto'].transform('sum').apply(clasificar_riesgo)

    # --- CRITERIO SEGURO ---
    palabras_clave = [
        "recuperación", "seguro", "diferencia", "no cobrados", "ajuste",
        "reclasificación", "ARS", "SENASA", "MAPFRE", "AFILIADO", "ASEGURADO", "CXC"
    ]
    # Detectar todas las descripciones sospechosas
    sospechosas = df['Descripcion'].dropna().astype(str).apply(
        lambda x: any(p.lower() in x.lower() for p in palabras_clave)
    )
    descripciones_sospechosas = df.loc[sospechosas, 'Descripcion'].unique()

    # Aplicar la lógica para todos los duplicados de esas descripciones
    df['Sospechosa'] = df['Descripcion'].isin(descripciones_sospechosas)
    df['¿Revisar?'] = df['Sospechosa'].map({True: "Sí"}).fillna("No")
    df['Descripcion'] = df.apply(
        lambda row: f"<span style='color:red'>{row['Descripcion']}</span>" if row['Sospechosa'] else row['Descripcion'],
        axis=1
    )

    df['Monto del Gasto'] = df['Monto'].round(2)
    df['Gasto Total de la Sucursal'] = df.groupby(['Sucursales', 'Mes'])['Monto'].transform('sum').round(2)
    df['% Participación'] = ((df['Monto'] / df['Gasto Total de la Sucursal']) * 100).round(2)
    df['Verificado (☐)'] = "☐"
    df['No Verificado (☐)'] = "☐"
    df['Comentario del Auditor'] = ""
    df['Fecha'] = df['Fecha'].dt.strftime('%d/%m/%Y')

    columnas = [
        'Sucursales', 'Grupo_Riesgo', 'Categoria', 'Descripcion', 'Fecha',
        'Monto del Gasto', 'Gasto Total de la Sucursal', '% Participación',
        '¿Revisar?', 'Verificado (☐)', 'No Verificado (☐)', 'Comentario del Auditor'
    ]

    df_out = df[columnas].rename(columns={
        "Sucursales": "Sucursal", "Categoria": "Categoría", "Descripcion": "Descripción"
    }).sort_values(by=['% Participación'], ascending=False)

    def generar_excel():
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            wb = writer.book
            header = wb.add_format({'bold': True, 'font_size': 28, 'font_color': 'red'})
            subheader = wb.add_format({'font_size': 12})

            df_out.to_excel(writer, sheet_name="Cédula Auditor", startrow=5, index=False)
            ws1 = writer.sheets["Cédula Auditor"]
            ws1.write("A1", "Auditoría grupo Farmavalue", header)
            ws1.write("A2", "Reporte de gastos del 01 de Enero al 20 de abril del 2025", subheader)
            ws1.write("A3", "Auditor Asignado:", subheader)
            ws1.write("A4", "Fecha de la Auditoría", subheader)

        output.seek(0)
        return output

    st.download_button(
        label="📄 Descargar Excel Cédula Auditor",
        data=generar_excel(),
        file_name="Cedula_Trabajo_OK_FINAL.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("📥 Por favor, sube un archivo Excel para comenzar.")
