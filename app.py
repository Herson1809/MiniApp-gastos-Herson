import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Cargar los datos
df = pd.read_excel('Gastos RD al 20 de abril limpia.xlsx', sheet_name='Base')

# Limpieza básica de datos
df['Fecha'] = pd.to_datetime(df['Fecha'])
df['Mes'] = df['Fecha'].dt.month_name()
df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce')

# 1. Análisis general
total_gastos = df['Monto'].sum()
num_registros = len(df)
promedio_gasto = df['Monto'].mean()
gasto_max = df['Monto'].max()
gasto_min = df['Monto'].min()

# 2. Análisis por categoría
gastos_por_categoria = df.groupby('Categoria')['Monto'].agg(['sum', 'count', 'mean']).sort_values('sum', ascending=False)

# 3. Análisis por sucursal
gastos_por_sucursal = df.groupby('Sucursales')['Monto'].agg(['sum', 'count', 'mean']).sort_values('sum', ascending=False)

# 4. Análisis temporal
gastos_por_dia = df.groupby(df['Fecha'].dt.date)['Monto'].sum()
gastos_por_mes = df.groupby('Mes')['Monto'].sum()

# 5. Top 10 gastos más altos
top_gastos = df.nlargest(10, 'Monto')

# 6. Distribución de montos
plt.figure(figsize=(10, 6))
sns.histplot(df['Monto'], bins=50, kde=True)
plt.title('Distribución de Montos de Gastos')
plt.xlabel('Monto')
plt.ylabel('Frecuencia')
plt.savefig('distribucion_montos.png')
plt.close()

# 7. Gráfico de gastos por categoría
plt.figure(figsize=(12, 8))
gastos_por_categoria['sum'].sort_values().plot(kind='barh')
plt.title('Gastos Totales por Categoría')
plt.xlabel('Monto Total')
plt.ylabel('Categoría')
plt.savefig('gastos_por_categoria.png')
plt.close()

# 8. Gráfico de gastos por sucursal (top 20)
plt.figure(figsize=(12, 8))
gastos_por_sucursal['sum'].nlargest(20).sort_values().plot(kind='barh')
plt.title('Top 20 Sucursales por Gastos Totales')
plt.xlabel('Monto Total')
plt.ylabel('Sucursal')
plt.savefig('gastos_por_sucursal.png')
plt.close()

# 9. Serie temporal de gastos
plt.figure(figsize=(12, 6))
gastos_por_dia.plot()
plt.title('Evolución Diaria de Gastos')
plt.xlabel('Fecha')
plt.ylabel('Monto Total')
plt.savefig('evolucion_gastos.png')
plt.close()

# Generar reporte en HTML
html_report = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Reporte de Gastos RD al 20 de abril</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        h1, h2 {{ color: #2c3e50; }}
        table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        img {{ max-width: 100%; height: auto; display: block; margin: 20px auto; }}
        .summary {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; }}
    </style>
</head>
<body>
    <h1>Reporte de Gastos RD al 20 de abril</h1>
    
    <div class="summary">
        <h2>Resumen General</h2>
        <p><strong>Total de gastos:</strong> RD$ {total_gastos:,.2f}</p>
        <p><strong>Número de registros:</strong> {num_registros:,}</p>
        <p><strong>Gasto promedio:</strong> RD$ {promedio_gasto:,.2f}</p>
        <p><strong>Gasto máximo:</strong> RD$ {gasto_max:,.2f}</p>
        <p><strong>Gasto mínimo:</strong> RD$ {gasto_min:,.2f}</p>
    </div>
    
    <h2>Gastos por Categoría</h2>
    {gastos_por_categoria.to_html()}
    
    <h2>Top 10 Gastos más Altos</h2>
    {top_gastos.to_html()}
    
    <h2>Distribución de Montos</h2>
    <img src="distribucion_montos.png" alt="Distribución de Montos">
    
    <h2>Gastos por Categoría</h2>
    <img src="gastos_por_categoria.png" alt="Gastos por Categoría">
    
    <h2>Top 20 Sucursales por Gastos</h2>
    <img src="gastos_por_sucursal.png" alt="Gastos por Sucursal">
    
    <h2>Evolución Diaria de Gastos</h2>
    <img src="evolucion_gastos.png" alt="Evolución de Gastos">
</body>
</html>
"""

# Guardar el reporte
with open('reporte_gastos.html', 'w', encoding='utf-8') as f:
    f.write(html_report)

print("Reporte generado exitosamente como 'reporte_gastos.html'")
