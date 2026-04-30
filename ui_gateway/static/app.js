const state = {
  sessionId: null,
  config: null,
  configOpen: false,
  heroOpen: false,
  debugMode: false,
  turnInFlight: false,
  pendingClarification: null,
  turns: [],
};

const CONFIG_OPEN_KEY = "prethink_gateway_config_open";
const HERO_OPEN_KEY = "prethink_gateway_hero_open";
const DEBUG_MODE_KEY = "prethink_gateway_debug_mode";
const STRICT_LOCKED_CONFIG_FIELDS = new Set([
  "compiler_mode",
  "served_handoff_mode",
  "require_final_confirmation",
]);

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

const SEMANTIC_IR_PRIMARY = {
  backend: "lmstudio",
  baseUrl: "http://127.0.0.1:1234",
  model: "qwen/qwen3.6-35b-a3b",
  contextLength: 16384,
  timeout: 120,
  temperature: 0.0,
  topP: 0.82,
  topK: 20,
  thinking: false,
};

const PROFILE_EXAMPLES = {
  general: {
    title: "Kick the tires with ordinary language.",
    description:
      "Good first tests are simple facts, direct questions, and one ambiguous sentence that should force clarification instead of a guess.",
    watch:
      "Prethinker should either commit facts, answer from the KB, or pause for a clarification.",
    caution:
      "If a turn only looks good after heavy normalization, the trace will show that.",
    chips: [
      {
        label: "Family fact",
        example: "scotts mom and dad is ann and ian.",
      },
      {
        label: "Simple location",
        example: "hope lives in salem.",
      },
      {
        label: "Possessive relation",
        example: "barny is freds best friend.",
      },
      {
        label: "Query after a write",
        example: "can you make muffins with walnuts?",
      },
      {
        label: "Clarification pressure",
        example: "remember that it ships next week.",
      },
      {
        label: "Narrative sentence",
        example:
          "at 9am on friday morning fred and wilma entered the pinky penny supermarket and headed over to the turnips.",
      },
    ],
  },
  "medical@v0": {
    title: "Try bounded medical language.",
    description:
      "Good first tests name the patient explicitly, use concrete drugs, symptoms, or labs, and include one shorthand or pronoun turn that should trigger clarification.",
    watch:
      "Prethinker should normalize onto the bounded medical palette, keep the patient explicit when possible, and pause instead of inventing identity or diagnosis.",
    caution:
      "Do not trust vague shorthand or unresolved patient references to be silently sharpened into durable medical state.",
    chips: [
      {
        label: "Medication fact",
        example: "Priya is taking warfarin.",
      },
      {
        label: "Brand to generic",
        example: "Priya is taking Coumadin.",
      },
      {
        label: "Symptom fact",
        example: "Mira is short of breath.",
      },
      {
        label: "Lab event",
        example: "Priya's serum creatinine was repeated this afternoon.",
      },
      {
        label: "Pronoun clarification",
        example: "His serum creatinine was repeated this afternoon.",
      },
      {
        label: "Bounded safety check",
        example: "Priya is taking warfarin and she is pregnant.",
      },
    ],
  },
};

const PROMPT_BOOKS = {
  general: [
    {
      title: "Lineage rules, then a proof",
      setup: "Reset in general mode. This shows hard facts, new rules, and a query that only works after those commits.",
      steps: [
        { label: "Write fact", utterance: "Cora is a parent of Dax." },
        { label: "Write fact", utterance: "Dax is a parent of Emma." },
        { label: "Add rule", utterance: "If X is a parent of Y then X is an ancestor of Y." },
        {
          label: "Add rule",
          utterance: "If X is a parent of Y and Y is an ancestor of Z then X is an ancestor of Z.",
        },
        { label: "Query proof", utterance: "Is Cora an ancestor of Emma?" },
      ],
      watch:
        "The ledger should show two facts, two rules, and a query answered from backward chaining rather than a prose guess.",
    },
    {
      title: "Ask from memory, not vibes",
      setup: "Use this to make the query route visibly depend on a previous write.",
      steps: [
        { label: "Write fact", utterance: "Hope lives in Salem." },
        { label: "Query fact", utterance: "Where does Hope live?" },
        { label: "Query miss", utterance: "Where does Maya live?" },
      ],
      watch:
        "Hope should answer from the KB; Maya should not be invented just because the question shape is familiar.",
    },
    {
      title: "Correction becomes a state update",
      setup: "Start with a clean statement, then force a correction.",
      steps: [
        { label: "Write fact", utterance: "The launch plan ships next week." },
        { label: "Correct it", utterance: "Actually, the launch plan ships in two weeks." },
        { label: "Query current", utterance: "When does the launch plan ship?" },
      ],
      watch:
        "The compiler should use a correction path instead of leaving two equally durable launch dates.",
    },
    {
      title: "Clarification beats guessing",
      setup: "Use an intentionally underspecified write.",
      steps: [
        { label: "Ambiguous write", utterance: "Remember that it ships next week." },
        { label: "Clarify subject", utterance: "The launch plan." },
      ],
      watch:
        "The first turn should hold because 'it' has no grounded referent. The follow-up should resolve the staged turn rather than starting a random new fact.",
    },
    {
      title: "Context check without sidecar",
      setup: "Keep the experimental sidecar off. This probes whether the main Semantic IR path uses recent context conservatively.",
      steps: [
        { label: "Context", utterance: "Scott's mom is Ann." },
        { label: "Context", utterance: "Priya's brother is Omar." },
        { label: "Ambiguous turn", utterance: "His brother lives in Morro Bay." },
      ],
      watch:
        "The main Semantic IR trace should explain whether context resolves 'his' or whether the compiler should still hold for clarification.",
    },
    {
      title: "Conjunctions and ingredient queries",
      setup: "Store a compact ingredient statement, then query one true and one absent ingredient.",
      steps: [
        { label: "Write bundle", utterance: "Muffins are made with flour, cranberries, and walnuts." },
        { label: "Query true", utterance: "Can you make muffins with walnuts?" },
        { label: "Query absent", utterance: "Can you make muffins with raisins?" },
      ],
      watch:
        "The trace should show normalization into ingredient facts. The absent ingredient should not be treated as known.",
    },
    {
      title: "Narrative compression",
      setup: "Try a long ordinary sentence that needs stable predicates rather than a beautiful summary.",
      steps: [
        {
          label: "Narrative",
          utterance:
            "At 9am on Friday morning Fred and Wilma entered the Pinky Penny supermarket and headed over to the turnips.",
        },
        { label: "Query", utterance: "Where did Fred go at 9am on Friday morning?" },
      ],
      watch:
        "This should exercise parsing and rescue behavior. Debug details should make clear what was normalized before the KB accepted it.",
    },
    {
      title: "Claim, identity, and time should stay separate",
      setup: "Use the semantic IR compiler path. This pressures claim-vs-fact, identity ambiguity, and temporal correction without a story-specific prompt.",
      steps: [
        {
          label: "Claim",
          utterance:
            "Arthur says the whole Silverton estate is his because Beatrice lived in London too long.",
        },
        {
          label: "Clarify place",
          utterance: "Beatrice says she meant London, Ontario, not London, UK.",
        },
        {
          label: "Ledger fact",
          utterance: "The ledger says Silverton, A. returned from Heathrow in April 2024.",
        },
        {
          label: "Correction",
          utterance: "Correction: that return stamp was April 2023, still A. Silverton.",
        },
        { label: "Query", utterance: "Does this prove Arthur forfeited his share?" },
      ],
      watch:
        "Look for claims remaining claims, London ambiguity staying explicit, A. Silverton not collapsing to Arthur, and the forfeiture query avoiding a hard conclusion.",
    },
    {
      title: "Route boundary",
      setup: "Use ordinary assistant requests that should not become KB mutations.",
      steps: [
        { label: "Other", utterance: "Translate this to French: the build passed." },
        { label: "Other", utterance: "Explain in plain words why semantic drift might happen." },
      ],
      watch:
        "These should stay outside durable symbolic memory unless you intentionally enable a served handoff.",
    },
  ],
  "medical@v0": [
    {
      title: "Brand name collapses to a drug concept",
      setup: "Apply the medical@v0 preset, then reset the session.",
      steps: [
        { label: "Write medication", utterance: "Priya is taking Coumadin." },
        { label: "Query medication", utterance: "Is Priya taking warfarin?" },
      ],
      watch:
        "The ledger should store a medication fact using the bounded palette, with Coumadin normalized toward warfarin.",
    },
    {
      title: "Vague shorthand, clarified into a lab result",
      setup: "Keep medical@v0 active.",
      steps: [
        { label: "Ambiguous write", utterance: "Mara's pressure is bad lately." },
        { label: "Clarify result", utterance: "Mara's blood pressure reading was high." },
        { label: "Query result", utterance: "Was Mara's blood pressure high?" },
      ],
      watch:
        "The first turn should hold. The clarification should commit a high blood-pressure result, not a diagnosis or advice.",
    },
    {
      title: "Pronouns are not patient identities",
      setup: "Try this immediately after reset, then resolve it.",
      steps: [
        { label: "Ambiguous write", utterance: "His serum creatinine was repeated this afternoon." },
        { label: "Clarify patient", utterance: "Priya." },
      ],
      watch:
        "The medical guard should hold until the patient identity is clarified, even though the lab phrase is clear.",
    },
    {
      title: "Context-dependent pronoun",
      setup: "Keep the sidecar off and let recent context compete with strict patient identity checks.",
      steps: [
        { label: "Context", utterance: "Priya is taking warfarin." },
        { label: "Context", utterance: "Mara has asthma." },
        { label: "Ambiguous write", utterance: "Her creatinine was repeated this afternoon." },
      ],
      watch:
        "The Semantic IR workspace can inspect context, but the durable write should still be conservative if two female patients are in scope.",
    },
    {
      title: "Bounded safety context, not broad advice",
      setup: "Keep medical@v0 active.",
      steps: [
        { label: "Write facts", utterance: "Priya is taking warfarin and she is pregnant." },
        { label: "Query fact", utterance: "Is Priya pregnant?" },
      ],
      watch:
        "The ledger should show bounded structured facts; this is context capture, not open-ended clinical recommendation.",
    },
    {
      title: "Allergy and medication are different slots",
      setup: "Use two statements that should not collapse into one predicate.",
      steps: [
        { label: "Write allergy", utterance: "Mara is allergic to penicillin." },
        { label: "Write medication", utterance: "Mara is taking amoxicillin." },
        { label: "Query allergy", utterance: "Is Mara allergic to penicillin?" },
      ],
      watch:
        "The profile should keep allergy and medication-use facts separate, even when both mention drug-like concepts.",
    },
    {
      title: "Symptom versus diagnosis",
      setup: "Force the profile to keep a finding separate from a condition.",
      steps: [
        { label: "Write symptom", utterance: "Mira is short of breath." },
        { label: "Write condition", utterance: "Mira has asthma." },
        { label: "Query symptom", utterance: "Is Mira short of breath?" },
      ],
      watch:
        "The ledger should distinguish symptom/finding capture from condition capture.",
    },
    {
      title: "Ambiguous shorthand that should stay soft",
      setup: "Use medically common shorthand with missing slot detail.",
      steps: [
        { label: "Ambiguous", utterance: "Priya's sugar looked bad this morning." },
        { label: "Clarify", utterance: "Her blood glucose result was high." },
      ],
      watch:
        "The guard should avoid deciding whether 'sugar' means diabetes, glucose, diet, or another concept until the follow-up pins it down.",
    },
    {
      title: "Open-ended medical advice boundary",
      setup: "Use an assistant-style request that should not be converted into durable state.",
      steps: [
        { label: "Other", utterance: "Should Priya stop taking warfarin?" },
        { label: "Other", utterance: "Explain what high creatinine means." },
      ],
      watch:
        "These are not KB mutations. The useful behavior is refusing to smuggle advice or broad medical explanation into committed facts.",
    },
  ],
};

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
  const activeProfile = config.active_profile || "general";
  const semanticEnabled = Boolean(config.semantic_ir_enabled);
  const semanticModel = String(config.semantic_ir_model || "").trim();
  const compilerModel = semanticEnabled && semanticModel ? semanticModel : config.compiler_model;
  const compilerBackend = String(config.compiler_backend || "").trim();
  document.getElementById("profile-label").textContent = activeProfile;
  document.getElementById("compiler-model-label").textContent = compilerModel;
  document.getElementById("compiler-mode-label").textContent =
    `${semanticEnabled ? "semantic_ir_v1" : config.compiler_mode} / ${compilerBackend || "backend?"} / handoff=${config.served_handoff_mode}`;
  document.getElementById("served-model-label").textContent = config.served_llm_model;
  document.getElementById("profile-pill").textContent = `Profile: ${activeProfile}`;
  document.getElementById("compiler-pill").textContent = semanticEnabled
    ? `SIR: ${compilerModel}`
    : `Compiler: ${compilerModel}`;
  document.getElementById("strict-pill").textContent = config.strict_mode ? "Strict mode on" : "Strict mode off";
  const ledgerProfileNote = document.getElementById("ledger-profile-note");
  if (ledgerProfileNote) {
    ledgerProfileNote.textContent = `Watching the current session in ${activeProfile} mode.`;
  }
}

function activeProfileExamples(config) {
  const profileId = String(config?.active_profile || "general").trim().toLowerCase();
  return PROFILE_EXAMPLES[profileId] || PROFILE_EXAMPLES.general;
}

function syncProfileExamples(config) {
  const profile = activeProfileExamples(config);
  const title = document.getElementById("empty-state-title");
  const description = document.getElementById("empty-state-description");
  const watch = document.getElementById("empty-state-watch");
  const caution = document.getElementById("empty-state-caution");
  if (title) {
    title.textContent = profile.title;
  }
  if (description) {
    description.textContent = profile.description;
  }
  if (watch) {
    watch.innerHTML = `<strong>What to watch for:</strong> ${escapeHtml(profile.watch)}`;
  }
  if (caution) {
    caution.innerHTML = `<strong>What not to trust:</strong> ${escapeHtml(profile.caution)}`;
  }
  const chips = Array.from(document.querySelectorAll(".example-chip"));
  chips.forEach((button, index) => {
    const item = profile.chips[index];
    if (!item) {
      button.hidden = true;
      return;
    }
    button.hidden = false;
    button.textContent = item.label;
    button.dataset.example = item.example;
  });
  renderPromptBook(config);
}

function activePromptBook(config) {
  const profileId = String(config?.active_profile || "general").trim().toLowerCase();
  return PROMPT_BOOKS[profileId] || PROMPT_BOOKS.general;
}

function loadPromptBookUtterance(utterance) {
  const field = document.getElementById("utterance");
  if (!field) {
    return;
  }
  field.value = String(utterance || "").trim();
  field.focus();
}

function renderPromptBook(config) {
  const list = document.getElementById("prompt-book-list");
  const profileLabel = document.getElementById("prompt-book-profile");
  if (!list) {
    return;
  }
  const activeProfile = String(config?.active_profile || "general").trim() || "general";
  if (profileLabel) {
    profileLabel.textContent = activeProfile;
  }
  clearElement(list);
  for (const item of activePromptBook(config)) {
    const card = document.createElement("article");
    card.className = "prompt-book-card";

    const title = document.createElement("h4");
    title.textContent = item.title;
    card.appendChild(title);

    const setup = document.createElement("p");
    setup.className = "prompt-book-setup";
    setup.textContent = item.setup;
    card.appendChild(setup);

    const steps = Array.isArray(item.steps) && item.steps.length
      ? item.steps
      : [{ label: "Utterance", utterance: item.utterance }];
    const stepList = document.createElement("div");
    stepList.className = "prompt-book-steps";
    steps.forEach((step, index) => {
      const row = document.createElement("div");
      row.className = "prompt-book-step";

      const number = document.createElement("span");
      number.className = "prompt-book-step-number";
      number.textContent = String(index + 1);
      row.appendChild(number);

      const button = document.createElement("button");
      button.className = "prompt-book-utterance";
      button.type = "button";
      const label = String(step.label || "Utterance").trim();
      const utteranceText = String(step.utterance || "").trim();
      button.innerHTML = `<span>${escapeHtml(label)}</span>${escapeHtml(utteranceText)}`;
      button.addEventListener("click", () => loadPromptBookUtterance(utteranceText));
      row.appendChild(button);

      stepList.appendChild(row);
    });
    card.appendChild(stepList);

    const watch = document.createElement("p");
    watch.className = "prompt-book-watch";
    watch.textContent = `Watch: ${item.watch}`;
    card.appendChild(watch);

    list.appendChild(card);
  }
}

function syncConnectionPill(message, tone = "neutral") {
  const pill = document.getElementById("connection-pill");
  pill.textContent = message;
  pill.dataset.tone = tone;
}

function updateEmptyState() {
  const emptyState = document.getElementById("empty-state");
  const chatLog = document.getElementById("chat-log");
  if (!emptyState || !chatLog) {
    return;
  }
  emptyState.hidden = chatLog.childElementCount > 0;
}

function updatePendingBanner() {
  const banner = document.getElementById("pending-banner");
  if (!banner) {
    return;
  }
  if (!state.pendingClarification || !state.pendingClarification.question) {
    banner.hidden = true;
    banner.textContent = "";
    return;
  }
  banner.hidden = false;
  banner.textContent =
    `Pending clarification: ${state.pendingClarification.question} ` +
    "Reply directly, or use /cancel to drop the staged turn.";
}

function collapseChatExpandos() {
  const chatLog = document.getElementById("chat-log");
  if (!chatLog) {
    return;
  }
  chatLog
    .querySelectorAll(".phase-details[open], .debug-text-details[open]")
    .forEach((details) => {
    details.open = false;
  });
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
  updateConfigFormAffordances(config);
  syncHero(config);
  syncProfileExamples(config);
}

function updateConfigFormAffordances(config) {
  const form = document.getElementById("config-form");
  if (!form) {
    return;
  }
  const strictMode = Boolean(config?.strict_mode);
  for (const name of STRICT_LOCKED_CONFIG_FIELDS) {
    const field = form.elements.namedItem(name);
    if (!field) {
      continue;
    }
    field.disabled = strictMode;
    const wrapper = field.closest(".config-field, .config-flag");
    if (wrapper) {
      wrapper.classList.toggle("is-locked", strictMode);
    }
  }
}

function findTurnPhase(turn, phaseName) {
  const phases = Array.isArray(turn?.phases) ? turn.phases : [];
  return phases.find((phase) => phase && phase.phase === phaseName) || null;
}

function turnExecutionProtocol(turn) {
  const packet =
    ((((turn || {}).trace || {}).prethink || {}).packet) || {};
  return packet && typeof packet.execution_protocol === "object"
    ? packet.execution_protocol
    : null;
}

function turnSegmentsByPhase(turn, phaseName) {
  const protocol = turnExecutionProtocol(turn);
  const segments = Array.isArray(protocol?.segments) ? protocol.segments : [];
  return segments.filter((segment) => {
    if (!segment || typeof segment !== "object") {
      return false;
    }
    return String(segment.phase || "").trim().toLowerCase() === phaseName;
  });
}

function formatSegmentText(text) {
  return String(text || "")
    .replace(/\s*\n+\s*/g, " / ")
    .replace(/\s+/g, " ")
    .trim();
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

  let noteText = "None reported.";
  const { semantic, ir, admission } = semanticTrace(trace);
  const reasons = Array.isArray(ingestData.reasons)
    ? ingestData.reasons.map((item) => String(item || "").trim()).filter(Boolean)
    : [];
  const selfNotes = Array.isArray(ir?.self_check?.notes)
    ? ir.self_check.notes.map((item) => String(item || "").trim()).filter(Boolean)
    : [];
  if (ir) {
    const risk = String(ir?.self_check?.bad_commit_risk || "").trim();
    const decision = String(ir.decision || "").trim();
    const turnType = String(ir.turn_type || "").trim();
    const noteParts = [];
    if (decision || turnType) {
      noteParts.push(`SIR ${decision || "decision?"}/${turnType || "turn?"}`);
    }
    if (risk) {
      noteParts.push(`risk=${risk}`);
    }
    if (selfNotes.length) {
      noteParts.push(selfNotes.slice(0, 2).join("; "));
    }
    noteText = noteParts.join("; ") || "Semantic IR workspace captured.";
  } else if (reasons.length) {
    noteText = reasons.join("; ");
  } else if (route === "command") {
    noteText = "Not applicable (slash command).";
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

  let compilerPathText = "";
  const traceSummary =
    trace && trace.summary && typeof trace.summary === "object"
      ? trace.summary
      : {};
  const prethinkSource = String(traceSummary.prethink_source || "").trim();
  const freethinkerAction = String(traceSummary.freethinker_action || "").trim().toLowerCase();
  const parseRescues = Array.isArray(traceSummary.parse_rescues)
    ? traceSummary.parse_rescues.map((item) => String(item || "").trim()).filter(Boolean)
    : [];
  const meaningfulParseRescues = parseRescues.filter(
    (item) => item !== "clarification_fields_normalized"
  );
  const compilerPathParts = [];
  if (ir) {
    const model = String(semantic.model || "").trim();
    compilerPathParts.push(`semantic_ir_v1${model ? `=${model}` : ""}`);
    if (admission && Object.keys(admission).length) {
      const ops = Array.isArray(admission.operations) ? admission.operations : [];
      const admitted = Number.isFinite(Number(admission.admitted_count))
        ? Number(admission.admitted_count)
        : ops.filter((op) => op && typeof op === "object" && Boolean(op.admitted)).length;
      const skipped = Number.isFinite(Number(admission.skipped_count))
        ? Number(admission.skipped_count)
        : Math.max(0, ops.length - admitted);
      compilerPathParts.push(`admission admitted=${admitted} skipped=${skipped}`);
    }
  }
  if (prethinkSource && prethinkSource !== "primary") {
    compilerPathParts.push(`routing=${prethinkSource}`);
  }
  if (freethinkerAction && freethinkerAction !== "skipped") {
    compilerPathParts.push(`freethinker=${freethinkerAction}`);
  }
  if (meaningfulParseRescues.length) {
    compilerPathParts.push(`parse adjusted via ${meaningfulParseRescues.join(", ")}`);
  }
  if (compilerPathParts.length) {
    compilerPathText = compilerPathParts.join("; ");
  } else if (route === "command") {
    compilerPathText = "Not applicable (slash command).";
  }

  return {
    ambiguity: ambiguityText,
    note: noteText,
    clarification: clarificationText,
    compilerPath: compilerPathText,
  };
}

function operationClauseText(op) {
  if (!op || typeof op !== "object") {
    return "";
  }
  const result = op.result && typeof op.result === "object" ? op.result : {};
  return String(
    result.fact ||
      result.rule ||
      result.query ||
      result.prolog_query ||
      op.clause ||
      op.query ||
      ""
  ).trim();
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
    const clause = operationClauseText(op);
    if (!clause || opLabel === "none") {
      continue;
    }
    lines.push(`${opLabel} :: ${clause}`);
  }

  const querySegments = turnSegmentsByPhase(turn, "query");
  const executedQueryCount = operations.filter((op) => {
    if (!op || typeof op !== "object") {
      return false;
    }
    return String(op.tool || "").trim() === "query_rows";
  }).length;
  if (querySegments.length > executedQueryCount) {
    for (const segment of querySegments.slice(executedQueryCount)) {
      const text = formatSegmentText(segment?.text || "");
      if (!text) {
        continue;
      }
      lines.push(`query_segment :: ${text} [detected, not executed]`);
    }
  }

  return lines;
}

function turnExecution(turn) {
  const commitPhase = findTurnPhase(turn, "commit");
  return commitPhase && typeof commitPhase.data === "object" ? commitPhase.data : {};
}

function countSuccessfulOperations(execution, toolName) {
  const operations = Array.isArray(execution?.operations) ? execution.operations : [];
  return operations.filter((op) => {
    if (!op || typeof op !== "object") {
      return false;
    }
    if (String(op.tool || "").trim() !== toolName) {
      return false;
    }
    const status = String((op.result && op.result.status) || "").trim().toLowerCase();
    return status === "success";
  }).length;
}

function countSuccessfulMutations(execution) {
  return (
    countSuccessfulOperations(execution, "assert_fact") +
    countSuccessfulOperations(execution, "assert_rule") +
    countSuccessfulOperations(execution, "retract_fact")
  );
}

function effectiveTurnRoute(turn) {
  const route = String(turn?.route || "other").trim().toLowerCase();
  const execution = turnExecution(turn);
  const executionStatus = String(execution?.status || "").trim().toLowerCase();
  const executionIntent = String(execution?.intent || "").trim().toLowerCase();
  if (executionStatus === "error") {
    if (["assert_fact", "assert_rule", "retract", "retract_fact", "write"].includes(executionIntent)) {
      return "write";
    }
    return route;
  }
  if (countSuccessfulMutations(execution) > 0) {
    return "write";
  }
  const operations = Array.isArray(execution?.operations) ? execution.operations : [];
  const hasQueryOperation = operations.some((op) => String(op?.tool || "").trim() === "query_rows");
  if (hasQueryOperation || execution?.query_result) {
    return "query";
  }
  return route;
}

function describeExecutedQuery(execution, utterance) {
  const queryResult = execution?.query_result;
  if (!queryResult || typeof queryResult !== "object") {
    return "";
  }
  const status = String(queryResult.status || "").trim().toLowerCase();
  const loweredUtterance = String(utterance || "").trim().toLowerCase();
  const yesNoLeadins = [
    "is ",
    "are ",
    "does ",
    "do ",
    "did ",
    "was ",
    "were ",
    "can ",
    "could ",
    "should ",
    "would ",
    "will ",
    "has ",
    "have ",
    "had ",
  ];
  const isYesNo = loweredUtterance.endsWith("?") && yesNoLeadins.some((prefix) => loweredUtterance.includes(` ${prefix}`) || loweredUtterance.startsWith(prefix));
  if (status === "success") {
    const variables = Array.isArray(queryResult.variables) ? queryResult.variables : [];
    const rows = Array.isArray(queryResult.rows) ? queryResult.rows : [];
    const numRows = Number(queryResult.num_rows ?? rows.length ?? 0);
    if (isYesNo && !variables.length) {
      return "Final query resolved true.";
    }
    return `Final query matched ${numRows} row(s).`;
  }
  if (status === "no_results") {
    return isYesNo ? "Final query resolved false." : "Final query matched no rows.";
  }
  return "Final query did not complete cleanly.";
}

function splitClauseArgs(rawArgs) {
  const args = [];
  let current = "";
  let depth = 0;
  for (const ch of String(rawArgs || "")) {
    if (ch === "," && depth === 0) {
      const token = current.trim();
      if (token) {
        args.push(token);
      }
      current = "";
      continue;
    }
    if (ch === "(") {
      depth += 1;
    } else if (ch === ")" && depth > 0) {
      depth -= 1;
    }
    current += ch;
  }
  const token = current.trim();
  if (token) {
    args.push(token);
  }
  return args;
}

function parseClauseText(clause) {
  const text = String(clause || "").trim();
  const match = /^([a-z_][a-z0-9_]*)\((.*)\)\.$/i.exec(text);
  if (!match) {
    return null;
  }
  return {
    predicate: match[1],
    args: splitClauseArgs(match[2]),
  };
}

function cleanLedgerToken(token) {
  return String(token || "")
    .trim()
    .replace(/^['"]+|['"]+$/g, "")
    .replace(/\.$/, "");
}

function isLikelyVariable(token) {
  const cleaned = cleanLedgerToken(token);
  return /^[A-Z_]/.test(cleaned);
}

function humanizeLedgerAtom(atom, { person = false } = {}) {
  const cleaned = cleanLedgerToken(atom);
  if (!cleaned) {
    return "";
  }
  const words = cleaned
    .replace(/_measurement$/i, "")
    .split("_")
    .filter(Boolean);
  if (!words.length) {
    return cleaned;
  }
  if (person) {
    return words
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  }
  return words.join(" ");
}

function predicateLabel(predicate) {
  return String(predicate || "")
    .trim()
    .replaceAll("_", " ");
}

function summarizeFactBody(predicate, args) {
  if (!predicate) {
    return "";
  }
  if (!Array.isArray(args) || !args.length) {
    return predicateLabel(predicate);
  }
  const object = (index, options = {}) => humanizeLedgerAtom(args[index], options);
  switch (predicate) {
    case "taking":
      return args.length >= 2 ? `taking ${object(1)}` : "taking";
    case "pregnant":
      return "pregnant";
    case "allergic_to":
      return args.length >= 2 ? `allergic to ${object(1)}` : "allergic";
    case "has_condition":
      return args.length >= 2 ? `has ${object(1)}` : "has condition";
    case "has_symptom":
      return args.length >= 2 ? `has symptom ${object(1)}` : "has symptom";
    case "underwent_lab_test":
      return args.length >= 2 ? `underwent ${object(1)}` : "underwent lab test";
    case "lab_result_high":
      return args.length >= 2 ? `${object(1)} high` : "lab result high";
    case "lab_result_rising":
      return args.length >= 2 ? `${object(1)} rising` : "lab result rising";
    case "lab_result_abnormal":
      return args.length >= 2 ? `${object(1)} abnormal` : "lab result abnormal";
    case "lives_in":
      return args.length >= 2 ? `lives in ${object(1, { person: true })}` : "lives somewhere";
    case "parent":
      return args.length >= 2 ? `parent of ${object(1, { person: true })}` : "parent";
    case "brother":
      return args.length >= 2 ? `brother of ${object(1, { person: true })}` : "brother";
    case "sister":
      return args.length >= 2 ? `sister of ${object(1, { person: true })}` : "sister";
    case "manager":
      return args.length >= 2 ? `manager of ${object(1, { person: true })}` : "manager";
    case "entered":
      return args.length >= 3
        ? `entered ${object(1, { person: true })} at ${object(2)}${args[3] ? ` ${object(3)}` : ""}`
        : "entered";
    case "headed_over":
      return args.length >= 2
        ? `headed over to ${object(1)}${args[2] ? ` from ${object(2)}` : ""}`
        : "headed over";
    default:
      if (args.length === 1) {
        return predicateLabel(predicate);
      }
      const remainder = args
        .slice(1)
        .map((token) => humanizeLedgerAtom(token, { person: true }))
        .join(", ");
      return `${predicateLabel(predicate)} ${remainder}`.trim();
  }
}

function deriveFactEntityKey(args) {
  if (!Array.isArray(args) || !args.length) {
    return "_session";
  }
  const first = cleanLedgerToken(args[0]);
  if (!first || isLikelyVariable(first)) {
    return "_session";
  }
  return first.toLowerCase();
}

function deriveEntityLabel(entityKey) {
  if (!entityKey || entityKey === "_session") {
    return "Session / global";
  }
  return humanizeLedgerAtom(entityKey, { person: true });
}

function deriveTouchedEntities(execution) {
  const operations = Array.isArray(execution?.operations) ? execution.operations : [];
  const labels = new Set();
  for (const op of operations) {
    const tool = String(op?.tool || "").trim();
    if (!["assert_fact", "retract_fact"].includes(tool)) {
      continue;
    }
    const clause = operationClauseText(op);
    const parsed = parseClauseText(clause);
    if (!parsed) {
      continue;
    }
    labels.add(deriveEntityLabel(deriveFactEntityKey(parsed.args)));
  }
  return Array.from(labels);
}

function buildQueryLedgerEntry({ turn, execution, clauseText }) {
  return {
    turnIndex: Number(turn?.turn_index || 0),
    utterance: String(turn?.utterance || "").trim(),
    clause: String(clauseText || turn?.utterance || "").trim(),
    summary: describeExecutedQuery(execution, turn?.utterance || "") || "Query recorded.",
  };
}

function buildLedgerState(turns) {
  const facts = new Map();
  const rules = new Map();
  const queryEntries = [];
  const latestTurn = Array.isArray(turns) && turns.length ? turns[turns.length - 1] : null;

  for (const turn of Array.isArray(turns) ? turns : []) {
    if (!turn || typeof turn !== "object") {
      continue;
    }
    const execution = turnExecution(turn);
    const operations = Array.isArray(execution?.operations) ? execution.operations : [];
    let sawQueryOp = false;
    for (const op of operations) {
      if (!op || typeof op !== "object") {
        continue;
      }
      const tool = String(op.tool || "").trim();
      const clause = operationClauseText(op);
      if (tool === "assert_fact" && clause) {
        const parsed = parseClauseText(clause);
        const entityKey = parsed ? deriveFactEntityKey(parsed.args) : "_session";
        facts.set(clause, {
          clause,
          predicate: parsed?.predicate || "",
          args: parsed?.args || [],
          entityKey,
          entityLabel: deriveEntityLabel(entityKey),
          summary: parsed ? summarizeFactBody(parsed.predicate, parsed.args) : clause,
          turnIndex: Number(turn.turn_index || 0),
        });
      } else if (tool === "retract_fact" && clause) {
        facts.delete(clause);
      } else if (tool === "assert_rule" && clause) {
        rules.set(clause, {
          clause,
          turnIndex: Number(turn.turn_index || 0),
        });
      } else if (tool === "query_rows") {
        sawQueryOp = true;
        queryEntries.push(buildQueryLedgerEntry({ turn, execution, clauseText: clause }));
      }
    }
    if (!sawQueryOp && execution?.query_result && effectiveTurnRoute(turn) === "query") {
      queryEntries.push(buildQueryLedgerEntry({ turn, execution, clauseText: turn?.utterance || "" }));
    }
  }

  const entities = new Map();
  for (const fact of facts.values()) {
    if (!entities.has(fact.entityKey)) {
      entities.set(fact.entityKey, {
        key: fact.entityKey,
        label: fact.entityLabel,
        facts: [],
        latestTurnIndex: 0,
      });
    }
    const group = entities.get(fact.entityKey);
    group.facts.push(fact);
    group.latestTurnIndex = Math.max(group.latestTurnIndex, fact.turnIndex);
  }

  const entityGroups = Array.from(entities.values())
    .map((group) => ({
      ...group,
      facts: group.facts.sort((a, b) => b.turnIndex - a.turnIndex || a.clause.localeCompare(b.clause)),
    }))
    .sort((a, b) => {
      if (a.key === "_session") {
        return 1;
      }
      if (b.key === "_session") {
        return -1;
      }
      return b.latestTurnIndex - a.latestTurnIndex || a.label.localeCompare(b.label);
    });

  const ruleEntries = Array.from(rules.values()).sort(
    (a, b) => b.turnIndex - a.turnIndex || a.clause.localeCompare(b.clause)
  );
  const recentQueries = queryEntries
    .sort((a, b) => b.turnIndex - a.turnIndex || a.clause.localeCompare(b.clause))
    .slice(0, 6);

  return {
    latestTurn,
    latestTurnIndex: Number(latestTurn?.turn_index || 0),
    entityGroups,
    ruleEntries,
    recentQueries,
    entityCount: entityGroups.length,
    factCount: facts.size,
    ruleCount: ruleEntries.length,
    queryCount: queryEntries.length,
  };
}

function summarizeLatestLedgerChange(turn) {
  if (!turn || typeof turn !== "object") {
    return {
      badge: "Waiting",
      tone: "neutral",
      title: "No structured memory has been built in this session yet.",
      detail: "Send a turn and this panel will show what Prethinker actually stored, held, or queried.",
    };
  }
  const route = effectiveTurnRoute(turn);
  const execution = turnExecution(turn);
  const clarifyPhase = findTurnPhase(turn, "clarify");
  if (String(clarifyPhase?.status || "").trim().toLowerCase() === "required") {
    const question = String(clarifyPhase?.data?.question || "").trim();
    return {
      badge: "Held",
      tone: "caution",
      title: "Latest turn paused before changing durable memory.",
      detail: question ? `Clarification needed: ${question}` : "Clarification was required before Prethinker could continue.",
    };
  }
  if (route === "write") {
    const facts = countSuccessfulOperations(execution, "assert_fact");
    const rules = countSuccessfulOperations(execution, "assert_rule");
    const retracts = countSuccessfulOperations(execution, "retract_fact");
    const parts = [];
    if (facts) {
      parts.push(`${facts} fact${facts === 1 ? "" : "s"}`);
    }
    if (rules) {
      parts.push(`${rules} rule${rules === 1 ? "" : "s"}`);
    }
    if (retracts) {
      parts.push(`${retracts} retraction${retracts === 1 ? "" : "s"}`);
    }
    const touchedEntities = deriveTouchedEntities(execution);
    return {
      badge: parts.length ? "Committed" : "Write attempt",
      tone: parts.length ? "success" : "neutral",
      title: parts.length
        ? `Latest turn committed ${parts.join(", ")}.`
        : "Latest turn was treated as a write, but nothing durable changed.",
      detail: touchedEntities.length
        ? `Updated ${touchedEntities.join(", ")}.`
        : describeExecutedQuery(execution, turn.utterance || "") || "No new entity bucket was changed.",
    };
  }
  if (route === "query") {
    return {
      badge: "Query",
      tone: "success",
      title: "Latest turn queried the current session memory.",
      detail: describeExecutedQuery(execution, turn.utterance || "") || "Query completed without changing durable memory.",
    };
  }
  return {
    badge: "Reviewed",
    tone: String(execution?.status || "").trim().toLowerCase() === "error" ? "danger" : "neutral",
    title: "Latest turn did not change durable memory.",
    detail: String((turn.assistant && turn.assistant.text) || "Prethinker reviewed the turn without a durable mutation.").trim(),
  };
}

function setPathCard(kind, { value, meta, tone = "neutral" }) {
  const card = document.getElementById(`path-${kind}-card`);
  const valueNode = document.getElementById(`path-${kind}-value`);
  const metaNode = document.getElementById(`path-${kind}-meta`);
  if (card) {
    card.className = `path-card tone-${tone}`;
  }
  if (valueNode) {
    valueNode.textContent = value;
  }
  if (metaNode) {
    metaNode.textContent = meta;
  }
}

function renderPathStrip(ledger) {
  const latestTurn = ledger?.latestTurn || null;
  const execution = turnExecution(latestTurn);
  const route = latestTurn ? effectiveTurnRoute(latestTurn) : "";
  const frontDoor = findTurnPhase(latestTurn, "ingest")?.data || {};
  const clarifyPhase = findTurnPhase(latestTurn, "clarify");
  const commitPhase = findTurnPhase(latestTurn, "commit");
  const activeProfile = String(state.config?.active_profile || "general").trim() || "general";
  const strictMode = Boolean(state.config?.strict_mode);
  const freethinkerPolicy = String(state.config?.freethinker_resolution_policy || "off").trim();
  const compilerIntent = String(frontDoor.compiler_intent || execution?.intent || route || "").trim();

  setPathCard("profile", {
    value: activeProfile,
    meta: `${strictMode ? "strict" : "open"} | sidecar ${freethinkerPolicy}`,
    tone: activeProfile === "medical@v0" ? "success" : "neutral",
  });

  if (!latestTurn) {
    setPathCard("route", { value: "Waiting", meta: "No turn yet", tone: "neutral" });
    setPathCard("gate", { value: "Idle", meta: "No pending hold", tone: "neutral" });
    setPathCard("action", { value: "None", meta: "No runtime call", tone: "neutral" });
  } else {
    setPathCard("route", {
      value: route || "other",
      meta: compilerIntent ? `compiler intent: ${compilerIntent}` : "slash or fallback path",
      tone: route === "write" || route === "query" ? "success" : "neutral",
    });

    const clarifyStatus = String(clarifyPhase?.status || "").trim().toLowerCase();
    const executionStatus = String(execution?.status || "").trim().toLowerCase();
    if (clarifyStatus === "required" || state.pendingClarification) {
      const question = String(
        clarifyPhase?.data?.question || state.pendingClarification?.question || ""
      ).trim();
      setPathCard("gate", {
        value: "Holding",
        meta: question || "Clarification required",
        tone: "caution",
      });
    } else if (executionStatus === "error" || String(commitPhase?.status || "").trim().toLowerCase() === "failed") {
      setPathCard("gate", {
        value: "Failed",
        meta: "Runtime or parse error",
        tone: "danger",
      });
    } else {
      setPathCard("gate", {
        value: "Clear",
        meta: clarifyStatus === "resolved" ? "Clarification resolved" : "No hold",
        tone: "success",
      });
    }

    const factWrites = countSuccessfulOperations(execution, "assert_fact");
    const ruleWrites = countSuccessfulOperations(execution, "assert_rule");
    const retractWrites = countSuccessfulOperations(execution, "retract_fact");
    const queryOps = Array.isArray(execution?.operations)
      ? execution.operations.filter((op) => String(op?.tool || "").trim() === "query_rows").length
      : 0;
    const mutationCount = factWrites + ruleWrites + retractWrites;
    if (executionStatus === "error" || String(commitPhase?.status || "").trim().toLowerCase() === "failed") {
      setPathCard("action", {
        value: "Blocked",
        meta: "No mutation",
        tone: "danger",
      });
    } else if (mutationCount > 0) {
      setPathCard("action", {
        value: `${mutationCount} mutation${mutationCount === 1 ? "" : "s"}`,
        meta: `${factWrites} fact | ${ruleWrites} rule | ${retractWrites} retract`,
        tone: "success",
      });
    } else if (queryOps > 0 || execution?.query_result) {
      setPathCard("action", {
        value: "Query",
        meta: describeExecutedQuery(execution, latestTurn?.utterance || "") || "Runtime query",
        tone: "success",
      });
    } else if (clarifyStatus === "required") {
      setPathCard("action", {
        value: "Paused",
        meta: "No mutation",
        tone: "caution",
      });
    } else {
      setPathCard("action", {
        value: "No mutation",
        meta: route === "command" ? "Console command" : "Reviewed only",
        tone: executionStatus === "error" ? "danger" : "neutral",
      });
    }
  }

  const factCount = Number(ledger?.factCount || 0);
  const ruleCount = Number(ledger?.ruleCount || 0);
  const queryCount = Number(ledger?.queryCount || 0);
  setPathCard("ledger", {
    value: `${factCount} fact${factCount === 1 ? "" : "s"}`,
    meta: `${ruleCount} rule${ruleCount === 1 ? "" : "s"} | ${queryCount} quer${queryCount === 1 ? "y" : "ies"} | console stream`,
    tone: factCount || ruleCount || queryCount ? "success" : "neutral",
  });
}

function clearElement(element) {
  if (element) {
    element.innerHTML = "";
  }
}

function renderLedger() {
  const ledger = buildLedgerState(state.turns);
  renderPathStrip(ledger);
  const activeProfile = String(state.config?.active_profile || "general").trim() || "general";
  const profileNote = document.getElementById("ledger-profile-note");
  if (profileNote) {
    profileNote.textContent = `Watching the current session in ${activeProfile} mode.`;
  }

  const setText = (id, text) => {
    const node = document.getElementById(id);
    if (node) {
      node.textContent = text;
    }
  };

  setText("ledger-entity-count", String(ledger.entityCount));
  setText("ledger-fact-count", String(ledger.factCount));
  setText("ledger-rule-count", String(ledger.ruleCount));
  setText("ledger-query-count", String(ledger.queryCount));
  setText(
    "ledger-entity-summary",
    ledger.factCount
      ? `${ledger.factCount} stored fact${ledger.factCount === 1 ? "" : "s"} across ${ledger.entityCount} bucket${ledger.entityCount === 1 ? "" : "s"}.`
      : "No stored facts yet."
  );
  setText(
    "ledger-rule-summary",
    ledger.ruleCount
      ? `${ledger.ruleCount} active rule${ledger.ruleCount === 1 ? "" : "s"}.`
      : "No active rules."
  );
  setText(
    "ledger-query-summary",
    ledger.queryCount
      ? `${ledger.queryCount} query event${ledger.queryCount === 1 ? "" : "s"} in this session.`
      : "No query history yet."
  );

  const latest = summarizeLatestLedgerChange(ledger.latestTurn);
  const latestCard = document.getElementById("ledger-latest-card");
  const latestBadge = document.getElementById("ledger-latest-badge");
  const latestTitle = document.getElementById("ledger-latest-title");
  const latestDetail = document.getElementById("ledger-latest-detail");
  if (latestCard) {
    latestCard.className = `ledger-latest-card tone-${latest.tone}`;
  }
  if (latestBadge) {
    latestBadge.className = `ledger-latest-badge tone-${latest.tone}`;
    latestBadge.textContent = latest.badge;
  }
  if (latestTitle) {
    latestTitle.textContent = latest.title;
  }
  if (latestDetail) {
    latestDetail.textContent = latest.detail;
  }

  const entityList = document.getElementById("ledger-entity-list");
  clearElement(entityList);
  if (entityList) {
    if (!ledger.entityGroups.length) {
      const empty = document.createElement("p");
      empty.className = "ledger-empty";
      empty.textContent = "No structured facts have been committed in this session yet.";
      entityList.appendChild(empty);
    } else {
      const fragment = document.createDocumentFragment();
      for (const group of ledger.entityGroups) {
        const card = document.createElement("section");
        card.className = "ledger-entity-card";
        const header = document.createElement("div");
        header.className = "ledger-entity-header";
        const title = document.createElement("p");
        title.className = "ledger-entity-title";
        title.textContent = group.label;
        const meta = document.createElement("p");
        meta.className = "ledger-entity-meta";
        meta.textContent = `${group.facts.length} fact${group.facts.length === 1 ? "" : "s"}`;
        header.appendChild(title);
        header.appendChild(meta);
        card.appendChild(header);

        const facts = document.createElement("div");
        facts.className = "ledger-fact-list";
        for (const fact of group.facts) {
          const item = document.createElement("div");
          item.className = "ledger-fact-item";
          if (fact.turnIndex === ledger.latestTurnIndex && ledger.latestTurnIndex > 0) {
            item.classList.add("is-fresh");
          }
          const head = document.createElement("div");
          head.className = "ledger-item-head";
          const summary = document.createElement("p");
          summary.className = "ledger-item-title";
          summary.textContent =
            fact.summary.charAt(0).toUpperCase() + fact.summary.slice(1);
          head.appendChild(summary);
          if (fact.turnIndex === ledger.latestTurnIndex && ledger.latestTurnIndex > 0) {
            const badge = document.createElement("span");
            badge.className = "ledger-item-badge";
            badge.textContent = "new";
            head.appendChild(badge);
          }
          const clause = document.createElement("p");
          clause.className = "ledger-clause";
          clause.textContent = fact.clause;
          item.appendChild(head);
          item.appendChild(clause);
          facts.appendChild(item);
        }
        card.appendChild(facts);
        fragment.appendChild(card);
      }
      entityList.appendChild(fragment);
    }
  }

  const ruleList = document.getElementById("ledger-rule-list");
  clearElement(ruleList);
  if (ruleList) {
    if (!ledger.ruleEntries.length) {
      const empty = document.createElement("p");
      empty.className = "ledger-empty";
      empty.textContent = "No rules have been asserted in this session yet.";
      ruleList.appendChild(empty);
    } else {
      const fragment = document.createDocumentFragment();
      for (const rule of ledger.ruleEntries) {
        const item = document.createElement("div");
        item.className = "ledger-rule-item";
        if (rule.turnIndex === ledger.latestTurnIndex && ledger.latestTurnIndex > 0) {
          item.classList.add("is-fresh");
        }
        const head = document.createElement("div");
        head.className = "ledger-item-head";
        const title = document.createElement("p");
        title.className = "ledger-item-title";
        title.textContent = "Rule in session memory";
        head.appendChild(title);
        if (rule.turnIndex === ledger.latestTurnIndex && ledger.latestTurnIndex > 0) {
          const badge = document.createElement("span");
          badge.className = "ledger-item-badge";
          badge.textContent = "new";
          head.appendChild(badge);
        }
        const clause = document.createElement("p");
        clause.className = "ledger-clause";
        clause.textContent = rule.clause;
        item.appendChild(head);
        item.appendChild(clause);
        fragment.appendChild(item);
      }
      ruleList.appendChild(fragment);
    }
  }

  const queryList = document.getElementById("ledger-query-list");
  clearElement(queryList);
  if (queryList) {
    if (!ledger.recentQueries.length) {
      const empty = document.createElement("p");
      empty.className = "ledger-empty";
      empty.textContent = "Queries answered from the current session memory will appear here.";
      queryList.appendChild(empty);
    } else {
      const fragment = document.createDocumentFragment();
      for (const query of ledger.recentQueries) {
        const item = document.createElement("div");
        item.className = "ledger-query-item";
        if (query.turnIndex === ledger.latestTurnIndex && ledger.latestTurnIndex > 0) {
          item.classList.add("is-fresh");
        }
        const head = document.createElement("div");
        head.className = "ledger-item-head";
        const title = document.createElement("p");
        title.className = "ledger-item-title";
        title.textContent = query.summary;
        head.appendChild(title);
        if (query.turnIndex === ledger.latestTurnIndex && ledger.latestTurnIndex > 0) {
          const badge = document.createElement("span");
          badge.className = "ledger-item-badge";
          badge.textContent = "new";
          head.appendChild(badge);
        }
        const detail = document.createElement("p");
        detail.className = "ledger-item-subline";
        detail.textContent = query.utterance || query.clause;
        const clause = document.createElement("p");
        clause.className = "ledger-clause";
        clause.textContent = query.clause;
        item.appendChild(head);
        item.appendChild(detail);
        item.appendChild(clause);
        fragment.appendChild(item);
      }
      queryList.appendChild(fragment);
    }
  }
}

function outcomeSummary(turn) {
  const route = effectiveTurnRoute(turn);
  const execution = turnExecution(turn);
  const clarifyPhase = findTurnPhase(turn, "clarify");
  const commitPhase = findTurnPhase(turn, "commit");
  const operationLines = summarizeCommitOperations(turn);
  const ingestSegments = turnSegmentsByPhase(turn, "ingest");
  const querySegments = turnSegmentsByPhase(turn, "query");
  const executedQueryCount = Array.isArray(execution?.operations)
    ? execution.operations.filter((op) => String(op?.tool || "").trim() === "query_rows").length
    : 0;
  const points = [];

  if (route === "command") {
    return {
      badge: "Command",
      tone: "neutral",
      title: "Handled as a console command instead of a language turn.",
      points: ["This bypassed the compiler and deterministic commit path."],
    };
  }

  if (String(clarifyPhase?.status || "").trim().toLowerCase() === "required") {
    const question = String(clarifyPhase?.data?.question || "").trim();
    if (question) {
      points.push(`Clarification question: ${question}`);
    }
    return {
      badge: "Needs clarification",
      tone: "caution",
      title: "Prethinker held this turn instead of guessing.",
      points,
    };
  }

  if (
    String(execution?.status || "").trim().toLowerCase() === "error" ||
    String(commitPhase?.status || "").trim().toLowerCase() === "failed"
  ) {
    const errors = Array.isArray(execution?.errors)
      ? execution.errors.map((item) => String(item || "").trim()).filter(Boolean)
      : [];
    points.push(...errors);
    return {
      badge: "Blocked",
      tone: "danger",
      title: "Deterministic execution failed; no KB mutation was committed.",
      points,
    };
  }

  if (route === "write") {
    const writesApplied = Number(
      execution?.writes_applied ||
        (countSuccessfulOperations(execution, "assert_fact") +
          countSuccessfulOperations(execution, "assert_rule") +
          countSuccessfulOperations(execution, "retract_fact")) ||
        0
    );
    if (writesApplied > 0) {
      points.push(`${writesApplied} deterministic mutation(s) applied.`);
    }
    const factWrites = countSuccessfulOperations(execution, "assert_fact");
    const ruleWrites = countSuccessfulOperations(execution, "assert_rule");
    const retractWrites = countSuccessfulOperations(execution, "retract_fact");
    if (factWrites > 0) {
      points.push(`${factWrites} fact assertion(s) applied.`);
    }
    if (ruleWrites > 0) {
      points.push(`${ruleWrites} rule assertion(s) applied.`);
    }
    if (retractWrites > 0) {
      points.push(`${retractWrites} retraction(s) applied.`);
    }
    const querySummary = describeExecutedQuery(execution, turn?.utterance || "");
    if (querySummary) {
      points.push(querySummary);
    }
    if (querySegments.length) {
      const ingestCount = ingestSegments.length;
      const queryCount = querySegments.length;
      points.push(
        `Segment plan detected ${ingestCount} ingest segment(s) and ${queryCount} query segment(s).`
      );
      if (executedQueryCount < queryCount) {
        const missingCount = queryCount - executedQueryCount;
        points.push(
          `${missingCount} query segment(s) were detected but not executed by the current pipeline.`
        );
      }
    }
    return {
      badge: String(commitPhase?.status || "").trim().toLowerCase() === "applied" ? "Committed" : "Write attempt",
      tone: String(commitPhase?.status || "").trim().toLowerCase() === "applied" ? "success" : "danger",
      title:
        writesApplied > 0
          ? "Prethinker converted the utterance into structured KB updates."
          : "Prethinker treated this as a write, but nothing was committed.",
      points,
    };
  }

  if (route === "query") {
    const rows = Array.isArray(execution?.query_result?.rows) ? execution.query_result.rows.length : null;
    if (rows !== null) {
      points.push(rows > 0 ? `Query matched ${rows} result row(s).` : "Query matched no rows.");
    }
    return {
      badge: "Answered",
      tone: "success",
      title: "Prethinker treated this as a deterministic query.",
      points,
    };
  }

  return {
    badge: "Reviewed",
    tone: String(execution?.status || "").trim().toLowerCase() === "error" ? "danger" : "neutral",
    title: "Prethinker inspected the turn without committing a KB mutation.",
    points,
  };
}

function appendUserMessage(text) {
  const log = document.getElementById("chat-log");
  const article = document.createElement("article");
  article.className = "message user-message";
  article.innerHTML = `<header class="message-header">user</header><div class="message-body">${escapeHtml(text)}</div>`;
  log.appendChild(article);
  log.scrollTop = log.scrollHeight;
  updateEmptyState();
}

function prettyJson(value) {
  return JSON.stringify(value, null, 2);
}

function semanticTrace(turnTrace) {
  const parse = turnTrace && typeof turnTrace.parse === "object" ? turnTrace.parse : {};
  const prethink = turnTrace && typeof turnTrace.prethink === "object" ? turnTrace.prethink : {};
  const parseSemantic = parse && typeof parse.semantic_ir === "object" ? parse.semantic_ir : {};
  const prethinkSemantic =
    prethink && typeof prethink.semantic_ir === "object" ? prethink.semantic_ir : {};
  const semantic = parseSemantic.parsed ? parseSemantic : prethinkSemantic;
  const ir = semantic && typeof semantic.parsed === "object" ? semantic.parsed : null;
  return {
    parse,
    prethink,
    semantic,
    ir,
    admission:
      (((parse?.normalized || {}).admission_diagnostics) ||
        (((parse?.rescues || [])[0] || {}).admission_diagnostics) ||
        {}),
  };
}

function hasSemanticTrace(turnTrace) {
  return Boolean(semanticTrace(turnTrace).ir);
}

function semanticTraceSummary(turnTrace) {
  const { semantic, ir, admission } = semanticTrace(turnTrace);
  if (!ir) {
    return "";
  }
  const model = String(semantic.model || "").trim() || "semantic_ir_v1";
  const decision = String(ir.decision || "").trim() || "decision?";
  const hasAdmission =
    admission &&
    (Array.isArray(admission.operations) ||
      Object.prototype.hasOwnProperty.call(admission, "admitted_count") ||
      Object.prototype.hasOwnProperty.call(admission, "skipped_count"));
  if (!hasAdmission) {
    return `${model} -> ${decision} | admission not reached`;
  }
  const ops = Array.isArray(admission?.operations) ? admission.operations : [];
  const admitted = Number.isFinite(Number(admission?.admitted_count))
    ? Number(admission.admitted_count)
    : ops.filter((op) => op && typeof op === "object" && Boolean(op.admitted)).length;
  const skipped = Number.isFinite(Number(admission?.skipped_count))
    ? Number(admission.skipped_count)
    : Math.max(0, ops.length - admitted);
  const counts = admitted !== null || skipped !== null
    ? ` | admitted ${admitted || 0}, skipped ${skipped || 0}`
    : "";
  return `${model} -> ${decision}${counts}`;
}

function debugValue(value, fallback = "-") {
  const text = String(value ?? "").trim();
  return text || fallback;
}

function debugArray(value) {
  return Array.isArray(value) ? value : [];
}

function debugCount(value) {
  return debugArray(value).length;
}

function debugArgs(args) {
  return debugArray(args).map((item) => String(item ?? "").trim()).filter(Boolean).join(", ");
}

function debugClauseList(clauses) {
  return debugArray(clauses).map((item) => String(item ?? "").trim()).filter(Boolean);
}

function appendDebugKvGrid(parent, rows) {
  const grid = document.createElement("div");
  grid.className = "pipeline-kv-grid";
  for (const [label, value] of rows) {
    const item = document.createElement("p");
    item.className = "pipeline-kv";
    const key = document.createElement("span");
    key.className = "pipeline-kv-key";
    key.textContent = String(label || "");
    const val = document.createElement("span");
    val.className = "pipeline-kv-value";
    val.textContent = debugValue(value);
    item.appendChild(key);
    item.appendChild(val);
    grid.appendChild(item);
  }
  parent.appendChild(grid);
}

function appendDebugTable(parent, headers, rows, emptyText = "None.") {
  if (!Array.isArray(rows) || !rows.length) {
    const empty = document.createElement("p");
    empty.className = "pipeline-empty";
    empty.textContent = emptyText;
    parent.appendChild(empty);
    return;
  }
  const wrap = document.createElement("div");
  wrap.className = "pipeline-table-wrap";
  const table = document.createElement("table");
  table.className = "pipeline-table";
  const thead = document.createElement("thead");
  const headRow = document.createElement("tr");
  for (const header of headers) {
    const th = document.createElement("th");
    th.textContent = String(header || "");
    headRow.appendChild(th);
  }
  thead.appendChild(headRow);
  table.appendChild(thead);
  const tbody = document.createElement("tbody");
  for (const row of rows) {
    const tr = document.createElement("tr");
    for (const cell of row) {
      const td = document.createElement("td");
      td.textContent = debugValue(cell, "");
      tr.appendChild(td);
    }
    tbody.appendChild(tr);
  }
  table.appendChild(tbody);
  wrap.appendChild(table);
  parent.appendChild(wrap);
}

function appendDebugClauseList(parent, title, clauses) {
  const section = document.createElement("section");
  section.className = "pipeline-subsection";
  const heading = document.createElement("p");
  heading.className = "pipeline-subtitle";
  heading.textContent = title;
  section.appendChild(heading);
  const list = debugClauseList(clauses);
  if (!list.length) {
    const empty = document.createElement("p");
    empty.className = "pipeline-empty";
    empty.textContent = "None.";
    section.appendChild(empty);
  } else {
    const code = document.createElement("pre");
    code.className = "pipeline-code-list";
    code.textContent = list.join("\n");
    section.appendChild(code);
  }
  parent.appendChild(section);
}

function buildEpistemicBoundaryPanel({ admitted, skipped, clauses, worlds }) {
  const facts = debugClauseList(clauses?.facts);
  const rules = debugClauseList(clauses?.rules);
  const retracts = debugClauseList(clauses?.retracts);
  const queries = debugClauseList(clauses?.queries);
  const scopedClauses = debugClauseList(worlds?.clauses);
  const worldRows = debugArray(worlds?.worlds);
  const panel = document.createElement("div");
  panel.className = "epistemic-boundary";

  const globalZone = document.createElement("section");
  globalZone.className = "epistemic-zone global-truth";
  const globalTitle = document.createElement("p");
  globalTitle.className = "epistemic-zone-title";
  globalTitle.textContent = "Global KB truth";
  const globalText = document.createElement("p");
  globalText.className = "epistemic-zone-copy";
  globalText.textContent =
    admitted > 0
      ? "Only admitted operations can mutate the durable Prolog KB."
      : "No durable KB mutation survived admission in this turn.";
  globalZone.appendChild(globalTitle);
  globalZone.appendChild(globalText);
  appendDebugKvGrid(globalZone, [
    ["admitted operations", admitted],
    ["facts", facts.length],
    ["rules", rules.length],
    ["retracts", retracts.length],
    ["queries", queries.length],
  ]);

  const scopedZone = document.createElement("section");
  scopedZone.className = "epistemic-zone scoped-worlds";
  const scopedTitle = document.createElement("p");
  scopedTitle.className = "epistemic-zone-title";
  scopedTitle.textContent = "Scoped worlds";
  const scopedText = document.createElement("p");
  scopedText.className = "epistemic-zone-copy";
  scopedText.textContent =
    scopedClauses.length || worldRows.length
      ? "Blocked, quarantined, or supported-but-skipped candidates are kept as isolated diagnostic memory."
      : "No isolated diagnostic world was needed for this turn.";
  scopedZone.appendChild(scopedTitle);
  scopedZone.appendChild(scopedText);
  appendDebugKvGrid(scopedZone, [
    ["worlds", worlds?.world_count ?? worldRows.length],
    ["scoped operations", worlds?.operation_count ?? debugArray(worlds?.operations).length],
    ["wrapper clauses", scopedClauses.length],
    ["skipped/challenged", skipped],
    ["authority", worlds?.authority || "-"],
  ]);

  panel.appendChild(globalZone);
  panel.appendChild(scopedZone);
  return panel;
}

function createPipelineLayer(title, summary = "") {
  const layer = document.createElement("section");
  layer.className = "pipeline-layer";
  const header = document.createElement("div");
  header.className = "pipeline-layer-header";
  const name = document.createElement("p");
  name.className = "pipeline-layer-title";
  name.textContent = title;
  header.appendChild(name);
  if (summary) {
    const status = document.createElement("p");
    status.className = "pipeline-layer-summary";
    status.textContent = summary;
    header.appendChild(status);
  }
  layer.appendChild(header);
  return layer;
}

function semanticModelInputPayload(semantic) {
  const modelInput = semantic && typeof semantic.model_input === "object" ? semantic.model_input : {};
  if (modelInput.input_payload && typeof modelInput.input_payload === "object") {
    return modelInput.input_payload;
  }
  if (modelInput.scenario && typeof modelInput.scenario === "object") {
    return modelInput.scenario;
  }
  return {};
}

function buildPipelineTraceBubble(turn) {
  const turnTrace = turn && typeof turn.trace === "object" ? turn.trace : null;
  const { semantic, ir, parse, admission } = semanticTrace(turnTrace);
  if (!ir) {
    return null;
  }

  const card = document.createElement("section");
  card.className = "phase-card debug-bubble-card pipeline-trace-card";
  const details = document.createElement("details");
  details.className = "phase-details debug-bubble-details";
  details.open = true;

  const model = String(semantic.model || "").trim() || "semantic_ir_v1";
  const decision = String(ir.decision || "").trim() || "decision?";
  const projected = String(admission?.projected_decision || "").trim();
  const admitted = Number.isFinite(Number(admission?.admitted_count))
    ? Number(admission.admitted_count)
    : debugArray(admission?.operations).filter((op) => op && typeof op === "object" && Boolean(op.admitted)).length;
  const skipped = Number.isFinite(Number(admission?.skipped_count))
    ? Number(admission.skipped_count)
    : Math.max(0, debugArray(admission?.operations).length - admitted);

  const summary = document.createElement("summary");
  summary.className = "phase-summary-row debug-bubble-summary";
  summary.innerHTML = `
    <span class="phase-name">pipeline trace</span>
    <span class="phase-status">${escapeHtml(
      `${model} -> ${decision}${projected ? ` / ${projected}` : ""} | admitted ${admitted}, skipped ${skipped}`
    )}</span>
  `;

  const body = document.createElement("div");
  body.className = "phase-body pipeline-trace-body";
  const intro = document.createElement("p");
  intro.className = "pipeline-intro";
  intro.textContent =
    "One-turn view: model context, Semantic IR proposal, deterministic admission, truth-maintenance pressure, and the KB/query surface.";
  body.appendChild(intro);

  const payload = semanticModelInputPayload(semantic);
  const context = debugArray(payload.context);
  const allowed = debugArray(payload.allowed_predicates);
  const contracts = debugArray(payload.predicate_contracts);
  const kbPack = payload.kb_context_pack && typeof payload.kb_context_pack === "object"
    ? payload.kb_context_pack
    : {};
  const kbClauses = [
    ...debugArray(kbPack.exact_clauses),
    ...debugArray(kbPack.relevant_clauses),
    ...debugArray(kbPack.recent_committed_logic),
  ].filter(Boolean);

  const inputLayer = createPipelineLayer("Layer 0 - Model Input", "what the semantic compiler saw");
  appendDebugKvGrid(inputLayer, [
    ["domain", payload.domain || turn.domain || state.config?.active_profile || "-"],
    ["model", model],
    ["context items", context.length],
    ["predicate palette", allowed.length],
    ["predicate contracts", contracts.length],
    ["KB context clauses", kbClauses.length],
  ]);
  if (context.length) {
    appendDebugTable(
      inputLayer,
      ["context item"],
      context.slice(0, 12).map((item) => [item]),
      "No context visible."
    );
  }
  body.appendChild(inputLayer);

  const selfCheck = ir.self_check && typeof ir.self_check === "object" ? ir.self_check : {};
  const workspaceLayer = createPipelineLayer("Layer 1 - Semantic Workspace", "soft proposal, not authority");
  appendDebugKvGrid(workspaceLayer, [
    ["decision", ir.decision],
    ["turn type", ir.turn_type],
    ["bad commit risk", selfCheck.bad_commit_risk],
    ["entities", debugCount(ir.entities)],
    ["assertions", debugCount(ir.assertions)],
    ["unsafe implications", debugCount(ir.unsafe_implications)],
    ["candidate ops", debugCount(ir.candidate_operations)],
    ["clarifications", debugCount(ir.clarification_questions)],
  ]);
  appendDebugTable(
    workspaceLayer,
    ["entity", "normalized", "type", "confidence"],
    debugArray(ir.entities).slice(0, 12).map((entity) => [
      entity?.surface || entity?.id || "",
      entity?.normalized || "",
      entity?.type || "",
      entity?.confidence ?? "",
    ]),
    "No entities proposed."
  );
  body.appendChild(workspaceLayer);

  const opsLayer = createPipelineLayer("Layer 2 - Candidate Operations", "what could become writes or queries");
  appendDebugTable(
    opsLayer,
    ["#", "op", "predicate(args)", "source", "safety", "polarity", "clause"],
    debugArray(ir.candidate_operations).map((op, index) => [
      index,
      op?.operation || "",
      `${op?.predicate || ""}(${debugArgs(op?.args)})`,
      op?.source || "",
      op?.safety || "",
      op?.polarity || "",
      op?.clause || "",
    ]),
    "No candidate operations proposed."
  );
  body.appendChild(opsLayer);

  const diagnostics = admission && typeof admission === "object" ? admission : {};
  const clauses = diagnostics.clauses && typeof diagnostics.clauses === "object" ? diagnostics.clauses : {};
  const admissionLayer = createPipelineLayer("Layer 3 - Deterministic Admission", "mapper decides what survives");
  appendDebugKvGrid(admissionLayer, [
    ["model decision", diagnostics.model_decision || ir.decision],
    ["projected decision", diagnostics.projected_decision || "-"],
    ["projection reason", diagnostics.projection_reason || "-"],
    ["operations", diagnostics.operation_count ?? debugCount(diagnostics.operations)],
    ["admitted", admitted],
    ["skipped/challenged", skipped],
  ]);
  appendDebugTable(
    admissionLayer,
    ["#", "admit", "effect", "predicate(args)", "skip/challenge", "rationale"],
    debugArray(diagnostics.operations).map((op) => [
      op?.index ?? "",
      op?.admitted ? "yes" : "no",
      op?.effect || "",
      `${op?.predicate || ""}(${debugArgs(op?.args)})`,
      op?.skip_reason || "",
      debugArray(op?.rationale_codes).join(", "),
    ]),
    "Admission diagnostics not recorded."
  );
  const clauseGrid = document.createElement("div");
  clauseGrid.className = "pipeline-clause-grid";
  appendDebugClauseList(clauseGrid, "facts admitted", clauses.facts);
  appendDebugClauseList(clauseGrid, "rules admitted", clauses.rules);
  appendDebugClauseList(clauseGrid, "retracts admitted", clauses.retracts);
  appendDebugClauseList(clauseGrid, "queries admitted", clauses.queries);
  admissionLayer.appendChild(clauseGrid);
  body.appendChild(admissionLayer);

  const tm = diagnostics.truth_maintenance && typeof diagnostics.truth_maintenance === "object"
    ? diagnostics.truth_maintenance
    : (ir.truth_maintenance && typeof ir.truth_maintenance === "object" ? ir.truth_maintenance : {});
  const alignment = diagnostics.truth_maintenance_alignment && typeof diagnostics.truth_maintenance_alignment === "object"
    ? diagnostics.truth_maintenance_alignment
    : {};
  const tmLayer = createPipelineLayer("Layer 4 - Truth Maintenance", "support, conflicts, and derived consequences");
  appendDebugKvGrid(tmLayer, [
    ["support links", debugCount(tm.support_links)],
    ["conflicts", debugCount(tm.conflicts)],
    ["retraction plan", debugCount(tm.retraction_plan)],
    ["derived consequences", debugCount(tm.derived_consequences)],
    ["fuzzy edges", alignment.fuzzy_edge_count ?? debugCount(alignment.fuzzy_edges)],
  ]);
  appendDebugTable(
    tmLayer,
    ["op", "kind", "role", "support ref"],
    debugArray(tm.support_links).slice(0, 12).map((item) => [
      item?.operation_index ?? "",
      item?.support_kind || "",
      item?.role || "",
      item?.support_ref || "",
    ]),
    "No support links recorded."
  );
  appendDebugTable(
    tmLayer,
    ["statement / conflict", "basis / existing", "policy"],
    [
      ...debugArray(tm.conflicts).map((item) => [
        item?.why || item?.conflict_kind || "",
        item?.existing_ref || "",
        item?.recommended_policy || "",
      ]),
      ...debugArray(tm.derived_consequences).map((item) => [
        item?.statement || "",
        debugArray(item?.basis).join(", "),
        item?.commit_policy || "",
      ]),
    ],
    "No conflict or derived-consequence pressure recorded."
  );
  body.appendChild(tmLayer);

  const worlds = diagnostics.epistemic_worlds && typeof diagnostics.epistemic_worlds === "object"
    ? diagnostics.epistemic_worlds
    : (parse?.epistemic_worlds && typeof parse.epistemic_worlds === "object" ? parse.epistemic_worlds : {});
  if (worlds && (Number(worlds.world_count || 0) || debugArray(worlds.clauses).length)) {
    const worldsLayer = createPipelineLayer(
      "Layer 5 - Epistemic Worlds",
      "scoped memory for blocked candidates, not global truth"
    );
    worldsLayer.appendChild(buildEpistemicBoundaryPanel({ admitted, skipped, clauses, worlds }));
    appendDebugTable(
      worldsLayer,
      ["world", "op", "predicate(args)", "policy", "reason"],
      debugArray(worlds.worlds).flatMap((world) =>
        debugArray(world?.operations).map((op) => [
          world?.world_id || op?.world_id || "",
          op?.world_operation_id || op?.operation_index || "",
          `${op?.predicate || ""}(${debugArgs(op?.args)})`,
          world?.world_type || "",
          op?.skip_reason || "",
        ])
      ),
      "No scoped-world operations recorded."
    );
    appendDebugClauseList(worldsLayer, "scoped wrapper clauses", worlds.clauses);
    body.appendChild(worldsLayer);
  }

  details.appendChild(summary);
  details.appendChild(body);
  card.appendChild(details);
  return card;
}

function collectSemanticWorkspaceBlocks(turnTrace) {
  const { semantic, ir, parse, admission } = semanticTrace(turnTrace);
  if (!ir) {
    return [];
  }
  const blocks = [];
  blocks.push({
    label: "Workspace decision",
    text: prettyJson({
      schema_version: ir.schema_version,
      decision: ir.decision,
      turn_type: ir.turn_type,
      clarification_questions: ir.clarification_questions || [],
      self_check: ir.self_check || {},
    }),
  });
  blocks.push({
    label: "Entities and referents",
    text: prettyJson({
      entities: ir.entities || [],
      referents: ir.referents || [],
    }),
  });
  blocks.push({
    label: "Assertions and unsafe implications",
    text: prettyJson({
      assertions: ir.assertions || [],
      unsafe_implications: ir.unsafe_implications || [],
    }),
  });
  blocks.push({
    label: "Candidate operations",
    text: prettyJson(ir.candidate_operations || []),
  });
  if (admission && Object.keys(admission).length) {
    blocks.push({
      label: "Deterministic admission gate",
      text: prettyJson(admission),
    });
  }
  if (parse?.admitted && typeof parse.admitted === "object") {
    blocks.push({
      label: "Runtime parse admitted to execution",
      text: prettyJson(parse.admitted),
    });
  } else if (parse?.normalized && typeof parse.normalized === "object") {
    blocks.push({
      label: "Runtime parse projected by mapper",
      text: prettyJson(parse.normalized),
    });
  }
  const rawMessage = String(semantic.raw_message || "").trim();
  if (rawMessage) {
    blocks.push({ label: "Raw structured model message", text: rawMessage });
  }
  return blocks;
}

function collectSegmentedStoryBlocks(turnTrace) {
  const segmented = turnTrace && typeof turnTrace.segmented_story === "object"
    ? turnTrace.segmented_story
    : null;
  if (!segmented) {
    return [];
  }
  const segments = Array.isArray(segmented.segments) ? segmented.segments : [];
  const compactSegments = segments.map((segment) => ({
    index: segment.index,
    status: segment.status,
    route: segment.route,
    decision: segment.decision,
    writes_applied: segment.writes_applied,
    admitted_count: segment.admitted_count,
    skipped_count: segment.skipped_count,
    held: Boolean(segment.clarification_question),
    utterance: segment.utterance,
    errors: segment.errors || [],
  }));
  return [
    {
      label: "Segmented story summary",
      text: prettyJson({
        strategy: segmented.strategy,
        segment_count: segmented.segment_count,
        writes_applied: segmented.writes_applied,
        admitted_count: segmented.admitted_count,
        skipped_count: segmented.skipped_count,
        held_count: segmented.held_count,
        error_count: segmented.error_count,
      }),
    },
    {
      label: "Segment outcomes",
      text: prettyJson(compactSegments),
    },
  ];
}

function findFirstMarkerIndex(text, markers) {
  let bestIndex = -1;
  for (const marker of markers) {
    const index = text.indexOf(marker);
    if (index >= 0 && (bestIndex < 0 || index < bestIndex)) {
      bestIndex = index;
    }
  }
  return bestIndex;
}

function splitPromptSections(promptText, kind, sharedPromptReference = "") {
  const trimmed = String(promptText || "").trim();
  if (!trimmed) {
    return { parts: [], sharedPromptText: "" };
  }

  const parts = [];
  let body = trimmed;
  if (body.startsWith("/no_think")) {
    parts.push({ label: "Mode directive", text: "/no_think" });
    body = body.slice("/no_think".length).replace(/^\s+/, "");
  }

  const utteranceMarkers =
    kind === "routing"
      ? ["\nUSER_UTTERANCE:\n", "\nUtterance:\n"]
      : kind === "freethinker"
        ? ["\nCURRENT_UTTERANCE:\n", "\nUtterance:\n", "\nUSER_UTTERANCE:\n"]
      : ["\nUtterance:\n", "\nUSER_UTTERANCE:\n"];
  let utterance = "";
  let promptBody = body;
  const utteranceMarkerIndex = findFirstMarkerIndex(body, utteranceMarkers);
  if (utteranceMarkerIndex >= 0) {
    const matchedMarker = utteranceMarkers.find(
      (marker) => body.indexOf(marker) === utteranceMarkerIndex
    );
    utterance = body.slice(utteranceMarkerIndex + matchedMarker.length).trim();
    promptBody = body.slice(0, utteranceMarkerIndex).trim();
  }

  const wrapperMarkers =
    kind === "parse"
      ? ["Route lock:", "Known ontology predicates:", "Return JSON only with exactly these keys:"]
      : kind === "freethinker"
        ? ["FREETHINKER_CONTEXT_JSON:"]
      : kind === "served"
        ? [
            "You are the served assistant behind a governed pre-think gateway.",
            "Follow these rules:",
            "GATEWAY_NOTE:",
            "DETERMINISTIC_SUMMARY_JSON:",
          ]
        : ["You are compiling a PRE-THINK routing packet.", "Return minified JSON only:"];

  let sharedPromptText = "";
  let taskWrapperText = promptBody;
  const guidancePrefix = "Additional guidance:\n";
  if (promptBody.startsWith(guidancePrefix)) {
    const guidanceBody = promptBody.slice(guidancePrefix.length);
    const wrapperIndex = findFirstMarkerIndex(guidanceBody, wrapperMarkers);
    if (wrapperIndex >= 0) {
      sharedPromptText = guidanceBody.slice(0, wrapperIndex).trim();
      taskWrapperText = guidanceBody.slice(wrapperIndex).trim();
    } else {
      sharedPromptText = guidanceBody.trim();
      taskWrapperText = "";
    }
  } else {
    const wrapperIndex = findFirstMarkerIndex(promptBody, wrapperMarkers);
    if (wrapperIndex > 0) {
      sharedPromptText = promptBody.slice(0, wrapperIndex).trim();
      taskWrapperText = promptBody.slice(wrapperIndex).trim();
    } else {
      taskWrapperText = promptBody.trim();
    }
  }

  if (sharedPromptText) {
    parts.push({
      label: "Shared system prompt",
      text:
        sharedPromptReference && sharedPromptText === sharedPromptReference
          ? "Same shared system prompt as Routing Prompt."
          : sharedPromptText,
    });
  }

  if (taskWrapperText) {
    parts.push({
        label:
          kind === "parse"
            ? "Parse wrapper / schema"
            : kind === "freethinker"
              ? "Freethinker wrapper / schema"
            : kind === "served"
              ? "Served handoff wrapper"
              : "Routing wrapper / schema",
      text: taskWrapperText,
    });
  }

  if (utterance) {
    parts.push({ label: "Utterance", text: utterance });
  }

  return { parts, sharedPromptText };
}

function collectModelContextBlocks(turn) {
  const turnTrace = turn && typeof turn.trace === "object" ? turn.trace : null;
  const blocks = [];
  const { semantic } = semanticTrace(turnTrace);
  const semanticModelInput = semantic && typeof semantic.model_input === "object" ? semantic.model_input : null;
  if (semanticModelInput) {
    blocks.push({
      label: "Semantic IR model input",
      text: prettyJson({
        model: semantic.model,
        backend: semantic.backend,
        base_url: semantic.base_url,
        latency_ms: semantic.latency_ms,
        input: semanticModelInput,
      }),
    });
  }
  let routingSharedPrompt = "";
  const prethinkPrimaryPrompt = String(
    ((((turnTrace || {}).prethink || {}).primary || {}).prompt_text || "")
  ).trim();
  if (prethinkPrimaryPrompt) {
    const decomposed = splitPromptSections(prethinkPrimaryPrompt, "routing");
    routingSharedPrompt = decomposed.sharedPromptText;
    blocks.push({ label: "Routing Prompt", parts: decomposed.parts });
  }

  const prethinkFallbackPrompt = String(
    ((((turnTrace || {}).prethink || {}).fallback || {}).prompt_text || "")
  ).trim();
  if (prethinkFallbackPrompt) {
    const decomposed = splitPromptSections(
      prethinkFallbackPrompt,
      "routing",
      routingSharedPrompt
    );
    blocks.push({ label: "Fallback Classifier Prompt", parts: decomposed.parts });
  }

  const parsePrompt = String(
    ((((turnTrace || {}).parse || {}).extractor || {}).prompt_text || "")
  ).trim();
  if (parsePrompt) {
    const decomposed = splitPromptSections(parsePrompt, "parse", routingSharedPrompt);
    blocks.push({ label: "Parse Prompt", parts: decomposed.parts });
  }

  const freethinkerPrompt = String(
    ((((turnTrace || {}).freethinker || {}).prompt_text) || "")
  ).trim();
  if (freethinkerPrompt) {
    blocks.push({
      label: "Freethinker Prompt",
      parts: splitPromptSections(freethinkerPrompt, "freethinker").parts,
    });
  }

  const servedPrompt = String(
    ((((turn || {}).assistant || {}).served_llm || {}).prompt_text || "")
  ).trim();
  if (servedPrompt) {
    blocks.push({
      label: "Served LLM Prompt",
      parts: splitPromptSections(servedPrompt, "served").parts,
    });
  }

  return blocks;
}

function collectCompilerJsonBlocks(turnTrace) {
  const blocks = [];
  const { ir, parse } = semanticTrace(turnTrace);
  if (ir && typeof ir === "object") {
    blocks.push({ label: "Semantic IR JSON", text: prettyJson(ir) });
  }
  if (parse?.normalized && typeof parse.normalized === "object") {
    blocks.push({ label: "Mapper Runtime JSON", text: prettyJson(parse.normalized) });
  }
  const routingJson = (((turnTrace || {}).prethink || {}).primary || {}).parsed;
  if (routingJson && typeof routingJson === "object") {
    blocks.push({ label: "Routing JSON", text: prettyJson(routingJson) });
  }

  const fallbackJson = (((turnTrace || {}).prethink || {}).fallback || {}).parsed;
  if (fallbackJson && typeof fallbackJson === "object") {
    blocks.push({ label: "Fallback Routing JSON", text: prettyJson(fallbackJson) });
  }

  const parseJson = (((turnTrace || {}).parse || {}).extractor || {}).parsed;
  if (parseJson && typeof parseJson === "object") {
    blocks.push({ label: "Parse JSON", text: prettyJson(parseJson) });
  }

  const freethinkerJson = ((turnTrace || {}).freethinker || {}).parsed;
  if (freethinkerJson && typeof freethinkerJson === "object") {
    blocks.push({ label: "Freethinker JSON", text: prettyJson(freethinkerJson) });
  }

  return blocks;
}

function shouldCollapseDebugText(text) {
  const normalized = String(text || "").trim();
  if (!normalized) {
    return false;
  }
  if (normalized.length > 420) {
    return true;
  }
  return normalized.split(/\r?\n/).length > 8;
}

function buildExpandableDebugText(text, { nested = false, label = "" } = {}) {
  const normalized = String(text || "").trim();
  if (!shouldCollapseDebugText(normalized)) {
    if (label) {
      const shell = document.createElement("section");
      shell.className = `debug-text-shell${nested ? " nested" : ""} has-label`;
      const heading = document.createElement("p");
      heading.className = "debug-inline-label";
      heading.textContent = label;
      const pre = document.createElement("pre");
      pre.className = "debug-text-scroller";
      pre.textContent = normalized;
      shell.appendChild(heading);
      shell.appendChild(pre);
      return shell;
    }
    const pre = document.createElement("pre");
    pre.textContent = normalized;
    return pre;
  }

  const lineCount = normalized.split(/\r?\n/).length;
  const shell = document.createElement("section");
  shell.className = `debug-text-shell${nested ? " nested" : ""}${label ? " has-label" : ""} is-collapsed`;

  const toggle = document.createElement("button");
  toggle.className = "debug-text-toggle";
  toggle.type = "button";
  toggle.setAttribute("aria-expanded", "false");
  const setToggleText = (expanded) => {
    if (!label) {
      toggle.textContent = expanded
        ? `Collapse JSON (${lineCount} lines)`
        : `Expand JSON (${lineCount} lines)`;
      return;
    }
    toggle.textContent = "";
    const labelSpan = document.createElement("span");
    labelSpan.className = "debug-text-label";
    labelSpan.textContent = label;
    const metaSpan = document.createElement("span");
    metaSpan.className = "debug-text-meta";
    metaSpan.textContent = expanded
      ? `Collapse (${lineCount} lines)`
      : `Expand (${lineCount} lines)`;
    toggle.appendChild(labelSpan);
    toggle.appendChild(metaSpan);
  };
  setToggleText(false);

  const pre = document.createElement("pre");
  pre.className = "debug-text-scroller";
  pre.textContent = normalized;

  toggle.addEventListener("click", () => {
    const expanded = shell.classList.toggle("is-expanded");
    shell.classList.toggle("is-collapsed", !expanded);
    toggle.setAttribute("aria-expanded", expanded ? "true" : "false");
    setToggleText(expanded);
  });

  shell.appendChild(toggle);
  shell.appendChild(pre);
  return shell;
}

function buildDebugBubble({ title, summary, blocks, variantClass }) {
  if (!Array.isArray(blocks) || !blocks.length) {
    return null;
  }
  const card = document.createElement("section");
  card.className = `phase-card debug-bubble-card ${variantClass}`.trim();

  const details = document.createElement("details");
  details.className = "phase-details debug-bubble-details";
  details.open = false;

  const bubbleSummary = document.createElement("summary");
  bubbleSummary.className = "phase-summary-row debug-bubble-summary";
  bubbleSummary.innerHTML = `
    <span class="phase-name">${escapeHtml(title)}</span>
    <span class="phase-status">${escapeHtml(summary)}</span>
  `;

  const body = document.createElement("div");
  body.className = "phase-body debug-bubble-body";
  for (const block of blocks) {
    const section = document.createElement("section");
    section.className = "debug-block";
    const isJsonBlock = String(variantClass || "").includes("debug-bubble-json");
    if (!isJsonBlock) {
      const heading = document.createElement("p");
      heading.className = "debug-block-label";
      heading.textContent = block.label;
      section.appendChild(heading);
    }
    if (Array.isArray(block.parts) && block.parts.length) {
      for (const part of block.parts) {
        const subSection = document.createElement("section");
        subSection.className = "debug-subblock";
        const subHeading = document.createElement("p");
        subHeading.className = "debug-subblock-label";
        subHeading.textContent = part.label;
        subSection.appendChild(subHeading);
        subSection.appendChild(
          buildExpandableDebugText(part.text, {
            nested: true,
          })
        );
        section.appendChild(subSection);
      }
    } else {
      section.appendChild(
        buildExpandableDebugText(block.text, {
          label: isJsonBlock ? block.label : "",
        })
      );
    }
    body.appendChild(section);
  }

  details.appendChild(bubbleSummary);
  details.appendChild(body);
  card.appendChild(details);
  return card;
}

function collectRawSemanticPayloadBlocks(turn, turnTrace) {
  const blocks = [];
  for (const block of collectSegmentedStoryBlocks(turnTrace)) {
    blocks.push({ ...block, label: `Story: ${block.label}` });
  }
  for (const block of collectModelContextBlocks(turn)) {
    blocks.push({ ...block, label: `Input: ${block.label}` });
  }
  for (const block of collectSemanticWorkspaceBlocks(turnTrace)) {
    blocks.push({ ...block, label: `Workspace: ${block.label}` });
  }
  for (const block of collectCompilerJsonBlocks(turnTrace)) {
    blocks.push({ ...block, label: `Runtime: ${block.label}` });
  }
  return blocks;
}

function appendGatewayTurn(turn) {
  const template = document.getElementById("message-template");
  const fragment = template.content.cloneNode(true);
  const article = fragment.querySelector(".message");
  const header = fragment.querySelector(".message-header");
  const body = fragment.querySelector(".message-body");
  article.classList.add("gateway-turn");

  const turnDetails = document.createElement("details");
  turnDetails.className = "turn-details";
  turnDetails.open = true;

  const turnSummary = document.createElement("summary");
  turnSummary.className = "turn-summary";
  const displayRoute = effectiveTurnRoute(turn);
  turnSummary.innerHTML = `
    <span class="turn-summary-title">${escapeHtml(`console turn ${turn.turn_index}`)}</span>
    <span class="turn-summary-route">${escapeHtml(`${displayRoute} route`)}</span>
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
  const outcome = outcomeSummary(turn);
  const outcomeEl = document.createElement("section");
  outcomeEl.className = `turn-outcome tone-${outcome.tone}`;
  const outcomeBadge = document.createElement("span");
  outcomeBadge.className = `outcome-badge tone-${outcome.tone}`;
  outcomeBadge.textContent = outcome.badge;
  const outcomeTitle = document.createElement("p");
  outcomeTitle.className = "turn-outcome-title";
  outcomeTitle.textContent = outcome.title;
  outcomeEl.appendChild(outcomeBadge);
  outcomeEl.appendChild(outcomeTitle);
  if (Array.isArray(outcome.points) && outcome.points.length) {
    const outcomeList = document.createElement("ul");
    outcomeList.className = "turn-outcome-points";
    for (const point of outcome.points) {
      const item = document.createElement("li");
      item.textContent = point;
      outcomeList.appendChild(item);
    }
    outcomeEl.appendChild(outcomeList);
  }
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
    ["Compiler note", internals.note],
    ["Clarification", internals.clarification],
  ];
  if (String(internals.compilerPath || "").trim()) {
    internalsRows.push(["Compiler path", internals.compilerPath]);
  }
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
  chatShell.appendChild(outcomeEl);
  if (operationListEl) {
    chatShell.appendChild(operationListEl);
  }
  body.appendChild(chatShell);
  const debugStack = document.createElement("div");
  debugStack.className = "debug-stack";
  debugStack.appendChild(internalsEl);

  const turnTrace = turn && typeof turn.trace === "object" ? turn.trace : null;
  const pipelineTraceBubble = buildPipelineTraceBubble(turn);
  if (pipelineTraceBubble) {
    debugStack.appendChild(pipelineTraceBubble);
  }
  if (hasSemanticTrace(turnTrace) || pipelineTraceBubble) {
    const rawSemanticBubble = buildDebugBubble({
      title: "raw semantic payloads",
      summary: "model input, workspace JSON, mapper JSON",
      blocks: collectRawSemanticPayloadBlocks(turn, turnTrace),
      variantClass: "debug-bubble-json",
    });
    if (rawSemanticBubble) {
      debugStack.appendChild(rawSemanticBubble);
    }
  } else {
    const segmentedBubble = buildDebugBubble({
      title: "story segments",
      summary: "long narrative ingestion",
      blocks: collectSegmentedStoryBlocks(turnTrace),
      variantClass: "debug-bubble-semantic",
    });
    if (segmentedBubble) {
      debugStack.appendChild(segmentedBubble);
    }
    const semanticBubble = buildDebugBubble({
      title: "semantic workspace",
      summary: semanticTraceSummary(turnTrace) || "semantic_ir_v1 proposal",
      blocks: collectSemanticWorkspaceBlocks(turnTrace),
      variantClass: "debug-bubble-semantic",
    });
    if (semanticBubble) {
      debugStack.appendChild(semanticBubble);
    }
    const modelContextBubble = buildDebugBubble({
      title: "model input",
      summary: "what the compiler saw",
      blocks: collectModelContextBlocks(turn),
      variantClass: "debug-bubble-context",
    });
    if (modelContextBubble) {
      debugStack.appendChild(modelContextBubble);
    }
    const compilerJsonBubble = buildDebugBubble({
      title: "compiler json",
      summary: "raw model output",
      blocks: collectCompilerJsonBlocks(turnTrace),
      variantClass: "debug-bubble-json",
    });
    if (compilerJsonBubble) {
      debugStack.appendChild(compilerJsonBubble);
    }
  }
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
    const traceSummaryText = document.createElement("p");
    traceSummaryText.className = "phase-summary";
    traceSummaryText.textContent = String(
      (turnTrace.summary && turnTrace.summary.overall) || "Compiler trace captured."
    );
    traceBody.appendChild(traceSummaryText);
    traceBody.appendChild(buildExpandableDebugText(JSON.stringify(turnTrace, null, 2)));

    traceDetails.appendChild(traceSummary);
    traceDetails.appendChild(traceBody);
    traceCard.appendChild(traceDetails);
    debugStack.appendChild(traceCard);
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
    const phaseSummaryText = document.createElement("p");
    phaseSummaryText.className = "phase-summary";
    phaseSummaryText.textContent = phase.summary;
    phaseBody.appendChild(phaseSummaryText);
    phaseBody.appendChild(buildExpandableDebugText(JSON.stringify(phase.data, null, 2)));

    phaseDetails.appendChild(phaseSummary);
    phaseDetails.appendChild(phaseBody);
    card.appendChild(phaseDetails);
    debugStack.appendChild(card);
  }

  turnContent.appendChild(body);
  turnContent.appendChild(debugStack);
  turnDetails.appendChild(turnSummary);
  turnDetails.appendChild(turnContent);
  article.innerHTML = "";
  article.appendChild(turnDetails);

  const chatLog = document.getElementById("chat-log");
  chatLog.appendChild(article);
  chatLog.scrollTop = chatLog.scrollHeight;
  updateEmptyState();
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

function setComposerBusy(isBusy) {
  state.turnInFlight = Boolean(isBusy);
  const form = document.getElementById("chat-form");
  const button = document.getElementById("send-button");
  const label = button?.querySelector(".send-button-label");
  if (form) {
    form.classList.toggle("is-processing", state.turnInFlight);
  }
  if (button) {
    button.disabled = state.turnInFlight;
    button.setAttribute("aria-busy", state.turnInFlight ? "true" : "false");
    button.setAttribute(
      "aria-label",
      state.turnInFlight ? "Prethinker is processing this turn" : "Open front door"
    );
  }
  if (label) {
    label.textContent = state.turnInFlight ? "Compiling Turn" : "Open Front Door";
  }
}

async function loadConfig() {
  const payload = await getJson("/api/config");
  state.config = payload.config;
  fillConfigForm(state.config);
  renderLedger();
}

async function submitUtterance(event) {
  event.preventDefault();
  if (state.turnInFlight) {
    return;
  }
  const field = document.getElementById("utterance");
  const utterance = field.value.trim();
  if (!utterance) {
    return;
  }
  collapseChatExpandos();
  appendUserMessage(utterance);
  field.value = "";
  setComposerBusy(true);

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
    state.pendingClarification = payload.pending_clarification || null;
    state.turns.push(payload.turn);
    appendGatewayTurn(payload.turn);
    renderLedger();
    updatePendingBanner();
    syncConnectionPill("Connected", "success");
  } catch (error) {
    state.pendingClarification = null;
    updatePendingBanner();
    syncConnectionPill("Offline", "danger");
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
    renderLedger();
  }
  finally {
    setComposerBusy(false);
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
    "semantic_ir_context_length",
    "semantic_ir_timeout",
    "semantic_ir_temperature",
    "semantic_ir_top_p",
    "semantic_ir_top_k",
    "freethinker_context_length",
    "freethinker_timeout",
    "freethinker_temperature",
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
  payload.semantic_ir_enabled = form.elements.namedItem("semantic_ir_enabled").checked;
  payload.semantic_ir_thinking = form.elements.namedItem("semantic_ir_thinking").checked;
  payload.freethinker_thinking = form.elements.namedItem("freethinker_thinking").checked;

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
    compiler_backend: SEMANTIC_IR_PRIMARY.backend,
    compiler_base_url: SEMANTIC_IR_PRIMARY.baseUrl,
    compiler_model: SEMANTIC_IR_PRIMARY.model,
    compiler_context_length: SEMANTIC_IR_PRIMARY.contextLength,
    compiler_timeout: SEMANTIC_IR_PRIMARY.timeout,
    semantic_ir_enabled: true,
    semantic_ir_model: SEMANTIC_IR_PRIMARY.model,
    semantic_ir_context_length: SEMANTIC_IR_PRIMARY.contextLength,
    semantic_ir_timeout: SEMANTIC_IR_PRIMARY.timeout,
    semantic_ir_temperature: SEMANTIC_IR_PRIMARY.temperature,
    semantic_ir_top_p: SEMANTIC_IR_PRIMARY.topP,
    semantic_ir_top_k: SEMANTIC_IR_PRIMARY.topK,
    semantic_ir_thinking: SEMANTIC_IR_PRIMARY.thinking,
    served_handoff_mode: "never",
    require_final_confirmation: true,
    clarification_eagerness: Math.max(0.75, Number(baseConfig?.clarification_eagerness || 0)),
  };
}

function servedChatPayload(baseConfig) {
  return {
    ...baseConfig,
    strict_mode: false,
    served_handoff_mode: "always",
    compiler_mode: "auto",
  };
}

function freethinkerAdvisoryPayload(baseConfig) {
  return {
    ...baseConfig,
    freethinker_resolution_policy: "advisory_only",
    freethinker_temperature: Number(baseConfig?.freethinker_temperature ?? 0.2) || 0.2,
    freethinker_thinking: Boolean(baseConfig?.freethinker_thinking),
    freethinker_model: String(baseConfig?.freethinker_model || SEMANTIC_IR_PRIMARY.model),
    freethinker_backend: String(baseConfig?.freethinker_backend || SEMANTIC_IR_PRIMARY.backend),
    freethinker_base_url: String(baseConfig?.freethinker_base_url || SEMANTIC_IR_PRIMARY.baseUrl),
    freethinker_context_length: Number(baseConfig?.freethinker_context_length || 16384),
    freethinker_timeout: Number(baseConfig?.freethinker_timeout || 60),
    freethinker_prompt_file: String(
      baseConfig?.freethinker_prompt_file || "modelfiles/freethinker_system_prompt.md"
    ),
  };
}

function medicalProfilePayload(baseConfig) {
  return {
    ...baseConfig,
    active_profile: "medical@v0",
    reply_surface_policy: "deterministic_template",
    strict_mode: true,
    compiler_mode: "strict",
    compiler_backend: SEMANTIC_IR_PRIMARY.backend,
    compiler_base_url: SEMANTIC_IR_PRIMARY.baseUrl,
    compiler_model: SEMANTIC_IR_PRIMARY.model,
    compiler_context_length: SEMANTIC_IR_PRIMARY.contextLength,
    compiler_timeout: SEMANTIC_IR_PRIMARY.timeout,
    semantic_ir_enabled: true,
    semantic_ir_model: SEMANTIC_IR_PRIMARY.model,
    semantic_ir_context_length: SEMANTIC_IR_PRIMARY.contextLength,
    semantic_ir_timeout: SEMANTIC_IR_PRIMARY.timeout,
    semantic_ir_temperature: SEMANTIC_IR_PRIMARY.temperature,
    semantic_ir_top_p: SEMANTIC_IR_PRIMARY.topP,
    semantic_ir_top_k: SEMANTIC_IR_PRIMARY.topK,
    semantic_ir_thinking: SEMANTIC_IR_PRIMARY.thinking,
    served_handoff_mode: "never",
    require_final_confirmation: true,
    clarification_eagerness: Math.max(0.8, Number(baseConfig?.clarification_eagerness || 0)),
    freethinker_resolution_policy: "off",
    freethinker_temperature: Number(baseConfig?.freethinker_temperature ?? 0.2) || 0.2,
    freethinker_thinking: Boolean(baseConfig?.freethinker_thinking),
    freethinker_model: String(baseConfig?.freethinker_model || SEMANTIC_IR_PRIMARY.model),
    freethinker_backend: String(baseConfig?.freethinker_backend || SEMANTIC_IR_PRIMARY.backend),
    freethinker_base_url: String(baseConfig?.freethinker_base_url || SEMANTIC_IR_PRIMARY.baseUrl),
    freethinker_context_length: Number(baseConfig?.freethinker_context_length || 16384),
    freethinker_timeout: Number(baseConfig?.freethinker_timeout || 60),
    freethinker_prompt_file: String(
      baseConfig?.freethinker_prompt_file || "modelfiles/freethinker_system_prompt.md"
    ),
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

async function applyServedChatPreference() {
  try {
    const payload = servedChatPayload(state.config || {});
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
      "Served chat preference applied (strict off, served handoff always, compiler auto).";
  } catch (error) {
    document.getElementById("config-status").textContent = `Served chat preset failed: ${String(error)}`;
  }
}

async function applyFreethinkerAdvisory() {
  try {
    const payload = freethinkerAdvisoryPayload(state.config || {});
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
      "Experimental sidecar enabled. Use only as a controlled sidecar-on comparison.";
  } catch (error) {
    document.getElementById("config-status").textContent = `Freethinker preset failed: ${String(error)}`;
  }
}

async function applyMedicalProfilePreset() {
  try {
    const payload = medicalProfilePayload(state.config || {});
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
      "medical@v0 applied (strict compiler, medical prompt profile, sidecar off).";
  } catch (error) {
    document.getElementById("config-status").textContent = `medical@v0 preset failed: ${String(error)}`;
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
    state.turns = [];
    state.pendingClarification = null;
    document.getElementById("chat-log").innerHTML = "";
    updatePendingBanner();
    updateEmptyState();
    renderLedger();
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

function setDebugMode(enabled) {
  state.debugMode = Boolean(enabled);
  document.body.classList.toggle("debug-mode", state.debugMode);
  const toggle = document.getElementById("debug-mode-toggle");
  if (toggle) {
    toggle.checked = state.debugMode;
  }
  try {
    localStorage.setItem(DEBUG_MODE_KEY, state.debugMode ? "1" : "0");
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
  const form = document.getElementById("config-form");
  const strictModeField = form?.elements?.namedItem("strict_mode");
  if (strictModeField) {
    strictModeField.addEventListener("change", () => {
      updateConfigFormAffordances({ strict_mode: strictModeField.checked });
    });
  }

  document.addEventListener("click", (event) => {
    if (!state.configOpen) {
      return;
    }
    const drawer = document.getElementById("config-drawer");
    const toggleButton = document.getElementById("config-toggle");
    const target = event.target;
    if (!(target instanceof Node)) {
      return;
    }
    if (drawer?.contains(target) || toggleButton?.contains(target)) {
      return;
    }
    setConfigOpen(false);
  });
}

function initDebugMode() {
  let initiallyEnabled = false;
  try {
    initiallyEnabled = localStorage.getItem(DEBUG_MODE_KEY) === "1";
  } catch (_error) {
    initiallyEnabled = false;
  }
  setDebugMode(initiallyEnabled);
  const toggle = document.getElementById("debug-mode-toggle");
  if (toggle) {
    toggle.addEventListener("change", (event) => {
      setDebugMode(Boolean(event.target.checked));
    });
  }
}

function initExampleChips() {
  const field = document.getElementById("utterance");
  document.querySelectorAll(".example-chip").forEach((button) => {
    button.addEventListener("click", () => {
      if (!field) {
        return;
      }
      field.value = String(button.dataset.example || "").trim();
      field.focus();
    });
  });
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
  initDebugMode();
  initExampleChips();
  initComposerKeyboardSubmit();
  document.getElementById("chat-form").addEventListener("submit", submitUtterance);
  document.getElementById("config-form").addEventListener("submit", saveConfig);
  document.getElementById("reset-button").addEventListener("click", resetSession);
  document.getElementById("export-button").addEventListener("click", exportSession);
  document.getElementById("strict-lock-button").addEventListener("click", applyStrictBouncerLock);
  document.getElementById("freethinker-advisory-button").addEventListener("click", applyFreethinkerAdvisory);
  document.getElementById("medical-profile-button").addEventListener("click", applyMedicalProfilePreset);
  document.getElementById("served-chat-button").addEventListener("click", applyServedChatPreference);
  try {
    await loadConfig();
    updatePendingBanner();
    updateEmptyState();
    renderLedger();
    syncConnectionPill("Connected", "success");
    document.getElementById("config-status").textContent =
      API_BASE ? `Connected to Prethinker Console at ${API_BASE}.` : "Connected to same-origin Prethinker Console.";
  } catch (error) {
    updatePendingBanner();
    updateEmptyState();
    renderLedger();
    syncConnectionPill("Offline", "danger");
    document.getElementById("config-status").textContent =
      `Could not load config from ${apiUrl("/api/config")}. ` +
      "Run `python ui_gateway/main.py` to enable Prethinker Console.";
  }
});
