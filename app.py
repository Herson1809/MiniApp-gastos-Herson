# app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import xlsxwriter

st.set_page_config(page_title="Auditoría de Gastos - FarmaValue", layout="wide")

# TÍTULO
st.markdown("<h1 style='text-align: center; color: white;'>Auditoría a Gastos por País - Grupo FarmaValue_Herson Hernández</h1>", unsafe_allow_html=True)

# BLOQUE 1: CARGA DE ARCHIVO
st.markdown("### ▶️ Sube tu archivo Excel (.xlsx)")
archivo = st.file_uploader("Selecciona tu archivo de gastos", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df['Mes'] = df['Fecha'].dt.strftime('%B')

    meses = ['January', 'February', 'March', 'April']
    df['Mes'] = pd.Categorical(df['Mes'], categories=meses, ordered=True)
    resumen_mes = df.groupby('Mes')['Monto'].sum().reindex(meses).fillna(0)

    # BLOQUE 2: GRÁFICA Y TOTALES
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### 📊 Gasto mensual por categoría")
        fig, ax = plt.subplots()
        resumen_mes.plot(kind='bar', color=['#3498db', '#f39c12', '#2ecc71', '#9b59b6'], ax=ax)
        ax.set_title("Gasto Mensual")
        ax.set_ylabel("Monto")
        ax.set_xlabel("Mes")
        ax.set_xticklabels(meses, rotation=0)
        st.pyplot(fig)

    with col2:
        st.markdown("### 🧾 Totales por Mes")
        for mes in meses:
            st.metric(mes, f"RD${resumen_mes[mes]:,.0f}")
        st.markdown("---")
        st.metric("Gran Total", f"RD${resumen_mes.sum():,.0f}")

    # BLOQUE 3: UMBRAL
    st.markdown("## 🛑 Tabla de Umbrales de Riesgo")
    st.markdown("""
        <table style='width:100%; text-align:center;'>
        <tr><th>🔴 Crítico</th><th>🟡 Moderado</th><th>🟢 Bajo</th></tr>
        <tr><td>≥ RD$6,000,000</td><td>≥ RD$3,000,000 y < RD$6,000,000</td><td>< RD$3,000,000</td></tr>
        </table>
    """, unsafe_allow_html=True)

    # BLOQUE 4: FILTRO Y RESUMEN
    def clasificar_riesgo(monto):
        if monto >= 6000000:
            return "🔴 Crítico"
        elif monto >= 3000000:
            return "🟡 Moderado"
        else:
            return "🟢 Bajo"

    tabla = df.copy()
    tabla['Grupo_Riesgo'] = tabla.groupby('Categoria')['Monto'].transform('sum').apply(clasificar_riesgo)
    resumen = pd.pivot_table(tabla, index=['Categoria', 'Grupo_Riesgo'], columns='Mes', values='Monto', aggfunc='sum', fill_value=0).reset_index()
    resumen['Total general'] = resumen[meses].sum(axis=1)
    resumen = resumen.sort_values('Total general', ascending=False).reset_index(drop=True)
    resumen.insert(0, 'No', resumen.index + 1)

    opcion = st.selectbox("Selecciona un grupo de riesgo:", ['Ver Todos'] + list(resumen['Grupo_Riesgo'].unique()))
    resumen_filtrado = resumen if opcion == 'Ver Todos' else resumen[resumen['Grupo_Riesgo'] == opcion]

    fila_total = {
        'No': '',
        'Categoria': 'TOTAL GENERAL',
        'Grupo_Riesgo': '',
        **{mes: resumen_filtrado[mes].sum() for mes in meses},
        'Total general': resumen_filtrado['Total general'].sum()
    }
    resumen_filtrado = pd.concat([resumen_filtrado, pd.DataFrame([fila_total])], ignore_index=True)

    for col in meses + ['Total general']:
        resumen_filtrado[col] = resumen_filtrado[col].apply(lambda x: f"{x:,.2f}" if isinstance(x, (int, float)) else x)

    st.dataframe(resumen_filtrado[['No', 'Categoria', 'Grupo_Riesgo'] + meses + ['Total general']], use_container_width=True)

    # BLOQUE 5: DESCARGA EXCEL
    st.markdown("## 📥 Descargar Cédula de Trabajo de Auditoría")

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        wb = writer.book
        ws = wb.add_worksheet('Resumen por Categoría')
        writer.sheets['Resumen por Categoría'] = ws

        # Encabezado personalizado
        ws.write('A1', 'Auditoría grupo Farmavalue', wb.add_format({'bold': True, 'font_size': 28, 'font_color': 'red'}))
        ws.write('A2', 'Reporte de gastos del 01 de Enero al 20 de abril del 2025', wb.add_format({'font_size': 12}))
        ws.write('A3', 'Auditor Asignado:', wb.add_format({'font_size': 12}))
        ws.write('A4', 'Fecha de la Auditoría', wb.add_format({'font_size': 12}))

        resumen_export = resumen[['No', 'Categoria', 'Grupo_Riesgo'] + meses + ['Total general']]
        resumen_export.to_excel(writer, sheet_name='Resumen por Categoría', startrow=5, index=False)

        formato_miles = wb.add_format({'num_format': '#,##0.00'})
        for col in range(3, 8):
            ws.set_column(col, col, 15, formato_miles)

        total_row = len(resumen_export) + 6
        ws.write(total_row, 1, 'TOTAL GENERAL')
        for idx, col in enumerate(meses + ['Total general'], start=3):
            letra = chr(65 + idx)
            ws.write_formula(total_row, idx, f'=SUM({letra}7:{letra}{total_row})', formato_miles)

    output.seek(0)
    b64 = base64.b64encode(output.read()).decode()
    st.markdown(f'<a href="data:application/octet-stream;base64,{b64}" download="Cedula_Resumen_Categoria_FINAL_OK.xlsx">📄 Descargar Excel Consolidado</a>', unsafe_allow_html=True)

else:
    st.info("📥 Sube un archivo Excel para comenzar.")
