# app.py - MiniApp Versión 2 - Mapa de Riesgo con Totales por Grupo
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

    if 'Descripcion' not in df.columns or 'Fecha' not in df.columns or 'Monto' not in df.columns or 'Categoria' not in df.columns:
        st.error("El archivo debe contener las columnas 'Descripcion', 'Fecha', 'Monto' y 'Categoria'.")
    else:
        df['Fecha'] = pd.to_datetime(df['Fecha'])
        df['Mes'] = df['Fecha'].dt.strftime('%B')

        # --- BLOQUE: Clasificación de riesgo por total por categoría ---
        def clasificar_riesgo(monto):
            if monto >= 6000000:
                return "🔴 Crítico"
            elif monto >= 3000000:
                return "🟡 Moderado"
            else:
                return "🟢 Bajo"

        # Calcular pivot por categoría y mes
        tabla = pd.pivot_table(df, index='Categoria', columns='Mes', values='Monto', aggfunc='sum', fill_value=0)
        tabla['Total'] = tabla.sum(axis=1)
        tabla['Nivel_Riesgo'] = tabla['Total'].apply(clasificar_riesgo)
        tabla = tabla.reset_index()

        # --- BLOQUE: Encabezado visual del mapa de riesgos ---
        st.markdown("""
        <h3 style='color:white;'>🧭 Mapa de Riesgos por Categoría</h3>
        <table style='width:100%; border-collapse: collapse;'>
            <tr style='text-align:center;'>
                <th style='padding:10px; background-color:#f8d7da;'>🔴 Crítico</th>
                <th style='padding:10px; background-color:#fff3cd;'>🟡 Moderado</th>
                <th style='padding:10px; background-color:#d4edda;'>🟢 Bajo</th>
            </tr>
            <tr style='text-align:center;'>
                <td style='padding:10px;'>Total &ge; 6,000,000</td>
                <td style='padding:10px;'>Total &ge; 3,000,000 y &lt; 6,000,000</td>
                <td style='padding:10px;'>Total &lt; 3,000,000</td>
            </tr>
        </table>
        <br>
        """, unsafe_allow_html=True)

        # --- BLOQUE: Selector interactivo ---
        grupo = st.selectbox("Selecciona un grupo de riesgo:", tabla['Nivel_Riesgo'].unique())
        filtrado = tabla[tabla['Nivel_Riesgo'] == grupo].copy()

        # --- BLOQUE: Agregar fila de total ---
        total_row = pd.DataFrame(filtrado.drop(columns=['Categoria', 'Nivel_Riesgo']).sum()).T
        total_row['Categoria'] = '🔢 Total general'
        total_row['Nivel_Riesgo'] = ''
        final = pd.concat([filtrado, total_row], ignore_index=True)

        # Mostrar tabla final
        st.dataframe(final[['Categoria', 'January', 'February', 'March', 'April', 'Total']], use_container_width=True)

else:
    st.info("📥 Sube un archivo Excel para comenzar.")
