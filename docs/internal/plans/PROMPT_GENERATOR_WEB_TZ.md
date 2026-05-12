# Prompt Generator Web UI

In short: a local web interface is needed on top of the current prompt-generator backend so batches of prompts can be assembled quickly through the UI, debugged, and saved to presets/history.

## 1. Goal

Build a local web UI for the prompt generator.

Project folder:

```text
C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator
```

Main flow:

1. choose parameters
2. press Generate
3. receive a single text block with prompts
4. press Copy

## 2. General Rules

- The interface is local.
- Output is always text.
- One prompt = one line.
- The output is always a single text block.
- The block has a `Copy` button.
- The user does not need additional export modes.
- The UI must be useful not only for generation, but also for ongoing debugging and rule tuning.

## 3. Main Modes

### Gender / Mode

Options:

- `Women`
- `Men`
- `Couples`

Default:

- nothing selected

Until a mode is selected:

- generation is unavailable

### Person Mode

Shown only for `Women` and `Men`.

Options:

- `Same person`
- `Different persons`

Default:

- `Different persons`

This toggle is hidden for `Couples`.

## 4. Subject Block

### 4.1 Core identity prompt

Shown only when `Same person` is selected.

Type:

- text input

Placeholder:

```text
25 years old American woman, pale skin, blue eyes, large natural breasts, slim toned body
```

Meaning:

- this is the identity core for the same model

### 4.2 Name

Type:

- optional text input

Default:

- empty

Example:

```text
Megan Fox
```

### 4.3 Age

Type:

- always a text input

Default:

```text
Random
```

Examples of allowed values:

```text
Random
21
21-23
25-30
young 21
30+
```

### 4.4 Race preset

Type:

- dropdown

Default:

- `Random default split`

Options:

- `Random default split`
- `Mostly whites`
- `Mostly blacks`
- `Mostly Asian`
- `Mostly Latina`
- `Mostly mixed`
- `Other`

If `Other`:

- show a text input
- the text from it is inserted directly into the race/ethnicity read

Example:

```text
white Balkan woman
```

### 4.5 Race logic

If `Random default split` is selected:

- use the generator's current working ratio
- without Arabs and Indians

Current default ratio:

- white: 65%
- black: 20%
- latina: 10%
- asian: 5%

Then, inside the large pool, more specific reads are chosen:

- American
- Russian
- German
- Swedish
- etc.

## 5. Couples Mode

If `Couples` is selected, additional fields appear.

### 5.1 Couple type

Options:

- `male + female`
- `female + female`
- `male + male`

### 5.2 Couples race mode

Options:

- `random`
- `same race`
- `mixed race`
- `custom`

### 5.3 Couples custom race input

Shown only if race mode = `custom`

Example:

```text
white Scandinavian woman + Black British man
```

### 5.4 Couple lead

Options:

- `balanced`
- `female-led`
- `male-led`

## 6. Batch Logic

### 6.1 Batch size

Type:

- number input

Default:

- `10`

### 6.2 Spicy level

Type:

- slider `1-8`

Show alongside:

- label
- short tooltip / helper text

Levels:

| Level | Label | Meaning |
|---|---|---|
| 1 | Sweet | beautiful and soft, almost without a sexual accent |
| 2 | Cute | cute, slight flirt |
| 3 | Confident | confident, attractive |
| 4 | Playful | playful, coquettish |
| 5 | Flirty | already noticeable tease/flirt |
| 6 | Lusty | sensual, hot |
| 7 | Slutty | as slutty as possible within safe bounds |
| 8 | Extreme | extreme horny within the allowed non-explicit range |

Default:

- `4`

### 6.3 Body mix preset

Type:

- dropdown

Default:

- `Random balanced`

Options:

- `Random balanced`
- `Slim / lean`
- `Toned`
- `Athletic`
- `Curvy`
- `Mixed with curvy accent`
- `Mixed with athletic accent`

### 6.4 Anti-repeat

Type:

- dropdown

Default:

- `Normal`

Options:

- `Low`
- `Normal`
- `Hard`
- `Brutal`

### 6.5 Validation mode

Type:

- dropdown

Default:

- `Normal`

Options:

- `Loose`
- `Normal`
- `Strict`

### 6.6 Seed

Needed for reproducibility and debugging.

Fields:

- `Seed mode`: `Auto` / `Manual`
- if `Manual`, show a number input

Default:

- `Auto`

## 7. Style & Scene

### 7.1 Style mode

Type:

- dropdown

Default:

- `Random`

Options:

- `Random`
- `Studio`
- `Lifestyle`
- `Luxury`
- `Old money`
- `Romantic`
- `Vacation`
- `Sport`
- `Fitness`
- `Cosplay`
- `Gaming`
- `Fantasy`
- `Sci-fi`
- `Characters`
- `LinkedIn / Work`
- `Nightlife`
- `Cultural / Bookish`
- `Creative / Artistic`
- `Urban day`
- `Coastal`

Note:

- a separate `Dating` route is not needed
- dating feel should be assembled from a combination of:
  - lifestyle / romantic / luxury / vacation
  - plus a flirty / soft / sexy vibe

### 7.2 Style vibe

A separate dropdown so everything is not forced into one list.

Default:

- `Random`

Options:

- `Random`
- `Soft`
- `Clean`
- `Sexy`
- `Glam`
- `Cinematic`
- `Casual`
- `Flirty`
- `Rich`
- `Editorial`

### 7.3 Pose / framing control

Type:

- dropdown

Default:

- `Mixed`

Options:

- `Random`
- `More portraits`
- `More full body`
- `Mixed`

### 7.4 Lighting / time control

Type:

- dropdown

Default:

- `Mixed`

Options:

- `Random`
- `Sunny`
- `Indoor warm`
- `Night`
- `Mixed`

### 7.5 Location strategy

Type:

- dropdown

Default:

- `Fresh only`

Options:

- `Random`
- `Fresh only`
- `Allow repeats`
- `Exact theme`

If `Exact theme`:

- show a text input

Example:

```text
sunlit Mediterranean villa interiors
```

## 8. Characters Mode

If `Characters` is selected:

- use the character bank from the existing base
- pull settings from the character bank / character routes

Optional input:

- `Character constraint`

Examples:

```text
only movie heroines
more game heroines
blonde iconic women
```

## 9. Output

Output:

- one text block
- one prompt = one line
- a `Copy` button

Also:

- the text can be selected with the mouse directly

### Color-coded prompt visualization

Add color highlighting for prompt parts in the UI.

Do not color the whole line at random.

Color by segment:

- `capture style`
- `subject/model block`
- `outfit`
- `pose`
- `setting`
- `technical/photo params`

Important:

- Copy must copy plain text
- colors are only for readability

## 10. Debug / History / Presets

### 10.1 Debug mode

Type:

- toggle

Default:

- `off`

If enabled:

- show a compact debug panel below the output

What can be shown:

- `scene_family`
- `base_space`
- `repair applied / not applied`
- `fallback used / not used`
- `anti-repeat reject count`
- `framing distribution`
- `pose distribution`

This is not critical for the end user, but it is needed to tune the generator.

### 10.2 History

Store recent runs.

For each run:

- timestamp
- all UI parameters
- seed
- output text
- short debug summary

From history, the user can:

- reopen
- rerun
- copy output

### 10.3 Presets

Need:

- `Preset name`
- `Save preset`
- `Load preset`

Saved:

- all UI parameters

## 11. Architectural Requirements

The UI must be convenient for continuous debugging and tuning.

That means it should be easy to understand:

- what actually went into generation
- why a particular batch was produced
- which routing / fallback / anti-repeat rules fired

Configuration and logic should be separated so they can be changed quickly without redesigning the whole interface.

## 12. What the Backend Must Support

- gender modes: women / men / couples
- same-person identity lock
- mixed batch mode
- couple composition logic
- race presets
- direct injection of other races
- male rules from legacy + expansion
- style mode routing
- style vibe overlay
- spicy level routing
- framing planner
- lighting planner
- scene family rotation
- recent anti-repeat window
- strict / normal / loose validation
- presets storage
- history storage
- seed reproducibility

## 13. What We Intentionally Do Not Do Yet

- metadata input field
- multi-format export
- output split into multiple model blocks
- JSON export for users
- complex per-model headers

## 14. Final UI Structure

1. `Subject`
2. `Batch Logic`
3. `Style & Scene`
4. `Output & Debug`

## 15. Minimum MVP

- all main dropdowns / inputs from this spec
- Generate
- one text output block
- Copy button
- presets save/load
- history
- debug toggle
- seed auto/manual
- color highlighting of prompt segments in the UI
