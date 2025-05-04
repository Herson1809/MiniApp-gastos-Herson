import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO

# Configuración de la app
st.set_page_config(page_title="Auditoría a Gastos - Grupo FarmaValue", layout="wide")
st.markdown("<h1 style='text-align: center;'>Auditoría a Gastos por País - Grupo FarmaValue_Herson Hernández</h1>", unsafe_allow_html=True)

# Subir archivo base
st.subheader("\U0001F4E5 Sube tu archivo Excel base")
archivo_excel = st.file_uploader("Selecciona el archivo de gastos", type=["xlsx"])

if archivo_excel:
    df = pd.read_excel(archivo_excel)
    df.columns = df.columns.str.strip()

    df = df[df["Fecha"].notna()]
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    df["Monto"] = pd.to_numeric(df["Monto"], errors='coerce')
    df = df.dropna(subset=["Monto"])

    df["Mes"] = df["Fecha"].dt.month
    df["Nombre_Mes"] = df["Fecha"].dt.strftime('%B')
    meses_ordenados = ['Enero', 'Febrero', 'Marzo', 'Abril']
    df["Nombre_Mes"] = pd.Categorical(df["Nombre_Mes"], categories=meses_ordenados, ordered=True)

    # BLOQUE 1: Gráfico mensual por categoría
    st.subheader("\U0001F4CA Gasto mensual por categoría")
    gasto_mensual = df.groupby("Nombre_Mes")["Monto"].sum().reindex(meses_ordenados).fillna(0)
    fig = px.bar(gasto_mensual.reset_index(), x="Nombre_Mes", y="Monto", text="Monto", labels={"Nombre_Mes": "Mes", "Monto": "Monto en RD$"})
    st.plotly_chart(fig, use_container_width=True)

    # BLOQUE 2: Análisis por nivel de riesgo
    st.subheader("\U0001F7E5\U0001F7E8\U0001F7E9 Análisis por Nivel de Riesgo")

    total_por_sucursal = df.groupby("Sucursales")["Monto"].sum().reset_index().rename(columns={"Monto": "Gasto Total de la Sucursal"})
    df = df.merge(total_por_sucursal, on="Sucursales", how="left")
    df["% Participación"] = (df["Monto"] / df["Gasto Total de la Sucursal"]) * 100

    def clasificar_riesgo(monto):
        if monto >= 6000000:
            return "Crítico"
        elif monto >= 3000000:
            return "Moderado"
        else:
            return "Bajo"

    df["Grupo de Riesgo"] = df["Monto"].apply(clasificar_riesgo)

    filtro_riesgo = st.selectbox("Selecciona el nivel de riesgo:", options=["Crítico", "Moderado", "Bajo"])
    df_filtrado = df[df["Grupo de Riesgo"] == filtro_riesgo].copy()
    df_filtrado["Monto"] = df_filtrado["Monto"].round(0).astype(int)
    df_filtrado["% Participación"] = df_filtrado["% Participación"].round(2)

    df_filtrado = df_filtrado[["Categoria", "Sucursales", "Fecha", "Descripcion", "Monto", "% Participación"]]
    df_filtrado = df_filtrado.rename(columns={"Categoria": "Categoría", "Descripcion": "Descripción"})

    st.dataframe(df_filtrado.reset_index(drop=True), use_container_width=True)

    # BLOQUE 3: Resumen por Categoría (descargable)
    st.subheader("\U0001F4C4 Resumen por Categoría (Descargable)")
    resumen = df.groupby(["Categoria", "Grupo de Riesgo", "Nombre_Mes"])["Monto"].sum().unstack(fill_value=0)
    resumen = resumen[meses_ordenados]
    resumen["Total general"] = resumen.sum(axis=1)
    resumen = resumen.reset_index()
    resumen.insert(0, "No", range(1, len(resumen) + 1))
    resumen[meses_ordenados + ["Total general"]] = resumen[meses_ordenados + ["Total general"]].applymap(lambda x: round(x / 1000, 2))

    resumen = resumen.rename(columns={"Categoria": "Categoría"})
    resumen = resumen[["No", "Categoría", "Grupo de Riesgo"] + meses_ordenados + ["Total general"]]
    total_row = ["", "TOTAL", ""] + [resumen[col].sum() if col not in ["No", "Grupo de Riesgo"] else "" for col in resumen.columns[3:]]
    resumen.loc[len(resumen)] = total_row

    def generar_excel():
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            resumen.to_excel(writer, sheet_name="Resumen por Categoría", index=False)
            workbook = writer.book
            header_format = workbook.add_format({'bold': True, 'font_color': 'red', 'font_size': 28})
            subtitle_format = workbook.add_format({'font_size': 12})
            worksheet = writer.sheets["Resumen por Categoría"]
            worksheet.insert_textbox('A1', 'Auditoría grupo Farmavalue', {'font': 'Calibri', 'font_size': 28, 'color': 'red', 'bold': True, 'x_offset': 0, 'y_offset': 0})
            worksheet.write("A3", "Reporte de gastos del 01 de Enero al 20 de abril del 2025", subtitle_format)
            worksheet.write("A4", "Auditor Asignado:", subtitle_format)
            worksheet.write("A5", "Fecha de la Auditoría", subtitle_format)
        output.seek(0)
        return output

    st.download_button(
        label="\U0001F4BE Descargar Resumen por Categoría",
        data=generar_excel(),
        file_name="Cedula_Resumen_Categoria_FINAL_OK.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
