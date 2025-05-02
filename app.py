# app.py - MiniApp Versión 2 - Dashboard de Gastos Regional con Total General
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

    if 'Categoria' not in df.columns or 'Fecha' not in df.columns or 'Monto' not in df.columns:
        st.error("El archivo debe contener las columnas 'Categoria', 'Fecha' y 'Monto'.")
    else:
        df['Fecha'] = pd.to_datetime(df['Fecha'])
        df['Mes'] = df['Fecha'].dt.strftime('%B')

        # --- BLOQUE 1: Gráfico de gastos por mes ---
        resumen_mes = df.groupby('Mes')['Monto'].sum().reindex(
            ['January', 'February', 'March', 'April', 'May', 'June', 'July',
             'August', 'September', 'October', 'November', 'December']
        )

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("### 📊 Gasto por Mes")
            fig, ax = plt.subplots(figsize=(6, 4))
            colores = ['#3498db', '#f39c12', '#2ecc71', '#9b59b6']
            resumen_mes.dropna().plot(kind='bar', ax=ax, color=colores)
            ax.set_xlabel("Mes")
            ax.set_ylabel("Monto")
            ax.set_title("Gasto Mensual")
            ax.set_xticklabels(resumen_mes.dropna().index, rotation=0)
            ax.get_yaxis().set_visible(False)
            st.pyplot(fig)

        with col2:
            st.markdown("### 📋 Totales por Mes")
            for mes, valor in resumen_mes.dropna().items():
                st.metric(label=mes, value=f"{valor:,.0f}")
            st.divider()
            st.metric(label="Gran Total", value=f"{resumen_mes.sum():,.0f}")

        # --- BLOQUE 2: Análisis por Nivel de Riesgo ---
        def clasificar_riesgo(monto_total):
            if monto_total >= 6000000:
                return "🔴 Crítico (≥ $6M)"
            elif monto_total >= 3000000:
                return "🟡 Moderado (≥ $3M y < $6M)"
            else:
                return "🟢 Bajo (< $3M)"

        df_riesgo = df.copy()
        tabla = pd.pivot_table(df_riesgo, index='Categoria', columns='Mes', values='Monto', aggfunc='sum', fill_value=0)
        tabla['Total'] = tabla.sum(axis=1)
        tabla['Grupo_Riesgo'] = tabla['Total'].apply(clasificar_riesgo)
        tabla = tabla.reset_index()

        # --- Fila de Total General ---
        total_general = pd.DataFrame({
            'Categoria': ['TOTAL GENERAL'],
            **{col: [tabla[col].sum()] for col in ['January', 'February', 'March', 'April']},
            'Total': [tabla['Total'].sum()],
            'Grupo_Riesgo': ['★ TODOS LOS GRUPOS']
        })
        tabla = pd.concat([tabla, total_general], ignore_index=True)

        st.markdown("---")
        st.markdown("## 🚦 Tabla de Umbrales de Riesgo")
        st.markdown("""
        <table style='width:100%; text-align:center;'>
          <tr>
            <th>🔴 Crítico</th><th>🟡 Moderado</th><th>🟢 Bajo</th>
          </tr>
          <tr>
            <td>≥ $6,000,000</td><td>≥ $3,000,000 y &lt; $6,000,000</td><td>&lt; $3,000,000</td>
          </tr>
        </table>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("## 🔍 Análisis por Nivel de Riesgo")
        riesgo_opcion = st.selectbox("Selecciona un grupo de riesgo:", options=tabla['Grupo_Riesgo'].unique())

        tabla_filtrada = tabla[tabla['Grupo_Riesgo'] == riesgo_opcion]

        st.dataframe(tabla_filtrada[['Categoria', 'January', 'February', 'March', 'April', 'Total']], use_container_width=True)

        # --- Descarga Excel ---
        if st.button("🗃️ Descargar Excel del Grupo Seleccionado"):
            ruta_salida = "Reporte_Grupo_Riesgo.xlsx"
            with pd.ExcelWriter(ruta_salida, engine="xlsxwriter") as writer:
                tabla_filtrada.to_excel(writer, sheet_name="Grupo Riesgo", index=False)
            with open(ruta_salida, "rb") as file:
                st.download_button(label="🗄️ Descargar archivo", data=file, file_name=ruta_salida)

else:
    st.info("📅 Sube un archivo Excel para comenzar.")
