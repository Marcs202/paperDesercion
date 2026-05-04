from flask import Flask, request, jsonify
import joblib
import pandas as pd
import time  # Importante para medir el tiempo
from waitress import serve
# Definir la clase APIModel (debe estar ANTES de cargar el .pkl)
class APIModel:
    def __init__(self, pipeline):
        self.pipeline = pipeline
    
    def _add_ire_malo(self, X):
        X = X.copy()
        X['IRE_malo'] = (X['IRE_Total'] - 5).clip(lower=0)
        X = X.drop(columns=['IRE_Total'])
        return X
    
    def predict(self, X):
        return self.pipeline.predict(self._add_ire_malo(X))
    
    def predict_proba(self, X):
        return self.pipeline.predict_proba(self._add_ire_malo(X))

app = Flask(__name__)

print("Cargando modelo...")
model = joblib.load('modelo_api_desercion.pkl')
print("Modelo cargado exitosamente")

REQUIRED_FIELDS = [
    'IdCampus', 'Sexo', 'TotalMateriasInscritas_Anio1',
    'TotalMateriasAprobadas_Anio1', 'TotalMateriasReprobadas_Anio1',
    'MateriasAprobadas_C2', 'TasaAprobacion_Anio1', 
    'PromedioGeneral_Anio1', 'AvanceCarrera_FinAnio1', 'IRE_Total'
]

@app.route('/predict', methods=['POST'])
def predict():
    # --- INICIO DE MEDICIÓN ---
    start_time = time.time() 
    
    try:
        data = request.get_json()

        # Validar campos faltantes
        faltantes = [field for field in REQUIRED_FIELDS if field not in data]
        if faltantes:
            return jsonify({
                'error': 'Faltan campos requeridos en el JSON',
                'campos_faltantes': faltantes
            }), 400

        # Crear DataFrame y predecir
        input_df = pd.DataFrame([data])[REQUIRED_FIELDS]
        prediction = model.predict(input_df)[0]
        probability = model.predict_proba(input_df)[0]

        # --- FIN DE MEDICIÓN ---
        end_time = time.time()
        # Tiempo en milisegundos
        # ... dentro de tu ruta /predict ...
        execution_time_ms = (end_time - start_time) * 1000 

        result = {
            'prediction': int(prediction),
            'prediction_label': 'Riesgo de deserción' if prediction == 1 else 'Continúa estudios',
            'probabilidad_desercion': float(probability[1]),
            'probabilidad_retencion': float(probability[0]),
            'stats': {
                # Enviamos el número puro para el test y el paper
                'server_process_time_val': round(execution_time_ms, 2),
                'display_time': f'{round(execution_time_ms, 2)} ms'
            }
        }
        
        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            'error': 'Error interno del servidor',
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
    serve(app, host='0.0.0.0', port=5000, threads=6)