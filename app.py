# app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import xlsxwriter

# --- CONFIGURACIÓN DE LA APP ---
st.set_page_config(page_title="Auditoría de Gastos - Grupo FarmaValue", layout="wide")

st.markdown("<h1 style='text-align: center; color: white;'>Auditoría a Gastos por País - Grupo FarmaValue_Herson Hernández</h1>", unsafe_allow_html=True)
st.markdown("### 📅 Sube tu archivo Excel")
archivo = st.file_uploader("Selecciona tu archivo de gastos", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df['Mes'] = df['Fecha'].dt.strftime('%B')
    
    meses_orden = ['January', 'February', 'March', 'April']
    df['Mes'] = pd.Categorical(df['Mes'], categories=meses_orden, ordered=True)

    # --- BLOQUE 1: GRÁFICO Y TOTALES ---
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

    # --- BLOQUE 2: UMBRALES ---
    st.markdown("---")
    st.markdown("## 🛑 Tabla de Umbrales de Riesgo")
    st.markdown("""
    <table style='width:100%; text-align:center;'>
        <tr><th>🔴 Crítico</th><th>🟡 Moderado</th><th>🟢 Bajo</th></tr>
        <tr><td>≥ RD$6,000,000</td><td>≥ RD$3,000,000 y < RD$6,000,000</td><td>< RD$3,000,000</td></tr>
    </table>
    """, unsafe_allow_html=True)

    # --- BLOQUE 3: CLASIFICACIÓN DE RIESGO ---
    def clasificar_riesgo(monto):
        if monto >= 6000000:
            return "🔴 Crítico"
        elif monto >= 3000000:
            return "🟡 Moderado"
        else:
            return "🟢 Bajo"

    suma_categoria = df.groupby('Categoria')['Monto'].sum()
    riesgo_map = suma_categoria.apply(clasificar_riesgo).to_dict()
    df['Grupo_Riesgo'] = df['Categoria'].map(riesgo_map)

    resumen = pd.pivot_table(
        df, index=['Categoria', 'Grupo_Riesgo'], columns='Mes', values='Monto',
        aggfunc='sum', fill_value=0).reset_index()
    resumen['Total general'] = resumen[meses_orden].sum(axis=1)
    resumen = resumen.sort_values(by='Total general', ascending=False).reset_index(drop=True)
    resumen.insert(0, 'No', resumen.index + 1)

    # --- BLOQUE 4: FILTRO POR RIESGO ---
    st.markdown("### 🔎 Filtra por Grupo de Riesgo")
    opciones = ['Ver Todos'] + sorted(resumen['Grupo_Riesgo'].unique())
    seleccion = st.selectbox("Selecciona un grupo de riesgo:", opciones)

    if seleccion != 'Ver Todos':
        resumen_filtrado = resumen[resumen['Grupo_Riesgo'] == seleccion].copy()
    else:
        resumen_filtrado = resumen.copy()

    total_row = resumen_filtrado[meses_orden + ['Total general']].sum()
    total_row = pd.DataFrame([['', 'TOTAL GENERAL', ''] + list(total_row)], columns=resumen_filtrado.columns)

    resumen_final = pd.concat([resumen_filtrado, total_row], ignore_index=True)

    for col in meses_orden + ['Total general']:
        resumen_final[col] = resumen_final[col].apply(lambda x: f"{x:,.2f}" if pd.notna(x) else x)

    st.dataframe(resumen_final[['No', 'Categoria', 'Grupo_Riesgo'] + meses_orden + ['Total general']], use_container_width=True)

else:
    st.info("📅 Por favor, sube un archivo Excel para comenzar.")
