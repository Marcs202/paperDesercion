# Módulo para entrenar modelo API con IRE_malo
def entrenar_y_guardar():
    """Entrena el modelo API con transformación IRE_malo y lo guarda"""
    import joblib
    from sklearn.metrics import f1_score
    from sklearn.compose import ColumnTransformer
    from sklearn.pipeline import Pipeline
    
    # Acceder a variables del scope global
    import sys
    frame = sys._getframe(1)
    X_train = frame.f_locals['X_train']
    X_test = frame.f_locals['X_test']
    y_train = frame.f_locals['y_train']
    y_test = frame.f_locals['y_test']
    numeric_transformer = frame.f_locals['numeric_transformer']
    categorical_transformer_low = frame.f_locals['categorical_transformer_low']
    best_models = frame.f_locals['best_models']
    final_model_name = frame.f_locals['final_model_name']
    
    print("="*80)
    print("GUARDANDO MODELO API CON TRANSFORMACION IRE_MALO")
    print("="*80)
    
    # Preparar datos
    columnas = ['IdCampus', 'Sexo', 'TotalMateriasInscritas_Anio1', 'TotalMateriasAprobadas_Anio1', 
                'TotalMateriasReprobadas_Anio1', 'MateriasAprobadas_C2', 'TasaAprobacion_Anio1', 
                'PromedioGeneral_Anio1', 'AvanceCarrera_FinAnio1', 'IRE_Total']
    
    X_train_ire = X_train[columnas].copy()
    X_test_ire = X_test[columnas].copy()
    
    # IRE_malo = max(0, IRE_Total - 5)
    X_train_ire['IRE_malo'] = (X_train_ire['IRE_Total'] - 5).clip(lower=0)
    X_test_ire['IRE_malo'] = (X_test_ire['IRE_Total'] - 5).clip(lower=0)
    print("OK: IRE_malo creado")
    
    numeric_feat = ['TotalMateriasInscritas_Anio1', 'TotalMateriasAprobadas_Anio1', 
                    'TotalMateriasReprobadas_Anio1', 'MateriasAprobadas_C2', 'TasaAprobacion_Anio1', 
                    'PromedioGeneral_Anio1', 'AvanceCarrera_FinAnio1', 'IRE_malo']
    cat_feat = ['IdCampus', 'Sexo']
    
    preprocessor_ire = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_feat),
            ('cat', categorical_transformer_low, cat_feat)
        ]
    )
    
    pipeline_ire = Pipeline(steps=[
        ('preprocessor', preprocessor_ire),
        ('classifier', best_models[final_model_name].named_steps['classifier'])
    ])
    
    print("Entrenando...")
    pipeline_ire.fit(X_train_ire, y_train)
    
    y_pred_ire = pipeline_ire.predict(X_test_ire)
    f1_ire = f1_score(y_test, y_pred_ire)
    print(f"F1-Score con IRE_malo: {f1_ire:.4f}")
    
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
    
    modelo_api_final = APIModel(pipeline_ire)
    joblib.dump(modelo_api_final, "modelo_api_desercion.pkl")
    
    print("OK: modelo_api_desercion.pkl guardado")
    print(f"    Transformacion: IRE_malo = max(0, IRE_Total - 5)")
    print(f"    F1-Score: {f1_ire:.4f}")
    print("="*80)
    
    return modelo_api_final, f1_ire
