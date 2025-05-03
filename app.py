import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import xlsxwriter

# --- 1. Título Principal ---
st.markdown("""
<h1 style='text-align: center; color: white;'>Dashboard de Gastos Regional - Herson Hernández</h1>
""", unsafe_allow_html=True)

# --- 2. Carga de archivo Excel ---
st.markdown("""
<h3 style='color: #5fc542;'>▶ Sube tu archivo Excel (.xlsx)</h3>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Arrastra o selecciona tu archivo", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    if not {'Categoria', 'Fecha', 'Monto', 'Sucursales', 'Descripcion'}.issubset(df.columns):
        st.error("El archivo debe contener las columnas 'Categoria', 'Fecha', 'Monto', 'Sucursales' y 'Descripcion'.")
    else:
        df['Fecha'] = pd.to_datetime(df['Fecha'])
        df['Mes'] = df['Fecha'].dt.strftime('%B')

        resumen_mes = df.groupby('Mes')['Monto'].sum().reindex(
            ['January', 'February', 'March', 'April', 'May', 'June', 'July',
             'August', 'September', 'October', 'November', 'December']
        )

        def clasificar_riesgo(monto_total):
            if monto_total >= 6000000:
                return "🔴 Crítico"
            elif monto_total >= 3000000:
                return "🟡 Moderado"
            else:
                return "🟢 Bajo"

        df_riesgo = df.copy()
        tabla = pd.pivot_table(df_riesgo, index='Categoria', columns='Mes', values='Monto', aggfunc='sum', fill_value=0)
        tabla['Total'] = tabla.sum(axis=1)
        tabla['Grupo_Riesgo'] = tabla['Total'].apply(clasificar_riesgo)
        orden_riesgo = {'🔴 Crítico': 0, '🟡 Moderado': 1, '🟢 Bajo': 2}
        tabla['Orden'] = tabla['Grupo_Riesgo'].map(orden_riesgo)
        tabla = tabla.sort_values(by='Orden').drop(columns='Orden')
        columnas_ordenadas = ['January', 'February', 'March', 'April', 'Total', 'Grupo_Riesgo']
        tabla = tabla.reset_index()[['Categoria'] + columnas_ordenadas]

        # --- Generar Resumen por Sucursal ---
        resumen_sucursal = df.groupby(['Sucursales', 'Categoria'])['Monto'].agg(['sum', 'count']).reset_index()
        resumen_sucursal.rename(columns={'sum': 'Total_Gasto', 'count': 'Cantidad_Registros'}, inplace=True)
        resumen_sucursal['Total_Sucursal'] = resumen_sucursal.groupby('Sucursales')['Total_Gasto'].transform('sum')
        resumen_sucursal['% Participacion'] = (resumen_sucursal['Total_Gasto'] / resumen_sucursal['Total_Sucursal']) * 100
        resumen_sucursal['% Participacion'] = resumen_sucursal['% Participacion'].round(2)
        resumen_sucursal['Total_Gasto'] = (resumen_sucursal['Total_Gasto'] / 1000).round(0).astype(int)
        resumen_sucursal['Total_Sucursal'] = (resumen_sucursal['Total_Sucursal'] / 1000).round(0).astype(int)

        # --- Auditoría por Sucursal con Revisión ---
        def marcar_revision_experta(desc, riesgo):
            desc = str(desc).lower()
            if riesgo in ['🔴 Crítico', '🟡 Moderado']:
                return '✅ Sí'
            if riesgo == '🟢 Bajo':
                claves = ['efectivo', 'reembolso', 'personal', 'varios', 'sin detalle', 'caja chica', 'gasto menor', 'otros']
                if any(p in desc for p in claves):
                    return '✅ Sí'
            return '❌ No'

        df['Grupo_Riesgo'] = df.groupby('Categoria')['Monto'].transform('sum').apply(clasificar_riesgo)
        df['¿Revisar?'] = df.apply(lambda x: marcar_revision_experta(x['Descripcion'], x['Grupo_Riesgo']), axis=1)
        df['Total_Sucursal'] = df.groupby('Sucursales')['Monto'].transform('sum')
        df['% Participacion'] = round((df['Monto'] / df['Total_Sucursal']) * 100, 2)
        df['Monto'] = (df['Monto'] / 1000).round(0).astype(int)
        df['Total_Sucursal'] = (df['Total_Sucursal'] / 1000).round(0).astype(int)

        columnas_exportar = ['Categoria', 'Sucursales', 'Fecha', 'Descripcion', 'Monto', 'Total_Sucursal', '% Participacion', 'Grupo_Riesgo', '¿Revisar?', 'Observaciones']
        df['Observaciones'] = ''
        auditoria_sucursal = df[columnas_exportar]
        auditoria_sucursal = auditoria_sucursal.sort_values(by='% Participacion', ascending=False)

        # --- Exportación final ---
        st.markdown("### 📤 Descargar Cédula de Trabajo de Auditoría")
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            tabla.to_excel(writer, sheet_name="Resumen por Categoría", startrow=6, index=False)
            resumen_sucursal.to_excel(writer, sheet_name="Resumen por Sucursal", startrow=6, index=False)
            auditoria_sucursal.to_excel(writer, sheet_name="Auditoría por Sucursal", startrow=6, index=False)

            wb = writer.book
            h = wb.add_format({'bold': True, 'font_size': 28, 'font_color': 'red'})
            s = wb.add_format({'font_size': 12})
            l = wb.add_format({'bold': True, 'font_size': 12})
            miles_format = wb.add_format({'num_format': '#,##0'})
            centrado = wb.add_format({'align': 'center'})

            for hoja in ["Resumen por Categoría", "Resumen por Sucursal", "Auditoría por Sucursal"]:
                ws = writer.sheets[hoja]
                ws.write("A1", "Auditoría grupo Farmavalue", h)
                ws.write("A2", "Reporte de gastos del 01 de Enero al 20 de abril del 2025", s)
                ws.write("A3", "Auditor Asignado:", l)
                ws.write("A4", "Fecha de la Auditoría:", l)

            ws_auditoria = writer.sheets['Auditoría por Sucursal']
            colnames = auditoria_sucursal.columns.tolist()
            if 'Monto' in colnames:
                idx = colnames.index('Monto')
                ws_auditoria.set_column(idx, idx, 12, miles_format)
            if 'Total_Sucursal' in colnames:
                idx = colnames.index('Total_Sucursal')
                ws_auditoria.set_column(idx, idx, 12, miles_format)
            if 'Observaciones' in colnames:
                idx = colnames.index('Observaciones')
                ws_auditoria.set_column(idx, idx, 20, centrado)

        output.seek(0)
        b64 = base64.b64encode(output.read()).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="Cedula_de_Trabajo_de_Auditoria.xlsx">📥 Descargar Cédula de Trabajo de Auditoría</a>'
        st.markdown(href, unsafe_allow_html=True)

else:
    st.info("📥 Sube un archivo Excel para comenzar.")
