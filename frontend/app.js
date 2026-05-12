import { deletePresetRequest, generateRun, loadBootstrap, savePresetRequest } from "./api/client.js";
import { clone, state } from "./state/store.js";
import { ICONS, iconMarkup } from "./components/icons.js";
import { createControls } from "./components/controls.js";
import { createCardRenderers } from "./components/cards.js";
import { createSubjectSections } from "./sections/subject.js";
import { createSceneSections } from "./sections/scene.js";
import { createOutputSections } from "./sections/output.js";
import { createFormController } from "./controllers/form_controller.js";

const app = document.getElementById("app");
const RERENDER_FIELDS = new Set([
  "personMode",
  "racePreset",
  "maleRacePreset",
  "hairstyle",
  "maleHairstyle",
  "hairColorControl",
  "outfitVibeControl",
  "beautyFinishControl",
  "styleMode",
  "locationStrategy",
  "debugMode",
  "appearanceMode",
  "maleAppearanceMode",
  "photoTypeControl",
  "photoTreatmentControl",
]);
const spicyOrder = ["random", "3", "4", "5", "6", "7", "8"];
const photoTypeOrder = ["balanced", "glossy", "studio", "stylized", "amateur", "custom"];

const esc = (value) =>
  String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");

const controls = createControls({ state, esc });
const { promptPreviewMarkup } = createCardRenderers({ esc });
const controller = createFormController({
  state,
  clone,
  generateRun,
  savePresetRequest,
  deletePresetRequest,
});
const subjectSections = createSubjectSections({ state, esc, controls, icons: ICONS, iconMarkup });
const sceneSections = createSceneSections({ state, esc, controls, icons: ICONS, iconMarkup });
const outputSections = createOutputSections({
  state,
  esc,
  controls,
  icons: ICONS,
  iconMarkup,
  promptPreviewMarkup,
});

function syncActionDockGeometry() {
  const root = document.documentElement;
  const sidebar = document.querySelector(".controls");
  const controlsRoot = document.querySelector(".controls-inner");
  if (!sidebar || !controlsRoot) {
    root.style.removeProperty("--dock-sidebar-left");
    root.style.removeProperty("--dock-sidebar-width");
    root.style.removeProperty("--dock-left");
    root.style.removeProperty("--dock-width");
    root.style.removeProperty("--dock-inner-offset");
    return;
  }
  const sidebarRect = sidebar.getBoundingClientRect();
  const rect = controlsRoot.getBoundingClientRect();
  root.style.setProperty("--dock-sidebar-left", `${Math.round(sidebarRect.left)}px`);
  root.style.setProperty("--dock-sidebar-width", `${Math.round(sidebarRect.width)}px`);
  root.style.setProperty("--dock-left", `${Math.round(rect.left)}px`);
  root.style.setProperty("--dock-width", `${Math.round(rect.width)}px`);
  root.style.setProperty("--dock-inner-offset", `${Math.round(rect.left - sidebarRect.left)}px`);
}

function updateSpicyUI() {
  const spicy = state.bootstrap?.options?.spicyLevels?.[state.form.spicyLevel];
  const sliderLabel = document.querySelector(".slider-label");
  const sliderHint = document.querySelector(".slider-head .field-hint");
  const slider = document.querySelector('input[name="spicySlider"]');
  if (sliderLabel && spicy) sliderLabel.textContent = spicy.label;
  if (sliderHint && spicy) sliderHint.textContent = spicy.hint;
  if (slider && spicy) slider.value = String(spicy.index);
}

function updatePhotoTypeUI() {
  const photoType = state.bootstrap?.options?.photoTypeLevels?.[state.form.photoTypeControl];
  const sliderLabel = document.querySelector(".photo-type-slider-label");
  const sliderHint = document.querySelector(".photo-type-slider-hint");
  const slider = document.querySelector('input[name="photoTypeSlider"]');
  if (sliderLabel && photoType) sliderLabel.textContent = photoType.label;
  if (sliderHint && photoType) sliderHint.textContent = photoType.hint;
  if (slider && photoType) slider.value = String(photoType.index);
}

function render() {
  if (!state.bootstrap || !state.form) {
    app.innerHTML = `<div class="shell"><div class="panel output-panel">Loading...</div></div>`;
    return;
  }
  app.innerHTML = `
    <div class="shell">
      ${outputSections.renderTopbar()}
      <main class="workspace">
        <div class="panel controls">
          <div class="controls-inner">
            ${subjectSections.renderSubject()}
            ${sceneSections.renderIntensitySection()}
            ${subjectSections.renderCoreIdentity()}
            ${sceneSections.renderSceneSection()}
            ${sceneSections.renderStylizationSection()}
            ${sceneSections.renderBatch()}
            ${outputSections.renderPresetSection()}
            ${outputSections.renderDebugSection()}
            ${outputSections.renderLineBankHelpSection()}
          </div>
        </div>
        ${outputSections.renderOutputPanel()}
      </main>
      ${outputSections.renderActionDock()}
    </div>
  `;
  syncActionDockGeometry();
  controls.applyPendingFocus();
}

controls.setRender(render);
controller.setRender(render);

async function bootstrap() {
  const data = await loadBootstrap();
  state.bootstrap = data;
  state.form = clone(data.defaults);
  controller.rememberLocationStrategy(state.form.locationStrategy);
  controller.normalizeFormDependencies();
  state.presets = data.presets;
  state.history = data.history;
  state.lastRun = data.history[0] ?? null;
  render();
}

document.addEventListener("input", (event) => {
  const target = event.target;
  if (!(target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement)) return;
  if (target.name === "presetName") {
    state.presetName = target.value;
    return;
  }
  if (target.name === "spicySlider") {
    state.form.spicyLevel = spicyOrder[Number(target.value)];
    state.error = "";
    updateSpicyUI();
    return;
  }
  if (target.name === "photoTypeSlider") {
    state.form.photoTypeControl = photoTypeOrder[Number(target.value)];
    controller.normalizeFormDependencies();
    state.error = "";
    updatePhotoTypeUI();
    render();
    return;
  }
  if (target.name === "exactThemeShortcut") {
    controller.setExactThemeShortcut(target.checked);
    return;
  }
  if (target instanceof HTMLInputElement && target.type === "checkbox") {
    controller.setField(target.name, target.checked, true);
    return;
  }
  controller.setField(target.name, target.value, RERENDER_FIELDS.has(target.name));
});

document.addEventListener("change", (event) => {
  const target = event.target;
  if (!(target instanceof HTMLInputElement)) return;
  if (target.name !== "spicySlider" && target.name !== "photoTypeSlider") return;
  render();
});

document.addEventListener("keydown", (event) => {
  let element = event.target;
  if (!(element instanceof Element)) element = element && element.parentElement;
  const trigger = element ? element.closest(".select-trigger") : null;
  const option = element ? element.closest(".select-option") : null;

  if (trigger) {
    const name = trigger.dataset.name;
    if (!name) return;
    if (event.key === "ArrowDown") {
      event.preventDefault();
      controls.openDropdown(name, state.openDropdown === name ? controls.stepDropdownValue(name, 1) : controls.stepDropdownValue(name, 1) || controls.firstDropdownValue(name));
      return;
    }
    if (event.key === "ArrowUp") {
      event.preventDefault();
      controls.openDropdown(name, state.openDropdown === name ? controls.stepDropdownValue(name, -1) : controls.stepDropdownValue(name, -1) || controls.lastDropdownValue(name));
      return;
    }
    if (event.key === "Home") {
      event.preventDefault();
      controls.openDropdown(name, controls.firstDropdownValue(name));
      return;
    }
    if (event.key === "End") {
      event.preventDefault();
      controls.openDropdown(name, controls.lastDropdownValue(name));
      return;
    }
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      if (state.openDropdown === name) {
        const selectedValue = state.activeDropdownValue || controls.dropdownFieldValue(name);
        if (selectedValue) controller.setField(name, selectedValue, true);
      } else {
        controls.openDropdown(name, controls.dropdownFieldValue(name) || controls.firstDropdownValue(name));
      }
      return;
    }
    if (event.key === "Escape" && state.openDropdown === name) {
      event.preventDefault();
      controls.closeDropdown(name, true);
    }
    return;
  }

  if (option) {
    const name = option.dataset.name;
    if (!name) return;
    const options = controls.selectOptionButtons(name);
    const currentIndex = options.findIndex((item) => item === option);
    if (event.key === "ArrowDown") {
      event.preventDefault();
      state.activeDropdownValue = options[Math.min(options.length - 1, currentIndex + 1)]?.dataset.value ?? state.activeDropdownValue;
      options[Math.min(options.length - 1, currentIndex + 1)]?.focus();
      return;
    }
    if (event.key === "ArrowUp") {
      event.preventDefault();
      state.activeDropdownValue = options[Math.max(0, currentIndex - 1)]?.dataset.value ?? state.activeDropdownValue;
      options[Math.max(0, currentIndex - 1)]?.focus();
      return;
    }
    if (event.key === "Home") {
      event.preventDefault();
      state.activeDropdownValue = options[0]?.dataset.value ?? state.activeDropdownValue;
      options[0]?.focus();
      return;
    }
    if (event.key === "End") {
      event.preventDefault();
      state.activeDropdownValue = options[options.length - 1]?.dataset.value ?? state.activeDropdownValue;
      options[options.length - 1]?.focus();
      return;
    }
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      controls.requestFocus("trigger", name);
      controller.setField(name, option.dataset.value, true);
      return;
    }
    if (event.key === "Escape") {
      event.preventDefault();
      controls.closeDropdown(name, true);
    }
    return;
  }

  if (event.key !== "Escape" || !state.openDropdown) return;
  controls.closeDropdown(state.openDropdown, true);
});

document.addEventListener("click", async (event) => {
  let element = event.target;
  if (!(element instanceof Element)) element = element && element.parentElement;
  const target = element ? element.closest("[data-action]") : null;

  if (!target) {
    const clickedInsideSelect = element ? !!element.closest(".custom-select") : false;
    if (state.openDropdown && !clickedInsideSelect) controls.closeDropdown(state.openDropdown, false);
    return;
  }

  const { action, value, id, index } = target.dataset;

  if (action === "set-mode") controller.setField("mode", value);
  if (action === "apply-women-personalization") {
    controller.applyWomenPersonalizationPreset(target.dataset.profile || "");
    return;
  }
  if (action === "toggle-dropdown") {
    state.openDropdown = state.openDropdown === target.dataset.name ? null : target.dataset.name;
    state.activeDropdownValue = state.openDropdown ? controls.dropdownFieldValue(target.dataset.name) || controls.firstDropdownValue(target.dataset.name) : "";
    if (!state.openDropdown) controls.requestFocus("trigger", target.dataset.name);
    else if (state.activeDropdownValue) controls.requestFocus("option", target.dataset.name, state.activeDropdownValue);
    render();
    return;
  }
  if (action === "pick-dropdown") {
    state.activeDropdownValue = target.dataset.value ?? "";
    controls.requestFocus("trigger", target.dataset.name);
    controller.setField(target.dataset.name, target.dataset.value, true);
    return;
  }
  if (action === "generate") await controller.generate();
  if (action === "reset-form") controller.resetForm();
  if (action === "save-preset") await controller.savePreset();
  if (action === "copy-inline-value") await controller.copyText(value ?? "");
  if (action === "copy-all") await controller.copyText(state.lastRun?.outputText ?? "");
  if (action === "copy-prompt") await controller.copyText(state.lastRun?.prompts?.[Number(index)]?.prompt ?? "");
  if (action === "load-preset") {
    const preset = state.presets.find((item) => item.id === id);
    if (preset) {
      state.form = clone(preset.formState);
      controller.rememberLocationStrategy(state.form.locationStrategy);
      controller.normalizeFormDependencies();
      render();
    }
  }
  if (action === "delete-preset") await controller.removePreset(id);
  if (action === "copy-history") {
    const run = state.history.find((item) => item.id === id);
    await controller.copyText(run?.outputText ?? "");
  }
});

bootstrap().catch((error) => {
  app.innerHTML = `<div class="shell"><div class="panel output-panel">${esc(error.message)}</div></div>`;
});

window.addEventListener("resize", syncActionDockGeometry);
