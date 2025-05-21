import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import xlsxwriter
import re

# --- BLOQUE DE SEGURIDAD ---
st.set_page_config(page_title="Acceso Seguro - FarmaValue", layout="wide")
st.markdown("<h2 style='text-align: center;'>🔐 Acceso a la Auditoría de Gastos</h2>", unsafe_allow_html=True)
password = st.text_input("Ingresa la contraseña para acceder a la aplicación:", type="password")
if password != "Herson2025":
    st.warning("🔒 Acceso restringido. Por favor, ingresa la contraseña correcta.")
    st.stop()

# --- ENCABEZADO DE LA APP ---
st.markdown("<h1 style='text-align: center; color: white;'>Auditoría a Gastos por País - Grupo FarmaValue_Herson Hernández</h1>", unsafe_allow_html=True)
archivo = st.file_uploader("📥 Sube tu archivo Excel", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df['Mes'] = df['Fecha'].dt.strftime('%B').astype(str)
    meses_orden = ['January', 'February', 'March', 'April']
    df['Mes'] = pd.Categorical(df['Mes'], categories=meses_orden, ordered=True)

    resumen_mes = df.groupby('Mes')['Monto'].sum().reindex(meses_orden)
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### 📊 Gasto por Mes")
        fig, ax = plt.subplots()
        colores = ['#3498db', '#f39c12', '#2ecc71', '#9b59b6']
        resumen_mes.plot(kind='bar', ax=ax, color=colores)
        ax.set_title("Gasto Mensual")
        ax.set_ylabel("")
        st.pyplot(fig)

    with col2:
        st.markdown("### 🧾 Totales por Mes")
        for mes, valor in resumen_mes.items():
            st.metric(label=mes, value=f"RD${valor:,.0f}")
        st.markdown("---")
        st.metric(label="Gran Total", value=f"RD${resumen_mes.sum():,.0f}")

    # --- UMBRALES DE RIESGO ---
    st.markdown("---")
    st.markdown("## 🛑 Tabla de Umbrales de Riesgo")
    st.markdown("""
    <table style='width:100%; text-align:center;'>
        <tr><th>🔴 Crítico</th><th>🟡 Moderado</th><th>🟢 Bajo</th></tr>
        <tr><td>≥ RD$1,500,000</td><td>> RD$501,000 y < RD$1,500,000</td><td>< RD$500,000</td></tr>
    </table>
    """, unsafe_allow_html=True)

    def clasificar_riesgo(monto):
        if monto >= 1500000:
            return "🔴 Crítico"
        elif monto > 501000:
            return "🟡 Moderado"
        else:
            return "🟢 Bajo"

    df['Grupo_Riesgo'] = df.groupby('Categoria')['Monto'].transform('sum').apply(clasificar_riesgo)

    resumen = pd.pivot_table(df, index=['Categoria', 'Grupo_Riesgo'], columns='Mes', values='Monto', aggfunc='sum', fill_value=0).reset_index()
    resumen['Total general'] = resumen[meses_orden].sum(axis=1)
    resumen = resumen.sort_values(by='Total general', ascending=False).reset_index(drop=True)
    resumen.insert(0, 'No', resumen.index + 1)
    resumen = resumen[resumen['Total general'] > 0]

    st.markdown("### 🔎 Filtra por Grupo de Riesgo")
    opciones = ['Ver Todos'] + sorted(resumen['Grupo_Riesgo'].dropna().unique())
    seleccion = st.selectbox("Selecciona un grupo de riesgo:", opciones)

    resumen_filtrado = resumen if seleccion == 'Ver Todos' else resumen[resumen['Grupo_Riesgo'] == seleccion]
    total_row = resumen_filtrado[meses_orden + ['Total general']].sum()
    total_row = pd.DataFrame([["", "TOTAL GENERAL", ""] + list(total_row)], columns=resumen_filtrado.columns)
    resumen_final = pd.concat([resumen_filtrado, total_row], ignore_index=True)

    for col in meses_orden + ['Total general']:
        resumen_final[col] = resumen_final[col].apply(lambda x: f"{x:,.2f}" if pd.notna(x) else x)

    st.dataframe(resumen_final[['No', 'Categoria', 'Grupo_Riesgo'] + meses_orden + ['Total general']], use_container_width=True)
else:
    st.info("📥 Por favor, sube un archivo Excel para comenzar.")
