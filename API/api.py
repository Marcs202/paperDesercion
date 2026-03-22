from flask import Flask, request, jsonify
import joblib
import pandas as pd

# Crear instancia de la aplicacion Flask
app = Flask(__name__)

# Cargar el modelo y las columnas al iniciar el servidor
# Esto ocurre una sola vez cuando se inicia la API
print("Cargando modelo...")
model = joblib.load('modelo_final_desercion.pkl')
feature_columns = joblib.load('feature_columns.pkl')
print("Modelo cargado exitosamente")

# Variables enteras y decimales del modelo
INT_FIELDS = ['IDCampus', 'Sexo', 'TotalMateriasInscritas_Anio1',
              'TotalMateriasAprobadas_Anio1', 'TotalMateriasReprobadas_Anio1']
FLOAT_FIELDS = ['TasaAprobacion_Anio1', 'PromedioGeneral_Anio1',
                'AvanceCarrera_FinAnio1', 'IRE_Total']
REQUIRED_FIELDS = INT_FIELDS + FLOAT_FIELDS


def prepare_input(data):
    """
    Prepara los datos de entrada para que coincidan con el formato
    esperado por el modelo entrenado.

    Args:
        data: Diccionario con los datos del estudiante

    Returns:
        DataFrame con las columnas en el orden correcto
    """
    # Convertir diccionario a DataFrame
    df = pd.DataFrame([data])

    # Forzar tipos de datos correctos
    for col in INT_FIELDS:
        df[col] = df[col].astype(int)
    for col in FLOAT_FIELDS:
        df[col] = df[col].astype(float)

    # Mantener solo las columnas en el orden correcto
    df = df[feature_columns]

    return df


# Ruta principal - endpoint para predicciones
@app.route('/predict', methods=['POST'])
def predict():
    """
    Endpoint principal para realizar predicciones.

    Espera un JSON con los datos del estudiante.
    Retorna un JSON con la prediccion y probabilidades.

    Metodo: POST
    Content-Type: application/json
    """
    try:
        # Obtener datos del request (JSON enviado por el cliente)
        data = request.get_json()

        # Validar que todos los campos requeridos esten presentes
        for field in REQUIRED_FIELDS:
            if field not in data:
                # Retornar error 400 (Bad Request) si falta algun campo
                return jsonify({
                    'error': f'Campo requerido faltante: {field}',
                    'campos_requeridos': REQUIRED_FIELDS
                }), 400

        # Preparar datos para el modelo
        input_df = prepare_input(data)

        # Realizar prediccion (0 = Continua estudios, 1 = Riesgo de desercion)
        prediction = model.predict(input_df)[0]

        # Obtener probabilidades [prob_retencion, prob_desercion]
        probability = model.predict_proba(input_df)[0]

        # Construir respuesta
        result = {
            'prediction': int(prediction),
            'prediction_label': 'Riesgo de deserción' if prediction == 1 else 'Continúa estudios',
            'probabilidad_desercion': float(probability[1]),
            'probabilidad_retencion': float(probability[0])
        }

        # Retornar respuesta exitosa (codigo 200)
        return jsonify(result), 200

    except Exception as e:
        # Capturar cualquier error y retornarlo como JSON
        # Codigo 500 = Internal Server Error
        return jsonify({
            'error': 'Error interno del servidor',
            'detalles': str(e)
        }), 500


# Ruta de health check - para verificar que el servidor esta funcionando
@app.route('/health', methods=['GET'])
def health():
    """
    Endpoint para verificar el estado del servidor.

    Metodo: GET
    Retorna: JSON con status healthy
    """
    return jsonify({
        'status': 'healthy',
        'modelo': 'Sistema Predictivo de Deserción Estudiantil',
        'version': '1.0'
    }), 200


# Ruta de informacion - describe los campos esperados
@app.route('/info', methods=['GET'])
def info():
    """
    Endpoint que retorna informacion sobre la API.

    Metodo: GET
    Retorna: JSON con informacion de uso
    """
    return jsonify({
        'nombre': 'API de Predicción de Deserción Estudiantil',
        'version': '1.0',
        'endpoints': {
            '/predict': {
                'metodo': 'POST',
                'descripcion': 'Realizar predicción de deserción estudiantil',
                'campos_requeridos': {
                    'IDCampus': 'int (1=Soyapango, 2=Antiguo Cuscatlán, 9=Virtual)',
                    'Sexo': 'int (1=Masculino, 2=Femenino)',
                    'TotalMateriasInscritas_Anio1': 'int - Total de materias inscritas en el primer año',
                    'TotalMateriasAprobadas_Anio1': 'int - Total de materias aprobadas en el primer año',
                    'TotalMateriasReprobadas_Anio1': 'int - Total de materias reprobadas en el primer año',
                    'TasaAprobacion_Anio1': 'float - Tasa de aprobación del primer año (0.0 a 1.0)',
                    'PromedioGeneral_Anio1': 'float - Promedio general del primer año',
                    'AvanceCarrera_FinAnio1': 'float - Porcentaje de avance de la carrera al fin del primer año (0.0 a 100)',
                    'IRE_Total': 'float - Índice de Rendimiento Estudiantil total'
                }
            },
            '/health': {
                'metodo': 'GET',
                'descripcion': 'Verificar estado del servidor'
            },
            '/info': {
                'metodo': 'GET',
                'descripcion': 'Obtener información de la API'
            }
        }
    }), 200


# Iniciar el servidor
if __name__ == '__main__':
    # host='0.0.0.0' permite acceso desde cualquier IP
    # port=5000 es el puerto por defecto
    # debug=True reinicia automaticamente al detectar cambios (solo para desarrollo)
    app.run(host='0.0.0.0', port=5000, debug=True)