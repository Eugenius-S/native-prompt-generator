export const request = async (url, options = {}) => {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Request failed");
  return data;
};

export const loadBootstrap = async () => request("/api/bootstrap");

export const generateRun = async (formState) =>
  request("/api/generate", {
    method: "POST",
    body: JSON.stringify({ formState }),
  });

export const savePresetRequest = async (name, formState) =>
  request("/api/presets", {
    method: "POST",
    body: JSON.stringify({ name, formState }),
  });

export const deletePresetRequest = async (id) =>
  request(`/api/presets?id=${encodeURIComponent(id)}`, { method: "DELETE" });
