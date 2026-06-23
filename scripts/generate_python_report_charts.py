"""
Generate EduData report charts from SQL Server with pyodbc.

All aggregations, thresholds and rankings are calculated in SQL Server. Python
only reads the result sets and renders dashboard-ready PNG files.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pyodbc


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "web_app" / "frontend" / "assets" / "charts"
SUMMARY_PATH = OUTPUT_DIR / "report_summary.json"

NAVY = "#07111f"
MUTED = "#64748b"
LINE = "#dbe5f1"
BLUE = "#2563eb"
RED = "#ef4444"
AMBER = "#f59e0b"
GREEN = "#16a34a"


def load_env_file() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.strip().startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"'))


def connect():
    driver = os.getenv("SQL_DRIVER", "ODBC Driver 17 for SQL Server")
    server = os.getenv("SQL_SERVER", r"localhost\SQLEXPRESS")
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


def fetch_dicts(conn, query: str) -> list[dict]:
    cursor = conn.cursor()
    cursor.execute(query)
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def number(value) -> float:
    return float(value or 0)


def setup_style() -> None:
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


def save_chart(fig, filename: str) -> str:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    path = OUTPUT_DIR / filename
    fig.savefig(path, dpi=190, bbox_inches="tight")
    plt.close(fig)
    print(f"Created {path}")
    return f"assets/charts/{filename}"


def chart_signal_trend(conn) -> dict:
    rows = fetch_dicts(
        conn,
        """
        SELECT
            SA.survey_number,
            CAST(AVG(CASE WHEN MD.metric_name = 'digital_addiction_score' THEN M.metric_value END) AS DECIMAL(12,2)) AS adiccion_digital,
            CAST(AVG(CASE WHEN MD.metric_name = 'wellbeing_percent' THEN M.metric_value END) AS DECIMAL(12,2)) AS bienestar,
            CAST(AVG(CASE WHEN MD.metric_name = 'class_attendance_rate' THEN M.metric_value END) AS DECIMAL(12,2)) AS asistencia,
            CAST(AVG(CASE WHEN MD.metric_name = 'stress_level' THEN M.metric_value END) AS DECIMAL(12,2)) AS estres
        FROM StudentAssessment SA
        INNER JOIN Mide M ON SA.Assessment_id = M.Assessment_id
        INNER JOIN MetricDefinition MD ON M.metric_id = MD.Metric_id
        WHERE MD.metric_name IN ('digital_addiction_score', 'wellbeing_percent', 'class_attendance_rate', 'stress_level')
        GROUP BY SA.survey_number
        ORDER BY SA.survey_number;
        """,
    )
    x = [int(row["survey_number"]) for row in rows]
    addiction = [number(row["adiccion_digital"]) for row in rows]
    wellbeing = [number(row["bienestar"]) for row in rows]
    attendance = [number(row["asistencia"]) for row in rows]
    stress = [number(row["estres"]) * 10 for row in rows]

    fig, ax = plt.subplots(figsize=(13.5, 6.2))
    ax.plot(x, addiction, marker="o", linewidth=3.2, color=RED, label="Adiccion digital")
    ax.plot(x, wellbeing, marker="o", linewidth=3.2, color=GREEN, label="Bienestar")
    ax.plot(x, attendance, marker="o", linewidth=3.2, color=BLUE, label="Asistencia")
    ax.plot(x, stress, marker="o", linewidth=3.2, color=AMBER, label="Estres x10")
    title_block(ax, "Reporte 1: evolucion de senales criticas", "Comparacion por encuesta de bienestar, asistencia, estres y adiccion")
    ax.set_xlabel("Numero de encuesta")
    ax.set_ylabel("Escala comparable")
    ax.set_ylim(0, 100)
    ax.set_xticks(x)
    clean_axes(ax)
    ax.legend(frameon=False, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.12))

    addiction_change = addiction[-1] - addiction[0]
    wellbeing_change = wellbeing[-1] - wellbeing[0]
    ax.annotate(f"Adiccion +{addiction_change:.1f}", xy=(x[-1], addiction[-1]), xytext=(-120, -34), textcoords="offset points", arrowprops={"arrowstyle": "->", "color": RED}, color=RED, fontweight="bold")
    ax.annotate(f"Bienestar {wellbeing_change:.1f}", xy=(x[-1], wellbeing[-1]), xytext=(-120, 28), textcoords="offset points", arrowprops={"arrowstyle": "->", "color": GREEN}, color=GREEN, fontweight="bold")
    return {
        "id": "signal_trend",
        "title": "Tendencia de senales criticas",
        "insight": f"Adiccion digital sube {addiction_change:.1f} puntos y bienestar cae {abs(wellbeing_change):.1f} entre encuesta 1 y 6.",
        "image": save_chart(fig, "report_01_risk_by_survey.png"),
        "kpi": f"+{addiction_change:.1f}",
        "kpiLabel": "puntos de adiccion",
    }


def chart_country_alerts(conn) -> dict:
    rows = fetch_dicts(
        conn,
        """
        WITH UltimaEncuesta AS (
            SELECT SA.Assessment_id, SA.student_id, C.country_name,
                   ROW_NUMBER() OVER (PARTITION BY SA.student_id ORDER BY SA.survey_number DESC, SA.Assessment_id DESC) AS rn
            FROM StudentAssessment SA
            INNER JOIN Student S ON SA.student_id = S.student_id
            INNER JOIN University U ON S.university_id = U.university_id
            INNER JOIN Country C ON U.country_id = C.country_id
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
        SELECT TOP 12 country_name, COUNT(*) AS estudiantes, SUM(alerta) AS estudiantes_alerta,
               CAST(100.0 * SUM(alerta) / COUNT(*) AS DECIMAL(12,2)) AS tasa_alerta
        FROM Alertas
        GROUP BY country_name
        HAVING COUNT(*) >= 80
        ORDER BY tasa_alerta DESC, estudiantes_alerta DESC;
        """,
    )
    plot = list(reversed(rows))
    labels = [row["country_name"] for row in plot]
    rates = [number(row["tasa_alerta"]) for row in plot]
    colors = [RED if rate >= 58 else AMBER for rate in rates]

    fig, ax = plt.subplots(figsize=(13.5, 6.2))
    bars = ax.barh(labels, rates, color=colors)
    title_block(ax, "Reporte 2: paises con mayor tasa de alerta", "Ultima encuesta por estudiante; alerta por bienestar, asistencia, estres o adiccion")
    ax.set_xlabel("% de estudiantes con al menos una alerta")
    ax.set_xlim(0, max(70, max(rates) + 6))
    clean_axes(ax, grid_axis="x")
    for bar, row in zip(bars, plot):
        ax.text(bar.get_width() + 0.8, bar.get_y() + bar.get_height() / 2, f"{bar.get_width():.1f}% ({int(row['estudiantes_alerta'])}/{int(row['estudiantes'])})", va="center", color=NAVY, fontsize=9.5)
    top = rows[0]
    return {
        "id": "country_alerts",
        "title": "Paises con mas alerta",
        "insight": f"{top['country_name']} lidera con {number(top['tasa_alerta']):.1f}% de estudiantes en alerta.",
        "image": save_chart(fig, "report_02_field_indicators.png"),
        "kpi": f"{number(top['tasa_alerta']):.1f}%",
        "kpiLabel": f"alerta en {top['country_name']}",
    }


def chart_university_priority(conn) -> dict:
    rows = fetch_dicts(
        conn,
        """
        WITH UltimaEncuesta AS (
            SELECT SA.Assessment_id, SA.student_id, U.university_name, C.country_name,
                   ROW_NUMBER() OVER (PARTITION BY SA.student_id ORDER BY SA.survey_number DESC, SA.Assessment_id DESC) AS rn
            FROM StudentAssessment SA
            INNER JOIN Student S ON SA.student_id = S.student_id
            INNER JOIN University U ON S.university_id = U.university_id
            INNER JOIN Country C ON U.country_id = C.country_id
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
        SELECT TOP 12 university_name, country_name, COUNT(*) AS estudiantes, SUM(alerta) AS estudiantes_alerta,
               CAST(100.0 * SUM(alerta) / COUNT(*) AS DECIMAL(12,2)) AS tasa_alerta,
               CAST(AVG(score_riesgo) AS DECIMAL(12,2)) AS score_riesgo
        FROM Riesgo
        GROUP BY university_name, country_name
        HAVING COUNT(*) >= 25
        ORDER BY score_riesgo DESC, tasa_alerta DESC;
        """,
    )
    plot = list(reversed(rows))
    labels = [row["university_name"].replace(" University", "").replace("Institute of Technology", "Inst. Tech")[:34] for row in plot]
    scores = [number(row["score_riesgo"]) for row in plot]

    fig, ax = plt.subplots(figsize=(13.5, 6.4))
    bars = ax.barh(labels, scores, color=BLUE)
    title_block(ax, "Reporte 3: universidades que requieren prioridad", "Score ponderado por adiccion, estres, bajo bienestar y baja asistencia")
    ax.set_xlabel("Score de riesgo institucional")
    clean_axes(ax, grid_axis="x")
    ax.set_xlim(0, max(scores) + 35)
    for bar, row in zip(bars, plot):
        ax.text(bar.get_width() + 0.8, bar.get_y() + bar.get_height() / 2, f"{bar.get_width():.1f} | {number(row['tasa_alerta']):.1f}% alerta | {int(row['estudiantes_alerta'])} casos", va="center", color=NAVY, fontsize=9)
    top = rows[0]
    return {
        "id": "university_priority",
        "title": "Universidades priorizadas",
        "insight": f"{top['university_name']} debe revisarse primero por score compuesto.",
        "image": save_chart(fig, "report_03_university_accumulation.png"),
        "kpi": int(top["estudiantes_alerta"]),
        "kpiLabel": "casos en universidad #1",
    }


def chart_field_heatmap(conn) -> dict:
    rows = fetch_dicts(
        conn,
        """
        WITH UltimaEncuesta AS (
            SELECT SA.Assessment_id, SA.student_id, F.field_of_study,
                   ROW_NUMBER() OVER (PARTITION BY SA.student_id ORDER BY SA.survey_number DESC, SA.Assessment_id DESC) AS rn
            FROM StudentAssessment SA
            INNER JOIN FieldOfStudy F ON SA.field_of_study_id = F.field_of_study_id
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
        SELECT field_of_study,
               CAST(100.0 * SUM(CASE WHEN adiccion >= 25 THEN 1 ELSE 0 END) / COUNT(*) AS DECIMAL(12,2)) AS adiccion_alta,
               CAST(100.0 * SUM(CASE WHEN bienestar < 45 THEN 1 ELSE 0 END) / COUNT(*) AS DECIMAL(12,2)) AS bienestar_bajo,
               CAST(100.0 * SUM(CASE WHEN asistencia < 80 THEN 1 ELSE 0 END) / COUNT(*) AS DECIMAL(12,2)) AS asistencia_baja,
               CAST(100.0 * SUM(CASE WHEN estres >= 7 THEN 1 ELSE 0 END) / COUNT(*) AS DECIMAL(12,2)) AS estres_alto
        FROM Perfil
        GROUP BY field_of_study
        ORDER BY field_of_study;
        """,
    )
    metrics = ["adiccion_alta", "bienestar_bajo", "asistencia_baja", "estres_alto"]
    labels = ["Adiccion alta", "Bienestar bajo", "Asistencia baja", "Estres alto"]
    matrix = np.array([[number(row[key]) for key in metrics] for row in rows])
    careers = [row["field_of_study"] for row in rows]

    fig, ax = plt.subplots(figsize=(13.5, 6.2))
    im = ax.imshow(matrix, cmap="YlOrRd", aspect="auto", vmin=0, vmax=max(30, float(matrix.max())))
    ax.set_xticks(np.arange(len(labels)), labels=labels)
    ax.set_yticks(np.arange(len(careers)), labels=careers)
    title_block(ax, "Reporte 4: mapa de alertas por carrera", "Porcentaje de estudiantes que activa cada condicion de riesgo en la ultima encuesta")
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ax.text(j, i, f"{matrix[i, j]:.1f}%", ha="center", va="center", color=NAVY, fontweight="bold", fontsize=9.5)
    cbar = fig.colorbar(im, ax=ax, pad=0.02)
    cbar.set_label("% estudiantes")
    for spine in ax.spines.values():
        spine.set_visible(False)
    row_scores = matrix.sum(axis=1)
    weakest = careers[int(row_scores.argmax())]
    return {
        "id": "field_heatmap",
        "title": "Alertas por carrera",
        "insight": f"{weakest} concentra la mayor carga combinada de alertas.",
        "image": save_chart(fig, "report_04_prioritized_students.png"),
        "kpi": weakest,
        "kpiLabel": "carrera a revisar",
    }


def chart_action_matrix(conn) -> dict:
    rows = fetch_dicts(
        conn,
        """
        WITH UltimaEncuesta AS (
            SELECT SA.Assessment_id, SA.student_id, U.university_name, C.country_name,
                   ROW_NUMBER() OVER (PARTITION BY SA.student_id ORDER BY SA.survey_number DESC, SA.Assessment_id DESC) AS rn
            FROM StudentAssessment SA
            INNER JOIN Student S ON SA.student_id = S.student_id
            INNER JOIN University U ON S.university_id = U.university_id
            INNER JOIN Country C ON U.country_id = C.country_id
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
        SELECT TOP 16 university_name, country_name, COUNT(*) AS estudiantes, SUM(alerta) AS estudiantes_alerta,
               CAST(100.0 * SUM(alerta) / COUNT(*) AS DECIMAL(12,2)) AS tasa_alerta,
               CAST(AVG(bienestar) AS DECIMAL(12,2)) AS bienestar_promedio
        FROM Riesgo
        GROUP BY university_name, country_name
        HAVING COUNT(*) >= 25
        ORDER BY tasa_alerta DESC, bienestar_promedio ASC;
        """,
    )
    x = [number(row["tasa_alerta"]) for row in rows]
    y = [number(row["bienestar_promedio"]) for row in rows]
    size = [number(row["estudiantes_alerta"]) * 10 for row in rows]
    colors = [RED if rate >= 60 and wellbeing < 50 else AMBER if rate >= 55 else BLUE for rate, wellbeing in zip(x, y)]

    fig, ax = plt.subplots(figsize=(13.5, 6.4))
    ax.scatter(x, y, s=size, c=colors, alpha=0.82, edgecolor="#ffffff", linewidth=1.5)
    title_block(ax, "Reporte 5: matriz de decision ejecutiva", "X = tasa de alerta; Y = bienestar. Abajo/derecha indica intervencion")
    ax.axvline(55, color=AMBER, linestyle="--", linewidth=1.4)
    ax.axhline(50, color=AMBER, linestyle="--", linewidth=1.4)
    for row in rows[:10]:
        label = row["university_name"].replace(" University", "").replace("Institute of Technology", "Inst. Tech")[:18]
        ax.annotate(label, (number(row["tasa_alerta"]), number(row["bienestar_promedio"])), xytext=(6, 4), textcoords="offset points", fontsize=8.5)
    ax.set_xlabel("% estudiantes con alerta")
    ax.set_ylabel("Bienestar promedio")
    ax.set_xlim(min(x) - 2, max(x) + 5)
    ax.set_ylim(min(y) - 2, max(y) + 2)
    clean_axes(ax)
    critical = [row for row in rows if number(row["tasa_alerta"]) >= 55 and number(row["bienestar_promedio"]) < 50]
    return {
        "id": "action_matrix",
        "title": "Matriz de intervencion",
        "insight": f"{len(critical)} universidades caen en zona critica de intervencion.",
        "image": save_chart(fig, "report_05_executive_attendance.png"),
        "kpi": len(critical),
        "kpiLabel": "universidades criticas",
    }


def write_summary(reports: list[dict]) -> None:
    SUMMARY_PATH.write_text(json.dumps({"reports": reports}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Created {SUMMARY_PATH}")


def main() -> None:
    load_env_file()
    setup_style()
    conn = connect()
    try:
        reports = [
            chart_signal_trend(conn),
            chart_country_alerts(conn),
            chart_university_priority(conn),
            chart_field_heatmap(conn),
            chart_action_matrix(conn),
        ]
        write_summary(reports)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
