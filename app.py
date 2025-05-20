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

    # --- Gráfico mensual ---
    resumen_mes = df.groupby('Mes')['Monto'].sum().reindex(meses_orden)
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### \U0001f4ca Gasto por Mes")
        fig, ax = plt.subplots()
        colores = ['#3498db', '#f39c12', '#2ecc71', '#9b59b6']
        resumen_mes.plot(kind='bar', ax=ax, color=colores)
        ax.set_title("Gasto Mensual")
        st.pyplot(fig)
    with col2:
        st.markdown("### \U0001f9be Totales por Mes")
        for mes, valor in resumen_mes.items():
            st.metric(label=mes, value=f"RD${valor:,.0f}")
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

    # --- TABLA RESUMEN ---
    resumen = pd.pivot_table(df, index=['Categoria', 'Grupo_Riesgo'], columns='Mes', values='Monto', aggfunc='sum', fill_value=0).reset_index()
    resumen['Total general'] = resumen[meses_orden].sum(axis=1)
    resumen = resumen.sort_values(by='Total general', ascending=False).reset_index(drop=True)
    resumen.insert(0, 'No', resumen.index + 1)

    st.markdown("### \U0001f50e Filtra por Grupo de Riesgo")
    opciones = ['Ver Todos'] + sorted(resumen['Grupo_Riesgo'].dropna().unique())
    seleccion = st.selectbox("Selecciona un grupo de riesgo:", opciones)
    resumen_filtrado = resumen if seleccion == 'Ver Todos' else resumen[resumen['Grupo_Riesgo'] == seleccion]
    total_row = resumen_filtrado[meses_orden + ['Total general']].sum()
    total_row = pd.DataFrame([['', 'TOTAL GENERAL', ''] + list(total_row)], columns=resumen_filtrado.columns)
    resumen_final = pd.concat([resumen_filtrado, total_row], ignore_index=True)
    for col in meses_orden + ['Total general']:
        resumen_final[col] = resumen_final[col].apply(lambda x: f"{x:,.2f}" if pd.notna(x) else x)
    st.dataframe(resumen_final[['No', 'Categoria', 'Grupo_Riesgo'] + meses_orden + ['Total general']], use_container_width=True)

    # --- CÉDULA DE AUDITORÍA ---
    df['Gasto Total Sucursal Mes'] = df.groupby(['Sucursales', 'Mes'])['Monto'].transform('sum')
    df['% Participación'] = (df['Monto'] / df['Gasto Total Sucursal Mes']) * 100
    df['% Participación'] = df['% Participación'].round(2)

    claves_seguro = ['recuperación', 'seguro', 'diferencia', 'no cobrados', 'ajuste', 'reclasificación',
                     'ars', 'senasa', 'mapfre', 'afiliado', 'asegurado', 'cxc']

    sospechoso = df['Descripcion'].astype(str).str.lower().apply(lambda x: any(clave in x for clave in claves_seguro))
    patrones_sospechosos = df[sospechoso]['Descripcion'].unique().tolist()
    df['Descripcion_Limpia'] = df['Descripcion'].astype(str)
    df['Sospechosa?'] = df['Descripcion_Limpia'].apply(lambda x: any(pat in x for pat in patrones_sospechosos))
    df['Color'] = df['Sospechosa?'].map({True: 'color: red;', False: ''})
    df['¿Revisar?'] = df['Sospechosa?'].map({True: 'Sí', False: df['% Participación'] > 15})
    df['¿Revisar?'] = df['¿Revisar?'].replace({True: 'Sí', False: 'No'})

    df['Monto del Gasto'] = df['Monto'].round(2)
    df['Gasto Total de la Sucursal'] = df['Gasto Total Sucursal Mes'].round(2)
    df['Verificado (☐)'] = "☐"
    df['No Verificado (☐)'] = "☐"
    df['Comentario del Auditor'] = ""

    columnas_finales = ['Sucursales', 'Grupo_Riesgo', 'Categoria', 'Descripcion_Limpia', 'Fecha',
                        'Monto del Gasto', 'Gasto Total de la Sucursal', '% Participación', '¿Revisar?',
                        'Verificado (☐)', 'No Verificado (☐)', 'Comentario del Auditor']
    df_cedula = df[columnas_finales].rename(columns={
        'Sucursales': 'Sucursal',
        'Categoria': 'Categoría',
        'Descripcion_Limpia': 'Descripción'
    })
    df_cedula['Fecha'] = pd.to_datetime(df_cedula['Fecha']).dt.strftime('%d/%m/%Y')
    df_cedula = df_cedula.sort_values(by=['% Participación'], ascending=False)

    # --- DESCARGA ---
    def generar_excel():
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_cedula.to_excel(writer, sheet_name="Cedula Auditor", startrow=5, index=False)
            ws = writer.sheets['Cedula Auditor']
            header = writer.book.add_format({'bold': True, 'font_size': 28, 'font_color': 'red'})
            sub = writer.book.add_format({'font_size': 12})
            ws.write("A1", "Auditoría grupo Farmavalue", header)
            ws.write("A2", "Reporte de gastos del 01 de Enero al 20 de abril del 2025", sub)
            ws.write("A3", "Auditor Asignado:", sub)
            ws.write("A4", "Fecha de la Auditoría", sub)
        output.seek(0)
        return output

    st.download_button(
        label="\U0001f4c4 Descargar Excel Cédula Auditor",
        data=generar_excel(),
        file_name="Cedula_Trabajo_3Hojas_OK.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
