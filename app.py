# --- BLOQUE FINAL: GENERAR ARCHIVO DE AUDITORÍA Y DESCARGAR ---
from io import BytesIO
import xlsxwriter

# Función auxiliar para dar formato a miles sin decimales
def formato_miles(valor):
    return f"{valor/1000:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Crear archivo en memoria
output = BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    wb = writer.book

    # FORMATO GENERAL
    formato_titulo = wb.add_format({'bold': True, 'font_size': 28, 'font_color': 'red'})
    formato_subtitulo = wb.add_format({'font_size': 12, 'bold': False})
    formato_encabezado = wb.add_format({'bold': True, 'bg_color': '#D9D9D9', 'border': 1, 'align': 'center'})
    formato_numero = wb.add_format({'num_format': '#,##0', 'align': 'center'})
    formato_celda = wb.add_format({'align': 'center'})
    formato_check = wb.add_format({'align': 'center', 'font_size': 14})

    # ---------- HOJA 1: RESUMEN POR CATEGORÍA ----------
    hoja1 = df.copy()
    hoja1['Total'] = hoja1.groupby('Categoria')['Monto'].transform('sum')
    hoja1 = hoja1.groupby('Categoria').agg(
        Cantidad_Registros=('Descripcion', 'count'),
        Total_Gasto=('Monto', 'sum')
    ).reset_index()
    hoja1['Grupo_Riesgo'] = hoja1['Total_Gasto'].apply(lambda x: "🔴 Crítico" if x >= 6_000_000 else "🟡 Moderado" if x >= 3_000_000 else "🟢 Bajo")
    hoja1['Total_Gasto'] = hoja1['Total_Gasto'].apply(lambda x: round(x/1000))
    hoja1 = hoja1.sort_values(by='Total_Gasto', ascending=False).reset_index(drop=True)
    hoja1.index += 1
    hoja1.to_excel(writer, sheet_name='Resumen por Categoría', index_label='N°')

    ws1 = writer.sheets['Resumen por Categoría']
    ws1.write('A1', 'Auditoría grupo Farmavalue', formato_titulo)
    ws1.write('A2', 'Reporte de gastos del 01 de Enero al 20 de abril del 2025', formato_subtitulo)
    ws1.write('A3', 'Auditor Asignado:', formato_subtitulo)
    ws1.write('A4', 'Fecha de la Auditoría', formato_subtitulo)

    for col_num, _ in enumerate(hoja1.columns.insert(0, 'N°')):
        ws1.set_column(col_num, col_num, 20)
        ws1.write(5, col_num, hoja1.columns.insert(0, 'N°')[col_num], formato_encabezado)

    # ---------- HOJA 2: RESUMEN POR SUCURSAL ----------
    hoja2 = df.copy()
    hoja2['Grupo_Riesgo'] = hoja2.groupby('Categoria')['Monto'].transform('sum').apply(
        lambda x: "🔴 Crítico" if x >= 6_000_000 else "🟡 Moderado" if x >= 3_000_000 else "🟢 Bajo"
    )
    resumen_suc = hoja2.groupby(['Sucursales', 'Grupo_Riesgo']).agg(
        Cantidad=('Descripcion', 'count'),
        Total=('Monto', 'sum')
    ).reset_index()
    resumen_suc['Total'] = resumen_suc['Total'].apply(lambda x: round(x/1000))
    resumen_suc = resumen_suc.sort_values(by='Total', ascending=False).reset_index(drop=True)
    resumen_suc.index += 1
    resumen_suc.to_excel(writer, sheet_name='Resumen por Sucursal', index_label='N°')

    ws2 = writer.sheets['Resumen por Sucursal']
    ws2.write('A1', 'Auditoría grupo Farmavalue', formato_titulo)
    ws2.write('A2', 'Reporte de gastos del 01 de Enero al 20 de abril del 2025', formato_subtitulo)
    ws2.write('A3', 'Auditor Asignado:', formato_subtitulo)
    ws2.write('A4', 'Fecha de la Auditoría', formato_subtitulo)

    for col_num, _ in enumerate(resumen_suc.columns.insert(0, 'N°')):
        ws2.set_column(col_num, col_num, 20)
        ws2.write(5, col_num, resumen_suc.columns.insert(0, 'N°')[col_num], formato_encabezado)

    # ---------- HOJA 3: AUDITORÍA SUCURSALES ----------
    aud = hoja2.copy()
    aud['¿Revisar?'] = aud['Descripcion'].apply(lambda x: '☑' if len(x) < 15 or any(p in str(x).lower() for p in ['varios', 'otros', 'misc']) else '☐')
    aud['Fecha'] = pd.to_datetime(aud['Fecha']).dt.strftime('%Y-%m-%d')
    aud['Monto'] = aud['Monto'].apply(lambda x: round(x/1000))
    aud = aud[['Sucursales', 'Fecha', 'Categoria', 'Grupo_Riesgo', 'Descripcion', 'Monto', '¿Revisar?']]
    aud = aud.sort_values(by='Monto', ascending=False).reset_index(drop=True)
    aud.index += 1
    aud.to_excel(writer, sheet_name='Auditoría Sucursales', index_label='N°')

    ws3 = writer.sheets['Auditoría Sucursales']
    ws3.write('A1', 'Auditoría grupo Farmavalue', formato_titulo)
    ws3.write('A2', 'Reporte de gastos del 01 de Enero al 20 de abril del 2025', formato_subtitulo)
    ws3.write('A3', 'Auditor Asignado:', formato_subtitulo)
    ws3.write('A4', 'Fecha de la Auditoría', formato_subtitulo)

    for col_num, _ in enumerate(aud.columns.insert(0, 'N°')):
        ws3.set_column(col_num, col_num, 20)
        ws3.write(5, col_num, aud.columns.insert(0, 'N°')[col_num], formato_encabezado)

# Botón de descarga
output.seek(0)
b64 = base64.b64encode(output.read()).decode()
st.markdown("## 📥 Descargar Cédula de Trabajo de Auditoría")
st.markdown(f'<a href="data:application/octet-stream;base64,{b64}" download="Cedula_de_Trabajo_de_Auditoria.xlsx">📄 Descargar Excel</a>', unsafe_allow_html=True)
