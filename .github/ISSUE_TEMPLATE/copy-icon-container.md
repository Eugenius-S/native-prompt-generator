---
name: Copy icon container (UI)
about: Standardize a circular 64×64 px container for the "Copy" icon next to each prompt
title: "UI: Circular 64×64 container for Copy icon"
labels:
  - enhancement
  - frontend
  - ui
assignees: []
---

Description
-------
The container around the "Copy" icon in the UI should be standardized: 64×64 px with the icon itself 32×32 px centered inside a circular shape. The current styling does not meet the requirements: the target area is too small / inconsistent and is not always keyboard accessible.

Where
----
- Frontend: next to each generated prompt in the `Latest prompts` list (rendered by `frontend/app.js`).

Current behavior
-----------------
- The copy icon is displayed, but the wrapper does not match the expected size / shape / accessibility.

Expected behavior
--------------------
- The clickable area is a circular 64×64 px container.
- The icon inside is 32×32 px and centered.
- On hover/focus, use a subtle background or outline for visual feedback.
- The button is keyboard accessible and has `aria-label` / `title`.

Implementation proposal
----------------------
1. Add a CSS class in `frontend/styles.css` (or the relevant stylesheet) and apply it to the wrapper element for the Copy icon.

Example CSS:

```css
.icon-copy-container {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  cursor: pointer;
  border: none;
  transition: background-color .12s ease, transform .08s ease;
}
.icon-copy-container:hover,
.icon-copy-container:focus {
  background-color: rgba(0,0,0,0.06);
}
.icon-copy-container .icon {
  width: 32px;
  height: 32px;
  pointer-events: none;
}
```

2. In the render code, replace/wrap the current icon in a button/element with the `icon-copy-container` class and add `aria-label="Copy prompt"`.

3. Tests/verification: manually verify in the UI that the click area is 64×64 px, is keyboard focusable, and does not introduce visual regressions.

Variants
--------
- On hover, use a theme variable for the background color.
- For the active state, you can add a subtle shadow.

Acceptance criteria
-----------------
- Visually: a circular 64×64 container, icon 32×32 centered.
- Click / touch target is at least 64×64 px.
- The button is keyboard accessible and has `aria-label`.
- There are no regressions in neighboring UI elements.

Note
---------
Ready to prepare a PR with the CSS fix and a small render change (`frontend/app.js`). Let me know if you want me to create the PR and which selector to use for the icon.
