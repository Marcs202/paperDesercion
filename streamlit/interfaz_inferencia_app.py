
import streamlit as st
import joblib
import pandas as pd
import os

# st.set_page_config debe ser la primera llamada de Streamlit
st.set_page_config(
    page_title="Predicción de Deserción Estudiantil",
    page_icon="🎓",
    layout="centered"
)

@st.cache_resource
def load_model():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    model = joblib.load(os.path.join(BASE_DIR, 'modelo_final_desercion.pkl'))
    feature_columns = joblib.load(os.path.join(BASE_DIR, 'feature_columns.pkl'))
    # Valores por defecto (medianas/modas) para columnas que el usuario no llena
    defaults_path = os.path.join(BASE_DIR, 'feature_defaults.pkl')
    if os.path.exists(defaults_path):
        feature_defaults = joblib.load(defaults_path)
    else:
        feature_defaults = {}
    return model, feature_columns, feature_defaults

try:
    model, feature_columns, feature_defaults = load_model()
    model_name = "Modelo Final Deserción"
except FileNotFoundError:
    st.error("No se encontraron los archivos del modelo (modelo_final_desercion.pkl, feature_columns.pkl).")
    st.stop()

st.title("Predicción de Deserción Estudiantil")
st.write(f"Modelo: **{model_name}** (Mejor Modelo Entrenado)")
st.divider()
st.subheader("Ingrese los datos del estudiante")

# ── Todas las columnas originales que el Pipeline espera (sin Carnet ni Deserto) ──
ALL_COLUMNS = [
    "Carrera", "Plan", "IdCampus", "Sexo", "AnioIngreso", "CicloIngreso",
    "InstitucionBach", "TieneBeca", "PorcentajeBeca_Promedio",
    "MateriasInscritas_C1", "MateriasAprobadas_C1", "MateriasReprobadas_C1",
    "TasaAprobacion_C1", "PromedioCiclo_C1",
    "MateriasInscritas_C2", "MateriasAprobadas_C2", "MateriasReprobadas_C2",
    "TasaAprobacion_C2", "PromedioCiclo_C2",
    "TotalMateriasInscritas_Anio1", "TotalMateriasAprobadas_Anio1",
    "TotalMateriasReprobadas_Anio1", "TasaAprobacion_Anio1",
    "PromedioGeneral_Anio1", "AvanceCarrera_FinAnio1", "PAES_Score",
    "CantInsolvencias_Recurrentes", "CantRetirosParciales", "CantRetirosTotales",
    "CantCambiosCarrera",
    "Ind_PAES", "Ind_CUM", "Ind_Avance", "Ind_Solvencia",
    "Ind_RetiroParcial", "Ind_RetiroTotal", "Ind_CambioCarrera",
    "Ind_Reprobacion", "Ind_BrechaDesercion", "IRE_Total",
]

user_input = {}

with st.form("form_prediccion"):

    # ── Sección 1: Datos Generales del Estudiante ──
    with st.expander(" Datos Generales del Estudiante", expanded=False):
        g1, g2 = st.columns(2)
        with g1:
           # user_input["Carrera"] = st.number_input("Código de Carrera", value=0, step=1)
            #user_input["Plan"] = st.number_input("Código de Plan", value=0, step=1)
            user_input["IdCampus"] = st.number_input("ID Campus", value=0, step=1)
            user_input["Sexo"] = st.selectbox("Sexo", [1, 2], format_func=lambda x: "Masculino" if x == 1 else "Femenino")
        with g2:
            pass
            #user_input["AnioIngreso"] = st.number_input("Año de Ingreso", value=2024, step=1)
            #user_input["CicloIngreso"] = st.selectbox("Ciclo de Ingreso", [1, 2])
            #user_input["InstitucionBach"] = st.number_input("Código Institución Bachillerato", value=0, step=1)
            #user_input["PAES_Score"] = st.number_input("Puntaje PAES", value=0.0, step=0.01, format="%.2f")

    # ── Sección 3: Rendimiento Ciclo 1 (comentada - no se usa para predicción) ──
    # with st.expander(" Rendimiento Académico - Ciclo 1", expanded=False):
    #     r1, r2 = st.columns(2)
    #     with r1:
    #         user_input["MateriasInscritas_C1"] = st.number_input("Materias Inscritas C1", value=0, step=1)
    #         user_input["MateriasAprobadas_C1"] = st.number_input("Materias Aprobadas C1", value=0, step=1)
    #         user_input["MateriasReprobadas_C1"] = st.number_input("Materias Reprobadas C1", value=0, step=1)
    #     with r2:
    #         user_input["TasaAprobacion_C1"] = st.number_input("Tasa Aprobación C1", value=0.0, step=0.01, format="%.2f")
    #         user_input["PromedioCiclo_C1"] = st.number_input("Promedio Ciclo 1", value=0.0, step=0.01, format="%.2f")

    # ── Sección 4: Rendimiento Ciclo 2 (comentada - no se usa para predicción) ──
    # with st.expander(" Rendimiento Académico - Ciclo 2", expanded=False):
    #     s1, s2 = st.columns(2)
    #     with s1:
    #         user_input["MateriasInscritas_C2"] = st.number_input("Materias Inscritas C2", value=0, step=1)
    #         user_input["MateriasAprobadas_C2"] = st.number_input("Materias Aprobadas C2", value=0, step=1)
    #         user_input["MateriasReprobadas_C2"] = st.number_input("Materias Reprobadas C2", value=0, step=1)
    #     with s2:
    #         user_input["TasaAprobacion_C2"] = st.number_input("Tasa Aprobación C2", value=0.0, step=0.01, format="%.2f")
    #         user_input["PromedioCiclo_C2"] = st.number_input("Promedio Ciclo 2", value=0.0, step=0.01, format="%.2f")

    # ── Sección 5: Resumen Año 1 ──
    with st.expander(" Resumen Académico Año 1", expanded=False):
        a1, a2 = st.columns(2)
        with a1:
            user_input["TotalMateriasInscritas_Anio1"] = st.number_input("Total Materias Inscritas Año 1", value=0, step=1)
            user_input["TotalMateriasAprobadas_Anio1"] = st.number_input("Total Materias Aprobadas Año 1", value=0, step=1)
            user_input["TotalMateriasReprobadas_Anio1"] = st.number_input("Total Materias Reprobadas Año 1", value=0, step=1)
            user_input["TasaAprobacion_Anio1"] = st.number_input("Tasa Aprobación Año 1", value=0.0, step=0.01, format="%.2f")
        with a2:
            user_input["PromedioGeneral_Anio1"] = st.number_input("Promedio General Año 1", value=0.0, step=0.01, format="%.2f")
            user_input["AvanceCarrera_FinAnio1"] = st.number_input("Avance de Carrera Fin Año 1 (%)", value=0.0, step=0.01, format="%.2f")
            user_input["IRE_Total"] = st.number_input("Índice de Rendimiento Estudiantil (IRE Total)", value=0, step=1)

    # ── Sección 6: Becas y Retiros (comentada - no se usa para predicción) ──
    # with st.expander(" Becas, Retiros e Insolvencias", expanded=False):
    #     b1, b2 = st.columns(2)
    #     with b1:
    #         user_input["TieneBeca"] = st.selectbox("¿Tiene Beca?", [0, 1], format_func=lambda x: "Sí" if x == 1 else "No")
    #         user_input["PorcentajeBeca_Promedio"] = st.number_input("Porcentaje Beca Promedio", value=0.0, step=0.01, format="%.2f")
    #         user_input["CantRetirosParciales"] = st.number_input("Cantidad de Retiros Parciales", value=0, step=1)
    #         user_input["CantRetirosTotales"] = st.number_input("Cantidad Retiros Totales", value=0, step=1)
    #     with b2:
    #         user_input["CantInsolvencias_Recurrentes"] = st.number_input("Insolvencias Recurrentes", value=0, step=1)
    #         user_input["CantCambiosCarrera"] = st.number_input("Cantidad Cambios de Carrera", value=0, step=1)

    # ── Sección 7: Indicadores IRE (comentada - no se usa para predicción) ──
    # with st.expander(" Indicadores IRE", expanded=False):
    #     i1, i2, i3 = st.columns(3)
    #     bin_labels = {
    #         "Ind_PAES": "PAES", "Ind_CUM": "CUM", "Ind_Avance": "Avance",
    #         "Ind_Solvencia": "Solvencia", "Ind_RetiroParcial": "Retiro Parcial",
    #         "Ind_RetiroTotal": "Retiro Total", "Ind_CambioCarrera": "Cambio Carrera",
    #         "Ind_Reprobacion": "Reprobación", "Ind_BrechaDesercion": "Brecha Deserción",
    #     }
    #     bin_cols = [i1, i2, i3]
    #     for idx, (key, label) in enumerate(bin_labels.items()):
    #         with bin_cols[idx % 3]:
    #             user_input[key] = st.selectbox(f"Ind. {label}", [0, 1], format_func=lambda x: "Sí" if x == 1 else "No", key=key)

    submitted = st.form_submit_button("Predecir Deserción", type="primary")


if submitted:
    try:
        # Construir DataFrame: usa el valor del usuario si existe, si no usa la mediana/moda del dataset
        input_df = pd.DataFrame([{col: user_input.get(col, feature_defaults.get(col, 0)) for col in ALL_COLUMNS}])
        prediction = model.predict(input_df)[0]
        probability = model.predict_proba(input_df)[0]

        st.success("Predicción completada correctamente")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Resultado", "DESERTA" if prediction == 1 else "NO DESERTA")
        with col2:
            st.metric("Prob. Deserción", f"{probability[1]:.1%}")
        with col3:
            st.metric("Prob. Permanencia", f"{probability[0]:.1%}")
        if prediction == 1:
            st.error(" ALERTA: Este estudiante tiene alta probabilidad de desertar. Se recomienda intervención temprana.")
        else:
            st.info("Este estudiante tiene baja probabilidad de desertar.")
        st.divider()
        st.subheader("Datos Ingresados")
        st.dataframe(input_df, use_container_width=True)
    except Exception as e:
        st.error(f"Error al realizar la predicción: {str(e)}")
        st.info("Verifique que los archivos modelo_final_desercion.pkl y feature_columns.pkl estén en el directorio.")

st.divider()
st.caption(f"Modelo entrenado: {model_name}")