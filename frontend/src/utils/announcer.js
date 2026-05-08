/**
 * WCAG 4.1.3 Status Messages - Screen reader announcer utility.
 *
 * Pushes text into the singleton #toast-announcer live region so that
 * screen readers (NVDA / VoiceOver / TalkBack) announce status and error
 * messages without requiring focus to move.
 *
 * Usage:
 *   import { announce } from '@/utils/announcer';
 *   announce('Application submitted successfully');
 *   announce('Upload failed. Please retry.', 'assertive');
 */
export function announce(message, priority = "polite") {
  if (typeof window === "undefined" || typeof document === "undefined") return;
  const el = document.getElementById("toast-announcer");
  if (!el || !message) return;
  el.setAttribute("aria-live", priority === "assertive" ? "assertive" : "polite");
  // Clear first, then re-set after a tick to force re-announcement of identical messages.
  el.textContent = "";
  setTimeout(() => {
    el.textContent = String(message);
  }, 50);
}

export default announce;
