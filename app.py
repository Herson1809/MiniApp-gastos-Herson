# app.py - MiniApp Versión 2 - Conectada a la nube y usando base limpia
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- 1. Título Principal ---
st.markdown("""
<h1 style='text-align: center; color: white;'>Dashboard de Gastos Regional - Herson Hernández</h1>
""", unsafe_allow_html=True)

# --- BLOQUE 1. GASTOS POR MES (Resumen Visual con Totales) ---
st.markdown("""
<h3 style='color: #5fc542;'>▶ Gastos por mes del período 2025</h3>
""", unsafe_allow_html=True)

# Datos fijos proporcionados (en pesos dominicanos, sin símbolo)
meses = ['January', 'February', 'March', 'April']
montos = [155185039.49, 142557960.86, 139691952.27, 82405901.16]
total = sum(montos)

# Gráfico de barras
fig, ax = plt.subplots()
colores = ['#001f5b', '#00b24f', '#33b7d8', '#f79646']
ax.bar(meses, montos, color=colores)
ax.set_title("Gastos por mes periodo 2025")
ax.bar_label(ax.containers[0], fmt='%.2f', label_type='edge')
st.pyplot(fig)

# Totales a la derecha
st.markdown("""
<style>
.cuadro-total {
    border: 1px solid black;
    padding: 8px;
    margin-bottom: 5px;
    width: 220px;
    font-weight: bold;
    background-color: #f5f5f5;
}
.cuadro-total-final {
    border: 2px solid black;
    padding: 8px;
    width: 220px;
    font-weight: bold;
    background-color: #e0e0e0;
}
</style>
""", unsafe_allow_html=True)

for mes, monto in zip(meses, montos):
    st.markdown(f"""
    <div class='cuadro-total'>
        {mes}: {monto:,.2f}
    </div>
    """, unsafe_allow_html=True)

st.markdown(f"""
<div class='cuadro-total-final'>
    Total: {total:,.2f}
</div>
""", unsafe_allow_html=True)

# --- Fin del bloque visual de resumen mensual ---
