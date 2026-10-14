import io
import os
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


# Función para convertir el DataFrame a un archivo de Excel (.xlsx) en memoria
def convertir_a_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Registros_Terreno")
    processed_data = output.getvalue()
    return processed_data


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
            st.warning("👥 Esta actividad requiere 2 personas e información de migración:")
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
                "Origen del problema (Explicación