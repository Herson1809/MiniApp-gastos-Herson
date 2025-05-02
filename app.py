# app.py - MiniApp Versión 2 con Auditoría por Categoría Crítica
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

    if 'Categoria' not in df.columns or 'Fecha' not in df.columns or 'Monto' not in df.columns:
        st.error("El archivo debe contener las columnas 'Categoria', 'Fecha' y 'Monto'.")
    else:
        df['Fecha'] = pd.to_datetime(df['Fecha'])
        df['Mes'] = df['Fecha'].dt.strftime('%B')

        resumen_mes = df.groupby('Mes')['Monto'].sum().reindex(
            ['January', 'February', 'March', 'April', 'May', 'June', 'July',
             'August', 'September', 'October', 'November', 'December']
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

        st.markdown("---")
        st.markdown("## 🛆 Tabla de Umbrales de Riesgo")
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

        st.markdown("---")
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

        st.dataframe(tabla_mostrar[['Categoria'] + columnas_monetarias + ['Grupo_Riesgo']], use_container_width=True)

        st.markdown("### 📄 Descargar Auditoría por Categoría (Excel con colores)")
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            tabla.to_excel(writer, sheet_name='Auditoría Categorías', index=False)
            workbook = writer.book
            worksheet = writer.sheets['Auditoría Categorías']

            rojo = workbook.add_format({'bg_color': '#FF9999'})
            amarillo = workbook.add_format({'bg_color': '#FFEB99'})
            verde = workbook.add_format({'bg_color': '#C6EFCE'})

            for row_num, riesgo in enumerate(tabla['Grupo_Riesgo'], start=1):
                col = tabla.columns.get_loc('Grupo_Riesgo')
                if 'Crítico' in riesgo:
                    worksheet.write(row_num, col, riesgo, rojo)
                elif 'Moderado' in riesgo:
                    worksheet.write(row_num, col, riesgo, amarillo)
                elif 'Bajo' in riesgo:
                    worksheet.write(row_num, col, riesgo, verde)

        output.seek(0)
        b64 = base64.b64encode(output.read()).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="Auditoria_Categorias_Semaforo_Color.xlsx">📥 Descargar Excel con Colores</a>'
        st.markdown(href, unsafe_allow_html=True)

else:
    st.info("📥 Sube un archivo Excel para comenzar.")
