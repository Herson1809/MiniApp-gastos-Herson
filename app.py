# app_version_80_por_ciento.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO
from datetime import datetime

# Configuración inicial
st.set_page_config(page_title="Auditoría a Gastos - Grupo FarmaValue", layout="wide")

# Título principal
st.markdown("<h1 style='text-align: center;'>Auditoría a Gastos por País - Grupo FarmaValue_Herson Hernández</h1>", unsafe_allow_html=True)

# Subir archivo base
st.subheader("📥 Sube tu archivo Excel base")
archivo_excel = st.file_uploader("Selecciona el archivo de gastos", type=["xlsx"])

if archivo_excel:
    df = pd.read_excel(archivo_excel)

    # Procesamiento inicial
    df.columns = df.columns.str.strip()
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    df["Mes"] = df["Fecha"].dt.month
    df["Nombre_Mes"] = df["Fecha"].dt.strftime('%B')
    meses_ordenados = ['Enero', 'Febrero', 'Marzo', 'Abril']
    df["Nombre_Mes"] = pd.Categorical(df["Nombre_Mes"], categories=meses_ordenados, ordered=True)

    # Gráfico mensual
    st.subheader("📊 Gasto mensual por categoría")
    gasto_mensual = df.groupby(["Nombre_Mes"])["Monto"].sum().reindex(meses_ordenados)
    fig = px.bar(gasto_mensual, x=gasto_mensual.index, y=gasto_mensual.values,
                 labels={"x": "Mes", "y": "Monto"}, text_auto=True)
    st.plotly_chart(fig, use_container_width=True)

    # Tabla de umbrales
    st.markdown("## 🛑 Tabla de Umbrales de Riesgo")
    st.markdown("""
    <table style='width:100%; text-align:center;'>
        <tr>
            <th style="color:red;">🔴 Crítico</th><th style="color:orange;">🟡 Moderado</th><th style="color:green;">🟢 Bajo</th>
        </tr>
        <tr>
            <td>≥ RD$6,000,000</td><td>≥ RD$3,000,000 y &lt; RD$6,000,000</td><td>&lt; RD$3,000,000</td>
        </tr>
    </table>
    """, unsafe_allow_html=True)

    # Clasificación de riesgo
    def clasificar_riesgo(monto):
        if monto >= 6000000:
            return "🔴 Crítico"
        elif monto >= 3000000:
            return "🟡 Moderado"
        else:
            return "🟢 Bajo"

    df["Grupo de Riesgo"] = df.groupby("Categoria")["Monto"].transform("sum").apply(clasificar_riesgo)

    # Resumen por categoría
    resumen = df.groupby(["Categoria", "Grupo de Riesgo", "Nombre_Mes"])["Monto"].sum().unstack(fill_value=0)
    resumen = resumen[meses_ordenados]
    resumen["Total general"] = resumen.sum(axis=1)
    resumen = resumen.reset_index()
    resumen.insert(0, "No", range(1, len(resumen) + 1))
    resumen[meses_ordenados + ["Total general"]] = resumen[meses_ordenados + ["Total general"]].applymap(lambda x: round(x / 1000, 2))

    resumen = resumen.rename(columns={"Categoria": "Categoría"})

    # Agregar total general
    total_row = ["", "TOTAL", ""] + [resumen[col].sum() if col != "Grupo de Riesgo" else "" for col in resumen.columns[3:]]
    resumen.loc[len(resumen)] = total_row

    # Filtro por nivel de riesgo
    st.markdown("## 🔍 Análisis por Nivel de Riesgo")
    opciones = ['Ver Todos'] + sorted(resumen["Grupo de Riesgo"].dropna().unique())
    seleccion = st.selectbox("Selecciona un nivel de riesgo:", opciones)

    if seleccion == 'Ver Todos':
        st.dataframe(resumen, use_container_width=True)
    else:
        st.dataframe(resumen[resumen["Grupo de Riesgo"] == seleccion], use_container_width=True)
