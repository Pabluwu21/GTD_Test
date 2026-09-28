import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components
from streamlit_gsheets import GSheetsConnection

# Configuración de la página
st.set_page_config(
    page_title="Control de Terreno - Habilitaciones y Servicios", layout="wide"
)

# Conexión con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# ENLACE OFICIAL DE TU GOOGLE FORM INTEGRADO
URL_GOOGLE_FORM = "https://docs.google.com/forms/d/e/1FAIpQLSd6s7LwRZUeW-R2VqgX6esSHTzm9iuS1d4CareTqk9nvswnqA/viewform?embedded=true"


def cargar_datos():
    try:
        # Lee la pestaña generada por el formulario de Google en la hoja de cálculo
        df = conn.read(worksheet="Respuestas de formulario 1", ttl=0)
        df = df.dropna(how="all")

        # Mapeo de nombres de columnas para concordar con los gráficos y paneles
        renombrar_cols = {
            "Marca temporal": "Fecha_Registro",
            "Nombre del Técnico a cargo": "Tecnico",
            "Orden de Trabajo": "Orden_Trabajo",
            "Código de Servicio": "Codigo_Servicio",
            "Tipo de Trabajo": "Tipo_Trabajo",
            "Acceso (Switch de Acceso)": "Acceso_Switch",
            "Puerta (Puerto / Slot de salida)": "Puerta_Switch",
            "IDS (Jefe de Implementación)": "IDS",
            "Operador de Red": "Operador_Red",
            "¿Se pudo realizar el trabajo?": "Estado_Trabajo",
            "Categoría del Problema": "Categoria_Fallo",
            "Origen del problema / Detalle": "Detalle_Fallo",
            "Estado del Equipamiento": "Estado_Equipamiento",
        }
        df = df.rename(columns=renombrar_cols)
        return df
    except Exception as e:
        st.warning(f"Esperando nuevos registros en Google Sheets... ({e})")
        return pd.DataFrame()


st.title("📡 Sistema de Control y Retroalimentación de Terreno")
st.markdown("Plataforma de gestión de trabajos, resguardo y causas de fallos.")

menu = st.sidebar.selectbox(
    "Menú Principal",
    [
        "Registrar Trabajo (Formulario)",
        "Panel de Control y Gráficos",
        "Perfil del Técnico",
    ],
)

# ---------------------------------------------------------
# PESTAÑA 1: REGISTRAR TRABAJO (Google Form)
# ---------------------------------------------------------
if menu == "Registrar Trabajo (Formulario)":
    st.header("📝 Formulario de Trabajo en Terreno")
    st.caption(
        "Ingrese el reporte del trabajo. Los datos quedarán guardados permanentemente en Google Sheets."
    )

    # Renderiza el formulario interactivo
    components.iframe(URL_GOOGLE_FORM, height=850, scrolling=True)

# ---------------------------------------------------------
# PESTAÑA 2: PANEL DE CONTROL Y GRÁFICOS
# ---------------------------------------------------------
elif menu == "Panel de Control y Gráficos":
    st.header("📊 Panel General, Gráficos y Retroalimentación")

    df = cargar_datos()

    if df.empty or len(df) == 0:
        st.info("Aún no hay registros guardados en la hoja de cálculo.")
    else:
        total = len(df)
        exitosos = (
            len(df[df["Estado_Trabajo"] == "Sí"])
            if "Estado_Trabajo" in df.columns
            else 0
        )
        fallidos = (
            len(df[df["Estado_Trabajo"] == "No"])
            if "Estado_Trabajo" in df.columns
            else 0
        )

        m1, m2, m3 = st.columns(3)
        m1.metric("Total Trabajos Registrados", total)
        m2.metric("Realizados con Éxito", exitosos)
        m3.metric("No Realizados (Fallos)", fallidos)

        st.divider()

        st.subheader("📈 Distribución Visual de Resultados")
        g_col1, g_col2 = st.columns(2)

        with g_col1:
            if "Estado_Trabajo" in df.columns:
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
            if "Estado_Trabajo" in df.columns and "Categoria_Fallo" in df.columns:
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
                    st.info(
                        "No hay trabajos fallidos registrados para mostrar causas."
                    )

        st.divider()

        st.subheader("📋 Consolidado de Trabajos (Google Sheets en Vivo)")
        st.dataframe(df, use_container_width=True)

        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Descargar Reporte Consolidado (Excel/CSV)",
            data=csv_data,
            file_name="reporte_trabajos_terreno.csv",
            mime="text/csv",
        )

        st.divider()

        st.subheader("🔎 Retroalimentación por IDS (Jefe de Implementación)")
        if "IDS" in df.columns:
            ids_unicos = df["IDS"].dropna().unique()
            if len(ids_unicos) > 0:
                ids_seleccionado = st.selectbox(
                    "Seleccione un IDS para revisar fallos asociados:",
                    ids_unicos,
                )

                df_ids = df[df["IDS"] == ids_seleccionado]
                fallos_ids = (
                    df_ids[df_ids["Estado_Trabajo"] == "No"]
                    if "Estado_Trabajo" in df_ids.columns
                    else pd.DataFrame()
                )

                st.write(
                    f"**Resumen para {ids_seleccionado}:** Total asignados: {len(df_ids)} | Trabajos con problema: {len(fallos_ids)}"
                )

                if not fallos_ids.empty:
                    for idx, row in fallos_ids.iterrows():
                        tec_val = row.get("Tecnico", "N/A")
                        op_val = row.get("Operador_Red", "N/A")
                        cat_val = row.get("Categoria_Fallo", "N/A")
                        det_val = row.get("Detalle_Fallo", "N/A")
                        ord_val = row.get("Orden_Trabajo", "N/A")
                        st.markdown(
                            f"- **Orden {ord_val}** (Técnico: {tec_val} | Operador: {op_val}): "
                            f"*{cat_val}* — **Origen:** {det_val}"
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

    if df.empty or len(df) == 0:
        st.info("Aún no hay datos para mostrar perfiles de técnicos.")
    else:
        if "Tecnico" in df.columns:
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
                    exi_tec = (
                        len(df_tec[df_tec["Estado_Trabajo"] == "Sí"])
                        if "Estado_Trabajo" in df_tec.columns
                        else 0
                    )
                    fal_tec = tot_tec - exi_tec

                    st.markdown(f"**Total Trabajos:** {tot_tec}")
                    st.markdown(f"✅ **Exitosos:** {exi_tec}")
                    st.markdown(f"❌ **Fallidos:** {fal_tec}")

                with card_col2:
                    st.subheader("📊 Análisis de Desempeño (Gráficos Circulares)")
                    pie_col1, pie_col2 = st.columns(2)

                    with pie_col1:
                        if "Estado_Trabajo" in df_tec.columns:
                            fig_tec_estado = px.pie(
                                df_tec,
                                names="Estado_Trabajo",
                                title="Proporción Éxito vs. Fallos",
                                color="Estado_Trabajo",
                                color_discrete_map={
                                    "Sí": "#2ecc71",
                                    "No": "#e74c3c",
                                },
                                hole=0.4,
                            )
                            st.plotly_chart(
                                fig_tec_estado, use_container_width=True
                            )

                    with pie_col2:
                        if "Tipo_Trabajo" in df_tec.columns:
                            fig_tec_tipos = px.pie(
                                df_tec,
                                names="Tipo_Trabajo",
                                title="Tipos de Trabajos Asignados",
                                hole=0.4,
                            )
                            st.plotly_chart(
                                fig_tec_tipos, use_container_width=True
                            )

                st.divider()

                st.subheader("📋 Historial de Trabajos de este Técnico")
                cols_mostrar = [
                    c
                    for c in [
                        "Fecha_Registro",
                        "Orden_Trabajo",
                        "Tipo_Trabajo",
                        "Estado_Trabajo",
                        "Categoria_Fallo",
                        "Detalle_Fallo",
                        "Estado_Equipamiento",
                    ]
                    if c in df_tec.columns
                ]
                st.dataframe(df_tec[cols_mostrar], use_container_width=True)