const dataNode = document.getElementById("trace-data");
let traceData = {};

try {
  traceData = JSON.parse(dataNode.textContent);
} catch (error) {
  traceData = { error: String(error) };
}

const $ = (selector) => document.querySelector(selector);

function text(value) {
  if (value === null || value === undefined) return "";
  return String(value);
}

function pretty(value) {
  return JSON.stringify(value, null, 2);
}

function el(tag, className = "", content = "") {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (content) node.textContent = content;
  return node;
}

function makeMetric(label, value) {
  const card = el("div", "status-pill");
  card.appendChild(el("span", "", label));
  card.appendChild(el("strong", "", value));
  return card;
}

function renderStatus() {
  const fixture = traceData.fixture || {};
  const strip = $("#status-strip");
  strip.appendChild(makeMetric("fixture", fixture.display_name || fixture.name || "-"));
  strip.appendChild(makeMetric("source", `${fixture.source_word_count || 0} words`));
  strip.appendChild(makeMetric("qa shown", `${fixture.qa_shown || 0} of ${fixture.qa_total || 0}`));
  strip.appendChild(makeMetric("compile", `${fixture.compile_pass_count || 0} passes`));
  strip.appendChild(makeMetric("artifact", "OpenRouter run"));
  strip.appendChild(makeMetric("status", fixture.status || "prototype"));
  const title = document.getElementById("fixture-title");
  if (title) title.textContent = fixture.title || fixture.display_name || fixture.name || "Fixture Trace";
  const lede = document.getElementById("fixture-lede");
  if (lede) {
    lede.textContent = "A specimen viewer for watching one fixture move from source packet to package artifacts to QA replay.";
  }
}

function renderNav() {
  const nav = $("#phase-nav");
  const items = [
    ["source-card", "Source Packet"],
    ...traceData.phases
      .filter((phase) => !["source", "qa-replay"].includes(phase.id))
      .map((phase) => [phase.id, phase.title]),
    ["questions", "QA Replay"]
  ];
  for (const [target, label] of items) {
    const button = el("button", "nav-button", label);
    button.type = "button";
    button.addEventListener("click", () => {
      const node = document.getElementById(target);
      if (node) node.scrollIntoView({ behavior: "smooth", block: "start" });
    });
    nav.appendChild(button);
  }
}

function renderSource() {
  const card = $("#source-card");
  card.id = "source-card";
  card.appendChild(el("p", "eyebrow", "Layer 0"));
  card.appendChild(el("h2", "", "Source Transcript"));
  card.appendChild(el("p", "lede", "The checked-in fixture source is shown as an ordered transcript of sections. Corrections and operational notes remain visible instead of being summarized away."));

  const details = el("details", "debug-block evidence");
  const summary = el("summary", "", "Show source transcript");
  details.appendChild(summary);
  const list = el("div", "source-turns");
  for (const turn of traceData.source_turns || []) {
    const row = el("div", "source-turn");
    row.appendChild(el("span", "turn-id", turn.label || (turn.turn ? `Turn ${turn.turn}` : "Section")));
    row.appendChild(el("span", "", turn.text));
    list.appendChild(row);
  }
  details.appendChild(list);
  card.appendChild(details);
}

function renderTable(table) {
  const wrapper = el("div", "evidence");
  if (table.title) wrapper.appendChild(el("h3", "", table.title));
  const tableNode = document.createElement("table");
  const thead = document.createElement("thead");
  const tr = document.createElement("tr");
  for (const col of table.columns || []) tr.appendChild(el("th", "", col));
  thead.appendChild(tr);
  tableNode.appendChild(thead);
  const tbody = document.createElement("tbody");
  for (const row of table.rows || []) {
    const rowNode = document.createElement("tr");
    for (const cell of row) rowNode.appendChild(el("td", "", cell));
    tbody.appendChild(rowNode);
  }
  tableNode.appendChild(tbody);
  wrapper.appendChild(tableNode);
  return wrapper;
}

function renderRawBlock(label, payload) {
  const details = el("details", "debug-block raw");
  details.appendChild(el("summary", "", label));
  details.appendChild(el("pre", "", pretty(payload)));
  return details;
}

function renderPhase(phase) {
  const section = el("section", "phase-card");
  section.id = phase.id;
  const details = document.createElement("details");
  details.open = phase.id === "qa-replay";
  const summary = el("summary", "card-summary");
  summary.appendChild(el("span", "phase-name", phase.title));
  summary.appendChild(el("span", "phase-status", `${phase.status || ""} | ${phase.summary || ""}`));
  details.appendChild(summary);

  const body = el("div", "card-body");
  const list = el("ul", "decision-list");
  for (const item of phase.decisions || []) list.appendChild(el("li", "", item));
  body.appendChild(list);

  for (const table of phase.tables || []) body.appendChild(renderTable(table));
  if (phase.raw) body.appendChild(renderRawBlock("Show raw phase payload", phase.raw));
  details.appendChild(body);
  section.appendChild(details);
  return section;
}

function renderPhases() {
  const list = $("#phase-list");
  for (const phase of traceData.phases || []) {
    if (!["source", "qa-replay"].includes(phase.id)) list.appendChild(renderPhase(phase));
  }
}

function renderQuestion(question) {
  const card = el("article", "question-card");
  const details = document.createElement("details");
  const summary = el("summary", "card-summary");
  summary.appendChild(el("span", "phase-name", `${question.id}: ${question.question}`));
  summary.appendChild(el("span", "phase-status verdict", question.verdict || "unscored"));
  details.appendChild(summary);

  const body = el("div", "card-body");
  const answer = el("div", "qa-answer");
  answer.appendChild(el("p", "", `Model decision: ${question.answer || "answer"}`));
  answer.appendChild(el("p", "", `Reference: ${question.reference || ""}`));
  body.appendChild(answer);
  body.appendChild(el("p", "", question.why));

  const evidence = el("div", "evidence qa-grid");
  evidence.appendChild(renderRawBlock("Query plan", question.query_plan || []));
  evidence.appendChild(renderRawBlock("Answer-bearing rows", question.rows || []));
  body.appendChild(evidence);

  body.appendChild(renderRawBlock("Reference and raw QA trace", {
    reference: question.reference,
    query_plan: question.query_plan,
    rows: question.rows,
    why: question.why
  }));

  details.appendChild(body);
  card.appendChild(details);
  return card;
}

function renderQuestions() {
  const list = $("#question-list");
  const header = el("section", "trace-card");
  header.id = "questions";
  header.appendChild(el("p", "eyebrow", "QA Replay"));
  header.appendChild(el("h2", "", "Question Cards"));
  header.appendChild(el("p", "lede", "Each question starts collapsed. Open only the questions you want, then reveal evidence or raw payloads with the depth control."));
  list.appendChild(header);
  for (const question of traceData.questions || []) list.appendChild(renderQuestion(question));
}

function renderArtifacts() {
  const list = $("#artifact-list");
  const fixture = traceData.fixture || {};
  const artifacts = [
    ["source", fixture.source_path],
    ["qa", fixture.qa_path],
    ["oracle", fixture.oracle_path],
    ["trace json", "experiments/fixture_trace/trace_events.json"],
    ["viewer", "experiments/fixture_trace/index.html"]
  ];
  for (const [label, path] of artifacts) {
    const card = el("section", "rail-card");
    card.appendChild(el("span", "tag", label));
    card.appendChild(el("p", "", path || "-"));
    list.appendChild(card);
  }
}

function setupDepthControls() {
  document.body.classList.add("depth-summary");
  document.querySelectorAll("[data-depth]").forEach((button) => {
    button.addEventListener("click", () => {
      const depth = button.getAttribute("data-depth");
      document.body.classList.remove("depth-summary", "depth-evidence", "depth-raw");
      document.body.classList.add(`depth-${depth}`);
      document.querySelectorAll("[data-depth]").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
    });
  });
}

renderStatus();
renderNav();
renderSource();
renderPhases();
renderQuestions();
renderArtifacts();
setupDepthControls();
