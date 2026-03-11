-- =========================================================
-- CREACIÓN DE TABLA DE FEATURES PARA MODELO DE DESERCIÓN
-- ENFOQUE: PRIMER AÑO ACADÉMICO (Ciclo 1 y 2) + INDICADORES IRE
-- Proyecto de Machine Learning Supervisado | 2026
-- =========================================================
USE GA;
GO

IF OBJECT_ID(N'dbo.DesercionEstudiantil_PrimerAnio', N'U') IS NOT NULL
    DROP TABLE dbo.DesercionEstudiantil_PrimerAnio;
GO

CREATE TABLE dbo.DesercionEstudiantil_PrimerAnio (
    Carnet VARCHAR(50) NOT NULL PRIMARY KEY,
    
    -- Identificación y Sociodemográfico
    Carrera VARCHAR(200) NULL,
    [Plan] VARCHAR(100) NULL,
    IdCampus INT NULL,
    Sexo VARCHAR(20) NULL,
    AnioIngreso INT NULL,
    CicloIngreso INT NULL,
    InstitucionBach VARCHAR(255) NULL,
    
    -- Económico (Primer Año)
    TieneBeca BIT DEFAULT 0,
    PorcentajeBeca_Promedio DECIMAL(5,2) NULL,
    
    -- === FEATURES DEL CICLO 1 ===
    MateriasInscritas_C1 INT NULL,
    MateriasAprobadas_C1 INT NULL,
    MateriasReprobadas_C1 INT NULL,
    TasaAprobacion_C1 DECIMAL(5,4) NULL,
    PromedioCiclo_C1 DECIMAL(9,2) NULL,
    
    -- === FEATURES DEL CICLO 2 ===
    MateriasInscritas_C2 INT NULL,
    MateriasAprobadas_C2 INT NULL,
    MateriasReprobadas_C2 INT NULL,
    TasaAprobacion_C2 DECIMAL(5,4) NULL,
    PromedioCiclo_C2 DECIMAL(9,2) NULL,
    
    -- === FEATURES AGREGADAS DEL PRIMER AÑO ===
    TotalMateriasInscritas_Anio1 INT NULL,
    TotalMateriasAprobadas_Anio1 INT NULL,
    TotalMateriasReprobadas_Anio1 INT NULL,
    TasaAprobacion_Anio1 DECIMAL(5,4) NULL,
    PromedioGeneral_Anio1 DECIMAL(9,2) NULL,
    
    -- Avance al finalizar primer año
    AvanceCarrera_FinAnio1 DECIMAL(5,2) NULL,
    
    -- === COMPONENTES DEL IRE (Optimizados y Filtrados) ===
    PAES_Score DECIMAL(18,2) NULL,
    CantInsolvencias_Recurrentes INT DEFAULT 0,
    CantRetirosParciales INT DEFAULT 0,
    CantRetirosTotales INT DEFAULT 0,
    CantCambiosCarrera INT DEFAULT 0,
    
    -- === INDICADORES BINARIOS IRE (0/1) ===
    Ind_PAES BIT DEFAULT 0,
    Ind_CUM BIT DEFAULT 0, 
    Ind_Avance BIT DEFAULT 0,
    Ind_Solvencia BIT DEFAULT 0,
    Ind_RetiroParcial BIT DEFAULT 0,
    Ind_RetiroTotal BIT DEFAULT 0,
    Ind_CambioCarrera BIT DEFAULT 0,
    Ind_Reprobacion BIT DEFAULT 0,
    Ind_BrechaDesercion BIT DEFAULT 0,
    
    -- VALOR FINAL IRE
    IRE_Total INT DEFAULT 0,
    
    -- === TARGET ===
    Deserto BIT NOT NULL  -- 1 = No se matriculó en segundo año, 0 = Continuó
);
GO

-- 1. Resumen académico por ciclo (ESTRICTAMENTE PRIMER AÑO)
WITH cte_inscr_summary AS (
    SELECT
        i.Carnet, i.Año AS Anio, i.Ciclo,
        MAX(i.Carrera) AS Carrera, MAX(i.Plan_) AS [Plan], MAX(i.IdCampus) AS IdCampus,
        COUNT(i.Asignatura) AS MateriasInscritas,
        COUNT(CASE WHEN UPPER(ISNULL(i.Resultado,'')) LIKE '%A%' THEN 1 END) AS MateriasAprobadas,
        COUNT(CASE WHEN UPPER(ISNULL(i.Resultado,'')) LIKE '%R%' THEN 1 END) AS MateriasReprobadas,
        CASE WHEN COUNT(*) = 0 THEN 0.0
             ELSE CAST(COUNT(CASE WHEN UPPER(ISNULL(i.Resultado,'')) LIKE '%A%' THEN 1 END) AS DECIMAL(9,4)) 
                  / CAST(NULLIF(COUNT(*), 0) AS DECIMAL(9,4))
        END AS TasaAprobacion,
        AVG(TRY_CAST(i.Calificacion AS DECIMAL(9,2))) AS PromedioCiclo
    FROM GA..Inscripciones AS i
    INNER JOIN GA..Alumno a ON i.Carnet = a.Carnet
    WHERE i.Año = a.AnioIngreso  
      AND i.Ciclo IN (1, 2)
      AND i.Año BETWEEN 2020 AND 2024
    GROUP BY i.Carnet, i.Año, i.Ciclo
),

-- 2. Pivotar datos por ciclo (C1 y C2)
cte_pivot_ciclos AS (
    SELECT
        Carnet, MAX(Carrera) AS Carrera, MAX([Plan]) AS [Plan], MAX(IdCampus) AS IdCampus,
        MAX(CASE WHEN Ciclo = 1 THEN MateriasInscritas END) AS MateriasInscritas_C1,
        MAX(CASE WHEN Ciclo = 1 THEN MateriasAprobadas END) AS MateriasAprobadas_C1,
        MAX(CASE WHEN Ciclo = 1 THEN MateriasReprobadas END) AS MateriasReprobadas_C1,
        MAX(CASE WHEN Ciclo = 1 THEN TasaAprobacion END) AS TasaAprobacion_C1,
        MAX(CASE WHEN Ciclo = 1 THEN PromedioCiclo END) AS PromedioCiclo_C1,
        
        MAX(CASE WHEN Ciclo = 2 THEN MateriasInscritas END) AS MateriasInscritas_C2,
        MAX(CASE WHEN Ciclo = 2 THEN MateriasAprobadas END) AS MateriasAprobadas_C2,
        MAX(CASE WHEN Ciclo = 2 THEN MateriasReprobadas END) AS MateriasReprobadas_C2,
        MAX(CASE WHEN Ciclo = 2 THEN TasaAprobacion END) AS TasaAprobacion_C2,
        MAX(CASE WHEN Ciclo = 2 THEN PromedioCiclo END) AS PromedioCiclo_C2,
        
        SUM(MateriasInscritas) AS TotalMateriasInscritas_Anio1,
        SUM(MateriasAprobadas) AS TotalMateriasAprobadas_Anio1,
        SUM(MateriasReprobadas) AS TotalMateriasReprobadas_Anio1
    FROM cte_inscr_summary
    GROUP BY Carnet
),

-- 3. FIX DUPLICADOS: Avance de carrera exacto a Diciembre de su primer año
cte_avance_carrera AS (
    SELECT 
        ac.Carnet,
        TRY_CAST(ac.AvanceCarrera AS DECIMAL(5,2)) AS AvanceCarrera,
        ROW_NUMBER() OVER (
            PARTITION BY ac.Carnet 
            ORDER BY CASE WHEN ac.FechaModificacion <= DATEFROMPARTS(a.AnioIngreso, 12, 31) THEN ac.FechaModificacion END DESC
        ) AS rn
    FROM GA..Alumnocarrera ac
    INNER JOIN GA..Alumno a ON ac.Carnet = a.Carnet
),

-- 4. Información de becas
cte_becas AS (
    SELECT 
        ab.CarnetBecado AS Carnet, 1 AS TieneBeca, AVG(rb.PorcentajeAranceles) AS PorcentajeBeca_Promedio
    FROM GA..PSAlumnosBecados ab
    INNER JOIN GA..PSRegistrosDeBecas rb ON ab.IdAlumnoBecado = rb.IdAlumnoBecado
    INNER JOIN GA..Alumno a ON ab.CarnetBecado = a.Carnet
    WHERE rb.Año = a.AnioIngreso AND rb.Ciclo IN (1, 2)
    GROUP BY ab.CarnetBecado
),

-- 5. Lógica de Solvencia
cte_solvencia AS (
    SELECT 
        a.Carnet, 
        COUNT(CASE WHEN pca.Mora > 0 THEN 1 END) AS CantInsolvencias
    FROM GA..Alumno a
    INNER JOIN VEN..VENClientes c 
        ON a.Carnet = c.Codigo  
    INNER JOIN VEN..VENPlanesPagosServicio pps 
        ON c.IdCliente = pps.IdCliente
    INNER JOIN VEN..VENPlanesCuotasArancel pca 
        ON pps.IdPlanPagoServicio = pca.IdPlanPagoServicio
    WHERE 
        pps.Anio = a.AnioIngreso 
    GROUP BY a.Carnet
),

-- 6. Lógica de Retiros
cte_retiros AS (
    SELECT 
        i.Carnet,
        COUNT(CASE WHEN i.Resultado = '1' THEN 1 END) AS RetirosParciales,
        COUNT(CASE WHEN i.Resultado = '2' THEN 1 END) AS RetirosTotales
    FROM GA..Inscripciones i
    INNER JOIN GA..Alumno a ON i.Carnet = a.Carnet
    WHERE i.Inscrita = 1 AND i.Resultado IN ('1', '2') AND i.Año = a.AnioIngreso 
    GROUP BY i.Carnet
),

-- 7. Cambios de Carrera
cte_cambios AS (
    SELECT c.Carnet, COUNT(DISTINCT c.CarreraN) AS CantCambios
    FROM GA..CambioCarrera c
    INNER JOIN GA..Alumno a ON c.Carnet = a.Carnet
    WHERE YEAR(ISNULL(c.FechaReg, DATEFROMPARTS(a.AnioIngreso, 1, 1))) = a.AnioIngreso
    GROUP BY c.Carnet
),

-- 8. Pensum
cte_pensum AS (
    SELECT Carrera, Plan_, COUNT(*) AS TotalMateriasPlan
    FROM GA..Pensum WHERE Obligatoria = 1
    GROUP BY Carrera, Plan_
),

-- 9. Determinar el Target
cte_desercion AS (
    SELECT DISTINCT
        i_anio1.Carnet,
        CASE WHEN i_anio2.Carnet IS NOT NULL THEN CAST(0 AS BIT) ELSE CAST(1 AS BIT) END AS Deserto
    FROM GA..Inscripciones i_anio1
    INNER JOIN GA..Alumno a ON i_anio1.Carnet = a.Carnet
    LEFT JOIN GA..Inscripciones i_anio2 
        ON i_anio1.Carnet = i_anio2.Carnet AND i_anio2.Año = a.AnioIngreso + 1 AND i_anio2.Ciclo = 1 
    WHERE i_anio1.Año = a.AnioIngreso AND i_anio1.Ciclo IN (1, 2) AND a.AnioIngreso BETWEEN 2020 AND 2024
)

-- 10. INSERCIÓN FINAL (Con CROSS APPLY para asegurar sincronización matemática perfecta)
INSERT INTO dbo.DesercionEstudiantil_PrimerAnio
SELECT 
    p.Carnet, p.Carrera, p.[Plan], p.IdCampus, per.Sexo, a.AnioIngreso, a.CicloIngreso, a.InstitucionBach,
    
    ISNULL(b.TieneBeca, 0) AS TieneBeca, b.PorcentajeBeca_Promedio,
    
    p.MateriasInscritas_C1, p.MateriasAprobadas_C1, p.MateriasReprobadas_C1, p.TasaAprobacion_C1, p.PromedioCiclo_C1,
    p.MateriasInscritas_C2, p.MateriasAprobadas_C2, p.MateriasReprobadas_C2, p.TasaAprobacion_C2, p.PromedioCiclo_C2,
    
    p.TotalMateriasInscritas_Anio1, p.TotalMateriasAprobadas_Anio1, p.TotalMateriasReprobadas_Anio1,
    
    CASE WHEN p.TotalMateriasInscritas_Anio1 = 0 THEN 0.0 ELSE CAST(p.TotalMateriasAprobadas_Anio1 AS DECIMAL(9,4)) / CAST(p.TotalMateriasInscritas_Anio1 AS DECIMAL(9,4)) END AS TasaAprobacion_Anio1,
    
    (ISNULL(p.PromedioCiclo_C1, 0) + ISNULL(p.PromedioCiclo_C2, 0)) / NULLIF((CASE WHEN p.PromedioCiclo_C1 IS NOT NULL THEN 1 ELSE 0 END + CASE WHEN p.PromedioCiclo_C2 IS NOT NULL THEN 1 ELSE 0 END), 0) AS PromedioGeneral_Anio1,
    
    ac.AvanceCarrera, 
    
    a.Paes, ISNULL(s.CantInsolvencias, 0), ISNULL(r.RetirosParciales, 0), ISNULL(r.RetirosTotales, 0), ISNULL(c.CantCambios, 0),
    
    -- Invocamos los indicadores calculados en el CROSS APPLY
    ire.Ind_PAES, ire.Ind_CUM, ire.Ind_Avance, ire.Ind_Solvencia, ire.Ind_RetiroParcial, ire.Ind_RetiroTotal, ire.Ind_CambioCarrera, ire.Ind_Reprobacion, ire.Ind_BrechaDesercion,
    
    -- La suma ahora es una suma limpia y directa de las columnas
    (ire.Ind_PAES + ire.Ind_CUM + ire.Ind_Avance + ire.Ind_Solvencia + ire.Ind_RetiroParcial + ire.Ind_RetiroTotal + ire.Ind_CambioCarrera + ire.Ind_Reprobacion + ire.Ind_BrechaDesercion) AS IRE_Total,
    
    d.Deserto

FROM cte_pivot_ciclos p
INNER JOIN GA..Alumno a ON p.Carnet = a.Carnet
INNER JOIN cte_desercion d ON p.Carnet = d.Carnet
LEFT JOIN AR..rhpersonas per ON a.IdPersona = per.IdPersona
LEFT JOIN cte_avance_carrera ac ON p.Carnet = ac.Carnet AND ac.rn = 1 
LEFT JOIN cte_becas b ON p.Carnet = b.Carnet
LEFT JOIN cte_solvencia s ON p.Carnet = s.Carnet
LEFT JOIN cte_retiros r ON p.Carnet = r.Carnet
LEFT JOIN cte_cambios c ON p.Carnet = c.Carnet
LEFT JOIN cte_pensum pen ON p.Carrera = pen.Carrera AND p.[Plan] = pen.Plan_
CROSS APPLY (
    -- Aquí se calculan las lógicas UNA sola vez
    SELECT 
        CASE WHEN a.Paes < 6.0 THEN 1 ELSE 0 END AS Ind_PAES,
        CASE WHEN (
            (ISNULL(p.PromedioCiclo_C1, 0) + ISNULL(p.PromedioCiclo_C2, 0)) / 
            NULLIF((CASE WHEN p.PromedioCiclo_C1 IS NOT NULL THEN 1 ELSE 0 END + CASE WHEN p.PromedioCiclo_C2 IS NOT NULL THEN 1 ELSE 0 END), 0)
        ) < 6.5 THEN 1 ELSE 0 END AS Ind_CUM,
        CASE WHEN (20 - ISNULL(ac.AvanceCarrera, 0)) >= 10 THEN 1 ELSE 0 END AS Ind_Avance,
        CASE WHEN ISNULL(s.CantInsolvencias, 0) >= 2 THEN 1 ELSE 0 END AS Ind_Solvencia,
        CASE WHEN ISNULL(r.RetirosParciales, 0) >= 2 THEN 1 ELSE 0 END AS Ind_RetiroParcial,
        CASE WHEN ISNULL(r.RetirosTotales, 0) >= 1 THEN 1 ELSE 0 END AS Ind_RetiroTotal,
        CASE WHEN ISNULL(c.CantCambios, 0) >= 1 THEN 1 ELSE 0 END AS Ind_CambioCarrera,
        CASE WHEN (CAST(ISNULL(p.TotalMateriasReprobadas_Anio1, 0) AS FLOAT) / NULLIF(pen.TotalMateriasPlan, 0)) >= 0.5 THEN 1 ELSE 0 END AS Ind_Reprobacion,
        0 AS Ind_BrechaDesercion
) ire
WHERE p.MateriasInscritas_C1 IS NOT NULL;
GO
-- =========================================================
-- VERIFICACIÓN DE RESULTADOS
-- =========================================================

-- Total de registros (1 fila por estudiante)
SELECT COUNT(*) AS TotalEstudiantes FROM dbo.DesercionEstudiantil_PrimerAnio;

-- Distribución de la variable objetivo
SELECT 
    CASE WHEN Deserto = 1 THEN 'Desertó' ELSE 'Continuó' END AS Estado,
    COUNT(*) AS Total,
    CAST(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() AS DECIMAL(5,2)) AS Porcentaje
FROM dbo.DesercionEstudiantil_PrimerAnio
GROUP BY Deserto
ORDER BY Deserto DESC;

-- Verificar que no hay valores nulos críticos
SELECT 
    COUNT(*) AS Total,
    SUM(CASE WHEN MateriasInscritas_C1 IS NULL THEN 1 ELSE 0 END) AS Nulos_C1,
    SUM(CASE WHEN TasaAprobacion_Anio1 IS NULL THEN 1 ELSE 0 END) AS Nulos_TasaAnio1,
    SUM(CASE WHEN PromedioGeneral_Anio1 IS NULL THEN 1 ELSE 0 END) AS Nulos_PromedioAnio1
FROM dbo.DesercionEstudiantil_PrimerAnio;

-- Estadísticas descriptivas de variables clave
SELECT 
    AVG(TasaAprobacion_Anio1) AS Promedio_TasaAprobacion,
    AVG(PromedioGeneral_Anio1) AS Promedio_Notas,
    AVG(CAST(TieneBeca AS FLOAT)) AS Porcentaje_Becados,
    AVG(TotalMateriasAprobadas_Anio1) AS Promedio_MateriasAprobadas
FROM dbo.DesercionEstudiantil_PrimerAnio;

-- Tasa de deserción por carrera
SELECT 
    Carrera,
    COUNT(*) AS TotalEstudiantes,
    SUM(CAST(Deserto AS INT)) AS TotalDesertores,
    CAST(AVG(CAST(Deserto AS FLOAT)) * 100 AS DECIMAL(5,2)) AS PorcentajeDesercion
FROM dbo.DesercionEstudiantil_PrimerAnio
GROUP BY Carrera
HAVING COUNT(*) >= 10  -- Solo carreras con al menos 10 estudiantes
ORDER BY PorcentajeDesercion DESC;

-- Muestra de datos
SELECT  * 
FROM dbo.DesercionEstudiantil_PrimerAnio 
ORDER BY Deserto DESC, Carnet;

-- Verificar que NO hay duplicados (debe devolver 0 filas)
SELECT Carnet, COUNT(*) AS Duplicados
FROM dbo.DesercionEstudiantil_PrimerAnio
GROUP BY Carnet
HAVING COUNT(*) > 1;

select * from ga..DesercionEstudiantil_PrimerAnio
order by cantInsolvencias_recurrentes desc