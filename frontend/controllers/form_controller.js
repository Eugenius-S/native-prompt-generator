export function createFormController({ state, clone, generateRun, savePresetRequest, deletePresetRequest }) {
  let render = () => {};

  function setRender(nextRender) {
    render = nextRender;
  }

  function rememberLocationStrategy(value) {
    if (value && value !== "exact_theme") state.locationStrategyBeforeExactTheme = value;
  }

  function restoreLocationStrategyAfterExactTheme() {
    return state.locationStrategyBeforeExactTheme && state.locationStrategyBeforeExactTheme !== "exact_theme"
      ? state.locationStrategyBeforeExactTheme
      : state.bootstrap?.defaults?.locationStrategy ?? "fresh_only";
  }

  function normalizeFormDependencies() {
    if (state.form.personMode !== "same_person") state.form.useCoreIdentityPrompt = false;
    if (state.form.mode !== "women") state.form.useCoreIdentityPrompt = false;
    if (state.form.appearanceMode !== "custom") state.form.appearancePrompt = "";
    if (state.form.maleAppearanceMode !== "custom") state.form.maleAppearancePrompt = "";
    if (state.form.mode === "men") {
      state.form.appearanceMode = "generated";
      state.form.appearancePrompt = "";
    }
    if (state.form.mode === "women") {
      state.form.maleAppearanceMode = "generated";
      state.form.maleAppearancePrompt = "";
    }
    if (state.form.mode === "men" && !state.form.maleHairLength) state.form.maleHairLength = "short";
    if (state.form.racePreset === "black_british") state.form.racePreset = "other";
    if (state.form.maleRacePreset === "black_british") state.form.maleRacePreset = "other";
    if (state.form.racePreset !== "other") state.form.customRace = "";
    if (state.form.maleRacePreset !== "other") state.form.maleCustomRace = "";
    if (state.form.hairstyle !== "custom") state.form.customHair = "";
    if (state.form.maleHairstyle !== "custom") state.form.maleCustomHair = "";
    if (state.form.hairColorControl !== "custom") state.form.customHairColor = "";
    if (state.form.photoTypeControl !== "custom") state.form.photoTreatmentControl = "random";
    if (state.form.mode === "men" || state.form.hairColorControl !== "random") state.form.allowDyedNaturalHairColors = false;
  }

  function resetForm() {
    state.form = clone(state.bootstrap.defaults);
    rememberLocationStrategy(state.form.locationStrategy);
    state.openDropdown = null;
    normalizeFormDependencies();
    state.error = "";
    render();
  }

  function setExactThemeShortcut(enabled) {
    if (enabled) {
      rememberLocationStrategy(state.form.locationStrategy);
      setField("locationStrategy", "exact_theme", true);
      return;
    }
    if (state.form.locationStrategy === "exact_theme") setField("locationStrategy", restoreLocationStrategyAfterExactTheme(), true);
  }

  function setField(name, value, rerender = true) {
    if (name === "debugMode") state.form.debugMode = value === true || value === "true";
    else if (name === "useCoreIdentityPrompt") state.form.useCoreIdentityPrompt = value === true || value === "true";
    else state.form[name] = value;
    if (name === "locationStrategy") rememberLocationStrategy(value);
    state.openDropdown = null;
    state.activeDropdownValue = "";
    normalizeFormDependencies();
    state.error = "";
    if (rerender) render();
  }

  function firstOptionValue(items, fallback = "random") {
    if (!Array.isArray(items) || !items.length) return fallback;
    return items.find((item) => !item.disabled)?.value ?? items[0].value ?? fallback;
  }

  function pickOptionValue(items, preferredValues, fallback = "random") {
    if (!Array.isArray(items) || !items.length) return fallback;
    for (const value of preferredValues) {
      if (items.some((item) => item.value === value && !item.disabled)) return value;
    }
    return firstOptionValue(items, fallback);
  }

  function womenPersonalizationPatch(profileId) {
    const options = state.bootstrap?.options ?? {};
    const makeupOptions = options.makeupControlOptions ?? [];
    const hairLengthOptions = options.hairLengthOptions ?? [];
    const outfitRevealOptions = options.outfitRevealOptions ?? [];
    const hairstyleOptions = options.hairstyleOptions ?? [];
    const hairColorOptions = options.hairColorControlOptions ?? [];
    const eyeColorOptions = options.eyeColorOptions ?? [];
    const breastSizeOptions = options.breastSizeOptions ?? [];

    const randomPatch = {
      appearanceMode: "generated",
      outfitReveal: pickOptionValue(outfitRevealOptions, ["random"], "random"),
      makeupControl: pickOptionValue(makeupOptions, ["random"], "random"),
      hairLength: pickOptionValue(hairLengthOptions, ["random"], "random"),
      hairstyle: pickOptionValue(hairstyleOptions, ["random"], firstOptionValue(hairstyleOptions, "random")),
      hairColorControl: pickOptionValue(hairColorOptions, ["random"], "random"),
      eyeColorControl: pickOptionValue(eyeColorOptions, ["random"], "random"),
      breastSizeControl: pickOptionValue(breastSizeOptions, ["random"], "random"),
      allowDyedNaturalHairColors: false,
    };

    if (profileId === "everyday_clean") {
      return {
        ...randomPatch,
        outfitReveal: pickOptionValue(outfitRevealOptions, ["reserved", "balanced", "random"], randomPatch.outfitReveal),
        makeupControl: pickOptionValue(makeupOptions, ["clean_minimal", "fresh_barely_there", "natural_pretty", "random"], randomPatch.makeupControl),
        hairLength: pickOptionValue(hairLengthOptions, ["medium", "long", "random"], randomPatch.hairLength),
      };
    }

    if (profileId === "soft_editorial") {
      return {
        ...randomPatch,
        outfitReveal: pickOptionValue(outfitRevealOptions, ["balanced", "reserved", "random"], randomPatch.outfitReveal),
        makeupControl: pickOptionValue(makeupOptions, ["soft_glam_clean", "natural_pretty", "random"], randomPatch.makeupControl),
        hairLength: pickOptionValue(hairLengthOptions, ["medium", "long", "random"], randomPatch.hairLength),
      };
    }

    if (profileId === "night_glam") {
      return {
        ...randomPatch,
        outfitReveal: pickOptionValue(outfitRevealOptions, ["revealing", "balanced", "random"], randomPatch.outfitReveal),
        makeupControl: pickOptionValue(makeupOptions, ["night_out_glam", "glossy_soft_glam", "soft_glam_clean", "random"], randomPatch.makeupControl),
        hairLength: pickOptionValue(hairLengthOptions, ["long", "medium", "random"], randomPatch.hairLength),
      };
    }

    if (profileId === "reset") return randomPatch;
    return null;
  }

  function applyWomenPersonalizationPreset(profileId) {
    if (state.form.mode !== "women") return;
    const patch = womenPersonalizationPatch(profileId);
    if (!patch) return;
    Object.assign(state.form, patch);
    state.error = "";
    normalizeFormDependencies();
    render();
  }

  async function generate(formState = state.form) {
    state.loading = true;
    state.error = "";
    render();
    try {
      const data = await generateRun(formState);
      state.lastRun = data.run;
      state.history = [data.run, ...state.history].slice(0, 20);
      state.form = clone(data.run.formState);
      rememberLocationStrategy(state.form.locationStrategy);
      normalizeFormDependencies();
    } catch (error) {
      state.error = error.message;
    } finally {
      state.loading = false;
      render();
    }
  }

  async function savePreset() {
    try {
      const data = await savePresetRequest(state.presetName, state.form);
      const normalizedName = data.preset.name.trim().toLowerCase();
      state.presets = [data.preset, ...state.presets.filter((item) => item.name.trim().toLowerCase() !== normalizedName)].slice(0, 50);
      state.presetName = "";
    } catch (error) {
      state.error = error.message;
    }
    render();
  }

  async function removePreset(id) {
    try {
      await deletePresetRequest(id);
      state.presets = state.presets.filter((item) => item.id !== id);
    } catch (error) {
      state.error = error.message;
    }
    render();
  }

  async function copyText(text) {
    if (text) await navigator.clipboard.writeText(text);
  }

  return {
    setRender,
    normalizeFormDependencies,
    resetForm,
    rememberLocationStrategy,
    restoreLocationStrategyAfterExactTheme,
    setExactThemeShortcut,
    setField,
    womenPersonalizationPatch,
    applyWomenPersonalizationPreset,
    generate,
    savePreset,
    removePreset,
    copyText,
  };
}
