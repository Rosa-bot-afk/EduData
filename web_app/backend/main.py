from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path

import joblib
import pypyodbc
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr


ROOT = Path(__file__).resolve().parents[2]
PREDICTION_DIR = Path(__file__).resolve().parent / "prediccion"
if str(PREDICTION_DIR) not in sys.path:
    sys.path.append(str(PREDICTION_DIR))

from preparar_input import preparar_input


def load_env() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"'))


load_env()


def connect():
    driver = os.getenv("SQL_DRIVER", "SQL Server")
    server = os.getenv("SQL_SERVER", "localhost")
    database = os.getenv("SQL_DATABASE", "StudentDigitalBehaviorDB")
    auth_mode = os.getenv("SQL_AUTH_MODE", "windows").lower()
    if auth_mode == "windows":
        return pypyodbc.connect(
            f"Driver={{{driver}}};Server={server};Database={database};Trusted_Connection=yes;"
        )
    username = os.getenv("SQL_USERNAME", "")
    password = os.getenv("SQL_PASSWORD", "")
    return pypyodbc.connect(
        f"Driver={{{driver}}};Server={server};Database={database};UID={username};PWD={password};"
    )


class UserCreate(BaseModel):
    email: EmailStr
    user_name: str
    password: str
    user_role: str


class SurveySubmission(BaseModel):
    student_id: int
    survey_number: int
    values: dict[str, float | int | str]


class DropoutPredictionInput(BaseModel):
    poverty_rate_percent: float
    internet_infrastructure_index: float
    age: int
    internet_access_hours: float
    academic_motivation: float
    education_content_hours: float
    brain_rot_level: float
    attention_span_minutes: float
    study_hours_per_week: float
    class_attendance_rate: float
    development_level: str
    urban_rural: str
    family_income_level: str


app = FastAPI(title="EduData Analytics API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


dropout_model = joblib.load(PREDICTION_DIR / "modelo_dropout.pkl")
dropout_columns = joblib.load(PREDICTION_DIR / "columnas_modelo.pkl")


@app.get("/health")
def health():
    return {"status": "ok", "service": "EduData Analytics"}


@app.get("/dashboard/global")
def dashboard_global():
    query = """
    SELECT
        COUNT(DISTINCT S.student_id) AS students,
        COUNT(DISTINCT U.university_id) AS universities,
        COUNT(SA.Assessment_id) AS assessments
    FROM Student S
    INNER JOIN University U ON S.university_id = U.university_id
    INNER JOIN StudentAssessment SA ON S.student_id = SA.student_id;
    """
    conn = connect()
    try:
        cur = conn.cursor()
        cur.execute(query)
        row = cur.fetchone()
        return {"students": row[0], "universities": row[1], "assessments": row[2]}
    finally:
        conn.close()


def classify_dropout_risk(probability: float) -> str:
    if probability >= 0.70:
        return "Alto"
    if probability >= 0.35:
        return "Medio"
    return "Bajo"


def dropout_recommendation(risk_level: str) -> str:
    if risk_level == "Alto":
        return "Derivar a seguimiento academico y bienestar universitario."
    if risk_level == "Medio":
        return "Programar monitoreo preventivo y revisar asistencia/motivacion."
    return "Mantener seguimiento regular en el proximo periodo."


def decode_family_income(value: float) -> str:
    if value <= 1:
        return "Low"
    if value <= 2:
        return "Middle"
    return "High"


def prediction_payload_from_row(row: dict) -> dict[str, float | int | str]:
    return {
        "poverty_rate_percent": float(row["poverty_rate_percent"]),
        "internet_infrastructure_index": float(row["internet_infrastructure_index"]),
        "age": int(row["age"]),
        "internet_access_hours": float(row["internet_access_hours"]),
        "academic_motivation": float(row["academic_motivation"]),
        "education_content_hours": float(row["education_content_hours"]),
        "brain_rot_level": float(row["brain_rot_level"]),
        "attention_span_minutes": float(row["attention_span_minutes"]),
        "study_hours_per_week": float(row["study_hours_per_week"]),
        "class_attendance_rate": float(row["class_attendance_rate"]),
        "development_level": str(row["development_level_name"]),
        "urban_rural": str(row["urban_rural"]),
        "family_income_level": decode_family_income(float(row["family_income_level"])),
    }


def predict_probability(payload: dict[str, float | int | str]) -> float:
    row = preparar_input(payload, dropout_columns)
    return float(dropout_model.predict_proba(row)[0, 1])


@app.post("/predictions/dropout")
def predict_dropout(payload: DropoutPredictionInput):
    try:
        probability = predict_probability(payload.dict())
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=f"Missing field: {exc}") from exc
    risk_level = classify_dropout_risk(probability)
    return {
        "dropout_probability": round(probability, 4),
        "dropout_probability_percent": round(probability * 100, 2),
        "risk_level": risk_level,
        "recommendation": dropout_recommendation(risk_level),
    }


@app.get("/predictions/university-risk")
def university_dropout_risk(
    university_name: str = Query("Northbridge", min_length=1),
    limit: int = Query(10, ge=1, le=100),
    view: str = Query("top", pattern="^(top|mixed)$"),
):
    university_query = """
    SELECT TOP 1 university_id, university_name
    FROM University
    WHERE university_name = ?
       OR university_name LIKE ?
    ORDER BY CASE WHEN university_name = ? THEN 0 ELSE 1 END, university_name;
    """
    metrics_query = """
    WITH latest AS (
        SELECT
            SA.Assessment_id,
            SA.student_id,
            SA.survey_number,
            SA.urban_rural,
            SA.age,
            SA.field_of_study_id,
            ROW_NUMBER() OVER (
                PARTITION BY SA.student_id
                ORDER BY SA.survey_number DESC, SA.Assessment_id DESC
            ) AS rn
        FROM StudentAssessment SA
        INNER JOIN Student S ON SA.student_id = S.student_id
        WHERE S.university_id = ?
    )
    SELECT
        S.student_id,
        U.user_name,
        Univ.university_name,
        F.field_of_study,
        C.country_name,
        DL.Development_level_name AS development_level_name,
        CI.poverty_rate_percent,
        CI.internet_infrastructure_index,
        L.survey_number,
        L.urban_rural,
        L.age,
        MAX(CASE WHEN MD.metric_name = 'internet_access_hours' THEN M.metric_value END) AS internet_access_hours,
        MAX(CASE WHEN MD.metric_name = 'academic_motivation' THEN M.metric_value END) AS academic_motivation,
        MAX(CASE WHEN MD.metric_name = 'education_content_hours' THEN M.metric_value END) AS education_content_hours,
        MAX(CASE WHEN MD.metric_name = 'brain_rot_level' THEN M.metric_value END) AS brain_rot_level,
        MAX(CASE WHEN MD.metric_name = 'attention_span_minutes' THEN M.metric_value END) AS attention_span_minutes,
        MAX(CASE WHEN MD.metric_name = 'study_hours_per_week' THEN M.metric_value END) AS study_hours_per_week,
        MAX(CASE WHEN MD.metric_name = 'class_attendance_rate' THEN M.metric_value END) AS class_attendance_rate,
        MAX(CASE WHEN MD.metric_name = 'family_income_level' THEN M.metric_value END) AS family_income_level
    FROM latest L
    INNER JOIN Student S ON L.student_id = S.student_id
    INNER JOIN [User] U ON S.usuario_id = U.user_id
    INNER JOIN University Univ ON S.university_id = Univ.university_id
    INNER JOIN Country C ON S.country_id = C.country_id
    INNER JOIN DevelopmentLevel DL ON C.development_id = DL.Development_Level_id
    INNER JOIN CountryIndicator CI ON C.country_id = CI.country_id
    INNER JOIN FieldOfStudy F ON L.field_of_study_id = F.field_of_study_id
    INNER JOIN Mide M ON L.Assessment_id = M.Assessment_id
    INNER JOIN MetricDefinition MD ON M.metric_id = MD.Metric_id
    WHERE L.rn = 1
      AND CI.indicator_year = 2025
      AND MD.metric_name IN (
        'internet_access_hours',
        'academic_motivation',
        'education_content_hours',
        'brain_rot_level',
        'attention_span_minutes',
        'study_hours_per_week',
        'class_attendance_rate',
        'family_income_level'
      )
    GROUP BY
        S.student_id,
        U.user_name,
        Univ.university_name,
        F.field_of_study,
        C.country_name,
        DL.Development_level_name,
        CI.poverty_rate_percent,
        CI.internet_infrastructure_index,
        L.survey_number,
        L.urban_rural,
        L.age;
    """
    conn = connect()
    try:
        cur = conn.cursor()
        cur.execute(university_query, (university_name, f"%{university_name}%", university_name))
        university = cur.fetchone()
        if not university:
            raise HTTPException(status_code=404, detail="University not found")

        university_id, matched_university_name = university
        cur.execute(metrics_query, (university_id,))
        columns = [column[0] for column in cur.description]
        rows = [dict(zip(columns, row)) for row in cur.fetchall()]

        ranked = []
        for row in rows:
            payload = prediction_payload_from_row(row)
            probability = predict_probability(payload)
            risk_level = classify_dropout_risk(probability)
            ranked.append(
                {
                    "student_id": row["student_id"],
                    "student": row["user_name"],
                    "university": row["university_name"],
                    "field_of_study": row["field_of_study"],
                    "country": row["country_name"],
                    "survey_number": row["survey_number"],
                    "dropout_probability": round(probability, 4),
                    "dropout_probability_percent": round(probability * 100, 2),
                    "risk_level": risk_level,
                    "recommendation": dropout_recommendation(risk_level),
                }
            )

        ranked.sort(key=lambda item: item["dropout_probability"], reverse=True)
        risk_counts = {
            "Alto": sum(1 for item in ranked if item["risk_level"] == "Alto"),
            "Medio": sum(1 for item in ranked if item["risk_level"] == "Medio"),
            "Bajo": sum(1 for item in ranked if item["risk_level"] == "Bajo"),
        }
        if view == "mixed":
            selected = []
            quotas = {"Alto": 4, "Medio": 3, "Bajo": 3}
            for risk_level, quota in quotas.items():
                selected.extend([item for item in ranked if item["risk_level"] == risk_level][:quota])
            selected.sort(key=lambda item: item["dropout_probability"], reverse=True)
            selected = selected[:limit]
        else:
            selected = ranked[:limit]
        return {
            "university": matched_university_name,
            "students_evaluated": len(ranked),
            "risk_counts": risk_counts,
            "view": view,
            "results": selected,
        }
    finally:
        conn.close()


@app.post("/users")
def create_user(payload: UserCreate):
    if payload.user_role not in {"estudiante", "administrador"}:
        raise HTTPException(status_code=400, detail="Invalid role")
    conn = connect()
    try:
        cur = conn.cursor()
        cur.execute("SELECT ISNULL(MAX(user_id), 0) + 1 FROM [User]")
        user_id = cur.fetchone()[0]
        cur.execute(
            """
            INSERT INTO [User] (user_id, email, user_name, [password], created_at, user_role)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                payload.email,
                payload.user_name,
                payload.password,
                datetime.now(),
                payload.user_role,
            ),
        )
        conn.commit()
        return {"created": True, "user_id": user_id}
    finally:
        conn.close()


@app.post("/surveys")
def submit_survey(payload: SurveySubmission):
    return {
        "received": True,
        "student_id": payload.student_id,
        "survey_number": payload.survey_number,
        "message": "Endpoint placeholder: insert into StudentAssessment and Mide here.",
    }
