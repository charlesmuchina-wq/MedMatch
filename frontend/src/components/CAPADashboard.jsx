/**
 * CAPA (Corrective Action Preventive Action) Dashboard
 * Part of Karau Automator
 * 
 * Quality management system for investigating nonconformances
 * and implementing corrective/preventive actions
 */

import { useState, useEffect, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from "@/components/ui/dialog";
import { 
  AlertTriangle, CheckCircle, XCircle, Clock, FileText, 
  Plus, ChevronRight, Search, Filter, RefreshCw,
  Shield, Target, Zap, ClipboardCheck, TrendingUp,
  ArrowRight, CheckSquare, AlertCircle, Info
} from "lucide-react";
import axios from "axios";
import { toast } from "sonner";

const API = process.env.REACT_APP_BACKEND_URL || "";

// Status colors and labels
const statusConfig = {
  draft: { color: "bg-slate-500", label: "Draft", icon: FileText },
  investigation: { color: "bg-blue-500", label: "Investigation", icon: Search },
  containment: { color: "bg-orange-500", label: "Containment", icon: Shield },
  resolution: { color: "bg-purple-500", label: "Resolution", icon: Target },
  voe_pending: { color: "bg-yellow-500", label: "VOE Pending", icon: Clock },
  voe_in_progress: { color: "bg-cyan-500", label: "VOE In Progress", icon: ClipboardCheck },
  closed: { color: "bg-green-500", label: "Closed", icon: CheckCircle },
  cancelled: { color: "bg-red-500", label: "Cancelled", icon: XCircle }
};

const severityConfig = {
  critical: { color: "bg-red-600", textColor: "text-red-600" },
  high: { color: "bg-orange-500", textColor: "text-orange-500" },
  medium: { color: "bg-yellow-500", textColor: "text-yellow-500" },
  low: { color: "bg-blue-500", textColor: "text-blue-500" }
};

// CAPA Card Component
const CAPACard = ({ capa, onClick }) => {
  const status = statusConfig[capa.status] || statusConfig.draft;
  const severity = severityConfig[capa.severity] || severityConfig.medium;
  const StatusIcon = status.icon;

  return (
    <Card 
      className="cursor-pointer hover:shadow-lg transition-all border-l-4"
      style={{ borderLeftColor: severity.color.replace('bg-', '') }}
      onClick={() => onClick(capa)}
      data-testid={`capa-card-${capa.id}`}
    >
      <CardContent className="p-4">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <code className="text-xs bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded">
                {capa.id}
              </code>
              <Badge className={`${status.color} text-white text-xs`}>
                <StatusIcon className="w-3 h-3 mr-1" />
                {status.label}
              </Badge>
              <Badge variant="outline" className={`text-xs ${severity.textColor}`}>
                {capa.severity}
              </Badge>
            </div>
            <h4 className="font-semibold text-sm mt-2">{capa.title}</h4>
            <p className="text-xs text-slate-500 mt-1 line-clamp-2">
              {capa.problem_statement}
            </p>
          </div>
          <ChevronRight className="w-5 h-5 text-slate-400" />
        </div>
        <div className="flex items-center gap-4 mt-3 text-xs text-slate-500">
          <span>Source: {capa.source}</span>
          <span>Created: {new Date(capa.created_at).toLocaleDateString()}</span>
        </div>
      </CardContent>
    </Card>
  );
};

// Create CAPA Dialog
const CreateCAPADialog = ({ open, onClose, onCreated }) => {
  const [formData, setFormData] = useState({
    title: "",
    problem_statement: "",
    capa_type: "both",
    severity: "medium",
    source: "",
    impacted_processes: "",
    tags: ""
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!formData.title || !formData.problem_statement) {
      toast.error("Title and problem statement are required");
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/api/capa/create`, {
        ...formData,
        impacted_processes: formData.impacted_processes.split(",").map(s => s.trim()).filter(Boolean),
        tags: formData.tags.split(",").map(s => s.trim()).filter(Boolean)
      });
      toast.success(`CAPA ${response.data.capa.id} created`);
      onCreated(response.data.capa);
      onClose();
      setFormData({
        title: "",
        problem_statement: "",
        capa_type: "both",
        severity: "medium",
        source: "",
        impacted_processes: "",
        tags: ""
      });
    } catch (error) {
      toast.error("Failed to create CAPA");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Create New CAPA</DialogTitle>
          <DialogDescription>
            Initiate a Corrective Action Preventive Action for a nonconformance
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4 py-4">
          <div>
            <label className="text-sm font-medium">Title *</label>
            <Input
              placeholder="Brief title of the nonconformance"
              value={formData.title}
              onChange={(e) => setFormData({...formData, title: e.target.value})}
            />
          </div>
          
          <div>
            <label className="text-sm font-medium">Problem Statement *</label>
            <Textarea
              placeholder="Detailed description of the issue..."
              rows={4}
              value={formData.problem_statement}
              onChange={(e) => setFormData({...formData, problem_statement: e.target.value})}
            />
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium">CAPA Type</label>
              <Select 
                value={formData.capa_type} 
                onValueChange={(v) => setFormData({...formData, capa_type: v})}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="corrective">Corrective</SelectItem>
                  <SelectItem value="preventive">Preventive</SelectItem>
                  <SelectItem value="both">Both</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <label className="text-sm font-medium">Severity</label>
              <Select 
                value={formData.severity} 
                onValueChange={(v) => setFormData({...formData, severity: v})}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="critical">Critical</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="low">Low</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          
          <div>
            <label className="text-sm font-medium">Source</label>
            <Input
              placeholder="Where the issue was identified (e.g., QA, Audit, Customer)"
              value={formData.source}
              onChange={(e) => setFormData({...formData, source: e.target.value})}
            />
          </div>
          
          <div>
            <label className="text-sm font-medium">Impacted Processes (comma-separated)</label>
            <Input
              placeholder="e.g., Translation, UI Rendering, Localization"
              value={formData.impacted_processes}
              onChange={(e) => setFormData({...formData, impacted_processes: e.target.value})}
            />
          </div>
        </div>
        
        <DialogFooter>
          <Button variant="outline" onClick={onClose}>Cancel</Button>
          <Button onClick={handleSubmit} disabled={loading}>
            {loading ? "Creating..." : "Create CAPA"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

// CAPA Detail View
const CAPADetailView = ({ capa, onUpdate, onClose }) => {
  const [activeTab, setActiveTab] = useState("overview");
  const [newCause, setNewCause] = useState({ description: "", category: "", evidence: "" });
  const [loading, setLoading] = useState(false);

  const addProbableCause = async () => {
    if (!newCause.description) return;
    setLoading(true);
    try {
      await axios.post(`${API}/api/capa/${capa.id}/investigation/probable-cause`, newCause);
      toast.success("Probable cause added");
      onUpdate();
      setNewCause({ description: "", category: "", evidence: "" });
    } catch (error) {
      toast.error("Failed to add cause");
    } finally {
      setLoading(false);
    }
  };

  const eliminateCause = async (causeId) => {
    const reason = prompt("Enter reason for elimination:");
    if (!reason) return;
    try {
      await axios.put(`${API}/api/capa/${capa.id}/investigation/cause/${causeId}/eliminate`, { reason });
      toast.success("Cause eliminated");
      onUpdate();
    } catch (error) {
      toast.error("Failed to eliminate cause");
    }
  };

  const retainCause = async (causeId) => {
    const justification = prompt("Enter justification for retaining this cause:");
    if (!justification) return;
    try {
      await axios.put(`${API}/api/capa/${capa.id}/investigation/cause/${causeId}/retain`, { justification });
      toast.success("Cause retained as root cause");
      onUpdate();
    } catch (error) {
      toast.error("Failed to retain cause");
    }
  };

  const updateStatus = async (newStatus) => {
    try {
      await axios.put(`${API}/api/capa/${capa.id}/status`, { status: newStatus });
      toast.success(`Status updated to ${newStatus}`);
      onUpdate();
    } catch (error) {
      toast.error("Failed to update status");
    }
  };

  const status = statusConfig[capa.status] || statusConfig.draft;
  const StatusIcon = status.icon;

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-4xl max-h-[90vh] overflow-hidden">
        <CardHeader className="border-b">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2">
                <code className="text-sm bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded">
                  {capa.id}
                </code>
                <Badge className={`${status.color} text-white`}>
                  <StatusIcon className="w-3 h-3 mr-1" />
                  {status.label}
                </Badge>
              </div>
              <CardTitle className="mt-2">{capa.title}</CardTitle>
            </div>
            <Button variant="ghost" onClick={onClose}>×</Button>
          </div>
        </CardHeader>
        
        <div className="overflow-y-auto" style={{ maxHeight: "calc(90vh - 200px)" }}>
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="w-full justify-start border-b rounded-none px-4">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="investigation">Investigation</TabsTrigger>
              <TabsTrigger value="containment">Containment</TabsTrigger>
              <TabsTrigger value="resolution">Resolution</TabsTrigger>
              <TabsTrigger value="voe">VOE</TabsTrigger>
              <TabsTrigger value="history">History</TabsTrigger>
            </TabsList>
            
            {/* Overview Tab */}
            <TabsContent value="overview" className="p-4 space-y-4">
              <div>
                <h4 className="font-medium text-sm text-slate-500">Problem Statement</h4>
                <p className="mt-1">{capa.problem_statement}</p>
              </div>
              
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <h4 className="font-medium text-sm text-slate-500">Type</h4>
                  <p className="mt-1 capitalize">{capa.capa_type}</p>
                </div>
                <div>
                  <h4 className="font-medium text-sm text-slate-500">Severity</h4>
                  <Badge className={severityConfig[capa.severity]?.color}>{capa.severity}</Badge>
                </div>
                <div>
                  <h4 className="font-medium text-sm text-slate-500">Source</h4>
                  <p className="mt-1">{capa.source}</p>
                </div>
              </div>
              
              <div>
                <h4 className="font-medium text-sm text-slate-500">Impacted Processes</h4>
                <div className="flex gap-2 mt-1 flex-wrap">
                  {capa.impacted_processes?.map((p, i) => (
                    <Badge key={i} variant="outline">{p}</Badge>
                  ))}
                </div>
              </div>
              
              {/* Status Actions */}
              <div className="pt-4 border-t">
                <h4 className="font-medium text-sm mb-2">Update Status</h4>
                <div className="flex gap-2 flex-wrap">
                  {capa.status === "draft" && (
                    <Button size="sm" onClick={() => updateStatus("investigation")}>
                      Start Investigation
                    </Button>
                  )}
                  {capa.status === "investigation" && (
                    <Button size="sm" onClick={() => updateStatus("containment")}>
                      Move to Containment
                    </Button>
                  )}
                  {capa.status === "containment" && (
                    <>
                      <Button size="sm" onClick={() => updateStatus("resolution")}>
                        Move to Resolution
                      </Button>
                      <Button size="sm" variant="outline" onClick={() => {
                        const justification = prompt("Enter justification for closing at containment:");
                        if (justification) {
                          axios.post(`${API}/api/capa/${capa.id}/containment/close`, { justification })
                            .then(() => { toast.success("CAPA closed at containment"); onUpdate(); })
                            .catch(() => toast.error("Failed to close"));
                        }
                      }}>
                        Close at Containment
                      </Button>
                    </>
                  )}
                  {capa.status === "resolution" && (
                    <Button size="sm" onClick={() => updateStatus("voe_pending")}>
                      Move to VOE
                    </Button>
                  )}
                </div>
              </div>
            </TabsContent>
            
            {/* Investigation Tab */}
            <TabsContent value="investigation" className="p-4 space-y-4">
              <div className="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg">
                <div className="flex items-center gap-2 text-blue-700 dark:text-blue-300">
                  <Info className="w-4 h-4" />
                  <span className="text-sm font-medium">Root Cause Investigation</span>
                </div>
                <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">
                  Add probable causes, then eliminate or retain them based on evidence.
                </p>
              </div>
              
              {/* Add Probable Cause */}
              <Card>
                <CardHeader className="py-3">
                  <CardTitle className="text-sm">Add Probable Cause</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <Input
                    placeholder="Description of the probable cause..."
                    value={newCause.description}
                    onChange={(e) => setNewCause({...newCause, description: e.target.value})}
                  />
                  <div className="grid grid-cols-2 gap-3">
                    <Select 
                      value={newCause.category} 
                      onValueChange={(v) => setNewCause({...newCause, category: v})}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Category" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="technical">Technical</SelectItem>
                        <SelectItem value="process">Process</SelectItem>
                        <SelectItem value="human">Human</SelectItem>
                        <SelectItem value="environmental">Environmental</SelectItem>
                      </SelectContent>
                    </Select>
                    <Input
                      placeholder="Evidence..."
                      value={newCause.evidence}
                      onChange={(e) => setNewCause({...newCause, evidence: e.target.value})}
                    />
                  </div>
                  <Button onClick={addProbableCause} disabled={loading} size="sm">
                    <Plus className="w-4 h-4 mr-1" /> Add Cause
                  </Button>
                </CardContent>
              </Card>
              
              {/* Probable Causes */}
              {capa.investigation?.probable_causes?.length > 0 && (
                <div>
                  <h4 className="font-medium text-sm mb-2">Probable Causes</h4>
                  <div className="space-y-2">
                    {capa.investigation.probable_causes.map((cause) => (
                      <Card key={cause.id} className="border-l-4 border-l-yellow-500">
                        <CardContent className="p-3">
                          <div className="flex justify-between items-start">
                            <div>
                              <p className="text-sm">{cause.description}</p>
                              <div className="flex gap-2 mt-1">
                                <Badge variant="outline" className="text-xs">{cause.category}</Badge>
                                {cause.evidence && <span className="text-xs text-slate-500">Evidence: {cause.evidence}</span>}
                              </div>
                            </div>
                            <div className="flex gap-1">
                              <Button size="sm" variant="outline" onClick={() => eliminateCause(cause.id)}>
                                <XCircle className="w-3 h-3 mr-1" /> Eliminate
                              </Button>
                              <Button size="sm" onClick={() => retainCause(cause.id)}>
                                <CheckCircle className="w-3 h-3 mr-1" /> Retain
                              </Button>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Eliminated Causes */}
              {capa.investigation?.eliminated_causes?.length > 0 && (
                <div>
                  <h4 className="font-medium text-sm mb-2 text-slate-500">Eliminated Causes</h4>
                  <div className="space-y-2">
                    {capa.investigation.eliminated_causes.map((cause) => (
                      <Card key={cause.id} className="border-l-4 border-l-slate-300 opacity-60">
                        <CardContent className="p-3">
                          <p className="text-sm line-through">{cause.description}</p>
                          <p className="text-xs text-slate-500 mt-1">
                            Reason: {cause.elimination_reason}
                          </p>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Retained Causes (Root Causes) */}
              {capa.investigation?.retained_causes?.length > 0 && (
                <div>
                  <h4 className="font-medium text-sm mb-2 text-green-600">✓ Retained Root Causes</h4>
                  <div className="space-y-2">
                    {capa.investigation.retained_causes.map((cause) => (
                      <Card key={cause.id} className="border-l-4 border-l-green-500 bg-green-50 dark:bg-green-900/20">
                        <CardContent className="p-3">
                          <p className="text-sm font-medium">{cause.description}</p>
                          <p className="text-xs text-green-700 dark:text-green-400 mt-1">
                            Justification: {cause.retention_justification}
                          </p>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              )}
            </TabsContent>
            
            {/* Containment Tab */}
            <TabsContent value="containment" className="p-4">
              <div className="bg-orange-50 dark:bg-orange-900/20 p-3 rounded-lg mb-4">
                <div className="flex items-center gap-2 text-orange-700 dark:text-orange-300">
                  <Shield className="w-4 h-4" />
                  <span className="text-sm font-medium">Containment Phase</span>
                </div>
                <p className="text-xs text-orange-600 dark:text-orange-400 mt-1">
                  Immediate actions to prevent further occurrence while investigating.
                </p>
              </div>
              
              <div className="space-y-4">
                {capa.containment?.actions?.map((action, i) => (
                  <Card key={action.id}>
                    <CardContent className="p-3">
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="text-sm">{action.description}</p>
                          <div className="flex gap-2 mt-1">
                            <Badge variant={action.status === "completed" ? "default" : "outline"}>
                              {action.status}
                            </Badge>
                            {action.responsible && <span className="text-xs text-slate-500">Owner: {action.responsible}</span>}
                          </div>
                        </div>
                        {action.status !== "completed" && (
                          <Button size="sm" onClick={async () => {
                            const notes = prompt("Completion notes:");
                            if (notes) {
                              await axios.put(`${API}/api/capa/${capa.id}/containment/action/${action.id}/complete`, { notes });
                              toast.success("Action completed");
                              onUpdate();
                            }
                          }}>
                            Complete
                          </Button>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))}
                
                <Button variant="outline" onClick={async () => {
                  const description = prompt("Containment action description:");
                  if (description) {
                    await axios.post(`${API}/api/capa/${capa.id}/containment/action`, { description });
                    toast.success("Containment action added");
                    onUpdate();
                  }
                }}>
                  <Plus className="w-4 h-4 mr-1" /> Add Containment Action
                </Button>
              </div>
            </TabsContent>
            
            {/* Resolution Tab */}
            <TabsContent value="resolution" className="p-4">
              <div className="bg-purple-50 dark:bg-purple-900/20 p-3 rounded-lg mb-4">
                <div className="flex items-center gap-2 text-purple-700 dark:text-purple-300">
                  <Target className="w-4 h-4" />
                  <span className="text-sm font-medium">Resolution Phase</span>
                </div>
                <p className="text-xs text-purple-600 dark:text-purple-400 mt-1">
                  Define corrective actions (fix the issue) and preventive actions (prevent recurrence).
                </p>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                {/* Corrective Actions */}
                <div>
                  <h4 className="font-medium text-sm mb-2">Corrective Actions</h4>
                  <div className="space-y-2">
                    {capa.resolution?.corrective_actions?.map((action) => (
                      <Card key={action.id} className="border-l-4 border-l-blue-500">
                        <CardContent className="p-2">
                          <p className="text-sm">{action.description}</p>
                          <Badge variant="outline" className="text-xs mt-1">{action.status}</Badge>
                        </CardContent>
                      </Card>
                    ))}
                    <Button variant="outline" size="sm" className="w-full" onClick={async () => {
                      const description = prompt("Corrective action:");
                      const howItAddresses = prompt("How does this address the problem?");
                      if (description) {
                        await axios.post(`${API}/api/capa/${capa.id}/resolution/corrective-action`, {
                          description,
                          how_it_addresses_problem: howItAddresses
                        });
                        toast.success("Corrective action added");
                        onUpdate();
                      }
                    }}>
                      <Plus className="w-3 h-3 mr-1" /> Add
                    </Button>
                  </div>
                </div>
                
                {/* Preventive Actions */}
                <div>
                  <h4 className="font-medium text-sm mb-2">Preventive Actions</h4>
                  <div className="space-y-2">
                    {capa.resolution?.preventive_actions?.map((action) => (
                      <Card key={action.id} className="border-l-4 border-l-green-500">
                        <CardContent className="p-2">
                          <p className="text-sm">{action.description}</p>
                          <Badge variant="outline" className="text-xs mt-1">{action.status}</Badge>
                        </CardContent>
                      </Card>
                    ))}
                    <Button variant="outline" size="sm" className="w-full" onClick={async () => {
                      const description = prompt("Preventive action (safeguard):");
                      const howItPrevents = prompt("How does this prevent future occurrence?");
                      if (description) {
                        await axios.post(`${API}/api/capa/${capa.id}/resolution/preventive-action`, {
                          description,
                          how_it_prevents_future: howItPrevents
                        });
                        toast.success("Preventive action added");
                        onUpdate();
                      }
                    }}>
                      <Plus className="w-3 h-3 mr-1" /> Add
                    </Button>
                  </div>
                </div>
              </div>
            </TabsContent>
            
            {/* VOE Tab */}
            <TabsContent value="voe" className="p-4">
              <div className="bg-cyan-50 dark:bg-cyan-900/20 p-3 rounded-lg mb-4">
                <div className="flex items-center gap-2 text-cyan-700 dark:text-cyan-300">
                  <ClipboardCheck className="w-4 h-4" />
                  <span className="text-sm font-medium">Verification of Effectiveness (VOE)</span>
                </div>
                <p className="text-xs text-cyan-600 dark:text-cyan-400 mt-1">
                  Verify that corrective and preventive actions were effective.
                </p>
              </div>
              
              {capa.voe?.overall_effectiveness && (
                <div className={`p-4 rounded-lg mb-4 ${
                  capa.voe.overall_effectiveness === "effective" ? "bg-green-100" :
                  capa.voe.overall_effectiveness === "partially_effective" ? "bg-yellow-100" : "bg-red-100"
                }`}>
                  <h4 className="font-medium">Overall Effectiveness: {capa.voe.overall_effectiveness}</h4>
                </div>
              )}
              
              <div className="space-y-2">
                {capa.voe?.verifications?.map((voe) => (
                  <Card key={voe.id}>
                    <CardContent className="p-3">
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="text-sm">{voe.verification_method}</p>
                          <p className="text-xs text-slate-500 mt-1">
                            Criteria: {voe.acceptance_criteria}
                          </p>
                          {voe.result && (
                            <Badge className={`mt-1 ${
                              voe.result === "pass" ? "bg-green-500" :
                              voe.result === "partial" ? "bg-yellow-500" : "bg-red-500"
                            }`}>
                              {voe.result}
                            </Badge>
                          )}
                        </div>
                        {voe.status !== "completed" && (
                          <Button size="sm" onClick={async () => {
                            const result = prompt("Result (pass/fail/partial):");
                            const evidence = prompt("Evidence:");
                            if (result && evidence) {
                              await axios.put(`${API}/api/capa/${capa.id}/voe/${voe.id}/execute`, {
                                result, evidence, notes: ""
                              });
                              toast.success("VOE executed");
                              onUpdate();
                            }
                          }}>
                            Execute
                          </Button>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))}
                
                <Button variant="outline" onClick={async () => {
                  const method = prompt("Verification method:");
                  const criteria = prompt("Acceptance criteria:");
                  if (method && criteria) {
                    await axios.post(`${API}/api/capa/${capa.id}/voe`, {
                      action_id: "general",
                      verification_method: method,
                      acceptance_criteria: criteria
                    });
                    toast.success("VOE added");
                    onUpdate();
                  }
                }}>
                  <Plus className="w-4 h-4 mr-1" /> Add Verification
                </Button>
              </div>
            </TabsContent>
            
            {/* History Tab */}
            <TabsContent value="history" className="p-4">
              <div className="space-y-2">
                {capa.history?.map((entry, i) => (
                  <div key={i} className="flex gap-3 text-sm">
                    <span className="text-slate-400 w-40 flex-shrink-0">
                      {new Date(entry.timestamp).toLocaleString()}
                    </span>
                    <div>
                      <span className="font-medium">{entry.action}</span>
                      <span className="text-slate-500 ml-2">by {entry.user}</span>
                      {entry.details && <p className="text-xs text-slate-500 mt-0.5">{entry.details}</p>}
                    </div>
                  </div>
                ))}
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </Card>
    </div>
  );
};

// Main CAPA Dashboard
const CAPADashboard = () => {
  const [capas, setCAPAs] = useState([]);
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [selectedCAPA, setSelectedCAPA] = useState(null);
  const [filter, setFilter] = useState({ status: "", search: "" });

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [capasRes, dashRes] = await Promise.all([
        axios.get(`${API}/api/capa/list`),
        axios.get(`${API}/api/capa/dashboard`)
      ]);
      setCAPAs(capasRes.data.capas);
      setDashboard(dashRes.data);
    } catch (error) {
      console.error("Failed to fetch CAPAs:", error);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchCAPADetail = async (capaId) => {
    try {
      const res = await axios.get(`${API}/api/capa/${capaId}`);
      setSelectedCAPA(res.data);
    } catch (error) {
      toast.error("Failed to load CAPA details");
    }
  };

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const filteredCAPAs = capas.filter(c => {
    if (filter.status && c.status !== filter.status) return false;
    if (filter.search && !c.title.toLowerCase().includes(filter.search.toLowerCase())) return false;
    return true;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-turquoise" />
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="capa-dashboard">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Shield className="w-6 h-6 text-turquoise" />
            CAPA System
          </h2>
          <p className="text-sm text-slate-500 mt-1">
            Corrective Action Preventive Action Management
          </p>
        </div>
        <Button onClick={() => setShowCreate(true)} className="bg-turquoise hover:bg-turquoise/90">
          <Plus className="w-4 h-4 mr-2" /> New CAPA
        </Button>
      </div>

      {/* Dashboard Stats */}
      {dashboard && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <Card className="bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-800 dark:to-slate-900">
            <CardContent className="p-4 text-center">
              <div className="text-3xl font-bold">{dashboard.total_capas}</div>
              <div className="text-xs text-slate-500">Total CAPAs</div>
            </CardContent>
          </Card>
          <Card className="bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20">
            <CardContent className="p-4 text-center">
              <div className="text-3xl font-bold text-orange-600">{dashboard.open_capas}</div>
              <div className="text-xs text-slate-500">Open</div>
            </CardContent>
          </Card>
          <Card className="bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/20">
            <CardContent className="p-4 text-center">
              <div className="text-3xl font-bold text-red-600">{dashboard.severity_distribution?.critical || 0}</div>
              <div className="text-xs text-slate-500">Critical</div>
            </CardContent>
          </Card>
          <Card className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20">
            <CardContent className="p-4 text-center">
              <div className="text-3xl font-bold text-green-600">{dashboard.status_distribution?.closed || 0}</div>
              <div className="text-xs text-slate-500">Closed</div>
            </CardContent>
          </Card>
          <Card className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20">
            <CardContent className="p-4 text-center">
              <div className="text-3xl font-bold text-blue-600">{dashboard.average_days_to_close}</div>
              <div className="text-xs text-slate-500">Avg Days</div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters */}
      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-2.5 w-4 h-4 text-slate-400" />
          <Input
            placeholder="Search CAPAs..."
            className="pl-9"
            value={filter.search}
            onChange={(e) => setFilter({...filter, search: e.target.value})}
          />
        </div>
        <Select value={filter.status || "all"} onValueChange={(v) => setFilter({...filter, status: v === "all" ? "" : v})}>
          <SelectTrigger className="w-48">
            <Filter className="w-4 h-4 mr-2" />
            <SelectValue placeholder="All Statuses" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Statuses</SelectItem>
            {Object.entries(statusConfig).map(([key, config]) => (
              <SelectItem key={key} value={key}>{config.label}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Button variant="outline" onClick={fetchData}>
          <RefreshCw className="w-4 h-4" />
        </Button>
      </div>

      {/* CAPA List */}
      <div className="space-y-3">
        {filteredCAPAs.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <Shield className="w-12 h-12 mx-auto mb-4 text-slate-300" />
              <p className="text-lg font-medium">No CAPAs found</p>
              <p className="text-slate-500">Create a new CAPA to get started</p>
            </CardContent>
          </Card>
        ) : (
          filteredCAPAs.map(capa => (
            <CAPACard 
              key={capa.id} 
              capa={capa} 
              onClick={(c) => fetchCAPADetail(c.id)}
            />
          ))
        )}
      </div>

      {/* Create Dialog */}
      <CreateCAPADialog
        open={showCreate}
        onClose={() => setShowCreate(false)}
        onCreated={(capa) => {
          setCAPAs([capa, ...capas]);
          fetchData();
        }}
      />

      {/* Detail View */}
      {selectedCAPA && (
        <CAPADetailView
          capa={selectedCAPA}
          onUpdate={() => fetchCAPADetail(selectedCAPA.id)}
          onClose={() => setSelectedCAPA(null)}
        />
      )}
    </div>
  );
};

export default CAPADashboard;
