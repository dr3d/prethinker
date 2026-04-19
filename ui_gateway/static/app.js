const state = {
  sessionId: null,
  config: null,
  configOpen: false,
  heroOpen: false,
};

const CONFIG_OPEN_KEY = "prethink_gateway_config_open";
const HERO_OPEN_KEY = "prethink_gateway_hero_open";

const API_BASE = (() => {
  const params = new URLSearchParams(window.location.search);
  const explicit = (params.get("apiBase") || "").trim();
  if (explicit) {
    return explicit.replace(/\/+$/, "");
  }
  if (window.location.protocol === "file:") {
    return "http://127.0.0.1:8765";
  }
  return "";
})();

function apiUrl(path) {
  return `${API_BASE}${path}`;
}

async function getJson(path, options = {}) {
  const response = await fetch(apiUrl(path), options);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

function downloadTextFile(text, filename, mimeType = "text/plain") {
  const blob = new Blob([text], { type: `${mimeType};charset=utf-8` });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  setTimeout(() => {
    URL.revokeObjectURL(link.href);
    link.remove();
  }, 0);
}

function syncHero(config) {
  document.getElementById("compiler-model-label").textContent = config.compiler_model;
  document.getElementById("compiler-mode-label").textContent =
    `${config.compiler_mode} / handoff=${config.served_handoff_mode}`;
  document.getElementById("served-model-label").textContent = config.served_llm_model;
}

function fillConfigForm(config) {
  const form = document.getElementById("config-form");
  for (const [key, value] of Object.entries(config)) {
    const field = form.elements.namedItem(key);
    if (!field) {
      continue;
    }
    if (field.type === "checkbox") {
      field.checked = Boolean(value);
    } else {
      field.value = value;
    }
  }
  syncHero(config);
}

function findTurnPhase(turn, phaseName) {
  const phases = Array.isArray(turn?.phases) ? turn.phases : [];
  return phases.find((phase) => phase && phase.phase === phaseName) || null;
}

function describeAmbiguity(score) {
  const clipped = Math.max(0, Math.min(1, Number(score)));
  const percent = Math.round(clipped * 100);
  let band = "Very low";
  if (clipped >= 0.8) {
    band = "Very high";
  } else if (clipped >= 0.6) {
    band = "High";
  } else if (clipped >= 0.35) {
    band = "Moderate";
  } else if (clipped >= 0.15) {
    band = "Low";
  }
  return `${band} (${percent}%)`;
}

function summarizeTurnInternals(turn) {
  const ingestPhase = findTurnPhase(turn, "ingest");
  const clarifyPhase = findTurnPhase(turn, "clarify");
  const route = String(turn?.route || "").trim().toLowerCase();
  const trace = turn && typeof turn.trace === "object" ? turn.trace : null;
  const ingestData = ingestPhase && typeof ingestPhase.data === "object" ? ingestPhase.data : {};
  const clarifyData = clarifyPhase && typeof clarifyPhase.data === "object" ? clarifyPhase.data : {};

  let ambiguityText = "Not provided.";
  const ambiguityScore = Number(ingestData.ambiguity_score);
  if (Number.isFinite(ambiguityScore)) {
    ambiguityText = describeAmbiguity(ambiguityScore);
  } else if (route === "command") {
    ambiguityText = "Not applicable (slash command).";
  }

  let ambiguitiesText = "None reported.";
  const reasons = Array.isArray(ingestData.reasons)
    ? ingestData.reasons.map((item) => String(item || "").trim()).filter(Boolean)
    : [];
  if (reasons.length) {
    ambiguitiesText = reasons.join("; ");
  } else if (route === "command") {
    ambiguitiesText = "Not applicable (slash command).";
  }

  let clarificationText = "Not required.";
  const clarifyStatus = String(clarifyPhase?.status || "").trim().toLowerCase();
  const clarificationQuestion = String(
    clarifyData.question || ingestData.clarification_question || ""
  ).trim();
  if (clarifyStatus === "required") {
    clarificationText = clarificationQuestion
      ? `Required: ${clarificationQuestion}`
      : "Required before commit.";
  } else if (clarifyStatus === "resolved") {
    const resolution = String(clarifyData.resolution || "resolved").trim();
    clarificationText = `Resolved (${resolution}).`;
  } else if (clarifyStatus === "cancelled") {
    clarificationText = "Cancelled by user.";
  } else if (route === "command") {
    clarificationText = "Not applicable (slash command).";
  }

  let traceText = "Not captured.";
  const traceSummary =
    trace && trace.summary && typeof trace.summary === "object"
      ? String(trace.summary.overall || "").trim()
      : "";
  if (traceSummary) {
    traceText = traceSummary;
  } else if (route === "command") {
    traceText = "Not applicable (slash command).";
  }

  return {
    ambiguity: ambiguityText,
    ambiguities: ambiguitiesText,
    clarification: clarificationText,
    trace: traceText,
  };
}

function summarizeCommitOperations(turn) {
  const commitPhase = findTurnPhase(turn, "commit");
  const commitData = commitPhase && typeof commitPhase.data === "object" ? commitPhase.data : {};
  const operations = Array.isArray(commitData.operations) ? commitData.operations : [];
  const lines = [];

  for (const op of operations) {
    if (!op || typeof op !== "object") {
      continue;
    }
    const result = op.result && typeof op.result === "object" ? op.result : {};
    const resultType = String(result.result_type || "").trim();
    const opLabel = String(op.tool || "").trim() || resultType || "operation";
    const fact = String(result.fact || "").trim() || "-";
    lines.push(`${opLabel} :: ${fact}`);
  }

  return lines;
}

function appendUserMessage(text) {
  const log = document.getElementById("chat-log");
  const article = document.createElement("article");
  article.className = "message user-message";
  article.innerHTML = `<header class="message-header">user</header><div class="message-body">${escapeHtml(text)}</div>`;
  log.appendChild(article);
  log.scrollTop = log.scrollHeight;
}

function appendGatewayTurn(turn) {
  const template = document.getElementById("message-template");
  const fragment = template.content.cloneNode(true);
  const article = fragment.querySelector(".message");
  const header = fragment.querySelector(".message-header");
  const body = fragment.querySelector(".message-body");
  const phaseList = fragment.querySelector(".phase-list");
  article.classList.add("gateway-turn");

  const turnDetails = document.createElement("details");
  turnDetails.className = "turn-details";
  turnDetails.open = true;

  const turnSummary = document.createElement("summary");
  turnSummary.className = "turn-summary";
  turnSummary.innerHTML = `
    <span class="turn-summary-title">${escapeHtml(`console turn ${turn.turn_index}`)}</span>
    <span class="turn-summary-route">${escapeHtml(`route=${turn.route}`)}</span>
  `;

  const turnContent = document.createElement("div");
  turnContent.className = "turn-content";
  header.textContent = "";
  const phases = Array.isArray(turn.phases) ? turn.phases : [];
  const assistantText = String((turn.assistant && turn.assistant.text) || "").trim();
  body.classList.add("turn-message-body");
  body.innerHTML = "";
  const chatShell = document.createElement("div");
  chatShell.className = "turn-chat-shell";
  const replyLabelEl = document.createElement("p");
  replyLabelEl.className = "message-header turn-speaker-label";
  replyLabelEl.textContent = "PRETHINKER";
  const replyTextEl = document.createElement("p");
  replyTextEl.className = "turn-reply-bubble";
  replyTextEl.textContent = assistantText || "(no assistant reply text)";
  const operationLines = summarizeCommitOperations(turn);
  let operationListEl = null;
  if (operationLines.length) {
    operationListEl = document.createElement("div");
    operationListEl.className = "turn-operation-list";
    for (const line of operationLines) {
      const lineEl = document.createElement("p");
      lineEl.className = "turn-operation-line";
      lineEl.textContent = line;
      operationListEl.appendChild(lineEl);
    }
  }
  const internals = summarizeTurnInternals(turn);
  const internalsEl = document.createElement("div");
  internalsEl.className = "turn-internals";
  const internalsRows = [
    ["Ambiguity", internals.ambiguity],
    ["Ambiguities", internals.ambiguities],
    ["Clarification", internals.clarification],
    ["Trace", internals.trace],
  ];
  for (const [label, value] of internalsRows) {
    const rowEl = document.createElement("p");
    rowEl.className = "turn-internal-row";
    const labelEl = document.createElement("span");
    labelEl.className = "turn-internal-label";
    labelEl.textContent = `${label}:`;
    const valueEl = document.createElement("span");
    valueEl.className = "turn-internal-value";
    valueEl.textContent = String(value || "").trim() || "-";
    rowEl.appendChild(labelEl);
    rowEl.appendChild(valueEl);
    internalsEl.appendChild(rowEl);
  }
  chatShell.appendChild(replyLabelEl);
  chatShell.appendChild(replyTextEl);
  if (operationListEl) {
    chatShell.appendChild(operationListEl);
  }
  chatShell.appendChild(internalsEl);
  body.appendChild(chatShell);

  const turnTrace = turn && typeof turn.trace === "object" ? turn.trace : null;
  if (turnTrace) {
    const traceCard = document.createElement("section");
    traceCard.className = "phase-card trace-card";

    const traceDetails = document.createElement("details");
    traceDetails.className = "phase-details";
    traceDetails.open = false;

    const traceSummary = document.createElement("summary");
    traceSummary.className = "phase-summary-row";
    traceSummary.innerHTML = `
      <span class="phase-name">trace</span>
      <span class="phase-status">${escapeHtml(
        String((turnTrace.summary && turnTrace.summary.prethink_source) || "captured")
      )}</span>
    `;

    const traceBody = document.createElement("div");
    traceBody.className = "phase-body";
    traceBody.innerHTML = `
      <p class="phase-summary">${escapeHtml(
        String((turnTrace.summary && turnTrace.summary.overall) || "Compiler trace captured.")
      )}</p>
      <pre>${escapeHtml(JSON.stringify(turnTrace, null, 2))}</pre>
    `;

    traceDetails.appendChild(traceSummary);
    traceDetails.appendChild(traceBody);
    traceCard.appendChild(traceDetails);
    turnContent.appendChild(traceCard);
  }

  for (const phase of phases) {
    const card = document.createElement("section");
    card.className = "phase-card";

    const phaseDetails = document.createElement("details");
    phaseDetails.className = "phase-details";
    phaseDetails.open = false;

    const phaseSummary = document.createElement("summary");
    phaseSummary.className = "phase-summary-row";
    phaseSummary.innerHTML = `
      <span class="phase-name">${escapeHtml(phase.phase)}</span>
      <span class="phase-status">${escapeHtml(phase.status)}</span>
    `;

    const phaseBody = document.createElement("div");
    phaseBody.className = "phase-body";
    phaseBody.innerHTML = `
      <p class="phase-summary">${escapeHtml(phase.summary)}</p>
      <pre>${escapeHtml(JSON.stringify(phase.data, null, 2))}</pre>
    `;

    phaseDetails.appendChild(phaseSummary);
    phaseDetails.appendChild(phaseBody);
    card.appendChild(phaseDetails);
    phaseList.appendChild(card);
  }

  turnContent.appendChild(body);
  turnContent.appendChild(phaseList);
  turnDetails.appendChild(turnSummary);
  turnDetails.appendChild(turnContent);
  article.innerHTML = "";
  article.appendChild(turnDetails);

  const chatLog = document.getElementById("chat-log");
  chatLog.appendChild(article);
  chatLog.scrollTop = chatLog.scrollHeight;
  requestAnimationFrame(() => {
    chatLog.scrollTop = chatLog.scrollHeight;
    const pageBottom = Math.max(
      document.body.scrollHeight,
      document.documentElement.scrollHeight
    );
    window.scrollTo(0, pageBottom);
  });
}

function escapeHtml(text) {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

async function loadConfig() {
  const payload = await getJson("/api/config");
  state.config = payload.config;
  fillConfigForm(state.config);
}

async function submitUtterance(event) {
  event.preventDefault();
  const field = document.getElementById("utterance");
  const utterance = field.value.trim();
  if (!utterance) {
    return;
  }
  appendUserMessage(utterance);
  field.value = "";

  try {
    const payload = await getJson("/api/prethink", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        session_id: state.sessionId,
        utterance,
      }),
    });
    state.sessionId = payload.session_id;
    appendGatewayTurn(payload.turn);
  } catch (error) {
    appendGatewayTurn({
      turn_index: 0,
      route: "error",
      assistant: {
        text:
          `Prethinker Console unavailable at ${apiUrl("/api/health")}. ` +
          "Run `python ui_gateway/main.py` or use ?apiBase=http://127.0.0.1:8765",
      },
      phases: [
        {
          phase: "network",
          status: "error",
          summary: "Could not reach local Prethinker Console API.",
          data: { error: String(error) },
        },
      ],
    });
  }
}

async function saveConfig(event) {
  event.preventDefault();
  const form = document.getElementById("config-form");
  const formData = new FormData(form);
  const payload = {};
  const numericFields = new Set([
    "served_llm_context_length",
    "served_llm_timeout",
    "compiler_context_length",
    "compiler_timeout",
    "clarification_eagerness",
  ]);

  for (const [key, value] of formData.entries()) {
    if (numericFields.has(key)) {
      payload[key] = value === "" ? null : Number(value);
    } else {
      payload[key] = value;
    }
  }
  payload.strict_mode = form.elements.namedItem("strict_mode").checked;
  payload.require_final_confirmation = form.elements.namedItem("require_final_confirmation").checked;

  try {
    const response = await getJson("/api/config", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
    state.config = response.config;
    fillConfigForm(state.config);
    document.getElementById("config-status").textContent = "Config saved to local JSON state.";
  } catch (error) {
    document.getElementById("config-status").textContent = `Save failed: ${String(error)}`;
  }
}

function strictBouncerPayload(baseConfig) {
  return {
    ...baseConfig,
    strict_mode: true,
    compiler_mode: "strict",
    served_handoff_mode: "never",
    require_final_confirmation: true,
    clarification_eagerness: Math.max(0.75, Number(baseConfig?.clarification_eagerness || 0)),
  };
}

async function applyStrictBouncerLock() {
  try {
    const payload = strictBouncerPayload(state.config || {});
    const response = await getJson("/api/config", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
    state.config = response.config;
    fillConfigForm(state.config);
    document.getElementById("config-status").textContent =
      "Strict bouncer lock applied (compiler strict, handoff never, confirmation required).";
  } catch (error) {
    document.getElementById("config-status").textContent = `Strict lock failed: ${String(error)}`;
  }
}

async function resetSession() {
  try {
    const payload = await getJson("/api/session/reset", {
      headers: {
        "X-Session-Id": state.sessionId || "",
      },
    });
    state.sessionId = payload.session_id;
    document.getElementById("chat-log").innerHTML = "";
  } catch (error) {
    document.getElementById("config-status").textContent = `Reset failed: ${String(error)}`;
  }
}

async function exportSession() {
  if (!state.sessionId) {
    document.getElementById("config-status").textContent =
      "No active session yet. Send at least one turn before exporting.";
    return;
  }
  try {
    const payload = await getJson(`/api/session/state?session_id=${encodeURIComponent(state.sessionId)}`);
    const stamp = new Date().toISOString().replaceAll(":", "-").replaceAll(".", "-");
    const filename = `prethink-session-${state.sessionId}-${stamp}.json`;
    downloadTextFile(JSON.stringify(payload, null, 2), filename, "application/json");
    document.getElementById("config-status").textContent = `Exported session trace: ${filename}`;
  } catch (error) {
    document.getElementById("config-status").textContent = `Export failed: ${String(error)}`;
  }
}

function setConfigOpen(open) {
  state.configOpen = Boolean(open);
  document.body.classList.toggle("config-open", state.configOpen);

  const drawer = document.getElementById("config-drawer");
  const toggle = document.getElementById("config-toggle");
  if (drawer) {
    drawer.setAttribute("aria-hidden", state.configOpen ? "false" : "true");
  }
  if (toggle) {
    toggle.setAttribute("aria-expanded", state.configOpen ? "true" : "false");
  }
  try {
    localStorage.setItem(CONFIG_OPEN_KEY, state.configOpen ? "1" : "0");
  } catch (_error) {
    // localStorage can be unavailable in strict contexts
  }
}

function setHeroOpen(open) {
  state.heroOpen = Boolean(open);
  document.body.classList.toggle("hero-open", state.heroOpen);

  const drawer = document.getElementById("hero-drawer");
  const toggle = document.getElementById("hero-toggle");
  if (drawer) {
    drawer.setAttribute("aria-hidden", state.heroOpen ? "false" : "true");
  }
  if (toggle) {
    toggle.setAttribute("aria-expanded", state.heroOpen ? "true" : "false");
  }
  try {
    localStorage.setItem(HERO_OPEN_KEY, state.heroOpen ? "1" : "0");
  } catch (_error) {
    // localStorage can be unavailable in strict contexts
  }
}

function initHeroDrawer() {
  let initiallyOpen = false;
  try {
    initiallyOpen = localStorage.getItem(HERO_OPEN_KEY) === "1";
  } catch (_error) {
    initiallyOpen = false;
  }
  setHeroOpen(initiallyOpen);

  const toggle = document.getElementById("hero-toggle");
  const close = document.getElementById("hero-close");
  if (toggle) {
    toggle.addEventListener("click", () => setHeroOpen(!state.heroOpen));
  }
  if (close) {
    close.addEventListener("click", () => setHeroOpen(false));
  }
}

function initConfigDrawer() {
  let initiallyOpen = false;
  try {
    initiallyOpen = localStorage.getItem(CONFIG_OPEN_KEY) === "1";
  } catch (_error) {
    initiallyOpen = false;
  }
  setConfigOpen(initiallyOpen);

  const toggle = document.getElementById("config-toggle");
  const close = document.getElementById("config-close");
  if (toggle) {
    toggle.addEventListener("click", () => setConfigOpen(!state.configOpen));
  }
  if (close) {
    close.addEventListener("click", () => setConfigOpen(false));
  }
}

function initComposerKeyboardSubmit() {
  const utteranceField = document.getElementById("utterance");
  const chatForm = document.getElementById("chat-form");
  if (!utteranceField || !chatForm) {
    return;
  }
  utteranceField.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      chatForm.requestSubmit();
    }
  });
}

window.addEventListener("DOMContentLoaded", async () => {
  initHeroDrawer();
  initConfigDrawer();
  initComposerKeyboardSubmit();
  document.getElementById("chat-form").addEventListener("submit", submitUtterance);
  document.getElementById("config-form").addEventListener("submit", saveConfig);
  document.getElementById("reset-button").addEventListener("click", resetSession);
  document.getElementById("export-button").addEventListener("click", exportSession);
  document.getElementById("strict-lock-button").addEventListener("click", applyStrictBouncerLock);
  try {
    await loadConfig();
    document.getElementById("config-status").textContent =
      API_BASE ? `Connected to Prethinker Console at ${API_BASE}.` : "Connected to same-origin Prethinker Console.";
  } catch (error) {
    document.getElementById("config-status").textContent =
      `Could not load config from ${apiUrl("/api/config")}. ` +
      "Run `python ui_gateway/main.py` to enable Prethinker Console.";
  }
});
