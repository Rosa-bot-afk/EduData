USE StudentDigitalBehaviorDB;
GO

/*
M5 - Construyendo el reporte ejecutivo
Consultas para dashboard ejecutivo de EduData Analytics.

Las consultas usan la estructura normalizada:
- StudentAssessment: cada entrevista realizada al estudiante.
- Mide: valor de cada metrica por entrevista.
- MetricDefinition: nombre y categoria de cada metrica.
*/

/* =========================================================
   CONSULTA 1 - FACIL
   Promedio ejecutivo de bienestar por periodo academico.

   Pregunta:
   Cual es el bienestar promedio de los estudiantes en cada periodo?
   ========================================================= */

SELECT
    AP.Period_year,
    AP.period_term,
    MD.metric_name,
    AVG(M.metric_value) AS promedio_bienestar
FROM Mide M
INNER JOIN MetricDefinition MD
    ON M.metric_id = MD.Metric_id
INNER JOIN StudentAssessment SA
    ON M.Assessment_id = SA.Assessment_id
INNER JOIN AcademicPeriod AP
    ON SA.academic_period_id = AP.Academic_Period_id
WHERE MD.metric_name = 'wellbeing_percent'
GROUP BY
    AP.Period_year,
    AP.period_term,
    MD.metric_name
ORDER BY
    AP.Period_year,
    AP.period_term;


/* =========================================================
   CONSULTA 2 - NIVEL MEDIO
   Tabla cruzada por periodo academico y nivel de riesgo.

   Pregunta M5 relacionada a Q21:
   Cual fue la cantidad de estudiantes por categoria de riesgo
   en cada periodo academico?

   Criterio:
   digital_addiction_score >= 70: Alto
   digital_addiction_score >= 40: Medio
   digital_addiction_score < 40: Bajo
   ========================================================= */

SELECT
    AP.Period_year,
    AP.period_term,
    SUM(CASE WHEN M.metric_value < 40 THEN 1 ELSE 0 END) AS riesgo_bajo,
    SUM(CASE WHEN M.metric_value >= 40 AND M.metric_value < 70 THEN 1 ELSE 0 END) AS riesgo_medio,
    SUM(CASE WHEN M.metric_value >= 70 THEN 1 ELSE 0 END) AS riesgo_alto
FROM Mide M
INNER JOIN MetricDefinition MD
    ON M.metric_id = MD.Metric_id
INNER JOIN StudentAssessment SA
    ON M.Assessment_id = SA.Assessment_id
INNER JOIN AcademicPeriod AP
    ON SA.academic_period_id = AP.Academic_Period_id
WHERE MD.metric_name = 'digital_addiction_score'
GROUP BY
    AP.Period_year,
    AP.period_term
ORDER BY
    AP.Period_year,
    AP.period_term;


/* =========================================================
   CONSULTA 3 - NIVEL MEDIO/ALTO
   Acumulado YTD por universidad.

   Pregunta M5 relacionada a Q22:
   Cuanto acumulo cada universidad desde el inicio del anio
   hasta cada mes?

   Metrica usada:
   ads_clicked_per_week.
   ========================================================= */

SELECT
    U.university_name,
    YEAR(SA.sent_date) AS anio,
    MONTH(SA.sent_date) AS mes,
    SUM(M2.metric_value) AS acumulado_ytd_ads_clicked
FROM University U
INNER JOIN Student S
    ON U.university_id = S.university_id
INNER JOIN StudentAssessment SA
    ON S.student_id = SA.student_id
INNER JOIN Mide M2
    ON SA.Assessment_id = M2.Assessment_id
INNER JOIN MetricDefinition MD2
    ON M2.metric_id = MD2.Metric_id
WHERE MD2.metric_name = 'ads_clicked_per_week'
GROUP BY
    U.university_name,
    YEAR(SA.sent_date),
    MONTH(SA.sent_date)
ORDER BY
    U.university_name,
    anio,
    mes;


/* =========================================================
   CONSULTA 4 - NIVEL ALTO
   Categoria de riesgo por estudiante segun varias metricas.

   Pregunta M5 relacionada a Q24:
   Cual es la categoria de riesgo de un registro dado su valor
   de metrica?

   Se calcula un indicador ejecutivo combinando:
   - digital_addiction_score
   - stress_level
   - wellbeing_percent
   ========================================================= */

SELECT
    SA.student_id,
    SA.survey_number,
    SA.sent_date,
    AVG(CASE WHEN MD.metric_name = 'digital_addiction_score' THEN M.metric_value END) AS digital_addiction_score,
    AVG(CASE WHEN MD.metric_name = 'stress_level' THEN M.metric_value END) AS stress_level,
    AVG(CASE WHEN MD.metric_name = 'wellbeing_percent' THEN M.metric_value END) AS wellbeing_percent,
    CASE
        WHEN AVG(CASE WHEN MD.metric_name = 'digital_addiction_score' THEN M.metric_value END) >= 70
          OR AVG(CASE WHEN MD.metric_name = 'stress_level' THEN M.metric_value END) >= 8
          OR AVG(CASE WHEN MD.metric_name = 'wellbeing_percent' THEN M.metric_value END) < 40
        THEN 'High Risk'
        WHEN AVG(CASE WHEN MD.metric_name = 'digital_addiction_score' THEN M.metric_value END) >= 50
          OR AVG(CASE WHEN MD.metric_name = 'stress_level' THEN M.metric_value END) >= 6
          OR AVG(CASE WHEN MD.metric_name = 'wellbeing_percent' THEN M.metric_value END) < 60
        THEN 'Medium Risk'
        ELSE 'Low Risk'
    END AS executive_risk_category
FROM StudentAssessment SA
INNER JOIN Mide M
    ON SA.Assessment_id = M.Assessment_id
INNER JOIN MetricDefinition MD
    ON M.metric_id = MD.Metric_id
WHERE MD.metric_name IN (
    'digital_addiction_score',
    'stress_level',
    'wellbeing_percent'
)
GROUP BY
    SA.student_id,
    SA.survey_number,
    SA.sent_date
ORDER BY
    SA.student_id,
    SA.survey_number;


/* =========================================================
   CONSULTA 5 - MAS COMPLEJA
   Reporte parametrico ejecutivo por pais, periodo y umbral.

   Pregunta M5 relacionada a Q25:
   Reporte parametrico de rendimiento filtrado por entidad,
   periodo y umbral.

   Parametros:
   - Pais
   - Periodo
   - Umbral minimo de asistencia

   Objetivo:
   Ver universidades de un pais y periodo donde el promedio
   de asistencia supera un umbral, junto con productividad,
   bienestar y adiccion digital.
   ========================================================= */

DECLARE @country_name VARCHAR(100);
DECLARE @period_year SMALLINT;
DECLARE @period_term TINYINT;
DECLARE @attendance_threshold DECIMAL(12,2);

SET @country_name = 'Peru';
SET @period_year = 2025;
SET @period_term = 1;
SET @attendance_threshold = 80;

SELECT
    C.country_name,
    U.university_name,
    AP.Period_year,
    AP.period_term,
    COUNT(DISTINCT S.student_id) AS total_estudiantes,
    AVG(CASE WHEN MD.metric_name = 'class_attendance_rate' THEN M.metric_value END) AS promedio_asistencia,
    AVG(CASE WHEN MD.metric_name = 'productivity_score' THEN M.metric_value END) AS promedio_productividad,
    AVG(CASE WHEN MD.metric_name = 'wellbeing_percent' THEN M.metric_value END) AS promedio_bienestar,
    AVG(CASE WHEN MD.metric_name = 'digital_addiction_score' THEN M.metric_value END) AS promedio_adiccion_digital
FROM Country C
INNER JOIN University U
    ON C.country_id = U.country_id
INNER JOIN Student S
    ON U.university_id = S.university_id
INNER JOIN StudentAssessment SA
    ON S.student_id = SA.student_id
INNER JOIN AcademicPeriod AP
    ON SA.academic_period_id = AP.Academic_Period_id
INNER JOIN Mide M
    ON SA.Assessment_id = M.Assessment_id
INNER JOIN MetricDefinition MD
    ON M.metric_id = MD.Metric_id
WHERE C.country_name = @country_name
  AND AP.Period_year = @period_year
  AND AP.period_term = @period_term
  AND MD.metric_name IN (
        'class_attendance_rate',
        'productivity_score',
        'wellbeing_percent',
        'digital_addiction_score'
  )
GROUP BY
    C.country_name,
    U.university_name,
    AP.Period_year,
    AP.period_term
HAVING AVG(CASE WHEN MD.metric_name = 'class_attendance_rate' THEN M.metric_value END) >= @attendance_threshold
ORDER BY
    promedio_asistencia DESC,
    promedio_productividad DESC;
