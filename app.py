# app.py - MiniApp Versión 2 - Dashboard de Gastos por Nivel de Riesgo
import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(layout="wide")
st.markdown("""
<h1 style='text-align: center; color: white;'>Dashboard de Gastos República Dominicana - Creado por Herson Stan</h1>
""", unsafe_allow_html=True)

# --- Carga del archivo Excel ---
st.markdown("### 📂 Sube tu archivo Excel (.xlsx)")
uploaded_file = st.file_uploader("Arrastra o selecciona tu archivo", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Verificar columnas requeridas
    df.columns = [col.strip() for col in df.columns]
    columnas_requeridas = ['Categoria', 'January', 'February', 'March', 'April']
    if not all(col in df.columns for col in columnas_requeridas):
        st.error("❌ El archivo no contiene las columnas requeridas: 'Categoria', 'January', 'February', 'March', 'April'")
    else:
        # --- Clasificación por riesgo ---
        df_pivot = df.groupby('Categoria')[['January', 'February', 'March', 'April']].sum()
        df_pivot['Total'] = df_pivot.sum(axis=1)

        def clasificar_riesgo(monto):
            if monto >= 6000000:
                return "🔴 Crítico (≥ $6,000,000.00)"
            elif monto >= 3000000:
                return "🟡 Moderado (≥ $3,000,000.00 y < $6,000,000.00)"
            else:
                return "🟢 Bajo (< $3,000,000.00)"

        df_pivot['Nivel de Riesgo'] = df_pivot['Total'].apply(clasificar_riesgo)
        df_pivot = df_pivot.reset_index()

        # --- Mapa visual de referencia de umbrales ---
        st.markdown("## 🗺️ Mapa de riesgo")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("### 🔴 Crítico")
            st.markdown("**≥ 6,000,000.00**")
        with col2:
            st.markdown("### 🟡 Moderado")
            st.markdown("**≥ 3,000,000.00 y < 6,000,000.00**")
        with col3:
            st.markdown("### 🟢 Bajo")
            st.markdown("**< 3,000,000.00**")

        st.divider()

        # --- Filtro por grupo de riesgo ---
        st.markdown("## 🔎 Análisis por Nivel de Riesgo")
        seleccion = st.selectbox("Selecciona un grupo de riesgo:", df_pivot['Nivel de Riesgo'].unique())

        df_filtrado = df_pivot[df_pivot['Nivel de Riesgo'] == seleccion]
        st.dataframe(df_filtrado[['Categoria', 'January', 'February', 'March', 'April', 'Total']], use_container_width=True)

else:
    st.info("📥 Por favor, sube tu archivo Excel para comenzar.")
