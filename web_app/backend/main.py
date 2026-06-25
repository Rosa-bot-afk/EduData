from __future__ import annotations

import os
import sys
from io import BytesIO
from decimal import Decimal
from datetime import datetime
from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pyodbc
from fastapi import FastAPI, HTTPException, Query, Response
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
    driver = os.getenv("SQL_DRIVER", "ODBC Driver 17 for SQL Server")
    server = os.getenv("SQL_SERVER", "localhost")
    database = os.getenv("SQL_DATABASE", "StudentDigitalBehaviorDB")
    auth_mode = os.getenv("SQL_AUTH_MODE", "windows").lower()
    if auth_mode == "windows":
        return pyodbc.connect(
            f"Driver={{{driver}}};Server={server};Database={database};Trusted_Connection=yes;",
            timeout=15,
        )
    username = os.getenv("SQL_USERNAME", "")
    password = os.getenv("SQL_PASSWORD", "")
    return pyodbc.connect(
        f"Driver={{{driver}}};Server={server};Database={database};UID={username};PWD={password};",
        timeout=15,
    )


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


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


def rows_as_dicts(cursor) -> list[dict]:
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def json_value(value):
    if isinstance(value, Decimal):
        return float(value)
    return value


def normalize_rows(rows: list[dict]) -> list[dict]:
    return [{key: json_value(value) for key, value in row.items()} for row in rows]


def period_condition(alias: str, period: str) -> str:
    if period == "2025-1":
        return f"AND {alias}.survey_number BETWEEN 1 AND 3"
    if period == "2025-2":
        return f"AND {alias}.survey_number BETWEEN 4 AND 6"
    return ""


def risk_level_from_rate(rate: float) -> str:
    if rate >= 58:
        return "Alto"
    if rate >= 50:
        return "Medio"
    return "Bajo"


NAVY = "#07111f"
MUTED = "#64748b"
LINE = "#dbe5f1"
BLUE = "#2563eb"
RED = "#ef4444"
AMBER = "#f59e0b"
GREEN = "#16a34a"


def setup_matplotlib_style() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": "#f8fafc",
            "axes.facecolor": "#ffffff",
            "savefig.facecolor": "#f8fafc",
            "axes.edgecolor": LINE,
            "axes.labelcolor": MUTED,
            "axes.titlecolor": NAVY,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "font.family": "DejaVu Sans",
            "font.size": 10.5,
            "axes.titleweight": "bold",
        }
    )


def clean_axes(ax, grid_axis: str = "y") -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(LINE)
    ax.spines["bottom"].set_color(LINE)
    ax.grid(axis=grid_axis, color="#e6edf6", linewidth=1)
    ax.set_axisbelow(True)


def title_block(ax, title: str, subtitle: str) -> None:
    ax.set_title(title, loc="left", fontsize=18, pad=20)
    ax.text(0, 1.025, subtitle, transform=ax.transAxes, color=MUTED, fontsize=10.5)


def report_png_response(fig) -> Response:
    fig.tight_layout()
    buffer = BytesIO()
    fig.savefig(buffer, format="png", dpi=190, bbox_inches="tight")
    plt.close(fig)
    buffer.seek(0)
    return Response(
        content=buffer.getvalue(),
        media_type="image/png",
        headers={"Cache-Control": "no-store"},
    )


def metric_number(row: dict, key: str) -> float:
    return float(row.get(key) or 0)


@app.post("/auth/login")
def login(payload: LoginRequest):
    query = """
    SELECT
        U.user_id,
        U.email,
        U.user_name,
        U.user_role,
        S.student_id,
        Univ.university_name,
        C.country_name,
        FS.field_of_study
    FROM [User] U
    LEFT JOIN Student S ON U.user_id = S.usuario_id
    LEFT JOIN University Univ ON S.university_id = Univ.university_id
    LEFT JOIN Country C ON S.country_id = C.country_id
    OUTER APPLY (
        SELECT TOP 1 F.field_of_study
        FROM StudentAssessment SA
        INNER JOIN FieldOfStudy F ON SA.field_of_study_id = F.field_of_study_id
        WHERE SA.student_id = S.student_id
        ORDER BY SA.survey_number DESC, SA.Assessment_id DESC
    ) FS
    WHERE U.email = ? AND U.[password] = ?;
    """
    conn = connect()
    try:
        cur = conn.cursor()
        cur.execute(query, payload.email, payload.password)
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=401, detail="Credenciales no encontradas en SQL Server")
        user_id, email, user_name, user_role, student_id, university, country, field = row
        role_key = "student" if user_role == "estudiante" else ("employee" if "camila" in user_name else "universityAdmin")
        context = " / ".join(part for part in [university, field or country] if part) or "EduData Analytics"
        return {
            "authenticated": True,
            "user": {
                "user_id": user_id,
                "email": email,
                "user_name": user_name,
                "user_role": user_role,
                "role_key": role_key,
                "student_id": student_id,
                "context": context,
                "university": university,
                "country": country,
                "field_of_study": field,
            },
        }
    finally:
        conn.close()


@app.get("/auth/access-users")
def access_users():
    query = """
    WITH RankedUsers AS (
        SELECT
            U.user_id,
            U.email,
            U.user_name,
            U.[password],
            U.user_role,
            S.student_id,
            Univ.university_name,
            C.country_name,
            FS.field_of_study,
            ROW_NUMBER() OVER (
                PARTITION BY U.user_role
                ORDER BY U.user_id
            ) AS rn
        FROM [User] U
        LEFT JOIN Student S ON U.user_id = S.usuario_id
        LEFT JOIN University Univ ON S.university_id = Univ.university_id
        LEFT JOIN Country C ON S.country_id = C.country_id
        OUTER APPLY (
            SELECT TOP 1 F.field_of_study
            FROM StudentAssessment SA
            INNER JOIN FieldOfStudy F ON SA.field_of_study_id = F.field_of_study_id
            WHERE SA.student_id = S.student_id
            ORDER BY SA.survey_number DESC, SA.Assessment_id DESC
        ) FS
    )
    SELECT
        user_id,
        email,
        user_name,
        [password],
        user_role,
        student_id,
        university_name,
        country_name,
        field_of_study
    FROM RankedUsers
    WHERE user_role = 'administrador'
       OR (user_role = 'estudiante' AND rn <= 3)
    ORDER BY CASE WHEN user_role = 'estudiante' THEN 0 ELSE 1 END, user_id;
    """
    conn = connect()
    try:
        cur = conn.cursor()
        cur.execute(query)
        users = rows_as_dicts(cur)
        for user in users:
            user["role_key"] = "student" if user["user_role"] == "estudiante" else ("employee" if "camila" in user["user_name"] else "universityAdmin")
            user["context"] = " / ".join(
                part for part in [user.get("university_name"), user.get("field_of_study") or user.get("country_name")] if part
            ) or "EduData Analytics"
        return {"users": users}
    finally:
        conn.close()


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


@app.get("/dashboard/summary")
def dashboard_summary():
    global_query = """
    SELECT
        (SELECT COUNT(*) FROM Student) AS students,
        (SELECT COUNT(*) FROM University) AS universities,
        (SELECT COUNT(*) FROM Country) AS countries,
        (SELECT COUNT(*) FROM StudentAssessment) AS assessments,
        (SELECT COUNT(*) FROM Mide) AS metrics;
    """
    trend_query = """
    SELECT
        SA.survey_number,
        CAST(AVG(CASE WHEN MD.metric_name = 'digital_addiction_score' THEN M.metric_value END) AS DECIMAL(12,2)) AS digital_addiction,
        CAST(AVG(CASE WHEN MD.metric_name = 'wellbeing_percent' THEN M.metric_value END) AS DECIMAL(12,2)) AS wellbeing,
        CAST(AVG(CASE WHEN MD.metric_name = 'class_attendance_rate' THEN M.metric_value END) AS DECIMAL(12,2)) AS attendance,
        CAST(AVG(CASE WHEN MD.metric_name = 'stress_level' THEN M.metric_value END) AS DECIMAL(12,2)) AS stress
    FROM StudentAssessment SA
    INNER JOIN Mide M ON SA.Assessment_id = M.Assessment_id
    INNER JOIN MetricDefinition MD ON M.metric_id = MD.Metric_id
    WHERE MD.metric_name IN ('digital_addiction_score', 'wellbeing_percent', 'class_attendance_rate', 'stress_level')
    GROUP BY SA.survey_number
    ORDER BY SA.survey_number;
    """
    alert_query = """
    WITH UltimaEncuesta AS (
        SELECT
            SA.Assessment_id,
            SA.student_id,
            C.country_name,
            U.university_name,
            ROW_NUMBER() OVER (
                PARTITION BY SA.student_id
                ORDER BY SA.survey_number DESC, SA.Assessment_id DESC
            ) AS rn
        FROM StudentAssessment SA
        INNER JOIN Student S ON SA.student_id = S.student_id
        INNER JOIN University U ON S.university_id = U.university_id
        INNER JOIN Country C ON U.country_id = C.country_id
    ),
    Perfil AS (
        SELECT
            UE.country_name,
            UE.university_name,
            UE.student_id,
            MAX(CASE WHEN MD.metric_name = 'digital_addiction_score' THEN M.metric_value END) AS addiction,
            MAX(CASE WHEN MD.metric_name = 'wellbeing_percent' THEN M.metric_value END) AS wellbeing,
            MAX(CASE WHEN MD.metric_name = 'class_attendance_rate' THEN M.metric_value END) AS attendance,
            MAX(CASE WHEN MD.metric_name = 'stress_level' THEN M.metric_value END) AS stress
        FROM UltimaEncuesta UE
        INNER JOIN Mide M ON UE.Assessment_id = M.Assessment_id
        INNER JOIN MetricDefinition MD ON M.metric_id = MD.Metric_id
        WHERE UE.rn = 1
          AND MD.metric_name IN ('digital_addiction_score', 'wellbeing_percent', 'class_attendance_rate', 'stress_level')
        GROUP BY UE.country_name, UE.university_name, UE.student_id
    ),
    Riesgo AS (
        SELECT
            country_name,
            university_name,
            student_id,
            CASE WHEN addiction >= 25 OR wellbeing < 45 OR attendance < 80 OR stress >= 7 THEN 1 ELSE 0 END AS alert_flag,
            (addiction * 1.30) + (stress * 7.00) + ((100 - wellbeing) * 0.90) + ((100 - attendance) * 0.80) AS risk_score
        FROM Perfil
    )
    SELECT TOP 8
        university_name,
        country_name,
        COUNT(*) AS students,
        SUM(alert_flag) AS alerts,
        CAST(100.0 * SUM(alert_flag) / COUNT(*) AS DECIMAL(12,2)) AS alert_rate,
        CAST(AVG(risk_score) AS DECIMAL(12,2)) AS risk_score
    FROM Riesgo
    GROUP BY university_name, country_name
    HAVING COUNT(*) >= 25
    ORDER BY risk_score DESC, alert_rate DESC;
    """
    conn = connect()
    try:
        cur = conn.cursor()
        cur.execute(global_query)
        global_row = dict(zip([column[0] for column in cur.description], cur.fetchone()))
        cur.execute(trend_query)
        trend = rows_as_dicts(cur)
        cur.execute(alert_query)
        priority = rows_as_dicts(cur)
        latest = trend[-1] if trend else {}
        first = trend[0] if trend else {}
        return {
            "global": global_row,
            "latest": latest,
            "deltas": {
                "digital_addiction": round(float(latest.get("digital_addiction", 0)) - float(first.get("digital_addiction", 0)), 2),
                "wellbeing": round(float(latest.get("wellbeing", 0)) - float(first.get("wellbeing", 0)), 2),
            },
            "trend": trend,
            "priority_universities": priority,
        }
    finally:
        conn.close()


@app.get("/reports/dashboard")
def dashboard_report(
    report: str = Query("trend", pattern="^(trend|countries|universities|fields|intervention|uni_trend|uni_fields|uni_students)$"),
    period: str = Query("2025-1", pattern="^(2025-1|2025-2|Todos)$"),
    risk: str = Query("Todos", pattern="^(Todos|Alto|Medio|Bajo)$"),
    metric: str = Query("all", pattern="^(all|addiction|wellbeing|attendance|stress)$"),
    min_rate: float = Query(55, ge=0, le=100),
    limit: int = Query(12, ge=3, le=30),
    zone: str = Query("all", pattern="^(all|critical|prevention|monitoring)$"),
    university_name: str = Query("", max_length=200),
):
    if report.startswith("uni_"):
        return university_dashboard_report(report, period, risk, metric, limit, zone, university_name)

    survey_filter = period_condition("SA", period)
    latest_filter = period_condition("SA", period)
    report_meta = {
        "trend": {
            "title": "Tendencia de senales criticas",
            "insight": "Comparacion por encuesta de bienestar, asistencia, estres y adiccion.",
            "type": "line",
            "kpiLabel": "puntos de adiccion",
        },
        "countries": {
            "title": "Paises con mayor tasa de alerta",
            "insight": "Ultima encuesta por estudiante; alerta por bienestar, asistencia, estres o adiccion.",
            "type": "bars",
            "kpiLabel": "alerta maxima",
        },
        "universities": {
            "title": "Universidades priorizadas",
            "insight": "Score ponderado por adiccion, estres, bajo bienestar y baja asistencia.",
            "type": "bars",
            "kpiLabel": "casos prioritarios",
        },
        "fields": {
            "title": "Mapa de alertas por carrera",
            "insight": "Porcentaje de estudiantes que activa cada condicion de riesgo en la ultima encuesta.",
            "type": "heat",
            "kpiLabel": "carrera a revisar",
        },
        "intervention": {
            "title": "Matriz de decision ejecutiva",
            "insight": "X = tasa de alerta; Y = bienestar. Abajo/derecha indica intervencion.",
            "type": "matrix",
            "kpiLabel": "universidades criticas",
        },
    }
    queries = {
        "trend": f"""
            SELECT
                SA.survey_number AS label,
                CAST(AVG(CASE WHEN MD.metric_name = 'digital_addiction_score' THEN M.metric_value END) AS DECIMAL(12,2)) AS addiction,
                CAST(AVG(CASE WHEN MD.metric_name = 'wellbeing_percent' THEN M.metric_value END) AS DECIMAL(12,2)) AS wellbeing,
                CAST(AVG(CASE WHEN MD.metric_name = 'class_attendance_rate' THEN M.metric_value END) AS DECIMAL(12,2)) AS attendance,
                CAST(AVG(CASE WHEN MD.metric_name = 'stress_level' THEN M.metric_value END) AS DECIMAL(12,2)) AS stress
            FROM StudentAssessment SA
            INNER JOIN Mide M ON SA.Assessment_id = M.Assessment_id
            INNER JOIN MetricDefinition MD ON M.metric_id = MD.Metric_id
            WHERE MD.metric_name IN ('digital_addiction_score', 'wellbeing_percent', 'class_attendance_rate', 'stress_level')
              {survey_filter}
            GROUP BY SA.survey_number
            ORDER BY SA.survey_number;
        """,
        "countries": f"""
            WITH UltimaEncuesta AS (
                SELECT SA.Assessment_id, SA.student_id, C.country_name,
                       ROW_NUMBER() OVER (PARTITION BY SA.student_id ORDER BY SA.survey_number DESC, SA.Assessment_id DESC) AS rn
                FROM StudentAssessment SA
                INNER JOIN Student S ON SA.student_id = S.student_id
                INNER JOIN University U ON S.university_id = U.university_id
                INNER JOIN Country C ON U.country_id = C.country_id
                WHERE 1 = 1 {latest_filter}
            ),
            Perfil AS (
                SELECT UE.country_name, UE.student_id,
                       MAX(CASE WHEN MD.metric_name = 'digital_addiction_score' THEN M.metric_value END) AS adiccion,
                       MAX(CASE WHEN MD.metric_name = 'wellbeing_percent' THEN M.metric_value END) AS bienestar,
                       MAX(CASE WHEN MD.metric_name = 'class_attendance_rate' THEN M.metric_value END) AS asistencia,
                       MAX(CASE WHEN MD.metric_name = 'stress_level' THEN M.metric_value END) AS estres
                FROM UltimaEncuesta UE
                INNER JOIN Mide M ON UE.Assessment_id = M.Assessment_id
                INNER JOIN MetricDefinition MD ON M.metric_id = MD.Metric_id
                WHERE UE.rn = 1
                  AND MD.metric_name IN ('digital_addiction_score', 'wellbeing_percent', 'class_attendance_rate', 'stress_level')
                GROUP BY UE.country_name, UE.student_id
            ),
            Alertas AS (
                SELECT country_name, student_id,
                       CASE WHEN adiccion >= 25 OR bienestar < 45 OR asistencia < 80 OR estres >= 7 THEN 1 ELSE 0 END AS alerta
                FROM Perfil
            )
            SELECT TOP {limit} country_name AS label, COUNT(*) AS students, SUM(alerta) AS alerts,
                   CAST(100.0 * SUM(alerta) / COUNT(*) AS DECIMAL(12,2)) AS value
            FROM Alertas
            GROUP BY country_name
            HAVING COUNT(*) >= 80
               AND CAST(100.0 * SUM(alerta) / COUNT(*) AS DECIMAL(12,2)) >= {min_rate}
            ORDER BY value DESC, alerts DESC;
        """,
        "universities": f"""
            WITH UltimaEncuesta AS (
                SELECT SA.Assessment_id, SA.student_id, U.university_name, C.country_name,
                       ROW_NUMBER() OVER (PARTITION BY SA.student_id ORDER BY SA.survey_number DESC, SA.Assessment_id DESC) AS rn
                FROM StudentAssessment SA
                INNER JOIN Student S ON SA.student_id = S.student_id
                INNER JOIN University U ON S.university_id = U.university_id
                INNER JOIN Country C ON U.country_id = C.country_id
                WHERE 1 = 1 {latest_filter}
            ),
            Perfil AS (
                SELECT UE.university_name, UE.country_name, UE.student_id,
                       MAX(CASE WHEN MD.metric_name = 'digital_addiction_score' THEN M.metric_value END) AS adiccion,
                       MAX(CASE WHEN MD.metric_name = 'wellbeing_percent' THEN M.metric_value END) AS bienestar,
                       MAX(CASE WHEN MD.metric_name = 'class_attendance_rate' THEN M.metric_value END) AS asistencia,
                       MAX(CASE WHEN MD.metric_name = 'stress_level' THEN M.metric_value END) AS estres
                FROM UltimaEncuesta UE
                INNER JOIN Mide M ON UE.Assessment_id = M.Assessment_id
                INNER JOIN MetricDefinition MD ON M.metric_id = MD.Metric_id
                WHERE UE.rn = 1
                  AND MD.metric_name IN ('digital_addiction_score', 'wellbeing_percent', 'class_attendance_rate', 'stress_level')
                GROUP BY UE.university_name, UE.country_name, UE.student_id
            ),
            Riesgo AS (
                SELECT university_name, country_name, student_id,
                       CASE WHEN adiccion >= 25 OR bienestar < 45 OR asistencia < 80 OR estres >= 7 THEN 1 ELSE 0 END AS alerta,
                       (adiccion * 1.30) + (estres * 7.00) + ((100 - bienestar) * 0.90) + ((100 - asistencia) * 0.80) AS score_riesgo
                FROM Perfil
            )
            SELECT TOP {limit} university_name AS label, country_name, COUNT(*) AS students, SUM(alerta) AS alerts,
                   CAST(100.0 * SUM(alerta) / COUNT(*) AS DECIMAL(12,2)) AS alert_rate,
                   CAST(AVG(score_riesgo) AS DECIMAL(12,2)) AS value
            FROM Riesgo
            GROUP BY university_name, country_name
            HAVING COUNT(*) >= 25
            ORDER BY value DESC, alert_rate DESC;
        """,
        "fields": f"""
            WITH UltimaEncuesta AS (
                SELECT SA.Assessment_id, SA.student_id, F.field_of_study,
                       ROW_NUMBER() OVER (PARTITION BY SA.student_id ORDER BY SA.survey_number DESC, SA.Assessment_id DESC) AS rn
                FROM StudentAssessment SA
                INNER JOIN FieldOfStudy F ON SA.field_of_study_id = F.field_of_study_id
                WHERE 1 = 1 {latest_filter}
            ),
            Perfil AS (
                SELECT UE.field_of_study, UE.student_id,
                       MAX(CASE WHEN MD.metric_name = 'digital_addiction_score' THEN M.metric_value END) AS adiccion,
                       MAX(CASE WHEN MD.metric_name = 'wellbeing_percent' THEN M.metric_value END) AS bienestar,
                       MAX(CASE WHEN MD.metric_name = 'class_attendance_rate' THEN M.metric_value END) AS asistencia,
                       MAX(CASE WHEN MD.metric_name = 'stress_level' THEN M.metric_value END) AS estres
                FROM UltimaEncuesta UE
                INNER JOIN Mide M ON UE.Assessment_id = M.Assessment_id
                INNER JOIN MetricDefinition MD ON M.metric_id = MD.Metric_id
                WHERE UE.rn = 1
                  AND MD.metric_name IN ('digital_addiction_score', 'wellbeing_percent', 'class_attendance_rate', 'stress_level')
                GROUP BY UE.field_of_study, UE.student_id
            )
            SELECT field_of_study AS label,
                   CAST(100.0 * SUM(CASE WHEN adiccion >= 25 THEN 1 ELSE 0 END) / COUNT(*) AS DECIMAL(12,2)) AS addiction,
                   CAST(100.0 * SUM(CASE WHEN bienestar < 45 THEN 1 ELSE 0 END) / COUNT(*) AS DECIMAL(12,2)) AS wellbeing_low,
                   CAST(100.0 * SUM(CASE WHEN asistencia < 80 THEN 1 ELSE 0 END) / COUNT(*) AS DECIMAL(12,2)) AS attendance_low,
                   CAST(100.0 * SUM(CASE WHEN estres >= 7 THEN 1 ELSE 0 END) / COUNT(*) AS DECIMAL(12,2)) AS stress_high
            FROM Perfil
            GROUP BY field_of_study
            ORDER BY field_of_study;
        """,
        "intervention": f"""
            WITH UltimaEncuesta AS (
                SELECT SA.Assessment_id, SA.student_id, U.university_name, C.country_name,
                       ROW_NUMBER() OVER (PARTITION BY SA.student_id ORDER BY SA.survey_number DESC, SA.Assessment_id DESC) AS rn
                FROM StudentAssessment SA
                INNER JOIN Student S ON SA.student_id = S.student_id
                INNER JOIN University U ON S.university_id = U.university_id
                INNER JOIN Country C ON U.country_id = C.country_id
                WHERE 1 = 1 {latest_filter}
            ),
            Perfil AS (
                SELECT UE.university_name, UE.country_name, UE.student_id,
                       MAX(CASE WHEN MD.metric_name = 'digital_addiction_score' THEN M.metric_value END) AS adiccion,
                       MAX(CASE WHEN MD.metric_name = 'wellbeing_percent' THEN M.metric_value END) AS bienestar,
                       MAX(CASE WHEN MD.metric_name = 'class_attendance_rate' THEN M.metric_value END) AS asistencia,
                       MAX(CASE WHEN MD.metric_name = 'stress_level' THEN M.metric_value END) AS estres
                FROM UltimaEncuesta UE
                INNER JOIN Mide M ON UE.Assessment_id = M.Assessment_id
                INNER JOIN MetricDefinition MD ON M.metric_id = MD.Metric_id
                WHERE UE.rn = 1
                  AND MD.metric_name IN ('digital_addiction_score', 'wellbeing_percent', 'class_attendance_rate', 'stress_level')
                GROUP BY UE.university_name, UE.country_name, UE.student_id
            ),
            Riesgo AS (
                SELECT university_name, country_name, student_id, bienestar,
                       CASE WHEN adiccion >= 25 OR bienestar < 45 OR asistencia < 80 OR estres >= 7 THEN 1 ELSE 0 END AS alerta
                FROM Perfil
            )
            SELECT TOP {limit} university_name AS label, country_name, COUNT(*) AS students, SUM(alerta) AS alerts,
                   CAST(100.0 * SUM(alerta) / COUNT(*) AS DECIMAL(12,2)) AS x,
                   CAST(AVG(bienestar) AS DECIMAL(12,2)) AS y
            FROM Riesgo
            GROUP BY university_name, country_name
            HAVING COUNT(*) >= 25
            ORDER BY x DESC, y ASC;
        """,
    }
    conn = connect()
    try:
        cur = conn.cursor()
        cur.execute(queries[report])
        rows = normalize_rows(rows_as_dicts(cur))
    finally:
        conn.close()

    if report in {"trend", "uni_trend"}:
        for row in rows:
            row["label"] = f"E{int(row['label'])}"
            row["risk"] = risk_level_from_rate(float(row["addiction"]))
        if rows:
            kpi = f"+{float(rows[-1]['addiction']) - float(rows[0]['addiction']):.1f}"
        else:
            kpi = "0.0"
    elif report == "fields":
        for row in rows:
            score = float(row["addiction"]) + float(row["wellbeing_low"]) + float(row["attendance_low"]) + float(row["stress_high"])
            row["risk"] = risk_level_from_rate(score / 4)
        if rows:
            kpi = max(rows, key=lambda item: item["addiction"] + item["wellbeing_low"] + item["attendance_low"] + item["stress_high"])["label"]
        else:
            kpi = "-"
    elif report == "intervention":
        for row in rows:
            x_value = float(row["x"])
            y_value = float(row["y"])
            row["zone"] = "critical" if x_value >= 55 and y_value < 50 else "prevention" if x_value >= 55 or y_value < 50 else "monitoring"
            row["risk"] = "Alto" if row["zone"] == "critical" else "Medio" if row["zone"] == "prevention" else "Bajo"
        kpi = sum(1 for row in rows if row["risk"] == "Alto")
    else:
        for row in rows:
            row["risk"] = risk_level_from_rate(float(row.get("alert_rate", row["value"])))
        kpi = f"{float(rows[0]['value']):.1f}" if rows else "-"

    if risk != "Todos":
        rows = [row for row in rows if row["risk"] == risk]
    if report == "intervention" and zone != "all":
        rows = [row for row in rows if row.get("zone") == zone]
    return {
        "id": report,
        **report_meta[report],
        "period": period,
        "risk": risk,
        "metric": metric,
        "min_rate": min_rate,
        "limit": limit,
        "zone": zone,
        "kpi": kpi,
        "rows": rows,
    }


def resolve_university(cursor, university_name: str) -> tuple[int, str]:
    target = university_name or "Kuala Lumpur Institute of Technology"
    cursor.execute(
        """
        SELECT TOP 1 university_id, university_name
        FROM University
        WHERE university_name = ?
           OR university_name LIKE ?
        ORDER BY CASE WHEN university_name = ? THEN 0 ELSE 1 END, university_name;
        """,
        (target, f"%{target}%", target),
    )
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Universidad no encontrada")
    return int(row[0]), str(row[1])


def university_dashboard_report(
    report: str,
    period: str,
    risk: str,
    metric: str,
    limit: int,
    zone: str,
    university_name: str,
):
    latest_filter = period_condition("SA", period)
    meta = {
        "uni_trend": {
            "title": "Evolucion del riesgo estudiantil por encuesta",
            "insight": "Indicadores historicos filtrados solo por la universidad administrada.",
            "type": "line",
            "kpiLabel": "serie institucional",
        },
        "uni_fields": {
            "title": "Mapa de alertas por carrera",
            "insight": "Alertas internas por carrera dentro de la universidad administrada.",
            "type": "heat",
            "kpiLabel": "carrera a revisar",
        },
        "uni_students": {
            "title": "Matriz de intervencion estudiantil",
            "insight": "Estudiantes pseudonimizados priorizados por riesgo, bienestar y asistencia.",
            "type": "student_matrix",
            "kpiLabel": "estudiantes prioritarios",
        },
    }
    conn = connect()
    try:
        cur = conn.cursor()
        university_id, matched_university = resolve_university(cur, university_name)
        if report == "uni_trend":
            query = f"""
                SELECT
                    SA.survey_number AS label,
                    CAST(AVG(CASE WHEN MD.metric_name = 'digital_addiction_score' THEN M.metric_value END) AS DECIMAL(12,2)) AS addiction,
                    CAST(AVG(CASE WHEN MD.metric_name = 'wellbeing_percent' THEN M.metric_value END) AS DECIMAL(12,2)) AS wellbeing,
                    CAST(AVG(CASE WHEN MD.metric_name = 'class_attendance_rate' THEN M.metric_value END) AS DECIMAL(12,2)) AS attendance,
                    CAST(AVG(CASE WHEN MD.metric_name = 'stress_level' THEN M.metric_value END) AS DECIMAL(12,2)) AS stress
                FROM StudentAssessment SA
                INNER JOIN Student S ON SA.student_id = S.student_id
                INNER JOIN Mide M ON SA.Assessment_id = M.Assessment_id
                INNER JOIN MetricDefinition MD ON M.metric_id = MD.Metric_id
                WHERE S.university_id = ?
                  AND MD.metric_name IN ('digital_addiction_score', 'wellbeing_percent', 'class_attendance_rate', 'stress_level')
                  {latest_filter}
                GROUP BY SA.survey_number
                ORDER BY SA.survey_number;
            """
            cur.execute(query, (university_id,))
            rows = normalize_rows(rows_as_dicts(cur))
            for row in rows:
                row["label"] = f"E{int(row['label'])}"
                row["risk"] = risk_level_from_rate(float(row["addiction"]))
            kpi = f"{len(rows)} encuestas"
        elif report == "uni_fields":
            query = f"""
                WITH UltimaEncuesta AS (
                    SELECT SA.Assessment_id, SA.student_id, F.field_of_study,
                           ROW_NUMBER() OVER (PARTITION BY SA.student_id ORDER BY SA.survey_number DESC, SA.Assessment_id DESC) AS rn
                    FROM StudentAssessment SA
                    INNER JOIN Student S ON SA.student_id = S.student_id
                    INNER JOIN FieldOfStudy F ON SA.field_of_study_id = F.field_of_study_id
                    WHERE S.university_id = ? {latest_filter}
                ),
                Perfil AS (
                    SELECT UE.field_of_study, UE.student_id,
                           MAX(CASE WHEN MD.metric_name = 'digital_addiction_score' THEN M.metric_value END) AS adiccion,
                           MAX(CASE WHEN MD.metric_name = 'wellbeing_percent' THEN M.metric_value END) AS bienestar,
                           MAX(CASE WHEN MD.metric_name = 'class_attendance_rate' THEN M.metric_value END) AS asistencia,
                           MAX(CASE WHEN MD.metric_name = 'stress_level' THEN M.metric_value END) AS estres
                    FROM UltimaEncuesta UE
                    INNER JOIN Mide M ON UE.Assessment_id = M.Assessment_id
                    INNER JOIN MetricDefinition MD ON M.metric_id = MD.Metric_id
                    WHERE UE.rn = 1
                      AND MD.metric_name IN ('digital_addiction_score', 'wellbeing_percent', 'class_attendance_rate', 'stress_level')
                    GROUP BY UE.field_of_study, UE.student_id
                )
                SELECT field_of_study AS label,
                       CAST(100.0 * SUM(CASE WHEN adiccion >= 25 THEN 1 ELSE 0 END) / COUNT(*) AS DECIMAL(12,2)) AS addiction,
                       CAST(100.0 * SUM(CASE WHEN bienestar < 45 THEN 1 ELSE 0 END) / COUNT(*) AS DECIMAL(12,2)) AS wellbeing_low,
                       CAST(100.0 * SUM(CASE WHEN asistencia < 80 THEN 1 ELSE 0 END) / COUNT(*) AS DECIMAL(12,2)) AS attendance_low,
                       CAST(100.0 * SUM(CASE WHEN estres >= 7 THEN 1 ELSE 0 END) / COUNT(*) AS DECIMAL(12,2)) AS stress_high
                FROM Perfil
                GROUP BY field_of_study
                ORDER BY field_of_study;
            """
            cur.execute(query, (university_id,))
            rows = normalize_rows(rows_as_dicts(cur))
            for row in rows:
                score = float(row["addiction"]) + float(row["wellbeing_low"]) + float(row["attendance_low"]) + float(row["stress_high"])
                row["risk"] = risk_level_from_rate(score / 4)
            kpi = max(rows, key=lambda item: item["addiction"] + item["wellbeing_low"] + item["attendance_low"] + item["stress_high"])["label"] if rows else "-"
        else:
            query = f"""
                WITH UltimaEncuesta AS (
                    SELECT SA.Assessment_id, SA.student_id, F.field_of_study,
                           ROW_NUMBER() OVER (PARTITION BY SA.student_id ORDER BY SA.survey_number DESC, SA.Assessment_id DESC) AS rn
                    FROM StudentAssessment SA
                    INNER JOIN Student S ON SA.student_id = S.student_id
                    INNER JOIN FieldOfStudy F ON SA.field_of_study_id = F.field_of_study_id
                    WHERE S.university_id = ? {latest_filter}
                ),
                Perfil AS (
                    SELECT TOP {limit}
                           UE.student_id,
                           CONCAT('EST-', RIGHT(CONCAT('00000', UE.student_id), 5)) AS label,
                           UE.field_of_study,
                           MAX(CASE WHEN MD.metric_name = 'digital_addiction_score' THEN M.metric_value END) AS addiction,
                           MAX(CASE WHEN MD.metric_name = 'wellbeing_percent' THEN M.metric_value END) AS wellbeing,
                           MAX(CASE WHEN MD.metric_name = 'class_attendance_rate' THEN M.metric_value END) AS attendance,
                           MAX(CASE WHEN MD.metric_name = 'stress_level' THEN M.metric_value END) AS stress
                    FROM UltimaEncuesta UE
                    INNER JOIN Mide M ON UE.Assessment_id = M.Assessment_id
                    INNER JOIN MetricDefinition MD ON M.metric_id = MD.Metric_id
                    WHERE UE.rn = 1
                      AND MD.metric_name IN ('digital_addiction_score', 'wellbeing_percent', 'class_attendance_rate', 'stress_level')
                    GROUP BY UE.student_id, UE.field_of_study
                    ORDER BY
                      (MAX(CASE WHEN MD.metric_name = 'digital_addiction_score' THEN M.metric_value END) * 1.30)
                      + (MAX(CASE WHEN MD.metric_name = 'stress_level' THEN M.metric_value END) * 7.00)
                      + ((100 - MAX(CASE WHEN MD.metric_name = 'wellbeing_percent' THEN M.metric_value END)) * 0.90)
                      + ((100 - MAX(CASE WHEN MD.metric_name = 'class_attendance_rate' THEN M.metric_value END)) * 0.80) DESC
                )
                SELECT *,
                       CAST((addiction * 1.30) + (stress * 7.00) + ((100 - wellbeing) * 0.90) + ((100 - attendance) * 0.80) AS DECIMAL(12,2)) AS x,
                       CAST(wellbeing AS DECIMAL(12,2)) AS y,
                       (CASE WHEN addiction >= 25 THEN 1 ELSE 0 END
                        + CASE WHEN wellbeing < 45 THEN 1 ELSE 0 END
                        + CASE WHEN attendance < 80 THEN 1 ELSE 0 END
                        + CASE WHEN stress >= 7 THEN 1 ELSE 0 END) AS alerts
                FROM Perfil
                ORDER BY x DESC;
            """
            cur.execute(query, (university_id,))
            rows = normalize_rows(rows_as_dicts(cur))
            for row in rows:
                x_value = float(row["x"])
                y_value = float(row["y"])
                attendance = float(row["attendance"])
                row["zone"] = "critical" if x_value >= 85 and (y_value < 50 or attendance < 80) else "prevention" if x_value >= 70 or y_value < 55 else "monitoring"
                row["risk"] = "Alto" if row["zone"] == "critical" else "Medio" if row["zone"] == "prevention" else "Bajo"
            if zone != "all":
                rows = [row for row in rows if row.get("zone") == zone]
            kpi = len(rows)
        if risk != "Todos":
            rows = [row for row in rows if row["risk"] == risk]
        return {
            "id": report,
            **meta[report],
            "period": period,
            "risk": risk,
            "metric": metric,
            "limit": limit,
            "zone": zone,
            "university": matched_university,
            "kpi": kpi,
            "rows": rows,
        }
    finally:
        conn.close()


@app.get("/reports/chart.png")
def dashboard_report_chart(
    report: str = Query("trend", pattern="^(trend|countries|universities|fields|intervention|uni_trend|uni_fields|uni_students)$"),
    period: str = Query("2025-1", pattern="^(2025-1|2025-2|Todos)$"),
    risk: str = Query("Todos", pattern="^(Todos|Alto|Medio|Bajo)$"),
    metric: str = Query("all", pattern="^(all|addiction|wellbeing|attendance|stress)$"),
    min_rate: float = Query(55, ge=0, le=100),
    limit: int = Query(12, ge=3, le=30),
    zone: str = Query("all", pattern="^(all|critical|prevention|monitoring)$"),
    university_name: str = Query("", max_length=200),
):
    data = dashboard_report(report=report, period=period, risk=risk, metric=metric, min_rate=min_rate, limit=limit, zone=zone, university_name=university_name)
    rows = data["rows"]
    setup_matplotlib_style()

    if not rows:
        fig, ax = plt.subplots(figsize=(13.5, 6.2))
        title_block(ax, data["title"], "Consulta SQL sin registros para los filtros seleccionados")
        ax.text(0.5, 0.5, "Sin datos para este filtro", ha="center", va="center", color=MUTED, fontsize=18, transform=ax.transAxes)
        ax.set_xticks([])
        ax.set_yticks([])
        return report_png_response(fig)

    if report == "trend":
        x = list(range(1, len(rows) + 1))
        labels = [row["label"] for row in rows]
        addiction = [metric_number(row, "addiction") for row in rows]
        wellbeing = [metric_number(row, "wellbeing") for row in rows]
        attendance = [metric_number(row, "attendance") for row in rows]
        stress = [metric_number(row, "stress") * 10 for row in rows]
        fig, ax = plt.subplots(figsize=(13.5, 6.2))
        metric_lines = {
            "addiction": (addiction, RED, "Adiccion digital"),
            "wellbeing": (wellbeing, GREEN, "Bienestar"),
            "attendance": (attendance, BLUE, "Asistencia"),
            "stress": (stress, AMBER, "Estres x10"),
        }
        active_lines = metric_lines.items() if metric == "all" else [(metric, metric_lines[metric])]
        for _, (values, color, label) in active_lines:
            ax.plot(x, values, marker="o", linewidth=3.2, color=color, label=label)
        title = "Evolucion del riesgo estudiantil por encuesta" if report == "uni_trend" else "Reporte 1: evolucion de senales criticas"
        title_block(ax, title, data["insight"])
        ax.set_xlabel("Numero de encuesta")
        ax.set_ylabel("Escala comparable")
        ax.set_ylim(0, 100)
        ax.set_xticks(x, labels=labels)
        clean_axes(ax)
        ax.legend(frameon=False, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.12))
        if len(rows) > 1:
            addiction_change = addiction[-1] - addiction[0]
            wellbeing_change = wellbeing[-1] - wellbeing[0]
            ax.annotate(f"Adiccion +{addiction_change:.1f}", xy=(x[-1], addiction[-1]), xytext=(-120, -34), textcoords="offset points", arrowprops={"arrowstyle": "->", "color": RED}, color=RED, fontweight="bold")
            ax.annotate(f"Bienestar {wellbeing_change:.1f}", xy=(x[-1], wellbeing[-1]), xytext=(-120, 28), textcoords="offset points", arrowprops={"arrowstyle": "->", "color": GREEN}, color=GREEN, fontweight="bold")
        return report_png_response(fig)

    if report in {"countries", "universities"}:
        plot = list(reversed(rows))
        labels = [str(row["label"]).replace(" University", "").replace("Institute of Technology", "Inst. Tech")[:36] for row in plot]
        values = [metric_number(row, "value") for row in plot]
        colors = [RED if row["risk"] == "Alto" else AMBER if row["risk"] == "Medio" else BLUE for row in plot]
        fig, ax = plt.subplots(figsize=(13.5, 6.2))
        bars = ax.barh(labels, values, color=colors)
        title = "Reporte 2: paises con mayor tasa de alerta" if report == "countries" else "Reporte 3: universidades que requieren prioridad"
        title_block(ax, title, data["insight"])
        ax.set_xlabel("% de estudiantes con alerta" if report == "countries" else "Score de riesgo institucional")
        ax.set_xlim(0, max(values) + 8)
        clean_axes(ax, grid_axis="x")
        for bar, row in zip(bars, plot):
            if report == "countries":
                label = f"{bar.get_width():.1f}% ({int(row['alerts'])}/{int(row['students'])})"
            else:
                label = f"{bar.get_width():.1f} | {float(row.get('alert_rate', 0)):.1f}% alerta | {int(row['alerts'])} casos"
            ax.text(bar.get_width() + 0.8, bar.get_y() + bar.get_height() / 2, label, va="center", color=NAVY, fontsize=9.5)
        return report_png_response(fig)

    if report in {"fields", "uni_fields"}:
        metric_map = {
            "addiction": ("addiction", "Adiccion alta"),
            "wellbeing": ("wellbeing_low", "Bienestar bajo"),
            "attendance": ("attendance_low", "Asistencia baja"),
            "stress": ("stress_high", "Estres alto"),
        }
        selected_metrics = list(metric_map.values()) if metric == "all" else [metric_map[metric]]
        metrics = [item[0] for item in selected_metrics]
        labels = [item[1] for item in selected_metrics]
        matrix = np.array([[metric_number(row, key) for key in metrics] for row in rows])
        careers = [row["label"] for row in rows]
        fig, ax = plt.subplots(figsize=(13.5, 6.2))
        im = ax.imshow(matrix, cmap="YlOrRd", aspect="auto", vmin=0, vmax=max(30, float(matrix.max())))
        ax.set_xticks(np.arange(len(labels)), labels=labels)
        ax.set_yticks(np.arange(len(careers)), labels=careers)
        title = "Mapa de alertas por carrera de mi universidad" if report == "uni_fields" else "Reporte 4: mapa de alertas por carrera"
        title_block(ax, title, data["insight"])
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                ax.text(j, i, f"{matrix[i, j]:.1f}%", ha="center", va="center", color=NAVY, fontweight="bold", fontsize=9.5)
        cbar = fig.colorbar(im, ax=ax, pad=0.02)
        cbar.set_label("% estudiantes")
        for spine in ax.spines.values():
            spine.set_visible(False)
        return report_png_response(fig)

    if report == "uni_students":
        x = [metric_number(row, "x") for row in rows]
        y = [metric_number(row, "y") for row in rows]
        size = [max(metric_number(row, "alerts") * 95, 90) for row in rows]
        fields = sorted({str(row.get("field_of_study", "Sin carrera")) for row in rows})
        palette = [RED, BLUE, GREEN, AMBER, "#7c3aed", "#0891b2", "#db2777"]
        color_by_field = {field: palette[index % len(palette)] for index, field in enumerate(fields)}
        colors = [color_by_field[str(row.get("field_of_study", "Sin carrera"))] for row in rows]
        fig, ax = plt.subplots(figsize=(13.5, 6.4))
        ax.scatter(x, y, s=size, c=colors, alpha=0.82, edgecolor="#ffffff", linewidth=1.5)
        title_block(ax, "Matriz de intervencion estudiantil", data["insight"])
        ax.axvline(85, color=AMBER, linestyle="--", linewidth=1.4)
        ax.axhline(50, color=AMBER, linestyle="--", linewidth=1.4)
        for row in rows[:10]:
            ax.annotate(str(row["label"]), (metric_number(row, "x"), metric_number(row, "y")), xytext=(6, 4), textcoords="offset points", fontsize=8.5)
        for field, color in color_by_field.items():
            ax.scatter([], [], c=color, label=field)
        ax.legend(frameon=False, ncol=min(3, len(fields)), loc="upper center", bbox_to_anchor=(0.5, -0.12))
        ax.set_xlabel("Score de riesgo")
        ax.set_ylabel("Bienestar promedio")
        ax.set_xlim(min(x) - 4, max(x) + 8)
        ax.set_ylim(min(y) - 4, max(y) + 6)
        clean_axes(ax)
        return report_png_response(fig)

    x = [metric_number(row, "x") for row in rows]
    y = [metric_number(row, "y") for row in rows]
    size = [max(metric_number(row, "alerts") * 10, 60) for row in rows]
    colors = [RED if row["risk"] == "Alto" else AMBER if row["risk"] == "Medio" else BLUE for row in rows]
    fig, ax = plt.subplots(figsize=(13.5, 6.4))
    ax.scatter(x, y, s=size, c=colors, alpha=0.82, edgecolor="#ffffff", linewidth=1.5)
    title_block(ax, "Reporte 5: matriz de decision ejecutiva", data["insight"])
    ax.axvline(55, color=AMBER, linestyle="--", linewidth=1.4)
    ax.axhline(50, color=AMBER, linestyle="--", linewidth=1.4)
    for row in rows[:10]:
        label = str(row["label"]).replace(" University", "").replace("Institute of Technology", "Inst. Tech")[:18]
        ax.annotate(label, (metric_number(row, "x"), metric_number(row, "y")), xytext=(6, 4), textcoords="offset points", fontsize=8.5)
    ax.set_xlabel("% estudiantes con alerta")
    ax.set_ylabel("Bienestar promedio")
    ax.set_xlim(min(x) - 2, max(x) + 5)
    ax.set_ylim(min(y) - 2, max(y) + 2)
    clean_axes(ax)
    return report_png_response(fig)


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
