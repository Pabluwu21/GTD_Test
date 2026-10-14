import io
import os
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
import pandas as pd
import plotly.express as px
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Control de Terreno - Habilitaciones y Servicios", layout="wide"
)

# Archivo de almacenamiento local para pruebas
ARCHIVO_DATOS = "registros_terreno.csv"

# Columnas del sistema
COLUMNAS = [
    "Fecha_Registro",
    "Tecnico",
    "Orden_Trabajo",
    "Codigo_Servicio",
    "Tipo_Trabajo",
    "Subtipo_NRA",
    "Tecnico_Apoyo",
    "Acceso_Nuevo",
    "IMC_Nuevo",
    "Acceso_Switch",
    "Puerta_Switch",
    "IDS",
    "Operador_Red",
    "Estado_Trabajo",
    "Categoria_Fallo",
    "Detalle_Fallo",
    "Estado_Equipamiento",
    "Observaciones",
]


# Función para generar y dar formato estético agrupado al Excel
def convertir_a_excel_formateado(df):
    output = io.BytesIO()

    # 1. ORDENAR DATOS POR TIPO Y SUBTIPO DE TRABAJO
    # Definir un orden personalizado para los tipos de trabajo principales
    orden_tipos = {
        "Habilitación de servicio": 1,
        "NRA": 2,
        "Levantamiento en terreno": 3,
    }

    df_agrupado = df.copy()
    df_agrupado["Prioridad_Grupo"] = df_agrupado["Tipo_Trabajo"].map(
        lambda x: orden_tipos.get(x, 99)
    )

    # Ordenar por Prioridad del Grupo, luego Subtipo NRA y Fecha
    df_agrupado = df_agrupado.sort_values(
        by=["Prioridad_Grupo", "Subtipo_NRA", "Fecha_Registro"],
        ascending=[True, True, True],
    ).drop(columns=["Prioridad_Grupo"])

    # 2. CREAR LIBRO Y ESTILOS OPENPYXL
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Registros_Agrupados"

    # Estilos de encabezado principal
    header_fill = PatternFill(
        start_color="1F4E78", end_color="1F4E78", fill_type="solid"
    )  # Azul Corporativo
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")

    # Colores sutiles para destacar grupos de trabajo
    fill_hab = PatternFill(
        start_color="E8F1F5", end_color="E8F1F5", fill_type="solid"
    )  # Azul tenue para Habilitación
    fill_nra = PatternFill(
        start_color="FEF5E7", end_color="FEF5E7", fill_type="solid"
    )  # Naranja/Crema tenue para NRA
    fill_lev = PatternFill(
        start_color="EAFAF1", end_color="EAFAF1", fill_type="solid"
    )  # Verde tenue para Levantamiento
    fill_default = PatternFill(
        start_color="FFFFFF", end_color="FFFFFF", fill_type="solid"
    )

    thin_border = Border(
        left=Side(style="thin", color="D9D9D9"),
        right=Side(style="thin", color="D9D9D9"),
        top=Side(style="thin", color="D9D9D9"),
        bottom=Side(style="thin", color="D9D9D9"),
    )

    align_center = Alignment(horizontal="center", vertical="center")
    align_left = Alignment(horizontal="left", vertical="center")

    # Escribir encabezados
    encabezados = list(df_agrupado.columns)
    ws.append(encabezados)

    for col_num, col_name in enumerate(encabezados, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = align_center
        cell.border = thin_border

    ws.row_dimensions[1].height = 28  # Altura del encabezado

    # Escribir filas de datos agrupadas con sombreado categórico
    for row_idx, row_data in enumerate(df_agrupado.values, start=2):
        ws.append(list(row_data))
        ws.row_dimensions[row_idx].height = 20  # Altura de filas

        # Identificar tipo de trabajo para asignar color de grupo
        tipo_actual = row_data[4]  # Columna 'Tipo_Trabajo'
        if tipo_actual == "Habilitación de servicio":
            row_fill = fill_hab
        elif tipo_actual == "NRA":
            row_fill = fill_nra
        elif tipo_actual == "Levantamiento en terreno":
            row_fill = fill_lev
        else:
            row_fill = fill_default

        for col_idx, value in enumerate(row_data, start=1):
            cell = ws.cell(row=row_idx, column=col_idx)
            cell.fill = row_fill
            cell.border = thin_border
            cell.font = Font(name="Calibri", size=10)

            # Alineación según tipo de columna
            col_name = encabezados[col_idx - 1]
            if col_name in [
                "Fecha_Registro",
                "Orden_Trabajo",
                "Codigo_Servicio",
                "Estado_Trabajo",
                "Puerta_Switch",
            ]:
                cell.alignment = align_center
            else:
                cell.alignment = align_left

    # Auto-ajustar ancho de columnas
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            val_str = str(cell.value or "")
            if len(val_str) > max_len:
                max_len = len(val_str)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

    wb.save(output)
    return output.getvalue()


# Función para cargar datos
def cargar_datos():
    if "df_datos" not in st.session_state:
        if os.path.exists(ARCHIVO_DATOS):
            st.session_state.df_datos = pd.read_csv(ARCHIVO_DATOS)
        else:
            st.session_state.df_datos = pd.DataFrame(columns=COLUMNAS)
    return st.session_state.df_datos


# Función para guardar un nuevo registro
def guardar_registro(nuevo_dict):
    df_actual = cargar_datos()
    df_nuevo = pd.DataFrame([nuevo_dict])
    df_final = pd.concat([df_actual, df_nuevo], ignore_index=True)

    st.session_state.df_datos = df_final

    try:
        df_final.to_csv(ARCHIVO_DATOS, index=False)
    except Exception:
        pass


st.title("📡 Sistema de Control y Retroalimentación de Terreno")
st.markdown("Plataforma de gestión de trabajos, resguardo y causas de fallos.")

# ---------------------------------------------------------
# BARRA LATERAL: NAVEGACIÓN
# ---------------------------------------------------------
st.sidebar.title("📌 Navegación")

opciones_menu = [
    "Registrar Trabajo",
    "Panel de Control y Gráficos",
    "Perfil del Técnico",
]

menu = st.sidebar.radio("Ir a:", opciones_menu)

# ---------------------------------------------------------
# PESTAÑA 1: REGISTRAR TRABAJO
# ---------------------------------------------------------
if menu == "Registrar Trabajo":
    st.header("📝 Formulario de Trabajo en Terreno")

    col1, col2 = st.columns(2)

    with col1:
        tecnico = st.text_input("Nombre del Técnico a cargo")
        orden = st.text_input("Orden de Trabajo (Ej: 1040548)")
        codigo_servicio = st.text_input("Código de Servicio (Ej: 010001)")
        tipo_trabajo = st.selectbox(
            "Tipo de Trabajo / Actividad",
            [
                "Habilitación de servicio",
                "NRA",
                "Levantamiento en terreno",
            ],
        )

    with col2:
        ids = st.selectbox(
            "IDS (Jefe de Implementación)",
            ["Nicolas Zuñiga", "Isaias Avalos", "Marcelo Saez"],
        )
        operador_red = st.text_input("Operador de Red")
        estado_trabajo = st.selectbox(
            "¿Se pudo realizar el trabajo?",
            ["Sí", "No"],
            key="estado_trabajo_select",
        )

    # Variables condicionales por defecto
    subtipo_nra = "N/A"
    tecnico_apoyo = "N/A"
    acceso_nuevo = "N/A"
    imc_nuevo = "N/A"
    acceso_switch = "N/A"
    puerta_switch = "N/A"

    # LÓGICA DE CAMPOS CONDICIONALES POR TIPO DE TRABAJO
    if tipo_trabajo == "Habilitación de servicio":
        st.info("🔌 Datos del Switch de Acceso (Requerido para Habilitaciones)")
        col_sw1, col_sw2 = st.columns(2)
        with col_sw1:
            acceso_switch = st.text_input(
                "Acceso (Switch de Acceso)",
                placeholder="Ej: SW-ACC-01",
            )
        with col_sw2:
            puerta_switch = st.text_input(
                "Puerta (Puerto / Slot de salida)",
                placeholder="Ej: Gi0/1/2",
            )

    elif tipo_trabajo == "NRA":
        st.info("📋 Detalle de Actividad NRA")
        subtipo_nra = st.selectbox(
            "Subtipo de NRA",
            [
                "Cambio de equipo",
                "Cambio de tecnología / Aumento de velocidad",
                "Manos Remotas",
                "Certificación",
                "Habilitación NRA",
                "Levantamiento NRA",
            ],
        )

        if subtipo_nra == "Cambio de tecnología / Aumento de velocidad":
            st.warning(
                "👥 Esta actividad requiere 2 personas e información de migración:"
            )
            col_tec, col_acc, col_imc = st.columns(3)
            with col_tec:
                tecnico_apoyo = st.text_input(
                    "Técnico de Apoyo",
                    placeholder="Ej: Juan Pérez",
                )
            with col_acc:
                acceso_nuevo = st.text_input(
                    "Acceso Nuevo",
                    placeholder="Ej: SW-ACC-NUEVO-01",
                )
            with col_imc:
                imc_nuevo = st.text_input(
                    "IMC Nuevo",
                    placeholder="Ej: IMC-998877",
                )

        elif subtipo_nra == "Habilitación NRA":
            acceso_switch = st.text_input(
                "Switch de Acceso de Mall",
                placeholder="Ej: SW-MALL-01",
            )

    categoria_fallo = "N/A"
    detalle_fallo = "N/A"
    estado_equipamiento = "N/A"

    st.markdown("---")

    if estado_trabajo == "No":
        st.warning("⚠️ Detalle el motivo por el cual NO se realizó el trabajo:")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            categoria_fallo = st.selectbox(
                "Categoría del Problema",
                [
                    "Falta de Equipo / Materiales",
                    "Sin Acceso / Permisos Denegados",
                    "Problema de Ruta / Logística",
                    "Falla de Coordinación / Supervisión",
                    "Cliente no Disponible",
                ],
            )
        with col_f2:
            detalle_fallo = st.text_area(
                "Origen del problema (Explicación para retroalimentación)"
            )

    elif estado_trabajo == "Sí":
        st.success("✅ Trabajo realizado. Indique estado del equipamiento:")
        estado_equipamiento = st.selectbox(
            "Estado del Equipamiento",
            [
                "Instalado y resguardado correctamente en rack",
                "Instalado pero quedó fuera del rack / sin resguardo",
                "Faltó equipo o componente secundario por instalar",
            ],
        )

    st.markdown("---")
    observaciones = st.text_area(
        "📝 Observaciones Generales (Opcional)",
        placeholder="Comentarios adicionales sobre la visita, detalles técnicos, etc.",
    )

    st.markdown("---")
    if st.button("Guardar Registro", type="primary"):
        if orden and tecnico:
            fecha_actual = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")
            registro = {
                "Fecha_Registro": fecha_actual,
                "Tecnico": tecnico,
                "Orden_Trabajo": orden,
                "Codigo_Servicio": codigo_servicio,
                "Tipo_Trabajo": tipo_trabajo,
                "Subtipo_NRA": subtipo_nra,
                "Tecnico_Apoyo": tecnico_apoyo,
                "Acceso_Nuevo": acceso_nuevo,
                "IMC_Nuevo": imc_nuevo,
                "Acceso_Switch": acceso_switch,
                "Puerta_Switch": puerta_switch,
                "IDS": ids,
                "Operador_Red": operador_red,
                "Estado_Trabajo": estado_trabajo,
                "Categoria_Fallo": categoria_fallo,
                "Detalle_Fallo": detalle_fallo,
                "Estado_Equipamiento": estado_equipamiento,
                "Observaciones": observaciones
                if observaciones
                else "Sin observaciones",
            }
            guardar_registro(registro)
            st.success(
                f"¡Registro para la Orden {orden} guardado exitosamente!"
            )
            st.balloons()
        else:
            st.error(
                "Por favor, complete al menos la Orden de Trabajo y el Nombre del Técnico."
            )

# ---------------------------------------------------------
# PESTAÑA 2: PANEL DE CONTROL Y GRÁFICOS
# ---------------------------------------------------------
elif menu == "Panel de Control y Gráficos":
    st.header("📊 Panel General, Gráficos y Retroalimentación")

    df = cargar_datos()

    if df.empty:
        st.info("Aún no hay registros guardados. Ingrese datos en el formulario.")
    else:
        total = len(df)
        exitosos = len(df[df["Estado_Trabajo"] == "Sí"])
        fallidos = len(df[df["Estado_Trabajo"] == "No"])

        m1, m2, m3 = st.columns(3)
        m1.metric("Total Trabajos Registrados", total)
        m2.metric("Realizados con Éxito", exitosos)
        m3.metric("No Realizados (Fallos)", fallidos)

        st.divider()

        st.subheader("📈 Distribución Visual de Resultados")
        g_col1, g_col2 = st.columns(2)

        with g_col1:
            st.markdown("**Proporción Éxito vs. Fallos General**")
            fig_pie_estado = px.pie(
                df,
                names="Estado_Trabajo",
                title="Efectividad Global de Trabajos",
                color="Estado_Trabajo",
                color_discrete_map={"Sí": "#2ecc71", "No": "#e74c3c"},
                hole=0.3,
            )
            st.plotly_chart(fig_pie_estado, use_container_width=True)

        with g_col2:
            st.markdown("**Distribución por Tipo de Trabajo**")
            fig_pie_tipos = px.pie(
                df,