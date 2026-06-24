# Contexto de las consultas SQL - Modulo M5

## Enfoque general

Las consultas fueron disenadas para construir un reporte ejecutivo de EduData Analytics. La idea no es solo extraer datos, sino convertir las respuestas de las encuestas en indicadores utiles para la toma de decisiones de una universidad o de la empresa.

El reporte usa la base normalizada del proyecto:

- `Student`: informacion del estudiante.
- `University`: universidad a la que pertenece.
- `StudentAssessment`: cada entrevista o encuesta realizada.
- `Mide`: valores de las metricas medidas en cada encuesta.
- `MetricDefinition`: nombre y categoria de cada metrica.
- `AcademicPeriod`: periodo academico de la encuesta.

Los temas usados vienen principalmente de las semanas 13 y 14:

- PIVOT: transformar filas en columnas para tablas cruzadas.
- UNPIVOT: transformar columnas en filas para normalizar datos de encuestas.
- YTD / MTD / QTD: acumulados temporales para reportes ejecutivos.
- NTILE y PERCENT_RANK: segmentacion y posicion relativa de registros.
- Vistas: encapsular consultas para que sean reutilizables por dashboards.
- Procedimientos almacenados: reportes parametrizados.
- IF / BEGIN / END: validar condiciones antes de ejecutar reportes.

---

## Consulta 1 - Promedio de bienestar por periodo academico

### Pregunta de negocio

¿Cual es el bienestar promedio de los estudiantes en cada periodo academico?

### Contexto

Esta consulta resume la metrica `wellbeing_percent` por periodo academico. Sirve para que un administrador pueda ver si el bienestar general de los estudiantes mejora, se mantiene o empeora a lo largo del tiempo.

### Relacion con la teoria

Se relaciona con el enfoque de reporte ejecutivo porque transforma muchos registros individuales en un indicador agregado. Tambien sirve como base para una vista, ya que es una consulta que podria reutilizarse constantemente en un dashboard.

### Utilidad en EduData Analytics

Permite mostrar un KPI de bienestar por periodo. En la app, este indicador puede alimentar graficos de tendencia y alertas institucionales.

---

## Consulta 2 - Tabla cruzada de estudiantes por nivel de riesgo

### Pregunta de negocio

¿Cuantos estudiantes hay en riesgo bajo, medio y alto en cada periodo academico?

### Contexto

La consulta clasifica a los estudiantes segun el valor de `digital_addiction_score`. Luego cuenta cuantos casos pertenecen a cada categoria de riesgo.

### Relacion con la teoria

Esta consulta se conecta con PIVOT porque el resultado esperado es una tabla matricial: los periodos quedan como filas y las categorias de riesgo como columnas (`riesgo_bajo`, `riesgo_medio`, `riesgo_alto`).

En clase, PIVOT se usa para convertir valores de una columna en columnas separadas. En nuestro caso, las categorias de riesgo funcionan como esas columnas del reporte ejecutivo.

### Utilidad en EduData Analytics

Ayuda a que el administrador vea rapidamente si el riesgo digital esta creciendo o disminuyendo. Es una consulta ideal para graficos de barras apiladas o tarjetas de resumen.

---

## Consulta 3 - Acumulado YTD por universidad

### Pregunta de negocio

¿Cuanto acumulo cada universidad desde el inicio del anio hasta cada mes?

### Contexto

La consulta calcula el acumulado mensual de una metrica, por ejemplo `ads_clicked_per_week`, agrupada por universidad. Esto permite observar el comportamiento acumulado durante el anio.

### Relacion con la teoria

Se relaciona directamente con YTD (Year To Date), visto en la semana 13. El YTD permite calcular un acumulado desde el inicio del anio hasta una fecha o mes de corte.

La logica es similar al patron visto en clase:

```sql
SUM(CASE WHEN fecha BETWEEN inicio_del_anio AND fecha_corte THEN valor ELSE 0 END)
```

### Utilidad en EduData Analytics

Sirve para construir graficos de tiempo y comparar universidades. En un dashboard ejecutivo, este tipo de indicador muestra tendencia acumulada y no solo valores aislados.

---

## Consulta 4 - Categoria ejecutiva de riesgo por estudiante

### Pregunta de negocio

¿Que categoria de riesgo tiene un estudiante segun sus metricas principales?

### Contexto

La consulta combina varias metricas:

- `digital_addiction_score`
- `stress_level`
- `wellbeing_percent`

Con esas metricas se crea una categoria ejecutiva: riesgo alto, medio o bajo.

### Relacion con la teoria

Se relaciona con estructuras de control logico mediante `CASE`, que permite clasificar registros segun condiciones. Tambien se puede complementar con `NTILE` o `PERCENT_RANK` para segmentar a los estudiantes por percentiles de riesgo.

Por ejemplo:

- `NTILE(4)` podria dividir estudiantes en cuartiles de riesgo.
- `PERCENT_RANK()` podria indicar que tan arriba o abajo esta un estudiante frente al resto.

### Utilidad en EduData Analytics

Esta consulta es clave para priorizar intervenciones. Permite identificar estudiantes que requieren seguimiento inmediato, monitoreo preventivo o seguimiento regular.

---

## Consulta 5 - Reporte parametrico ejecutivo por pais, periodo y umbral

### Pregunta de negocio

¿Que universidades cumplen con un umbral minimo de asistencia en un pais y periodo especifico?

### Contexto

La consulta recibe parametros como pais, anio, periodo y umbral de asistencia. Luego devuelve universidades que cumplen la condicion, junto con indicadores de productividad, bienestar y adiccion digital.

### Relacion con la teoria

Esta consulta se relaciona con procedimientos almacenados, porque el reporte puede convertirse en un SP parametrizado.

En clase se explica que un procedimiento almacenado sirve cuando el negocio necesita ejecutar el mismo reporte cambiando variables. En este caso, el administrador podria cambiar:

- Pais.
- Periodo.
- Umbral de asistencia.

Tambien se relaciona con `IF`, porque antes de ejecutar el reporte se podria validar si existen datos para ese pais o periodo.

### Utilidad en EduData Analytics

Es una consulta pensada para la vista de empleado EduData, porque permite analizar varias universidades y paises. Tambien ayuda a construir filtros dentro de la app.

---

## Como explicar la conexion con los PPTs

Nuestro proyecto aplica los temas de clase de la siguiente manera:

1. Usamos agregaciones para convertir encuestas individuales en indicadores ejecutivos.
2. Usamos logica tipo PIVOT para crear tablas cruzadas por periodo y riesgo.
3. Usamos acumulados temporales como YTD para analizar la evolucion de metricas.
4. Usamos clasificacion de riesgo con `CASE`, y podria ampliarse con `NTILE` y `PERCENT_RANK`.
5. Usamos la idea de vistas y procedimientos almacenados para que los reportes sean reutilizables y parametrizables.

En conjunto, las consultas permiten que EduData Analytics pase de tener una base de datos transaccional a tener una capa analitica para dashboards, indicadores y reportes ejecutivos.

---

## Recomendacion para mejorar la entrega

Para que el trabajo se vea mas alineado con las semanas 13 y 14, se recomienda presentar las consultas con estos nombres:

1. Matriz de riesgo por periodo usando logica PIVOT.
2. Tendencia de bienestar por periodo academico.
3. Acumulado YTD de actividad digital por universidad.
4. Clasificacion ejecutiva de riesgo por estudiante.
5. Reporte parametrico para dashboard institucional.

Si el profesor pide evidenciar mas temas de clase, se puede agregar una vista llamada `vw_ReporteEjecutivoUniversidad` y un procedimiento almacenado llamado `sp_ReporteEjecutivoPorPaisPeriodo`.
