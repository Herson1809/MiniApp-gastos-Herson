# app.py - MiniApp Versión 2 con Encabezado y Exportación por Riesgo
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import xlsxwriter

# --- Título Principal ---
st.markdown("""
<h1 style='text-align: center; color: white;'>Dashboard de Gastos Regional - Herson Hernández</h1>
""", unsafe_allow_html=True)

# --- Carga del archivo Excel ---
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

        # --- BLOQUE: Gasto mensual ---
        resumen_mes = df.groupby('Mes')['Monto'].sum().reindex(
            ['January', 'February', 'March', 'April', 'May', 'June',
             'July', 'August', 'September', 'October', 'November', 'December']
        )

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
            st.markdown("### 📋 Totales por Mes")
            for mes, valor in resumen_mes.dropna().items():
                st.metric(label=mes, value=f"RD${valor:,.0f}")
            st.divider()
            st.metric(label="Gran Total", value=f"RD${resumen_mes.sum():,.0f}")

        # --- Clasificación de Riesgo ---
        def clasificar_riesgo(monto):
            if monto >= 6000000:
                return "🔴 Crítico"
            elif monto >= 3000000:
                return "🟡 Moderado"
            else:
                return "🟢 Bajo"

        df_riesgo = df.copy()
        tabla = pd.pivot_table(df_riesgo, index='Categoria', columns='Mes',
                               values='Monto', aggfunc='sum', fill_value=0)
        tabla['Total'] = tabla.sum(axis=1)
        tabla['Grupo_Riesgo'] = tabla['Total'].apply(clasificar_riesgo)
        orden_riesgo = {'🔴 Crítico': 0, '🟡 Moderado': 1, '🟢 Bajo': 2}
        tabla['Orden'] = tabla['Grupo_Riesgo'].map(orden_riesgo)
        tabla = tabla.sort_values(by='Orden').drop(columns='Orden')
        columnas_finales = ['Categoria', 'Grupo_Riesgo', 'January', 'February', 'March', 'April', 'Total']
        tabla = tabla.reset_index()[columnas_finales]

        # --- Análisis Interactivo por Riesgo ---
        st.markdown("## 🔍 Análisis por Nivel de Riesgo")
        opciones = ['Ver Todos'] + sorted(tabla['Grupo_Riesgo'].unique())
        riesgo_opcion = st.selectbox("Selecciona un grupo de riesgo:", options=opciones)

        if riesgo_opcion == 'Ver Todos':
            tabla_filtrada = tabla
        else:
            tabla_filtrada = tabla[tabla['Grupo_Riesgo'] == riesgo_opcion]

        tabla_mostrar = tabla_filtrada.copy()
        columnas_monetarias = ['January', 'February', 'March', 'April', 'Total']
        for col in columnas_monetarias:
            tabla_mostrar[col] = tabla_mostrar[col].apply(lambda x: f"RD${x:,.0f}")

        st.dataframe(tabla_mostrar, use_container_width=True)

        # --- Exportar a Excel con Encabezado Institucional ---
        st.markdown("### 📥 Descargar Análisis en Excel por Nivel de Riesgo")
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            tabla_filtrada.to_excel(writer, sheet_name="Riesgo", startrow=5, index=False)
            workbook = writer.book
            worksheet = writer.sheets["Riesgo"]

            # Estilos
            rojo = workbook.add_format({'bg_color': '#FF9999'})
            amarillo = workbook.add_format({'bg_color': '#FFFACD'})
            verde = workbook.add_format({'bg_color': '#C6EFCE'})
            grande_rojo = workbook.add_format({'font_size': 28, 'bold': True, 'font_color': 'red'})
            mediano = workbook.add_format({'font_size': 12, 'bold': False, 'font_color': 'black'})

            # Encabezado
            worksheet.merge_range("A1:G1", "Auditoría grupo Farmavalue", grande_rojo)
            worksheet.merge_range("A2:G2", "Reporte de gastos del 01 de Enero al 20 de abril del 2025", mediano)
            worksheet.write("A3", "Auditor Asignado:", mediano)
            worksheet.write("A4", "Fecha de la Auditoría", mediano)

            for row_num, riesgo in enumerate(tabla_filtrada['Grupo_Riesgo'], start=6):
                col = tabla_filtrada.columns.get_loc('Grupo_Riesgo')
                if 'Crítico' in riesgo:
                    worksheet.write(row_num, col, riesgo, rojo)
                elif 'Moderado' in riesgo:
                    worksheet.write(row_num, col, riesgo, amarillo)
                elif 'Bajo' in riesgo:
                    worksheet.write(row_num, col, riesgo, verde)

        output.seek(0)
        b64 = base64.b64encode(output.read()).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="Riesgo_Categorias.xlsx">📤 Descargar Excel con Riesgos</a>'
        st.markdown(href, unsafe_allow_html=True)

else:
    st.info("📥 Sube un archivo Excel para comenzar.")
