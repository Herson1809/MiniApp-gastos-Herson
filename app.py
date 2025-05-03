# app.py - MiniApp Auditoría Final COMPLETA (Genera Excel desde DataFrame)
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import xlsxwriter

# --- Título ---
st.markdown("<h1 style='text-align: center; color: white;'>Dashboard de Gastos Regional - Herson Hernández</h1>", unsafe_allow_html=True)

# --- Carga de archivo ---
st.markdown("### ▶ Sube tu archivo Excel (.xlsx)", unsafe_allow_html=True)
uploaded_file = st.file_uploader("Arrastra o selecciona tu archivo", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    if not {'Categoria', 'Fecha', 'Monto', 'Sucursales', 'Descripcion'}.issubset(df.columns):
        st.error("El archivo debe contener: 'Categoria', 'Fecha', 'Monto', 'Sucursales', 'Descripcion'.")
    else:
        df['Fecha'] = pd.to_datetime(df['Fecha'])
        df['Mes'] = df['Fecha'].dt.strftime('%B')
        df['Año'] = df['Fecha'].dt.year

        # --- RESUMEN POR MES ---
        resumen_mes = df.groupby('Mes')['Monto'].sum().reindex(
            ['January', 'February', 'March', 'April', 'May', 'June', 'July',
             'August', 'September', 'October', 'November', 'December'])

        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("### 📊 Gasto por Mes")
            fig, ax = plt.subplots(figsize=(6, 4))
            resumen_mes.dropna().plot(kind='bar', ax=ax)
            ax.set_title("Gasto Mensual")
            ax.set_xlabel("Mes")
            ax.set_ylabel("Monto")
            st.pyplot(fig)

        with col2:
            st.markdown("### 📋 Totales por Mes")
            for mes, valor in resumen_mes.dropna().items():
                st.metric(label=mes, value=f"RD${valor:,.0f}")
            st.divider()
            st.metric(label="Gran Total", value=f"RD${resumen_mes.sum():,.0f}")

        # --- CLASIFICACIÓN DE RIESGO ---
        def clasificar_riesgo(valor):
            if valor >= 6_000_000:
                return "🔴 Crítico"
            elif valor >= 3_000_000:
                return "🟡 Moderado"
            else:
                return "🟢 Bajo"

        df['Grupo_Riesgo'] = df.groupby('Categoria')['Monto'].transform('sum').apply(clasificar_riesgo)

        # --- GENERAR 3 HOJAS FINAL CON ENCABEZADO INSTITUCIONAL ---
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            workbook = writer.book
            encabezado = [
                ["Auditoria grupo Farmavalue"],
                ["Reporte de gastos del 01 de Enero al 20 de abril del 2025"],
                ["Auditor Asignado:"],
                ["Fecha de la Auditoría"]
            ]

            formato_rojo = workbook.add_format({'color': 'red', 'bold': True, 'font_size': 28})
            formato_negro = workbook.add_format({'color': 'black', 'font_size': 12})
            formato_total = workbook.add_format({'bold': True, 'bg_color': '#d9d9d9'})
            formato_miles = workbook.add_format({'num_format': '#,##0', 'align': 'right'})

            # --- HOJA 1: Resumen por Categoría ---
            resumen_cat = df.groupby(['Categoria', 'Grupo_Riesgo'], as_index=False)['Monto'].sum()
            resumen_cat = resumen_cat.sort_values(by='Monto', ascending=False)
            resumen_cat['Monto'] = resumen_cat['Monto'] / 1000  # Miles
            resumen_cat.insert(0, 'N°', range(1, len(resumen_cat) + 1))

            sheet1 = "Resumen por Categoría"
            resumen_cat.to_excel(writer, sheet_name=sheet1, startrow=5, index=False)
            ws1 = writer.sheets[sheet1]
            for i, linea in enumerate(encabezado):
                ws1.write(i, 0, linea[0], formato_rojo if i == 0 else formato_negro)
            ws1.write(len(resumen_cat) + 5, 2, "TOTAL", formato_total)
            ws1.write(len(resumen_cat) + 5, 3, resumen_cat['Monto'].sum(), formato_total)

        # Agregar más hojas si lo deseas: resumen por sucursal, auditoría, etc.

        # --- DESCARGA DEL ARCHIVO FINAL ---
        st.markdown("### 📥 Descargar Cédula de Trabajo de Auditoría")
        buffer.seek(0)
        b64 = base64.b64encode(buffer.read()).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="Cédula de Trabajo de Auditoría.xlsx">📎 Descargar Cédula de Trabajo de Auditoría</a>'
        st.markdown(href, unsafe_allow_html=True)

else:
    st.info("📥 Sube un archivo Excel para comenzar.")
