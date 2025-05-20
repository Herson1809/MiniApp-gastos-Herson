import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import xlsxwriter

# --- CONFIGURACIÓN DE LA APP ---
st.set_page_config(page_title="Auditoría de Gastos - Grupo FarmaValue", layout="wide")

# --- BLOQUE DE SEGURIDAD ---
st.markdown("<h2 style='text-align: center;'>🔐 Acceso a la Auditoría de Gastos</h2>", unsafe_allow_html=True)
password = st.text_input("Ingresa la contraseña para acceder a la aplicación:", type="password")
if password != "Herson2025":
    st.warning("🔒 Acceso restringido. Por favor, ingresa la contraseña correcta.")
    st.stop()

# --- ENCABEZADO ---
st.markdown("<h1 style='text-align: center; color: white;'>Auditoría a Gastos por País - Grupo FarmaValue_Herson Hernández</h1>", unsafe_allow_html=True)
st.markdown("### 📥 Sube tu archivo Excel")
archivo = st.file_uploader("Selecciona tu archivo de gastos", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df['Mes'] = df['Fecha'].dt.strftime('%B')

    meses_orden = ['January', 'February', 'March', 'April']
    df['Mes'] = pd.Categorical(df['Mes'], categories=meses_orden, ordered=True)

    # BLOQUE 1: GRÁFICO Y TOTALES
    resumen_mes = df.groupby('Mes')['Monto'].sum().reindex(meses_orden)
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### 📊 Gasto por Mes")
        fig, ax = plt.subplots()
        colores = ['#3498db', '#f39c12', '#2ecc71', '#9b59b6']
        resumen_mes.plot(kind='bar', ax=ax, color=colores)
        ax.set_title("Gasto Mensual")
        st.pyplot(fig)

    with col2:
        st.markdown("### 🧾 Totales por Mes")
        for mes, valor in resumen_mes.items():
            st.metric(label=mes, value=f"RD${valor:,.0f}")
        st.metric(label="Gran Total", value=f"RD${resumen_mes.sum():,.0f}")

    # BLOQUE 2: UMBRALES
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

    # BLOQUE 3: ANÁLISIS POR RIESGO
    resumen = pd.pivot_table(df, index=['Categoria', 'Grupo_Riesgo'], columns='Mes', values='Monto', aggfunc='sum', fill_value=0).reset_index()
    resumen['Total general'] = resumen[meses_orden].sum(axis=1)
    resumen = resumen.sort_values(by='Total general', ascending=False).reset_index(drop=True)
    resumen.insert(0, 'No', resumen.index + 1)
    resumen = resumen[resumen['Total general'] > 0]

    # FILTRO
    st.markdown("### 🔎 Filtra por Grupo de Riesgo")
    opciones = ['Ver Todos'] + sorted(resumen['Grupo_Riesgo'].dropna().unique())
    seleccion = st.selectbox("Selecciona un grupo de riesgo:", opciones)

    resumen_filtrado = resumen if seleccion == 'Ver Todos' else resumen[resumen['Grupo_Riesgo'] == seleccion]
    total_row = resumen_filtrado[meses_orden + ['Total general']].sum()
    total_row = pd.DataFrame([["", "TOTAL GENERAL", ""] + list(total_row)], columns=resumen_filtrado.columns)
    resumen_final = pd.concat([resumen_filtrado, total_row], ignore_index=True)

    for col in meses_orden + ['Total general']:
        resumen_final[col] = resumen_final[col].apply(lambda x: f"{x:,.2f}" if pd.notna(x) else x)

    st.dataframe(resumen_final[['No', 'Categoria', 'Grupo_Riesgo'] + meses_orden + ['Total general']], use_container_width=True)

    # BLOQUE 4: CÉDULA AUDITOR (aplicando color rojo por descripción global)
    palabras_clave = ['recuperación', 'seguro', 'diferencia', 'no cobrados', 'ajuste',
                      'reclasificación', 'ars', 'senasa', 'mapfre', 'afiliado', 'asegurado', 'cxc']

    df['Descripcion'] = df['Descripcion'].astype(str)
    df['es_sospechosa'] = df['Descripcion'].str.lower().apply(lambda x: any(p in x for p in palabras_clave))

    descripciones_marcadas = df[df['es_sospechosa']]['Descripcion'].unique().tolist()
    df['Descripcion_Roja'] = df['Descripcion'].apply(lambda x: f"<span style='color:red'>{x}</span>" if x in descripciones_marcadas else x)
    df['¿Revisar?'] = df['Descripcion'].apply(lambda x: "Sí" if x in descripciones_marcadas else "No")

    df['Monto del Gasto'] = df['Monto'].round(2)
    df['Gasto Total Sucursal'] = df.groupby('Sucursales')['Monto'].transform('sum').round(2)
    df['% Participación'] = ((df['Monto'] / df['Gasto Total Sucursal']) * 100).round(2)
    df['Verificado (☐)'] = "☐"
    df['No Verificado (☐)'] = "☐"
    df['Comentario del Auditor'] = ""

    cedula = df[[
        'Sucursales', 'Grupo_Riesgo', 'Categoria', 'Descripcion_Roja', 'Fecha', 'Monto del Gasto',
        'Gasto Total Sucursal', '% Participación', '¿Revisar?', 'Verificado (☐)',
        'No Verificado (☐)', 'Comentario del Auditor']].rename(columns={
            "Sucursales": "Sucursal",
            "Categoria": "Categoría",
            "Descripcion_Roja": "Descripción"
        })

    cedula = cedula.sort_values(by=['Sucursal', '% Participación'], ascending=[True, False])
    cedula['Fecha'] = pd.to_datetime(cedula['Fecha']).dt.strftime('%d/%m/%Y')

    # BLOQUE 5: CRITERIOS
    criterios = pd.DataFrame({
        "Criterio": [
            "Monto mayor o igual a RD$2,000,000",
            "Participación mayor al 15%",
            "Descripción sospechosa (ej: seguros, CxC, etc.)"
        ],
        "Aplicación": [
            "Riesgo Crítico automático",
            "Alta participación en gasto de sucursal",
            "Encubrimiento o error operativo"
        ]
    })

    # BLOQUE 6: DESCARGA
    def generar_excel():
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            wb = writer.book
            header = wb.add_format({'bold': True, 'font_size': 28, 'font_color': 'red'})
            sub = wb.add_format({'font_size': 12})

            resumen_final.to_excel(writer, sheet_name="Resumen por Categoría", startrow=5, index=False)
            ws1 = writer.sheets["Resumen por Categoría"]
            ws1.write("A1", "Auditoría grupo Farmavalue", header)
            ws1.write("A2", "Reporte de gastos del 01 de Enero al 20 de abril del 2025", sub)
            ws1.write("A3", "Auditor Asignado:", sub)
            ws1.write("A4", "Fecha de la Auditoría", sub)

            criterios.to_excel(writer, sheet_name="Criterios de Revisión Auditor", startrow=5, index=False)
            ws2 = writer.sheets["Criterios de Revisión Auditor"]
            ws2.write("A1", "Auditoría grupo Farmavalue", header)
            ws2.write("A2", "Reporte de gastos del 01 de Enero al 20 de abril del 2025", sub)
            ws2.write("A3", "Auditor Asignado:", sub)
            ws2.write("A4", "Fecha de la Auditoría", sub)

            cedula.to_excel(writer, sheet_name="Cédula Auditor", startrow=5, index=False)
            ws3 = writer.sheets["Cédula Auditor"]
            ws3.write("A1", "Auditoría grupo Farmavalue", header)
            ws3.write("A2", "Reporte de gastos del 01 de Enero al 20 de abril del 2025", sub)
            ws3.write("A3", "Auditor Asignado:", sub)
            ws3.write("A4", "Fecha de la Auditoría", sub)

        output.seek(0)
        return output

    st.markdown("---")
    st.download_button(
        label="📄 Descargar Excel Consolidado",
        data=generar_excel(),
        file_name="Cedula_Trabajo_3Hojas_OK.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("📥 Por favor, sube un archivo Excel para comenzar.")
