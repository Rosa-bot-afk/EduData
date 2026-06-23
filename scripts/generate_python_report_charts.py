"""
Generate Python visualizations for the EduData Analytics executive report.

The script reads the normalized SQL Server tables and exports PNG charts used
by the web app. Run it from the project root:

    python scripts/generate_python_report_charts.py
"""

from __future__ import annotations

import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import pypyodbc


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "web_app" / "frontend" / "assets" / "charts"
ADMIN_UNIVERSITY = os.getenv("REPORT_UNIVERSITY", "Kuala Lumpur Institute of Technology")


def load_env_file() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"'))


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


def read_sql(conn, query: str, params: tuple = ()) -> pd.DataFrame:
    cursor = conn.cursor()
    cursor.execute(query, params)
    columns = [column[0] for column in cursor.description]
    rows = cursor.fetchall()
    return pd.DataFrame.from_records(rows, columns=columns)


def setup_style() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": "#f8fafc",
            "axes.facecolor": "#ffffff",
            "axes.edgecolor": "#e2e8f0",
            "axes.labelcolor": "#64748b",
            "axes.titlecolor": "#0f172a",
            "xtick.color": "#64748b",
            "ytick.color": "#64748b",
            "font.family": "Segoe UI",
            "font.size": 11,
            "axes.titleweight": "bold",
        }
    )


def save_chart(fig, filename: str) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / filename, dpi=170, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"Created {OUTPUT_DIR / filename}")


def clean_axes(ax) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#e2e8f0")
    ax.spines["bottom"].set_color("#e2e8f0")
    ax.grid(axis="y", color="#e2e8f0", linewidth=1, alpha=0.8)
    ax.set_axisbelow(True)


def to_numeric(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    for column in columns:
        if column in df:
            df[column] = pd.to_numeric(df[column], errors="coerce")
    return df


def admin_trend(conn) -> None:
    query = """
    SELECT
        SA.survey_number,
        MIN(SA.sent_date) AS sent_date,
        MD.metric_name,
        AVG(M.metric_value) AS metric_average
    FROM University U
    INNER JOIN Student S ON U.university_id = S.university_id
    INNER JOIN StudentAssessment SA ON S.student_id = SA.student_id
    INNER JOIN Mide M ON SA.Assessment_id = M.Assessment_id
    INNER JOIN MetricDefinition MD ON M.metric_id = MD.Metric_id
    WHERE U.university_name = ?
      AND MD.metric_name IN ('wellbeing_percent', 'class_attendance_rate', 'digital_addiction_score')
    GROUP BY SA.survey_number, MD.metric_name
    ORDER BY SA.survey_number, MD.metric_name;
    """
    df = read_sql(conn, query, (ADMIN_UNIVERSITY,))
    df = to_numeric(df, ["metric_average"])
    pivot = df.pivot(index="survey_number", columns="metric_name", values="metric_average")
    labels = {
        "wellbeing_percent": "Bienestar",
        "class_attendance_rate": "Asistencia",
        "digital_addiction_score": "Adiccion digital",
    }
    colors = {
        "wellbeing_percent": "#2f8a5b",
        "class_attendance_rate": "#2857a4",
        "digital_addiction_score": "#db7a1f",
    }
    fig, ax = plt.subplots(figsize=(13.5, 6.4))
    for metric in labels:
        if metric in pivot:
            ax.fill_between(
                pivot.index,
                pivot[metric].astype(float),
                alpha=0.08,
                color=colors[metric],
            )
            ax.plot(
                pivot.index,
                pivot[metric],
                marker="o",
                markersize=8,
                linewidth=3.4,
                color=colors[metric],
                label=labels[metric],
            )
    ax.set_title("Evolucion temporal de indicadores clave", loc="left", fontsize=18, pad=16)
    ax.text(
        0,
        1.02,
        f"{ADMIN_UNIVERSITY} | seis entrevistas longitudinales",
        transform=ax.transAxes,
        color="#64748b",
        fontsize=11,
    )
    ax.set_xlabel("Entrevista")
    ax.set_ylabel("Promedio")
    ax.set_xticks(pivot.index)
    ax.set_xticklabels([f"E{int(x)}" for x in pivot.index])
    ax.set_ylim(0, 100)
    clean_axes(ax)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.24), ncol=3, frameon=False)
    save_chart(fig, "admin_trend_indicators.png")


def admin_risk_by_field(conn) -> None:
    query = """
    WITH latest AS (
        SELECT
            SA.Assessment_id,
            SA.student_id,
            SA.field_of_study_id,
            ROW_NUMBER() OVER (
                PARTITION BY SA.student_id
                ORDER BY SA.survey_number DESC, SA.Assessment_id DESC
            ) AS rn
        FROM StudentAssessment SA
        INNER JOIN Student S ON SA.student_id = S.student_id
        INNER JOIN University U ON S.university_id = U.university_id
        WHERE U.university_name = ?
    )
    SELECT
        F.field_of_study,
        CASE
            WHEN M.metric_value >= 70 THEN 'Alto'
            WHEN M.metric_value >= 40 THEN 'Medio'
            ELSE 'Bajo'
        END AS risk_level,
        COUNT(*) AS students
    FROM latest L
    INNER JOIN FieldOfStudy F ON L.field_of_study_id = F.field_of_study_id
    INNER JOIN Mide M ON L.Assessment_id = M.Assessment_id
    INNER JOIN MetricDefinition MD ON M.metric_id = MD.Metric_id
    WHERE L.rn = 1
      AND MD.metric_name = 'digital_addiction_score'
    GROUP BY
        F.field_of_study,
        CASE
            WHEN M.metric_value >= 70 THEN 'Alto'
            WHEN M.metric_value >= 40 THEN 'Medio'
            ELSE 'Bajo'
        END
    ORDER BY F.field_of_study;
    """
    df = read_sql(conn, query, (ADMIN_UNIVERSITY,))
    df = to_numeric(df, ["students"])
    pivot = df.pivot(index="field_of_study", columns="risk_level", values="students").fillna(0)
    for col in ["Bajo", "Medio", "Alto"]:
        if col not in pivot:
            pivot[col] = 0
    pivot = pivot[["Bajo", "Medio", "Alto"]]
    totals = pivot.sum(axis=1).sort_values(ascending=True)
    pivot = pivot.loc[totals.index]
    fig, ax = plt.subplots(figsize=(13.5, 6.4))
    left = pd.Series([0] * len(pivot), index=pivot.index)
    colors = {"Bajo": "#22c55e", "Medio": "#f59e0b", "Alto": "#ef4444"}
    for risk in ["Bajo", "Medio", "Alto"]:
        ax.barh(pivot.index, pivot[risk], left=left, color=colors[risk], label=risk, height=0.62)
        left += pivot[risk]
    ax.set_title("Composicion de riesgo digital por carrera", loc="left", fontsize=18, pad=16)
    ax.set_xlabel("Carrera")
    ax.set_ylabel("")
    clean_axes(ax)
    ax.grid(axis="x", color="#e2e8f0", linewidth=1, alpha=0.8)
    ax.grid(axis="y", visible=False)
    ax.legend(title="Riesgo", frameon=False, loc="lower right")
    save_chart(fig, "admin_risk_by_field.png")


def admin_field_profile(conn) -> None:
    query = """
    SELECT
        F.field_of_study,
        AVG(CASE WHEN MD.metric_name = 'class_attendance_rate' THEN M.metric_value END) AS attendance,
        AVG(CASE WHEN MD.metric_name = 'productivity_score' THEN M.metric_value END) AS productivity,
        AVG(CASE WHEN MD.metric_name = 'wellbeing_percent' THEN M.metric_value END) AS wellbeing
    FROM University U
    INNER JOIN Student S ON U.university_id = S.university_id
    INNER JOIN StudentAssessment SA ON S.student_id = SA.student_id
    INNER JOIN FieldOfStudy F ON SA.field_of_study_id = F.field_of_study_id
    INNER JOIN Mide M ON SA.Assessment_id = M.Assessment_id
    INNER JOIN MetricDefinition MD ON M.metric_id = MD.Metric_id
    WHERE U.university_name = ?
      AND SA.survey_number = 6
      AND MD.metric_name IN ('class_attendance_rate', 'productivity_score', 'wellbeing_percent')
    GROUP BY F.field_of_study
    ORDER BY F.field_of_study;
    """
    df = to_numeric(read_sql(conn, query, (ADMIN_UNIVERSITY,)), ["attendance", "productivity", "wellbeing"])
    fig, ax = plt.subplots(figsize=(13.5, 6.4))
    sizes = (df["productivity"].fillna(0).astype(float) + 8) * 18
    scatter = ax.scatter(
        df["attendance"],
        df["wellbeing"],
        s=sizes,
        c=df["productivity"],
        cmap="viridis",
        alpha=0.86,
        edgecolor="#ffffff",
        linewidth=1.6,
    )
    for _, row in df.iterrows():
        ax.annotate(
            row["field_of_study"],
            (row["attendance"], row["wellbeing"]),
            xytext=(8, 6),
            textcoords="offset points",
            fontsize=10,
            color="#334155",
        )
    ax.set_title("Mapa de rendimiento por carrera", loc="left", fontsize=18, pad=16)
    ax.set_xlabel("Asistencia promedio")
    ax.set_ylabel("Bienestar promedio")
    ax.set_xlim(max(0, float(df["attendance"].min()) - 8), min(100, float(df["attendance"].max()) + 8))
    ax.set_ylim(max(0, float(df["wellbeing"].min()) - 8), min(100, float(df["wellbeing"].max()) + 8))
    clean_axes(ax)
    cbar = fig.colorbar(scatter, ax=ax, pad=0.02)
    cbar.set_label("Productividad")
    save_chart(fig, "admin_field_profile.png")


def employee_country_wellbeing(conn) -> None:
    query = """
    SELECT TOP 10
        C.country_name,
        AVG(CASE WHEN MD.metric_name = 'wellbeing_percent' THEN M.metric_value END) AS wellbeing,
        AVG(CASE WHEN MD.metric_name = 'class_attendance_rate' THEN M.metric_value END) AS attendance,
        AVG(CASE WHEN MD.metric_name = 'productivity_score' THEN M.metric_value END) AS productivity,
        AVG(CASE WHEN MD.metric_name = 'digital_addiction_score' THEN M.metric_value END) AS digital_risk
    FROM Country C
    INNER JOIN University U ON C.country_id = U.country_id
    INNER JOIN Student S ON U.university_id = S.university_id
    INNER JOIN StudentAssessment SA ON S.student_id = SA.student_id
    INNER JOIN Mide M ON SA.Assessment_id = M.Assessment_id
    INNER JOIN MetricDefinition MD ON M.metric_id = MD.Metric_id
    WHERE MD.metric_name IN (
        'wellbeing_percent',
        'class_attendance_rate',
        'productivity_score',
        'digital_addiction_score'
    )
    GROUP BY C.country_name
    ORDER BY wellbeing DESC;
    """
    df = to_numeric(read_sql(conn, query), ["wellbeing", "attendance", "productivity", "digital_risk"])
    df = df.set_index("country_name")[["wellbeing", "attendance", "productivity", "digital_risk"]]
    fig, ax = plt.subplots(figsize=(13.5, 6.4))
    image = ax.imshow(df.values, cmap="YlGnBu", aspect="auto", vmin=0, vmax=100)
    ax.set_title("Mapa global de indicadores por pais", loc="left", fontsize=18, pad=16)
    ax.set_xticks(range(len(df.columns)))
    ax.set_xticklabels(["Bienestar", "Asistencia", "Productividad", "Riesgo digital"])
    ax.set_yticks(range(len(df.index)))
    ax.set_yticklabels(df.index)
    for row in range(df.shape[0]):
        for col in range(df.shape[1]):
            ax.text(col, row, f"{df.iloc[row, col]:.1f}", ha="center", va="center", color="#0f172a", fontsize=9)
    cbar = fig.colorbar(image, ax=ax, pad=0.02)
    cbar.set_label("Promedio")
    ax.spines[:].set_visible(False)
    save_chart(fig, "employee_country_wellbeing.png")


def employee_global_risk(conn) -> None:
    query = """
    WITH assessment_metrics AS (
        SELECT
            SA.Assessment_id,
            SA.survey_number,
            AVG(CASE WHEN MD.metric_name = 'digital_addiction_score' THEN M.metric_value END) AS digital_addiction_score,
            AVG(CASE WHEN MD.metric_name = 'stress_level' THEN M.metric_value END) AS stress_level,
            AVG(CASE WHEN MD.metric_name = 'wellbeing_percent' THEN M.metric_value END) AS wellbeing_percent
        FROM StudentAssessment SA
        INNER JOIN Mide M ON SA.Assessment_id = M.Assessment_id
        INNER JOIN MetricDefinition MD ON M.metric_id = MD.Metric_id
        WHERE MD.metric_name IN ('digital_addiction_score', 'stress_level', 'wellbeing_percent')
        GROUP BY SA.Assessment_id, SA.survey_number
    ),
    classified AS (
        SELECT
            survey_number,
            CASE
                WHEN digital_addiction_score >= 70
                  OR stress_level >= 8
                  OR wellbeing_percent < 40
                THEN 'Alto'
                WHEN digital_addiction_score >= 50
                  OR stress_level >= 6
                  OR wellbeing_percent < 60
                THEN 'Medio'
                ELSE 'Bajo'
            END AS risk_level
        FROM assessment_metrics
    )
    SELECT survey_number, risk_level, COUNT(*) AS students
    FROM classified
    GROUP BY survey_number, risk_level
    ORDER BY survey_number, risk_level;
    """
    df = to_numeric(read_sql(conn, query), ["students"])
    pivot = df.pivot(index="survey_number", columns="risk_level", values="students").fillna(0)
    for col in ["Bajo", "Medio", "Alto"]:
        if col not in pivot:
            pivot[col] = 0
    pivot = pivot[["Bajo", "Medio", "Alto"]]
    fig, ax = plt.subplots(figsize=(13.5, 6.4))
    ax.stackplot(
        pivot.index,
        pivot["Bajo"],
        pivot["Medio"],
        pivot["Alto"],
        labels=["Bajo", "Medio", "Alto"],
        colors=["#22c55e", "#f59e0b", "#ef4444"],
        alpha=0.86,
    )
    ax.set_title("Evolucion global de estudiantes por nivel de riesgo", loc="left", fontsize=18, pad=16)
    ax.set_xlabel("Entrevista")
    ax.set_ylabel("Estudiantes")
    ax.set_xticks(pivot.index)
    ax.set_xticklabels([f"E{int(x)}" for x in pivot.index])
    clean_axes(ax)
    ax.legend(loc="upper left", frameon=False, ncol=3)
    save_chart(fig, "employee_global_risk.png")


def employee_university_performance(conn) -> None:
    query = """
    SELECT TOP 10
        U.university_name,
        AVG(CASE WHEN MD.metric_name = 'class_attendance_rate' THEN M.metric_value END) AS attendance,
        AVG(CASE WHEN MD.metric_name = 'productivity_score' THEN M.metric_value END) AS productivity,
        AVG(CASE WHEN MD.metric_name = 'wellbeing_percent' THEN M.metric_value END) AS wellbeing
    FROM University U
    INNER JOIN Student S ON U.university_id = S.university_id
    INNER JOIN StudentAssessment SA ON S.student_id = SA.student_id
    INNER JOIN Mide M ON SA.Assessment_id = M.Assessment_id
    INNER JOIN MetricDefinition MD ON M.metric_id = MD.Metric_id
    WHERE MD.metric_name IN ('class_attendance_rate', 'productivity_score', 'wellbeing_percent')
    GROUP BY U.university_name
    HAVING AVG(CASE WHEN MD.metric_name = 'class_attendance_rate' THEN M.metric_value END) IS NOT NULL
    ORDER BY
        AVG(CASE WHEN MD.metric_name = 'wellbeing_percent' THEN M.metric_value END) DESC,
        AVG(CASE WHEN MD.metric_name = 'class_attendance_rate' THEN M.metric_value END) DESC;
    """
    df = to_numeric(read_sql(conn, query), ["attendance", "productivity", "wellbeing"])
    df["label"] = df["university_name"].str.replace(" University", "", regex=False).str.slice(0, 24)
    fig, ax = plt.subplots(figsize=(13.5, 6.4))
    sizes = (df["productivity"].fillna(0).astype(float) + 10) * 16
    scatter = ax.scatter(
        df["attendance"],
        df["wellbeing"],
        s=sizes,
        c=df["productivity"],
        cmap="plasma",
        alpha=0.82,
        edgecolor="#ffffff",
        linewidth=1.5,
    )
    for _, row in df.iterrows():
        ax.annotate(row["label"], (row["attendance"], row["wellbeing"]), xytext=(7, 5), textcoords="offset points", fontsize=9)
    ax.set_title("Universidades destacadas: asistencia vs bienestar", loc="left", fontsize=18, pad=16)
    ax.set_xlabel("Asistencia promedio")
    ax.set_ylabel("Bienestar promedio")
    ax.set_xlim(max(0, float(df["attendance"].min()) - 6), min(100, float(df["attendance"].max()) + 6))
    ax.set_ylim(max(0, float(df["wellbeing"].min()) - 6), min(100, float(df["wellbeing"].max()) + 6))
    clean_axes(ax)
    cbar = fig.colorbar(scatter, ax=ax, pad=0.02)
    cbar.set_label("Productividad")
    save_chart(fig, "employee_university_performance.png")


def main() -> None:
    load_env_file()
    setup_style()
    conn = connect()
    try:
        admin_trend(conn)
        admin_risk_by_field(conn)
        admin_field_profile(conn)
        employee_country_wellbeing(conn)
        employee_global_risk(conn)
        employee_university_performance(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
