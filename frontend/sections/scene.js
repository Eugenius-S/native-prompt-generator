export function createSceneSections({ state, esc, controls, icons, iconMarkup }) {
  const { field, selectControl } = controls;

  function renderIntensitySection() {
    const options = state.bootstrap.options;
    const spicy = options.spicyLevels[state.form.spicyLevel];
    const spicyIndex = spicy.index;
    return `
      <section class="section">
        <div class="section-head"><div><h2>Spicy level</h2></div></div>
        <div class="field-grid">
          ${field({
            label: "Spicy level",
            span2: true,
            hideLabel: true,
            input: `
              <div class="slider-wrap">
                <div class="slider-head">
                  <span class="slider-label-wrap">${iconMarkup(icons.chili, "slider-icon")}<span class="slider-label">${esc(spicy.label)}</span></span>
                  <span class="field-hint">${esc(spicy.hint)}</span>
                </div>
                <input class="slider-control" type="range" min="0" max="6" step="1" name="spicySlider" value="${spicyIndex}" />
              </div>
            `,
          })}
        </div>
      </section>
    `;
  }

  function renderBatch() {
    const options = state.bootstrap.options;
    const validationHelp = options.validationModeHelp[state.form.validationMode] ?? "";
    return `
      <section class="section">
        <div class="section-head"><div><h2>Batch</h2></div></div>
        <div class="field-grid">
          ${field({ label: "Validation mode", input: selectControl("validationMode", options.validationModeOptions, state.form.validationMode), hint: validationHelp })}
          ${field({
            label: "Anti-repeat effort",
            input: selectControl("antiRepeat", options.antiRepeatOptions, state.form.antiRepeat),
            hint: "Higher levels try harder to avoid repeated scenes, outfits, and poses.",
          })}
        </div>
      </section>
    `;
  }

  function renderSceneSection() {
    const options = state.bootstrap.options;
    const mode = state.form.mode;
    const exactThemeMode = state.form.locationStrategy === "exact_theme";
    const womenSceneFamilyLocked = mode === "women" && state.form.womenSceneFamily !== "random";
    return `
      <section class="section">
        <div class="section-head"><div><h2>Scene</h2></div></div>
        <div class="field-grid">
          ${field({ label: "Scene mode", input: selectControl("styleMode", options.styleModeOptions, state.form.styleMode) })}
          ${field({
            label: "Scene focus",
            input: selectControl("sceneFocus", options.sceneFocusOptions, state.form.sceneFocus, exactThemeMode),
            hint: exactThemeMode ? "Turns off while Exact theme is on." : "",
            disabled: exactThemeMode,
          })}
          ${mode === "women"
            ? field({
                label: "Women scene family",
                span2: true,
                input: selectControl("womenSceneFamily", options.womenSceneFamilyOptions, state.form.womenSceneFamily),
                hint: "Women mode only. Pushes the run toward one scene family and adjusts reveal, hair, and makeup around it.",
              })
            : ""}
          ${field({
            label: "Exact theme shortcut",
            span2: true,
            input: `
              <label class="toggle-row">
                <input type="checkbox" name="exactThemeShortcut" ${exactThemeMode ? "checked" : ""} />
                <span>Lock scene to exact theme</span>
              </label>
            `,
            hint: womenSceneFamilyLocked ? "This stays synced with Location strategy, but Women scene family still wins." : "This stays synced with Location strategy = Exact theme.",
          })}
          ${field({ label: "Location strategy", input: selectControl("locationStrategy", options.locationStrategyOptions, state.form.locationStrategy), hint: exactThemeMode ? "This stays in sync with the shortcut." : "" })}
          ${field({
            label: "Exact theme",
            span2: true,
            input: `<input class="input" name="exactTheme" value="${esc(state.form.exactTheme)}" placeholder="sunlit Mediterranean villa interiors / moody wine bar / retro arcade neon" />`,
            hint: exactThemeMode ? (womenSceneFamilyLocked ? "Strongest scene push, but Women scene family can still override it." : "Strongest scene push.") : "",
          })}
          ${field({
            label: "Character constraint",
            span2: true,
            input: `<input class="input" name="characterConstraint" value="${esc(state.form.characterConstraint)}" placeholder="heiress / fantasy warrior / femme fatale / Lara Croft type" />`,
            hint: "Free text that nudges subject, outfit, scene, and vibe.",
          })}
        </div>
      </section>
    `;
  }

  function renderStylizationSection() {
    const options = state.bootstrap.options;
    const photoType = options.photoTypeLevels[state.form.photoTypeControl];
    const photoTypeIndex = photoType.index;
    return `
      <section class="section">
        <div class="section-head"><div><h2>Stylization</h2></div></div>
        <div class="field-grid">
          ${field({
            label: "Photo type",
            span2: true,
            hideLabel: true,
            input: `
              <div class="slider-wrap">
                <div class="slider-head">
                  <span class="slider-label-wrap"><span class="slider-label photo-type-slider-label">${esc(photoType.label)}</span></span>
                  <span class="field-hint photo-type-slider-hint">${esc(photoType.hint)}</span>
                </div>
                <input class="slider-control" type="range" min="0" max="5" step="1" name="photoTypeSlider" value="${photoTypeIndex}" />
              </div>
            `,
          })}
          ${field({
            label: "Photo treatment bias",
            input: selectControl("photoTreatmentControl", options.photoTreatmentControlOptions, state.form.photoTreatmentControl, state.form.photoTypeControl !== "custom"),
            hint: state.form.photoTypeControl === "custom" ? "Manual treatment lock." : "Available only when Photo type is Custom.",
            disabled: state.form.photoTypeControl !== "custom",
          })}
          ${field({ label: "Vibe", input: selectControl("styleVibe", options.styleVibeOptions, state.form.styleVibe) })}
          ${field({ label: "Pose / framing", input: selectControl("poseFramingControl", options.poseFramingOptions, state.form.poseFramingControl) })}
          ${field({ label: "Lighting / time", input: selectControl("lightingControl", options.lightingOptions, state.form.lightingControl) })}
        </div>
      </section>
    `;
  }

  return { renderIntensitySection, renderBatch, renderSceneSection, renderStylizationSection };
}
