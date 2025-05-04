# app.py - Version_80_App_Auditoria_Gastos_FarmaValue
import streamlit as st
import pandas as pd
import base64
from io import BytesIO

# --- TÍTULO PRINCIPAL ---
st.markdown("""
<h1 style='text-align: center; color: white;'>Auditoría a Gastos por País - Grupo FarmaValue_Herson Hernández</h1>
""", unsafe_allow_html=True)

# --- BLOQUE 1: CARGA DE ARCHIVO ---
st.markdown("### ▶️ Sube tu archivo Excel (.xlsx)")
archivo = st.file_uploader("Selecciona tu archivo de gastos", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df['Mes'] = df['Fecha'].dt.strftime('%B')

    resumen_mes = df.groupby('Mes')['Monto'].sum().reindex([
        'January', 'February', 'March', 'April'
    ])

    # --- BLOQUE 2: VISUALIZACIÓN GRAFICA Y METRICAS ---
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 📊 Gasto por Mes")
        colores = ['#3498db', '#f39c12', '#2ecc71', '#9b59b6']
        fig = pd.DataFrame({'Mes': resumen_mes.index, 'Monto': resumen_mes.values})
        st.bar_chart(fig.set_index('Mes'))

    with col2:
        st.markdown("### 🧼 Totales por Mes")
        for mes, valor in resumen_mes.dropna().items():
            st.metric(label=mes, value=f"RD${valor:,.0f}")
        st.markdown("---")
        st.metric(label="Gran Total", value=f"RD${resumen_mes.sum():,.0f}")

    # --- BLOQUE 3: TABLA DE UMBRALES ---
    st.markdown("---")
    st.markdown("## 🛑 Tabla de Umbrales de Riesgo")
    st.markdown("""
    <table style='width:100%; text-align:center;'>
        <tr>
            <th>🔴 Crítico</th><th>🟡 Moderado</th><th>🔵 Bajo</th>
        </tr>
        <tr>
            <td>≥ RD$6,000,000</td><td>≥ RD$3,000,000 y < RD$6,000,000</td><td>< RD$3,000,000</td>
        </tr>
    </table>
    """, unsafe_allow_html=True)

    # --- BLOQUE 4: FILTRO POR RIESGO ---
    def clasificar_riesgo(monto_total):
        if monto_total >= 6000000:
            return "🔴 Crítico"
        elif monto_total >= 3000000:
            return "🟡 Moderado"
        else:
            return "🔵 Bajo"

    tabla = df.copy()
    tabla['Grupo_Riesgo'] = tabla.groupby('Categoria')['Monto'].transform('sum').apply(clasificar_riesgo)

    resumen = pd.pivot_table(tabla, index=['Categoria', 'Grupo_Riesgo'], columns='Mes', values='Monto', aggfunc='sum', fill_value=0)
    resumen['Total'] = resumen.sum(axis=1)
    resumen = resumen.reset_index()

    st.markdown("## 🔍 Análisis por Nivel de Riesgo")
    opciones = ['Ver Todos'] + sorted(resumen['Grupo_Riesgo'].unique())
    riesgo_opcion = st.selectbox("Selecciona un grupo de riesgo:", options=opciones)

    if riesgo_opcion == 'Ver Todos':
        tabla_filtrada = resumen
    else:
        tabla_filtrada = resumen[resumen['Grupo_Riesgo'] == riesgo_opcion]

    columnas_monetarias = ['January', 'February', 'March', 'April', 'Total']
    for col in columnas_monetarias:
        if col in tabla_filtrada.columns:
            tabla_filtrada[col] = tabla_filtrada[col].apply(lambda x: f"RD${x:,.2f}")

    st.dataframe(tabla_filtrada[['Categoria', 'Grupo_Riesgo'] + columnas_monetarias], use_container_width=True)

    # --- BLOQUE 5: DESCARGA DEL EXCEL FINAL ---
    st.markdown("---")
    st.markdown("## 📂 Descargar Reporte Consolidado Final")
    try:
        with open("Cedula_de_Trabajo_de_Auditoria_FINAL.xlsx", "rb") as f:
            bytes_data = f.read()
            b64 = base64.b64encode(bytes_data).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="Cedula_de_Trabajo_de_Auditoria_FINAL.xlsx">📄 Descargar Cédula de Trabajo de Auditoría (Versión 80%)</a>'
            st.markdown(href, unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("❌ El archivo 'Cedula_de_Trabajo_de_Auditoria_FINAL.xlsx' no fue encontrado. Asegúrate de subirlo al entorno del proyecto.")
else:
    st.info("📄 Sube un archivo Excel para comenzar.")
