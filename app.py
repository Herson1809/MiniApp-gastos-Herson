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
