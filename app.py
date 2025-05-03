# app.py - MiniApp Auditoría a Gastos por País - Grupo FarmaValue
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
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
        st.markdown("### 🧾 Totales por Mes")
        for mes, valor in resumen_mes.dropna().items():
            st.metric(label=mes, value=f"RD${valor:,.0f}")
        st.markdown("---")
        st.metric(label="Gran Total", value=f"RD${resumen_mes.sum():,.0f}")

    # --- BLOQUE 3: DESCARGA DEL ARCHIVO FINAL ---
    st.markdown("### 📥 Descargar Reporte de Auditoría Consolidado")

    try:
        with open("Cedula_de_Trabajo_de_Auditoria_FINAL.xlsx", "rb") as f:
            bytes_data = f.read()
            b64 = base64.b64encode(bytes_data).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="Cedula_de_Trabajo_de_Auditoria_FINAL.xlsx">📄 Descargar Cédula de Trabajo de Auditoría</a>'
            st.markdown(href, unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("❌ El archivo final de auditoría no se encuentra en la ruta especificada. Asegúrate de subir o generar el archivo correctamente.")
else:
    st.info("🔄 Esperando que subas un archivo para procesar.")
