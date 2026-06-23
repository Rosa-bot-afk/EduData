const API_BASE = "http://127.0.0.1:8000";

const credentials = {
  student: { email: "student00001_tanzania@student.synthetic.edu", password: "Pwd00001!2025" },
  universityAdmin: { email: "sofia.ramirez@synthetic.edu", password: "AdminSofia001!" },
  employee: { email: "camila.torres@synthetic.edu", password: "AdminCamila003!" },
};

const roles = {
  student: {
    role: "Estudiante",
    user: "student00001_tanzania",
    context: "Expediente estudiantil",
    kicker: "Expediente estudiantil",
    title: "Seguimiento academico y digital desde la base.",
    copy: "Lectura individual de encuestas, bienestar, asistencia y alertas calculadas con datos registrados.",
    period: "Ultima encuesta disponible",
    status: "Seguimiento activo",
  },
  universityAdmin: {
    role: "Administrador",
    user: "sofia.ramirez.admin",
    context: "Gestion institucional",
    kicker: "Dashboard institucional",
    title: "Cohortes, asistencia y riesgo con lectura ejecutiva.",
    copy: "Panel para priorizar universidades, carreras y estudiantes con evidencia operativa.",
    period: "Corte operativo 2025",
    status: "Datos actualizados",
  },
  employee: {
    role: "Empleado EduData",
    user: "camila.torres.admin",
    context: "EduData Analytics / cartera global",
    kicker: "Operacion global",
    title: "Cartera universitaria y senales criticas en una pantalla.",
    copy: "Supervisa cobertura, alertas, reportes y modelo predictivo con trazabilidad hacia la base normalizada.",
    period: "Corte operativo",
    status: "Reportes regenerados con Python",
  },
};

const state = {
  role: "student",
  selectedRole: "student",
  module: "overview",
  surveyCompleted: 3,
  draftSaved: false,
  reportPeriod: "2025-1",
  reportRisk: "Todos",
  reportEntity: "Todos los paises",
  passwords: {
    student: "Pwd00001!2025",
    universityAdmin: "AdminSofia001!",
    employee: "AdminCamila003!",
  },
  users: [
    ["student00001_tanzania", "student00001_tanzania@student.synthetic.edu", "Estudiante", "Northbridge University", "Data Science", "Activo"],
    ["sofia.ramirez.admin", "sofia.ramirez@synthetic.edu", "Administrador", "EduData Analytics", "No aplica", "Activo"],
    ["camila.torres.admin", "camila.torres@synthetic.edu", "Empleado EduData", "EduData Analytics", "No aplica", "Activo"],
  ],
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
  predictionSource: "Pendiente de calculo en backend",
  predictionRankingUniversity: "Kuala Lumpur Institute of Technology",
  predictionRankingLoaded: false,
  currentUser: null,
  sqlSummary: null,
  sqlStatus: "Sin conectar",
  predictionRanking: [
    { student: "Amina Kato", field_of_study: "Law", dropout_probability_percent: 98.72, risk_level: "Alto", recommendation: "Seguimiento inmediato" },
    { student: "Daniel Njoroge", field_of_study: "STEM", dropout_probability_percent: 78.41, risk_level: "Alto", recommendation: "Cita con tutor academico" },
    { student: "Lucia Ramos", field_of_study: "Business", dropout_probability_percent: 52.18, risk_level: "Medio", recommendation: "Monitoreo preventivo" },
    { student: "Mei Chen", field_of_study: "Medicine", dropout_probability_percent: 24.35, risk_level: "Bajo", recommendation: "Seguimiento regular" },
  ],
};

const notices = {
  student: [
    ["Encuesta enviada", "Tu encuesta 3 fue registrada correctamente."],
    ["Proxima apertura", "La encuesta 4 estara disponible el 08 Ago 2025."],
    ["Progreso actualizado", "Ya puedes revisar tus indicadores personales."],
  ],
  universityAdmin: [
    ["Riesgo alto", "10 estudiantes requieren seguimiento prioritario."],
    ["Usuarios pendientes", "4 estudiantes aun no activan sus credenciales."],
    ["Reporte actualizado", "Indicadores de bienestar y adiccion digital listos."],
  ],
  employee: [
    ["Carga completada", "90,000 entrevistas procesadas."],
    ["Cliente nuevo", "Una universidad solicito credenciales iniciales."],
    ["Revision ejecutiva", "Reporte M5 listo para presentacion."],
  ],
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

const sqlReports = [
  {
    title: "Tendencia de senales criticas",
    insight: "Promedios por encuesta: muestra como sube la adiccion digital mientras baja el bienestar.",
    image: "assets/charts/report_01_risk_by_survey.png",
    kpi: "+3.0",
    kpiLabel: "puntos de adiccion digital",
  },
  {
    title: "Paises con mas alerta",
    insight: "Ranking por tasa de estudiantes con al menos una alerta academica o digital.",
    image: "assets/charts/report_02_field_indicators.png",
    kpi: "62.5%",
    kpiLabel: "alerta en Japan",
  },
  {
    title: "Universidades priorizadas",
    insight: "Score compuesto con adiccion, estres, bajo bienestar y baja asistencia.",
    image: "assets/charts/report_03_university_accumulation.png",
    kpi: "53",
    kpiLabel: "casos en la universidad #1",
  },
  {
    title: "Alertas por carrera",
    insight: "Mapa de calor para ver que condicion pesa mas en cada carrera.",
    image: "assets/charts/report_04_prioritized_students.png",
    kpi: "Arts",
    kpiLabel: "carrera a revisar primero",
  },
  {
    title: "Matriz de intervencion",
    insight: "Cruza tasa de alerta y bienestar para separar monitoreo de intervencion.",
    image: "assets/charts/report_05_executive_attendance.png",
    kpi: "7",
    kpiLabel: "universidades en zona critica",
  },
];

function metrics() {
  if (state.sqlSummary) {
    const global = state.sqlSummary.global;
    const latest = state.sqlSummary.latest;
    const deltas = state.sqlSummary.deltas;
    const firstPriority = state.sqlSummary.priority_universities?.[0];
    return [
      ["Estudiantes", formatNumber(global.students), `${formatNumber(global.assessments)} encuestas`, ""],
      ["Metricas", formatNumber(global.metrics), `${formatNumber(global.universities)} universidades`, ""],
      ["Bienestar", `${Number(latest.wellbeing).toFixed(1)}%`, `${Number(deltas.wellbeing).toFixed(1)} pts vs encuesta 1`, Number(deltas.wellbeing) < 0 ? "warn" : ""],
      ["Prioridad", firstPriority ? `${Number(firstPriority.alert_rate).toFixed(1)}%` : "-", firstPriority ? firstPriority.country_name : state.sqlStatus, "warn"],
    ];
  }
  return [
    ["Conexion", "Pendiente", "Levanta el backend en puerto 8000", "warn"],
    ["Estudiantes", "-", "Sin conexion API", ""],
    ["Metricas", "-", "Sin conexion API", ""],
    ["Reportes", "5", "Visualizaciones ejecutivas", ""],
  ];
}

function formatNumber(value) {
  return Number(value || 0).toLocaleString("en-US");
}

function setSelectedRole(role) {
  state.selectedRole = role;
  document.querySelectorAll(".role-card").forEach((button) => {
    button.classList.toggle("selected", button.dataset.role === role);
  });
  document.getElementById("login-email").value = credentials[role].email;
  document.getElementById("login-password").value = state.passwords[role];
}

async function enterSystem() {
  const email = document.getElementById("login-email").value.trim();
  const password = document.getElementById("login-password").value;
  try {
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!response.ok) throw new Error("Credenciales no validadas");
    const data = await response.json();
    const user = data.user;
    state.currentUser = user;
    state.role = user.role_key;
    state.selectedRole = user.role_key;
    roles[state.role] = {
      ...roles[state.role],
      user: user.user_name,
      context: user.context || roles[state.role].context,
      role: user.user_role === "estudiante" ? "Estudiante" : roles[state.role].role,
    };
    loadDashboardSummary();
  } catch (error) {
    showToast("No se pudo iniciar sesion. Revisa tu correo y contrasena.");
    return;
  }
  state.module = "overview";
  document.getElementById("access-stage").hidden = true;
  document.getElementById("product-shell").hidden = false;
  renderShell();
  window.scrollTo({ top: 0, behavior: "auto" });
  showToast("Ingreso correcto.");
}

async function loadDashboardSummary() {
  try {
    const controller = new AbortController();
    const timer = window.setTimeout(() => controller.abort(), 12000);
    const response = await fetch(`${API_BASE}/dashboard/summary`, { signal: controller.signal });
    window.clearTimeout(timer);
    if (!response.ok) throw new Error("No se pudo cargar dashboard");
    state.sqlSummary = await response.json();
    state.sqlStatus = "Conectado";
    if (!document.getElementById("product-shell").hidden) renderShell();
  } catch (error) {
    state.sqlStatus = "Dashboard pendiente";
  }
}

function renderShell() {
  const role = roles[state.role];
  document.getElementById("active-user").textContent = role.user;
  document.getElementById("active-role").textContent = role.role;
  document.getElementById("mission-kicker").textContent = role.kicker;
  document.getElementById("mission-title").textContent = role.title;
  document.getElementById("mission-copy").textContent = role.copy;
  document.getElementById("mission-context").textContent = role.context;
  document.getElementById("mission-period").textContent = role.period;
  document.getElementById("mission-status").textContent = role.status;

  document.querySelectorAll(".admin-module").forEach((item) => {
    item.hidden = state.role === "student";
  });
  if (state.module === "prediction" && state.role === "student") state.module = "overview";
  document.querySelectorAll(".dock-item").forEach((item) => {
    item.classList.toggle("active", item.dataset.module === state.module);
  });

  document.getElementById("metric-strip").innerHTML = metrics()
    .map(([label, value, detail, tone]) => `
      <article class="data-card">
        <span>${label}</span>
        <strong>${value}</strong>
        <em class="delta ${tone}">${detail}</em>
      </article>
    `)
    .join("");

  document.getElementById("module-root").innerHTML = renderModule();
  bindModuleEvents();
}

function setModule(module) {
  state.module = module;
  window.scrollTo({ top: 0, behavior: "auto" });
  renderShell();
}

function renderModule() {
  if (state.module === "prediction") return predictionModule();
  if (state.module === "people") return peopleModule();
  return overviewModule();
}

function overviewModule() {
  const priority = state.sqlSummary?.priority_universities?.[0];
  const global = state.sqlSummary?.global;
  const insight = priority
    ? `${priority.university_name} aparece como prioridad principal con ${Number(priority.alert_rate).toFixed(1)}% de estudiantes en alerta.`
    : "Resumen ejecutivo de cohortes, bienestar, asistencia, alertas y reportes institucionales.";
  const coverage = global
    ? [[formatNumber(global.students), "Estudiantes"], [formatNumber(global.assessments), "Encuestas"], [formatNumber(global.universities), "Universidades"]]
    : [["15,000", "Estudiantes"], ["90,000", "Encuestas"], ["185", "Universidades"]];
  const bars = state.sqlSummary
    ? state.sqlSummary.priority_universities.slice(0, 4).map((item) => [item.country_name, Math.round(Number(item.alert_rate))])
    : [["Japan", 62], ["UK", 60], ["Germany", 59], ["Singapore", 56]];

  return `
    <article class="glass-cell span-7">
      <div class="cell-head">
        <div><span class="quiet-code">Dashboard</span><h2>Resumen ejecutivo</h2></div>
        <span class="status-chip">Actualizado</span>
      </div>
      <p>${insight}</p>
      ${insightRow(coverage)}
      <div class="action-row"><button class="command-button primary" data-module="prediction">Abrir modelo predictivo</button><button class="command-button ghost" data-module="people">Panel de usuarios</button></div>
    </article>
    <article class="glass-cell span-5 report-filter-cell">
      <div class="cell-head"><div><span class="quiet-code">Prioridad</span><h3>Alertas por pais</h3></div></div>
      ${miniBars(bars)}
    </article>
    <article class="glass-cell span-12">
      <div class="cell-head"><div><span class="quiet-code">Reportes</span><h2>Visualizaciones ejecutivas</h2></div><span class="status-chip">5 graficos</span></div>
      ${reportGallery()}
    </article>
    <article class="glass-cell span-8">
      <div class="cell-head"><div><span class="quiet-code">Seguimiento</span><h3>Senales recientes</h3></div></div>
      <div class="timeline-list">${notices[state.role].slice(0, 4).map(([title, text]) => `<article><strong>${title}</strong><span>${text}</span></article>`).join("")}</div>
    </article>
    <article class="glass-cell span-4">
      <div class="cell-head"><div><span class="quiet-code">Acceso</span><h3>Cuenta activa</h3></div></div>
      ${profileGrid()}
      <button class="command-button ghost" id="change-password-inline" type="button">Cambiar contrasena</button>
    </article>
  `;
}

function surveyModule() {
  if (state.role !== "student") {
    return `
      <article class="glass-cell span-8">
        <div class="cell-head"><div><span class="quiet-code">Encuestas</span><h2>Seguimiento de respuestas</h2></div><span class="status-chip">100%</span></div>
        ${insightRow([["516", "Respuestas"], ["0", "Pendientes criticos"], ["6/6", "Entrevistas"]])}
        <p>Este perfil revisa avance y completitud. Solo estudiantes responden formularios personales.</p>
        <button class="command-button primary" data-module="reports">Ver reporte de encuestas</button>
      </article>
      ${noticesModule("span-4")}
      ${tableModule("Estado de encuestas", ["Encuesta", "Fecha", "Estado", "Bienestar", "Riesgo"], surveyRows(), "span-12")}
    `;
  }
  const progress = Math.round((state.surveyCompleted / 6) * 100);
  return `
    <article class="glass-cell span-8">
      <div class="cell-head"><div><span class="quiet-code">Encuesta activa</span><h2>Seguimiento estudiantil ${Math.min(state.surveyCompleted + 1, 6)}</h2></div><span class="status-chip">${state.draftSaved ? "Borrador" : "En progreso"}</span></div>
      ${miniBars([["Avance", progress], ["Bienestar", 68], ["Asistencia", 91]])}
      <div class="form-grid">
        <label>Horas en redes sociales <input id="social-hours" type="number" min="0" max="24" step="0.1" value="3.8" /></label>
        <label>Horas de sueno <input id="sleep-hours" type="number" min="0" max="24" step="0.1" value="6.7" /></label>
        <label>Nivel de estres <input id="stress-level" type="number" min="0" max="10" value="6" /></label>
        <label>Asistencia a clases <input id="attendance-rate" type="number" min="0" max="100" value="91" /></label>
      </div>
      <div class="action-row"><button class="command-button primary" id="submit-survey">Enviar encuesta</button><button class="command-button ghost" id="save-draft">Guardar borrador</button></div>
    </article>
    ${noticesModule("span-4")}
    ${tableModule("Estado de mis encuestas", ["Encuesta", "Fecha", "Estado", "Bienestar", "Riesgo"], surveyRows(), "span-12")}
  `;
}

function reportsModule() {
  const head = state.role === "student"
    ? ["Encuesta", "Periodo", "Bienestar", "Adiccion digital", "Riesgo"]
    : state.role === "universityAdmin"
      ? ["Carrera", "Estudiantes", "Asistencia", "Bienestar", "Riesgo"]
      : ["Universidad", "Pais", "Estudiantes", "Bienestar", "Riesgo"];
  return `
    <article class="glass-cell span-5">
      <div class="cell-head"><div><span class="quiet-code">Filtros</span><h2>Reporte ejecutivo</h2></div><span class="status-chip">Interactivo</span></div>
      <div class="form-grid">
        <label>Periodo <select id="panel-period"><option ${selected("2025-1", state.reportPeriod)}>2025-1</option><option ${selected("2025-2", state.reportPeriod)}>2025-2</option></select></label>
        <label>Riesgo <select id="panel-risk"><option ${selected("Todos", state.reportRisk)}>Todos</option><option ${selected("Alto", state.reportRisk)}>Alto</option><option ${selected("Medio", state.reportRisk)}>Medio</option><option ${selected("Bajo", state.reportRisk)}>Bajo</option></select></label>
        ${state.role === "employee" ? `<label>Vista global <select id="panel-entity"><option ${selected("Todos los paises", state.reportEntity)}>Todos los paises</option><option ${selected("Top bienestar", state.reportEntity)}>Top bienestar</option><option ${selected("Riesgo global", state.reportEntity)}>Riesgo global</option><option ${selected("Universidades destacadas", state.reportEntity)}>Universidades destacadas</option></select></label>` : ""}
      </div>
      <button class="command-button primary" id="apply-report-filter">Aplicar filtros</button>
    </article>
    <article class="glass-cell span-7">
      <div class="cell-head"><div><span class="quiet-code">Reportes</span><h2>5 reportes ejecutivos</h2></div></div>
      ${reportGallery()}
    </article>
    ${tableModule("Reporte filtrado", head, filteredReportRows(), "span-12")}
  `;
}

function predictionModule() {
  const result = state.predictionResult;
  const probability = Number(result.dropout_probability_percent || 0);
  const riskClass = riskClassFor(result.risk_level);
  return `
    <article class="glass-cell span-8">
      <div class="cell-head"><div><span class="quiet-code">Modelo predictivo</span><h2>Workbench de riesgo estudiantil</h2></div><span class="risk-pill ${riskClass}">${result.risk_level}</span></div>
      <div class="form-grid prediction-form">
        <label>Estudiante <input id="predict-student-name" value="${state.predictionInput.studentName}" /></label>
        <label>Carrera <select id="predict-field"><option ${selected("Law", state.predictionInput.fieldOfStudy)}>Law</option><option ${selected("Medicine", state.predictionInput.fieldOfStudy)}>Medicine</option><option ${selected("Business", state.predictionInput.fieldOfStudy)}>Business</option><option ${selected("STEM", state.predictionInput.fieldOfStudy)}>STEM</option></select></label>
        <label>Asistencia (%) <input id="predict-attendance" type="number" min="0" max="100" value="${state.predictionInput.class_attendance_rate}" /></label>
        <label>Motivacion (0-10) <input id="predict-motivation" type="number" min="0" max="10" value="${state.predictionInput.academic_motivation}" /></label>
        <label>Horas estudio <input id="predict-study-hours" type="number" min="0" max="80" step="0.5" value="${state.predictionInput.study_hours_per_week}" /></label>
        <label>Horas internet <input id="predict-internet-hours" type="number" min="0" max="24" step="0.5" value="${state.predictionInput.internet_access_hours}" /></label>
        <label>Brain rot <input id="predict-brain-rot" type="number" min="0" max="10" value="${state.predictionInput.brain_rot_level}" /></label>
        <label>Edad <input id="predict-age" type="number" min="14" max="80" value="${state.predictionInput.age}" /></label>
        <label>Atencion <input id="predict-attention" type="number" min="1" max="180" value="${state.predictionInput.attention_span_minutes}" /></label>
      </div>
      <div class="action-row"><button class="command-button primary" id="run-prediction">Calcular riesgo</button><button class="command-button ghost" id="load-risk-ranking">Ranking institucional</button><button class="command-button ghost" id="load-high-risk-case">Caso de alto riesgo</button></div>
    </article>
    <article class="glass-cell span-4">
      <span class="quiet-code">Resultado</span>
      <strong class="risk-score">${probability.toFixed(2)}%</strong>
      <span class="risk-pill ${riskClass}">Riesgo ${result.risk_level}</span>
      <p>${result.recommendation}</p>
      <small>Fuente: ${state.predictionSource}</small>
    </article>
    <article class="glass-cell span-12">
      <div class="cell-head"><div><span class="quiet-code">Explicacion para exposicion</span><h2>Modelo predictivo de desercion estudiantil</h2></div><span class="status-chip">Regresion logistica</span></div>
      <div class="model-explain">
        <article><strong>Objetivo</strong><p>Estimar la probabilidad de desercion para priorizar acompanamiento academico y bienestar universitario.</p></article>
        <article><strong>Variables usadas</strong><p>Asistencia, motivacion, horas de estudio, uso de internet, brain rot, atencion, contexto socioeconomico e infraestructura digital.</p></article>
        <article><strong>Interpretacion</strong><p>El porcentaje no sentencia al estudiante. Es una alerta temprana para que un equipo humano revise el caso.</p></article>
        <article><strong>Accion recomendada</strong><p>Riesgo alto: seguimiento inmediato. Riesgo medio: monitoreo preventivo. Riesgo bajo: seguimiento regular.</p></article>
      </div>
    </article>
    ${tableModule("Estudiantes priorizados", ["Estudiante", "Carrera", "Probabilidad", "Riesgo", "Accion sugerida"], predictionRows(), "span-12")}
  `;
}

function peopleModule() {
  const canCreate = state.role !== "student";
  return `
    <article class="glass-cell ${canCreate ? "span-7" : "span-8"}">
      <div class="cell-head"><div><span class="quiet-code">Cuenta</span><h2>${canCreate ? "Crear y revisar accesos" : "Mi cuenta"}</h2></div></div>
      ${canCreate ? `
        <div class="form-grid">
          <label>Correo <input id="new-email" type="email" placeholder="nuevo@universidad.edu" /></label>
          <label>Rol <select id="new-role"><option>Estudiante</option><option>Admin universidad</option><option>Empleado EduData</option></select></label>
          <label>Usuario <input id="new-user" placeholder="usuario.institucional" /></label>
          <label>Universidad/empresa <input id="new-org" placeholder="Northbridge University" /></label>
          <label>Carrera <input id="new-field" placeholder="Data Science" /></label>
        </div>
        <button class="command-button primary" id="create-user">Agregar usuario</button>
      ` : `<p>Los estudiantes revisan su acceso. La creacion de usuarios corresponde a administradores autorizados.</p>`}
    </article>
    <article class="glass-cell ${canCreate ? "span-5" : "span-4"}">
      <div class="cell-head"><div><span class="quiet-code">Perfil activo</span><h3>Sesion actual</h3></div></div>
      ${profileGrid()}
      <button class="command-button ghost" id="change-password-inline" type="button">Cambiar contrasena</button>
    </article>
    ${tableModule("Usuarios del entorno", ["Usuario", "Correo", "Rol", "Universidad/empresa", "Carrera", "Estado"], state.users, "span-12")}
  `;
}

function insightRow(items) {
  return `<div class="insight-row">${items.map(([value, label]) => `<article><strong>${value}</strong><span>${label}</span></article>`).join("")}</div>`;
}

function miniBars(items) {
  return `<ul class="mini-bars">${items.map(([label, value]) => `<li><span>${label}</span><div class="bar-track"><i style="width:${value}%"></i></div><strong>${value}%</strong></li>`).join("")}</ul>`;
}

function noticesModule(span) {
  return `
    <article class="glass-cell ${span}">
      <div class="cell-head"><div><span class="quiet-code">Alertas</span><h3>Senales recientes</h3></div><button class="icon-action" id="refresh-notices" type="button" aria-label="Actualizar">R</button></div>
      <div class="timeline-list">${notices[state.role].slice(0, 4).map(([title, text]) => `<article><strong>${title}</strong><span>${text}</span></article>`).join("")}</div>
    </article>
  `;
}

function profileGrid() {
  const role = roles[state.role];
  return `
    <div class="profile-grid">
      <article><span>Usuario</span><strong>${role.user}</strong></article>
      <article><span>Rol</span><strong>${role.role}</strong></article>
      <article><span>Contexto</span><strong>${role.context}</strong></article>
    </div>
  `;
}

function tableModule(title, head, rows, span) {
  return `
    <article class="glass-cell ${span}">
      <div class="cell-head"><div><span class="quiet-code">Data table</span><h2>${title}</h2></div></div>
      <div class="table-shell"><div class="table-scroll"><table><thead><tr>${head.map((item) => `<th>${item}</th>`).join("")}</tr></thead><tbody>${rows.map((row) => `<tr>${row.map(renderCell).join("")}</tr>`).join("")}</tbody></table></div></div>
    </article>
  `;
}

function renderCell(cell) {
  const risk = String(cell).toLowerCase();
  if (["bajo", "medio", "alto"].includes(risk)) {
    return `<td><span class="risk-pill ${riskClassFor(cell)}">${cell}</span></td>`;
  }
  return `<td>${cell}</td>`;
}

function reportGallery() {
  return `
    <div class="report-gallery">
      ${sqlReports.map((report, index) => `
        <article class="report-card ${index === 0 ? "featured-report" : ""}">
          <img src="${report.image}" alt="${report.title}" />
          <div>
            <span class="quiet-code">Reporte ${index + 1}</span>
            <strong>${report.title}</strong>
            <p>${report.insight}</p>
            <em>${report.kpi} ${report.kpiLabel}</em>
          </div>
        </article>
      `).join("")}
    </div>
  `;
}

function selected(value, current) {
  return value === current ? "selected" : "";
}

function riskClassFor(value) {
  const risk = String(value).toLowerCase();
  if (risk === "alto") return "high";
  if (risk === "medio") return "medium";
  return "low";
}

function surveyRows() {
  return [
    ["1", "08 Mar", "Completada", "64%", "Bajo"],
    ["2", "08 May", "Completada", "66%", "Medio"],
    ["3", "08 Jul", state.surveyCompleted >= 3 ? "Completada" : "Pendiente", "68%", "Medio"],
    ["4", "08 Ago", state.surveyCompleted >= 4 ? "Completada" : "Pendiente", state.surveyCompleted >= 4 ? "71%" : "-", "Medio"],
    ["5", "08 Oct", "Pendiente", "-", "-"],
    ["6", "08 Dic", "Pendiente", "-", "-"],
  ];
}

function filteredReportRows() {
  const rows = reportRows[state.role];
  return state.reportRisk === "Todos" ? rows : rows.filter((row) => row[row.length - 1] === state.reportRisk);
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

function bindModuleEvents() {
  document.querySelectorAll("[data-module]").forEach((button) => {
    button.addEventListener("click", () => {
      setModule(button.dataset.module);
    });
  });

  const refresh = document.getElementById("refresh-notices");
  if (refresh) refresh.addEventListener("click", () => {
    notices[state.role].unshift(["Actualizado", "Senales refrescadas desde el tablero activo."]);
    showToast("Notificaciones actualizadas.");
    renderShell();
  });

  const saveDraft = document.getElementById("save-draft");
  if (saveDraft) saveDraft.addEventListener("click", () => {
    state.draftSaved = true;
    showToast("Borrador guardado en pantalla.");
    renderShell();
  });

  const submitSurvey = document.getElementById("submit-survey");
  if (submitSurvey) submitSurvey.addEventListener("click", () => {
    if (state.surveyCompleted < 6) state.surveyCompleted += 1;
    state.draftSaved = false;
    notices.student.unshift(["Encuesta enviada", `Encuesta ${state.surveyCompleted} registrada en pantalla.`]);
    showToast("Encuesta registrada en pantalla.");
    renderShell();
  });

  const applyReport = document.getElementById("apply-report-filter");
  if (applyReport) applyReport.addEventListener("click", () => {
    state.reportPeriod = document.getElementById("panel-period").value;
    state.reportRisk = document.getElementById("panel-risk").value;
    const entity = document.getElementById("panel-entity");
    if (entity) state.reportEntity = entity.value;
    showToast("Filtros aplicados.");
    renderShell();
  });

  const createUser = document.getElementById("create-user");
  if (createUser) createUser.addEventListener("click", () => {
    const email = document.getElementById("new-email").value.trim();
    const role = document.getElementById("new-role").value;
    const username = document.getElementById("new-user").value.trim() || email.split("@")[0];
    const org = document.getElementById("new-org").value.trim() || "Northbridge University";
    const field = document.getElementById("new-field").value.trim() || (role === "Estudiante" ? "Data Science" : "No aplica");
    if (!email) {
      showToast("Ingresa un correo para crear el usuario.");
      return;
    }
    state.users.unshift([username, email, role, org, field, "Local"]);
    showToast("Usuario agregado en pantalla.");
    renderShell();
  });

  const changeInline = document.getElementById("change-password-inline");
  if (changeInline) changeInline.addEventListener("click", openPasswordModal);

  const runPrediction = document.getElementById("run-prediction");
  if (runPrediction) runPrediction.addEventListener("click", predictDropout);

  const loadRanking = document.getElementById("load-risk-ranking");
  if (loadRanking) loadRanking.addEventListener("click", loadUniversityRiskRanking);

  const highRiskCase = document.getElementById("load-high-risk-case");
  if (highRiskCase) highRiskCase.addEventListener("click", () => {
    state.predictionInput = {
      ...state.predictionInput,
      studentName: "Amina Kato",
      fieldOfStudy: "Law",
      internet_access_hours: 10,
      academic_motivation: 2,
      brain_rot_level: 9,
      study_hours_per_week: 3,
      class_attendance_rate: 55,
    };
    showToast("Caso de alto riesgo cargado. Presiona calcular con backend.");
    renderShell();
  });
}

function readPredictionInput() {
  return {
    studentName: document.getElementById("predict-student-name").value.trim() || "Estudiante",
    fieldOfStudy: document.getElementById("predict-field").value,
    poverty_rate_percent: state.predictionInput.poverty_rate_percent,
    internet_infrastructure_index: state.predictionInput.internet_infrastructure_index,
    age: Number(document.getElementById("predict-age").value),
    internet_access_hours: Number(document.getElementById("predict-internet-hours").value),
    academic_motivation: Number(document.getElementById("predict-motivation").value),
    education_content_hours: state.predictionInput.education_content_hours,
    brain_rot_level: Number(document.getElementById("predict-brain-rot").value),
    attention_span_minutes: Number(document.getElementById("predict-attention").value),
    study_hours_per_week: Number(document.getElementById("predict-study-hours").value),
    class_attendance_rate: Number(document.getElementById("predict-attendance").value),
    development_level: state.predictionInput.development_level,
    urban_rural: state.predictionInput.urban_rural,
    family_income_level: state.predictionInput.family_income_level,
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
    showToast("No se pudo calcular: levanta el backend para usar el modelo predictivo.");
  }
  renderShell();
}

async function loadUniversityRiskRanking() {
  try {
    const response = await fetch("http://127.0.0.1:8000/predictions/university-risk?university_name=Kuala%20Lumpur%20Institute%20of%20Technology&limit=10&view=mixed");
    if (!response.ok) throw new Error("Backend unavailable");
    const data = await response.json();
    state.predictionRanking = data.results.map((item) => ({
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
      state.predictionSource = "Ranking institucional";
    }
    showToast(`Ranking real cargado: ${data.students_evaluated} estudiantes evaluados.`);
  } catch (error) {
    state.predictionRankingLoaded = true;
    showToast("No se pudo cargar el ranking institucional.");
  }
  renderShell();
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
    showToast("La contrasena actual no coincide.");
    return;
  }
  if (next.length < 8) {
    showToast("La nueva contrasena debe tener al menos 8 caracteres.");
    return;
  }
  if (next !== confirm) {
    showToast("La confirmacion no coincide.");
    return;
  }
  state.passwords[state.role] = next;
  document.getElementById("login-password").value = next;
  closePasswordModal();
  showToast("Contrasena actualizada en pantalla.");
}

function logout() {
  document.getElementById("product-shell").hidden = true;
  document.getElementById("access-stage").hidden = false;
  state.module = "overview";
  closePasswordModal();
  setSelectedRole(state.selectedRole);
  showToast("Sesion cerrada.");
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

document.querySelectorAll(".role-card").forEach((button) => {
  button.addEventListener("click", () => setSelectedRole(button.dataset.role));
});

document.querySelectorAll(".dock-item").forEach((button) => {
  button.addEventListener("click", () => {
    setModule(button.dataset.module);
  });
});

document.getElementById("enter-system").addEventListener("click", enterSystem);
document.getElementById("logout-button").addEventListener("click", logout);
document.getElementById("close-password-modal").addEventListener("click", closePasswordModal);
document.getElementById("save-password").addEventListener("click", savePassword);
