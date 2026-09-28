import pandas as pd
import plotly.express as px
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Control de Terreno - Habilitaciones y Servicios", layout="wide"
)

# Columnas del sistema
COLUMNAS = [
    "Fecha_Registro",
    "Tecnico",
    "Orden_Trabajo",
    "Codigo_Servicio",
    "Tipo_Trabajo",
    "Acceso_Switch",
    "Puerta_Switch",
    "IDS",
    "Operador_Red",
    "Estado_Trabajo",
    "Categoria_Fallo",
    "Detalle_Fallo",
    "Estado_Equipamiento",
]

# Inicialización de la base de datos en la memoria de la sesión
if "df_datos" not in st.session_state:
    st.session_state.df_datos = pd.DataFrame(columns=COLUMNAS)


# Función para cargar datos
def cargar_datos():
    return st.session_state.df_datos


# Función para guardar un nuevo registro
def guardar_registro(nuevo_dict):
    df_actual = st.session_state.df_datos
    df_nuevo = pd.DataFrame([nuevo_dict])
    st.session_state.df_datos = pd.concat(
        [df_actual, df_nuevo], ignore_index=True
    )


st.title("📡 Sistema de Control y Retroalimentación de Terreno")
st.markdown("Plataforma de gestión de trabajos, resguardo y causas de fallos.")

menu = st.sidebar.selectbox(
    "Menú Principal",
    [
        "Registrar Trabajo",
        "Panel de Control y Gráficos",
        "Perfil del Técnico",
    ],
)

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
            "Tipo de Trabajo",
            [
                "Habilitación de servicio",
                "Levantamiento en terreno",
                "NRA",
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

    # Campos condicionales para Switch de Acceso (Solo en Habilitación de servicio)
    acceso_switch = "N/A"
    puerta_switch = "N/A"

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

    # Variables de falla / equipamiento
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
    if st.button("Guardar Registro", type="primary"):
        if orden and tecnico:
            fecha_actual = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")
            registro = {
                "Fecha_Registro": fecha_actual,
                "Tecnico": tecnico,
                "Orden_Trabajo": orden,
                "Codigo_Servicio": codigo_servicio,
                "Tipo_Trabajo": tipo_trabajo,
                "Acceso_Switch": acceso_switch,
                "Puerta_Switch": puerta_switch,
                "IDS": ids,
                "Operador_Red": operador_red,
                "Estado_Trabajo": estado_trabajo,
                "Categoria_Fallo": categoria_fallo,
                "Detalle_Fallo": detalle_fallo,
                "Estado_Equipamiento": estado_equipamiento,
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
        # Métricas principales
        total = len(df)
        exitosos = len(df[df["Estado_Trabajo"] == "Sí"])
        fallidos = len(df[df["Estado_Trabajo"] == "No"])

        m1, m2, m3 = st.columns(3)
        m1.metric("Total Trabajos Registrados", total)
        m2.metric("Realizados con Éxito", exitosos)
        m3.metric("No Realizados (Fallos)", fallidos)

        st.divider()

        # Sección de Gráficos Circulares
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
            df_fallos = df[df["Estado_Trabajo"] == "No"]
            if not df_fallos.empty:
                st.markdown("**Distribución de Categorías de Fallos**")
                fig_pie_fallos = px.pie(
                    df_fallos,
                    names="Categoria_Fallo",
                    title="Causas de Trabajos No Realizados",
                    hole=0.3,
                )
                st.plotly_chart(fig_pie_fallos, use_container_width=True)
            else:
                st.info("No hay trabajos fallidos registrados para mostrar causas.")

        st.divider()

        # Tabla consolidada de datos
        st.subheader("📋 Consolidado de Trabajos (Tabla Interactiva)")
        st.dataframe(df, use_container_width=True)

        # Botón de descarga
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Descargar Reporte Consolidado (Excel/CSV)",
            data=csv_data,
            file_name="reporte_trabajos_terreno.csv",
            mime="text/csv",
        )

        st.divider()

        # Retroalimentación por IDS
        st.subheader("🔎 Retroalimentación por IDS (Jefe de Implementación)")
        ids_unicos = df["IDS"].dropna().unique()
        if len(ids_unicos) > 0:
            ids_seleccionado = st.selectbox(
                "Seleccione un IDS para revisar fallos asociados:",
                ids_unicos,
            )

            df_ids = df[df["IDS"] == ids_seleccionado]
            fallos_ids = df_ids[df_ids["Estado_Trabajo"] == "No"]

            st.write(
                f"**Resumen para {ids_seleccionado}:** Total asignados: {len(df_ids)} | Trabajos con problema: {len(fallos_ids)}"
            )

            if not fallos_ids.empty:
                for idx, row in fallos_ids.iterrows():
                    st.markdown(
                        f"- **Orden {row['Orden_Trabajo']}** (Técnico: {row['Tecnico']} | Operador: {row['Operador_Red']}): "
                        f"*{row['Categoria_Fallo']}* — **Origen:** {row['Detalle_Fallo']}"
                    )
            else:
                st.success(
                    f"El IDS {ids_seleccionado} no presenta trabajos fallidos."
                )

# ---------------------------------------------------------
# PESTAÑA 3: PERFIL DEL TÉCNICO
# ---------------------------------------------------------
elif menu == "Perfil del Técnico":
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
            st.dataframe(
                df_tec[
                    [
                        "Fecha_Registro",
                        "Orden_Trabajo",
                        "Tipo_Trabajo",
                        "Estado_Trabajo",
                        "Categoria_Fallo",
                        "Detalle_Fallo",
                        "Estado_Equipamiento",
                    ]
                ],
                use_container_width=True,
            )