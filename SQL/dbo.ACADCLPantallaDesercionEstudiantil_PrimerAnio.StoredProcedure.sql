USE [GA]
GO
 
DROP PROCEDURE IF EXISTS [dbo].[ACADCLPantallaDesercionEstudiantil_PrimerAnio]
GO
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- =============================================
-- Author:		Kevin Ponce
-- Create date:	27 - April - 2026
-- =============================================
CREATE PROCEDURE ACADCLPantallaDesercionEstudiantil_PrimerAnio
	@i_Metodo INT = NULL,
	@i_Carnet VARCHAR(50) = NULL,
	@i_Carrera VARCHAR(200) = NULL,
	@i_Plan VARCHAR(100) = NULL,
	@i_IdCampus INT = NULL,
	@i_Sexo VARCHAR(20) = NULL,
	@i_AnioIngreso INT = NULL,
	@i_CicloIngreso INT = NULL,
	@i_InstitucionBach VARCHAR(255) = NULL,
	@i_TieneBeca BIT = NULL,
	@i_PorcentajeBeca_Promedio DECIMAL = NULL,
	@i_MateriasInscritas_C1 INT = NULL,
	@i_MateriasAprobadas_C1 INT = NULL,
	@i_MateriasReprobadas_C1 INT = NULL,
	@i_TasaAprobacion_C1 DECIMAL = NULL,
	@i_PromedioCiclo_C1 DECIMAL = NULL,
	@i_MateriasInscritas_C2 INT = NULL,
	@i_MateriasAprobadas_C2 INT = NULL,
	@i_MateriasReprobadas_C2 INT = NULL,
	@i_TasaAprobacion_C2 DECIMAL = NULL,
	@i_PromedioCiclo_C2 DECIMAL = NULL,
	@i_TotalMateriasInscritas_Anio1 INT = NULL,
	@i_TotalMateriasAprobadas_Anio1 INT = NULL,
	@i_TotalMateriasReprobadas_Anio1 INT = NULL,
	@i_TasaAprobacion_Anio1 DECIMAL = NULL,
	@i_PromedioGeneral_Anio1 DECIMAL = NULL,
	@i_AvanceCarrera_FinAnio1 DECIMAL = NULL,
	@i_PAES_Score DECIMAL = NULL,
	@i_CantInsolvencias_Recurrentes INT = NULL,
	@i_CantRetirosParciales INT = NULL,
	@i_CantRetirosTotales INT = NULL,
	@i_CantCambiosCarrera INT = NULL,
	@i_Ind_PAES BIT = NULL,
	@i_Ind_CUM BIT = NULL,
	@i_Ind_Avance BIT = NULL,
	@i_Ind_Solvencia BIT = NULL,
	@i_Ind_RetiroParcial BIT = NULL,
	@i_Ind_RetiroTotal BIT = NULL,
	@i_Ind_CambioCarrera BIT = NULL,
	@i_Ind_Reprobacion BIT = NULL,
	@i_Ind_BrechaDesercion BIT = NULL,
	@i_IRE_Total INT = NULL,
	@i_Deserto BIT = NULL,
	@i_Login VARCHAR(50) = NULL
AS

		/*>>>
			=============================================
			Script exclusivamente para el modulo de:

				MODULO PARA EL QUE SERÁ CREADO EL SP

			Haciendo uso de la logica de servicios.
			=============================================
			los metodos del script se componen en:

			método 1: creación del registro
			método 2: modificación del registro
			método 3: eliminar el registro 
			método 4: listar los registros
			método 5: listar haciendo uso del servicio de   [SERVICIO].[NombredelServicio]
			
		>>>*/
BEGIN
	DECLARE	@w_Id		INT = NULL,
			@w_Error	INT = NULL
 
 
	-- Listar
	IF @i_Metodo = 1
	BEGIN
		SELECT	Carnet,
				Carrera,
				[Plan] AS 'Plan',
				IdCampus,
				Sexo,
				AnioIngreso,
				CicloIngreso,
				InstitucionBach,
				TieneBeca,
				PorcentajeBeca_Promedio,
				MateriasInscritas_C1,
				MateriasAprobadas_C1,
				MateriasReprobadas_C1,
				TasaAprobacion_C1,
				PromedioCiclo_C1,
				MateriasInscritas_C2,
				MateriasAprobadas_C2,
				MateriasReprobadas_C2,
				TasaAprobacion_C2,
				PromedioCiclo_C2,
				TotalMateriasInscritas_Anio1,
				TotalMateriasAprobadas_Anio1,
				TotalMateriasReprobadas_Anio1,
				TasaAprobacion_Anio1,
				PromedioGeneral_Anio1,
				AvanceCarrera_FinAnio1,
				PAES_Score,
				CantInsolvencias_Recurrentes,
				CantRetirosParciales,
				CantRetirosTotales,
				CantCambiosCarrera,
				Ind_PAES,
				Ind_CUM,
				Ind_Avance,
				Ind_Solvencia,
				Ind_RetiroParcial,
				Ind_RetiroTotal,
				Ind_CambioCarrera,
				Ind_Reprobacion,
				Ind_BrechaDesercion,
				IRE_Total,
				Deserto
		FROM	GA..ACADDesercionEstudiantil_PrimerAnio
		WHERE	Carnet = @i_Carnet
    END
 
END
GO

