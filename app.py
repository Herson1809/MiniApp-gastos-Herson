import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Título principal
st.markdown("""
<h1 style='text-align: center; color: white;'>Dashboard de Gastos Regional - Herson Hernández</h1>
""", unsafe_allow_html=True)

# Carga de archivo
st.markdown("### 📂 Sube tu archivo Excel (.xlsx)")
uploaded_file = st.file_uploader("Arrastra o selecciona tu archivo", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    if 'Mes' in df.columns and 'Monto' in df.columns:
        # Agrupar por Mes
        resumen = df.groupby('Mes')['Monto'].sum().reset_index()

        # Ordenar manualmente los meses
        orden_meses = ["January", "February", "March", "April", "May", "June", 
                       "July", "August", "September", "October", "November", "December"]
        resumen['Mes'] = pd.Categorical(resumen['Mes'], categories=orden_meses, ordered=True)
        resumen = resumen.sort_values('Mes')

        # Columnas para gráfico y métricas
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("### 📊 Gasto por Mes")
            fig, ax = plt.subplots(figsize=(6, 4))
            colores = ['#4E79A7', '#A0CBE8', '#F28E2B', '#FFBE7D', '#59A14F',
                       '#8CD17D', '#B6992D', '#F1CE63', '#499894', '#86BCB6',
                       '#E15759', '#FF9D9A']
            ax.bar(resumen['Mes'], resumen['Monto'], color=colores[:len(resumen)])
            ax.set_xlabel("Mes")
            ax.set_ylabel("")  # No mostrar etiqueta de eje Y
            ax.set_yticks([])  # Quitar valores del eje Y
            ax.set_title("Gastos por mes periodo 2025")
            plt.xticks(rotation=45)
            st.pyplot(fig)

        with col2:
            st.markdown("### 💵 Totales por Mes")
            for index, row in resumen.iterrows():
                st.metric(label=f"{row['Mes']}", value=f"{row['Monto']:,.0f}")
            st.markdown("---")
            total = resumen['Monto'].sum()
            st.metric(label="Total", value=f"{total:,.0f}")
    else:
        st.error("❌ El archivo no contiene las columnas requeridas: 'Mes' y 'Monto'.")
else:
    st.info("📥 Sube un archivo Excel para comenzar.")
