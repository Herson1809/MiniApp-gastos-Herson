# app.py - Auditoría de Gastos FarmaValue
import streamlit as st
import pandas as pd
import base64
from io import BytesIO
import xlsxwriter

st.set_page_config(page_title="Auditoría FarmaValue", layout="wide")

# --- TÍTULO INSTITUCIONAL ---
st.markdown("""
<h1 style='text-align: center; color: white;'>Auditoría a Gastos por País - Grupo FarmaValue_Herson Hernández</h1>
""", unsafe_allow_html=True)

# --- BLOQUE 1: CARGA DE ARCHIVO ---
st.markdown("### 📥 Sube tu archivo Excel base")
archivo = st.file_uploader("Selecciona el archivo de gastos", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)

    # --- PROCESO DE LIMPIEZA Y CÁLCULOS ---
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df['Mes'] = df['Fecha'].dt.strftime('%B')
    df['Año'] = df['Fecha'].dt.year
    df = df[df['Año'] == 2025]  # Solo datos de 2025

    # Agrupación por Categoría
    resumen_cat = df.groupby('Categoria').agg({
        'Monto': 'sum',
        'Mes': lambda x: ', '.join(sorted(x.unique()))
    }).reset_index()

    # Clasificación de Riesgo
    def clasificar_riesgo(valor):
        if valor >= 6000000:
            return "🔴 Crítico"
        elif valor >= 3000000:
            return "🟡 Moderado"
        else:
            return "🟢 Bajo"

    resumen_cat['Grupo de Riesgo'] = resumen_cat['Monto'].apply(clasificar_riesgo)

    # Pivote mensual
    resumen_pivot = pd.pivot_table(df, values='Monto', index='Categoria', columns='Mes', aggfunc='sum', fill_value=0).reset_index()
    resumen_final = pd.merge(resumen_cat[['Categoria', 'Grupo de Riesgo']], resumen_pivot, on='Categoria', how='left')
    resumen_final['Total general'] = resumen_final.iloc[:, 2:].sum(axis=1)
    resumen_final = resumen_final.sort_values(by='Total general', ascending=False).reset_index(drop=True)
    resumen_final.index += 1
    resumen_final.insert(0, 'No', resumen_final.index)

    # --- AUDITORÍA SUCURSALES ---
    df['Grupo de Riesgo'] = df.groupby('Categoria')['Monto'].transform('sum').apply(clasificar_riesgo)
    df['Gasto Total Sucursal'] = df.groupby('Sucursales')['Monto'].transform('sum')
    df['% Participación'] = round((df['Monto'] / df['Gasto Total Sucursal']) * 100, 2)
    df['Prioridad para Revisión'] = df.apply(lambda row: '✅ Sí' if (
        row['Grupo de Riesgo'] == '🔴 Crítico' or
        (row['Grupo de Riesgo'] == '🟢 Bajo' and row['% Participación'] >= 5)
    ) else '🔍 No', axis=1)

    auditoria_suc = df[['Sucursales', 'Grupo de Riesgo', 'Categoria', 'Descripcion', 'Fecha',
                        'Monto', 'Gasto Total Sucursal', '% Participación', 'Prioridad para Revisión']].copy()
    auditoria_suc = auditoria_suc.sort_values(by=['Grupo de Riesgo', '% Participación'], ascending=[True, False])
    auditoria_suc.insert(9, 'Verificado ⬜', '')
    auditoria_suc.insert(10, 'No Verificado ⬜', '')
    auditoria_suc.insert(11, 'Comentario del Auditor', '')

    # --- EXPORTACIÓN EXCEL CON FORMATO ---
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Hoja 1: Resumen Categoría
        resumen_final.to_excel(writer, sheet_name='Resumen por Categoría', index=False, startrow=5)
        ws1 = writer.sheets['Resumen por Categoría']
        ws1.write('A1', "Auditoría grupo FarmaValue", writer.book.add_format({'bold': True, 'font_color': 'red', 'font_size': 28}))
        ws1.write('A2', "Reporte de gastos del 01 de Enero al 20 de abril del 2025", writer.book.add_format({'font_size': 12}))
        ws1.write('A3', "Auditor Asignado:", writer.book.add_format({'font_size': 12}))
        ws1.write('A4', "Fecha de la Auditoría", writer.book.add_format({'font_size': 12}))

        for col in ['January', 'February', 'March', 'April', 'Total general']:
            if col in resumen_final.columns:
                col_idx = resumen_final.columns.get_loc(col) + 1
                ws1.set_column(col_idx, col_idx, 15, writer.book.add_format({'num_format': '#,##0'}))

        # TOTAL GENERAL
        row_total = 5 + len(resumen_final)
        ws1.write(f'A{row_total + 1}', 'TOTAL GENERAL')
        for i, col in enumerate(['January', 'February', 'March', 'April', 'Total general']):
            col_letter = chr(67 + i)
            ws1.write_formula(f'{col_letter}{row_total + 1}', f'SUM({col_letter}6:{col_letter}{row_total})')

        # Hoja 2: Auditoría por Sucursales
        auditoria_suc.to_excel(writer, sheet_name='Auditoría Sucursales', index=False, startrow=5)
        ws2 = writer.sheets['Auditoría Sucursales']
        ws2.write('A1', "Auditoría grupo FarmaValue", writer.book.add_format({'bold': True, 'font_color': 'red', 'font_size': 28}))
        ws2.write('A2', "Reporte de gastos del 01 de Enero al 20 de abril del 2025", writer.book.add_format({'font_size': 12}))
        ws2.write('A3', "Auditor Asignado:", writer.book.add_format({'font_size': 12}))
        ws2.write('A4', "Fecha de la Auditoría", writer.book.add_format({'font_size': 12}))

        # Formato columnas
        ws2.set_column('E:E', 12, writer.book.add_format({'num_format': 'yyyy-mm-dd'}))
        ws2.set_column('F:G', 18, writer.book.add_format({'num_format': '#,##0.00'}))
        ws2.set_column('H:H', 15)
        ws2.set_column('I:L', 20)

    output.seek(0)
    b64 = base64.b64encode(output.read()).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="Cedula_de_Trabajo_de_Auditoria_FINAL.xlsx">📥 Descargar Cédula de Trabajo de Auditoría</a>'
    st.markdown(href, unsafe_allow_html=True)

else:
    st.warning("🔺 Sube un archivo para generar los reportes.")
