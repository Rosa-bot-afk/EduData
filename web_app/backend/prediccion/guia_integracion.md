# Modelo de predicción de deserción estudiantil — Guía de integración

## Qué te estoy enviando

| Archivo | Qué es |
|---|---|
| `modelo_dropout.pkl` | El modelo de regresión logística ya entrenado |
| `columnas_modelo.pkl` | La lista de las 14 variables que usa el modelo, en el orden correcto |
| `preparar_input.py` | Función que traduce los datos del formulario al formato que el modelo necesita |
| `ejemplo_uso.py` | Ejemplo completo de cómo usar todo junto |

**Importante:** los 4 archivos deben estar en la misma carpeta, porque `ejemplo_uso.py` importa la función desde `preparar_input.py`.

No necesitas el CSV original ni el script de entrenamiento — todo el trabajo de limpieza, selección de variables y entrenamiento ya quedó "empaquetado" dentro de estos archivos.

---

## Requisitos antes de usarlo

Instala estas librerías en el entorno donde corra tu backend:

```bash
pip install scikit-learn==1.4.1 numpy joblib
```

La versión de `scikit-learn` importa: si usas una muy distinta a 1.4.1, puede salir un warning o incluso fallar al cargar el modelo.

---

## Cómo usarlo (flujo básico)

```python
import joblib
from preparar_input import preparar_input

# 1. Cargar el modelo y las columnas (una sola vez, al iniciar el servidor)
modelo = joblib.load("modelo_dropout.pkl")
columnas_modelo = joblib.load("columnas_modelo.pkl")

# 2. Datos que llegan del formulario web (esto cambia por cada usuario)
datos_formulario = {
    "poverty_rate_percent": 45,
    "internet_infrastructure_index": 30,
    "age": 22,
    "internet_access_hours": 10,
    "academic_motivation": 2,
    "education_content_hours": 0.5,
    "brain_rot_level": 9,
    "attention_span_minutes": 8,
    "study_hours_per_week": 3,
    "class_attendance_rate": 55,
    "development_level": "Underdeveloped",   # "Developed" o "Underdeveloped"
    "urban_rural": "Rural",                  # "Urban" o "Rural"
    "family_income_level": "Low"             # "Low", "Middle" o "High"
}

# 3. Preparar los datos y predecir
fila = preparar_input(datos_formulario, columnas_modelo)
probabilidad = modelo.predict_proba(fila)[0, 1]

print(f"Probabilidad de deserción: {probabilidad:.2%}")
```

Corre `ejemplo_uso.py` directamente para ver esto funcionando sin tener que escribir nada — ya está listo para ejecutarse tal cual.

---

## Qué debe llenar el usuario en el formulario web

El diccionario `datos_formulario` necesita estas 13 claves. Aquí va qué representa cada una y qué tipo de campo conviene en el formulario:

**Campos numéricos** (inputs tipo número o sliders):
- `poverty_rate_percent` — tasa de pobreza (0-100)
- `internet_infrastructure_index` — índice de infraestructura de internet (0-100)
- `age` — edad del estudiante
- `internet_access_hours` — horas diarias de acceso a internet
- `academic_motivation` — motivación académica (escala, ej. 0-10)
- `education_content_hours` — horas semanales consumiendo contenido educativo
- `brain_rot_level` — nivel de "brain rot" (escala, ej. 0-10)
- `attention_span_minutes` — minutos de capacidad de atención
- `study_hours_per_week` — horas de estudio por semana
- `class_attendance_rate` — porcentaje de asistencia a clases (0-100)

**Campos de selección** (dropdowns o radio buttons):
- `development_level` — `"Developed"` o `"Underdeveloped"`
- `urban_rural` — `"Urban"` o `"Rural"`
- `family_income_level` — `"Low"`, `"Middle"` o `"High"`

Los nombres de las claves del diccionario tienen que escribirse **exactamente así** (mismo texto, mismas mayúsculas) para que `preparar_input()` los reconozca.

---

## Sobre el resultado: probabilidad vs. clasificación

El modelo te da un número entre 0 y 1 (la probabilidad de deserción). Si en la web quieres mostrar algo más simple como "Sí está en riesgo" / "No está en riesgo", tienes que elegir un punto de corte (umbral).

Por defecto, lo normal es usar 0.5:

```python
umbral = 0.5
en_riesgo = probabilidad >= umbral
```

Pero para este tipo de predicción (detectar a tiempo a estudiantes en riesgo), muchas veces conviene bajar el umbral a algo como 0.35, para no dejar pasar casos reales — aunque eso genere más falsas alarmas. Esto es una decisión que conviene que conversemos juntas antes de fijarla en la web, no es algo puramente técnico.

---

## Si algo no funciona

Si al cargar el modelo te sale un error de "número de features no coincide" o algo parecido, probablemente sea un problema de versiones de librerías entre tu entorno y el mío. Avísame y lo revisamos juntas.
