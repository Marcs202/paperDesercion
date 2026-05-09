from flask import Flask, request, jsonify
import joblib
import pandas as pd

# Crear instancia de la aplicación Flask
app = Flask(__name__)

# Cargar el modelo 
print("Cargando modelo...")
model = joblib.load('modelo_api_desercion.pkl')
print("Modelo cargado exitosamente")

# Las 10 columnas exactas que espera el modelo ligero
REQUIRED_FIELDS = [
    'IdCampus', 
    'Sexo', 
    'TotalMateriasInscritas_Anio1',
    'TotalMateriasAprobadas_Anio1', 
    'TotalMateriasReprobadas_Anio1',
    'MateriasAprobadas_C2',
    'TasaAprobacion_Anio1', 
    'PromedioGeneral_Anio1',
    'AvanceCarrera_FinAnio1', 
    'IRE_Total'
]

# Ruta principal - endpoint para predicciones
@app.route('/predict', methods=['POST'])
def predict():
    """
    Endpoint principal para realizar predicciones.
    Espera un JSON con los 10 datos del estudiante.
    """
    try:
        data = request.get_json()

        # Validar qué campos faltan exactamente
        faltantes = [field for field in REQUIRED_FIELDS if field not in data]
        if faltantes:
            return jsonify({
                'error': 'Faltan campos requeridos en el JSON',
                'campos_faltantes': faltantes,
                'campos_requeridos': REQUIRED_FIELDS
            }), 400

        # Crear DataFrame directamente con el orden correcto
        # El pipeline de scikit-learn se encargará del One-Hot y el escalado
        input_df = pd.DataFrame([data])[REQUIRED_FIELDS]

        # Realizar predicción
        prediction = model.predict(input_df)[0]
        probability = model.predict_proba(input_df)[0]

        # Construir respuesta
        result = {
            'prediction': int(prediction),
            'prediction_label': 'Riesgo de deserción' if prediction == 1 else 'Continúa estudios',
            'probabilidad_desercion': float(probability[1]),
            'probabilidad_retencion': float(probability[0])
        }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            'error': 'Error interno del servidor al procesar la predicción',
            'detalles': str(e)
        }), 500


# Ruta de health check - para verificar que el servidor está funcionando
@app.route('/health', methods=['GET'])
def health():
    """
    Endpoint para verificar el estado del servidor.
    """
    return jsonify({
        'status': 'healthy',
        'modelo': 'Sistema Predictivo de Deserción Estudiantil',
        'version': '1.0'
    }), 200


# Ruta de información - describe los campos esperados
@app.route('/info', methods=['GET'])
def info():
    """
    Endpoint que retorna información sobre la API y su uso.
    """
    return jsonify({
        'nombre': 'API de Predicción de Deserción Estudiantil',
        'version': '1.0',
        'endpoints': {
            '/predict': {
                'metodo': 'POST',
                'descripcion': 'Realizar predicción de deserción estudiantil',
                'campos_requeridos': {
                    'IdCampus': 'int (1=Soyapango, 2=Antiguo Cuscatlán, 9=Virtual)',
                    'Sexo': 'int (102301=Masculino, 102302=Femenino)',
                    'TotalMateriasInscritas_Anio1': 'int - Total de materias inscritas en el primer año',
                    'TotalMateriasAprobadas_Anio1': 'int - Total de materias aprobadas en el primer año',
                    'TotalMateriasReprobadas_Anio1': 'int - Total de materias reprobadas en el primer año',
                    'MateriasAprobadas_C2': 'int - Total de materias aprobadas específicamente en el ciclo 2',
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
                'descripcion': 'Obtener esta información de la API'
            }
        }
    }), 200


# Iniciar el servidor
if __name__ == '__main__':
    # host='0.0.0.0' permite acceso desde cualquier IP
    # port=5000 es el puerto por defecto
    app.run(host='0.0.0.0', port=5000, debug=True)