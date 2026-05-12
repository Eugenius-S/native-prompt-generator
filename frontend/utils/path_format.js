const WINDOWS_PLATFORM_TOKENS = ["win32", "win64", "windows", "wince", "wow64"];

function runtimePlatform() {
  if (typeof navigator === "undefined") return "";
  if (typeof navigator.userAgentData?.platform === "string") {
    return navigator.userAgentData.platform.toLowerCase();
  }
  if (typeof navigator.platform === "string") {
    return navigator.platform.toLowerCase();
  }
  if (typeof navigator.userAgent === "string") {
    return navigator.userAgent.toLowerCase();
  }
  return "";
}

export function isWindowsRuntime() {
  const platform = runtimePlatform();
  return WINDOWS_PLATFORM_TOKENS.some((token) => platform.includes(token));
}

export function uiPathSeparator() {
  return isWindowsRuntime() ? "\\" : "/";
}

export function formatUiPath(path) {
  const separator = uiPathSeparator();
  return String(path ?? "").replace(/[\\/]+/g, separator);
}

export function withTrailingUiSeparator(segment) {
  return `${formatUiPath(segment)}${uiPathSeparator()}`;
}

export function joinUiPathSegments(parts) {
  if (!Array.isArray(parts) || !parts.length) return "";
  return formatUiPath(parts.filter(Boolean).join("/"));
}
