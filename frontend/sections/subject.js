const LEGACY_RACE_PRESET_LABELS = {
  black_nigerian: "Black Nigerian",
  latina_colombian: "Colombian Latina",
  latina_mexican: "Mexican Latina",
  white_english: "White English",
  white_italian: "White Italian",
  white_polish: "White Polish",
};

const LEGACY_MALE_RACE_PRESET_LABELS = {
  black_nigerian: "Black Nigerian",
  latina_colombian: "Colombian Latino",
  latina_mexican: "Mexican Latino",
  white_english: "White English",
  white_italian: "White Italian",
  white_polish: "White Polish",
};

const WOMEN_PERSONALIZATION_PRESETS = [
  { value: "everyday_clean", label: "Clean everyday" },
  { value: "soft_editorial", label: "Soft editorial" },
  { value: "night_glam", label: "Night glam" },
  { value: "reset", label: "Back to random" },
];

export function createSubjectSections({ state, esc, controls, icons, iconMarkup }) {
  const { field, segmentedControl, selectControl, withLegacyCurrentOption } = controls;

  function renderModeButtons() {
    return state.bootstrap.options.modeOptions
      .map((item) => {
        const active = state.form.mode === item.value ? "active" : "";
        const modeIcon = item.value === "women" ? icons.woman : item.value === "men" ? icons.man : icons.couple;
        return `<button type="button" class="mode-button ${active}" title="${esc(item.value)}" aria-label="${esc(item.value)}" data-action="set-mode" data-value="${esc(item.value)}" ${item.disabled ? "disabled" : ""}>${iconMarkup(modeIcon, "mode-icon")}</button>`;
      })
      .join("");
  }

  function renderSubject() {
    const options = state.bootstrap.options;
    const mode = state.form.mode;
    const racePresetOptions = withLegacyCurrentOption(options.racePresetOptions, state.form.racePreset, LEGACY_RACE_PRESET_LABELS);
    const maleRacePresetOptions = withLegacyCurrentOption(options.maleRacePresetOptions, state.form.maleRacePreset, LEGACY_MALE_RACE_PRESET_LABELS);
    const showCustomRace = state.form.racePreset === "other";
    const showMaleCustomRace = state.form.maleRacePreset === "other";
    const customRacePlaceholder = {
      women: "white Balkan woman / Black American woman / Latina woman",
      men: "white Balkan man / Black American man / Latino man",
      couples: "white Balkan woman / Black American woman / Latina woman",
    };
    const maleCustomRacePlaceholder = "white Balkan man / Black American man / Latino man";
    if (mode === "couples") {
      return `
        <section class="section">
          <div class="section-head"><div><h2>Subject</h2></div></div>
          <div class="mode-switch">${renderModeButtons()}</div>
          <div class="field-grid" style="margin-bottom:20px;">
            ${field({ label: "Identity mode", span2: true, input: selectControl("personMode", options.personModeOptions, state.form.personMode) })}
          </div>
          <div class="sub-block">
            <div class="sub-block-head"><h3>Woman</h3></div>
            <div class="field-grid">
              ${field({ label: "Age", input: `<input class="input" name="age" value="${esc(state.form.age)}" placeholder="Random / 18 / 18-20 / 21-23 / 25-30 / 30+" />` })}
              ${field({ label: "Identity preset", input: selectControl("racePreset", racePresetOptions, state.form.racePreset) })}
              ${field({ label: "Name", input: `<input class="input" name="name" value="${esc(state.form.name)}" placeholder="Sofia / Lara / Veronica" />` })}
              ${field({
                label: "Custom identity text",
                disabled: !showCustomRace,
                input: `<input class="input" name="customRace" value="${esc(state.form.customRace)}" placeholder="${esc(customRacePlaceholder.couples)}" ${showCustomRace ? "" : "disabled"} />`,
                hint: showCustomRace ? "Used for the woman." : "",
              })}
            </div>
          </div>
          <div class="sub-block">
            <div class="sub-block-head"><h3>Man</h3></div>
            <div class="field-grid">
              ${field({ label: "Age", input: `<input class="input" name="maleAge" value="${esc(state.form.maleAge)}" placeholder="Random / 18 / 18-20 / 21-23 / 25-30 / 30+" />` })}
              ${field({ label: "Identity preset", input: selectControl("maleRacePreset", maleRacePresetOptions, state.form.maleRacePreset) })}
              ${field({ label: "Name", input: `<input class="input" name="maleName" value="${esc(state.form.maleName)}" placeholder="Alex / Daniel / Marco" />` })}
              ${field({
                label: "Custom identity text",
                disabled: !showMaleCustomRace,
                input: `<input class="input" name="maleCustomRace" value="${esc(state.form.maleCustomRace)}" placeholder="${esc(maleCustomRacePlaceholder)}" ${showMaleCustomRace ? "" : "disabled"} />`,
                hint: showMaleCustomRace ? "Used for the man." : "",
              })}
            </div>
          </div>
        </section>
      `;
    }
    return `
      <section class="section">
        <div class="section-head"><div><h2>Subject</h2></div></div>
        <div class="mode-switch">${renderModeButtons()}</div>
        <div class="field-grid">
          ${field({ label: "Identity mode", input: selectControl("personMode", options.personModeOptions, state.form.personMode) })}
          ${field({ label: "Age", input: `<input class="input" name="age" value="${esc(state.form.age)}" placeholder="Random / 18 / 18-20 / 21-23 / 25-30 / 30+" />` })}
          ${field({ label: "Name", input: `<input class="input" name="name" value="${esc(state.form.name)}" placeholder="Sofia / Lara / Veronica" />` })}
          ${field({ label: "Identity preset", input: selectControl("racePreset", racePresetOptions, state.form.racePreset) })}
          ${field({
            label: "Custom identity text",
            span2: true,
            disabled: !showCustomRace,
            input: `<input class="input" name="customRace" value="${esc(state.form.customRace)}" placeholder="${esc(customRacePlaceholder[mode] ?? customRacePlaceholder.women)}" ${showCustomRace ? "" : "disabled"} />`,
            hint: showCustomRace ? "Used in scoring and in the final subject text." : "",
          })}
        </div>
      </section>
    `;
  }

  function renderCoreIdentity() {
    const options = state.bootstrap.options;
    const mode = state.form.mode;
    const samePersonMode = state.form.personMode === "same_person";
    const femaleAppearanceCustom = state.form.appearanceMode === "custom";
    const maleAppearanceCustom = state.form.maleAppearanceMode === "custom";
    const customHairstyle = state.form.hairstyle === "custom";
    const maleCustomHairstyle = state.form.maleHairstyle === "custom";
    const customHairColor = state.form.hairColorControl === "custom";
    const maleHairLengthOptions = options.hairLengthOptions;
    const eyeColorField = field({
      label: "Eye color",
      disabled: femaleAppearanceCustom,
      input: selectControl("eyeColorControl", options.eyeColorOptions, state.form.eyeColorControl, femaleAppearanceCustom),
    });
    const breastSizeField = field({
      label: "Breast size",
      disabled: femaleAppearanceCustom,
      input: selectControl("breastSizeControl", options.breastSizeOptions, state.form.breastSizeControl, femaleAppearanceCustom),
    });
    const femaleAppearanceModeField = field({
      label: "Appearance mode",
      span2: true,
      hideLabel: true,
      input: segmentedControl("appearanceMode", options.appearanceModeOptions, state.form.appearanceMode),
    });
    const maleAppearanceModeField = field({
      label: "Appearance mode",
      span2: true,
      hideLabel: true,
      input: segmentedControl("maleAppearanceMode", options.appearanceModeOptions, state.form.maleAppearanceMode),
    });

    const renderFemaleAppearanceBlocks = ({ includeSamePersonExtras = false } = {}) => `
      <div class="sub-block">
        <div class="sub-block-head"><h3>Physical traits</h3></div>
        <div class="field-grid">
          ${field({ label: "Body mix", disabled: femaleAppearanceCustom, input: selectControl("bodyMixPreset", options.bodyMixPresetOptions, state.form.bodyMixPreset, femaleAppearanceCustom) })}
          ${breastSizeField}
          ${field({
            label: "Hair color",
            span2: true,
            disabled: femaleAppearanceCustom,
            input: `
              <div class="field-stack">
                ${selectControl("hairColorControl", options.hairColorControlOptions, state.form.hairColorControl, femaleAppearanceCustom)}
                <label class="toggle-row ${femaleAppearanceCustom || state.form.hairColorControl !== "random" ? "is-disabled" : ""}">
                  <input type="checkbox" name="allowDyedNaturalHairColors" ${state.form.allowDyedNaturalHairColors ? "checked" : ""} ${femaleAppearanceCustom || state.form.hairColorControl !== "random" ? "disabled" : ""} />
                  <span>Allow dyed hair</span>
                </label>
              </div>
            `,
            hint: femaleAppearanceCustom ? "" : state.form.hairColorControl === "random" ? "Keeps it to natural-looking dyed shades." : "Only used when Hair color is Random.",
          })}
          ${field({ label: "Custom hair color", disabled: femaleAppearanceCustom || !customHairColor, input: `<input class="input" name="customHairColor" value="${esc(state.form.customHairColor)}" placeholder="warm chestnut / espresso black / honey blonde" ${femaleAppearanceCustom || !customHairColor ? "disabled" : ""} />` })}
          ${eyeColorField}
        </div>
      </div>
      <div class="sub-block">
        <div class="sub-block-head"><h3>Hair &amp; finish</h3></div>
        <div class="field-grid">
          ${field({ label: "Beauty finish", disabled: femaleAppearanceCustom, input: selectControl("beautyFinishControl", options.beautyFinishOptions, state.form.beautyFinishControl, femaleAppearanceCustom) })}
          ${field({ label: "Makeup", disabled: femaleAppearanceCustom, input: selectControl("makeupControl", options.makeupControlOptions, state.form.makeupControl, femaleAppearanceCustom) })}
          ${field({ label: "Hair length", disabled: femaleAppearanceCustom, input: selectControl("hairLength", options.hairLengthOptions, state.form.hairLength, femaleAppearanceCustom) })}
          ${field({ label: "Hairstyle", disabled: femaleAppearanceCustom, input: selectControl("hairstyle", options.hairstyleOptions, state.form.hairstyle, femaleAppearanceCustom) })}
          ${field({ label: "Custom hairstyle", disabled: femaleAppearanceCustom || !customHairstyle, input: `<input class="input" name="customHair" value="${esc(state.form.customHair)}" placeholder="wet slicked-back bob / elegant loose curls / polished bun" ${femaleAppearanceCustom || !customHairstyle ? "disabled" : ""} />` })}
        </div>
      </div>
      <div class="sub-block">
        <div class="sub-block-head"><h3>Clothing</h3></div>
        <div class="field-grid">
          ${field({ label: "Outfit vibe", disabled: femaleAppearanceCustom, input: selectControl("outfitVibeControl", options.outfitVibeOptions, state.form.outfitVibeControl, femaleAppearanceCustom) })}
          ${field({ label: "Reveal level", disabled: femaleAppearanceCustom, input: selectControl("outfitReveal", options.outfitRevealOptions, state.form.outfitReveal, femaleAppearanceCustom) })}
        </div>
      </div>
      <div class="sub-block">
        <div class="sub-block-head"><h3>Custom appearance</h3></div>
        <div class="field-grid">
          ${field({
            label: "Custom appearance prompt",
            span2: true,
            disabled: !femaleAppearanceCustom,
            input: `<textarea class="textarea" name="appearancePrompt" placeholder="polished copper redhead with green eyes, clean makeup, silk blouse and midi skirt" ${femaleAppearanceCustom ? "" : "disabled"}>${esc(state.form.appearancePrompt)}</textarea>`,
            hint: femaleAppearanceCustom ? "Keeps the same woman look across this run." : "",
          })}
          ${includeSamePersonExtras
            ? `
              ${field({
                label: "Use core identity prompt",
                span2: true,
                input: `
                  <label class="toggle-row">
                    <input type="checkbox" name="useCoreIdentityPrompt" ${state.form.useCoreIdentityPrompt ? "checked" : ""} />
                    <span>Keep one core identity prompt across the batch</span>
                  </label>
                `,
              })}
              ${field({ label: "Core identity prompt", span2: true, disabled: !state.form.useCoreIdentityPrompt, input: `<textarea class="textarea" name="coreIdentityPrompt" placeholder="One fixed model description for the whole batch." ${state.form.useCoreIdentityPrompt ? "" : "disabled"}>${esc(state.form.coreIdentityPrompt)}</textarea>` })}
            `
            : ""}
        </div>
      </div>
    `;

    const renderMaleAppearanceBlocks = ({ includeBodyMix = true } = {}) => `
      ${includeBodyMix
        ? `
          <div class="sub-block">
            <div class="sub-block-head"><h3>Physical traits</h3></div>
            <div class="field-grid">
              ${field({ label: "Body mix", disabled: maleAppearanceCustom, input: selectControl("bodyMixPreset", options.bodyMixPresetOptions, state.form.bodyMixPreset, maleAppearanceCustom) })}
            </div>
          </div>
        `
        : ""}
      <div class="sub-block">
        <div class="sub-block-head"><h3>Hair &amp; finish</h3></div>
        <div class="field-grid">
          ${field({ label: "Hair length", disabled: maleAppearanceCustom, input: selectControl("maleHairLength", maleHairLengthOptions, state.form.maleHairLength, maleAppearanceCustom) })}
          ${field({ label: "Hairstyle", disabled: maleAppearanceCustom, input: selectControl("maleHairstyle", options.maleHairstyleOptions, state.form.maleHairstyle, maleAppearanceCustom) })}
          ${field({ label: "Custom hairstyle", span2: true, disabled: maleAppearanceCustom || !maleCustomHairstyle, input: `<input class="input" name="maleCustomHair" value="${esc(state.form.maleCustomHair)}" placeholder="slicked-back undercut / relaxed surfer hair / polished buzz cut" ${maleAppearanceCustom || !maleCustomHairstyle ? "disabled" : ""} />` })}
          ${field({ label: "Grooming", disabled: maleAppearanceCustom, input: selectControl("maleGroomingControl", options.maleGroomingOptions, state.form.maleGroomingControl, maleAppearanceCustom) })}
        </div>
      </div>
      <div class="sub-block">
        <div class="sub-block-head"><h3>Clothing</h3></div>
        <div class="field-grid">
          ${field({ label: "Outfit vibe", disabled: maleAppearanceCustom, input: selectControl("maleOutfitControl", options.maleOutfitOptions, state.form.maleOutfitControl, maleAppearanceCustom) })}
        </div>
      </div>
      <div class="sub-block">
        <div class="sub-block-head"><h3>Custom appearance</h3></div>
        <div class="field-grid">
          ${field({
            label: "Custom appearance prompt",
            span2: true,
            disabled: !maleAppearanceCustom,
            input: `<textarea class="textarea" name="maleAppearancePrompt" placeholder="clean side-part haircut, light stubble, open-collar shirt with tailored trousers" ${maleAppearanceCustom ? "" : "disabled"}>${esc(state.form.maleAppearancePrompt)}</textarea>`,
            hint: maleAppearanceCustom ? "Keeps the same man look across this run." : "",
          })}
        </div>
      </div>
    `;

    if (mode === "men") {
      return `
        <section class="section">
          <div class="section-head"><div><h2>Appearance</h2></div></div>
          <div class="field-grid">${maleAppearanceModeField}</div>
          <p class="sub-block-copy">These fields shape the man for single-man runs.</p>
          ${renderMaleAppearanceBlocks()}
        </section>
      `;
    }

    if (mode === "couples") {
      return `
        <section class="section">
          <div class="section-head"><div><h2>Appearance</h2></div></div>
          <div class="sub-block">
            <div class="sub-block-head"><h3>Woman</h3></div>
            <div class="field-grid">${femaleAppearanceModeField}</div>
            ${renderFemaleAppearanceBlocks({ includeSamePersonExtras: false })}
          </div>
          <div class="sub-block">
            <div class="sub-block-head"><h3>Man</h3></div>
            <div class="field-grid">${maleAppearanceModeField}</div>
            <p class="sub-block-copy">Body mix stays in the Woman block. Here you control the man's hair, grooming, and outfit.</p>
            ${renderMaleAppearanceBlocks({ includeBodyMix: false })}
          </div>
        </section>
      `;
    }

    return `
      <section class="section">
        <div class="section-head"><div><h2>Personalization</h2></div></div>
        <div class="field-grid">${femaleAppearanceModeField}</div>
        <div class="sub-block">
          <div class="sub-block-head"><h3>Quick personalization</h3></div>
          <p class="sub-block-copy">One click sets a ready-made women-side mix for reveal, makeup, and hair.</p>
          <div class="inline-actions women-preset-actions">
            ${WOMEN_PERSONALIZATION_PRESETS.map((item) => `<button type="button" class="history-button" data-action="apply-women-personalization" data-profile="${esc(item.value)}" ${femaleAppearanceCustom ? "disabled" : ""}>${esc(item.label)}</button>`).join("")}
          </div>
        </div>
        ${renderFemaleAppearanceBlocks({ includeSamePersonExtras: samePersonMode })}
      </section>
    `;
  }

  return { renderModeButtons, renderSubject, renderCoreIdentity };
}
