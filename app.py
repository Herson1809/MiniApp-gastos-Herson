# app.py - MiniApp Final con descarga de Cédula de Auditoría
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

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("### 📊 Gasto por Mes")
            fig, ax = plt.subplots(figsize=(6, 4))
            colores = ['#3498db', '#f39c12', '#2ecc71', '#9b59b6']
            resumen_mes.dropna().plot(kind='bar', ax=ax, color=colores[:len(resumen_mes.dropna())])
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

        # BLOQUE 2: Tabla de Umbrales de Riesgo y Análisis por Nivel de Riesgo
        st.markdown("---")
        st.markdown("## 🛆 Tabla de Umbrales de Riesgo")
        st.markdown("""
        <table style='width:100%; text-align:center;'>
          <tr>
            <th style='color:red;'>🔴 Crítico</th>
            <th style='color:orange;'>🟡 Moderado</th>
            <th style='color:green;'>🟢 Bajo</th>
          </tr>
          <tr>
            <td>≥ RD$6,000,000</td>
            <td>≥ RD$3,000,000 y &lt; RD$6,000,000</td>
            <td>&lt; RD$3,000,000</td>
          </tr>
        </table>
        """, unsafe_allow_html=True)

        def clasificar_riesgo(monto):
            if monto >= 6000000:
                return '🔴 Crítico'
            elif monto >= 3000000:
                return '🟡 Moderado'
            else:
                return '🟢 Bajo'

        tabla = df.groupby('Categoria')['Monto'].sum().reset_index()
        tabla['Grupo_Riesgo'] = tabla['Monto'].apply(clasificar_riesgo)

        for mes in ['January', 'February', 'March', 'April']:
            df_mes = df[df['Mes'] == mes]
            tabla_mes = df_mes.groupby('Categoria')['Monto'].sum()
            tabla[mes] = tabla['Categoria'].map(tabla_mes).fillna(0)

        tabla['Total'] = tabla[['January', 'February', 'March', 'April']].sum(axis=1)
        orden_riesgo = {'🔴 Crítico': 0, '🟡 Moderado': 1, '🟢 Bajo': 2}
        tabla['Orden'] = tabla['Grupo_Riesgo'].map(orden_riesgo)
        tabla = tabla.sort_values(by=['Orden', 'Total'], ascending=[True, False])

        st.markdown("## 🔍 Análisis por Nivel de Riesgo")
        opciones_riesgo = ['Ver Todos'] + sorted(tabla['Grupo_Riesgo'].unique())
        seleccion = st.selectbox("Selecciona un grupo de riesgo:", opciones_riesgo)

        if seleccion == 'Ver Todos':
            tabla_filtrada = tabla.copy()
        else:
            tabla_filtrada = tabla[tabla['Grupo_Riesgo'] == seleccion].copy()

        columnas_monetarias = ['January', 'February', 'March', 'April', 'Total']
        for col in columnas_monetarias:
            tabla_filtrada[col] = tabla_filtrada[col].apply(lambda x: f"RD${x:,.0f}")

        tabla_final = tabla_filtrada[['Categoria', 'Grupo_Riesgo', 'January', 'February', 'March', 'April', 'Total']]
        st.dataframe(tabla_final, use_container_width=True)

        # BLOQUE 3: Descarga del Reporte Final Consolidado
        st.markdown("---")
        st.markdown("## 📤 Descargar Reporte de Auditoría Consolidado")

        with open("Cedula_de_Trabajo_de_Auditoria_FINAL.xlsx", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="Cedula_de_Trabajo_de_Auditoria_FINAL.xlsx">📄 Descargar Cédula de Trabajo de Auditoría</a>'
            st.markdown(href, unsafe_allow_html=True)

else:
    st.info("📥 Sube un archivo Excel para comenzar.")
