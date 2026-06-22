import { useState, useEffect, useCallback, useRef } from "react";
import { toast } from "sonner";
import {
  Bot, ListChecks, Sparkles, Send, Plus, Trash2, Loader2,
  Wand2, CheckCircle2, Circle, Clock, Mail, KanbanSquare, Users, RefreshCw
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { apiClient } from "@/utils/apiClient";

const PRIORITY_STYLES = {
  high: "bg-rose-500/15 text-rose-300 border-rose-500/30",
  medium: "bg-amber-500/15 text-amber-300 border-amber-500/30",
  low: "bg-sky-500/15 text-sky-300 border-sky-500/30",
};
const STATUS_META = {
  open: { label: "Open", icon: Circle, color: "text-slate-400" },
  in_progress: { label: "In Progress", icon: Clock, color: "text-amber-400" },
  done: { label: "Done", icon: CheckCircle2, color: "text-emerald-400" },
};
const STATUS_FLOW = ["open", "in_progress", "done"];

const ICONS = { "list-checks": ListChecks, kanban: KanbanSquare, users: Users, bot: Bot };

const patch = (url, body) =>
  apiClient.request(url, { method: "PATCH", body: JSON.stringify(body) });

const StatCard = ({ label, value, accent, testid }) => (
  <div
    data-testid={testid}
    className="rounded-2xl border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-white/[0.03] backdrop-blur px-5 py-4"
  >
    <div className={`text-3xl font-semibold ${accent}`}>{value}</div>
    <div className="text-xs uppercase tracking-wider text-slate-400 mt-1">{label}</div>
  </div>
);

const TaskRow = ({ task, onCycle, onDelete }) => {
  const sm = STATUS_META[task.status] || STATUS_META.open;
  const SIcon = sm.icon;
  return (
    <div
      data-testid={`task-row-${task.id}`}
      className="flex items-start gap-3 rounded-xl border border-slate-200 dark:border-white/10 bg-white dark:bg-white/[0.02] p-4 hover:border-turquoise/40 transition-colors"
    >
      <button
        data-testid={`task-cycle-${task.id}`}
        onClick={() => onCycle(task)}
        title="Advance status"
        className={`mt-0.5 ${sm.color} hover:scale-110 transition-transform`}
      >
        <SIcon className="w-5 h-5" />
      </button>
      <div className="flex-1 min-w-0">
        <div className={`font-medium ${task.status === "done" ? "line-through text-slate-500" : "text-slate-900 dark:text-slate-100"}`}>
          {task.title}
        </div>
        {task.description ? (
          <div className="text-sm text-slate-400 mt-0.5">{task.description}</div>
        ) : null}
        <div className="flex flex-wrap items-center gap-2 mt-2">
          <Badge variant="outline" className={PRIORITY_STYLES[task.priority] || PRIORITY_STYLES.medium}>
            {task.priority}
          </Badge>
          {task.assignee ? (
            <span className="text-xs text-slate-400">@{task.assignee}</span>
          ) : null}
          {task.due_date ? (
            <span className="text-xs text-slate-500">due {task.due_date}</span>
          ) : null}
          {task.source_label ? (
            <span className="text-xs text-turquoise/70">{task.source_label}</span>
          ) : null}
        </div>
      </div>
      <button
        data-testid={`task-delete-${task.id}`}
        onClick={() => onDelete(task)}
        className="text-slate-500 hover:text-rose-400 transition-colors"
      >
        <Trash2 className="w-4 h-4" />
      </button>
    </div>
  );
};

export default function AgentsPage() {
  const [tasks, setTasks] = useState([]);
  const [stats, setStats] = useState({ total: 0, open: 0, in_progress: 0, done: 0, completion_rate: 0 });
  const [defs, setDefs] = useState({ templates: [], custom: [] });
  const [loading, setLoading] = useState(true);

  // create task
  const [newTitle, setNewTitle] = useState("");
  const [newPriority, setNewPriority] = useState("medium");
  const [newAssignee, setNewAssignee] = useState("");

  // extraction
  const [transcript, setTranscript] = useState("");
  const [sourceLabel, setSourceLabel] = useState("");
  const [extracting, setExtracting] = useState(false);

  // chat
  const [agentId, setAgentId] = useState("tpl_worklist_manager");
  const [chatInput, setChatInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [sending, setSending] = useState(false);
  const chatEndRef = useRef(null);

  // custom agent
  const [caName, setCaName] = useState("");
  const [caDesc, setCaDesc] = useState("");
  const [caPrompt, setCaPrompt] = useState("");
  const [creatingAgent, setCreatingAgent] = useState(false);

  const refresh = useCallback(async () => {
    try {
      const [t, s, d] = await Promise.all([
        apiClient.get("/api/agents/tasks", {}, { skipCache: true }),
        apiClient.get("/api/agents/tasks-stats", {}, { skipCache: true }),
        apiClient.get("/api/agents/definitions", {}, { skipCache: true }),
      ]);
      setTasks(t.data?.tasks || []);
      setStats(s.data || {});
      setDefs(d.data || { templates: [], custom: [] });
    } catch (e) {
      toast.error("Failed to load agents data");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { refresh(); }, [refresh]);
  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  const createTask = async () => {
    if (!newTitle.trim()) return toast.error("Enter a task title");
    try {
      await apiClient.post("/api/agents/tasks", {
        title: newTitle.trim(), priority: newPriority, assignee: newAssignee.trim(),
      });
      setNewTitle(""); setNewAssignee(""); setNewPriority("medium");
      toast.success("Task created");
      refresh();
    } catch { toast.error("Could not create task"); }
  };

  const cycleStatus = async (task) => {
    const next = STATUS_FLOW[(STATUS_FLOW.indexOf(task.status) + 1) % STATUS_FLOW.length];
    setTasks((prev) => prev.map((t) => (t.id === task.id ? { ...t, status: next } : t)));
    try { await patch(`/api/agents/tasks/${task.id}`, { status: next }); refresh(); }
    catch { toast.error("Update failed"); refresh(); }
  };

  const deleteTask = async (task) => {
    setTasks((prev) => prev.filter((t) => t.id !== task.id));
    try { await apiClient.delete(`/api/agents/tasks/${task.id}`); refresh(); }
    catch { toast.error("Delete failed"); refresh(); }
  };

  const extract = async () => {
    if (transcript.trim().length < 20) return toast.error("Paste a longer transcript");
    setExtracting(true);
    try {
      const r = await apiClient.post("/api/agents/extract-worklist", {
        transcript: transcript.trim(), source_label: sourceLabel.trim() || "Meeting",
      });
      toast.success(`Extracted ${r.data?.extracted ?? 0} task(s)`);
      setTranscript("");
      refresh();
    } catch { toast.error("Extraction failed"); }
    finally { setExtracting(false); }
  };

  const sendMessage = async () => {
    const msg = chatInput.trim();
    if (!msg) return;
    setChatInput("");
    setMessages((prev) => [...prev, { role: "user", text: msg }]);
    setSending(true);
    try {
      const r = await apiClient.post("/api/agents/chat", {
        message: msg, agent_id: agentId, session_id: sessionId,
      });
      const d = r.data || {};
      setSessionId(d.session_id);
      setMessages((prev) => [...prev, { role: "agent", text: d.reply, actions: d.actions || [] }]);
      if ((d.actions || []).length) refresh();
    } catch {
      setMessages((prev) => [...prev, { role: "agent", text: "Sorry, I hit an error. Try again." }]);
    } finally { setSending(false); }
  };

  const createAgent = async () => {
    if (!caName.trim() || !caPrompt.trim()) return toast.error("Name and instructions are required");
    setCreatingAgent(true);
    try {
      await apiClient.post("/api/agents/definitions", {
        name: caName.trim(), description: caDesc.trim(), system_prompt: caPrompt.trim(),
      });
      setCaName(""); setCaDesc(""); setCaPrompt("");
      toast.success("Agent created");
      refresh();
    } catch { toast.error("Could not create agent"); }
    finally { setCreatingAgent(false); }
  };

  const deleteAgent = async (id) => {
    try { await apiClient.delete(`/api/agents/definitions/${id}`); toast.success("Agent deleted"); refresh(); }
    catch { toast.error("Delete failed"); }
  };

  const allAgents = [...(defs.templates || []), ...(defs.custom || [])];

  return (
    <div className="min-h-screen text-slate-900 dark:text-slate-100" data-testid="agents-page">
      <div className="max-w-6xl mx-auto px-5 py-8">
        {/* Header */}
        <div className="flex items-center gap-3 mb-2">
          <div className="rounded-2xl bg-gradient-to-br from-turquoise to-cyan-600 p-2.5 shadow-lg shadow-turquoise/20">
            <Bot className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-semibold tracking-tight">Managed Agents</h1>
            <p className="text-sm text-slate-400">Claude-powered worklists & automation from your meetings</p>
          </div>
          <Button
            variant="ghost" size="sm" className="ml-auto text-slate-400"
            onClick={refresh} data-testid="agents-refresh-btn"
          >
            <RefreshCw className="w-4 h-4 mr-1" /> Refresh
          </Button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 my-6">
          <StatCard testid="stat-open" label="Open" value={stats.open || 0} accent="text-slate-700 dark:text-slate-200" />
          <StatCard testid="stat-progress" label="In Progress" value={stats.in_progress || 0} accent="text-amber-300" />
          <StatCard testid="stat-done" label="Done" value={stats.done || 0} accent="text-emerald-300" />
          <StatCard testid="stat-rate" label="Completion" value={`${stats.completion_rate || 0}%`} accent="text-turquoise" />
        </div>

        <Tabs defaultValue="worklist">
          <TabsList className="bg-slate-50 dark:bg-white/[0.03] border border-slate-200 dark:border-white/10" data-testid="agents-tabs">
            <TabsTrigger value="worklist" data-testid="tab-worklist"><ListChecks className="w-4 h-4 mr-1.5" />Worklist</TabsTrigger>
            <TabsTrigger value="extract" data-testid="tab-extract"><Wand2 className="w-4 h-4 mr-1.5" />Extract</TabsTrigger>
            <TabsTrigger value="chat" data-testid="tab-chat"><Sparkles className="w-4 h-4 mr-1.5" />Agent</TabsTrigger>
            <TabsTrigger value="agents" data-testid="tab-agents"><Bot className="w-4 h-4 mr-1.5" />Agents</TabsTrigger>
          </TabsList>

          {/* WORKLIST */}
          <TabsContent value="worklist" className="mt-5">
            <Card className="border-slate-200 dark:border-white/10 bg-white dark:bg-white/[0.02] mb-4">
              <CardContent className="p-4 flex flex-col md:flex-row gap-3">
                <Input
                  data-testid="new-task-title"
                  placeholder="New task title…"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && createTask()}
                  className="flex-1 bg-transparent border-slate-300 dark:border-white/15"
                />
                <Input
                  data-testid="new-task-assignee"
                  placeholder="Assignee"
                  value={newAssignee}
                  onChange={(e) => setNewAssignee(e.target.value)}
                  className="md:w-40 bg-transparent border-slate-300 dark:border-white/15"
                />
                <Select value={newPriority} onValueChange={setNewPriority}>
                  <SelectTrigger className="md:w-36 bg-transparent border-slate-300 dark:border-white/15" data-testid="new-task-priority">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Low</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                  </SelectContent>
                </Select>
                <Button onClick={createTask} className="bg-turquoise hover:bg-turquoise/90 text-white" data-testid="create-task-btn">
                  <Plus className="w-4 h-4 mr-1" /> Add
                </Button>
              </CardContent>
            </Card>

            {loading ? (
              <div className="flex justify-center py-12"><Loader2 className="w-6 h-6 animate-spin text-turquoise" /></div>
            ) : tasks.length === 0 ? (
              <div className="text-center py-12 text-slate-500" data-testid="worklist-empty">
                No tasks yet — add one above or extract from a transcript.
              </div>
            ) : (
              <div className="space-y-2" data-testid="worklist-list">
                {tasks.map((t) => (
                  <TaskRow key={t.id} task={t} onCycle={cycleStatus} onDelete={deleteTask} />
                ))}
              </div>
            )}
          </TabsContent>

          {/* EXTRACT */}
          <TabsContent value="extract" className="mt-5">
            <Card className="border-slate-200 dark:border-white/10 bg-white dark:bg-white/[0.02]">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2"><Wand2 className="w-5 h-5 text-turquoise" />Extract worklist from transcript</CardTitle>
                <CardDescription>Paste a meeting transcript — Claude pulls out owner-assigned action items.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <Input
                  data-testid="extract-label"
                  placeholder="Source label (e.g. Q3 Planning Sync)"
                  value={sourceLabel}
                  onChange={(e) => setSourceLabel(e.target.value)}
                  className="bg-transparent border-slate-300 dark:border-white/15"
                />
                <Textarea
                  data-testid="extract-transcript"
                  placeholder="Paste the meeting transcript here…"
                  value={transcript}
                  onChange={(e) => setTranscript(e.target.value)}
                  className="min-h-[200px] bg-transparent border-slate-300 dark:border-white/15"
                />
                <Button onClick={extract} disabled={extracting} className="bg-turquoise hover:bg-turquoise/90 text-white" data-testid="extract-btn">
                  {extracting ? <Loader2 className="w-4 h-4 mr-1 animate-spin" /> : <Sparkles className="w-4 h-4 mr-1" />}
                  Extract worklist
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          {/* CHAT */}
          <TabsContent value="chat" className="mt-5">
            <Card className="border-slate-200 dark:border-white/10 bg-white dark:bg-white/[0.02]">
              <CardHeader className="pb-3">
                <div className="flex items-center gap-3">
                  <CardTitle className="text-lg">Chat with an agent</CardTitle>
                  <Select value={agentId} onValueChange={(v) => { setAgentId(v); setMessages([]); setSessionId(null); }}>
                    <SelectTrigger className="w-64 bg-transparent border-slate-300 dark:border-white/15 ml-auto" data-testid="chat-agent-select">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {allAgents.map((a) => (
                        <SelectItem key={a.id} value={a.id}>{a.name}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </CardHeader>
              <CardContent>
                <div className="h-[340px] overflow-y-auto space-y-3 pr-1 mb-3" data-testid="chat-messages">
                  {messages.length === 0 ? (
                    <div className="text-sm text-slate-500 text-center pt-12">
                      Try: “Create a high priority task to review the contract, then list my open tasks.”
                    </div>
                  ) : messages.map((m, i) => (
                    <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                      <div className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm whitespace-pre-wrap ${
                        m.role === "user" ? "bg-turquoise text-white" : "bg-slate-100 dark:bg-white/[0.05] border border-slate-200 dark:border-white/10 text-slate-900 dark:text-slate-100"}`}>
                        {m.text}
                        {m.actions && m.actions.length > 0 && (
                          <div className="mt-2 flex flex-wrap gap-1.5">
                            {m.actions.map((a, j) => (
                              <span key={j} className="inline-flex items-center gap-1 text-[11px] rounded-full bg-black/30 px-2 py-0.5 text-turquoise">
                                {a.tool === "send_followup_email" ? <Mail className="w-3 h-3" /> : <CheckCircle2 className="w-3 h-3" />}
                                {a.tool}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                  {sending && (
                    <div className="flex justify-start"><div className="rounded-2xl px-4 py-2.5 bg-slate-100 dark:bg-white/[0.05] border border-slate-200 dark:border-white/10">
                      <Loader2 className="w-4 h-4 animate-spin text-turquoise" /></div></div>
                  )}
                  <div ref={chatEndRef} />
                </div>
                <div className="flex gap-2">
                  <Input
                    data-testid="chat-input"
                    placeholder="Ask the agent to do something…"
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && !sending && sendMessage()}
                    className="bg-transparent border-slate-300 dark:border-white/15"
                  />
                  <Button onClick={sendMessage} disabled={sending} className="bg-turquoise hover:bg-turquoise/90 text-white" data-testid="chat-send-btn">
                    <Send className="w-4 h-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* AGENTS */}
          <TabsContent value="agents" className="mt-5 space-y-5">
            <div className="grid md:grid-cols-2 gap-3">
              {allAgents.map((a) => {
                const Icon = ICONS[a.icon] || Bot;
                return (
                  <div key={a.id} data-testid={`agent-card-${a.id}`} className="rounded-2xl border border-slate-200 dark:border-white/10 bg-white dark:bg-white/[0.02] p-4 flex gap-3">
                    <div className="rounded-xl bg-turquoise/15 p-2 h-fit"><Icon className="w-5 h-5 text-turquoise" /></div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{a.name}</span>
                        {a.is_template
                          ? <Badge variant="outline" className="text-[10px] border-slate-300 dark:border-white/15 text-slate-400">Template</Badge>
                          : <Badge variant="outline" className="text-[10px] border-turquoise/30 text-turquoise">Custom</Badge>}
                      </div>
                      <p className="text-sm text-slate-400 mt-1">{a.description}</p>
                    </div>
                    {!a.is_template && (
                      <button data-testid={`agent-delete-${a.id}`} onClick={() => deleteAgent(a.id)} className="text-slate-500 hover:text-rose-400">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                );
              })}
            </div>

            <Card className="border-slate-200 dark:border-white/10 bg-white dark:bg-white/[0.02]">
              <CardHeader>
                <CardTitle className="text-lg">Build a custom agent</CardTitle>
                <CardDescription>Define a name and instructions — it uses the same task & email tools.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <Input data-testid="ca-name" placeholder="Agent name" value={caName} onChange={(e) => setCaName(e.target.value)} className="bg-transparent border-slate-300 dark:border-white/15" />
                <Input data-testid="ca-desc" placeholder="Short description" value={caDesc} onChange={(e) => setCaDesc(e.target.value)} className="bg-transparent border-slate-300 dark:border-white/15" />
                <Textarea data-testid="ca-prompt" placeholder="Instructions / persona (system prompt)…" value={caPrompt} onChange={(e) => setCaPrompt(e.target.value)} className="min-h-[120px] bg-transparent border-slate-300 dark:border-white/15" />
                <Button onClick={createAgent} disabled={creatingAgent} className="bg-turquoise hover:bg-turquoise/90 text-white" data-testid="ca-create-btn">
                  {creatingAgent ? <Loader2 className="w-4 h-4 mr-1 animate-spin" /> : <Plus className="w-4 h-4 mr-1" />}
                  Create agent
                </Button>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
