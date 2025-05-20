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

    resumen = pd.pivot_table(df, index=['Categoria', 'Grupo_Riesgo'], columns='Mes', values='Monto', aggfunc='sum', fill_value=0).reset_index()
    resumen['Total general'] = resumen[meses_orden].sum(axis=1)
    resumen = resumen.sort_values(by='Total general', ascending=False).reset_index(drop=True)
    resumen.insert(0, 'No', resumen.index + 1)
    resumen = resumen[resumen['Total general'] > 0]

    st.markdown("### 🔎 Filtra por Grupo de Riesgo")
    opciones = ['Ver Todos'] + sorted(resumen['Grupo_Riesgo'].dropna().unique())
    seleccion = st.selectbox("Selecciona un grupo de riesgo:", opciones)

    resumen_filtrado = resumen if seleccion == 'Ver Todos' else resumen[resumen['Grupo_Riesgo'] == seleccion]
    total_row = resumen_filtrado[meses_orden + ['Total general']].sum()
    total_row = pd.DataFrame([['', 'TOTAL GENERAL', ''] + list(total_row)], columns=resumen_filtrado.columns)
    resumen_final = pd.concat([resumen_filtrado, total_row], ignore_index=True)

    for col in meses_orden + ['Total general']:
        resumen_final[col] = resumen_final[col].apply(lambda x: f"{x:,.2f}" if pd.notna(x) else x)

    st.dataframe(resumen_final[['No', 'Categoria', 'Grupo_Riesgo'] + meses_orden + ['Total general']], use_container_width=True)

    # --- GENERACIÓN DE LA CÉDULA ---
    if 'Mes' in df.columns and 'Sucursales' in df.columns:
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
                'reclasificación', 'ars', 'senasa', 'mapfre', 'afiliado', 'asegurado', 'cxc'
            ]) else ''
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
    else:
        cedula = pd.DataFrame()

    criterios = pd.DataFrame({
        "Criterio": [
            "Monto mayor o igual a RD$2,000,000",
            "Participación mayor al 15%",
            "Descripción sospechosa (ej: snack, sin comprobante, etc.)",
            "Repetidos +3 veces (gasto hormiga)",
            "Relación con seguros (CxC, ARS, MAPFRE...)"
        ],
        "Aplicación": [
            "Riesgo Crítico automático",
            "Alta participación en gasto de sucursal",
            "Revisión de concepto",
            "Sujeto a revisión",
            "Marcado en rojo y sujeto a revisión"
        ]
    })

    # --- DESCARGA EXCEL ---
    def generar_excel():
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            wb = writer.book
            header = wb.add_format({'bold': True, 'font_size': 28, 'font_color': 'red'})
            subheader = wb.add_format({'font_size': 12})

            resumen_final.to_excel(writer, sheet_name="Resumen por Categoría", startrow=5, index=False)
            ws1 = writer.sheets["Resumen por Categoría"]
            ws1.write("A1", "Auditoría grupo Farmavalue", header)
            ws1.write("A2", "Reporte de gastos del 01 de Enero al 20 de abril del 2025", subheader)
            ws1.write("A3", "Auditor Asignado:", subheader)
            ws1.write("A4", "Fecha de la Auditoría", subheader)

            criterios.to_excel(writer, sheet_name="Criterios de Revisión Auditor", startrow=5, index=False)
            ws2 = writer.sheets["Criterios de Revisión Auditor"]
            ws2.write("A1", "Auditoría grupo Farmavalue", header)
            ws2.write("A2", "Reporte de gastos del 01 de Enero al 20 de abril del 2025", subheader)
            ws2.write("A3", "Auditor Asignado:", subheader)
            ws2.write("A4", "Fecha de la Auditoría", subheader)

            if not cedula.empty:
                cedula.to_excel(writer, sheet_name="Cédula Auditor", startrow=5, index=False)
                ws3 = writer.sheets["Cédula Auditor"]
                ws3.write("A1", "Auditoría grupo Farmavalue", header)
                ws3.write("A2", "Reporte de gastos del 01 de Enero al 20 de abril del 2025", subheader)
                ws3.write("A3", "Auditor Asignado:", subheader)
                ws3.write("A4", "Fecha de la Auditoría", subheader)

        output.seek(0)
        return output

    st.markdown("---")
    st.download_button(
        label="📄 Descargar Excel Cédula Auditor",
        data=generar_excel(),
        file_name="Cedula_Trabajo_3Hojas_OK.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("📥 Por favor, sube un archivo Excel para comenzar.")
