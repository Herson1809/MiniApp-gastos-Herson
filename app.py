import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# Título Principal
st.markdown("""
<h1 style='text-align: center; color: white;'>Dashboard Gastos República Dominicana - Creado por Herson Stan</h1>
""", unsafe_allow_html=True)

# Carga de archivo
uploaded_file = st.file_uploader("📂 Sube tu archivo Excel (.xlsx)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    if 'Mes' in df.columns and 'Monto' in df.columns:
        resumen = df.groupby('Mes')['Monto'].sum().reset_index()
        orden_meses = ["January", "February", "March", "April", "May", "June", "July",
                       "August", "September", "October", "November", "December"]
        resumen['Mes'] = pd.Categorical(resumen['Mes'], categories=orden_meses, ordered=True)
        resumen = resumen.sort_values('Mes')

        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown("### 📊 Gastos por mes periodo 2025")
            fig, ax = plt.subplots(figsize=(8, 5))
            colors = ['#003f5c', '#2f4b7c', '#665191', '#ffa600']
            ax.bar(resumen['Mes'], resumen['Monto'], color=colors[:len(resumen)])
            ax.set_xticks(range(len(resumen)))
            ax.set_xticklabels(resumen['Mes'], fontsize=10)
            ax.set_yticks([])
            for i, v in enumerate(resumen['Monto']):
                ax.text(i, v + max(resumen['Monto']) * 0.01, f"{v:,.2f}", ha='center', fontweight='bold')
            st.pyplot(fig)

        with col2:
            st.markdown("### 📌 Detalle por mes")
            for _, row in resumen.iterrows():
                st.markdown(f"<div style='padding: 6px 0; font-size:14px;'><b>{row['Mes']}</b><br>{row['Monto']:,.2f}</div>", unsafe_allow_html=True)
            st.divider()
            st.markdown(f"<div style='padding-top: 10px; font-size:15px;'><b style='color:#00cc44;'>Total</b><br><b>{resumen['Monto'].sum():,.2f}</b></div>", unsafe_allow_html=True)

    else:
        st.error("❌ El archivo no contiene las columnas 'Mes' y 'Monto'.")
else:
    st.info("📥 Sube un archivo Excel para comenzar.")
