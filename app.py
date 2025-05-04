# app.py - MiniApp Auditoría a Gastos por País - Grupo FarmaValue

import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
import xlsxwriter

# --- CONFIGURACIÓN DE LA APP ---
st.set_page_config(page_title="Auditoría de Gastos", layout="wide")
st.markdown("<h1 style='text-align: center;'>Auditoría a Gastos por País - Grupo FarmaValue</h1>", unsafe_allow_html=True)

# --- CARGA DE ARCHIVO ---
st.subheader("📁 Cargar archivo base de gastos")
archivo = st.file_uploader("Selecciona el archivo Excel", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df['Mes'] = df['Fecha'].dt.strftime('%B')

    # --- Orden de meses ---
    orden_meses = ['January', 'February', 'March', 'April']
    df['Mes'] = pd.Categorical(df['Mes'], categories=orden_meses, ordered=True)

    # --- Cálculo de total por categoría y riesgo ---
    resumen = df.groupby(['Categoria', 'Grupo de Riesgo', 'Mes'])['Monto'].sum().unstack(fill_value=0)
    resumen = resumen[orden_meses]
    resumen['Total general'] = resumen.sum(axis=1)
    resumen = resumen.reset_index()
    resumen.insert(0, 'No', range(1, len(resumen) + 1))

    # Formato de miles y 2 decimales
    for col in orden_meses + ['Total general']:
        resumen[col] = (resumen[col] / 1000).round(2)

    # Total general en fila final
    fila_total = ["", "TOTAL", ""] + [resumen[col].sum() if col in resumen.columns[3:] else "" for col in resumen.columns[3:]]
    resumen.loc[len(resumen)] = fila_total

    # --- Generar hoja de Cédula Auditoría ---
    total_sucursal = df.groupby("Sucursales")["Monto"].sum().reset_index()
    total_sucursal.columns = ["Sucursales", "Gasto Total de la Sucursal"]
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

    df["¿Revisar?"] = df.apply(lambda x: "Sí" if (
        x["Monto"] >= 6000000 or
        x["% Participación"] >= 25 or
        pd.notnull(x["Descripcion"]) and any(palabra in x["Descripcion"].lower() for palabra in ['bebida', 'snack', 'comida', 'almuerzo', 'cena', 'combustible', 'refrescos', 'varios', 'misc', 'sin comprobantes'])
    ) else "No", axis=1)

    df["Monto del Gasto"] = df["Monto"].round(2)
    df["Gasto Total de la Sucursal"] = df["Gasto Total de la Sucursal"].round(2)
    df["% Participación"] = df["% Participación"].round(2)
    df["Verificado (☐)"] = ""
    df["No Verificado (☐)"] = ""
    df["Comentario del Auditor"] = ""

    cedula = df[[
        "Sucursales", "Grupo de Riesgo", "Categoria", "Descripcion", "Fecha", "Monto del Gasto",
        "Gasto Total de la Sucursal", "% Participación", "¿Revisar?", "Verificado (☐)", "No Verificado (☐)", "Comentario del Auditor"
    ]].rename(columns={
        "Sucursales": "Sucursal",
        "Categoria": "Categoría",
        "Descripcion": "Descripción"
    })

    cedula = cedula.sort_values(by=["Sucursal", "% Participación"], ascending=[True, False])
    cedula["Fecha"] = cedula["Fecha"].dt.strftime("%d/%m/%Y")

    # --- EXPORTACIÓN ---
    def generar_excel():
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            wb = writer.book

            # Hoja 1: Resumen por Categoría
            resumen.to_excel(writer, sheet_name="Resumen por Categoría", startrow=5, index=False)
            ws1 = writer.sheets["Resumen por Categoría"]
            ws1.write('A1', 'Auditoría grupo Farmavalue', wb.add_format({'bold': True, 'font_size': 28, 'font_color': 'red'}))
            ws1.write('A2', 'Reporte de gastos del 01 de Enero al 20 de abril del 2025', wb.add_format({'font_size': 12}))
            ws1.write('A3', 'Auditor Asignado:', wb.add_format({'font_size': 12}))
            ws1.write('A4', 'Fecha de la Auditoría', wb.add_format({'font_size': 12}))

            # Hoja 2: Cédula Auditoría
            cedula.to_excel(writer, sheet_name="Cédula Auditoría", startrow=5, index=False)
            ws2 = writer.sheets["Cédula Auditoría"]
            ws2.write('A1', 'Auditoría grupo Farmavalue', wb.add_format({'bold': True, 'font_size': 28, 'font_color': 'red'}))
            ws2.write('A2', 'Reporte de gastos del 01 de Enero al 20 de abril del 2025', wb.add_format({'font_size': 12}))
            ws2.write('A3', 'Auditor Asignado:', wb.add_format({'font_size': 12}))
            ws2.write('A4', 'Fecha de la Auditoría', wb.add_format({'font_size': 12}))

        output.seek(0)
        return output

    st.subheader("📤 Descargar reporte de auditoría")
    st.download_button(
        label="📄 Descargar Excel Consolidado",
        data=generar_excel(),
        file_name="Cedula_de_Trabajo_de_Auditoria_FINAL.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
