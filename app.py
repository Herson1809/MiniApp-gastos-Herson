# app.py - Auditoría de Gastos - Generación de Integración y Cédula Auditor
import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import base64

st.set_page_config(layout="wide")

# --- TÍTULO ---
st.markdown("""
<h1 style='text-align: center; color: white;'>Auditoría a Gastos por País - Grupo FarmaValue_Herson Hernández</h1>
""", unsafe_allow_html=True)

# --- CARGA DE ARCHIVO ---
archivo = st.file_uploader("📁 Sube el archivo base de gastos (.xlsx)", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df['Mes'] = df['Fecha'].dt.strftime('%B')
    
    # Total de gastos por sucursal
    total_sucursal = df.groupby('Sucursales')['Monto'].sum().reset_index()
    total_sucursal.columns = ['Sucursales', 'Gasto_Total_Sucursal']
    
    # Unir a la base original
    df_merge = df.merge(total_sucursal, on='Sucursales', how='left')
    
    # Calcular % de participación
    df_merge['% Participación'] = (df_merge['Monto'] / df_merge['Gasto_Total_Sucursal']) * 100
    
    # Clasificar Grupo de Riesgo
    def clasificar_riesgo(monto):
        if monto >= 6000000:
            return '🔴 Crítico'
        elif monto >= 3000000:
            return '🟡 Moderado'
        else:
            return '🟢 Bajo'
    
    riesgo_categoria = df_merge.groupby('Categoria')['Monto'].sum().reset_index()
    riesgo_categoria['Grupo de Riesgo'] = riesgo_categoria['Monto'].apply(clasificar_riesgo)
    
    df_merge = df_merge.merge(riesgo_categoria[['Categoria', 'Grupo de Riesgo']], on='Categoria', how='left')

    # Criterios de revisión
    def marcar_revision(row):
        descripcion = str(row['Descripcion']).lower()
        if row['Monto'] >= 500000:
            return '✅ Sí'
        if any(word in descripcion for word in ['gasto hormiga', 'varios', 'otros', 'misc', 'sundries']):
            return '✅ Sí'
        if row['% Participación'] >= 10:
            return '✅ Sí'
        return '🔍 No'
    
    df_merge['¿Revisar?'] = df_merge.apply(marcar_revision, axis=1)

    # Ordenar la integración
    integracion = df_merge.copy()
    integracion = integracion.sort_values(by=['Sucursales', 'Monto'], ascending=[True, False])

    # Crear hoja final: Cédula Auditor
    auditor_df = integracion[[
        'Sucursales', 'Grupo de Riesgo', 'Categoria', 'Descripcion', 'Fecha',
        'Monto', 'Gasto_Total_Sucursal', '% Participación', '¿Revisar?'
    ]].copy()

    auditor_df = auditor_df.rename(columns={
        'Sucursales': 'Sucursal',
        'Monto': 'Monto del Gasto',
        'Gasto_Total_Sucursal': 'Gasto Total de la Sucursal'
    })

    auditor_df['Verificado (☐)'] = ''
    auditor_df['No Verificado (☐)'] = ''
    auditor_df['Comentario del Auditor'] = ''
    auditor_df['% Participación'] = auditor_df['% Participación'].round(2)
    auditor_df = auditor_df.sort_values(by=['Sucursal', '% Participación'], ascending=[True, False])

    # Generar Excel para descarga
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        integracion.to_excel(writer, sheet_name="Integración de gastos", index=False)
        hoja_auditor = 'Cédula Auditor'
        auditor_df.to_excel(writer, sheet_name=hoja_auditor, index=False)
        
        # Encabezado institucional
        workbook = writer.book
        worksheet = writer.sheets[hoja_auditor]

        title_format = workbook.add_format({'bold': True, 'font_color': 'red', 'font_size': 28, 'align': 'left'})
        subtitle_format = workbook.add_format({'font_size': 12, 'align': 'left'})
        center_format = workbook.add_format({'align': 'center'})
        money_format = workbook.add_format({'num_format': '#,##0.00'})
        percent_format = workbook.add_format({'num_format': '0.00', 'align': 'center'})

        # Insertar encabezado
        worksheet.merge_range('A1:M1', "Auditoría grupo Farmavalue", title_format)
        worksheet.merge_range('A2:M2', "Reporte de gastos del 01 de Enero al 20 de abril del 2025", subtitle_format)
        worksheet.write('A3', "Auditor Asignado:", subtitle_format)
        worksheet.write('A4', "Fecha de la Auditoría", subtitle_format)

        # Aplicar formato desde fila 6
        for col_num, value in enumerate(auditor_df.columns.values):
            worksheet.write(5, col_num, value, center_format)

        worksheet.set_column('F:G', 18, money_format)
        worksheet.set_column('H:H', 16, percent_format)
        worksheet.set_column('A:E', 20)
        worksheet.set_column('I:L', 16)
        worksheet.set_column('M:M', 30)

        # Ajustar alto de filas del encabezado
        worksheet.set_row(0, 32)
        worksheet.set_row(1, 18)

    output.seek(0)
    b64 = base64.b64encode(output.read()).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="Reporte_Integracion_Cedula.xlsx">📥 Descargar Reporte Integrado</a>'
    st.markdown(href, unsafe_allow_html=True)

else:
    st.info("📁 Por favor sube un archivo Excel válido para comenzar.")
