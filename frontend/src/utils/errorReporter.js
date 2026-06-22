// Zero-cost in-house error reporting — posts to our own /api/observability/error.
// Fails silently; never throws.
export async function reportError(error, context = {}) {
  try {
    const API = process.env.REACT_APP_BACKEND_URL;
    if (!API) return;
    const payload = {
      message: (error && (error.message || String(error))) || "Unknown error",
      stack: (error && error.stack) || "",
      url: typeof window !== "undefined" ? window.location.href : "",
      level: "error",
      source: "frontend",
      context: context || {},
      release: process.env.REACT_APP_ENV || "development",
    };
    await fetch(`${API}/api/observability/error`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      keepalive: true,
    });
  } catch (_) {
    /* swallow — error reporting must never break the app */
  }
}

export function installGlobalErrorHandlers() {
  if (typeof window === "undefined" || window.__errReporterInstalled) return;
  window.__errReporterInstalled = true;
  window.addEventListener("error", (e) =>
    reportError(e.error || e.message, { type: "window.onerror" })
  );
  window.addEventListener("unhandledrejection", (e) =>
    reportError(e.reason, { type: "unhandledrejection" })
  );
}
