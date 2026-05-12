import { joinUiPathSegments, uiPathSeparator, withTrailingUiSeparator } from "../utils/path_format.js";

export function createOutputSections({ state, esc, controls, icons, iconMarkup, promptPreviewMarkup }) {
  const { field, selectControl } = controls;
  const LINE_BANK_ROOT = withTrailingUiSeparator(joinUiPathSegments(["backend", "engine", "data", "overrides", "line_banks"]));

  function renderCollapsibleSection({ title, badge = "", body = "", defaultOpen = false, extraClass = "" }) {
    const classes = ["section", "collapsible-section", extraClass].filter(Boolean).join(" ");
    return `
      <details class="${classes}" ${defaultOpen ? "open" : ""}>
        <summary class="section-summary">
          <span class="section-summary-title">${esc(title)}</span>
          <span class="section-summary-side">
            ${badge ? `<span class="pill">${esc(badge)}</span>` : ""}
            <span class="section-summary-caret" aria-hidden="true">⌄</span>
          </span>
        </summary>
        <div class="collapsible-content">
          ${body}
        </div>
      </details>
    `;
  }

  function lineBankBucketInfo(spicyLevel) {
    if (spicyLevel === "random") {
      return {
        badgeLabel: "3 spicy files",
        fileLabel: "1_3.md / 4_5.md / 6_8.md",
        hint: "Random spicy can pull from more than one spicy file.",
      };
    }
    const numeric = Number(spicyLevel);
    if (Number.isNaN(numeric) || numeric <= 3) {
      return { badgeLabel: "1_3.md", fileLabel: "1_3.md", hint: `Spicy ${esc(spicyLevel)} uses ${esc("1_3.md")}.` };
    }
    if (numeric <= 5) {
      return { badgeLabel: "4_5.md", fileLabel: "4_5.md", hint: `Spicy ${esc(spicyLevel)} uses ${esc("4_5.md")}.` };
    }
    return { badgeLabel: "6_8.md", fileLabel: "6_8.md", hint: `Spicy ${esc(spicyLevel)} uses ${esc("6_8.md")}.` };
  }

  function renderLineBankStructure(mode, fileLabel, hint) {
    if (mode !== "women" && mode !== "men") {
      return `
        <ul class="line-bank-list">
          <li>Couples do not use line-banks yet.</li>
          <li>Use women or men mode if you want these files to affect output.</li>
        </ul>
      `;
    }
    return `
      <ul class="line-bank-list">
        <li><strong>${esc(withTrailingUiSeparator(mode))}</strong> picks the gender folder.</li>
        <li><strong>${esc(withTrailingUiSeparator("poses"))}</strong>, <strong>${esc(withTrailingUiSeparator("outfits"))}</strong>, or <strong>${esc(withTrailingUiSeparator("expressions"))}</strong> picks what you are editing.</li>
        <li><strong>${esc(fileLabel)}</strong> picks the spicy file. ${hint}</li>
      </ul>
    `;
  }

  function renderPresetSection() {
    return `
      <section class="section">
        <div class="section-head"><div><h2>Preset</h2></div></div>
        <div class="field-grid">
          ${field({ label: "Preset name", span2: true, input: `<input class="input" name="presetName" value="${esc(state.presetName)}" placeholder="Women / soft luxury" />` })}
        </div>
        <div class="toolbar" style="margin-top:14px;">
          <button type="button" class="ghost-button" data-action="save-preset">Save current preset</button>
        </div>
      </section>
    `;
  }

  function renderDebugSection() {
    return renderCollapsibleSection({
      title: "Debug",
      badge: state.form.debugMode ? "On" : "Off",
      body: `
        <div class="field-grid">
          ${field({
            label: "Debug mode",
            span2: true,
            input: selectControl("debugMode", [{ value: "false", label: "Off" }, { value: "true", label: "On" }], state.form.debugMode ? "true" : "false"),
          })}
        </div>
      `,
    });
  }

  function renderLineBankHelpSection() {
    const mode = state.form.mode;
    const bucket = lineBankBucketInfo(state.form.spicyLevel);
    const sep = uiPathSeparator();
    return renderCollapsibleSection({
      title: "Line-banks",
      badge: bucket.badgeLabel,
      extraClass: "line-bank-section",
      body: `
        <div class="section-head section-head-tight">
          <div>
            <p>Edit prompt lines here without touching the JSON banks.</p>
          </div>
          <div class="inline-actions">
            <button type="button" class="ghost-button" data-action="copy-inline-value" data-value="${esc(LINE_BANK_ROOT)}">Copy path</button>
          </div>
        </div>
        <div class="sub-block">
          <div class="sub-block-head">
            <h3>Root folder</h3>
            <p>Open this folder in VS Code.</p>
          </div>
          <div class="status-line line-bank-path">${esc(LINE_BANK_ROOT)}</div>
          <p class="small-note">Starter files can stay as comments.</p>
        </div>
        <div class="sub-block">
          <div class="sub-block-head">
            <h3>How to pick a file</h3>
            <p>${mode === "couples" ? "This only applies to women and men mode." : `Use three parts: gender ${sep} category ${sep} spicy file.`}</p>
          </div>
          ${renderLineBankStructure(mode, bucket.fileLabel, bucket.hint)}
        </div>
        <div class="sub-block">
          <div class="sub-block-head">
            <h3>How it works</h3>
          </div>
          <ul class="line-bank-list">
            <li>One non-comment line equals one item.</li>
            <li>Lines that start with <strong>#</strong> are safe comments.</li>
            <li>Keep one idea per line.</li>
          </ul>
        </div>
      `,
    });
  }

  function renderActionDock() {
    return `
      <div class="action-dock-wrap">
        <div class="action-dock-fade"></div>
        <section class="action-dock panel">
          <div class="toolbar action-dock-toolbar">
            <button type="button" class="ghost-button reset-button" data-action="reset-form" aria-label="Reset form" title="Reset form"></button>
            <label class="dock-qty-field" for="dock-batch-size">
              <span class="dock-qty-label">Qty</span>
              <input id="dock-batch-size" class="input dock-qty-input" type="number" min="1" max="100" name="batchSize" value="${esc(state.form.batchSize)}" />
            </label>
            <button type="button" class="primary-button generate-button" data-action="generate" ${state.loading ? "disabled" : ""}>${iconMarkup(icons.magic, "button-icon")}<span>${state.loading ? "Working..." : "Generate"}</span></button>
          </div>
          ${state.error ? `<div class="message action-dock-message">${esc(state.error)}</div>` : ""}
        </section>
      </div>
    `;
  }

  function renderTopbar() {
    return `
      <header class="topbar">
        <div class="title-wrap">
          <h1>Native Structure Prompts Generator</h1>
          <p>Build AI photoshoot prompts fast, with control, in batches.</p>
        </div>
      </header>
    `;
  }

  function renderDebugPanel() {
    if (!state.form.debugMode || !state.lastRun?.debug) return "";
    const debug = state.lastRun.debug;
    const list = (obj) => Object.entries(obj || {}).map(([key, value]) => `<li>${esc(key)}: ${esc(value)}</li>`).join("");
    const signalList = (signals, className) =>
      Array.isArray(signals) && signals.length
        ? `<div class="debug-signal-row ${className}">${signals.map((signal) => `<span class="debug-signal ${className}">${esc(signal)}</span>`).join("")}</div>`
        : "";
    const decisionCard = (item) => `
      <div class="debug-decision">
        <div class="debug-decision-head">
          <strong>Prompt ${esc(item.index)}</strong>
          ${item.route ? `<span>${esc(item.route)}</span>` : ""}
        </div>
        <div class="debug-decision-meta">
          ${item.photoTreatment ? `<span><strong>treatment:</strong> ${esc(item.photoTreatment)}</span>` : ""}
          ${item.photoTreatmentCategory ? `<span><strong>category:</strong> ${esc(item.photoTreatmentCategory)}</span>` : ""}
          ${item.captureRender ? `<span><strong>render:</strong> ${esc(item.captureRender)}</span>` : ""}
        </div>
        ${signalList(item.styleSignals?.matched, "is-good")}
        ${signalList(item.treatmentSignals?.matched, "is-good")}
        ${signalList(item.styleSignals?.misses, "is-warn")}
        ${signalList(item.treatmentSignals?.misses, "is-warn")}
        <ul>
          ${item.sceneFamily ? `<li>scene: ${esc(item.sceneFamily)}</li>` : ""}
          ${item.setting ? `<li>setting: ${esc(item.setting)}</li>` : ""}
          ${item.outfit ? `<li>female outfit: ${esc(item.outfit)}</li>` : ""}
          ${item.material ? `<li>material: ${esc(item.material)}</li>` : ""}
          ${item.color ? `<li>color: ${esc(item.color)}</li>` : ""}
          ${item.pose ? `<li>female pose: ${esc(item.pose)}</li>` : ""}
          ${item.hand ? `<li>hand: ${esc(item.hand)}</li>` : ""}
          ${item.framing ? `<li>framing: ${esc(item.framing)}</li>` : ""}
          ${item.lighting ? `<li>lighting: ${esc(item.lighting)}</li>` : ""}
          ${item.time ? `<li>time: ${esc(item.time)}</li>` : ""}
          ${item.mood ? `<li>mood: ${esc(item.mood)}</li>` : ""}
          ${item.hair ? `<li>female hair: ${esc(item.hair)}</li>` : ""}
          ${item.hairColor ? `<li>female hair color: ${esc(item.hairColor)}</li>` : ""}
          ${item.makeup ? `<li>female makeup: ${esc(item.makeup)}</li>` : ""}
          ${item.maleOutfit ? `<li>male outfit: ${esc(item.maleOutfit)}</li>` : ""}
          ${item.maleOutfitVibe ? `<li>male outfit vibe: ${esc(item.maleOutfitVibe)}</li>` : ""}
          ${item.malePose ? `<li>male pose: ${esc(item.malePose)}</li>` : ""}
          ${item.maleHair ? `<li>male hair: ${esc(item.maleHair)}</li>` : ""}
          ${item.maleGrooming ? `<li>male grooming: ${esc(item.maleGrooming)}</li>` : ""}
          ${item.maleAppearanceMode ? `<li>male appearance mode: ${esc(item.maleAppearanceMode)}</li>` : ""}
          ${item.capture ? `<li>capture: ${esc(item.capture)}</li>` : ""}
          ${item.cameraVibe ? `<li>camera vibe: ${esc(item.cameraVibe)}</li>` : ""}
          ${item.colorGrade ? `<li>color grade: ${esc(item.colorGrade)}</li>` : ""}
          ${item.finish ? `<li>finish: ${esc(item.finish)}</li>` : ""}
          ${item.findingsCount !== undefined ? `<li>findings: ${esc(item.findingsCount)}</li>` : ""}
          ${item.repairApplied !== undefined ? `<li>repair: ${item.repairApplied ? "yes" : "no"}</li>` : ""}
        </ul>
      </div>
    `;
    return `
      <div class="debug-grid">
        <div class="debug-card"><h3>Run</h3><ul><li>batch: ${esc(debug.batchSize)}</li><li>identity lock: ${debug.identityLock ? "on" : "off"}</li><li>effective spicy: ${esc(debug.effectiveSpicyLevel)}</li><li>style mode: ${esc(debug.effectiveStyleMode ?? state.form.styleMode)}</li><li>photo type: ${esc(debug.effectivePhotoType ?? state.form.photoTypeControl ?? "balanced")}</li><li>location strategy: ${esc(debug.effectiveLocationStrategy ?? state.form.locationStrategy)}</li><li>anti-repeat: ${esc(debug.effectiveAntiRepeat ?? state.form.antiRepeat)}</li><li>scene focus: ${esc(debug.effectiveSceneFocus ?? state.form.sceneFocus)}</li>${debug.effectiveWomenSceneFamily && debug.effectiveWomenSceneFamily !== "off" ? `<li>women scene family: ${esc(debug.effectiveWomenSceneFamily)}</li>` : ""}<li>outfit reveal: ${esc(debug.effectiveOutfitReveal ?? state.form.outfitReveal)}</li><li>makeup: ${esc(debug.effectiveMakeup ?? state.form.makeupControl)}</li><li>stylized: ${esc(debug.stylizedCount ?? 0)}</li><li>polished: ${esc(debug.polishedCount ?? 0)}</li><li>unique treatments: ${esc(debug.uniquePhotoTreatments ?? 0)}</li><li>repairs: ${esc(debug.repairAppliedCount)}</li><li>validation findings: ${esc(debug.validationFindingCount)}</li></ul></div>
        <div class="debug-card"><h3>Stylization</h3><ul>${list(debug.photoTreatmentCategoryDistribution)}</ul></div>
        <div class="debug-card"><h3>Photo type mix</h3><ul>${list(debug.photoTreatmentMixBucketDistribution)}</ul></div>
        <div class="debug-card"><h3>Treatment quality</h3><ul>${list(debug.photoTreatmentQualityTierDistribution)}</ul></div>
        <div class="debug-card"><h3>Treatment tone</h3><ul>${list(debug.photoTreatmentToneDistribution)}</ul></div>
        <div class="debug-card"><h3>Photo treatment</h3><ul>${list(debug.photoTreatmentDistribution)}</ul></div>
        <div class="debug-card"><h3>Capture</h3><ul>${list(debug.captureDistribution)}</ul></div>
        <div class="debug-card"><h3>Lighting</h3><ul>${list(debug.lightingDistribution)}</ul></div>
        <div class="debug-card"><h3>Camera vibe</h3><ul>${list(debug.cameraVibeDistribution)}</ul></div>
        <div class="debug-card"><h3>Appearance</h3><ul><li>woman mode: ${esc(debug.femaleAppearanceMode ?? "off")}</li>${debug.femaleAppearancePrompt ? `<li>woman prompt: ${esc(debug.femaleAppearancePrompt)}</li>` : ""}<li>man mode: ${esc(debug.maleAppearanceMode ?? "off")}</li>${debug.maleAppearancePrompt ? `<li>man prompt: ${esc(debug.maleAppearancePrompt)}</li>` : ""}</ul></div>
        <div class="debug-card"><h3>Scene family</h3><ul>${list(debug.sceneFamilyDistribution)}</ul></div>
        <div class="debug-card"><h3>Framing</h3><ul>${list(debug.framingDistribution)}</ul></div>
        <div class="debug-card"><h3>Pose</h3><ul>${list(debug.poseDistribution)}</ul></div>
        ${Array.isArray(debug.promptDecisions) && debug.promptDecisions.length ? `<div class="debug-card full"><h3>Per prompt decisions</h3><div class="debug-decision-list">${debug.promptDecisions.map((item) => decisionCard(item)).join("")}</div></div>` : ""}
      </div>
    `;
  }

  function renderLatestPrompts() {
    if (!state.lastRun) return `<div class="empty">Run a batch and the latest prompts will show up here, one per line.</div>`;
    return `
      <section class="section">
        <div class="section-head"><div><h2>Latest batch</h2></div><div class="inline-actions"><span class="pill">${esc(state.lastRun.prompts.length)} prompts</span><button type="button" class="ghost-button" data-action="copy-all">Copy batch</button></div></div>
        <div class="preview-list">
          ${state.lastRun.prompts.map((item, index) => `<div class="preview-line"><div class="prompt-head"><strong>Prompt ${index + 1}</strong><button type="button" class="history-button copy-button icon-copy-container" title="Copy prompt" aria-label="Copy prompt" data-action="copy-prompt" data-index="${index}">${iconMarkup(icons.copy, "button-icon copy-icon")}</button></div>${promptPreviewMarkup(item)}</div>`).join("")}
        </div>
      </section>
    `;
  }

  function renderPresets() {
    if (!state.presets.length) return `<div class="empty">No saved presets yet.</div>`;
    return `
      <section class="section">
        <div class="section-head"><div><h2>Saved presets</h2></div></div>
        <div class="preset-list">
          ${state.presets.map((item) => `<div class="preset-item"><div class="preset-top"><div><p class="list-headline">${esc(item.name)}</p><div class="preset-meta">${esc(item.formState.mode)} | batch ${esc(item.formState.batchSize)}</div></div><div class="inline-actions"><button type="button" class="history-button" data-action="load-preset" data-id="${esc(item.id)}">Use</button><button type="button" class="history-button" data-action="delete-preset" data-id="${esc(item.id)}">Delete</button></div></div></div>`).join("")}
        </div>
      </section>
    `;
  }

  function renderHistory() {
    if (!state.history.length) return `<div class="empty">No history yet.</div>`;
    return renderCollapsibleSection({
      title: "History",
      badge: `${state.history.length} runs`,
      body: `
        <div class="history-list">
          ${state.history.map((item) => `<div class="history-item"><div class="history-top"><div><p class="list-headline">${esc(item.timestamp)}</p><div class="history-meta">${esc(item.formState.mode)} | batch ${esc(item.formState.batchSize)}</div></div><div class="inline-actions"><button type="button" class="history-button copy-button icon-copy-container" title="Copy prompt" aria-label="Copy prompt" data-action="copy-history" data-id="${esc(item.id)}">${iconMarkup(icons.copy, "button-icon copy-icon")}</button></div></div><div class="small-note preview-snippet">${esc((item.outputText || "").split("\n")[0])}</div></div>`).join("")}
        </div>
      `,
      extraClass: "history-section",
    });
  }

  function renderOutputPanel() {
    return `<div class="output-column sticky-output">${renderLatestPrompts()}${renderDebugPanel()}${renderPresets()}${renderHistory()}</div>`;
  }

  return {
    renderPresetSection,
    renderDebugSection,
    renderLineBankHelpSection,
    renderActionDock,
    renderTopbar,
    renderDebugPanel,
    renderLatestPrompts,
    renderPresets,
    renderHistory,
    renderOutputPanel,
  };
}
