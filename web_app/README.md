# EduData Analytics Web App

Primera version visual de la plataforma prometida para EduData Analytics.

## Roles

- Estudiante: completa encuestas y revisa su progreso.
- Admin universidad: ve dashboards de su universidad y crea usuarios.
- Empleado EduData: ve resultados globales y administra clientes/usuarios.

## Frontend

Abrir:

```text
web_app/frontend/index.html
```

O levantar servidor local:

```bash
python -m http.server 5500 -d web_app/frontend
```

Luego entrar a:

```text
http://localhost:5500
```

## Backend opcional

Instalar:

```bash
pip install fastapi uvicorn pypyodbc pydantic[email]
```

Ejecutar:

```bash
uvicorn web_app.backend.main:app --reload --port 8000
```

API:

- `GET /health`
- `GET /dashboard/global`
- `POST /users`
- `POST /surveys`
- `POST /predictions/dropout`
- `GET /predictions/university-risk`

## Modelo predictivo

Los archivos del modelo estan guardados en:

```text
web_app/backend/prediccion
```

Incluye:

- `modelo_dropout.pkl`
- `columnas_modelo.pkl`
- `preparar_input.py`
- `guia_integracion.md`

Para usar la prediccion completa:

1. Instalar dependencias desde la raiz del proyecto:

```bash
pip install -r requirements.txt
```

2. Levantar el frontend:

```bash
python -m http.server 5500 -d web_app/frontend
```

3. Levantar el backend en otra terminal:

```bash
uvicorn web_app.backend.main:app --reload --port 8000
```

4. Entrar a `http://localhost:5500`.
5. Iniciar sesion como `Admin universidad`.
6. Abrir el modulo `Prediccion`.
7. Completar o modificar los datos del estudiante.
8. Presionar `Calcular riesgo`.

Si el backend esta prendido, la pantalla usa el modelo real. Si el backend esta apagado, la pantalla usa una prediccion demo local para que la interfaz siga funcionando durante la presentacion.

La tabla `Estudiantes priorizados por el modelo` usa:

```text
GET /predictions/university-risk?university_name=Northbridge&limit=10
```

Ese endpoint lee SQL Server, toma la ultima encuesta de cada estudiante de la universidad encontrada, arma las variables que necesita el modelo, calcula la probabilidad de desercion y devuelve el top ordenado de mayor a menor riesgo. No inserta ni modifica datos.

## Respuesta a la duda

Si un administrador crea un usuario en la pagina, el frontend llama a `POST /users`.
El backend valida la solicitud y ejecuta un `INSERT INTO [User]` en SQL Server.

En produccion tambien se deberia:

- encriptar contrasenas;
- validar permisos por rol;
- asociar estudiantes a universidad;
- registrar auditoria de cambios;
- enviar notificaciones por correo.
