import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Título Principal
st.markdown("""
<h1 style='text-align: center; color: white;'>Dashboard de Gastos Regional - Herson Hernández</h1>
""", unsafe_allow_html=True)

# Sección de carga de archivo
st.markdown("""
<h3 style="color: #f5c542;">📂 Sube tu archivo Excel (.xlsx)</h3>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Arrastra o selecciona tu archivo", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Validar si existe la columna 'Nombre_Mes'
    if 'Mes' in df.columns and 'Monto' in df.columns:

        # Agrupamos por Mes
        resumen = df.groupby('Mes')['Monto'].sum().reset_index()

        # Ordenamos los meses de forma manual
        orden_meses = ["January", "February", "March", "April", "May", "June", "July",
                       "August", "September", "October", "November", "December"]
        resumen['Mes'] = pd.Categorical(resumen['Mes'], categories=orden_meses, ordered=True)
        resumen = resumen.sort_values('Mes')

        # Paleta de colores armoniosa
        colores = ['#4C72B0', '#55A868', '#C44E52', '#8172B3', '#CCB974', '#64B5CD']

        # Gráfica y Totales
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("### 📊 Gasto por Mes")
            fig, ax = plt.subplots(figsize=(6, 4))
            barras = ax.bar(resumen['Mes'], resumen['Monto'], color=colores[:len(resumen)])
            ax.set_xlabel("Mes")
            ax.set_yticks([])  # Eliminar los números del eje Y
            ax.set_ylabel("")
            ax.set_title("Gastos por mes periodo 2025")

            # Mostrar valores sobre cada barra
            for barra in barras:
                yval = barra.get_height()
                ax.text(barra.get_x() + barra.get_width()/2, yval + max(resumen['Monto']) * 0.01,
                        f"{yval:,.2f}", ha='center', va='bottom', fontsize=8, weight='bold')

            st.pyplot(fig)

        with col2:
            st.markdown("### 📋 Totales por Mes")
            for index, row in resumen.iterrows():
                st.metric(label=f"{row['Mes']}", value=f"{row['Monto']:,.0f}")
            st.divider()
            total_gasto = resumen['Monto'].sum()
            st.metric(label="Total", value=f"{total_gasto:,.0f}")

    else:
        st.error("❌ El archivo no contiene la columna 'Mes' o 'Monto'.")
else:
    st.info("📥 Sube un archivo Excel para comenzar.")
