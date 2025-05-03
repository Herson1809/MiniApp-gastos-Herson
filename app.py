# app.py - MiniApp Auditoría a Gastos por País - Grupo FarmaValue
import streamlit as st
import pandas as pd
import base64
from io import BytesIO

# --- TÍTULO PRINCIPAL ---
st.markdown("""
<h1 style='text-align: center; color: white;'>Auditoría a Gastos por País - Grupo FarmaValue_Herson Hernández</h1>
""", unsafe_allow_html=True)

# --- BLOQUE 1: CARGA DE ARCHIVO ---
st.markdown("### ▶️ Sube tu archivo Excel (.xlsx)")
archivo = st.file_uploader("Selecciona tu archivo de gastos", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)

    # --- BLOQUE 2: CONSTRUCCIÓN DE LA HOJA RESUMEN POR CATEGORÍA ---
    st.markdown("## 📊 Resumen por Categoría (en miles)")
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df['Mes'] = df['Fecha'].dt.strftime('%B')

    categorias = df.groupby(['Categoria'])['Monto'].sum().sort_values(ascending=False).reset_index()
    categorias['Monto'] = categorias['Monto'] / 1000

    # Cálculo por mes y total
    pivot = pd.pivot_table(df, values='Monto', index=['Categoria', 'Grupo de Riesgo'],
                           columns='Mes', aggfunc='sum', fill_value=0)
    pivot = pivot[['January', 'February', 'March', 'April']]  # mantener orden
    pivot = pivot / 1000  # convertir a miles
    pivot['Total general'] = pivot.sum(axis=1)

    pivot = pivot.reset_index()
    pivot.index += 1
    pivot.index.name = 'No'

    # Calcular totales por columna
    total_row = ['TOTAL GENERAL', '', *pivot[['January', 'February', 'March', 'April', 'Total general']].sum().round(0)]
    df_final = pd.concat([pivot, pd.DataFrame([total_row], columns=pivot.columns)], ignore_index=True)

    # Mostrar en pantalla
    st.dataframe(df_final)

    # --- BLOQUE 3: DESCARGA DE ARCHIVO FINAL ---
    st.markdown("## 📥 Descargar Reporte de Auditoría Consolidado")

    def to_excel(df):
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, index=False, sheet_name='Resumen por Categoría', startrow=4)

        # Encabezado institucional
        workbook = writer.book
        worksheet = writer.sheets['Resumen por Categoría']
        bold = workbook.add_format({'bold': True})
        red_bold = workbook.add_format({'bold': True, 'font_color': 'red', 'font_size': 16})
        normal = workbook.add_format({'font_size': 12})

        worksheet.merge_range('A1:G1', 'Auditoría grupo Farmavalue', red_bold)
        worksheet.write('A2', 'Reporte de gastos del 01 de Enero al 20 de abril del 2025', normal)
        worksheet.write('A3', 'Auditor Asignado:', bold)
        worksheet.write('A4', 'Fecha de la Auditoría:', bold)

        writer.close()
        processed_data = output.getvalue()
        return processed_data

    excel_data = to_excel(df_final)
    b64 = base64.b64encode(excel_data).decode()
    st.markdown(f"""
    <a href="data:application/octet-stream;base64,{b64}" download="Cedula_de_Trabajo_de_Auditoria_FINAL.xlsx">
        📄 Descargar Cédula de Trabajo de Auditoría
    </a>
    """, unsafe_allow_html=True)
