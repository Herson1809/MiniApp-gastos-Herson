import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- 1. Título Principal ---
st.markdown("<h1 style='text-align: center; color: white;'>Gastos por mes período 2025</h1>", unsafe_allow_html=True)

# --- 2. Datos Manuales ---
data = {
    'Mes': ['January', 'February', 'March', 'April'],
    'Monto': [155185039.49, 142557960.86, 139691952.27, 82405901.16]
}
df = pd.DataFrame(data)

# --- 3. Colores personalizados por mes ---
colores = ['#002147', '#00B050', '#00B0F0', '#F79646']

# --- 4. Crear gráfica ---
fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(df['Mes'], df['Monto'], color=colores)

# Eliminar eje Y
ax.spines['left'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_visible(False)

# Agregar etiquetas sobre las barras
for bar, valor in zip(bars, df['Monto']):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f'{valor:,.2f}', 
            ha='center', va='bottom', fontsize=10, fontweight='bold')

# --- 5. Mostrar gráfica ---
st.pyplot(fig)

# --- 6. Mostrar valores a la derecha tipo tarjetas ---
st.markdown("<hr>", unsafe_allow_html=True)
for i in range(len(df)):
    st.markdown(
        f"""
        <div style="border: 2px solid #333; padding: 10px; margin-bottom: 5px; background-color: #f5f5f5; text-align: center;">
            <strong style="color: black;">{df['Mes'][i]}</strong><br>
            <span style="color: black;">{df['Monto'][i]:,.2f}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

# Total
total = df['Monto'].sum()
st.markdown(
    f"""
    <div style="background-color: #f5f5f5; padding: 10px; border-top: 3px double black; text-align: center;">
        <strong style="color: black;">Total</strong><br>
        <span style="color: black; font-weight: bold;">{total:,.2f}</span>
    </div>
    """,
    unsafe_allow_html=True
)
