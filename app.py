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

# Valores alineados a la derecha
espaciado = 7_000_000
for i, (mes, monto) in enumerate(zip(meses, montos)):
    y_pos = barra.get_height() - i * espaciado
    ax.text(4.3, montos[i], f"{mes}: {int(monto):,}", va='center', fontsize=10)

# Total al final
total = sum(montos)
ax.text(4.3, 10_000_000, f"Total:\n{int(total):,}", fontsize=12, fontweight='bold', color='green')

# Ajustar vista
ax.set_xlim(-0.5, 5)
plt.tight_layout()
plt.show()
