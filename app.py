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

# Columnas del sistema actualizadas
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
                "Observaciones": observaciones if observaciones else "Sin observaciones",
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
# PESTAÑA 2: PANEL DE CONTROL Y GRÁFICOS (Sólo Admin)
# ---------------------------------------------------------
elif menu == "Panel de Control y Gráficos" and es_admin:
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
                names="Tipo_Trabajo",
                title="Tipos de Actividades Solicitadas",
                hole=0.3,
            )
            st.plotly_chart(fig_pie_tipos, use_container_width=True)

        st.divider()

        st.subheader("📋 Consolidado de Trabajos (Tabla Interactiva)")
        st.dataframe(df, use_container_width=True)

        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Descargar Reporte Consolidado (Excel/CSV)",
            data=csv_data,
            file_name="reporte_trabajos_terreno.csv",
            mime="text/csv",
        )

# ---------------------------------------------------------
# PESTAÑA 3: PERFIL DEL TÉCNICO (Sólo Admin)
# ---------------------------------------------------------
elif menu == "Perfil del Técnico" and es_admin:
    st.header("👤 Perfil Individual del Técnico y Desempeño")

    df = cargar_datos()

    if df.empty:
        st.info("Aún no hay datos para mostrar perfiles de técnicos.")
    else:
        tecnicos_unicos = df["Tecnico"].dropna().unique()
        if len(tecnicos_unicos) > 0:
            tecnico_sel = st.selectbox("Seleccione un Técnico:", tecnicos_unicos)

            df_tec = df[df["Tecnico"] == tecnico_sel]

            st.markdown("---")

            card_col1, card_col2 = st.columns([1, 3])

            with card_col1:
                st.image(
                    "https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
                    width=130,
                )
                st.subheader(f"{tecnico_sel}")
                st.caption("Técnico de Terreno / Cuadrilla")

                tot_tec = len(df_tec)
                exi_tec = len(df_tec[df_tec["Estado_Trabajo"] == "Sí"])
                fal_tec = tot_tec - exi_tec

                st.markdown(f"**Total Trabajos:** {tot_tec}")
                st.markdown(f"✅ **Exitosos:** {exi_tec}")
                st.markdown(f"❌ **Fallidos:** {fal_tec}")

            with card_col2:
                st.subheader("📊 Análisis de Desempeño (Gráficos Circulares)")
                pie_col1, pie_col2 = st.columns(2)

                with pie_col1:
                    fig_tec_estado = px.pie(
                        df_tec,
                        names="Estado_Trabajo",
                        title="Proporción Éxito vs. Fallos",
                        color="Estado_Trabajo",
                        color_discrete_map={"Sí": "#2ecc71", "No": "#e74c3c"},
                        hole=0.4,
                    )
                    st.plotly_chart(fig_tec_estado, use_container_width=True)

                with pie_col2:
                    fig_tec_tipos = px.pie(
                        df_tec,
                        names="Tipo_Trabajo",
                        title="Tipos de Trabajos Asignados",
                        hole=0.4,
                    )
                    st.plotly_chart(fig_tec_tipos, use_container_width=True)

            st.divider()

            st.subheader("📋 Historial de Trabajos de este Técnico")
            st.dataframe(df_tec, use_container_width=True)