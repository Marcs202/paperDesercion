# API de Predicción de Deserción Estudiantil

Sistema predictivo basado en Machine Learning que estima la probabilidad de deserción de un estudiante universitario a partir de indicadores académicos de su primer año.

---

## Tabla de Contenidos

- [Requisitos Previos](#requisitos-previos)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Instalación](#instalación)
- [Ejecución](#ejecución)
- [Endpoints](#endpoints)
  - [POST /predict](#post-predict)
  - [GET /health](#get-health)
  - [GET /info](#get-info)
- [Variables de Entrada](#variables-de-entrada)
- [Códigos de Respuesta HTTP](#códigos-de-respuesta-http)
- [Ejemplos de Uso](#ejemplos-de-uso)

---

## Requisitos Previos

- **Python** 3.8 o superior
- **pip** (gestor de paquetes de Python)

### Dependencias

| Paquete    | Descripción                                  |
|------------|----------------------------------------------|
| `flask`    | Framework web para crear la API REST         |
| `joblib`   | Serialización/deserialización del modelo .pkl|
| `pandas`   | Manipulación de datos tabulares              |

---

## Estructura del Proyecto

```
API/
├── api.py                        # Código fuente de la API
├── modelo_final_desercion.pkl    # Modelo de Machine Learning entrenado
├── feature_columns.pkl           # Orden de columnas esperado por el modelo
└── README.md                     # Esta documentación
```

---

## Instalación

1. **Clonar o descargar** el proyecto en tu máquina local.

2. **Crear un entorno virtual** (recomendado):

   ```bash
   python -m venv venv
   ```

3. **Activar el entorno virtual**:

   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux / macOS:
     ```bash
     source venv/bin/activate
     ```

4. **Instalar las dependencias**:

   ```bash
   pip install flask joblib pandas scikit-learn
   ```

---

## Ejecución

Desde la carpeta `API/`, ejecutar:

```bash
python api.py
```

El servidor se iniciará en `http://0.0.0.0:5000`. Verás en consola:

```
Cargando modelo...
Modelo cargado exitosamente
 * Running on http://0.0.0.0:5000
```

> **Nota:** El modo `debug=True` está habilitado por defecto para desarrollo. Desactívalo en producción.

---

## Endpoints

### POST /predict

Realiza una predicción de deserción estudiantil.

| Propiedad      | Valor                        |
|----------------|------------------------------|
| **URL**        | `/predict`                   |
| **Método**     | `POST`                       |
| **Content-Type** | `application/json`         |

#### Cuerpo de la solicitud (JSON)

Se deben enviar **obligatoriamente** las 9 variables del modelo:

```json
{
  "IDCampus": 2,
  "Sexo": 1,
  "TotalMateriasInscritas_Anio1": 10,
  "TotalMateriasAprobadas_Anio1": 7,
  "TotalMateriasReprobadas_Anio1": 3,
  "TasaAprobacion_Anio1": 0.7,
  "PromedioGeneral_Anio1": 7.5,
  "AvanceCarrera_FinAnio1": 18.5,
  "IRE_Total": 1
}
```

#### Respuesta exitosa (200)

```json
{
  "prediction": 0,
  "prediction_label": "Continúa estudios",
  "probabilidad_desercion": 0.23,
  "probabilidad_retencion": 0.77
}
```

| Campo                    | Tipo   | Descripción                                                    |
|--------------------------|--------|----------------------------------------------------------------|
| `prediction`             | int    | Valor numérico de la predicción (`0` o `1`)                    |
| `prediction_label`       | string | Etiqueta legible: `"Riesgo de deserción"` o `"Continúa estudios"` |
| `probabilidad_desercion` | float  | Probabilidad estimada de que el estudiante deserte (0.0 a 1.0)|
| `probabilidad_retencion` | float  | Probabilidad estimada de que el estudiante continúe (0.0 a 1.0)|

#### Respuesta de error — campo faltante (400)

```json
{
  "error": "Campo requerido faltante: Sexo",
  "campos_requeridos": [
    "IDCampus", "Sexo", "TotalMateriasInscritas_Anio1",
    "TotalMateriasAprobadas_Anio1", "TotalMateriasReprobadas_Anio1",
    "TasaAprobacion_Anio1", "PromedioGeneral_Anio1",
    "AvanceCarrera_FinAnio1", "IRE_Total"
  ]
}
```

#### Respuesta de error — error interno (500)

```json
{
  "error": "Error interno del servidor",
  "detalles": "Descripción técnica del error"
}
```

---

### GET /health

Verifica que el servidor esté funcionando correctamente.

| Propiedad  | Valor      |
|------------|------------|
| **URL**    | `/health`  |
| **Método** | `GET`      |

#### Respuesta (200)

```json
{
  "status": "healthy",
  "modelo": "Sistema Predictivo de Deserción Estudiantil",
  "version": "1.0"
}
```

---

### GET /info

Retorna la documentación de uso de la API en formato JSON, incluyendo los campos requeridos y sus tipos.

| Propiedad  | Valor    |
|------------|----------|
| **URL**    | `/info`  |
| **Método** | `GET`    |

#### Respuesta (200)

Devuelve un JSON con la descripción completa de todos los endpoints y las variables esperadas.

---

## Variables de Entrada

Las 9 variables que el modelo requiere para realizar la predicción:

### Variables enteras (`int`)

| Variable                          | Descripción                                      | Valores permitidos                                   |
|-----------------------------------|--------------------------------------------------|------------------------------------------------------|
| `IDCampus`                        | Identificador del campus universitario           | `1` = Soyapango, `2` = Antiguo Cuscatlán, `9` = Virtual |
| `Sexo`                            | Sexo del estudiante                              | `1` = Masculino, `2` = Femenino                      |
| `TotalMateriasInscritas_Anio1`    | Cantidad de materias inscritas en el primer año  | Entero positivo                                      |
| `TotalMateriasAprobadas_Anio1`    | Cantidad de materias aprobadas en el primer año  | Entero ≥ 0                                           |
| `TotalMateriasReprobadas_Anio1`   | Cantidad de materias reprobadas en el primer año | Entero ≥ 0                                           |

### Variables decimales (`float`)

| Variable                  | Descripción                                              | Rango típico   |
|---------------------------|----------------------------------------------------------|----------------|
| `TasaAprobacion_Anio1`   | Tasa de aprobación del primer año                        | 0.0 a 1.0      |
| `PromedioGeneral_Anio1`  | Promedio general de notas del primer año                 | 0.0 a 10.0     |
| `AvanceCarrera_FinAnio1` | Porcentaje de avance de la carrera al final del primer año | 0.0 a 100.0  |
| `IRE_Total`              | Índice de Rendimiento Estudiantil total                  | 0.0 a 6.0      |

---

## Códigos de Respuesta HTTP

| Código | Significado                | Causa                                        |
|--------|----------------------------|----------------------------------------------|
| `200`  | OK                         | Solicitud procesada exitosamente             |
| `400`  | Bad Request                | Falta uno o más campos requeridos en el JSON |
| `500`  | Internal Server Error      | Error inesperado en el servidor              |

---

## Ejemplos de Uso

### Con cURL

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "IDCampus": 1,
    "Sexo": 2,
    "TotalMateriasInscritas_Anio1": 12,
    "TotalMateriasAprobadas_Anio1": 4,
    "TotalMateriasReprobadas_Anio1": 8,
    "TasaAprobacion_Anio1": 0.33,
    "PromedioGeneral_Anio1": 5.2,
    "AvanceCarrera_FinAnio1": 10.0,
    "IRE_Total": 0.30
  }'
```

### Con Python (requests)

```python
import requests

url = "http://localhost:5000/predict"

datos_estudiante = {
    "IDCampus": 2,
    "Sexo": 1,
    "TotalMateriasInscritas_Anio1": 10,
    "TotalMateriasAprobadas_Anio1": 9,
    "TotalMateriasReprobadas_Anio1": 1,
    "TasaAprobacion_Anio1": 0.9,
    "PromedioGeneral_Anio1": 8.5,
    "AvanceCarrera_FinAnio1": 25.0,
    "IRE_Total": 0.85
}

respuesta = requests.post(url, json=datos_estudiante)
print(respuesta.json())
```

**Salida esperada:**

```json
{
  "prediction": 0,
  "prediction_label": "Continúa estudios",
  "probabilidad_desercion": 0.12,
  "probabilidad_retencion": 0.88
}
```

### Con PowerShell

```powershell
$body = @{
    IDCampus = 9
    Sexo = 1
    TotalMateriasInscritas_Anio1 = 8
    TotalMateriasAprobadas_Anio1 = 3
    TotalMateriasReprobadas_Anio1 = 5
    TasaAprobacion_Anio1 = 0.375
    PromedioGeneral_Anio1 = 5.8
    AvanceCarrera_FinAnio1 = 12.0
    IRE_Total = 0.40
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:5000/predict -Method Post -Body $body -ContentType "application/json"
```

### Verificar estado del servidor

```bash
curl http://localhost:5000/health
```

### Consultar información de la API

```bash
curl http://localhost:5000/info
```
