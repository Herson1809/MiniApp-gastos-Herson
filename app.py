# app.py - Auditoría a Gastos por País - Grupo FarmaValue

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import xlsxwriter

st.set_page_config(page_title="Auditoría FarmaValue", layout="wide")

# --- TÍTULO PRINCIPAL ---
st.markdown("<h1 style='text-align: center; color: white;'>Auditoría a Gastos por País - Grupo FarmaValue_Herson Hernández</h1>", unsafe_allow_html=True)

# --- BLOQUE 1: CARGA DE ARCHIVO ---
st.markdown("### 📥 Sube tu archivo Excel base")
archivo = st.file_uploader("Selecciona el archivo de gastos", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df['Mes'] = df['Fecha'].dt.strftime('%B')

    # --- BLOQUE 2: GRÁFICO MENSUAL ---
    resumen_mes = df.groupby(df['Mes'])['Monto'].sum().reindex(['January', 'February', 'March', 'April'])

    st.markdown("### 📊 Gasto mensual por categoría")
    fig, ax = plt.subplots()
    resumen_mes.plot(kind='bar', ax=ax, color=['#1abc9c', '#3498db', '#9b59b6', '#e67e22'])
    ax.set_ylabel("Monto")
    ax.set_xlabel("Mes")
    st.pyplot(fig)

    # --- BLOQUE 3: TABLA DE UMBRALES DE RIESGO ---
    st.markdown("### 🧾 Tabla de Umbrales de Riesgo")
    st.markdown("""
    <table style='width:100%; text-align:center;'>
        <tr><th style='color:red'>🔴 Crítico</th><th style='color:orange'>🟡 Moderado</th><th style='color:green'>🟢 Bajo</th></tr>
        <tr><td>≥ RD$6,000,000</td><td>≥ RD$3,000,000 y < RD$6,000,000</td><td>< RD$3,000,000</td></tr>
    </table>
    """, unsafe_allow_html=True)

    # --- BLOQUE 4: ANÁLISIS Y CLASIFICACIÓN DE RIESGO ---
    def clasificar_riesgo(monto):
        if monto >= 6000000:
            return "Crítico"
        elif monto >= 3000000:
            return "Moderado"
        else:
            return "Bajo"

    df['Grupo_Riesgo'] = df.groupby('Categoria')['Monto'].transform('sum').apply(clasificar_riesgo)

    # --- Generar hoja: Resumen por Categoría ---
    resumen = df.groupby(['Categoria', 'Grupo_Riesgo', 'Mes'])['Monto'].sum().unstack().fillna(0)
    resumen = resumen[['January', 'February', 'March', 'April']]
    resumen['Total general'] = resumen.sum(axis=1)
    resumen = resumen.reset_index()
    resumen.insert(0, 'No', resumen.index + 1)

    # --- BLOQUE 5: GENERAR CÉDULA DE AUDITORÍA ---
    cedula = df.copy()
    cedula['Gasto Total de la Sucursal'] = cedula.groupby('Sucursales')['Monto'].transform('sum')
    cedula['% Participación'] = cedula['Monto'] / cedula['Gasto Total de la Sucursal']
    cedula['¿Revisar?'] = cedula.apply(
        lambda row: 'Sí' if (
            row['Monto'] >= 6000000 or
            row['% Participación'] >= 0.25 or
            any(palabra in str(row['Descripcion']).lower() for palabra in ['varios', 'misc', 'sin comprobantes', 'otros', 'na']) or
            row['Monto'] < 2000
        ) else 'No', axis=1
    )

    cedula_final = cedula[[
        'Sucursales', 'Grupo_Riesgo', 'Categoria', 'Descripcion', 'Fecha', 'Monto',
        'Gasto Total de la Sucursal', '% Participación', '¿Revisar?'
    ]].copy()

    cedula_final['Verificado (☐)'] = ''
    cedula_final['No Verificado (☐)'] = ''
    cedula_final['Comentario del Auditor'] = ''
    cedula_final = cedula_final.sort_values(by=['Sucursales', 'Monto'], ascending=[True, False])
    cedula_final['Monto'] = cedula_final['Monto'].map('{:,.2f}'.format)
    cedula_final['Gasto Total de la Sucursal'] = cedula_final['Gasto Total de la Sucursal'].map('{:,.2f}'.format)
    cedula_final['% Participación'] = (cedula_final['% Participación'] * 100).map('{:.2f}%'.format)

    # --- BLOQUE 6: DESCARGA DEL ARCHIVO ---
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        wb = writer.book

        # Hoja 1: Resumen por Categoría
        resumen_sheet = resumen.copy()
        resumen_sheet.to_excel(writer, sheet_name="Resumen por Categoría", index=False, startrow=5)
        ws1 = writer.sheets["Resumen por Categoría"]
        ws1.write('A1', 'Auditoría grupo Farmavalue', wb.add_format({'bold': True, 'font_size': 28, 'font_color': 'red'}))
        ws1.write('A2', 'Reporte de gastos del 01 de Enero al 20 de abril del 2025', wb.add_format({'font_size': 12}))
        ws1.write('A3', 'Auditor Asignado:', wb.add_format({'font_size': 12}))
        ws1.write('A4', 'Fecha de la Auditoría', wb.add_format({'font_size': 12}))

        # Formato
        miles_format = wb.add_format({'num_format': '#,##0.00'})
        for col_num in range(3, 8):
            ws1.set_column(col_num, col_num, 18, miles_format)

        # Total general
        last_row = len(resumen_sheet) + 5
        ws1.write(last_row, 1, 'TOTAL GENERAL')
        for i, col in enumerate(['January', 'February', 'March', 'April', 'Total general']):
            col_letter = chr(68 + i)
            ws1.write_formula(last_row, 3 + i, f"=SUM({col_letter}6:{col_letter}{last_row})", miles_format)

        # Hoja 2: Cédula Auditoría
        cedula_final.to_excel(writer, sheet_name='Cédula Auditoría', index=False, startrow=5)
        ws2 = writer.sheets['Cédula Auditoría']
        ws2.write('A1', 'Auditoría grupo Farmavalue', wb.add_format({'bold': True, 'font_size': 28, 'font_color': 'red'}))
        ws2.write('A2', 'Reporte de gastos del 01 de Enero al 20 de abril del 2025', wb.add_format({'font_size': 12}))
        ws2.write('A3', 'Auditor Asignado:', wb.add_format({'font_size': 12}))
        ws2.write('A4', 'Fecha de la Auditoría', wb.add_format({'font_size': 12}))

    output.seek(0)
    b64 = base64.b64encode(output.read()).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="Cedula_Trabajo_Auditoria.xlsx">📥 Descargar Excel Consolidado</a>'
    st.markdown("### 📥 Descargar Cédula de Trabajo de Auditoría")
    st.markdown(href, unsafe_allow_html=True)

else:
    st.warning("⚠️ Por favor, sube un archivo Excel para comenzar.")
