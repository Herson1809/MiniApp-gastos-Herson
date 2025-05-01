import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Título principal del dashboard
st.markdown("""
<h1 style='text-align: center; color: white;'>Dashboard de Gastos República Dominicana - Creado por Herson Stan</h1>
""", unsafe_allow_html=True)

# Sección de carga de archivo
st.markdown("### 📂 Sube tu archivo Excel (.xlsx)")
uploaded_file = st.file_uploader("Selecciona tu archivo", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    if 'Nombre_Mes' in df.columns and 'Monto' in df.columns:
        resumen = df.groupby('Nombre_Mes')['Monto'].sum().reset_index()

        # Ordenar meses manualmente
        orden_meses = ["January", "February", "March", "April", "May", "June", "July",
                       "August", "September", "October", "November", "December"]
        resumen['Nombre_Mes'] = pd.Categorical(resumen['Nombre_Mes'], categories=orden_meses, ordered=True)
        resumen = resumen.sort_values('Nombre_Mes')

        # Gráfica de barras
        st.markdown("### 📊 Gráfico de Gasto por Mes")
        fig, ax = plt.subplots(figsize=(6, 4))

        colores = ['#6baed6', '#9ecae1', '#c6dbef', '#e6550d']  # Paleta armoniosa
        bars = ax.bar(resumen['Nombre_Mes'], resumen['Monto'], color=colores[:len(resumen)])

        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, yval + max(resumen['Monto']) * 0.01,
                    f'{yval:,.2f}', ha='center', va='bottom', fontsize=8, fontweight='bold')

        ax.set_xticks(range(len(resumen['Nombre_Mes'])))
        ax.set_xticklabels(resumen['Nombre_Mes'], rotation=0)
        ax.set_yticks([])  # Quitar eje Y
        ax.set_ylabel("")  # Quitar etiqueta Y
        ax.set_title("Gastos por mes periodo 2025", fontsize=12, weight='bold')
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)

        st.pyplot(fig)

    else:
        st.error("El archivo no contiene las columnas requeridas: 'Nombre_Mes' y 'Monto'.")
else:
    st.info("📥 Por favor sube un archivo Excel para comenzar.")
