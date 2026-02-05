import { Clock, Zap, AlertCircle } from "lucide-react";
import { Badge } from "@/components/ui/badge";

const FreshnessBadge = ({ freshness, className = "" }) => {
  if (!freshness) {
    return null;
  }

  const { badge, is_fresh, minutes_ago } = freshness;

  // Determine styling based on freshness
  let variant = "outline";
  let Icon = Clock;
  let colorClass = "text-slate-500";

  if (is_fresh) {
    if (minutes_ago !== null && minutes_ago < 60) {
      // Very fresh - posted within the hour
      Icon = Zap;
      variant = "default";
      colorClass = "bg-green-500 text-white hover:bg-green-600";
    } else if (minutes_ago !== null && minutes_ago < 1440) {
      // Fresh - posted within 24 hours
      Icon = Clock;
      colorClass = "bg-turquoise/20 text-turquoise border-turquoise/50";
    } else {
      // Fairly fresh - within a few days
      colorClass = "bg-blue-50 text-blue-600 border-blue-200 dark:bg-blue-900/20 dark:text-blue-400";
    }
  } else {
    // Not fresh
    Icon = AlertCircle;
    colorClass = "bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400";
  }

  return (
    <Badge
      variant={variant}
      className={`flex items-center gap-1 text-[10px] px-2 py-0.5 ${colorClass} ${className}`}
      data-testid="freshness-badge"
      role="status"
      aria-label={`Job freshness: ${badge}`}
    >
      <Icon className="h-3 w-3" aria-hidden="true" />
      <span>{badge}</span>
    </Badge>
  );
};

export default FreshnessBadge;
