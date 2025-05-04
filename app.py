import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

# Configuración de la página
st.set_page_config(page_title="Auditoría a Gastos - Grupo FarmaValue", layout="wide")

# Título principal
st.markdown("<h1 style='text-align: center;'>Auditoría a Gastos por País - Grupo FarmaValue_Herson Hernández</h1>", unsafe_allow_html=True)

# Carga del archivo
st.subheader("📥 Sube tu archivo Excel base")
archivo = st.file_uploader("Selecciona el archivo de gastos", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    df.columns = df.columns.str.strip()
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    df["Mes"] = df["Fecha"].dt.month
    df["Nombre_Mes"] = df["Fecha"].dt.strftime('%B')
    
    meses_ordenados = ['Enero', 'Febrero', 'Marzo', 'Abril']
    df["Nombre_Mes"] = pd.Categorical(df["Nombre_Mes"], categories=meses_ordenados, ordered=True)

    # Cálculo por sucursal
    total_por_sucursal = df.groupby("Sucursales")["Monto"].sum().reset_index()
    total_por_sucursal.columns = ["Sucursales", "Gasto Total de la Sucursal"]
    df = df.merge(total_por_sucursal, on="Sucursales", how="left")
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

    # Criterio de revisión
    df["¿Revisar?"] = np.where(
        (df["Monto"] >= 6000000) |
        (df["% Participación"] > 25) |
        (df["Descripcion"].str.contains("bebida|snack|comida|almuerzo|cena|combustible|refrescos", case=False, na=False)),
        "Sí", "No"
    )

    # Cédula Auditor
    cedula = df.copy()
    cedula["Monto del Gasto"] = cedula["Monto"].round(2)
    cedula["Gasto Total de la Sucursal"] = cedula["Gasto Total de la Sucursal"].round(2)
    cedula["% Participación"] = cedula["% Participación"].round(2)
    cedula["Verificado (☐)"] = ""
    cedula["No Verificado (☐)"] = ""
    cedula["Comentario del Auditor"] = ""

    cedula_final = cedula[[
        "Sucursales", "Grupo de Riesgo", "Categoria", "Descripcion", "Fecha", "Monto del Gasto",
        "Gasto Total de la Sucursal", "% Participación", "¿Revisar?",
        "Verificado (☐)", "No Verificado (☐)", "Comentario del Auditor"
    ]].rename(columns={
        "Sucursales": "Sucursal", "Categoria": "Categoría", "Descripcion": "Descripción"
    }).sort_values(by=["Sucursal", "% Participación"], ascending=[True, False])

    # Resumen por categoría
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

    # Criterios de revisión
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

    # Exportar Excel
    def generar_excel():
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            resumen.to_excel(writer, sheet_name="Resumen por Categoría", index=False)
            criterios.to_excel(writer, sheet_name="Criterios de Revisión Auditor", index=False)
            cedula_final.to_excel(writer, sheet_name="Cédula Auditor", index=False)

            workbook = writer.book
            format_title = workbook.add_format({'bold': True, 'font_size': 28, 'color': 'red'})
            format_sub = workbook.add_format({'font_size': 12})

            for hoja in ["Resumen por Categoría", "Criterios de Revisión Auditor", "Cédula Auditor"]:
                worksheet = writer.sheets[hoja]
                worksheet.insert_textbox('A1', 'Auditoría grupo Farmavalue', {
                    'font': 'Calibri', 'font_size': 28, 'color': 'red', 'bold': True,
                    'x_offset': 0, 'y_offset': 0
                })
                worksheet.write("A3", "Reporte de gastos del 01 de Enero al 20 de abril del 2025", format_sub)
                worksheet.write("A4", "Auditor Asignado:", format_sub)
                worksheet.write("A5", "Fecha de la Auditoría", format_sub)

        output.seek(0)
        return output

    # Botón de descarga
    st.subheader("📤 Descargar Cédula de Trabajo de Auditoría")
    st.download_button(
        label="📁 Descargar Excel Consolidado",
        data=generar_excel(),
        file_name="Cedula_de_Trabajo_de_Auditoria_FINAL.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
