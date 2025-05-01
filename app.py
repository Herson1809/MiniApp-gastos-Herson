import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Título principal
st.markdown("""
<h1 style='text-align: center; color: white;'>Dashboard de Gastos República Dominicana - Creado por Herson Stan</h1>
""", unsafe_allow_html=True)

# Subida de archivo
uploaded_file = st.file_uploader("📂 Sube tu archivo Excel (.xlsx)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    if 'Nombre_Mes' in df.columns and 'Monto' in df.columns:
        resumen = df.groupby('Nombre_Mes')['Monto'].sum().reset_index()

        # Orden de los meses
        orden_meses = ["January", "February", "March", "April", "May", "June", "July",
                       "August", "September", "October", "November", "December"]
        resumen['Nombre_Mes'] = pd.Categorical(resumen['Nombre_Mes'], categories=orden_meses, ordered=True)
        resumen = resumen.sort_values('Nombre_Mes')

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("### 📊 Gastos por mes periodo 2025")
            fig, ax = plt.subplots(figsize=(6, 4))
            colores = ['#1f77b4', '#2ca02c', '#17becf', '#ff7f0e']
            barras = ax.bar(resumen['Nombre_Mes'], resumen['Monto'], color=colores[:len(resumen)])
            for bar, monto in zip(barras, resumen['Monto']):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f'{monto:,.2f}',
                        ha='center', va='bottom', fontsize=8, fontweight='bold')
            ax.set_title("Gastos por mes periodo 2025", fontsize=12, weight='bold')
            ax.set_xlabel("")
            ax.set_ylabel("")
            ax.set_yticks([])  # Eliminar eje Y
            ax.spines['left'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
            st.pyplot(fig)

        with col2:
            st.markdown("### 🧾 Totales por Mes")
            for _, row in resumen.iterrows():
                st.metric(label=f"{row['Nombre_Mes']}", value=f"{row['Monto']:,.0f}")
            st.divider()
            st.metric(label="🟩 Total", value=f"{resumen['Monto'].sum():,.0f}")
    else:
        st.error("❌ El archivo no contiene la columna 'Nombre_Mes' o 'Monto'.")
else:
    st.info("📥 Por favor sube un archivo para iniciar.")
