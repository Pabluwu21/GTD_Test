import io
import os
import pandas as pd
import plotly.express as px
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Control de Terreno - Habilitaciones y Servicios", layout="wide"
)

# Definir la contraseña de Administrador
CLAVE_ADMIN = "admin123"

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
# BARRA LATERAL: CONTROL DE ACCESO
# ---------------------------------------------------------
st.sidebar.title("🔐 Control de Acceso")

es_admin = False
clave_ingresada = st.sidebar.text_input(
    "Clave de Administrador", type="password", placeholder="Ingrese clave..."
)

if clave_ingresada == CLAVE_ADMIN:
    es_admin = True
    st.sidebar.success("🔓 Acceso de Administrador Activo")
elif clave_ingresada != "":
    st.sidebar.error("❌ Clave incorrecta")

st.sidebar.divider()

if es_admin:
    opciones_menu = [
        "Registrar Trabajo",
        "Panel de Control y Gráficos",
        "Perfil del Técnico",
    ]
else:
    opciones_menu = ["Registrar Trabajo"]
    st.sidebar.info(
        "ℹ️ Modo Usuario: Sólo acceso habilitado para el registro de trabajos."
    )

menu = st.sidebar.radio("Navegación", opciones_menu)

# ---------------------------------------------------------
# PESTAÑA 1: REGISTRAR TRABAJO
# ---------------------------------------------------------
if menu == "Registrar Trabajo":
    st.header("