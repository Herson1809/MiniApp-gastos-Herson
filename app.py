# app.py - Auditoría de Gastos - Grupo FarmaValue

import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import base64

st.set_page_config(page_title="Auditoría - FarmaValue", layout="wide")

st.markdown("<h1 style='text-align: center; color: white;'>Auditoría a Gastos por País - Grupo FarmaValue_Herson Hernández</h1>", unsafe_allow_html=True)

archivo = st.file_uploader("📥 Sube tu archivo Excel base", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    df.columns = df.columns.str.strip()

    df["Fecha"] = pd.to_datetime(df["Fecha"])
    df["Nombre_Mes"] = df["Fecha"].dt.strftime('%B')

    meses_ordenados = ['January', 'February', 'March', 'April']
    df["Nombre_Mes"] = pd.Categorical(df["Nombre_Mes"], categories=meses_ordenados, ordered=True)

    total_sucursal = df.groupby("Sucursales")["Monto"].sum().reset_index()
    total_sucursal = total_sucursal.rename(columns={"Monto": "Gasto Total de la Sucursal"})
    df = df.merge(total_sucursal, on="Sucursales", how="left")
    df["% Participación"] = (df["Monto"] / df["Gasto Total de la Sucursal"]) * 100

    def clasificar_riesgo(monto):
        if monto >= 6000000:
            return "Crítico"
        elif monto >= 3000000:
            return "Moderado"
        else:
            return "Bajo"

    df["Grupo de Riesgo"] = df["Monto"].apply(clasificar_riesgo)

    patrones_sospechosos = r"(varios|misc|sin comprobantes|mescelanea|otros)"
    sospechoso = df["Descripcion"].str.lower().str.contains(patrones_sospechosos, na=False)
    gasto_hormiga = (df["Monto"] < 10000) & (df["Descripcion"].str.len() < 15)
    alto_porcentaje = df["% Participación"] > 25
    monto_elevado = df["Monto"] >= 6000000

    df["¿Revisar?"] = np.where(monto_elevado | alto_porcentaje | sospechoso | gasto_hormiga, "Sí", "No")

    df["Monto del Gasto"] = df["Monto"].round(2)
    df["% Participación"] = df["% Participación"].round(2)
    df["Verificado (☐)"] = ""
    df["No Verificado (☐)"] = ""
    df["Comentario del Auditor"] = ""

    cedula_final = df[[
        "Sucursales", "Grupo de Riesgo", "Categoria", "Descripcion", "Fecha",
        "Monto del Gasto", "Gasto Total de la Sucursal", "% Participación", "¿Revisar?",
        "Verificado (☐)", "No Verificado (☐)", "Comentario del Auditor"
    ]].rename(columns={
        "Sucursales": "Sucursal",
        "Categoria": "Categoría",
        "Descripcion": "Descripción"
    })

    cedula_final = cedula_final.sort_values(by=["Sucursal", "% Participación"], ascending=[True, False])

    resumen = df.groupby(["Categoria", "Grupo de Riesgo", "Nombre_Mes"])["Monto"].sum().unstack(fill_value=0)
    resumen = resumen[meses_ordenados]
    resumen["Total general"] = resumen.sum(axis=1)
    resumen = resumen.reset_index()
    resumen.insert(0, "No", range(1, len(resumen) + 1))
    resumen[meses_ordenados + ["Total general"]] = resumen[meses_ordenados + ["Total general"]].applymap(lambda x: round(x, 2))

    total_row = ["", "TOTAL", ""] + [resumen[col].sum() if col != "Grupo de Riesgo" else "" for col in resumen.columns[3:]]
    resumen.loc[len(resumen)] = total_row

    resumen = resumen.rename(columns={
        "Categoria": "Categoría"
    })

    resumen = resumen[["No", "Categoría", "Grupo de Riesgo"] + meses_ordenados + ["Total general"]]

    def generar_excel():
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            workbook = writer.book

            encabezado_fmt = workbook.add_format({'bold': True, 'font_size': 28, 'font_color': 'red'})
            subtitulo_fmt = workbook.add_format({'font_size': 12})
            miles_fmt = workbook.add_format({'num_format': '#,##0.00'})

            # Hoja 1: Resumen por Categoría
            resumen.to_excel(writer, sheet_name="Resumen por Categoría", startrow=5, index=False)
            ws1 = writer.sheets["Resumen por Categoría"]
            ws1.write("A1", "Auditoría grupo Farmavalue", encabezado_fmt)
            ws1.write("A2", "Reporte de gastos del 01 de Enero al 20 de abril del 2025", subtitulo_fmt)
            ws1.write("A3", "Auditor Asignado:", subtitulo_fmt)
            ws1.write("A4", "Fecha de la Auditoría", subtitulo_fmt)

            for col in range(3, 8):
                ws1.set_column(col, col, 18, miles_fmt)

            # Hoja 2: Cédula Auditoría
            cedula_final.to_excel(writer, sheet_name="Cédula Auditoría", startrow=5, index=False)
            ws2 = writer.sheets["Cédula Auditoría"]
            ws2.write("A1", "Auditoría grupo Farmavalue", encabezado_fmt)
            ws2.write("A2", "Reporte de gastos del 01 de Enero al 20 de abril del 2025", subtitulo_fmt)
            ws2.write("A3", "Auditor Asignado:", subtitulo_fmt)
            ws2.write("A4", "Fecha de la Auditoría", subtitulo_fmt)

            for col in range(5, 8):
                ws2.set_column(col, col, 18, miles_fmt)

        output.seek(0)
        return output

    st.subheader("📤 Descargar Cédula de Trabajo de Auditoría")
    st.download_button(
        label="📁 Descargar Excel Consolidado",
        data=generar_excel(),
        file_name="Cedula_de_Trabajo_de_Auditoria_FINAL.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("📄 Sube un archivo Excel para iniciar.")
