
import streamlit as st
import joblib
import pandas as pd

# st.set_page_config debe ser la primera llamada de Streamlit
st.set_page_config(
    page_title="Predicción de Deserción Estudiantil",
    page_icon="🎓",
    layout="centered"
)


@st.cache_resource
def load_model():
    model = joblib.load('modelo_final_desercion.pkl')
    feature_columns = joblib.load('feature_columns.pkl')
    return model, feature_columns

try:
    model, feature_columns = load_model()
    model_name = "Modelo Final Deserción"
except FileNotFoundError:
    st.error("No se encontraron los archivos del modelo (modelo_final_desercion.pkl, feature_columns.pkl).")
    st.stop()

st.title("Predicción de Deserción Estudiantil")
st.write(f"Modelo: **{model_name}** (entrenado y optimizado)")
st.divider()
st.subheader("Ingrese los datos requeridos para la predicción")

# Diccionario para mostrar nombres amigables y tipo de input
feature_labels = {
    'num__TotalMateriasAprobadas_Anio1': ("Total Materias Aprobadas Año 1", 'number'),
    'cat_low__Ind_Avance_0': ("¿No avanzó de año? (0=No, 1=Sí)", 'select'),
    'cat_low__Ind_Solvencia_1': ("¿Solvente en pagos? (0=No, 1=Sí)", 'select'),
    'num__TotalMateriasInscritas_Anio1': ("Total Materias Inscritas Año 1", 'number'),
    'num__MateriasAprobadas_C2': ("Materias Aprobadas Ciclo 2", 'number'),
    'num__AvanceCarrera_FinAnio1': ("% Avance Carrera al Final Año 1", 'number'),
    'num__TasaAprobacion_C2': ("Tasa de Aprobación Ciclo 2 (0-1)", 'number'),
    'cat_low__Ind_Avance_1': ("¿Avanzó de año? (0=No, 1=Sí)", 'select'),
    'cat_low__Ind_CambioCarrera_0': ("¿No cambió de carrera? (0=No, 1=Sí)", 'select'),
    'cat_low__CantCambiosCarrera_1': ("Cantidad de Cambios de Carrera = 1", 'select'),
    'cat_low__Ind_CambioCarrera_1': ("¿Cambió de carrera? (0=No, 1=Sí)", 'select'),
    'cat_low__CantCambiosCarrera_0': ("Cantidad de Cambios de Carrera = 0", 'select'),
    'cat_low__Ind_Solvencia_0': ("¿No es solvente en pagos? (0=No, 1=Sí)", 'select'),
    'num__MateriasInscritas_C2': ("Materias Inscritas Ciclo 2", 'number'),
    'num__PromedioCiclo_C2': ("Promedio Ciclo 2 (0-10)", 'number'),
}

user_input = {}

with st.form("form_prediccion"):
    for feat in feature_columns:
        label, tipo = feature_labels.get(feat, (feat, 'number'))
        if tipo == 'number':
            user_input[feat] = st.number_input(label, value=0.0, step=1.0 if 'Promedio' not in label and 'Tasa' not in label else 0.01)
        elif tipo == 'select':
            user_input[feat] = st.selectbox(label, [0, 1], format_func=lambda x: "Sí" if x == 1 else "No")
    submitted = st.form_submit_button("Predecir Deserción", type="primary")

if submitted:
    try:
        input_df = pd.DataFrame([user_input])[feature_columns]
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
st.caption(f"Modelo entrenado: {model_name} | Features: {', '.join(feature_columns)}")