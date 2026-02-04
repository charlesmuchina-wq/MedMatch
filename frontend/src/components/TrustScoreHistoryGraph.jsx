/**
 * Trust Score History Graph Component
 * Displays trust score progression over time with interactive chart
 */
import { useState, useEffect } from "react";
import { TrendingUp, TrendingDown, Minus, Calendar, RefreshCw, ChevronDown, Award } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { toast } from "sonner";
import axios from "axios";

const API = process.env.REACT_APP_BACKEND_URL;

/**
 * Simple Line Chart using SVG
 */
const SimpleLineChart = ({ data, width = 600, height = 200 }) => {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-48 text-slate-400">
        No data available
      </div>
    );
  }

  // Extract scores and find min/max
  const scores = data.map(d => d.total_score);
  const minScore = Math.min(...scores);
  const maxScore = Math.max(...scores);
  const scoreRange = maxScore - minScore || 1;

  // Padding
  const padding = { top: 20, right: 20, bottom: 40, left: 50 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  // Calculate points
  const points = data.map((d, i) => {
    const x = padding.left + (i / (data.length - 1 || 1)) * chartWidth;
    const y = padding.top + chartHeight - ((d.total_score - minScore) / scoreRange) * chartHeight;
    return { x, y, ...d };
  });

  // Create path
  const pathD = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');
  
  // Create area path (for gradient fill)
  const areaD = `${pathD} L ${points[points.length - 1].x} ${padding.top + chartHeight} L ${padding.left} ${padding.top + chartHeight} Z`;

  // Y-axis labels
  const yLabels = [minScore, Math.round((minScore + maxScore) / 2), maxScore];

  // X-axis labels (show first, middle, and last dates)
  const xLabelIndices = data.length <= 3 
    ? data.map((_, i) => i) 
    : [0, Math.floor(data.length / 2), data.length - 1];

  return (
    <svg width="100%" viewBox={`0 0 ${width} ${height}`} className="overflow-visible">
      <defs>
        <linearGradient id="scoreGradient" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#14b8a6" stopOpacity="0.3" />
          <stop offset="100%" stopColor="#14b8a6" stopOpacity="0" />
        </linearGradient>
      </defs>

      {/* Grid lines */}
      {yLabels.map((label, i) => {
        const y = padding.top + chartHeight - ((label - minScore) / scoreRange) * chartHeight;
        return (
          <g key={i}>
            <line
              x1={padding.left}
              x2={width - padding.right}
              y1={y}
              y2={y}
              stroke="#e2e8f0"
              strokeDasharray="4 4"
            />
            <text
              x={padding.left - 10}
              y={y + 4}
              textAnchor="end"
              className="fill-slate-400 text-xs"
            >
              {label}
            </text>
          </g>
        );
      })}

      {/* Area fill */}
      <path d={areaD} fill="url(#scoreGradient)" />

      {/* Line */}
      <path
        d={pathD}
        fill="none"
        stroke="#14b8a6"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />

      {/* Data points */}
      {points.map((p, i) => (
        <g key={i}>
          <circle
            cx={p.x}
            cy={p.y}
            r="4"
            fill="#14b8a6"
            className="cursor-pointer"
          />
          <circle
            cx={p.x}
            cy={p.y}
            r="6"
            fill="#14b8a6"
            fillOpacity="0.2"
          />
        </g>
      ))}

      {/* X-axis labels */}
      {xLabelIndices.map((idx) => {
        const d = data[idx];
        const x = padding.left + (idx / (data.length - 1 || 1)) * chartWidth;
        const date = new Date(d.recorded_at);
        const label = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        return (
          <text
            key={idx}
            x={x}
            y={height - 10}
            textAnchor="middle"
            className="fill-slate-400 text-xs"
          >
            {label}
          </text>
        );
      })}
    </svg>
  );
};

/**
 * Trend Indicator
 */
const TrendIndicator = ({ trend }) => {
  if (!trend) return null;

  const { direction, change, change_percentage } = trend;

  if (direction === "stable" || change === 0) {
    return (
      <div className="flex items-center gap-1 text-slate-500">
        <Minus className="w-4 h-4" />
        <span className="text-sm">No change</span>
      </div>
    );
  }

  const isUp = direction === "up";
  const Icon = isUp ? TrendingUp : TrendingDown;
  const colorClass = isUp ? "text-emerald-500" : "text-red-500";

  return (
    <div className={`flex items-center gap-1 ${colorClass}`}>
      <Icon className="w-4 h-4" />
      <span className="text-sm font-medium">
        {isUp ? "+" : ""}{change} pts ({change_percentage > 0 ? "+" : ""}{change_percentage}%)
      </span>
    </div>
  );
};

/**
 * Main Trust Score History Graph Component
 */
const TrustScoreHistoryGraph = ({ compact = false }) => {
  const [loading, setLoading] = useState(true);
  const [historyData, setHistoryData] = useState(null);
  const [period, setPeriod] = useState(30); // Days

  useEffect(() => {
    fetchHistory();
  }, [period]);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("medmatch-token");
      const response = await axios.get(
        `${API}/api/credentials/trust-score/history?days=${period}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setHistoryData(response.data);
    } catch (err) {
      console.error("Failed to fetch trust score history:", err);
      // Don't show error toast, just silently fail
    } finally {
      setLoading(false);
    }
  };

  const periodOptions = [
    { value: 7, label: "Last 7 days" },
    { value: 30, label: "Last 30 days" },
    { value: 90, label: "Last 90 days" },
    { value: 180, label: "Last 6 months" },
    { value: 365, label: "Last year" }
  ];

  if (compact) {
    return (
      <Card className="overflow-hidden" data-testid="trust-score-history-compact">
        <CardContent className="p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-turquoise" />
              <span className="text-sm font-medium">Score Trend</span>
            </div>
            {historyData?.trend && <TrendIndicator trend={historyData.trend} />}
          </div>
          
          {loading ? (
            <div className="h-24 flex items-center justify-center">
              <RefreshCw className="w-5 h-5 animate-spin text-slate-400" />
            </div>
          ) : historyData?.history?.length > 0 ? (
            <SimpleLineChart data={historyData.history} width={300} height={80} />
          ) : (
            <div className="h-24 flex items-center justify-center text-sm text-slate-400">
              Start using the platform to track your progress!
            </div>
          )}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="overflow-hidden" data-testid="trust-score-history-graph">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Award className="w-5 h-5 text-turquoise" />
              Trust Score History
            </CardTitle>
            <CardDescription>Track your credibility progression over time</CardDescription>
          </div>
          
          <div className="flex items-center gap-2">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm">
                  <Calendar className="w-4 h-4 mr-2" />
                  {periodOptions.find(o => o.value === period)?.label}
                  <ChevronDown className="w-4 h-4 ml-2" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                {periodOptions.map((option) => (
                  <DropdownMenuItem
                    key={option.value}
                    onClick={() => setPeriod(option.value)}
                    className={period === option.value ? "bg-slate-100" : ""}
                  >
                    {option.label}
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>
            
            <Button variant="ghost" size="sm" onClick={fetchHistory}>
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        {/* Current Stats */}
        {historyData && (
          <div className="grid grid-cols-3 gap-4 mb-6 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
            <div className="text-center">
              <p className="text-2xl font-bold text-turquoise">{historyData.current_score}</p>
              <p className="text-xs text-slate-500">Current Score</p>
            </div>
            <div className="text-center">
              <Badge variant="outline" className="text-sm">
                {historyData.current_level}
              </Badge>
              <p className="text-xs text-slate-500 mt-1">Level</p>
            </div>
            <div className="text-center">
              <TrendIndicator trend={historyData.trend} />
              <p className="text-xs text-slate-500 mt-1">Trend ({period}d)</p>
            </div>
          </div>
        )}

        {/* Chart */}
        {loading ? (
          <div className="h-52 flex items-center justify-center">
            <RefreshCw className="w-8 h-8 animate-spin text-slate-400" />
          </div>
        ) : historyData?.history?.length > 0 ? (
          <div className="h-52">
            <SimpleLineChart data={historyData.history} width={600} height={200} />
          </div>
        ) : (
          <div className="h-52 flex flex-col items-center justify-center text-slate-400">
            <TrendingUp className="w-12 h-12 mb-2 opacity-50" />
            <p className="text-sm">No history data yet</p>
            <p className="text-xs">Your score will be tracked as you use the platform</p>
          </div>
        )}

        {/* Data Points Info */}
        {historyData?.data_points > 0 && (
          <p className="text-xs text-slate-400 text-center mt-4">
            Based on {historyData.data_points} data point{historyData.data_points !== 1 ? 's' : ''} over {period} days
          </p>
        )}
      </CardContent>
    </Card>
  );
};

export default TrustScoreHistoryGraph;
