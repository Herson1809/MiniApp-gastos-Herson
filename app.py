# app.py - MiniApp Versión Final con Cédula de Trabajo de Auditoría
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
st.markdown("### ▶️ Sube tu archivo Excel (.xlsx)")
uploaded_file = st.file_uploader("Arrastra o selecciona tu archivo", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    if not {'Categoria', 'Fecha', 'Monto', 'Sucursales', 'Descripcion'}.issubset(df.columns):
        st.error("El archivo debe contener las columnas 'Categoria', 'Fecha', 'Monto', 'Sucursales' y 'Descripcion'.")
    else:
        df['Fecha'] = pd.to_datetime(df['Fecha'])
        df['Mes'] = df['Fecha'].dt.strftime('%B')

        # --- BLOQUE 1: Gráfico y Totales por Mes ---
        resumen_mes = df.groupby('Mes')['Monto'].sum().reindex(
            ['January', 'February', 'March', 'April']
        )

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("### 📊 Gasto por Mes")
            fig, ax = plt.subplots(figsize=(6, 4))
            resumen_mes.dropna().plot(kind='bar', ax=ax, color='#3498db')
            ax.set_xlabel("Mes")
            ax.set_ylabel("Monto")
            ax.set_title("Gasto Mensual")
            ax.ticklabel_format(style='plain', axis='y')  # Sin notación científica
            ax.set_xticklabels(resumen_mes.dropna().index, rotation=90)
            st.pyplot(fig)

        with col2:
            st.markdown("### 📋 Totales por Mes")
            for mes, valor in resumen_mes.dropna().items():
                st.metric(label=mes, value=f"RD${valor:,.0f}")
            st.divider()
            st.metric(label="Gran Total", value=f"RD${resumen_mes.sum():,.0f}")

        # --- BLOQUE 2: Umbrales de Riesgo ---
        st.markdown("---")
        st.markdown("## 🛑 Tabla de Umbrales de Riesgo")
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

        # --- BLOQUE 3: Análisis por Nivel de Riesgo ---
        st.markdown("---")
        st.markdown("## 🔍 Análisis por Nivel de Riesgo")

        def clasificar_riesgo(monto):
            if monto >= 6000000:
                return "🔴 Crítico"
            elif monto >= 3000000:
                return "🟡 Moderado"
            else:
                return "🟢 Bajo"

        tabla_riesgo = df.groupby('Categoria')['Monto'].sum().reset_index()
        tabla_riesgo['Grupo_Riesgo'] = tabla_riesgo['Monto'].apply(clasificar_riesgo)
        tabla_riesgo = tabla_riesgo.sort_values(by='Monto', ascending=False)

        riesgo_opciones = ['Ver Todos'] + sorted(tabla_riesgo['Grupo_Riesgo'].unique())
        seleccion_riesgo = st.selectbox("Selecciona un grupo de riesgo:", options=riesgo_opciones)

        if seleccion_riesgo == 'Ver Todos':
            tabla_filtrada = tabla_riesgo
        else:
            tabla_filtrada = tabla_riesgo[tabla_riesgo['Grupo_Riesgo'] == seleccion_riesgo]

        tabla_filtrada['Monto'] = tabla_filtrada['Monto'].apply(lambda x: f"RD${x:,.0f}")
        st.dataframe(tabla_filtrada[['Categoria', 'Monto', 'Grupo_Riesgo']], use_container_width=True)

        # --- BLOQUE FINAL: Descargar archivo completo ---
        st.markdown("---")
        st.markdown("## 📥 Descargar Cédula de Trabajo de Auditoría")

        # Archivo previamente generado con todas las hojas correctas
        with open("Cedula_de_Trabajo_de_Auditoria.xlsx", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="Cedula_de_Trabajo_de_Auditoria.xlsx">📥 Descargar Cédula de Trabajo de Auditoría</a>'
            st.markdown(href, unsafe_allow_html=True)

else:
    st.info("📁 Sube un archivo Excel para comenzar.")
