"""
Build the exact feature row expected by the dropout logistic-regression model.

The backend avoids pandas here: SQL Server is queried with pyodbc and the model
receives a NumPy matrix ordered with columnas_modelo.pkl.
"""

import numpy as np


def preparar_input(datos_formulario, columnas_modelo):
    fila = {col: 0 for col in columnas_modelo}

    for var in [
        "poverty_rate_percent",
        "internet_infrastructure_index",
        "age",
        "internet_access_hours",
        "academic_motivation",
        "education_content_hours",
        "brain_rot_level",
        "attention_span_minutes",
        "study_hours_per_week",
        "class_attendance_rate",
    ]:
        fila[var] = datos_formulario[var]

    if datos_formulario["development_level"] == "Underdeveloped":
        fila["Development_level_name_Underdeveloped"] = 1

    if datos_formulario["urban_rural"] == "Urban":
        fila["urban_rural_Urban"] = 1

    if datos_formulario["family_income_level"] == "Low":
        fila["family_income_level_Low"] = 1
    elif datos_formulario["family_income_level"] == "Middle":
        fila["family_income_level_Middle"] = 1

    return np.array([[fila[col] for col in columnas_modelo]], dtype=float)
