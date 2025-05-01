import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- Título principal ---
st.markdown("""
<h1 style='text-align: center; color: white;'>Dashboard de Gastos República Dominicana - Creado por Herson Stan</h1>
""", unsafe_allow_html=True)

# --- Carga del archivo ---
st.markdown("""
<h3 style='color: #f5c542;'>📂 Sube tu archivo Excel (.xlsx)</h3>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Arrastra o selecciona tu archivo", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    if 'Mes' in df.columns and 'Monto' in df.columns:

        resumen = df.groupby('Mes')['Monto'].sum().reset_index()

        # Orden manual de los meses
        orden_meses = ["January", "February", "March", "April", "May", "June", "July",
                       "August", "September", "October", "November", "December"]
        resumen['Mes'] = pd.Categorical(resumen['Mes'], categories=orden_meses, ordered=True)
        resumen = resumen.sort_values('Mes')

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("### 📊 Gasto por mes periodo 2025")
            colores = ['#4E79A7', '#A0CBE8', '#F28E2B', '#FFBE7D', '#59A14F', '#8CD17D',
                       '#B6992D', '#F1CE63', '#499894', '#86BCB6', '#E15759', '#FF9D9A']
            fig, ax = plt.subplots(figsize=(6,4))
            ax.bar(resumen['Mes'], resumen['Monto'], color=colores[:len(resumen)])
            ax.set_xlabel("Mes")
            ax.set_yticks([])  # Elimina los valores del eje Y
            ax.set_title("Gastos por mes periodo 2025")
            ax.tick_params(axis='x', rotation=45)
            st.pyplot(fig)

        with col2:
            st.markdown("### 📋 Gasto Mensual")
            for index, row in resumen.iterrows():
                st.metric(label=row['Mes'], value=f"{row['Monto']:,.0f}")
            st.divider()
            st.metric(label="✅ Total", value=f"{resumen['Monto'].sum():,.0f}")

    else:
        st.error("❌ El archivo no contiene las columnas 'Mes' y 'Monto'.")
else:
    st.info("📥 Sube un archivo Excel para comenzar.")
