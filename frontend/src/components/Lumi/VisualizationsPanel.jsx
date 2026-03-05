import { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import {
  X, Loader2, BarChart3, GitBranch, Network, RefreshCw,
  TrendingUp, Users, MessageCircle, Clock, Calendar
} from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  BarChart, Bar, LineChart, Line, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, RadarChart, Radar, PolarGrid,
  PolarAngleAxis, PolarRadiusAxis
} from 'recharts';
import { API, ESY } from './constants';

const TABS = [
  { key: 'activity', label: 'Activity', icon: BarChart3 },
  { key: 'timeline', label: 'Timeline', icon: GitBranch },
  { key: 'graph', label: 'Knowledge', icon: Network },
];

const CHART_COLORS = [ESY.turquoise, ESY.pink, ESY.deepRed, '#6C5CE7', '#00B894', '#FDCB6E', '#E17055'];

export const VisualizationsPanel = ({ isOpen, onClose, token }) => {
  const [tab, setTab] = useState('activity');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/lumi/analytics/visualizations?tab=${tab}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) setData(await res.json());
    } catch (e) {
      toast.error('Failed to load analytics');
    }
    setLoading(false);
  }, [token, tab]);

  useEffect(() => { if (isOpen) load(); }, [isOpen, load]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center" onClick={onClose}>
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" />
      <div className="relative bg-white rounded-2xl w-full max-w-3xl shadow-2xl border border-slate-200 overflow-hidden max-h-[88vh] flex flex-col" onClick={e => e.stopPropagation()} data-testid="visualizations-panel">

        <div className="px-6 py-5 border-b border-slate-100 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: `linear-gradient(135deg, ${ESY.turquoise}, ${ESY.pink})` }}>
              <BarChart3 className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-black text-gray-900">Visualizations</h2>
              <p className="text-xs text-gray-600 font-medium">Intelligence in Every Conversation</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={load} className="p-1.5 hover:bg-slate-100 rounded-lg" data-testid="refresh-viz">
              <RefreshCw className={`w-4 h-4 text-gray-600 ${loading ? 'animate-spin' : ''}`} />
            </button>
            <button onClick={onClose} className="p-1.5 hover:bg-slate-100 rounded-lg" data-testid="close-viz">
              <X className="w-5 h-5 text-gray-600" />
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex items-center gap-1 px-6 pt-3 flex-shrink-0">
          {TABS.map(t => (
            <button key={t.key} onClick={() => setTab(t.key)}
              className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${tab === t.key ? 'bg-slate-900 text-white' : 'text-slate-600 hover:bg-slate-100'}`}
              data-testid={`viz-tab-${t.key}`}>
              <t.icon className="w-3.5 h-3.5" />{t.label}
            </button>
          ))}
        </div>

        <ScrollArea className="flex-1 min-h-0">
          <div className="p-6">
            {loading ? (
              <div className="flex items-center justify-center py-16"><Loader2 className="w-6 h-6 animate-spin text-slate-400" /></div>
            ) : tab === 'activity' ? (
              <ActivityTab data={data} />
            ) : tab === 'timeline' ? (
              <TimelineTab data={data} />
            ) : (
              <KnowledgeTab data={data} />
            )}
          </div>
        </ScrollArea>
      </div>
    </div>
  );
};

/* ============ Activity Charts Tab ============ */
const ActivityTab = ({ data }) => {
  if (!data) return null;
  const { daily_messages, channel_activity, hourly_heatmap, team_stats } = data;

  return (
    <div className="space-y-6">
      {/* KPI cards */}
      <div className="grid grid-cols-4 gap-3">
        {(team_stats || []).map((stat, i) => (
          <div key={i} className="bg-slate-50 rounded-xl p-3.5 border border-slate-100" data-testid={`kpi-${i}`}>
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">{stat.label}</p>
            <p className="text-2xl font-black text-slate-900 mt-1">{stat.value}</p>
            {stat.trend && (
              <div className="flex items-center gap-1 mt-1">
                <TrendingUp className="w-3 h-3 text-emerald-500" />
                <span className="text-[10px] font-semibold text-emerald-600">{stat.trend}</span>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Daily messages line chart */}
      <div className="bg-slate-50 rounded-xl p-4 border border-slate-100">
        <h3 className="text-sm font-bold text-slate-800 mb-3 flex items-center gap-2">
          <MessageCircle className="w-4 h-4" style={{ color: ESY.turquoise }} />Message Volume (7 days)
        </h3>
        <ResponsiveContainer width="100%" height={200}>
          <AreaChart data={daily_messages || []}>
            <defs>
              <linearGradient id="msgGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={ESY.turquoise} stopOpacity={0.3}/>
                <stop offset="95%" stopColor={ESY.turquoise} stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
            <XAxis dataKey="day" tick={{ fontSize: 10, fill: '#94A3B8' }} />
            <YAxis tick={{ fontSize: 10, fill: '#94A3B8' }} />
            <Tooltip contentStyle={{ borderRadius: 12, border: '1px solid #E2E8F0', fontSize: 12 }} />
            <Area type="monotone" dataKey="count" stroke={ESY.turquoise} fill="url(#msgGrad)" strokeWidth={2} />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Channel activity bar chart */}
      <div className="bg-slate-50 rounded-xl p-4 border border-slate-100">
        <h3 className="text-sm font-bold text-slate-800 mb-3 flex items-center gap-2">
          <BarChart3 className="w-4 h-4" style={{ color: ESY.pink }} />Channel Activity
        </h3>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={channel_activity || []} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
            <XAxis type="number" tick={{ fontSize: 10, fill: '#94A3B8' }} />
            <YAxis dataKey="name" type="category" tick={{ fontSize: 10, fill: '#64748B' }} width={100} />
            <Tooltip contentStyle={{ borderRadius: 12, border: '1px solid #E2E8F0', fontSize: 12 }} />
            <Bar dataKey="messages" radius={[0, 6, 6, 0]}>
              {(channel_activity || []).map((_, i) => <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Hourly heatmap */}
      <div className="bg-slate-50 rounded-xl p-4 border border-slate-100">
        <h3 className="text-sm font-bold text-slate-800 mb-3 flex items-center gap-2">
          <Clock className="w-4 h-4" style={{ color: ESY.deepRed }} />Activity Heatmap (24h)
        </h3>
        <div className="flex items-end gap-1 h-24">
          {(hourly_heatmap || []).map((h, i) => (
            <div key={i} className="flex-1 flex flex-col items-center gap-1">
              <div className="w-full rounded-t transition-all" style={{
                height: `${Math.max((h.count / Math.max(...(hourly_heatmap || []).map(x => x.count), 1)) * 80, 4)}px`,
                backgroundColor: h.count > 0 ? `${ESY.turquoise}${Math.min(Math.round((h.count / Math.max(...hourly_heatmap.map(x => x.count), 1)) * 255), 255).toString(16).padStart(2, '0')}` : '#E2E8F0',
              }} />
              {i % 4 === 0 && <span className="text-[8px] text-slate-400">{h.hour}</span>}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

/* ============ Project Timeline Tab ============ */
const TimelineTab = ({ data }) => {
  if (!data) return null;
  const { milestones, burndown, team_radar } = data;

  return (
    <div className="space-y-6">
      {/* Milestones */}
      <div>
        <h3 className="text-sm font-bold text-slate-800 mb-3 flex items-center gap-2">
          <GitBranch className="w-4 h-4" style={{ color: ESY.turquoise }} />Project Milestones
        </h3>
        <div className="relative">
          <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-slate-200" />
          <div className="space-y-4">
            {(milestones || []).map((m, i) => (
              <div key={i} className="flex items-start gap-4 relative" data-testid={`milestone-${i}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 z-10 ring-4 ring-white ${m.status === 'done' ? 'bg-emerald-500' : m.status === 'active' ? 'bg-blue-500' : 'bg-slate-300'}`}>
                  {m.status === 'done' ? (
                    <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" /></svg>
                  ) : m.status === 'active' ? (
                    <div className="w-2.5 h-2.5 rounded-full bg-white animate-pulse" />
                  ) : (
                    <div className="w-2 h-2 rounded-full bg-white/60" />
                  )}
                </div>
                <div className={`flex-1 p-3 rounded-xl border ${m.status === 'active' ? 'bg-blue-50 border-blue-200' : m.status === 'done' ? 'bg-emerald-50 border-emerald-200' : 'bg-slate-50 border-slate-200'}`}>
                  <div className="flex items-center justify-between">
                    <h4 className="text-sm font-bold text-slate-800">{m.title}</h4>
                    <span className={`text-[9px] font-bold px-2 py-0.5 rounded-full ${m.status === 'done' ? 'bg-emerald-100 text-emerald-700' : m.status === 'active' ? 'bg-blue-100 text-blue-700' : 'bg-slate-100 text-slate-600'}`}>
                      {m.status === 'done' ? 'Complete' : m.status === 'active' ? 'In Progress' : 'Upcoming'}
                    </span>
                  </div>
                  <p className="text-xs text-slate-500 mt-1">{m.description}</p>
                  <p className="text-[10px] text-slate-400 mt-1.5 flex items-center gap-1"><Calendar className="w-3 h-3" />{m.date}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Task burndown */}
      <div className="bg-slate-50 rounded-xl p-4 border border-slate-100">
        <h3 className="text-sm font-bold text-slate-800 mb-3">Task Burndown</h3>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={burndown || []}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
            <XAxis dataKey="day" tick={{ fontSize: 10, fill: '#94A3B8' }} />
            <YAxis tick={{ fontSize: 10, fill: '#94A3B8' }} />
            <Tooltip contentStyle={{ borderRadius: 12, border: '1px solid #E2E8F0', fontSize: 12 }} />
            <Line type="monotone" dataKey="ideal" stroke="#94A3B8" strokeDasharray="5 5" strokeWidth={1.5} dot={false} />
            <Line type="monotone" dataKey="actual" stroke={ESY.pink} strokeWidth={2.5} dot={{ r: 3, fill: ESY.pink }} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Team radar */}
      <div className="bg-slate-50 rounded-xl p-4 border border-slate-100">
        <h3 className="text-sm font-bold text-slate-800 mb-3 flex items-center gap-2">
          <Users className="w-4 h-4" style={{ color: ESY.pink }} />Team Capability Radar
        </h3>
        <ResponsiveContainer width="100%" height={250}>
          <RadarChart data={team_radar || []}>
            <PolarGrid stroke="#CBD5E1" />
            <PolarAngleAxis dataKey="skill" tick={{ fontSize: 10, fill: '#64748B' }} />
            <PolarRadiusAxis tick={{ fontSize: 9, fill: '#94A3B8' }} />
            <Radar name="Team" dataKey="score" stroke={ESY.turquoise} fill={ESY.turquoise} fillOpacity={0.2} strokeWidth={2} />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

/* ============ Knowledge Graph Tab ============ */
const KnowledgeTab = ({ data }) => {
  const [hovered, setHovered] = useState(null);
  const [selected, setSelected] = useState(null);

  if (!data) return null;
  const { nodes, connections, categories } = data;

  const CATEGORY_NAMES = ['People', 'Projects', 'Tasks', 'Channels'];

  const handleNodeClick = (node, i) => {
    setSelected(selected === i ? null : i);
  };

  const getConnectedNodes = (idx) => {
    if (idx === null) return new Set();
    const node = nodes[idx];
    const linked = new Set(node.links || []);
    // Also find nodes that link TO this node
    nodes.forEach((n, ni) => { if ((n.links || []).includes(idx)) linked.add(ni); });
    return linked;
  };

  const activeConnections = hovered !== null ? getConnectedNodes(hovered) : (selected !== null ? getConnectedNodes(selected) : null);
  const activeIdx = hovered !== null ? hovered : selected;

  return (
    <div className="space-y-6">
      {/* Category distribution + Connection strength */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-slate-50 rounded-xl p-4 border border-slate-100">
          <h3 className="text-sm font-bold text-slate-800 mb-3">Entity Distribution</h3>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={categories || []} cx="50%" cy="50%" innerRadius={50} outerRadius={80} paddingAngle={3} dataKey="count">
                {(categories || []).map((_, i) => <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />)}
              </Pie>
              <Tooltip contentStyle={{ borderRadius: 12, border: '1px solid #E2E8F0', fontSize: 12 }} />
            </PieChart>
          </ResponsiveContainer>
          <div className="flex flex-wrap gap-2 mt-2">
            {(categories || []).map((cat, i) => (
              <span key={i} className="flex items-center gap-1.5 text-[10px] font-semibold text-slate-600">
                <span className="w-2 h-2 rounded-full" style={{ backgroundColor: CHART_COLORS[i % CHART_COLORS.length] }} />
                {cat.name} ({cat.count})
              </span>
            ))}
          </div>
        </div>

        <div className="bg-slate-50 rounded-xl p-4 border border-slate-100">
          <h3 className="text-sm font-bold text-slate-800 mb-3">Connection Strength</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={connections || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
              <XAxis dataKey="type" tick={{ fontSize: 9, fill: '#94A3B8' }} />
              <YAxis tick={{ fontSize: 10, fill: '#94A3B8' }} />
              <Tooltip contentStyle={{ borderRadius: 12, border: '1px solid #E2E8F0', fontSize: 12 }} />
              <Bar dataKey="strength" radius={[6, 6, 0, 0]}>
                {(connections || []).map((_, i) => <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Interactive knowledge graph */}
      <div className="bg-slate-50 rounded-xl p-4 border border-slate-100">
        <h3 className="text-sm font-bold text-slate-800 mb-3 flex items-center gap-2">
          <Network className="w-4 h-4" style={{ color: ESY.turquoise }} />Knowledge Network
          <span className="text-[10px] text-slate-400 font-normal ml-auto">Click a node to explore connections</span>
        </h3>
        <div className="relative bg-slate-900 rounded-xl overflow-hidden" style={{ height: 340 }} data-testid="knowledge-network-viz">
          <svg width="100%" height="100%" viewBox="0 0 600 340" className="cursor-pointer" onClick={() => { setSelected(null); setHovered(null); }}>
            {/* Links */}
            {(nodes || []).map((node, ni) => {
              const links = node.links || [];
              return links.map((linkIdx, li) => {
                const target = (nodes || [])[linkIdx];
                if (!target) return null;
                const isActive = activeIdx !== null && (activeIdx === ni || activeIdx === linkIdx);
                const isDirectConnection = activeConnections && (activeConnections.has(ni) || activeConnections.has(linkIdx)) && (activeIdx === ni || activeIdx === linkIdx);
                return (
                  <line key={`link-${ni}-${li}`}
                    x1={node.x} y1={node.y} x2={target.x} y2={target.y}
                    stroke={isDirectConnection ? CHART_COLORS[node.category % CHART_COLORS.length] : activeIdx !== null ? 'rgba(255,255,255,0.03)' : 'rgba(255,255,255,0.08)'}
                    strokeWidth={isDirectConnection ? 2 : 1}
                    style={{ transition: 'all 0.3s ease' }} />
                );
              });
            })}
            {/* Nodes */}
            {(nodes || []).map((node, i) => {
              const isActive = activeIdx === i;
              const isConnected = activeConnections ? activeConnections.has(i) : false;
              const isDimmed = activeIdx !== null && !isActive && !isConnected;
              const size = node.size || 12;
              const renderSize = isActive ? size * 1.3 : isConnected ? size * 1.1 : size;
              return (
                <g key={i} transform={`translate(${node.x},${node.y})`}
                  onMouseEnter={() => setHovered(i)}
                  onMouseLeave={() => setHovered(null)}
                  onClick={(e) => { e.stopPropagation(); handleNodeClick(node, i); }}
                  style={{ cursor: 'pointer', transition: 'all 0.3s ease' }}
                  data-testid={`kg-node-${i}`}>
                  {/* Glow */}
                  {isActive && <circle r={renderSize + 8} fill={CHART_COLORS[node.category % CHART_COLORS.length]} opacity={0.15} />}
                  {/* Pulse ring for active */}
                  {isActive && <circle r={renderSize + 4} fill="none" stroke={CHART_COLORS[node.category % CHART_COLORS.length]} strokeWidth={1.5} opacity={0.4}>
                    <animate attributeName="r" from={renderSize + 2} to={renderSize + 12} dur="1.5s" repeatCount="indefinite" />
                    <animate attributeName="opacity" from="0.4" to="0" dur="1.5s" repeatCount="indefinite" />
                  </circle>}
                  {/* Node circle */}
                  <circle r={renderSize} fill={CHART_COLORS[node.category % CHART_COLORS.length]}
                    opacity={isDimmed ? 0.2 : 0.9}
                    style={{ transition: 'all 0.3s ease' }} />
                  <circle r={renderSize} fill="none"
                    stroke={isActive ? 'white' : 'rgba(255,255,255,0.2)'}
                    strokeWidth={isActive ? 2 : 1}
                    style={{ transition: 'all 0.3s ease' }} />
                  {/* Label */}
                  <text y={-(renderSize + 6)} textAnchor="middle"
                    fill={isDimmed ? 'rgba(255,255,255,0.15)' : isActive ? 'white' : 'rgba(255,255,255,0.7)'}
                    fontSize={isActive ? 11 : 9} fontWeight={isActive ? '700' : '600'}
                    style={{ transition: 'all 0.3s ease' }}>
                    {node.label}
                  </text>
                  {/* Category label on hover */}
                  {isActive && (
                    <text y={renderSize + 14} textAnchor="middle" fill="rgba(255,255,255,0.5)" fontSize={8} fontWeight="500">
                      {CATEGORY_NAMES[node.category] || 'Unknown'}
                    </text>
                  )}
                </g>
              );
            })}
          </svg>

          {/* Selected node detail card */}
          {selected !== null && nodes[selected] && (
            <div className="absolute top-3 right-3 bg-black/80 backdrop-blur-md border border-white/10 rounded-xl p-3 max-w-[180px]" data-testid="kg-detail-card">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-6 h-6 rounded-full flex items-center justify-center" style={{ backgroundColor: CHART_COLORS[nodes[selected].category % CHART_COLORS.length] }}>
                  <span className="text-[9px] text-white font-bold">{nodes[selected].label[0]}</span>
                </div>
                <div>
                  <p className="text-xs font-bold text-white">{nodes[selected].label}</p>
                  <p className="text-[9px] text-white/50">{CATEGORY_NAMES[nodes[selected].category]}</p>
                </div>
              </div>
              <div className="text-[9px] text-white/60 space-y-1">
                <p>Connections: {(nodes[selected].links || []).length}</p>
                <p className="text-white/40">Click elsewhere to deselect</p>
              </div>
            </div>
          )}

          {/* Legend */}
          <div className="absolute bottom-3 left-3 flex items-center gap-3">
            {CATEGORY_NAMES.map((label, i) => (
              <span key={i} className="flex items-center gap-1 text-[9px] font-semibold text-white/50">
                <span className="w-2 h-2 rounded-full" style={{ backgroundColor: CHART_COLORS[i] }} />{label}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
