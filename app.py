import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- TÍTULO PRINCIPAL ---
st.markdown("""
<h1 style='text-align: center; color: white;'>Dashboard de Gastos Regional - Herson Hernández</h1>
""", unsafe_allow_html=True)

# --- CARGA DE ARCHIVO ---
st.markdown("<h3 style='color: #5fc542;'>📂 Sube tu archivo Excel (.xlsx)</h3>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("Arrastra o selecciona tu archivo", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    if 'Descripcion' not in df.columns or 'Fecha' not in df.columns or 'Monto' not in df.columns:
        st.error("El archivo debe contener las columnas: 'Descripcion', 'Fecha' y 'Monto'.")
    else:
        df['Fecha'] = pd.to_datetime(df['Fecha'])
        df['Mes'] = df['Fecha'].dt.strftime('%B')

        # --- BLOQUE 1: GRAFICO DE GASTOS POR MES ---
        resumen_mes = df.groupby('Mes')['Monto'].sum().reindex([
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ])

        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("### 📊 Gasto por Mes")
            fig, ax = plt.subplots(figsize=(6, 4))
            colores = ['#5DADE2', '#85C1E9', '#F5B041', '#F8C471']
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

        # --- BLOQUE 2: MAPA DE RIESGO Y ANÁLISIS POR NIVEL ---
        def clasificar_riesgo(monto_total):
            if monto_total >= 6000000:
                return "🔴 Crítico (≥ $6M)"
            elif monto_total >= 3000000:
                return "🟡 Moderado (≥ $3M)"
            else:
                return "🟢 Bajo (< $3M)"

        df_riesgo = df.copy()
        tabla = pd.pivot_table(df_riesgo, index='Categoria', columns='Mes', values='Monto', aggfunc='sum', fill_value=0)
        tabla['Total'] = tabla.sum(axis=1)
        tabla['Grupo_Riesgo'] = tabla['Total'].apply(clasificar_riesgo)
        tabla = tabla.reset_index()[['Categoria', 'January', 'February', 'March', 'April', 'Total', 'Grupo_Riesgo']]

        st.markdown("---")
        st.markdown("## 🧭 Mapa de riesgo")
        st.markdown("""
        <table style="width:100%; text-align:center">
            <tr>
                <th style="color:white">🔴 Crítico</th>
                <th style="color:white">🟡 Moderado</th>
                <th style="color:white">🟢 Bajo</th>
            </tr>
            <tr>
                <td style="color:white;">≥ 6,000,000.00</td>
                <td style="color:white;">≥ 3,000,000.00 y &lt; 6,000,000.00</td>
                <td style="color:white;">&lt; 3,000,000.00</td>
            </tr>
        </table>
        """, unsafe_allow_html=True)

        st.markdown("## 🔎 Análisis por Nivel de Riesgo")
        riesgo_opcion = st.selectbox("Selecciona un grupo de riesgo:", options=tabla['Grupo_Riesgo'].unique())
        tabla_filtrada = tabla[tabla['Grupo_Riesgo'] == riesgo_opcion]

        st.dataframe(tabla_filtrada[['Categoria', 'January', 'February', 'March', 'April', 'Total']], use_container_width=True)

        st.markdown("### 📌 Total del grupo seleccionado")
        total_riesgo = tabla_filtrada[['January', 'February', 'March', 'April', 'Total']].sum()
        st.dataframe(pd.DataFrame([total_riesgo], index=[f"🔍 Total {riesgo_opcion}"]), use_container_width=True)

else:
    st.info("📥 Sube un archivo Excel para comenzar.")
