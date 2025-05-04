# app.py - Auditoría a Gastos Grupo FarmaValue
import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="Auditoría a Gastos - Grupo FarmaValue", layout="wide")

# Título principal
st.markdown("<h1 style='text-align: center;'>Auditoría a Gastos por País - Grupo FarmaValue_Herson Hernández</h1>", unsafe_allow_html=True)

# Subir archivo base
st.subheader("📥 Sube tu archivo Excel base")
archivo_excel = st.file_uploader("Selecciona el archivo de gastos", type=["xlsx"])

if archivo_excel:
    df = pd.read_excel(archivo_excel)

    # Preparación de columnas
    df.columns = df.columns.str.strip()
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    df["Mes"] = df["Fecha"].dt.month
    df["Nombre_Mes"] = df["Fecha"].dt.strftime('%B')

    # Mapeo personalizado de meses
    meses_ordenados = ['Enero', 'Febrero', 'Marzo', 'Abril']
    df["Nombre_Mes"] = pd.Categorical(df["Nombre_Mes"], categories=meses_ordenados, ordered=True)

    # Gasto total por sucursal
    total_por_sucursal = df.groupby("Sucursales")["Monto"].sum().reset_index()
    total_por_sucursal = total_por_sucursal.rename(columns={"Monto": "Gasto Total de la Sucursal"})
    df = df.merge(total_por_sucursal, on="Sucursales", how="left")

    # Cálculo de participación
    df["% Participación"] = (df["Monto"] / df["Gasto Total de la Sucursal"]) * 100

    # Clasificación de riesgo
    def clasificar_riesgo(monto):
        if monto >= 6000000:
            return "Crítico"
        elif monto >= 3000000:
            return "Moderado"
        else:
            return "Bajo"
    df["Grupo de Riesgo"] = df["Monto"].apply(clasificar_riesgo)

    # Evaluación de revisión
    df["¿Revisar?"] = np.where(
        (df["Monto"] >= 6000000) |
        (df["% Participación"] > 25) |
        (df["Descripcion"].str.contains("bebida|snack|comida|almuerzo|cena|combustible|refrescos", case=False, na=False)),
        "Sí", "No"
    )

    # ---------------- HOJA 1: RESUMEN POR CATEGORÍA ----------------
    resumen = df.groupby(["Categoria", "Grupo de Riesgo", "Nombre_Mes"])["Monto"].sum().unstack(fill_value=0)
    resumen = resumen[meses_ordenados]
    resumen["Total general"] = resumen.sum(axis=1)
    resumen = resumen.reset_index()
    resumen.insert(0, "No", range(1, len(resumen) + 1))
    resumen[meses_ordenados + ["Total general"]] = resumen[meses_ordenados + ["Total general"]].applymap(lambda x: round(x / 1000, 2))
    resumen = resumen.rename(columns={"Categoria": "Categoría"})
    resumen = resumen[["No", "Categoría", "Grupo de Riesgo"] + meses_ordenados + ["Total general"]]
    total_row = ["", "TOTAL", ""] + [resumen[col].sum() if col != "Grupo de Riesgo" else "" for col in resumen.columns[3:]]
    resumen.loc[len(resumen)] = total_row

    # ---------------- HOJA 2: CRITERIOS AUDITOR ----------------
    criterios = pd.DataFrame({
        "Criterio": [
            "Monto mayor o igual a RD$6,000,000",
            "Participación mayor al 25% del total de la sucursal",
            "Gasto sospechoso por concepto (snack, comida, bebida, combustible, etc.)"
        ],
        "Descripción": [
            "Clasificado como riesgo crítico automáticamente",
            "Gastos relevantes por su peso porcentual en el total de sucursal",
            "Gastos hormiga o posibles usos indebidos"
        ]
    })

    # ---------------- HOJA 3: CÉDULA AUDITOR ----------------
    df["Monto del Gasto"] = df["Monto"].round(2)
    df["Gasto Total de la Sucursal"] = df["Gasto Total de la Sucursal"].round(2)
    df["% Participación"] = df["% Participación"].round(2)
    df["Verificado (☐)"] = ""
    df["No Verificado (☐)"] = ""
    df["Comentario del Auditor"] = ""

    cedula = df[[
        "Sucursales", "Grupo de Riesgo", "Categoria", "Descripcion", "Fecha", "Monto del Gasto",
        "Gasto Total de la Sucursal", "% Participación", "¿Revisar?",
        "Verificado (☐)", "No Verificado (☐)", "Comentario del Auditor"
    ]].rename(columns={
        "Sucursales": "Sucursal",
        "Categoria": "Categoría",
        "Descripcion": "Descripción"
    })

    cedula = cedula.sort_values(by=["Sucursal", "% Participación"], ascending=[True, False])

    # ---------------- EXPORTACIÓN A EXCEL ----------------
    def generar_excel():
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            resumen.to_excel(writer, sheet_name="Resumen por Categoría", index=False)
            criterios.to_excel(writer, sheet_name="Criterios de Revisión Auditor", index=False)
            cedula.to_excel(writer, sheet_name="Cédula Auditor", index=False)

            workbook = writer.book
            header_format = workbook.add_format({'bold': True, 'font_color': 'red', 'font_size': 28})
            subtitle_format = workbook.add_format({'font_size': 12})

            for hoja in ["Resumen por Categoría", "Criterios de Revisión Auditor", "Cédula Auditor"]:
                worksheet = writer.sheets[hoja]
                worksheet.insert_textbox('A1', 'Auditoría grupo Farmavalue', {
                    'font': 'Calibri', 'font_size': 28, 'color': 'red', 'bold': True, 'x_offset': 0, 'y_offset': 0})
                worksheet.write("A3", "Reporte de gastos del 01 de Enero al 20 de abril del 2025", subtitle_format)
                worksheet.write("A4", "Auditor Asignado:", subtitle_format)
                worksheet.write("A5", "Fecha de la Auditoría", subtitle_format)

        output.seek(0)
        return output

    # ---------------- BOTÓN DE DESCARGA ----------------
    st.subheader("📤 Descargar Cédula de Trabajo de Auditoría")
    st.download_button(
        label="📁 Descargar Excel Consolidado",
        data=generar_excel(),
        file_name="Cedula_de_Trabajo_de_Auditoria_FINAL.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
