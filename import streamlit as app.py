import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Título Principal
st.markdown("""
<h1 style='text-align: center; color: white;'>Dashboard de Gastos Regional - Herson Hernández</h1>
""", unsafe_allow_html=True)

# Sección de carga de archivo
st.markdown("""
<h3 style="color: #f5c542;">📂 Sube tu archivo Excel (.xlsx)</h3>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Arrastra o selecciona tu archivo", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Validar si existe la columna 'Nombre_Mes'
    if 'Nombre_Mes' in df.columns and 'Monto' in df.columns:

        # Agrupamos por Nombre_Mes
        resumen = df.groupby('Nombre_Mes')['Monto'].sum().reset_index()

        # Ordenamos los meses de forma manual
        orden_meses = ["January", "February", "March", "April", "May", "June", "July",
                       "August", "September", "October", "November", "December"]
        resumen['Nombre_Mes'] = pd.Categorical(resumen['Nombre_Mes'], categories=orden_meses, ordered=True)
        resumen = resumen.sort_values('Nombre_Mes')

        # Gráfica y Totales
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("### 📊 Gráfico de Gasto por Mes")
            fig, ax = plt.subplots(figsize=(6,4))
            ax.bar(resumen['Nombre_Mes'], resumen['Monto'], color=['#3498db', '#e67e22', '#2ecc71', '#9b59b6', '#f1c40f'])
            ax.set_xlabel("Mes")
            ax.set_ylabel("Monto ($)")
            ax.set_title("Gasto por Mes")
            plt.xticks(rotation=45)
            st.pyplot(fig)

        with col2:
            st.markdown("### 📋 Indicadores de Gasto Mensual")
            for index, row in resumen.iterrows():
                st.metric(label=f"Mes: {row['Nombre_Mes']}", value=f"${row['Monto']:,.2f}")
            
            # Total general
            st.divider()
            total_gasto = resumen['Monto'].sum()
            st.metric(label="Gran Total", value=f"${total_gasto:,.2f}")

    else:
        st.error("❌ El archivo no contiene la columna 'Nombre_Mes' o 'Monto'.")
else:
    st.info("📥 Sube un archivo Excel para comenzar.")

# AUDITORÍA POR SUCURSAL
st.markdown("---")
st.markdown("## 📍 Auditoría Financiera por Sucursal")

# Crear DataFrame de auditoría por sucursal
auditoria_sucursal = pd.DataFrame([
    {"Sucursal": "FD00 Bodega", "Mes": "January", "Categoría": "Sin comprobantes", "Monto": 1500000, "Riesgo": "Alto", "Comentario": "No hay soporte documental."},
    {"Sucursal": "FD01 Sucursal", "Mes": "February", "Categoría": "Servicios Profesionales", "Monto": 750000, "Riesgo": "Medio", "Comentario": "Montos elevados respecto promedio."},
    {"Sucursal": "FD03 Otro", "Mes": "March", "Categoría": "Viáticos y Gastos Menores", "Monto": 300000, "Riesgo": "Bajo", "Comentario": "No usual en esta sucursal."}
])

# Mostrar auditoría por sucursal en formato horizontal
cols = st.columns(3)  # 3 tarjetas por fila
for idx, row in auditoria_sucursal.iterrows():
    with cols[idx % 3]:
        st.markdown(f"""
        <div style="background-color:#1e1e1e; padding:15px; border-radius:10px; margin-bottom:20px;">
            <h4 style="color:#ff5c5c;">📍 {row['Sucursal']}</h4>
            <p><b>📅 Mes:</b> {row['Mes']}</p>
            <p><b>📂 Categoría:</b> {row['Categoría']}</p>
            <p><b>💵 Monto:</b> ${row['Monto']:,.0f}</p>
            <p><b>⚠️ Riesgo:</b> {row['Riesgo']}</p>
            <p><b>📝 Comentario de auditoría:</b> {row['Comentario']}</p>
        </div>
        """, unsafe_allow_html=True)

# AUDITORÍA POR CATEGORÍA (Formato Tablero)

st.markdown("---")
st.markdown("## 📂 Auditoría Financiera por Categoría")

# Crear DataFrame de auditoría por categoría
auditoria_categoria = pd.DataFrame([
    {"Categoría": "Sin comprobantes", "Sucursal": "FD00 Bodega", "Mes": "January", "Monto": 1500000, "Riesgo": "Alto", "Comentario": "Gastos sin soporte documental."},
    {"Categoría": "Servicios Profesionales", "Sucursal": "FD01 Sucursal", "Mes": "February", "Monto": 750000, "Riesgo": "Medio", "Comentario": "Altos pagos de servicios."},
    {"Categoría": "Viáticos y Gastos Menores", "Sucursal": "FD03 Otro", "Mes": "March", "Monto": 300000, "Riesgo": "Bajo", "Comentario": "Viáticos inusuales."},
    {"Categoría": "Consultorías", "Sucursal": "FD04 Principal", "Mes": "April", "Monto": 1250000, "Riesgo": "Alto", "Comentario": "Pagos sin contratos claros."}
])



# Mostrar auditoría por categoría en formato horizontal
cols_cat = st.columns(3)  # 3 tarjetas por fila
for idx, row in auditoria_categoria.iterrows():
    with cols_cat[idx % 3]:
        st.markdown(f"""
        <div style="background-color:#1e1e1e; padding:15px; border-radius:10px; margin-bottom:20px;">
            <h4 style="color:#ffbd4a;">📂 {row['Categoría']}</h4>
            <p><b>🏢 Sucursal:</b> {row['Sucursal']}</p>
            <p><b>📅 Mes:</b> {row['Mes']}</p>
            <p><b>💵 Monto:</b> ${row['Monto']:,.0f}</p>
            <p><b>⚠️ Riesgo:</b> {row['Riesgo']}</p>
            <p><b>📝 Comentario de auditoría:</b> {row['Comentario']}</p>
        </div>
        """, unsafe_allow_html=True)
# BLOQUES DE AUDITORIA - DASHBOARD

import streamlit as st
import pandas as pd

# --- Bloque 1: Auditoría Financiera por Sucursal ---
st.markdown("---")
st.markdown("## 🔍 Auditoría Financiera por Sucursal")

# DataFrame de auditoría por sucursal
auditoria_sucursal = pd.DataFrame([
    {"Sucursal": "FD00 Bodega", "Mes": "January", "Categoría": "Sin comprobantes", "Monto": 1500000, "Riesgo": "Alto", "Comentario": "No hay soporte documental."},
    {"Sucursal": "FD01 Sucursal", "Mes": "February", "Categoría": "Servicios Profesionales", "Monto": 750000, "Riesgo": "Medio", "Comentario": "Montos elevados respecto promedio."},
    {"Sucursal": "FD03 Otro", "Mes": "March", "Categoría": "Viáticos y Gastos Menores", "Monto": 300000, "Riesgo": "Bajo", "Comentario": "No usual en esta sucursal."}
])

# Mostrar horizontalmente
cols = st.columns(len(auditoria_sucursal))
for idx, row in auditoria_sucursal.iterrows():
    with cols[idx]:
        st.metric(label=f"Sucursal: {row['Sucursal']}", value=f"${row['Monto']:,.0f}")
        st.write(f"**Mes:** {row['Mes']}")
        st.write(f"**Categoría:** {row['Categoría']}")
        riesgo_color = {"Alto": "🔴", "Medio": "🔶", "Bajo": "🔴"}  # Colores de semáforo
        st.write(f"**Riesgo:** {riesgo_color.get(row['Riesgo'], '')} {row['Riesgo']}")
        st.caption(f"Comentario: {row['Comentario']}")


# --- Bloque 2: Auditoría Financiera por Categoría ---
st.markdown("---")
st.markdown("## 📊 Auditoría Financiera por Categoría")
# --- Sección de Categoría ---

# DataFrame de auditoría por categoría
auditoria_categoria = pd.DataFrame([
    {"Categoría": "Sin comprobantes", "Mes": "January", "Monto": 1500000, "Riesgo": "Alto", "Comentario": "Gastos sin soporte documental."},
    {"Categoría": "Servicios Profesionales", "Mes": "February", "Monto": 750000, "Riesgo": "Medio", "Comentario": "Altos pagos de servicios."},
    {"Categoría": "Viáticos y Gastos Menores", "Mes": "March", "Monto": 300000, "Riesgo": "Bajo", "Comentario": "Viáticos inusuales."},
    {"Categoría": "Consultorías", "Mes": "April", "Monto": 1250000, "Riesgo": "Alto", "Comentario": "Pagos sin contratos claros."}
])


# Filtro para categoría
nivel_riesgo_categoria = st.selectbox("Filtrar por nivel de riesgo en Categorías:", ["Todos", "Alto", "Medio", "Bajo"])

if nivel_riesgo_categoria != "Todos":
    vista_filtrada_categoria = auditoria_categoria[auditoria_categoria["Riesgo"] == nivel_riesgo_categoria]
else:
    vista_filtrada_categoria = auditoria_categoria.copy()

# Función para agregar semáforo de riesgo
def semaforo_categoria(riesgo):
    if riesgo == "Alto":
        return "🔴 " + riesgo
    elif riesgo == "Medio":
        return "🟠 " + riesgo
    elif riesgo == "Bajo":
        return "🟡 " + riesgo
    else:
        return riesgo

# Aplicar semáforo
vista_filtrada_categoria["Riesgo"] = vista_filtrada_categoria["Riesgo"].apply(semaforo_categoria)

# Mostrar tabla de categoría
st.dataframe(vista_filtrada_categoria, use_container_width=True)

# DataFrame de auditoría por categoría
# Crear DataFrame para vista previa por categoría
vista_categoria = pd.DataFrame([
    {"Categoría": "Sin comprobantes", "Sucursal": "FD00 Bodega", "Mes": "January", "Monto": 1500000, "Riesgo": "Alto", "Comentario": "No hay soporte documental."},
    {"Categoría": "Servicios Profesionales", "Sucursal": "FD01 Sucursal", "Mes": "February", "Monto": 750000, "Riesgo": "Medio", "Comentario": "Montos elevados respecto promedio."},
    {"Categoría": "Viáticos y Gastos Menores", "Sucursal": "FD03 Otro", "Mes": "March", "Monto": 300000, "Riesgo": "Bajo", "Comentario": "No usual en esta sucursal."},
    {"Categoría": "Consultorías", "Sucursal": "FD04 Principal", "Mes": "April", "Monto": 1250000, "Riesgo": "Alto", "Comentario": "Pagos sin contratos claros."}
])
# Filtro para categorías
nivel_riesgo_categoria = st.selectbox("Filtrar por nivel de riesgo (Sucursal):", ["Todos", "Alto", "Medio", "Bajo"])


if nivel_riesgo_categoria != "Todos":
    vista_filtrada_categoria = vista_categoria[vista_categoria["Riesgo"] == nivel_riesgo_categoria]
else:
    vista_filtrada_categoria = vista_categoria

# Función para agregar semáforo en categorías
def semaforo_categoria(riesgo):
    if riesgo == "Alto":
        return "🔴 " + riesgo
    elif riesgo == "Medio":
        return "🟠 " + riesgo
    elif riesgo == "Bajo":
        return "🟡 " + riesgo
    else:
        return riesgo

# Aplicar semáforo a la columna "Riesgo"
vista_filtrada_categoria["Riesgo"] = vista_filtrada_categoria["Riesgo"].apply(semaforo_categoria)

# Mostrar la tabla final
st.dataframe(vista_filtrada_categoria, use_container_width=True)


auditoria_categoria = pd.DataFrame([
    {"Categoría": "Sin comprobantes", "Mes": "January", "Monto": 1500000, "Riesgo": "Alto", "Comentario": "Gastos sin soporte documental."},
    {"Categoría": "Servicios Profesionales", "Mes": "February", "Monto": 750000, "Riesgo": "Medio", "Comentario": "Altos pagos de servicios."},
    {"Categoría": "Viáticos y Gastos Menores", "Mes": "March", "Monto": 300000, "Riesgo": "Bajo", "Comentario": "Viáticos inusuales."},
    {"Categoría": "Consultorías", "Mes": "April", "Monto": 1250000, "Riesgo": "Alto", "Comentario": "Pagos sin contratos claros."}

])


# Mostrar horizontalmente
cols_cat = st.columns(len(auditoria_categoria))
for idx, row in auditoria_categoria.iterrows():
    with cols_cat[idx]:
        st.metric(label=f"Categoría: {row['Categoría']}", value=f"${row['Monto']:,.0f}")
        st.write(f"**Mes:** {row['Mes']}")
        riesgo_color = {"Alto": "🔴", "Medio": "🔶", "Bajo": "🔴"}
        st.write(f"**Riesgo:** {riesgo_color.get(row['Riesgo'], '')} {row['Riesgo']}")
        st.caption(f"Comentario: {row['Comentario']}")
# --- Vista Previa de Hallazgos y Generar Reporte de Auditoria ---

import streamlit as st
import pandas as pd

st.markdown("---")
st.markdown("## 🔎 Vista Previa de Hallazgos de Auditoría")

# Simulamos datos de hallazgos
hallazgos = pd.DataFrame([
    {"Sucursal": "FD00 Bodega", "Mes": "January", "Categoría": "Sin comprobantes", "Monto": 1500000, "Riesgo": "Alto", "Comentario": "No hay soporte documental."},
    {"Sucursal": "FD01 Sucursal", "Mes": "February", "Categoría": "Servicios Profesionales", "Monto": 750000, "Riesgo": "Medio", "Comentario": "Montos elevados respecto promedio."},
    {"Sucursal": "FD03 Otro", "Mes": "March", "Categoría": "Viáticos y Gastos Menores", "Monto": 300000, "Riesgo": "Bajo", "Comentario": "No usual en esta sucursal."},
    {"Sucursal": "FD02 Principal", "Mes": "April", "Categoría": "Consultorías", "Monto": 1250000, "Riesgo": "Alto", "Comentario": "Pagos sin contratos claros."}
])

# Opcional: Filtro por nivel de riesgo
nivel_riesgo = st.selectbox("Filtrar por nivel de riesgo:", ("Todos", "Alto", "Medio", "Bajo"))

# Aplicar filtro si se selecciona
if nivel_riesgo != "Todos":
    hallazgos = hallazgos[hallazgos['Riesgo'] == nivel_riesgo]

# Mostrar tabla de hallazgos
# Vista previa de hallazgos
st.subheader("🔎 Vista Previa de Hallazgos de Auditoría")

# # --- Filtro de riesgo ---
# Crear DataFrame para vista previa
vista_previa = pd.DataFrame([
    {"Sucursal": "FD00 Bodega", "Mes": "January", "Categoría": "Sin comprobantes", "Monto": 1500000, "Riesgo": "Alto", "Comentario": "No hay soporte documental."},
    {"Sucursal": "FD01 Sucursal", "Mes": "February", "Categoría": "Servicios Profesionales", "Monto": 750000, "Riesgo": "Medio", "Comentario": "Montos elevados respecto promedio."},
    {"Sucursal": "FD03 Otro", "Mes": "March", "Categoría": "Viáticos y Gastos Menores", "Monto": 300000, "Riesgo": "Bajo", "Comentario": "No usual en esta sucursal."},
    {"Sucursal": "FD04 Principal", "Mes": "April", "Categoría": "Consultorías", "Monto": 1250000, "Riesgo": "Alto", "Comentario": "Pagos sin contratos claros."}
])

if nivel_riesgo != "Todos":
    vista_filtrada = vista_previa[vista_previa["Riesgo"] == nivel_riesgo]
else:
    vista_filtrada = vista_previa

# --- Aplicar Semáforo 🚦 ---
def semaforo(riesgo):
    if riesgo == "Alto":
        return "🔴 Alto"
    elif riesgo == "Medio":
        return "🟠 Medio"
    elif riesgo == "Bajo":
        return "🟡 Bajo"
    else:
        return riesgo

vista_filtrada['Riesgo'] = vista_filtrada['Riesgo'].apply(semaforo)

# --- Mostrar tabla con semáforo ---
st.dataframe(vista_filtrada, use_container_width=True)
hallazgos["Riesgo"] = hallazgos["Riesgo"].apply(semaforo)  # Línea nueva 👈


# Boton para exportar
import io

if st.button("🖐️ Generar Reporte de Auditoría"):
    # Crear archivo Excel temporal
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        hallazgos.to_excel(writer, index=False, sheet_name='Hallazgos Auditoria')
    st.download_button(
        label="🔗 Descargar Reporte Excel",
        data=output.getvalue(),
        file_name="Reporte_Auditoria_Hallazgos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
import streamlit as st
import pandas as pd

# --- Sección de Selección para Reporte ---

st.markdown("---")
st.markdown("## 🔍 Seleccionar Información para Generar Reporte de Auditoría")

# Opciones de selección
opciones = [
    "Imprimir Todo",
    "Imprimir Solo Sucursales",
    "Imprimir Solo Categorías",
    "Seleccionar Sucursales Específicas",
    "Seleccionar Categorías Específicas"
]

seleccion = st.multiselect("Elige las opciones que deseas incluir en el reporte:", opciones)

# Mostrar lo que se ha seleccionado
if seleccion:
    st.success(f"Seleccionaste: {', '.join(seleccion)}")

    # Botón para generar reporte basado en selección
    if st.button("🖨️ Generar Reporte de Auditoría", key="generar_reporte_auditoria_selector"):
        st.info("🔗 El reporte será generado según tus selecciones.")

else:
    st.warning("⚠️ Debes seleccionar al menos una opción para habilitar la generación del reporte.")
# --- Bloque: Análisis de Gastos por Categoría Limpia (mensual) ---

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# --- Análisis por Categoría_Limpia ---
st.markdown("---")
st.markdown("## 🌊 Análisis de Gasto por Categoría")

# --- Análisis por Categoría_Limpia ---
st.markdown("---")
st.markdown("### 🌁 Gasto por Mes - Categoría seleccionada")

# Verifica que el archivo fue cargado y contiene las columnas necesarias
if uploaded_file:
    df = pd.read_excel(uploaded_file)

    columnas_necesarias = {'Categoria_Limpia', 'Nombre_Mes', 'Monto'}
    if columnas_necesarias.issubset(df.columns):

        # 1. Selector de categoría
        categoria_seleccionada = st.selectbox(
            "Selecciona una categoría:",
            df['Categoria_Limpia'].dropna().unique()
        )

        # 2. Agrupar por mes los datos de la categoría seleccionada
        resumen_categoria = df[df['Categoria_Limpia'] == categoria_seleccionada]
        resumen_mensual = resumen_categoria.groupby('Nombre_Mes')['Monto'].sum().reset_index()

        # 3. Ordenar meses correctamente
        orden_meses = ["January", "February", "March", "April", "May", "June", "July",
                       "August", "September", "October", "November", "December"]
        resumen_mensual['Nombre_Mes'] = pd.Categorical(resumen_mensual['Nombre_Mes'], categories=orden_meses, ordered=True)
        resumen_mensual = resumen_mensual.sort_values('Nombre_Mes')

        # 4. Visualización
        col1, col2 = st.columns([2, 1])

        with col1:
            fig, ax = plt.subplots()
            ax.bar(resumen_mensual['Nombre_Mes'], resumen_mensual['Monto'])
            ax.set_xlabel("Mes")
            ax.set_ylabel("Monto ($)")
            ax.set_title("Gasto por Mes")
            plt.xticks(rotation=45)
            st.pyplot(fig)

        with col2:
            st.markdown("### 📋 Indicadores de Gasto Mensual")
            for _, row in resumen_mensual.iterrows():
                color = "\U0001F7E5" if row['Monto'] > 1_000_000 else ("\U0001F7E7" if row['Monto'] > 500_000 else "\U0001F7E8")
                st.metric(label=f"Mes: {row['Nombre_Mes']}", value=f"{color} ${row['Monto']:,.2f}")

            st.divider()
            total = resumen_mensual['Monto'].sum()
            st.metric(label="Gran Total", value=f"${total:,.2f}")

        import io

import io

# Crear el archivo Excel temporal
output = io.BytesIO()
with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
    # Hoja 1: Resumen por Categoría
    resumen_mensual.to_excel(writer, index=False, sheet_name='Resumen por Categoría')

    # Hoja 2: Detalle por Categoría
    detalle_categoria = df[df['Categoria_Limpia'] == categoria_seleccionada]
    detalle_categoria.to_excel(writer, index=False, sheet_name='Detalle por Categoría')

    # Hoja 3: Checklist de Auditoría
    hoja_auditoria = detalle_categoria.copy()
    hoja_auditoria["✅ Verificado"] = ""
    hoja_auditoria["📑 Documento Soporte"] = ""
    hoja_auditoria["📅 Fecha de Revisión"] = ""
    hoja_auditoria["👤 Aprobado por"] = ""
    hoja_auditoria["✍️ Firma"] = ""
    hoja_auditoria.to_excel(writer, index=False, sheet_name='Hoja de Auditoría')


# Botón de descarga con clave única para evitar conflicto
st.download_button(
    label="⬇️ Descargar Reporte de Categoría",
    data=output.getvalue(),
    file_name=f"Reporte_{categoria_seleccionada.replace(' ', '_')}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    key="descargar_categoria_completo"
)

st.warning("⚠️ Debes cargar primero el archivo Excel arriba para usar este análisis.")

