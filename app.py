# app.py - MiniApp Auditoría de Gastos por Categoría (Final Validado)
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import xlsxwriter

# --- TÍTULO PRINCIPAL ---
st.markdown("""
<h1 style='text-align: center; color: white;'>Auditoría a Gastos por País - Grupo FarmaValue_Herson Hernández</h1>
""", unsafe_allow_html=True)

# --- BLOQUE 1: CARGA DE ARCHIVO ---
st.markdown("### ▶️ Sube tu archivo Excel (.xlsx)")
archivo = st.file_uploader("Selecciona tu archivo de gastos", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df['Mes'] = df['Fecha'].dt.strftime('%B')

    # --- BLOQUE 2: VISUALIZACIÓN GRÁFICA ---
    resumen_mes = df.groupby('Mes')['Monto'].sum().reindex([
        'January', 'February', 'March', 'April'
    ])

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 📊 Gasto por Mes")
        fig, ax = plt.subplots(figsize=(6, 4))
        colores = ['#3498db', '#f39c12', '#2ecc71', '#9b59b6']
        resumen_mes.dropna().plot(kind='bar', ax=ax, color=colores)
        ax.set_xlabel("Mes")
        ax.set_ylabel("Monto")
        ax.set_title("Gasto Mensual")
        ax.set_xticklabels(resumen_mes.dropna().index, rotation=0)
        ax.get_yaxis().set_visible(False)
        st.pyplot(fig)

    with col2:
        st.markdown("### 🧾 Totales por Mes")
        for mes, valor in resumen_mes.dropna().items():
            st.metric(label=mes, value=f"RD${valor:,.0f}")
        st.markdown("---")
        st.metric(label="Gran Total", value=f"RD${resumen_mes.sum():,.0f}")

    # --- BLOQUE 3: TABLA DE UMBRALES ---
    st.markdown("---")
    st.markdown("## 🛑 Tabla de Umbrales de Riesgo")
    st.markdown("""
    <table style='width:100%; text-align:center;'>
        <tr>
            <th>🔴 Crítico</th><th>🟡 Moderado</th><th>🟢 Bajo</th>
        </tr>
        <tr>
            <td>≥ RD$6,000,000</td><td>≥ RD$3,000,000 y < RD$6,000,000</td><td>< RD$3,000,000</td>
        </tr>
    </table>
    """, unsafe_allow_html=True)

    # --- BLOQUE 4: ANÁLISIS POR RIESGO ---
    st.markdown("## 🔍 Análisis por Nivel de Riesgo")

    def clasificar_riesgo(monto_total):
        if monto_total >= 6000000:
            return "🔴 Crítico"
        elif monto_total >= 3000000:
            return "🟡 Moderado"
        else:
            return "🟢 Bajo"

    tabla = df.copy()
    tabla['Grupo_Riesgo'] = tabla.groupby('Categoria')['Monto'].transform('sum').apply(clasificar_riesgo)

    resumen = pd.pivot_table(tabla, index=['Categoria', 'Grupo_Riesgo'], columns='Mes', values='Monto', aggfunc='sum', fill_value=0)
    resumen['Total'] = resumen.sum(axis=1)
    resumen = resumen.reset_index()

    resumen['No'] = range(1, len(resumen) + 1)
    resumen = resumen[['No', 'Categoria', 'Grupo_Riesgo', 'January', 'February', 'March', 'April', 'Total']]
    resumen = resumen.sort_values(by='Total', ascending=False).reset_index(drop=True)

    total_row = pd.DataFrame(resumen[['January', 'February', 'March', 'April', 'Total']].sum()).T
    total_row.insert(0, 'Grupo_Riesgo', '')
    total_row.insert(0, 'Categoria', 'TOTAL GENERAL')
    total_row.insert(0, 'No', '')
    resumen = pd.concat([resumen, total_row], ignore_index=True)

    # Formato en miles y con 2 decimales
    columnas_miles = ['January', 'February', 'March', 'April', 'Total']
    for col in columnas_miles:
        resumen[col] = resumen[col].apply(lambda x: f"{x/1000:,.2f}" if pd.notnull(x) and x != '' else '')

    st.dataframe(resumen, use_container_width=True)

    # --- BLOQUE 5: DESCARGA DE REPORTE ---
    st.markdown("---")
    st.markdown("## 🧾 Descargar Cédula de Resumen por Categoría")

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        resumen.to_excel(writer, sheet_name='Resumen por Categoría', index=False, startrow=5)
        workbook = writer.book
        worksheet = writer.sheets['Resumen por Categoría']

        # Encabezado personalizado
        encabezado = [
            ("A1", "Auditoría grupo Farmavalue", 28, 'red'),
            ("A2", "Reporte de gastos del 01 de Enero al 20 de abril del 2025", 12, 'black'),
            ("A3", "Auditor Asignado:", 12, 'black'),
            ("A4", "Fecha de la Auditoría", 12, 'black')
        ]
        for cell, text, size, color in encabezado:
            formato = workbook.add_format({'font_size': size, 'bold': True, 'font_color': color})
            worksheet.write(cell, text, formato)

    output.seek(0)
    b64 = base64.b64encode(output.read()).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="Cedula_Resumen_Categoria_FINAL_OK.xlsx">📄 Descargar Excel Validado</a>'
    st.markdown(href, unsafe_allow_html=True)
