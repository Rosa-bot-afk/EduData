"""
Load the Excel dataset into SQL Server using pypyodbc, following the same
connection style shown in class.

Before running:
1. Create the tables with sql/01_create_tables.sql
2. Install dependencies:
   pip install -r requirements.txt
3. Copy .env.example to .env and edit the connection values.

Run from the project root:
   python scripts/load_excel_to_sql_server.py
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

import pandas as pd
import pypyodbc


ROOT = Path(__file__).resolve().parents[1]
EXCEL_PATH = ROOT / "data" / "official_students_longitudinal_90000_v2.xlsx"

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


load_env_file()

SERVER = os.getenv("SQL_SERVER", "localhost")
DATABASE = os.getenv("SQL_DATABASE", "StudentDigitalBehaviorDB")
USERNAME = os.getenv("SQL_USERNAME", "")
PASSWORD = os.getenv("SQL_PASSWORD", "")
DRIVER = os.getenv("SQL_DRIVER", "SQL Server")
AUTH_MODE = os.getenv("SQL_AUTH_MODE", "sql").lower()

BATCH_SIZE = 5000
MIDE_BATCH_SIZE = 50000
RESET_BEFORE_LOAD = os.getenv("RESET_BEFORE_LOAD", "no").lower() in ("1", "true", "yes", "si")

METRICS = [
    ("family_income_level", "socioeconomic", "coded_category"),
    ("internet_access_hours", "digital_access", "hours_per_day"),
    ("academic_motivation", "academic", "score_1_10"),
    ("social_media_hours", "digital_behavior", "hours_per_day"),
    ("sessions_per_day", "digital_behavior", "count_per_day"),
    ("average_session_length_minutes", "digital_behavior", "minutes"),
    ("late_night_usage", "digital_behavior", "coded_category"),
    ("education_content_hours", "content", "hours_per_day"),
    ("short_video_hours", "content", "hours_per_day"),
    ("entertainment_content_hours", "content", "hours_per_day"),
    ("news_content_hours", "content", "hours_per_day"),
    ("likes_given_per_day", "interaction", "count_per_day"),
    ("comments_written_per_day", "interaction", "count_per_day"),
    ("posts_created_per_week", "interaction", "count_per_week"),
    ("brain_rot_level", "wellbeing", "percent"),
    ("attention_span_minutes", "academic", "minutes"),
    ("study_hours_per_week", "academic", "hours_per_week"),
    ("class_attendance_rate", "academic", "percent"),
    ("productivity_score", "wellbeing", "score_0_10"),
    ("sleep_hours", "health", "hours_per_night"),
    ("stress_level", "health", "score_0_10"),
    ("anxiety_score", "health", "score_0_10"),
    ("depression_score", "health", "score_0_10"),
    ("ads_viewed_per_day", "advertising", "count_per_day"),
    ("ads_clicked_per_week", "advertising", "count_per_week"),
    ("impulse_purchase_scale", "spending", "score_0_10"),
    ("digital_spending_per_month", "spending", "money_per_month"),
    ("cyberbullying_exposure", "risk", "coded_boolean"),
    ("adult_content_exposure", "risk", "coded_boolean"),
    ("digital_addiction_score", "wellbeing", "score_0_100"),
    ("wellbeing_percent", "wellbeing", "percent"),
    ("perceived_financial_impact", "spending", "percent"),
]

CODE_MAPS = {
    "family_income_level": {"LOW": 1, "MIDDLE": 2, "HIGH": 3},
    "late_night_usage": {"Never": 0, "Sometimes": 1, "Often": 2, "Always": 3},
    "cyberbullying_exposure": {"No": 0, "Yes": 1},
    "adult_content_exposure": {"No": 0, "Yes": 1},
}


def connect():
    if AUTH_MODE == "windows":
        return pypyodbc.connect(
            f"""Driver={{{DRIVER}}};
Server={SERVER};
Database={DATABASE};
Trusted_Connection=yes;"""
        )

    return pypyodbc.connect(
        f"""Driver={{{DRIVER}}};
Server={SERVER};
Database={DATABASE};
UID={USERNAME};
PWD={PASSWORD};"""
    )


def chunks(values: list[tuple], size: int) -> Iterable[list[tuple]]:
    for start in range(0, len(values), size):
        yield values[start : start + size]


def run_many(cursor, sql: str, values: list[tuple], batch_size: int = BATCH_SIZE) -> None:
    if not values:
        return
    if batch_size == 1:
        for value in values:
            cursor.execute(sql, value)
        return
    for batch in chunks(values, batch_size):
        try:
            cursor.executemany(sql, batch)
        except Exception:
            raise


def clear_existing_data(cursor) -> None:
    tables = [
        "Mide",
        "StudentAssessment",
        "Employee",
        "Student_nacionality",
        "Nacionality",
        "MinorStudent",
        "AdultStudent",
        "Student",
        "[User]",
        "MetricDefinition",
        "FieldOfStudy",
        "AcademicPeriod",
        "DeviceType",
        "University",
        "CountryIndicator",
        "Country",
        "DevelopmentLevel",
    ]
    for table in tables:
        cursor.execute(f"DELETE FROM {table}")


def fetch_map(cursor, sql: str) -> dict:
    cursor.execute(sql)
    return {row[0]: row[1] for row in cursor.fetchall()}


def fetch_pair_map(cursor, sql: str) -> dict:
    cursor.execute(sql)
    return {(row[0], row[1]): row[2] for row in cursor.fetchall()}


def yes_no_or_none(value):
    if pd.isna(value):
        return None
    return str(value)


def metric_value(metric_name: str, raw_value):
    if metric_name in CODE_MAPS:
        return CODE_MAPS[metric_name][str(raw_value).strip()]
    return float(raw_value)


def sql_text(value: str) -> str:
    return "'" + str(value).replace("'", "''") + "'"


def require_empty_database(cursor) -> None:
    tables = [
        "Mide",
        "StudentAssessment",
        "Employee",
        "Student_nacionality",
        "Nacionality",
        "MinorStudent",
        "AdultStudent",
        "Student",
        "[User]",
        "MetricDefinition",
        "FieldOfStudy",
        "AcademicPeriod",
        "DeviceType",
        "University",
        "CountryIndicator",
        "Country",
        "DevelopmentLevel",
    ]
    not_empty = []
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        if cursor.fetchone()[0] > 0:
            not_empty.append(table)
    if not_empty:
        raise RuntimeError(
            "These tables already contain data: "
            + ", ".join(not_empty)
            + ". Use an empty database, or delete data intentionally before loading."
        )


def main() -> None:
    print("Reading Excel...")
    data = pd.read_excel(EXCEL_PATH, sheet_name="DATA")
    users = pd.read_excel(EXCEL_PATH, sheet_name="USERS")
    employees = pd.read_excel(EXCEL_PATH, sheet_name="EMPLOYEES")

    data = data.sort_values(["student_id", "survey_number"]).reset_index(drop=True)
    student_data = data.drop_duplicates("student_id").copy()

    conn = connect()
    cursor = conn.cursor()

    try:
        if RESET_BEFORE_LOAD:
            print("Cleaning existing data because RESET_BEFORE_LOAD=yes...")
            clear_existing_data(cursor)
            conn.commit()

        require_empty_database(cursor)

        print("Loading DevelopmentLevel...")
        development_values = sorted(data["development_level"].drop_duplicates())
        run_many(
            cursor,
            "INSERT INTO DevelopmentLevel (Development_level_name) VALUES (?)",
            [(x,) for x in development_values],
        )
        conn.commit()
        development_id = fetch_map(
            cursor,
            "SELECT Development_level_name, Development_Level_id FROM DevelopmentLevel",
        )

        print("Loading Country...")
        countries = (
            student_data[["Country", "development_level"]]
            .drop_duplicates()
            .sort_values("Country")
        )
        run_many(
            cursor,
            "INSERT INTO Country (country_name, development_id) VALUES (?, ?)",
            [(row.Country, development_id[row.development_level]) for row in countries.itertuples()],
        )
        conn.commit()
        country_id = fetch_map(cursor, "SELECT country_name, country_id FROM Country")

        print("Loading CountryIndicator...")
        country_indicators = (
            student_data[
                [
                    "Country",
                    "poverty_rate_percent",
                    "internet_infrastructure_index",
                    "average_internet_speed_mbps",
                ]
            ]
            .drop_duplicates("Country")
            .sort_values("Country")
        )
        run_many(
            cursor,
            """
            INSERT INTO CountryIndicator (
                indicator_year,
                poverty_rate_percent,
                internet_infrastructure_index,
                average_internet_speed_mbs,
                country_id
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (
                    2025,
                    float(row.poverty_rate_percent),
                    float(row.internet_infrastructure_index),
                    float(row.average_internet_speed_mbps),
                    country_id[row.Country],
                )
                for row in country_indicators.itertuples()
            ],
        )
        conn.commit()

        print("Loading University...")
        universities = (
            student_data[["Country", "University"]]
            .drop_duplicates()
            .sort_values(["Country", "University"])
        )
        run_many(
            cursor,
            "INSERT INTO University (university_name, university_type, country_id) VALUES (?, ?, ?)",
            [
                (row.University, "University", country_id[row.Country])
                for row in universities.itertuples()
            ],
        )
        conn.commit()
        university_id = fetch_pair_map(
            cursor,
            """
            SELECT c.country_name, u.university_name, u.university_id
            FROM University u
            INNER JOIN Country c ON c.country_id = u.country_id
            """,
        )

        print("Loading DeviceType...")
        devices = sorted(data["device_access"].drop_duplicates())
        run_many(
            cursor,
            "INSERT INTO DeviceType (Device_name) VALUES (?)",
            [(x,) for x in devices],
        )
        conn.commit()
        device_id = fetch_map(cursor, "SELECT Device_name, Device_type_id FROM DeviceType")

        print("Loading AcademicPeriod...")
        periods = (
            data[["AcademicPeriod", "start_date", "end_date"]]
            .drop_duplicates()
            .sort_values("AcademicPeriod")
        )
        run_many(
            cursor,
            """
            INSERT INTO AcademicPeriod (start_date, Period_year, period_term, end_date)
            VALUES (?, ?, ?, ?)
            """,
            [
                (
                    pd.to_datetime(row.start_date).date(),
                    int(str(row.AcademicPeriod).split("-")[0]),
                    int(str(row.AcademicPeriod).split("-")[1]),
                    pd.to_datetime(row.end_date).date(),
                )
                for row in periods.itertuples()
            ],
        )
        conn.commit()
        academic_period_id = fetch_pair_map(
            cursor,
            "SELECT Period_year, period_term, Academic_Period_id FROM AcademicPeriod",
        )

        print("Loading FieldOfStudy...")
        fields = sorted(data["field_of_study"].drop_duplicates())
        run_many(
            cursor,
            "INSERT INTO FieldOfStudy (field_of_study) VALUES (?)",
            [(x,) for x in fields],
        )
        conn.commit()
        field_id = fetch_map(cursor, "SELECT field_of_study, field_of_study_id FROM FieldOfStudy")

        print("Loading MetricDefinition...")
        run_many(
            cursor,
            "INSERT INTO MetricDefinition (metric_name, category, unit) VALUES (?, ?, ?)",
            METRICS,
        )
        conn.commit()
        metric_id = fetch_map(cursor, "SELECT metric_name, Metric_id FROM MetricDefinition")

        print("Loading User...")
        users_values = [
            (
                int(row.usuario_id),
                row.Email,
                row.User,
                row.Password,
                pd.to_datetime(row.Created_at).to_pydatetime(),
                row.Rol,
            )
            for row in users.itertuples()
        ]
        run_many(
            cursor,
            """
            INSERT INTO [User] (user_id, email, user_name, [password], created_at, user_role)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            users_values,
        )
        conn.commit()

        print("Loading Student...")
        for row in student_data.itertuples():
            cursor.execute(
                f"""
                INSERT INTO Student (student_id, gender, university_id, country_id, usuario_id)
                VALUES (
                    {int(row.student_id)},
                    {sql_text(row.Gender)},
                    {int(university_id[(row.Country, row.University)])},
                    {int(country_id[row.Country])},
                    {int(row.usuario_id)}
                )
                """
            )
        conn.commit()

        print("Loading Employee...")
        employee_user_by_employee_id = (
            users.dropna(subset=["employee_id"])
            .assign(employee_id=lambda df: df["employee_id"].astype(int))
            .set_index("employee_id")["usuario_id"]
            .to_dict()
        )
        employee_values = [
            (
                int(row.employee_id),
                row.First_name,
                row.LastName,
                pd.to_datetime(row.hire_date).date(),
                row.job_rol,
                int(employee_user_by_employee_id[int(row.employee_id)]),
            )
            for row in employees.itertuples()
        ]
        run_many(
            cursor,
            """
            INSERT INTO Employee (employee_id, First_name, LastName, hire_date, job_role, user_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            employee_values,
        )
        conn.commit()

        print("Loading AdultStudent and MinorStudent...")
        first_assessment = data.sort_values(["student_id", "survey_number"]).drop_duplicates("student_id")
        minors = first_assessment[first_assessment["Age"] < 18]
        adults = first_assessment[first_assessment["Age"] >= 18]
        adult_values = [
            (
                yes_no_or_none(row.autonomia_financiera),
                yes_no_or_none(row.trabaja_actualmente),
                int(row.student_id),
            )
            for row in adults.itertuples()
        ]
        minor_values = [
            (
                yes_no_or_none(row.tipo_tutor),
                yes_no_or_none(row.consentimiento_tutor),
                int(row.student_id),
            )
            for row in minors.itertuples()
        ]
        run_many(
            cursor,
            """
            INSERT INTO AdultStudent (financial_autonomy, is_employed, student_id)
            VALUES (?, ?, ?)
            """,
            adult_values,
        )
        run_many(
            cursor,
            """
            INSERT INTO MinorStudent (guardian_type, guardian_consent, student_id)
            VALUES (?, ?, ?)
            """,
            minor_values,
        )
        conn.commit()

        print("Loading Nacionality and Student_nacionality...")
        nationalities = sorted(student_data["Nationality"].drop_duplicates())
        run_many(
            cursor,
            "INSERT INTO Nacionality (nacionality_name) VALUES (?)",
            [(x,) for x in nationalities],
        )
        conn.commit()
        nationality_id = fetch_map(cursor, "SELECT nacionality_name, nacionality_id FROM Nacionality")
        student_nationality_values = [
            (nationality_id[row.Nationality], int(row.student_id))
            for row in student_data.itertuples()
        ]
        run_many(
            cursor,
            """
            INSERT INTO Student_nacionality (nacionality_id, student_id)
            VALUES (?, ?)
            """,
            student_nationality_values,
        )
        conn.commit()

        print("Loading StudentAssessment...")
        assessment_values = []
        for row in data.itertuples():
            period_year, period_term = str(row.AcademicPeriod).split("-")
            assessment_values.append(
                (
                    int(row.survey_number),
                    row.urban_rural,
                    row.education_level,
                    pd.to_datetime(row.sent_date).date(),
                    pd.to_datetime(row.reception_date).date(),
                    row.parents_divorced,
                    int(row.Age),
                    device_id[row.device_access],
                    academic_period_id[(int(period_year), int(period_term))],
                    field_id[row.field_of_study],
                    int(row.student_id),
                )
            )
        run_many(
            cursor,
            """
            INSERT INTO StudentAssessment (
                survey_number,
                urban_rural,
                education_level,
                sent_date,
                reception_date,
                parents_divorced,
                age,
                Device_type_id,
                academic_period_id,
                field_of_study_id,
                student_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            assessment_values,
        )
        conn.commit()
        assessment_id = fetch_pair_map(
            cursor,
            "SELECT student_id, survey_number, Assessment_id FROM StudentAssessment",
        )

        print("Loading Mide. This is the longest step...")
        mide_batch = []
        inserted_mide = 0
        for row in data.itertuples(index=False):
            row_dict = row._asdict()
            current_assessment_id = assessment_id[(int(row_dict["student_id"]), int(row_dict["survey_number"]))]
            for metric_name, _, _ in METRICS:
                mide_batch.append(
                    (
                        metric_id[metric_name],
                        current_assessment_id,
                        metric_value(metric_name, row_dict[metric_name]),
                    )
                )
            if len(mide_batch) >= MIDE_BATCH_SIZE:
                cursor.executemany(
                    """
                    INSERT INTO Mide (metric_id, Assessment_id, metric_value)
                    VALUES (?, ?, ?)
                    """,
                    mide_batch,
                )
                conn.commit()
                inserted_mide += len(mide_batch)
                print(f"  Mide rows inserted: {inserted_mide}")
                mide_batch.clear()
        if mide_batch:
            cursor.executemany(
                """
                INSERT INTO Mide (metric_id, Assessment_id, metric_value)
                VALUES (?, ?, ?)
                """,
                mide_batch,
            )
            conn.commit()
            inserted_mide += len(mide_batch)
            print(f"  Mide rows inserted: {inserted_mide}")

        print("Validating row counts...")
        expected_counts = {
            "Student": 15000,
            "StudentAssessment": 90000,
            "Mide": 90000 * len(METRICS),
            "[User]": len(users),
            "Employee": len(employees),
        }
        for table, expected in expected_counts.items():
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            actual = cursor.fetchone()[0]
            print(f"  {table}: {actual}")
            if actual != expected:
                raise RuntimeError(f"{table} expected {expected}, got {actual}")

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM (
                SELECT student_id
                FROM StudentAssessment
                GROUP BY student_id
                HAVING COUNT(*) = 6
            ) x
            """
        )
        completed_students = cursor.fetchone()[0]
        print(f"  Students with 6 assessments: {completed_students}")
        if completed_students != 15000:
            raise RuntimeError("Not every student has 6 assessments.")

        print("Done. Data loaded successfully.")

    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
