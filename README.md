# Proyecto Comportamiento Digital de Estudiantes

Proyecto para crear una base de datos SQL Server a partir de una base longitudinal de estudiantes universitarios.

## Estructura

- `sql/01_create_tables.sql`: crea las tablas, llaves primarias, llaves foraneas, restricciones e indices.
- `data/official_students_longitudinal_90000_v2.xlsx`: base longitudinal con 90,000 entrevistas.
- `docs/mide_table_example_from_longitudinal.xlsx`: ejemplo visual de como se ve la tabla `Mide`.
- `scripts/load_excel_to_sql_server.py`: carga el Excel a SQL Server usando `pypyodbc` y `pandas`.
- `scripts/generate_python_report_charts.py`: genera graficos en Python para la pagina de reportes.
- `web_app/frontend/assets/charts`: imagenes PNG usadas por los dashboards.
- `.env.example`: plantilla de conexion.

## Pasos de uso

1. Abrir SQL Server Management Studio.
2. Ejecutar `sql/01_create_tables.sql`.
3. Instalar dependencias:

```bash
pip install -r requirements.txt
```

4. Copiar `.env.example` como `.env`.
5. Editar `.env` con tus datos de conexion.
6. Ejecutar la carga:

```bash
python scripts/load_excel_to_sql_server.py
```

## Conexion en la universidad

Usar los datos que entregue el profesor o la universidad:

```env
SQL_AUTH_MODE=sql
SQL_SERVER=TU_SERVIDOR_SQL
SQL_DATABASE=StudentDigitalBehaviorDB
SQL_USERNAME=TU_USUARIO
SQL_PASSWORD=TU_PASSWORD
SQL_DRIVER=SQL Server
```

## Conexion local en casa

Si usas Windows Authentication:

```env
SQL_AUTH_MODE=windows
SQL_SERVER=TU_PC\SQLEXPRESS
SQL_DATABASE=StudentDigitalBehaviorDB
SQL_USERNAME=
SQL_PASSWORD=
SQL_DRIVER=SQL Server
```

## Notas

La tabla `Mide` es la mas grande. Se genera desde `DATA` y carga 2,880,000 filas, porque son 90,000 entrevistas por 32 metricas.

El script valida al final:

- 15,000 estudiantes.
- 90,000 entrevistas.
- 2,880,000 registros en `Mide`.
- Cada estudiante con sus 6 entrevistas.

## Pagina web

La primera version de la plataforma esta en:

```text
web_app/frontend
```

Para verla en navegador:

```bash
python -m http.server 5500 -d web_app/frontend
```

Luego abrir:

```text
http://localhost:5500
```

El backend base esta en:

```text
web_app/backend/main.py
```

Para levantarlo:

```bash
python -m uvicorn web_app.backend.main:app --reload --port 8000
```

## Graficos en Python

Los graficos del reporte ejecutivo se generan desde SQL Server con Python y se guardan como imagenes en la app.

Para actualizarlos despues de cargar o cambiar datos:

```bash
python scripts/generate_python_report_charts.py
```

La vista de `Admin universidad` muestra graficos solo de su universidad. La vista de `Empleado EduData` muestra una version general con filtros de alcance global.
