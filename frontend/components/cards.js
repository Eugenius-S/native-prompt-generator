export function createCardRenderers({ esc }) {
  function promptPreviewMarkup(item) {
    if (!item?.segments) {
      return `<span>${esc(item?.prompt ?? "")}</span>`;
    }
    const characterSegment = item.segments.character ? `<span class="seg-subject">${esc(item.segments.character)}</span>.` : "";
    return `
      <span class="seg-subject">${esc(item.segments.subject)}</span>.
      ${characterSegment}
      <span class="seg-outfit">${esc(item.segments.outfit)}</span>.
      <span class="seg-pose">${esc(item.segments.pose)}</span>.
      <span class="seg-setting">${esc(item.segments.setting)}</span>.
      <span class="seg-mood">${esc(item.segments.mood)}</span>.
      <span class="seg-technical">${esc(item.segments.technical)}</span>.
    `;
  }

  return { promptPreviewMarkup };
}
