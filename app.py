import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- Título ---
st.markdown("""
<h1 style='text-align: center; color: white;'>Dashboard de Gastos Regional - Herson Hernández</h1>
""", unsafe_allow_html=True)

# --- Carga del archivo Excel ---
st.markdown("""
<h3 style="color: #f5c542;">📂 Sube tu archivo Excel (.xlsx)</h3>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Arrastra o selecciona tu archivo", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Validar si existen columnas clave
    if 'Mes' in df.columns and 'Monto' in df.columns:

        # Agrupamos por Mes
        resumen = df.groupby('Mes')['Monto'].sum().reset_index()

        # Ordenamos manualmente
        orden_meses = ["January", "February", "March", "April", "May", "June", "July",
                       "August", "September", "October", "November", "December"]
        resumen['Mes'] = pd.Categorical(resumen['Mes'], categories=orden_meses, ordered=True)
        resumen = resumen.sort_values('Mes')

        # Gráfica + Indicadores
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("### 📊 Gasto por Mes - Fase 2")
            fig, ax = plt.subplots(figsize=(6,4))
            ax.bar(resumen['Mes'], resumen['Monto'], color=['#3498db', '#e67e22', '#2ecc71', '#9b59b6'])
            ax.set_xlabel("Mes")
            ax.set_ylabel("Monto (DOP)")
            ax.set_title("Gastos por Mes (Fase 2)")
            plt.xticks(rotation=45)
            st.pyplot(fig)

        with col2:
            st.markdown("### 📋 Totales por Mes")
            for index, row in resumen.iterrows():
                st.metric(label=f"{row['Mes']}", value=f"{row['Monto']:,.2f}")
            st.divider()
            st.metric(label="Gran Total", value=f"{resumen['Monto'].sum():,.2f}")

    else:
        st.error("❌ El archivo no contiene la columna 'Mes' o 'Monto'.")
else:
    st.info("📥 Sube un archivo Excel para comenzar.")
