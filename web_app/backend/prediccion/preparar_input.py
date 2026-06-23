"""
Función para traducir los datos de un formulario web
al formato exacto que espera el modelo de regresión logística
de predicción de deserción estudiantil (is_dropout).

Uso: ver ejemplo_uso.py
"""

import pandas as pd


def preparar_input(datos_formulario, columnas_modelo):
    """
    Convierte un diccionario con los datos del formulario web
    en un DataFrame con las columnas exactas que espera el modelo.

    Parámetros
    ----------
    datos_formulario : dict
        Diccionario con las respuestas del formulario. Debe incluir:
        - poverty_rate_percent (numérico)
        - internet_infrastructure_index (numérico)
        - age (numérico)
        - internet_access_hours (numérico)
        - academic_motivation (numérico)
        - education_content_hours (numérico)
        - brain_rot_level (numérico)
        - attention_span_minutes (numérico)
        - study_hours_per_week (numérico)
        - class_attendance_rate (numérico)
        - development_level (texto: "Developed" o "Underdeveloped")
        - urban_rural (texto: "Urban" o "Rural")
        - family_income_level (texto: "Low", "Middle" o "High")

    columnas_modelo : list
        Lista de columnas cargada desde columnas_modelo.pkl

    Retorna
    -------
    pd.DataFrame
        Una fila lista para pasar a modelo.predict_proba(...)
    """
    fila = {col: 0 for col in columnas_modelo}

    # Variables numéricas: se copian directamente
    for var in ["poverty_rate_percent", "internet_infrastructure_index",
                "age", "internet_access_hours", "academic_motivation",
                "education_content_hours", "brain_rot_level",
                "attention_span_minutes", "study_hours_per_week",
                "class_attendance_rate"]:
        fila[var] = datos_formulario[var]

    # Variables categóricas: se convierten a su dummy correspondiente
    if datos_formulario["development_level"] == "Underdeveloped":
        fila["Development_level_name_Underdeveloped"] = 1

    if datos_formulario["urban_rural"] == "Urban":
        fila["urban_rural_Urban"] = 1

    if datos_formulario["family_income_level"] == "Low":
        fila["family_income_level_Low"] = 1
    elif datos_formulario["family_income_level"] == "Middle":
        fila["family_income_level_Middle"] = 1
    # Si es "High", ambas quedan en 0 (es la categoría base)

    # Se reordenan las columnas para que coincidan exactamente
    # con el orden usado al entrenar el modelo
    return pd.DataFrame([fila])[columnas_modelo]
