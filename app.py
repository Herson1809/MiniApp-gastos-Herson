# app.py - MiniApp Versión 2 - Conectada a la nube y usando base limpia
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- 1. Título Principal ---
st.markdown("""
<h1 style='text-align: center; color: white;'>Dashboard de Gastos Regional - Herson Hernández</h1>
""", unsafe_allow_html=True)

# --- 2. Carga de archivo Excel ---
st.markdown("""
<h3 style='color: #5fc542;'>▶ Sube tu archivo Excel (.xlsx)</h3>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Arrastra o selecciona tu archivo", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # --- 3. Validación de columna Descripcion ---
    if 'Descripcion' not in df.columns:
        st.error("La columna 'Descripcion' no está en el archivo.")
    else:
        df['Fecha'] = pd.to_datetime(df['Fecha'])
        df['Mes'] = pd.to_datetime(df['Fecha']).dt.strftime('%B')

        # --- 4. Gráfico por mes ---
        resumen_mes = df.groupby('Mes')['Monto'].sum().reindex(
            ['January', 'February', 'March', 'April', 'May', 'June', 'July',
             'August', 'September', 'October', 'November', 'December']
        )
        st.bar_chart(resumen_mes.fillna(0))

        # --- 5. Selector por categoría (Descripcion) ---
        categoria = st.selectbox("Selecciona una categoría:", df['Descripcion'].unique())
        filtro_df = df[df['Descripcion'] == categoria]

        st.metric("Total de la categoría", f"${filtro_df['Monto'].sum():,.2f}")

        # --- 6. Exportación a Excel ---
        if st.button("Exportar reporte de esta categoría"):
            with pd.ExcelWriter("Reporte_Categoria.xlsx", engine="xlsxwriter") as writer:
                df.to_excel(writer, sheet_name="General", index=False)
                filtro_df.to_excel(writer, sheet_name="Detalle", index=False)
                pd.DataFrame({"Checklist": ["Cumple", "No cumple"]}).to_excel(
                    writer, sheet_name="Auditoría", index=False)
            st.success("Archivo generado como Reporte_Categoria.xlsx")

        # --- 7. Mostrar tabla detallada ---
        st.dataframe(filtro_df.sort_values(by='Monto', ascending=False))
