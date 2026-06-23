/*
  SQL Server schema only for the student digital behavior survey project.
  This file creates only tables, primary keys, foreign keys, checks, and indexes.
  It does not insert any data.
*/

CREATE DATABASE StudentDigitalBehaviorDB;
GO

USE StudentDigitalBehaviorDB;
GO

CREATE TABLE DevelopmentLevel (
    Development_Level_id INT IDENTITY(1,1) NOT NULL,
    Development_level_name VARCHAR(50) NOT NULL,

    CONSTRAINT PK_DevelopmentLevel PRIMARY KEY (Development_Level_id),
    CONSTRAINT UQ_DevelopmentLevel_name UNIQUE (Development_level_name)
);
GO

CREATE TABLE Country (
    country_id INT IDENTITY(1,1) NOT NULL,
    country_name VARCHAR(100) NOT NULL,
    development_id INT NOT NULL,

    CONSTRAINT PK_Country PRIMARY KEY (country_id),
    CONSTRAINT UQ_Country_name UNIQUE (country_name),
    CONSTRAINT FK_Country_DevelopmentLevel
        FOREIGN KEY (development_id)
        REFERENCES DevelopmentLevel (Development_Level_id)
);
GO

CREATE TABLE CountryIndicator (
    Country_Indicator_id INT IDENTITY(1,1) NOT NULL,
    indicator_year SMALLINT NOT NULL,
    poverty_rate_percent DECIMAL(5,2) NOT NULL,
    internet_infrastructure_index DECIMAL(5,2) NOT NULL,
    average_internet_speed_mbs DECIMAL(8,2) NOT NULL,
    country_id INT NOT NULL,

    CONSTRAINT PK_CountryIndicator PRIMARY KEY (Country_Indicator_id),
    CONSTRAINT FK_CountryIndicator_Country
        FOREIGN KEY (country_id)
        REFERENCES Country (country_id),
    CONSTRAINT UQ_CountryIndicator_country_year UNIQUE (country_id, indicator_year),
    CONSTRAINT CK_CountryIndicator_poverty CHECK (poverty_rate_percent BETWEEN 0 AND 100),
    CONSTRAINT CK_CountryIndicator_infra CHECK (internet_infrastructure_index BETWEEN 0 AND 100),
    CONSTRAINT CK_CountryIndicator_speed CHECK (average_internet_speed_mbs >= 0)
);
GO

CREATE TABLE University (
    university_id INT IDENTITY(1,1) NOT NULL,
    university_name VARCHAR(200) NOT NULL,
    university_type VARCHAR(80) NULL,
    country_id INT NOT NULL,

    CONSTRAINT PK_University PRIMARY KEY (university_id),
    CONSTRAINT FK_University_Country
        FOREIGN KEY (country_id)
        REFERENCES Country (country_id),
    CONSTRAINT UQ_University_country_name UNIQUE (country_id, university_name)
);
GO

CREATE TABLE DeviceType (
    Device_type_id INT IDENTITY(1,1) NOT NULL,
    Device_name VARCHAR(50) NOT NULL,

    CONSTRAINT PK_DeviceType PRIMARY KEY (Device_type_id),
    CONSTRAINT UQ_DeviceType_name UNIQUE (Device_name),
    CONSTRAINT CK_DeviceType_name CHECK (Device_name IN ('Smartphone', 'Laptop', 'PC'))
);
GO

CREATE TABLE AcademicPeriod (
    Academic_Period_id INT IDENTITY(1,1) NOT NULL,
    start_date DATE NOT NULL,
    Period_year SMALLINT NOT NULL,
    period_term TINYINT NOT NULL,
    end_date DATE NOT NULL,

    CONSTRAINT PK_AcademicPeriod PRIMARY KEY (Academic_Period_id),
    CONSTRAINT UQ_AcademicPeriod_year_term UNIQUE (Period_year, period_term),
    CONSTRAINT CK_AcademicPeriod_term CHECK (period_term IN (1, 2)),
    CONSTRAINT CK_AcademicPeriod_dates CHECK (start_date < end_date)
);
GO

CREATE TABLE FieldOfStudy (
    field_of_study_id INT IDENTITY(1,1) NOT NULL,
    field_of_study VARCHAR(80) NOT NULL,

    CONSTRAINT PK_FieldOfStudy PRIMARY KEY (field_of_study_id),
    CONSTRAINT UQ_FieldOfStudy_name UNIQUE (field_of_study)
);
GO

CREATE TABLE MetricDefinition (
    Metric_id INT IDENTITY(1,1) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    category VARCHAR(80) NOT NULL,
    unit VARCHAR(50) NULL,

    CONSTRAINT PK_MetricDefinition PRIMARY KEY (Metric_id),
    CONSTRAINT UQ_MetricDefinition_name UNIQUE (metric_name)
);
GO

CREATE TABLE [User] (
    user_id INT NOT NULL,
    email VARCHAR(150) NOT NULL,
    user_name VARCHAR(100) NOT NULL,
    [password] VARCHAR(255) NOT NULL,
    created_at DATETIME2(0) NOT NULL,
    user_role VARCHAR(30) NOT NULL,

    CONSTRAINT PK_User PRIMARY KEY (user_id),
    CONSTRAINT UQ_User_email UNIQUE (email),
    CONSTRAINT UQ_User_name UNIQUE (user_name),
    CONSTRAINT CK_User_role CHECK (user_role IN ('estudiante', 'administrador'))
);
GO

CREATE TABLE Student (
    student_id INT NOT NULL,
    gender VARCHAR(20) NOT NULL,
    university_id INT NOT NULL,
    country_id INT NOT NULL,
    usuario_id INT NOT NULL,

    CONSTRAINT PK_Student PRIMARY KEY (student_id),
    CONSTRAINT UQ_Student_usuario UNIQUE (usuario_id),
    CONSTRAINT FK_Student_University
        FOREIGN KEY (university_id)
        REFERENCES University (university_id),
    CONSTRAINT FK_Student_Country
        FOREIGN KEY (country_id)
        REFERENCES Country (country_id),
    CONSTRAINT FK_Student_User
        FOREIGN KEY (usuario_id)
        REFERENCES [User] (user_id),
    CONSTRAINT CK_Student_gender CHECK (gender IN ('Female', 'Male', 'Other'))
);
GO

CREATE TABLE AdultStudent (
    adult_student_id INT IDENTITY(1,1) NOT NULL,
    financial_autonomy VARCHAR(3) NOT NULL,
    is_employed VARCHAR(3) NOT NULL,
    student_id INT NOT NULL,

    CONSTRAINT PK_AdultStudent PRIMARY KEY (adult_student_id),
    CONSTRAINT UQ_AdultStudent_student UNIQUE (student_id),
    CONSTRAINT FK_AdultStudent_Student
        FOREIGN KEY (student_id)
        REFERENCES Student (student_id),
    CONSTRAINT CK_AdultStudent_financial CHECK (financial_autonomy IN ('Yes', 'No')),
    CONSTRAINT CK_AdultStudent_employed CHECK (is_employed IN ('Yes', 'No'))
);
GO

CREATE TABLE MinorStudent (
    minor_student_id INT IDENTITY(1,1) NOT NULL,
    guardian_type VARCHAR(30) NOT NULL,
    guardian_consent VARCHAR(3) NOT NULL,
    student_id INT NOT NULL,

    CONSTRAINT PK_MinorStudent PRIMARY KEY (minor_student_id),
    CONSTRAINT UQ_MinorStudent_student UNIQUE (student_id),
    CONSTRAINT FK_MinorStudent_Student
        FOREIGN KEY (student_id)
        REFERENCES Student (student_id),
    CONSTRAINT CK_MinorStudent_guardian CHECK (guardian_type IN ('Father', 'Mother', 'Guardian')),
    CONSTRAINT CK_MinorStudent_consent CHECK (guardian_consent IN ('Yes', 'No'))
);
GO

CREATE TABLE Nacionality (
    nacionality_id INT IDENTITY(1,1) NOT NULL,
    nacionality_name VARCHAR(100) NOT NULL,

    CONSTRAINT PK_Nacionality PRIMARY KEY (nacionality_id),
    CONSTRAINT UQ_Nacionality_name UNIQUE (nacionality_name)
);
GO

CREATE TABLE Student_nacionality (
    nacionality_id INT NOT NULL,
    student_id INT NOT NULL,

    CONSTRAINT PK_Student_nacionality PRIMARY KEY (nacionality_id, student_id),
    CONSTRAINT FK_StudentNacionality_Nacionality
        FOREIGN KEY (nacionality_id)
        REFERENCES Nacionality (nacionality_id),
    CONSTRAINT FK_StudentNacionality_Student
        FOREIGN KEY (student_id)
        REFERENCES Student (student_id)
);
GO

CREATE TABLE Employee (
    employee_id INT NOT NULL,
    First_name VARCHAR(80) NOT NULL,
    LastName VARCHAR(80) NOT NULL,
    hire_date DATE NOT NULL,
    job_role VARCHAR(80) NOT NULL,
    user_id INT NOT NULL,

    CONSTRAINT PK_Employee PRIMARY KEY (employee_id),
    CONSTRAINT UQ_Employee_user UNIQUE (user_id),
    CONSTRAINT FK_Employee_User
        FOREIGN KEY (user_id)
        REFERENCES [User] (user_id),
    CONSTRAINT CK_Employee_job_role CHECK (job_role IN ('Academic Coordinator', 'Data Analyst', 'System Administrator'))
);
GO

CREATE TABLE StudentAssessment (
    Assessment_id BIGINT IDENTITY(1,1) NOT NULL,
    survey_number TINYINT NOT NULL,
    urban_rural VARCHAR(20) NOT NULL,
    education_level VARCHAR(30) NOT NULL,
    sent_date DATE NOT NULL,
    reception_date DATE NOT NULL,
    parents_divorced VARCHAR(3) NOT NULL,
    age TINYINT NOT NULL,
    Device_type_id INT NOT NULL,
    academic_period_id INT NOT NULL,
    field_of_study_id INT NOT NULL,
    student_id INT NOT NULL,

    CONSTRAINT PK_StudentAssessment PRIMARY KEY (Assessment_id),
    CONSTRAINT FK_StudentAssessment_DeviceType
        FOREIGN KEY (Device_type_id)
        REFERENCES DeviceType (Device_type_id),
    CONSTRAINT FK_StudentAssessment_AcademicPeriod
        FOREIGN KEY (academic_period_id)
        REFERENCES AcademicPeriod (Academic_Period_id),
    CONSTRAINT FK_StudentAssessment_FieldOfStudy
        FOREIGN KEY (field_of_study_id)
        REFERENCES FieldOfStudy (field_of_study_id),
    CONSTRAINT FK_StudentAssessment_Student
        FOREIGN KEY (student_id)
        REFERENCES Student (student_id),
    CONSTRAINT UQ_StudentAssessment_student_survey UNIQUE (student_id, survey_number),
    CONSTRAINT CK_StudentAssessment_survey CHECK (survey_number BETWEEN 1 AND 6),
    CONSTRAINT CK_StudentAssessment_urban CHECK (urban_rural IN ('Urban', 'Rural')),
    CONSTRAINT CK_StudentAssessment_education CHECK (education_level IN ('Undergraduate', 'Postgraduate')),
    CONSTRAINT CK_StudentAssessment_parents CHECK (parents_divorced IN ('Yes', 'No')),
    CONSTRAINT CK_StudentAssessment_age CHECK (age BETWEEN 16 AND 25),
    CONSTRAINT CK_StudentAssessment_dates CHECK (sent_date <= reception_date)
);
GO

CREATE TABLE Mide (
    metric_id INT NOT NULL,
    Assessment_id BIGINT NOT NULL,
    metric_value DECIMAL(12,2) NOT NULL,

    CONSTRAINT PK_Mide PRIMARY KEY (metric_id, Assessment_id),
    CONSTRAINT FK_Mide_MetricDefinition
        FOREIGN KEY (metric_id)
        REFERENCES MetricDefinition (Metric_id),
    CONSTRAINT FK_Mide_StudentAssessment
        FOREIGN KEY (Assessment_id)
        REFERENCES StudentAssessment (Assessment_id)
);
GO

CREATE INDEX IX_CountryIndicator_country_id ON CountryIndicator (country_id);
CREATE INDEX IX_University_country_id ON University (country_id);
CREATE INDEX IX_Student_country_id ON Student (country_id);
CREATE INDEX IX_Student_university_id ON Student (university_id);
CREATE INDEX IX_StudentAssessment_student_id ON StudentAssessment (student_id);
CREATE INDEX IX_StudentAssessment_period_id ON StudentAssessment (academic_period_id);
CREATE INDEX IX_Mide_Assessment_id ON Mide (Assessment_id);
GO
