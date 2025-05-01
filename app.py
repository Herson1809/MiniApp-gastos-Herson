import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Datos
meses = ['January', 'February', 'March', 'April']
montos = [155185039.49, 142557960.86, 139691952.27, 82405901.16]
total = sum(montos)

# Diseño del layout
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("<h1 style='text-align: center; color: white;'>Dashboard Gastos República Dominicana - Creado por Herson Stan</h1>", unsafe_allow_html=True)
    
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(meses, montos, color=['#002147', '#00A859', '#3CB4E5', '#FFA500'])

    # Ocultar ejes innecesarios
    ax.spines[['top', 'right', 'left']].set_visible(False)
    ax.tick_params(left=False, bottom=False)
    ax.set_yticks([])

    # Etiquetas sobre las barras
    for bar, monto in zip(bars, montos):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f"{monto:,.2f}", 
                ha='center', va='bottom', fontsize=9, fontweight='bold')

    ax.set_title("Gastos por mes periodo 2025", fontsize=14, weight='bold')
    st.pyplot(fig)

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"🟦 **January**<br>{montos[0]:,.2f}", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"🟩 **February**<br>{montos[1]:,.2f}", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"🟦 **March**<br>{montos[2]:,.2f}", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"🟧 **April**<br>{montos[3]:,.2f}", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"✅ **Total**<br><strong>{total:,.2f}</strong>", unsafe_allow_html=True)
