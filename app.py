import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Título principal
st.markdown("""
<h1 style='text-align: center; color: white;'>Dashboard de Gastos Regional - Herson Hernández</h1>
""", unsafe_allow_html=True)

# Carga del archivo
st.markdown("### 📁 Sube tu archivo Excel")
uploaded_file = st.file_uploader("Selecciona tu archivo", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    if 'Categoria' not in df.columns or 'Fecha' not in df.columns or 'Monto' not in df.columns:
        st.error("El archivo debe contener las columnas 'Categoria', 'Fecha' y 'Monto'.")
    else:
        df['Fecha'] = pd.to_datetime(df['Fecha'])
        df['Nombre_Mes'] = df['Fecha'].dt.strftime('%B')

        # Umbrales de riesgo actualizados
        def clasificar_riesgo(monto_total):
            if monto_total >= 6000000:
                return "🔴 Crítico (≥ $6,000,000.00)"
            elif monto_total >= 3000000:
                return "🟡 Moderado (≥ $3,000,000.00 y < $6,000,000.00)"
            else:
                return "🟢 Bajo (< $3,000,000.00)"

        # Bloque visual: Mapa de riesgo
        st.markdown("## 🗺️ Mapa de Riesgo (Umbrales)")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**Crítico**")
            st.markdown("<div style='background-color:#ff4d4d;padding:10px;border-radius:5px;text-align:center;'>≥ 6,000,000.00</div>", unsafe_allow_html=True)
        with col2:
            st.markdown("**Moderado**")
            st.markdown("<div style='background-color:#ffe066;padding:10px;border-radius:5px;text-align:center;'>≥ 3,000,000.00 y < 6,000,000.00</div>", unsafe_allow_html=True)
        with col3:
            st.markdown("**Bajo**")
            st.markdown("<div style='background-color:#28a745;padding:10px;border-radius:5px;text-align:center;'> < 3,000,000.00</div>", unsafe_allow_html=True)

        # Pivot y cálculo de riesgo
        tabla = pd.pivot_table(df, index='Categoria', columns='Nombre_Mes', values='Monto', aggfunc='sum', fill_value=0)
        tabla['Total'] = tabla.sum(axis=1)
        tabla['Nivel_Riesgo'] = tabla['Total'].apply(clasificar_riesgo)
        columnas_orden = ['January', 'February', 'March', 'April']
        columnas_validas = [col for col in columnas_orden if col in tabla.columns]
        tabla = tabla.reset_index()[['Categoria'] + columnas_validas + ['Total', 'Nivel_Riesgo']]

        # Filtro visual
        st.markdown("## 🔍 Análisis por Nivel de Riesgo")
        riesgo_opcion = st.selectbox("Selecciona un grupo de riesgo:", options=tabla['Nivel_Riesgo'].unique())
        filtrado = tabla[tabla['Nivel_Riesgo'] == riesgo_opcion]

        # Mostrar tabla
        st.dataframe(filtrado[['Categoria'] + columnas_validas + ['Total']], use_container_width=True)

else:
    st.warning("Por favor, sube un archivo para continuar.")
