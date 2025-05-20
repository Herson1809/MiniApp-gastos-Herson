import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import xlsxwriter

# --- BLOQUE DE SEGURIDAD ---
st.set_page_config(page_title="Acceso Seguro - FarmaValue", layout="wide")
st.markdown("<h2 style='text-align: center;'>🔐 Acceso a la Auditoría de Gastos</h2>", unsafe_allow_html=True)
password = st.text_input("Ingresa la contraseña para acceder a la aplicación:", type="password")
if password != "Herson2025":
    st.warning("🔒 Acceso restringido. Por favor, ingresa la contraseña correcta.")
    st.stop()

# --- ENCABEZADO DE LA APP ---
st.markdown("<h1 style='text-align: center; color: white;'>Auditoría a Gastos por País - Grupo FarmaValue_Herson Hernández</h1>", unsafe_allow_html=True)
archivo = st.file_uploader("📅 Sube tu archivo Excel", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df['Mes'] = df['Fecha'].dt.strftime('%B').astype(str)
    meses_orden = ['January', 'February', 'March', 'April']
    df['Mes'] = pd.Categorical(df['Mes'], categories=meses_orden, ordered=True)

    resumen_mes = df.groupby('Mes')['Monto'].sum().reindex(meses_orden)
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### 📊 Gasto por Mes")
        fig, ax = plt.subplots()
        colores = ['#3498db', '#f39c12', '#2ecc71', '#9b59b6']
        resumen_mes.plot(kind='bar', ax=ax, color=colores)
        ax.set_title("Gasto Mensual")
        ax.set_ylabel("")
        st.pyplot(fig)

    with col2:
        st.markdown("### 🧲 Totales por Mes")
        for mes, valor in resumen_mes.items():
            st.metric(label=mes, value=f"RD${valor:,.0f}")
        st.markdown("---")
        st.metric(label="Gran Total", value=f"RD${resumen_mes.sum():,.0f}")

    st.markdown("---")
    st.markdown("## 🛑 Tabla de Umbrales de Riesgo")
    st.markdown("""
    <table style='width:100%; text-align:center;'>
        <tr><th>🔴 Crítico</th><th>🟡 Moderado</th><th>🟢 Bajo</th></tr>
        <tr><td>≥ RD$2,000,000</td><td>≥ RD$1,000,000 y < RD$2,000,000</td><td>< RD$1,000,000</td></tr>
    </table>
    """, unsafe_allow_html=True)

    def clasificar_riesgo(monto):
        if monto >= 2000000:
            return "🔴 Crítico"
        elif monto >= 1000000:
            return "🟡 Moderado"
        else:
            return "🟢 Bajo"

    df['Grupo_Riesgo'] = df.groupby('Categoria')['Monto'].transform('sum').apply(clasificar_riesgo)

    # MARCADORES SOSPECHOSOS
    palabras_sospechosas = ["recuperación", "seguro", "diferencia", "no cobrados", "ajuste", "reclasificación",
                             "ars", "senasa", "mapfre", "afiliado", "asegurado", "cxc"]

    df['Descripcion_Lower'] = df['Descripcion'].astype(str).str.lower()
    df['Sospechosa'] = df['Descripcion_Lower'].apply(lambda x: any(pal in x for pal in palabras_sospechosas))

    # Asegurar que si hay al menos un sospechoso con la misma descripción, se marquen todos
    descripciones_sospechosas = df.loc[df['Sospechosa'], 'Descripcion_Lower'].unique()
    df['Sospechosa'] = df['Descripcion_Lower'].isin(descripciones_sospechosas)

    # Marcar en rojo
    def marcar_rojo(valor, sospechosa):
        if sospechosa:
            return f"<span style='color:red'>{valor}</span>"
        return valor

    df['Descripcion'] = df.apply(lambda row: marcar_rojo(row['Descripcion'], row['Sospechosa']), axis=1)
    df['¿Revisar?'] = df['Sospechosa'].map({True: "Sí", False: "No"})

    # Mostrar ejemplo de tabla
    st.markdown("### 🔎 Resultados con Criterio Seguro (Rojo y Revisar)")
    st.dataframe(df[['Sucursales', 'Categoria', 'Grupo_Riesgo', 'Descripcion', '¿Revisar?']].head(10), use_container_width=True)

    # AQUÍ CONTINUARÍAS CON LOS BLOQUES SIGUIENTES COMO DESCARGA, GRÁFICOS DETALLADOS ETC

else:
    st.info("📅 Por favor, sube un archivo Excel para comenzar.")
