# app.py - MiniApp Versión 2 - Dashboard de Gastos
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- 1. Título Principal ---
st.markdown("""
<h1 style='text-align: center; color: white;'>Dashboard de Gastos Regional - Herson Hernández</h1>
""", unsafe_allow_html=True)

# --- 2. Carga de archivo Excel ---
st.markdown("### 📁 Sube tu archivo Excel")
uploaded_file = st.file_uploader("Selecciona tu archivo", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    if 'Categoria' not in df.columns or 'Fecha' not in df.columns or 'Monto' not in df.columns:
        st.error("El archivo debe contener las columnas 'Categoria', 'Fecha' y 'Monto'.")
    else:
        df['Fecha'] = pd.to_datetime(df['Fecha'])
        df['Nombre_Mes'] = df['Fecha'].dt.strftime('%B')

        # --- 3. BLOQUE: Gráfico de gastos por mes ---
        resumen_mes = df.groupby('Nombre_Mes')['Monto'].sum().reindex(
            ['January', 'February', 'March', 'April']
        )

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("### 📊 Gasto por Mes")
            fig, ax = plt.subplots(figsize=(6, 4))
            colores = ['#5DADE2', '#AED6F1', '#F5B041', '#F8C471']
            resumen_mes.dropna().plot(kind='bar', ax=ax, color=colores)
            ax.set_xlabel("Mes")
            ax.set_title("Gastos por mes periodo 2025")
            ax.set_xticklabels(resumen_mes.dropna().index, rotation=45)
            ax.get_yaxis().set_visible(False)
            st.pyplot(fig)

        with col2:
            st.markdown("### 💵 Totales por Mes")
            for mes, valor in resumen_mes.dropna().items():
                st.metric(label=mes, value=f"{valor:,.0f}")
            st.divider()
            st.metric(label="Total", value=f"{resumen_mes.sum():,.0f}")

        # --- 4. BLOQUE: Mapa visual de umbrales ---
        def clasificar_riesgo(monto_total):
            if monto_total >= 6000000:
                return "🔴 Crítico (≥ $6M)"
            elif monto_total >= 3000000:
                return "🟡 Moderado (≥ $3M y < $6M)"
            else:
                return "🟢 Bajo (< $3M)"

        st.markdown("## 🗺️ Mapa de Riesgo (Umbrales)")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**Crítico**")
            st.markdown("<div style='background-color:#ff4d4d;padding:8px;border-radius:6px;text-align:center;'>≥ 6,000,000.00</div>", unsafe_allow_html=True)
        with col2:
            st.markdown("**Moderado**")
            st.markdown("<div style='background-color:#ffe066;padding:8px;border-radius:6px;text-align:center;'>≥ 3,000,000.00 y < 6,000,000.00</div>", unsafe_allow_html=True)
        with col3:
            st.markdown("**Bajo**")
            st.markdown("<div style='background-color:#28a745;padding:8px;border-radius:6px;text-align:center;'> < 3,000,000.00</div>", unsafe_allow_html=True)

        # --- 5. BLOQUE: Análisis por grupo de riesgo ---
        tabla = pd.pivot_table(df, index='Categoria', columns='Nombre_Mes', values='Monto', aggfunc='sum', fill_value=0)
        tabla['Total'] = tabla.sum(axis=1)
        tabla['Nivel_Riesgo'] = tabla['Total'].apply(clasificar_riesgo)
        columnas_ordenadas = ['January', 'February', 'March', 'April']
        columnas_validas = [col for col in columnas_ordenadas if col in tabla.columns]
        tabla = tabla.reset_index()[['Categoria'] + columnas_validas + ['Total', 'Nivel_Riesgo']]

        st.markdown("## 🔍 Análisis por Nivel de Riesgo")
        riesgo_opcion = st.selectbox("Selecciona un grupo de riesgo:", options=tabla['Nivel_Riesgo'].unique())

        filtrado = tabla[tabla['Nivel_Riesgo'] == riesgo_opcion]
        st.dataframe(filtrado[['Categoria'] + columnas_validas + ['Total']], use_container_width=True)

else:
    st.info("📥 Sube un archivo Excel para comenzar.")
