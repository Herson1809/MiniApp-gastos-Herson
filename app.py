import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import xlsxwriter

# --- Título Principal ---
st.markdown("""
<h1 style='text-align: center; color: white;'>Dashboard de Gastos Regional Grupo FarmaValue - Herson Hernández</h1>
""", unsafe_allow_html=True)

# --- Carga del archivo Excel ---
st.markdown("""
<h3 style='color: #5fc542;'>▶ Sube tu archivo Excel (.xlsx)</h3>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Arrastra o selecciona tu archivo", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    if not {'Categoria', 'Fecha', 'Monto', 'Sucursales', 'Descripcion'}.issubset(df.columns):
        st.error("El archivo debe contener las columnas 'Categoria', 'Fecha', 'Monto', 'Sucursales', 'Descripcion'.")
    else:
        df['Fecha'] = pd.to_datetime(df['Fecha'])
        df['Mes'] = df['Fecha'].dt.strftime('%B')

        def clasificar_riesgo(monto):
            if monto >= 6000000:
                return "🔴 Crítico"
            elif monto >= 3000000:
                return "🟡 Moderado"
            else:
                return "🟢 Bajo"

        df['Grupo_Riesgo'] = df.groupby('Categoria')['Monto'].transform('sum').apply(clasificar_riesgo)

        # --- Tabla de umbrales ---
        st.markdown("## 🛆 Tabla de Umbrales de Riesgo")
        st.markdown("""
        <table style='width:100%; text-align:center;'>
          <tr>
            <th>🔴 Crítico</th><th>🟡 Moderado</th><th>🟢 Bajo</th>
          </tr>
          <tr>
            <td>≥ RD$6,000,000</td><td>≥ RD$3,000,000 y &lt; RD$6,000,000</td><td>&lt; RD$3,000,000</td>
          </tr>
        </table>
        """, unsafe_allow_html=True)

        # --- Resumen por Categoría ---
        resumen_categoria = df.groupby(['Categoria', 'Grupo_Riesgo'])['Monto'].sum().reset_index()
        resumen_categoria['Total (Miles)'] = resumen_categoria['Monto'] / 1000
        resumen_categoria = resumen_categoria.drop(columns=['Monto'])
        resumen_categoria = resumen_categoria.sort_values(by='Total (Miles)', ascending=False)
        resumen_categoria.insert(0, 'No.', range(1, len(resumen_categoria) + 1))

        # --- Resumen por Sucursal ---
        resumen_sucursal = df.groupby(['Sucursales', 'Grupo_Riesgo'])['Monto'].agg(['sum', 'count']).reset_index()
        resumen_sucursal['Total (Miles)'] = resumen_sucursal['sum'] / 1000
        resumen_sucursal = resumen_sucursal.drop(columns=['sum'])
        resumen_sucursal = resumen_sucursal.rename(columns={'count': 'Cantidad'})
        resumen_sucursal = resumen_sucursal.sort_values(by='Total (Miles)', ascending=False)

        # --- Auditoría por Sucursal ---
        def marcar_revision(desc):
            desc = str(desc).lower()
            if len(desc) < 15 or any(x in desc for x in ['varios', 'otros', 'misc']):
                return '✅ Sí'
            return '🔍 No'

        df['¿Revisar?'] = df['Descripcion'].apply(marcar_revision)
        auditoria = df.groupby(['Sucursales', 'Fecha', 'Categoria', 'Grupo_Riesgo', 'Descripcion', '¿Revisar?'])['Monto'].sum().reset_index()
        auditoria['% Participación'] = auditoria.groupby('Sucursales')['Monto'].transform(lambda x: x / x.sum() * 100)
        auditoria['Monto (Miles)'] = auditoria['Monto'] / 1000
        auditoria = auditoria.drop(columns='Monto')
        auditoria = auditoria.sort_values(by='% Participación', ascending=False)

        # --- Descargar Excel con Encabezado Institucional ---
        st.markdown("### 📥 Descargar Cédula de Trabajo de Auditoría")
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            wb_format = lambda wb: {
                'rojo': wb.add_format({'bg_color': '#FF9999'}),
                'amarillo': wb.add_format({'bg_color': '#FFFACD'}),
                'verde': wb.add_format({'bg_color': '#C6EFCE'}),
                'grande_rojo': wb.add_format({'font_size': 28, 'bold': True, 'font_color': 'red'}),
                'mediano': wb.add_format({'font_size': 12, 'bold': False, 'font_color': 'black'}),
                'centrado': wb.add_format({'align': 'center'})
            }

            def escribir_hoja(df, nombre, writer):
                df.to_excel(writer, sheet_name=nombre, startrow=5, index=False)
                wb = writer.book
                ws = writer.sheets[nombre]
                estilos = wb_format(wb)
                ws.merge_range("A1:G1", "Auditoría grupo Farmavalue", estilos['grande_rojo'])
                ws.merge_range("A2:G2", "Reporte de gastos del 01 de Enero al 20 de abril del 2025", estilos['mediano'])
                ws.write("A3", "Auditor Asignado:", estilos['mediano'])
                ws.write("A4", "Fecha de la Auditoría", estilos['mediano'])
                if 'Grupo_Riesgo' in df.columns:
                    for row_num, riesgo in enumerate(df['Grupo_Riesgo'], start=6):
                        col = df.columns.get_loc('Grupo_Riesgo')
                        if 'Crítico' in riesgo:
                            ws.write(row_num, col, riesgo, estilos['rojo'])
                        elif 'Moderado' in riesgo:
                            ws.write(row_num, col, riesgo, estilos['amarillo'])
                        elif 'Bajo' in riesgo:
                            ws.write(row_num, col, riesgo, estilos['verde'])

            escribir_hoja(resumen_categoria, "Resumen por Categoría", writer)
            escribir_hoja(resumen_sucursal, "Resumen por Sucursal", writer)
            escribir_hoja(auditoria, "Auditoría por Sucursal", writer)

        output.seek(0)
        b64 = base64.b64encode(output.read()).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="Cedula_de_Trabajo_Auditoria.xlsx">📤 Descargar Reporte Completo</a>'
        st.markdown(href, unsafe_allow_html=True)

else:
    st.info("📥 Sube un archivo Excel para comenzar.")
