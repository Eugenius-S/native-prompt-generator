export const state = {
  bootstrap: null,
  form: null,
  locationStrategyBeforeExactTheme: "fresh_only",
  presets: [],
  history: [],
  lastRun: null,
  loading: false,
  error: "",
  presetName: "",
  openDropdown: null,
  activeDropdownValue: "",
  focusRequest: null,
};

export const clone = (value) => JSON.parse(JSON.stringify(value));

export const disabledFields = () => new Set(state.bootstrap?.disabledFields ?? []);

export const isDisabled = (key) => disabledFields().has(key);
