# app.py - MiniApp Versión 2 - Dashboard de Gastos
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

    if 'Descripcion' not in df.columns or 'Fecha' not in df.columns or 'Monto' not in df.columns:
        st.error("El archivo debe contener las columnas 'Descripcion', 'Fecha' y 'Monto'.")
    else:
        df['Fecha'] = pd.to_datetime(df['Fecha'])
        df['Mes'] = df['Fecha'].dt.strftime('%B')

        # --- 3. BLOQUE: Gráfico de gastos por mes ---
        resumen_mes = df.groupby('Mes')['Monto'].sum().reindex(
            ['January', 'February', 'March', 'April', 'May', 'June', 'July',
             'August', 'September', 'October', 'November', 'December']
        )

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("### 📊 Gasto por Mes")
            fig, ax = plt.subplots(figsize=(6, 4))
            colores = ['#5DADE2', '#AED6F1', '#F5B041', '#F8C471']
            resumen_mes.dropna().plot(kind='bar', ax=ax, color=colores)
            ax.set_xlabel("Mes")
            ax.set_ylabel("")
            ax.set_title("Gastos por mes periodo 2025")
            ax.set_xticklabels(resumen_mes.dropna().index, rotation=45)
            ax.get_yaxis().set_visible(False)
            st.pyplot(fig)

        with col2:
            st.markdown("### 💵 Totales por Mes")
            for mes, valor in resumen_mes.dropna().items():
                st.metric(label=mes, value=f"{valor:,.0f}")
            st.divider()
            st.metric(label="Total", value=f"{resumen_mes.sum():,.0f}")

        # --- 4. BLOQUE: Mapa visual de riesgo ---
        st.markdown("""
        <style>
            .risk-table {
                border-collapse: collapse;
                margin: auto;
                font-size: 16px;
                text-align: center;
            }
            .risk-table th {
                background-color: #f0f0f0;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 18px;
            }
            .risk-table td {
                padding: 10px 20px;
                font-weight: bold;
                color: white;
            }
            .critico { background-color: #d32f2f; border-radius: 10px; }
            .moderado { background-color: #fbc02d; color: black; border-radius: 10px; }
            .bajo { background-color: #388e3c; border-radius: 10px; }
        </style>

        <h3 style='text-align: center;'>🧭 Mapa de Riesgo por Categoría</h3>

        <table class="risk-table">
            <tr>
                <th>Crítico</th>
                <th>Moderado</th>
                <th>Bajo</th>
            </tr>
            <tr>
                <td class="critico">≥ 6,000,000.00</td>
                <td class="moderado">≥ 3,000,000.00 y &lt; 6,000,000.00</td>
                <td class="bajo">&lt; 3,000,000.00</td>
            </tr>
        </table>
        """, unsafe_allow_html=True)

        # --- 5. BLOQUE: Análisis por grupo de riesgo ---
        st.markdown("## 🔍 Análisis por Nivel de Riesgo")

        def clasificar_riesgo(monto_total):
            if monto_total >= 6000000:
                return "🔴 Crítico (≥ $6M)"
            elif monto_total >= 3000000:
                return "🟡 Moderado (≥ $3M y < $6M)"
            else:
                return "🟢 Bajo (< $3M)"

        df_riesgo = df.copy()
        tabla = pd.pivot_table(df_riesgo, index='Descripcion', columns='Mes', values='Monto', aggfunc='sum', fill_value=0)
        tabla['Total'] = tabla.sum(axis=1)
        tabla['Grupo_Riesgo'] = tabla['Total'].apply(clasificar_riesgo)
        columnas_ordenadas = ['January', 'February', 'March', 'April', 'Total', 'Grupo_Riesgo']
        tabla = tabla.reset_index()[['Descripcion'] + columnas_ordenadas]

        riesgo_opcion = st.selectbox("Selecciona un grupo de riesgo:", options=tabla['Grupo_Riesgo'].unique())

        tabla_filtrada = tabla[tabla['Grupo_Riesgo'] == riesgo_opcion]
        st.dataframe(tabla_filtrada[['Descripcion', 'January', 'February', 'March', 'April', 'Total']], use_container_width=True)

else:
    st.info("📥 Sube un archivo Excel para comenzar.")
