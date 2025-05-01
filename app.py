import matplotlib.pyplot as plt

# Datos
meses = ['January', 'February', 'March', 'April']
montos = [155_185_039.49, 142_557_960.86, 139_691_952.27, 82_405_901.16]
colores = ['#001f3f', '#2ECC40', '#39CCCC', '#FF851B']

# Crear figura y ejes
fig, ax = plt.subplots(figsize=(10, 6))
barras = ax.bar(meses, montos, color=colores)

# Título principal
plt.suptitle("Dashboard Gastos República Dominicana - Creado por Herson Stan", fontsize=16, fontweight='bold')

# Subtítulo
ax.set_title("Gastos por mes periodo 2025", fontsize=13, fontweight='bold')

# Quitar bordes y eje Y
ax.spines[['top', 'right', 'left']].set_visible(False)
ax.tick_params(axis='y', left=False, labelleft=False)

# Etiquetas sobre las barras
for barra, monto in zip(barras, montos):
    ax.text(barra.get_x() + barra.get_width() / 2,
            barra.get_height() + 3_000_000,
            f"{monto:,.2f}",
            ha='center', va='bottom', fontsize=10, fontweight='bold')

# Valores a la derecha alineados visualmente con las barras
alineaciones = [montos[0], montos[1], montos[2], montos[3]]
for i, (mes, monto) in enumerate(zip(meses, montos)):
    ax.text(4.2, alineaciones[i], f"{mes}: {int(monto):,}", va='center', fontsize=10)

# Total alineado al nivel de la barra más baja
total = sum(montos)
ax.text(4.2, 70_000_000, f"Total:\n{int(total):,}", fontsize=12, fontweight='bold', color='green')

# Ajustes finales
ax.set_xlim(-0.5, 5)
plt.tight_layout()
plt.show()

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Datos
meses = ['January', 'February', 'March', 'April']
montos = [155185039.49, 142557960.86, 139691952.27, 82405901.16]
total = sum(montos)

# Layout con proporción ajustada
col1, col2 = st.columns([4, 1])

with col1:
    st.markdown("<h1 style='text-align: center; color: white;'>Dashboard Gastos República Dominicana - Creado por Herson Stan</h1>", unsafe_allow_html=True)
    
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(meses, montos, color=['#002147', '#00A859', '#3CB4E5', '#FFA500'])

    ax.spines[['top', 'right', 'left']].set_visible(False)
    ax.tick_params(left=False, bottom=False)
    ax.set_yticks([])

    for bar, monto in zip(bars, montos):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f"{monto:,.2f}", 
                ha='center', va='bottom', fontsize=9, fontweight='bold')

    ax.set_title("Gastos por mes periodo 2025", fontsize=14, weight='bold')
    st.pyplot(fig)

with col2:
    st.markdown("<br><br><br>", unsafe_allow_html=True)  # alineación con la gráfica
    for mes, monto, color in zip(meses, montos, ['🟦', '🟩', '🟦', '🟧']):
        st.markdown(f"<p style='margin-bottom:-10px'>{color} <strong>{mes}</strong></p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:16px; margin-top:0px; margin-bottom:5px'>{monto:,.0f}</p>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"✅ <strong>Total</strong><br><span style='font-size:18px'><strong>{total:,.0f}</strong></span>", unsafe_allow_html=True)
