import { FlaskConical } from 'lucide-react';

/**
 * PreviewBadge — marks a feature whose backend is simulated / not yet
 * production-grade, so the meeting UI does not over-claim.
 *
 * Used on panels (Beamforming, WebXR Spatial, SLAM Tracking, 360 Multi-Focus)
 * whose data is generated telemetry rather than real hardware/sensor output.
 *
 * Accessibility: the state is conveyed by the visible text label (not color
 * alone), amber-300 on the dark panel gives high contrast, and an
 * `aria-label`/`title` carries the fuller explanation for assistive tech and
 * hover — keeping the axe/WCAG 2.2 AA gate green.
 */
export default function PreviewBadge({
  label = 'Simulated',
  title = 'Preview feature — the data shown is simulated, not from live hardware or sensors.',
  className = '',
}) {
  return (
    <span
      role="note"
      aria-label={`${label}. ${title}`}
      title={title}
      className={`inline-flex items-center gap-0.5 rounded-full border border-amber-400/30 bg-amber-400/10 px-1.5 py-0.5 text-[7px] font-semibold uppercase tracking-wide text-amber-300 ${className}`}
    >
      <FlaskConical className="w-2 h-2" aria-hidden="true" />
      {label}
    </span>
  );
}
