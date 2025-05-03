# app.py - MiniApp Auditoría a Gastos por País - Grupo FarmaValue

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
    
    resumen_mes = df.groupby('Mes')['Monto'].sum().reindex([
        'January', 'February', 'March', 'April'
    ])

    # --- BLOQUE 2: VISUALIZACIÓN GRÁFICA Y MÉTRICAS ---
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
        <tr><th>🔴 Crítico</th><th>🟡 Moderado</th><th>🟢 Bajo</th></tr>
        <tr><td>≥ RD$6,000,000</td><td>≥ RD$3,000,000 y < RD$6,000,000</td><td>< RD$3,000,000</td></tr>
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
    resumen = pd.pivot_table(
        tabla, index=['Categoria', 'Grupo_Riesgo'], columns='Mes', values='Monto',
        aggfunc='sum', fill_value=0).reset_index()
    resumen['Total general'] = resumen[['January', 'February', 'March', 'April']].sum(axis=1)
    resumen = resumen.sort_values(by='Total general', ascending=False).reset_index(drop=True)
    resumen.insert(0, 'No', resumen.index + 1)

    # --- BLOQUE 5: FILTRO DE VISUALIZACIÓN ---
    opciones = ['Ver Todos'] + sorted(resumen['Grupo_Riesgo'].unique())
    riesgo_opcion = st.selectbox("Selecciona un grupo de riesgo:", options=opciones)

    if riesgo_opcion == 'Ver Todos':
        tabla_filtrada = resumen
    else:
        tabla_filtrada = resumen[resumen['Grupo_Riesgo'] == riesgo_opcion]

    for col in ['January', 'February', 'March', 'April', 'Total general']:
        tabla_filtrada[col] = tabla_filtrada[col].apply(lambda x: f"{x:,.2f}")

    st.dataframe(tabla_filtrada[['No', 'Categoria', 'Grupo_Riesgo', 'January', 'February', 'March', 'April', 'Total general']], use_container_width=True)

    # --- BLOQUE 6: DESCARGA DEL REPORTE FINAL ---
    st.markdown("---")
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

        # Contenido desde fila 6
        resumen_final = resumen[['No', 'Categoria', 'Grupo_Riesgo', 'January', 'February', 'March', 'April', 'Total general']]
        resumen_final.to_excel(writer, sheet_name='Resumen por Categoría', startrow=5, index=False)

        # Formato de miles
        formato_miles = wb.add_format({'num_format': '#,##0.00'})
        for col_idx in range(3, 8):
            ws.set_column(col_idx, col_idx, 14, formato_miles)

        # Línea TOTAL GENERAL
        total_row = len(resumen_final) + 6
        ws.write(total_row, 1, 'TOTAL GENERAL')
        for col_idx, col in enumerate(['January', 'February', 'March', 'April', 'Total general'], start=3):
            col_letter = chr(65 + col_idx)
            ws.write_formula(total_row, col_idx, f'=SUM({col_letter}7:{col_letter}{total_row})', formato_miles)

    output.seek(0)
    b64 = base64.b64encode(output.read()).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="Cedula_Resumen_Categoria_FINAL_OK.xlsx">📄 Descargar Resumen por Categoría</a>'
    st.markdown(href, unsafe_allow_html=True)

else:
    st.info("📥 Sube un archivo Excel para comenzar.")
