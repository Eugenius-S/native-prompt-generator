export function createControls({ state, esc }) {
  let render = () => {};

  function setRender(nextRender) {
    render = nextRender;
  }

  function optionMarkup(items, value) {
    return items
      .map((item) => `<option value="${esc(item.value)}" ${item.value === value ? "selected" : ""} ${item.disabled ? "disabled" : ""}>${esc(item.label)}</option>`)
      .join("");
  }

  function resolveOption(items, value) {
    return items.find((item) => item.value === value) ?? items.find((item) => !item.disabled) ?? items[0] ?? { value: "", label: "" };
  }

  function withLegacyCurrentOption(items, value, legacyLabels) {
    if (!value || items.some((item) => item.value === value) || !legacyLabels[value]) return items;
    return [{ value, label: `Legacy saved preset: ${legacyLabels[value]}`, disabled: true }, ...items];
  }

  function dropdownMenuId(name) {
    return `select-menu-${name}`;
  }

  function dropdownOptionId(name, value) {
    return `select-option-${name}-${String(value).replace(/[^a-z0-9_-]+/gi, "-")}`;
  }

  function dropdownFieldValue(name) {
    if (name === "debugMode") return state.form.debugMode ? "true" : "false";
    if (name === "useCoreIdentityPrompt") return state.form.useCoreIdentityPrompt ? "true" : "false";
    return String(state.form?.[name] ?? "");
  }

  function requestFocus(kind, name, value = "") {
    state.focusRequest = { kind, name, value };
  }

  function selectOptionButtons(name) {
    const root = document.querySelector(`.custom-select[data-select-name="${name}"]`);
    if (!root) return [];
    return Array.from(root.querySelectorAll(".select-option:not([disabled])"));
  }

  function firstDropdownValue(name) {
    return selectOptionButtons(name)[0]?.dataset.value ?? "";
  }

  function lastDropdownValue(name) {
    const buttons = selectOptionButtons(name);
    return buttons[buttons.length - 1]?.dataset.value ?? "";
  }

  function stepDropdownValue(name, step) {
    const buttons = selectOptionButtons(name);
    if (!buttons.length) return "";
    const currentValue = state.openDropdown === name ? state.activeDropdownValue || dropdownFieldValue(name) : dropdownFieldValue(name);
    const currentIndex = buttons.findIndex((button) => button.dataset.value === currentValue);
    if (currentIndex === -1) return buttons[step >= 0 ? 0 : buttons.length - 1]?.dataset.value ?? "";
    const nextIndex = Math.max(0, Math.min(buttons.length - 1, currentIndex + step));
    return buttons[nextIndex]?.dataset.value ?? currentValue;
  }

  function applyPendingFocus() {
    const pending = state.focusRequest;
    if (!pending) return;
    state.focusRequest = null;
    window.requestAnimationFrame(() => {
      if (pending.kind === "trigger") {
        document.querySelector(`.select-trigger[data-name="${pending.name}"]`)?.focus();
        return;
      }
      const selector = pending.value ? `.select-option[data-name="${pending.name}"][data-value="${pending.value}"]` : `.select-option[data-name="${pending.name}"]`;
      document.querySelector(selector)?.focus();
    });
  }

  function openDropdown(name, focusValue = "") {
    state.openDropdown = name;
    state.activeDropdownValue = focusValue || dropdownFieldValue(name) || firstDropdownValue(name);
    if (state.activeDropdownValue) requestFocus("option", name, state.activeDropdownValue);
    render();
  }

  function closeDropdown(name, restoreFocus = true) {
    state.openDropdown = null;
    state.activeDropdownValue = "";
    if (restoreFocus) requestFocus("trigger", name);
    render();
  }

  function selectControl(name, items, value, disabled = false) {
    const selected = resolveOption(items, value);
    const isOpen = !disabled && state.openDropdown === name;
    const activeValue = isOpen ? state.activeDropdownValue || selected.value : selected.value;
    const menuId = dropdownMenuId(name);
    const activeDescendant = isOpen ? dropdownOptionId(name, activeValue) : "";
    return `
      <div class="custom-select ${isOpen ? "is-open" : ""} ${disabled ? "is-disabled" : ""}" data-select-name="${esc(name)}">
        <button
          type="button"
          class="select-trigger"
          data-action="toggle-dropdown"
          data-name="${esc(name)}"
          role="combobox"
          aria-haspopup="listbox"
          aria-expanded="${isOpen ? "true" : "false"}"
          aria-controls="${esc(menuId)}"
          aria-activedescendant="${esc(activeDescendant)}"
          ${disabled ? "disabled" : ""}
        >
          <span>${esc(selected.label)}</span>
          <span class="select-chevron" aria-hidden="true"></span>
        </button>
        <div class="select-menu" id="${esc(menuId)}" role="listbox" aria-hidden="${isOpen ? "false" : "true"}">
          ${items
            .map(
              (item) => `
                <button
                  type="button"
                  id="${esc(dropdownOptionId(name, item.value))}"
                  class="select-option ${item.value === activeValue ? "is-selected" : ""}"
                  data-action="pick-dropdown"
                  data-name="${esc(name)}"
                  data-value="${esc(item.value)}"
                  role="option"
                  aria-selected="${item.value === activeValue ? "true" : "false"}"
                  ${item.disabled ? "disabled" : ""}
                >
                  <span>${esc(item.label)}</span>
                </button>
              `,
            )
            .join("")}
        </div>
      </div>
    `;
  }

  function field({ label, input, hint = "", span2 = false, disabled = false, hideLabel = false }) {
    return `
      <label class="field ${span2 ? "span-2" : ""} ${disabled ? "is-disabled" : ""}">
        ${hideLabel ? "" : `<span class="field-label">${esc(label)}</span>`}
        ${input}
        ${hint ? `<span class="field-hint">${esc(hint)}</span>` : ""}
      </label>
    `;
  }

  function segmentedControl(name, items, value, disabled = false) {
    return `
      <div class="segmented-control ${disabled ? "is-disabled" : ""}">
        ${items
          .map(
            (item) => `
              <label class="segmented-option ${item.value === value ? "active" : ""} ${disabled ? "is-disabled" : ""}">
                <input type="radio" name="${esc(name)}" value="${esc(item.value)}" ${item.value === value ? "checked" : ""} ${disabled ? "disabled" : ""} />
                <span>${esc(item.label)}</span>
              </label>
            `,
          )
          .join("")}
      </div>
    `;
  }

  return {
    setRender,
    optionMarkup,
    resolveOption,
    withLegacyCurrentOption,
    dropdownMenuId,
    dropdownOptionId,
    dropdownFieldValue,
    requestFocus,
    selectOptionButtons,
    firstDropdownValue,
    lastDropdownValue,
    stepDropdownValue,
    applyPendingFocus,
    openDropdown,
    closeDropdown,
    selectControl,
    field,
    segmentedControl,
  };
}
