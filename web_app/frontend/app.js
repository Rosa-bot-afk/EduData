const roleConfig = {
  student: {
    title: "Portal del estudiante",
    user: "student00001_tanzania",
    email: "student00001_tanzania@student.synthetic.edu",
    role: "Estudiante",
    university: "Northbridge University",
    fieldOfStudy: "Data Science",
    context: "Northbridge University · Data Science",
    kicker: "Seguimiento personal",
    heroTitle: "Completa tus encuestas y revisa tu progreso.",
    heroText: "Consulta tus indicadores de bienestar, productividad, uso digital y asistencia despues de cada envio.",
  },
  universityAdmin: {
    title: "Dashboard universidad",
    user: "admin.university",
    email: "admin.universidad@edudata.demo",
    role: "Admin universidad",
    university: "Kuala Lumpur Institute of Technology",
    fieldOfStudy: "No aplica",
    context: "Kuala Lumpur Institute of Technology",
    kicker: "Gestion institucional",
    heroTitle: "Monitorea cohortes, riesgos y progreso de tus estudiantes.",
    heroText: "Visualiza resultados agregados por periodo, carrera, universidad y categoria de riesgo.",
  },
  employee: {
    title: "Panel EduData Analytics",
    user: "camila.torres",
    email: "camila.torres@synthetic.edu",
    role: "Empleado EduData",
    university: "No aplica",
    fieldOfStudy: "No aplica",
    context: "EduData Analytics",
    kicker: "Vision global",
    heroTitle: "Administra clientes, usuarios y resultados multiuniversidad.",
    heroText: "Supervisa la operacion general, crea cuentas y analiza indicadores consolidados de todas las universidades.",
  },
};

const demoCredentials = {
  student: { email: "student00001_tanzania@student.synthetic.edu", password: "Pwd00001!2025" },
  universityAdmin: { email: "admin.universidad@edudata.demo", password: "AdminUniversidad001!" },
  employee: { email: "camila.torres@synthetic.edu", password: "AdminCamila003!" },
};

const state = {
  role: "student",
  selectedLoginRole: "student",
  authenticated: false,
  page: "dashboard",
  surveyCompleted: 3,
  draftSaved: false,
  reportPeriod: "2025-1",
  reportRisk: "Todos",
  reportEntity: "Todos los paises",
  predictionInput: {
    studentName: "Amina Kato",
    fieldOfStudy: "Law",
    poverty_rate_percent: 45,
    internet_infrastructure_index: 30,
    age: 22,
    internet_access_hours: 10,
    academic_motivation: 2,
    education_content_hours: 0.5,
    brain_rot_level: 9,
    attention_span_minutes: 8,
    study_hours_per_week: 3,
    class_attendance_rate: 55,
    development_level: "Underdeveloped",
    urban_rural: "Rural",
    family_income_level: "Low",
  },
  predictionResult: {
    dropout_probability_percent: 98.72,
    risk_level: "Alto",
    recommendation: "Derivar a seguimiento academico y bienestar universitario.",
  },
  predictionRanking: [
    { student: "Amina Kato", field_of_study: "Law", dropout_probability_percent: 98.72, risk_level: "Alto", recommendation: "Seguimiento inmediato" },
    { student: "Daniel Njoroge", field_of_study: "STEM", dropout_probability_percent: 78.41, risk_level: "Alto", recommendation: "Cita con tutor academico" },
    { student: "Lucia Ramos", field_of_study: "Business", dropout_probability_percent: 52.18, risk_level: "Medio", recommendation: "Monitoreo preventivo" },
    { student: "Mei Chen", field_of_study: "Medicine", dropout_probability_percent: 24.35, risk_level: "Bajo", recommendation: "Seguimiento regular" },
  ],
  predictionRankingLoaded: false,
  predictionRankingUniversity: "Kuala Lumpur Institute of Technology",
  predictionSource: "Demo local",
  passwords: {
    student: "Pwd00001!2025",
    universityAdmin: "AdminUniversidad001!",
    employee: "AdminCamila003!",
  },
  users: [
    ["student00001_tanzania", "student00001_tanzania@student.synthetic.edu", "Estudiante", "Northbridge University", "Data Science", "Activo"],
    ["admin.university", "admin.universidad@edudata.demo", "Admin universidad", "Northbridge University", "No aplica", "Activo"],
    ["camila.torres", "camila.torres@synthetic.edu", "Empleado EduData", "EduData Analytics", "No aplica", "Activo"],
  ],
  notices: {
    student: [
      ["Encuesta enviada", "Tu encuesta 3 fue registrada correctamente."],
      ["Proxima apertura", "La encuesta 4 estara disponible el 08 Ago 2025."],
      ["Progreso actualizado", "Ya puedes revisar tus indicadores personales."],
    ],
    universityAdmin: [
      ["Reporte actualizado", "Se actualizaron indicadores de bienestar y adiccion digital."],
      ["Usuarios pendientes", "4 estudiantes aun no activan sus credenciales."],
      ["Riesgo alto", "10 estudiantes requieren seguimiento prioritario."],
    ],
    employee: [
      ["Carga completada", "90,000 entrevistas procesadas en SQL Server."],
      ["Cliente nuevo", "Una universidad solicito credenciales iniciales."],
      ["Revision ejecutiva", "Reporte M5 listo para presentacion."],
    ],
  },
};

const reportRows = {
  student: [
    ["1", "2025-1", "64%", "42", "Bajo"],
    ["2", "2025-1", "66%", "45", "Medio"],
    ["3", "2025-1", "68%", "47", "Medio"],
    ["4", "2025-2", "-", "-", "Pendiente"],
  ],
  universityAdmin: [
    ["Medicine", "18", "88%", "73%", "Bajo"],
    ["Business", "16", "84%", "69%", "Medio"],
    ["STEM", "21", "81%", "66%", "Medio"],
    ["Law", "12", "76%", "58%", "Alto"],
  ],
  employee: [
    ["Northbridge University of Lima", "Peru", "82", "72%", "Bajo"],
    ["Crescent Brazil Institute", "Brazil", "91", "68%", "Medio"],
    ["Riverstone Tanzania Metropolitan University", "Tanzania", "86", "61%", "Alto"],
    ["Meridian Toronto University", "Canada", "94", "76%", "Bajo"],
  ],
};

document.body.classList.add("demo-locked");

function setRole(role) {
  state.role = role;
  state.page = "dashboard";
  renderApp();
}

function setPage(page) {
  state.page = page;
  renderApp();
}

function pageTitle() {
  const names = {
    dashboard: "Dashboard",
    survey: "Encuestas",
    reports: "Reportes",
    prediction: "Prediccion",
    users: "Usuarios",
  };
  return names[state.page];
}

function kpis() {
  if (state.role === "student") {
    return [
      ["Encuestas completadas", `${state.surveyCompleted} / 6`, "Siguiente apertura: 08 Ago"],
      ["Bienestar actual", state.surveyCompleted > 3 ? "71%" : "68%", "+4 vs encuesta anterior"],
      ["Riesgo digital", "Medio", "Atencion recomendada"],
      ["Asistencia", "91%", "Dentro del objetivo"],
    ];
  }
  if (state.role === "universityAdmin") {
    return [
      ["Estudiantes activos", "78", "Kuala Lumpur Institute of Technology"],
      ["Encuestas recibidas", "516", "100% completadas"],
      ["Riesgo alto", state.reportRisk === "Alto" ? "10 casos" : "12%", "-2 puntos vs periodo anterior"],
      ["Bienestar promedio", "71%", "+3 puntos"],
    ];
  }
  return [
    ["Universidades", "185", "50 paises"],
    ["Estudiantes", "15,000", "90,000 entrevistas"],
    ["Usuarios activos", String(state.users.length), "Demo en memoria"],
    ["Alertas criticas", "284", "Priorizadas por riesgo"],
  ];
}

function renderApp() {
  const role = roleConfig[state.role];
  if (state.page === "prediction" && state.role !== "universityAdmin") {
    state.page = "dashboard";
  }
  document.getElementById("page-title").textContent = `${role.title} · ${pageTitle()}`;
  document.getElementById("active-user").textContent = role.user;
  document.getElementById("active-role").textContent = role.role;
  document.getElementById("active-context").textContent = role.context;
  document.getElementById("sidebar-role").textContent = role.role;
  document.getElementById("sidebar-user").textContent = role.user;
  document.querySelectorAll(".nav-link").forEach((link) => {
    const page = link.getAttribute("href").replace("#", "");
    if (link.classList.contains("admin-only")) {
      link.hidden = state.role !== "universityAdmin";
    }
    link.classList.toggle("active", page === state.page);
  });
  document.getElementById("page-root").innerHTML = renderPage();
  bindPageEvents();
  const canvas = document.getElementById("trendCanvas");
  if (canvas) drawChart(canvas);
}

function renderPage() {
  if (state.page === "dashboard") return dashboardPage();
  if (state.page === "survey") return surveyPage();
  if (state.page === "reports") return reportsPage();
  if (state.page === "prediction") return predictionPage();
  return usersPage();
}

function hero() {
  const role = roleConfig[state.role];
  return `
    <section class="hero-band page-hero">
      <canvas id="trendCanvas" width="900" height="220" aria-label="Visualizacion ejecutiva"></canvas>
      <div class="hero-copy">
        <span>${role.kicker}</span>
        <h2>${role.heroTitle}</h2>
        <p>${role.heroText}</p>
      </div>
    </section>`;
}

function kpiGrid() {
  return `<section class="kpi-grid">${kpis()
    .map(([label, value, delta], index) => {
      const tone = index === 2 ? "warning" : "";
      return `<article class="kpi-card"><span>${label}</span><strong>${value}</strong><em class="delta ${tone}">${delta}</em></article>`;
    })
    .join("")}</section>`;
}

function noticesPanel() {
  return `
    <article class="panel">
      <div class="panel-header">
        <div><span class="eyebrow">Alertas</span><h3>Notificaciones</h3></div>
        <button class="icon-button" id="refresh-notices" title="Actualizar">↻</button>
      </div>
      <div class="timeline">${state.notices[state.role]
        .slice(0, 4)
        .map(([title, text]) => `<div class="notice"><strong>${title}</strong><span>${text}</span></div>`)
        .join("")}</div>
    </article>`;
}

function dashboardPage() {
  const body =
    state.role === "student"
      ? `
        <article class="panel primary-panel">
          <div class="panel-header"><div><span class="eyebrow">Resumen personal</span><h3>Tu progreso academico y digital</h3></div><span class="risk medium">Riesgo medio</span></div>
          <div class="demo-banner">Modo demo: puedes explorar y modificar valores visibles, sin guardar en SQL Server.</div>
          ${insights([["68%", "Bienestar"], ["47", "Adiccion digital"], ["22 h", "Estudio semanal"]])}
          <p>Tu bienestar mejoro respecto a la encuesta anterior, pero el uso digital nocturno sigue en observacion.</p>
          <div class="button-row"><button class="primary-button" data-page="survey">Responder encuesta</button><button class="secondary-button" data-page="reports">Ver progreso</button></div>
        </article>`
      : state.role === "universityAdmin"
        ? `
        <article class="panel primary-panel">
          <div class="panel-header"><div><span class="eyebrow">Reporte ejecutivo</span><h3>Kuala Lumpur Institute of Technology</h3></div><span class="risk low">Estable</span></div>
          <div class="demo-banner">Modo demo: filtros, usuarios y reportes cambian la pantalla, pero no hacen INSERT.</div>
          ${insights([["86", "Estudiantes"], ["12%", "Riesgo alto"], ["71%", "Bienestar"]])}
          <p>La universidad mantiene buen nivel de asistencia, con focos de intervencion en Law y STEM.</p>
          <div class="button-row"><button class="primary-button" data-page="prediction">Ver prediccion</button><button class="secondary-button" data-page="reports">Abrir reportes</button><button class="secondary-button" data-page="users">Gestionar usuarios</button></div>
        </article>`
        : `
        <article class="panel primary-panel">
          <div class="panel-header"><div><span class="eyebrow">Operacion global</span><h3>EduData Analytics</h3></div><span class="risk medium">284 alertas</span></div>
          <div class="demo-banner">Modo demo: supervision global simulada para presentar la propuesta.</div>
          ${insights([["185", "Universidades"], ["50", "Paises"], ["90k", "Entrevistas"]])}
          <p>La plataforma consolida indicadores multiuniversidad y permite priorizar intervenciones por riesgo.</p>
          <div class="button-row"><button class="primary-button" data-page="reports">Panel global</button><button class="secondary-button" data-page="users">Crear usuario</button></div>
        </article>`;
  return `<div class="page-stack">${hero()}${kpiGrid()}<section class="content-grid">${body}${noticesPanel()}</section></div>`;
}

function surveyPage() {
  if (state.role !== "student") {
    return `
      <div class="page-stack">
        <section class="page-heading"><span class="eyebrow">Encuestas</span><h2>Seguimiento de respuestas</h2><p>Este perfil revisa el avance de encuestas, no responde como estudiante.</p></section>
        ${kpiGrid()}
        <section class="content-grid">
          <article class="panel primary-panel">
            <div class="panel-header"><div><span class="eyebrow">Completitud</span><h3>Estado de encuestas por periodo</h3></div><span class="risk low">100%</span></div>
            ${insights([["516", "Respuestas"], ["0", "Pendientes criticos"], ["6/6", "Entrevistas"]])}
            <button class="primary-button" data-page="reports">Ver reporte de encuestas</button>
          </article>
          ${noticesPanel()}
        </section>
        ${tablePanel("Estado de encuestas", ["Encuesta", "Fecha", "Estado", "Bienestar", "Riesgo"], surveyRows())}
      </div>`;
  }
  const progress = Math.round((state.surveyCompleted / 6) * 100);
  return `
    <div class="page-stack">
      <section class="page-heading"><span class="eyebrow">Encuesta activa</span><h2>Encuesta ${Math.min(state.surveyCompleted + 1, 6)} - seguimiento estudiantil</h2><p>Completa y envia tu encuesta en la fecha asignada.</p></section>
      <section class="content-grid">
        <article class="panel primary-panel">
          <div class="panel-header"><div><span class="eyebrow">Formulario</span><h3>Datos academicos, digitales y bienestar</h3></div><span class="risk medium">${state.draftSaved ? "Borrador guardado" : "En progreso"}</span></div>
          <div class="demo-banner">En demo solo actualiza el progreso visual. No se guarda en SQL Server.</div>
          <div class="progress-bar"><span style="width: ${progress}%"></span></div>
          <div class="question-grid">
            <label>Horas en redes sociales <input id="social-hours" type="number" min="0" max="24" step="0.1" value="3.8" /></label>
            <label>Horas de sueno <input id="sleep-hours" type="number" min="0" max="24" step="0.1" value="6.7" /></label>
            <label>Nivel de estres <input id="stress-level" type="number" min="0" max="10" value="6" /></label>
            <label>Asistencia a clases <input id="attendance-rate" type="number" min="0" max="100" value="91" /></label>
            <label>Uso nocturno <select id="late-usage"><option>Never</option><option selected>Sometimes</option><option>Often</option><option>Always</option></select></label>
            <label>Gasto digital mensual <input id="digital-spend" type="number" min="0" value="42" /></label>
          </div>
          <div class="button-row"><button class="primary-button" id="submit-survey">Enviar encuesta</button><button class="secondary-button" id="save-draft">Guardar borrador</button></div>
        </article>
        ${noticesPanel()}
      </section>
      ${tablePanel("Estado de mis encuestas", ["Encuesta", "Fecha", "Estado", "Bienestar", "Riesgo"], surveyRows())}
    </div>`;
}

function reportsPage() {
  const head =
    state.role === "student"
      ? ["Encuesta", "Periodo", "Bienestar", "Adiccion digital", "Riesgo"]
      : state.role === "universityAdmin"
        ? ["Carrera", "Estudiantes", "Asistencia", "Bienestar", "Riesgo"]
        : ["Universidad", "Pais", "Estudiantes", "Bienestar", "Riesgo"];
  const rows = filteredReportRows();
  const entityFilter =
    state.role === "employee"
      ? `<label>Filtro global <select id="panel-entity"><option ${state.reportEntity === "Todos los paises" ? "selected" : ""}>Todos los paises</option><option ${state.reportEntity === "Top bienestar" ? "selected" : ""}>Top bienestar</option><option ${state.reportEntity === "Riesgo global" ? "selected" : ""}>Riesgo global</option><option ${state.reportEntity === "Universidades destacadas" ? "selected" : ""}>Universidades destacadas</option></select></label>`
      : "";
  return `
    <div class="page-stack">
      <section class="page-heading"><span class="eyebrow">Reportes</span><h2>Construyendo el reporte ejecutivo M5</h2><p>Filtra indicadores y revisa resultados para la toma de decisiones.</p></section>
      ${reportVisualizations()}
      <section class="content-grid">
        <article class="panel primary-panel">
          <div class="panel-header"><div><span class="eyebrow">Filtros</span><h3>Reporte parametrico</h3></div><span class="risk low">Interactivo</span></div>
          <div class="demo-banner">Cambia periodo y riesgo para actualizar la tabla de esta pagina.</div>
          <div class="question-grid">
            <label>Periodo <select id="panel-period"><option ${state.reportPeriod === "2025-1" ? "selected" : ""}>2025-1</option><option ${state.reportPeriod === "2025-2" ? "selected" : ""}>2025-2</option></select></label>
            <label>Riesgo <select id="panel-risk"><option ${state.reportRisk === "Todos" ? "selected" : ""}>Todos</option><option ${state.reportRisk === "Alto" ? "selected" : ""}>Alto</option><option ${state.reportRisk === "Medio" ? "selected" : ""}>Medio</option><option ${state.reportRisk === "Bajo" ? "selected" : ""}>Bajo</option></select></label>
            ${entityFilter}
          </div>
          ${insights([[state.reportPeriod, "Periodo"], [state.reportRisk, "Riesgo"], [state.role === "employee" ? state.reportEntity : "Universidad", "Alcance"]])}
          <button class="primary-button" id="apply-report-filter">Aplicar filtros</button>
        </article>
        ${noticesPanel()}
      </section>
      ${tablePanel("Reporte ejecutivo filtrado", head, rows)}
    </div>`;
}

function reportVisualizations() {
  if (state.role === "student") {
    return "";
  }
  const adminCharts = [
    ["Evolucion por encuesta", "Bienestar, asistencia y adiccion digital para la universidad.", "assets/charts/admin_trend_indicators.png"],
    ["Riesgo por carrera", "Distribucion bajo, medio y alto usando la metrica digital_addiction_score.", "assets/charts/admin_risk_by_field.png"],
    ["Perfil por carrera", "Comparacion ejecutiva de asistencia, productividad y bienestar.", "assets/charts/admin_field_profile.png"],
  ];
  const employeeCharts = [
    ["Top paises por bienestar", "Vista global para comparar rendimiento entre paises cliente.", "assets/charts/employee_country_wellbeing.png", "Top bienestar"],
    ["Riesgo global", "Cantidad de estudiantes por categoria de riesgo en toda la cartera.", "assets/charts/employee_global_risk.png", "Riesgo global"],
    ["Universidades destacadas", "Ranking ejecutivo por asistencia, productividad y bienestar.", "assets/charts/employee_university_performance.png", "Universidades destacadas"],
  ];
  const charts = state.role === "universityAdmin"
    ? adminCharts
    : employeeCharts.filter((chart) => state.reportEntity === "Todos los paises" || chart[3] === state.reportEntity);
  const subtitle =
    state.role === "universityAdmin"
      ? "Graficos generados en Python para Kuala Lumpur Institute of Technology."
      : `Graficos generados en Python con vista general. Filtro activo: ${state.reportEntity}.`;
  return `
    <section class="chart-section">
      <div class="report-visual-header">
        <div>
          <span class="eyebrow">Visualizaciones Python</span>
          <h3>Reporte ejecutivo grafico</h3>
          <p>${subtitle}</p>
        </div>
        <span class="risk low">Python + SQL Server</span>
      </div>
      <div class="chart-grid">
        ${charts
          .map(
            ([title, description, src], index) => `
          <article class="chart-card ${index === 0 ? "featured-chart" : ""}">
            <img src="${src}" alt="${title}" />
            <div>
              <strong>${title}</strong>
              <span>${description}</span>
            </div>
          </article>`
          )
          .join("")}
      </div>
    </section>`;
}

function predictionPage() {
  const result = state.predictionResult;
  const probability = Number(result.dropout_probability_percent || 0);
  const riskClass = result.risk_level === "Alto" ? "high" : result.risk_level === "Medio" ? "medium" : "low";
  return `
    <div class="page-stack prediction-page">
      <section class="page-heading">
        <span class="eyebrow">Modelo predictivo</span>
        <h2>Prediccion de riesgo de desercion</h2>
        <p>Evalua estudiantes de ${state.predictionRankingUniversity} para priorizar seguimiento academico y bienestar universitario.</p>
      </section>
      <section class="content-grid prediction-layout">
        <article class="panel primary-panel">
          <div class="panel-header">
            <div><span class="eyebrow">Simulador para admin universidad</span><h3>Datos del estudiante</h3></div>
            <span class="risk ${riskClass}">${result.risk_level}</span>
          </div>
          <div class="demo-banner prediction-note">Ranking conectado a SQL Server con estudiantes reales de la universidad.</div>
          <div class="question-grid">
            <label>Estudiante <input id="predict-student-name" value="${state.predictionInput.studentName}" /></label>
            <label>Carrera <select id="predict-field"><option ${selected("Law", state.predictionInput.fieldOfStudy)}>Law</option><option ${selected("Medicine", state.predictionInput.fieldOfStudy)}>Medicine</option><option ${selected("Business", state.predictionInput.fieldOfStudy)}>Business</option><option ${selected("STEM", state.predictionInput.fieldOfStudy)}>STEM</option></select></label>
            <label class="model-extra-field">Edad <input id="predict-age" type="number" min="14" max="80" value="${state.predictionInput.age}" /></label>
            <label>Asistencia a clases (%) <input id="predict-attendance" type="number" min="0" max="100" value="${state.predictionInput.class_attendance_rate}" /></label>
            <label>Motivacion academica (0-10) <input id="predict-motivation" type="number" min="0" max="10" value="${state.predictionInput.academic_motivation}" /></label>
            <label>Horas de estudio semanal <input id="predict-study-hours" type="number" min="0" max="80" step="0.5" value="${state.predictionInput.study_hours_per_week}" /></label>
            <label>Horas diarias de internet <input id="predict-internet-hours" type="number" min="0" max="24" step="0.5" value="${state.predictionInput.internet_access_hours}" /></label>
            <label>Brain rot (0-10) <input id="predict-brain-rot" type="number" min="0" max="10" value="${state.predictionInput.brain_rot_level}" /></label>
            <label class="model-extra-field">Atencion (minutos) <input id="predict-attention" type="number" min="1" max="180" value="${state.predictionInput.attention_span_minutes}" /></label>
            <label class="model-extra-field">Contenido educativo (horas) <input id="predict-education-content" type="number" min="0" max="80" step="0.5" value="${state.predictionInput.education_content_hours}" /></label>
            <label class="model-extra-field">Pobreza del pais (%) <input id="predict-poverty" type="number" min="0" max="100" value="${state.predictionInput.poverty_rate_percent}" /></label>
            <label class="model-extra-field">Infraestructura internet <input id="predict-infrastructure" type="number" min="0" max="100" value="${state.predictionInput.internet_infrastructure_index}" /></label>
            <label class="model-extra-field">Desarrollo <select id="predict-development"><option ${selected("Developed", state.predictionInput.development_level)}>Developed</option><option ${selected("Underdeveloped", state.predictionInput.development_level)}>Underdeveloped</option></select></label>
            <label class="model-extra-field">Zona <select id="predict-zone"><option ${selected("Urban", state.predictionInput.urban_rural)}>Urban</option><option ${selected("Rural", state.predictionInput.urban_rural)}>Rural</option></select></label>
            <label class="model-extra-field">Ingreso familiar <select id="predict-income"><option ${selected("Low", state.predictionInput.family_income_level)}>Low</option><option ${selected("Middle", state.predictionInput.family_income_level)}>Middle</option><option ${selected("High", state.predictionInput.family_income_level)}>High</option></select></label>
          </div>
          <div class="button-row"><button class="primary-button" id="run-prediction">Calcular riesgo</button><button class="secondary-button" id="load-risk-ranking">Cargar ranking real</button><button class="secondary-button" id="load-high-risk-demo">Cargar caso critico</button></div>
        </article>
        <article class="panel prediction-card">
          <span class="eyebrow">Resultado</span>
          <div class="risk-score">${probability.toFixed(2)}%</div>
          <span class="risk ${riskClass}">Riesgo ${result.risk_level}</span>
          <p>${result.recommendation}</p>
          <small>Fuente: ${state.predictionSource}</small>
        </article>
      </section>
      ${tablePanel("Estudiantes priorizados por el modelo", ["Estudiante", "Carrera", "Probabilidad", "Riesgo", "Accion sugerida"], predictionRows())}
    </div>`;
}

function usersPage() {
  const role = roleConfig[state.role];
  if (state.role === "student") {
    return `
      <div class="page-stack">
        <section class="page-heading"><span class="eyebrow">Usuarios</span><h2>Mi cuenta</h2><p>Consulta el estado de tu acceso a EduData Analytics.</p></section>
        <article class="panel primary-panel">
          ${accountProfile()}
          ${insights([["Activo", "Estado"], [role.role, "Rol"], ["Demo", "Modo"]])}
          <p>Los estudiantes no crean usuarios. Esa accion corresponde a administradores autorizados.</p>
          <div class="button-row"><button class="primary-button" id="change-password-inline">Cambiar contraseña</button></div>
        </article>
      </div>`;
  }
  return `
    <div class="page-stack">
      <section class="page-heading"><span class="eyebrow">Gestion de usuarios</span><h2>Crear y revisar accesos</h2><p>Agrega usuarios demo y revisa la lista en pantalla.</p></section>
      <section class="content-grid">
        <article class="panel primary-panel">
          <div class="panel-header"><div><span class="eyebrow">Nuevo usuario</span><h3>Alta simulada</h3></div><span class="risk medium">Sin SQL</span></div>
          <div class="demo-banner">El usuario se agrega a la tabla visual de abajo. No se guarda en la base.</div>
          <div class="question-grid">
            <label>Correo <input id="new-email" type="email" placeholder="nuevo@universidad.edu" /></label>
            <label>Rol <select id="new-role"><option>Estudiante</option><option>Admin universidad</option><option>Empleado EduData</option></select></label>
            <label>Nombre de usuario <input id="new-user" placeholder="usuario.demo" /></label>
            <label>Universidad/empresa <input id="new-org" placeholder="Northbridge University" /></label>
            <label>Carrera <input id="new-field" placeholder="Data Science" /></label>
          </div>
          <button class="primary-button" id="create-user">Agregar a la demo</button>
        </article>
        <article class="panel">${accountProfile()}<div class="button-row"><button class="primary-button" id="change-password-inline">Cambiar contraseña</button></div></article>
      </section>
      ${tablePanel("Usuarios de la demo", ["Usuario", "Correo", "Rol", "Universidad/empresa", "Carrera", "Estado"], state.users)}
    </div>`;
}

function accountProfile() {
  const role = roleConfig[state.role];
  const fieldRow = state.role === "student" ? `<div><span>Carrera</span><strong>${role.fieldOfStudy}</strong></div>` : "";
  return `
    <div class="profile-grid">
      <div><span>Usuario</span><strong>${role.user}</strong></div>
      <div><span>Correo</span><strong>${role.email}</strong></div>
      <div><span>Rol</span><strong>${role.role}</strong></div>
      <div><span>Universidad/empresa</span><strong>${role.context === "EduData Analytics" ? "EduData Analytics" : role.university}</strong></div>
      ${fieldRow}
    </div>`;
}

function selected(value, current) {
  return value === current ? "selected" : "";
}

function predictionRows() {
  return state.predictionRanking.map((item) => [
    item.student,
    item.field_of_study,
    `${Number(item.dropout_probability_percent).toFixed(2)}%`,
    item.risk_level,
    item.recommendation,
  ]);
}

function insights(items) {
  return `<div class="insight-grid">${items.map(([value, label]) => `<div><strong>${value}</strong><span>${label}</span></div>`).join("")}</div>`;
}

function tablePanel(title, head, rows) {
  return `
    <section class="panel table-panel">
      <div class="panel-header"><div><span class="eyebrow">Vista dinamica</span><h3>${title}</h3></div></div>
      <div class="table-wrap"><table><thead><tr>${head.map((x) => `<th>${x}</th>`).join("")}</tr></thead><tbody>${rows
        .map((row) => `<tr>${row.map((cell) => renderCell(cell)).join("")}</tr>`)
        .join("")}</tbody></table></div>
    </section>`;
}

function renderCell(cell) {
  const riskClass = String(cell).toLowerCase();
  if (["bajo", "medio", "alto"].includes(riskClass)) {
    const cls = riskClass === "bajo" ? "low" : riskClass === "medio" ? "medium" : "high";
    return `<td><span class="risk ${cls}">${cell}</span></td>`;
  }
  return `<td>${cell}</td>`;
}

function surveyRows() {
  return [
    ["1", "08 Mar", "Completada", "64%", "Bajo"],
    ["2", "08 May", "Completada", "66%", "Medio"],
    ["3", "08 Jul", state.surveyCompleted >= 3 ? "Completada" : "Pendiente", "68%", "Medio"],
    ["4", "08 Ago", state.surveyCompleted >= 4 ? "Completada demo" : "Pendiente", state.surveyCompleted >= 4 ? "71%" : "-", "Medio"],
    ["5", "08 Oct", "Pendiente", "-", "-"],
    ["6", "08 Dic", "Pendiente", "-", "-"],
  ];
}

function filteredReportRows() {
  const rows = reportRows[state.role];
  return state.reportRisk === "Todos" ? rows : rows.filter((row) => row[row.length - 1] === state.reportRisk);
}

function bindPageEvents() {
  document.querySelectorAll("[data-page]").forEach((button) => {
    button.addEventListener("click", () => setPage(button.dataset.page));
  });
  const refresh = document.getElementById("refresh-notices");
  if (refresh) {
    refresh.addEventListener("click", () => {
      state.notices[state.role].unshift(["Actualizado", "Notificaciones refrescadas en modo demo."]);
      showToast("Notificaciones actualizadas.");
      renderApp();
    });
  }
  const saveDraft = document.getElementById("save-draft");
  if (saveDraft) {
    saveDraft.addEventListener("click", () => {
      state.draftSaved = true;
      showToast("Borrador guardado en la demo.");
      renderApp();
    });
  }
  const submitSurvey = document.getElementById("submit-survey");
  if (submitSurvey) {
    submitSurvey.addEventListener("click", () => {
      if (state.surveyCompleted < 6) state.surveyCompleted += 1;
      state.draftSaved = false;
      state.notices.student.unshift(["Encuesta enviada", `Encuesta ${state.surveyCompleted} registrada en modo demo.`]);
      showToast("Encuesta enviada en modo demo. No se actualizo SQL.");
      renderApp();
    });
  }
  const applyReport = document.getElementById("apply-report-filter");
  if (applyReport) {
    applyReport.addEventListener("click", () => {
      state.reportPeriod = document.getElementById("panel-period").value;
      state.reportRisk = document.getElementById("panel-risk").value;
      const entity = document.getElementById("panel-entity");
      if (entity) state.reportEntity = entity.value;
      showToast("Filtros aplicados.");
      renderApp();
    });
  }
  const createUser = document.getElementById("create-user");
  if (createUser) {
    createUser.addEventListener("click", () => {
      const email = document.getElementById("new-email").value.trim();
      const role = document.getElementById("new-role").value;
      const username = document.getElementById("new-user").value.trim() || email.split("@")[0];
      const org = document.getElementById("new-org").value.trim() || "Northbridge University";
      const field = document.getElementById("new-field").value.trim() || (role === "Estudiante" ? "Data Science" : "No aplica");
      if (!email) {
        showToast("Ingresa un correo para crear el usuario demo.");
        return;
      }
      state.users.unshift([username, email, role, org, field, "Demo"]);
      showToast("Usuario agregado en pantalla. No se guardo en SQL.");
      renderApp();
    });
  }
  const changeInline = document.getElementById("change-password-inline");
  if (changeInline) {
    changeInline.addEventListener("click", openPasswordModal);
  }
  const runPrediction = document.getElementById("run-prediction");
  if (runPrediction) {
    runPrediction.addEventListener("click", predictDropout);
  }
  const loadRanking = document.getElementById("load-risk-ranking");
  if (loadRanking) {
    loadRanking.addEventListener("click", loadUniversityRiskRanking);
    if (!state.predictionRankingLoaded && state.role === "universityAdmin" && state.page === "prediction") {
      loadUniversityRiskRanking();
    }
  }
  const highRiskDemo = document.getElementById("load-high-risk-demo");
  if (highRiskDemo) {
    highRiskDemo.addEventListener("click", () => {
      state.predictionInput = {
        studentName: "Amina Kato",
        fieldOfStudy: "Law",
        poverty_rate_percent: 45,
        internet_infrastructure_index: 30,
        age: 22,
        internet_access_hours: 10,
        academic_motivation: 2,
        education_content_hours: 0.5,
        brain_rot_level: 9,
        attention_span_minutes: 8,
        study_hours_per_week: 3,
        class_attendance_rate: 55,
        development_level: "Underdeveloped",
        urban_rural: "Rural",
        family_income_level: "Low",
      };
      state.predictionResult = localDropoutPrediction(state.predictionInput);
      state.predictionRanking = [
        { student: state.predictionInput.studentName, field_of_study: state.predictionInput.fieldOfStudy, dropout_probability_percent: state.predictionResult.dropout_probability_percent, risk_level: state.predictionResult.risk_level, recommendation: "Seguimiento inmediato" },
        { student: "Daniel Njoroge", field_of_study: "STEM", dropout_probability_percent: 78.41, risk_level: "Alto", recommendation: "Cita con tutor academico" },
        { student: "Lucia Ramos", field_of_study: "Business", dropout_probability_percent: 52.18, risk_level: "Medio", recommendation: "Monitoreo preventivo" },
        { student: "Mei Chen", field_of_study: "Medicine", dropout_probability_percent: 24.35, risk_level: "Bajo", recommendation: "Seguimiento regular" },
      ];
      state.predictionRankingLoaded = true;
      state.predictionRankingUniversity = "Kuala Lumpur Institute of Technology";
      state.predictionSource = "Demo local";
      showToast("Caso critico cargado.");
      renderApp();
    });
  }
}

async function loadUniversityRiskRanking() {
  try {
    const response = await fetch("http://127.0.0.1:8000/predictions/university-risk?university_name=Kuala%20Lumpur%20Institute%20of%20Technology&limit=10&view=mixed");
    if (!response.ok) throw new Error("Backend unavailable");
    const data = await response.json();
    state.predictionRanking = mixedPresentationRows(data.results).map((item) => ({
      student: item.student,
      field_of_study: item.field_of_study,
      dropout_probability_percent: item.dropout_probability_percent,
      risk_level: item.risk_level,
      recommendation: item.risk_level === "Alto" ? "Seguimiento inmediato" : item.recommendation,
    }));
    state.predictionRankingLoaded = true;
    state.predictionRankingUniversity = data.university;
    if (data.results.length > 0) {
      const first = data.results[0];
      state.predictionInput.studentName = first.student;
      state.predictionInput.fieldOfStudy = first.field_of_study;
      state.predictionResult = {
        dropout_probability: first.dropout_probability,
        dropout_probability_percent: first.dropout_probability_percent,
        risk_level: first.risk_level,
        recommendation: first.recommendation,
      };
      state.predictionSource = "Ranking real desde SQL Server";
    }
    const counts = data.risk_counts ? ` Alto ${data.risk_counts.Alto}, Medio ${data.risk_counts.Medio}, Bajo ${data.risk_counts.Bajo}.` : "";
    showToast(`Ranking real cargado: ${data.students_evaluated} estudiantes evaluados.${counts}`);
  } catch (error) {
    state.predictionRankingLoaded = true;
    showToast("No se pudo cargar SQL: se mantiene ranking demo.");
  }
  renderApp();
}

function mixedPresentationRows(results) {
  const selected = [];
  ["Alto", "Medio", "Bajo"].forEach((risk) => {
    selected.push(...results.filter((item) => item.risk_level === risk).slice(0, 2));
  });
  if (selected.length < 6) {
    results.forEach((item) => {
      if (selected.length < 6 && !selected.some((row) => row.student_id === item.student_id)) {
        selected.push(item);
      }
    });
  }
  return selected.sort((a, b) => b.dropout_probability_percent - a.dropout_probability_percent);
}

function readPredictionInput() {
  return {
    studentName: document.getElementById("predict-student-name").value.trim() || "Estudiante demo",
    fieldOfStudy: document.getElementById("predict-field").value,
    poverty_rate_percent: Number(document.getElementById("predict-poverty").value),
    internet_infrastructure_index: Number(document.getElementById("predict-infrastructure").value),
    age: Number(document.getElementById("predict-age").value),
    internet_access_hours: Number(document.getElementById("predict-internet-hours").value),
    academic_motivation: Number(document.getElementById("predict-motivation").value),
    education_content_hours: Number(document.getElementById("predict-education-content").value),
    brain_rot_level: Number(document.getElementById("predict-brain-rot").value),
    attention_span_minutes: Number(document.getElementById("predict-attention").value),
    study_hours_per_week: Number(document.getElementById("predict-study-hours").value),
    class_attendance_rate: Number(document.getElementById("predict-attendance").value),
    development_level: document.getElementById("predict-development").value,
    urban_rural: document.getElementById("predict-zone").value,
    family_income_level: document.getElementById("predict-income").value,
  };
}

async function predictDropout() {
  state.predictionInput = readPredictionInput();
  const payload = { ...state.predictionInput };
  delete payload.studentName;
  delete payload.fieldOfStudy;
  try {
    const response = await fetch("http://127.0.0.1:8000/predictions/dropout", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error("Backend unavailable");
    state.predictionResult = await response.json();
    state.predictionSource = "Modelo real en backend";
    showToast("Prediccion calculada con el modelo real.");
  } catch (error) {
    state.predictionResult = localDropoutPrediction(state.predictionInput);
    state.predictionSource = "Demo local";
    showToast("Backend apagado: se uso prediccion demo.");
  }
  renderApp();
}

function localDropoutPrediction(input) {
  let score = 18;
  score += (100 - input.class_attendance_rate) * 0.32;
  score += Math.max(0, 6 - input.academic_motivation) * 6.5;
  score += Math.max(0, 8 - input.study_hours_per_week) * 3.2;
  score += Math.max(0, input.internet_access_hours - 6) * 3.8;
  score += input.brain_rot_level * 3.4;
  score += Math.max(0, 20 - input.attention_span_minutes) * 1.1;
  score += input.family_income_level === "Low" ? 8 : input.family_income_level === "Middle" ? 3 : 0;
  score += input.development_level === "Underdeveloped" ? 5 : 0;
  score += input.urban_rural === "Rural" ? 3 : 0;
  const probability = Math.max(3, Math.min(98.9, score));
  const risk = probability >= 70 ? "Alto" : probability >= 35 ? "Medio" : "Bajo";
  return {
    dropout_probability: probability / 100,
    dropout_probability_percent: probability,
    risk_level: risk,
    recommendation: risk === "Alto"
      ? "Derivar a seguimiento academico y bienestar universitario."
      : risk === "Medio"
        ? "Programar monitoreo preventivo y revisar asistencia/motivacion."
        : "Mantener seguimiento regular en el proximo periodo.",
  };
}

function drawChart(canvas) {
  const ctx = canvas.getContext("2d");
  const w = canvas.width;
  const h = canvas.height;
  ctx.clearRect(0, 0, w, h);
  const gradient = ctx.createLinearGradient(0, 0, w, h);
  gradient.addColorStop(0, "#102841");
  gradient.addColorStop(1, "#0c5d64");
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, w, h);
  const series = state.role === "student" ? [48, 52, 55, 58, 62, state.surveyCompleted > 3 ? 72 : 68] : state.role === "universityAdmin" ? [62, 65, 63, 69, 71, 74] : [58, 61, 67, 70, 76, 82];
  ctx.strokeStyle = "rgba(255,255,255,0.22)";
  ctx.lineWidth = 1;
  for (let i = 0; i < 6; i++) {
    const y = 32 + i * 30;
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(w, y);
    ctx.stroke();
  }
  ctx.strokeStyle = "#f39b3d";
  ctx.lineWidth = 4;
  ctx.beginPath();
  series.forEach((value, i) => {
    const x = 80 + i * 135;
    const y = h - 35 - value * 1.65;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();
  ctx.fillStyle = "#ffffff";
  series.forEach((value, i) => {
    const x = 80 + i * 135;
    const y = h - 35 - value * 1.65;
    ctx.beginPath();
    ctx.arc(x, y, 5, 0, Math.PI * 2);
    ctx.fill();
  });
}

function showToast(message) {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.hidden = false;
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => {
    toast.hidden = true;
  }, 3200);
}

function enterDemo() {
  const expected = { ...demoCredentials[state.selectedLoginRole], password: state.passwords[state.selectedLoginRole] };
  const email = document.getElementById("login-email").value.trim();
  const password = document.getElementById("login-password").value;
  if (email !== expected.email || password !== expected.password) {
    showToast("Credenciales incorrectas para el perfil seleccionado.");
    return;
  }
  const appShell = document.getElementById("app-shell");
  const loginScreen = document.getElementById("login-screen");
  document.body.classList.remove("demo-locked");
  document.body.classList.add("logged-in");
  state.authenticated = true;
  appShell.hidden = false;
  loginScreen.hidden = true;
  window.scrollTo(0, 0);
  setRole(state.selectedLoginRole);
  showToast("Ingreso correcto.");
}

function openPasswordModal() {
  document.getElementById("current-password").value = "";
  document.getElementById("new-password").value = "";
  document.getElementById("confirm-password").value = "";
  document.getElementById("password-modal").hidden = false;
}

function closePasswordModal() {
  document.getElementById("password-modal").hidden = true;
}

function savePassword() {
  const current = document.getElementById("current-password").value;
  const next = document.getElementById("new-password").value;
  const confirm = document.getElementById("confirm-password").value;
  if (current !== state.passwords[state.role]) {
    showToast("La contraseña actual no coincide.");
    return;
  }
  if (next.length < 8) {
    showToast("La nueva contraseña debe tener al menos 8 caracteres.");
    return;
  }
  if (next !== confirm) {
    showToast("La confirmacion no coincide.");
    return;
  }
  state.passwords[state.role] = next;
  document.getElementById("login-password").value = next;
  closePasswordModal();
  showToast("Contraseña actualizada en modo demo.");
}

function logout() {
  document.body.classList.add("demo-locked");
  document.body.classList.remove("logged-in");
  state.authenticated = false;
  state.page = "dashboard";
  document.getElementById("app-shell").hidden = true;
  document.getElementById("login-screen").hidden = false;
  document.getElementById("password-modal").hidden = true;
  document.getElementById("login-email").value = demoCredentials[state.selectedLoginRole].email;
  document.getElementById("login-password").value = state.passwords[state.selectedLoginRole];
  window.scrollTo(0, 0);
  showToast("Sesión cerrada.");
}

document.querySelectorAll(".nav-link").forEach((link) => {
  link.addEventListener("click", (event) => {
    event.preventDefault();
    setPage(link.getAttribute("href").replace("#", ""));
  });
});

document.querySelectorAll(".demo-login").forEach((button) => {
  button.addEventListener("click", () => {
    state.selectedLoginRole = button.dataset.role;
    document.getElementById("login-email").value = button.dataset.email;
    document.getElementById("login-password").value = state.passwords[button.dataset.role];
    document.querySelectorAll(".demo-login").forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
  });
});

document.getElementById("enter-demo").addEventListener("click", enterDemo);
document.getElementById("change-password").addEventListener("click", openPasswordModal);
document.getElementById("close-password-modal").addEventListener("click", closePasswordModal);
document.getElementById("save-password").addEventListener("click", savePassword);
document.getElementById("logout-button").addEventListener("click", logout);
renderApp();
