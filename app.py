# app.py - MiniApp Auditoría a Gastos por País - Grupo FarmaValue (Versión 80%)
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# --- TÍTULO PRINCIPAL ---
st.markdown("""
<h1 style='text-align: center; color: white;'>Auditoría a Gastos por País - Grupo FarmaValue_Herson Hernández</h1>
""", unsafe_allow_html=True)

# --- CARGA DE ARCHIVO ---
st.markdown("### ▶️ Sube tu archivo Excel (.xlsx)")
archivo = st.file_uploader("Selecciona tu archivo de gastos", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df['Mes'] = df['Fecha'].dt.strftime('%B')

    resumen_mes = df.groupby('Mes')['Monto'].sum().reindex(['January', 'February', 'March', 'April'])

    # --- BLOQUE 1: GRAFICA DE GASTOS POR MES ---
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### 📊 Gasto por Mes")
        fig, ax = plt.subplots(figsize=(6, 4))
        colores = ['#3498db', '#f39c12', '#2ecc71', '#9b59b6']
        resumen_mes.dropna().plot(kind='bar', ax=ax, color=colores)
        ax.set_xlabel("Mes")
        ax.set_ylabel("Monto")
        ax.set_title("Gasto Mensual")
        ax.set_xticklabels(resumen_mes.dropna().index, rotation=0)
        ax.get_yaxis().set_visible(False)
        st.pyplot(fig)

    with col2:
        st.markdown("### 📋 Totales por Mes")
        for mes, valor in resumen_mes.dropna().items():
            st.metric(label=mes, value=f"RD${valor:,.0f}")
        st.markdown("---")
        st.metric(label="Gran Total", value=f"RD${resumen_mes.sum():,.0f}")

    # --- BLOQUE 2: TABLA DE UMBRALES Y FILTRO ---
    st.markdown("## 🛑 Tabla de Umbrales de Riesgo")
    st.markdown("""
    <table style='width:100%; text-align:center;'>
        <tr>
            <th>🔴 Crítico</th><th>🟡 Moderado</th><th>🟢 Bajo</th>
        </tr>
        <tr>
            <td>≥ RD$6,000,000</td><td>≥ RD$3,000,000 y < RD$6,000,000</td><td>< RD$3,000,000</td>
        </tr>
    </table>
    """, unsafe_allow_html=True)

    def clasificar_riesgo(monto_total):
        if monto_total >= 6000000:
            return "🔴 Crítico"
        elif monto_total >= 3000000:
            return "🟡 Moderado"
        else:
            return "🟢 Bajo"

    tabla = df.copy()
    tabla['Grupo_Riesgo'] = tabla.groupby('Categoria')['Monto'].transform('sum').apply(clasificar_riesgo)

    resumen = pd.pivot_table(tabla, index=['Categoria', 'Grupo_Riesgo'], columns='Mes', values='Monto', aggfunc='sum', fill_value=0)
    resumen['Total general'] = resumen.sum(axis=1)
    resumen = resumen.reset_index().sort_values(by='Total general', ascending=False).reset_index(drop=True)
    resumen.index += 1
    resumen = resumen.rename_axis('No').reset_index()

    # Filtro por grupo de riesgo
    st.markdown("## 🔍 Análisis por Nivel de Riesgo")
    opciones = ['Ver Todos'] + sorted(resumen['Grupo_Riesgo'].unique())
    filtro = st.selectbox("Selecciona un grupo de riesgo:", options=opciones)
    if filtro != 'Ver Todos':
        resumen = resumen[resumen['Grupo_Riesgo'] == filtro]

    columnas_monetarias = ['January', 'February', 'March', 'April', 'Total general']
    for col in columnas_monetarias:
        resumen[col] = resumen[col].apply(lambda x: f"{x/1000:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    st.dataframe(resumen[['No', 'Categoria', 'Grupo_Riesgo'] + columnas_monetarias], use_container_width=True)

    # --- BLOQUE FINAL: DESCARGAR REPORTE ---
    st.markdown("## 📤 Descargar Cédula de Trabajo de Auditoría")

    try:
        with open("Cedula_de_Trabajo_de_Auditoria_FINAL.xlsx", "rb") as f:
            bytes_data = f.read()
            b64 = base64.b64encode(bytes_data).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="Cedula_de_Trabajo_de_Auditoria_FINAL.xlsx">📄 Descargar Reporte Completo</a>'
            st.markdown(href, unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("❌ El archivo 'Cedula_de_Trabajo_de_Auditoria_FINAL.xlsx' no fue encontrado en el entorno del proyecto.")

else:
    st.info("📥 Sube un archivo Excel para comenzar.")
