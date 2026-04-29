#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para guardar el modelo API con transformación IRE_malo
Ejecutar desde Jupyter: %run save_api_model_ire_malo.py
"""

import joblib
from sklearn.metrics import f1_score

print("\n" + "="*80)
print("GUARDANDO MODELO API CON TRANSFORMACION IRE_MALO")
print("="*80)

# Usar variables locales que existen en el notebook
try:
    # Validar que existan los datos necesarios
    assert 'X_train' in locals(), "X_train no encontrado"
    assert 'X_test' in locals(), "X_test no encontrado"
    assert 'y_test' in locals(), "y_test no encontrado"
    
    # Preparar datos con IRE_malo
    columnas = ['IdCampus', 'Sexo', 'TotalMateriasInscritas_Anio1', 'TotalMateriasAprobadas_Anio1', 
                'TotalMateriasReprobadas_Anio1', 'MateriasAprobadas_C2', 'TasaAprobacion_Anio1', 
                'PromedioGeneral_Anio1', 'AvanceCarrera_FinAnio1', 'IRE_Total']
    
    X_train_ire = X_train[columnas].copy()
    X_test_ire = X_test[columnas].copy()
    
    # Crear IRE_malo = max(0, IRE_Total - 5)
    X_train_ire['IRE_malo'] = (X_train_ire['IRE_Total'] - 5).clip(lower=0)
    X_test_ire['IRE_malo'] = (X_test_ire['IRE_Total'] - 5).clip(lower=0)
    print("OK: IRE_malo creado: max(0, IRE_Total - 5)")
    
    # Features
    numeric_feat = ['TotalMateriasInscritas_Anio1', 'TotalMateriasAprobadas_Anio1', 
                    'TotalMateriasReprobadas_Anio1', 'MateriasAprobadas_C2', 'TasaAprobacion_Anio1', 
                    'PromedioGeneral_Anio1', 'AvanceCarrera_FinAnio1', 'IRE_malo']
    cat_feat = ['IdCampus', 'Sexo']
    
    # Preprocesador
    preprocessor_ire = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_feat),
            ('cat', categorical_transformer_low, cat_feat)
        ]
    )
    
    # Pipeline
    pipeline_ire = Pipeline(steps=[
        ('preprocessor', preprocessor_ire),
        ('classifier', best_models[final_model_name].named_steps['classifier'])
    ])
    
    print("Entrenando modelo...")
    pipeline_ire.fit(X_train_ire, y_train)
    
    # Evaluar
    y_pred_ire = pipeline_ire.predict(X_test_ire)
    f1_ire = f1_score(y_test, y_pred_ire)
    print(f"OK: F1-Score con IRE_malo: {f1_ire:.4f}")
    
    # Wrapper
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
    
    # Guardar
    modelo_api_final = APIModel(pipeline_ire)
    joblib.dump(modelo_api_final, "modelo_api_desercion.pkl")
    
    print("\n" + "="*80)
    print("EXITO: modelo_api_desercion.pkl guardado")
    print(f"  Transformacion: IRE_malo = max(0, IRE_Total - 5)")
    print(f"  F1-Score: {f1_ire:.4f}")
    print(f"  Wrapper automatico activo")
    print("="*80 + "\n")
    
except Exception as e:
    print(f"ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
