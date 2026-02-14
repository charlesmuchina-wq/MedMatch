/**
 * Enterprise API Management Page
 * Premium tier feature for managing API keys and webhooks
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import {
  Key, Webhook, ArrowLeft, Plus, Copy, Eye, EyeOff, Trash2,
  RefreshCw, Shield, Zap, ExternalLink, CheckCircle, XCircle,
  Clock, Activity, Code, Settings, AlertTriangle, Lock
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter
} from '../components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';
import { Checkbox } from '../components/ui/checkbox';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL;

// Available scopes for API keys
const AVAILABLE_SCOPES = [
  { id: 'read:candidates', label: 'Read Candidates', description: 'View candidate profiles' },
  { id: 'write:candidates', label: 'Write Candidates', description: 'Import/update candidates' },
  { id: 'read:applications', label: 'Read Applications', description: 'View job applications' },
  { id: 'write:applications', label: 'Write Applications', description: 'Update application status' },
  { id: 'read:jobs', label: 'Read Jobs', description: 'View job postings' },
  { id: 'write:jobs', label: 'Write Jobs', description: 'Create/update jobs' },
  { id: 'read:interviews', label: 'Read Interviews', description: 'View interview schedules' },
  { id: 'write:interviews', label: 'Write Interviews', description: 'Schedule interviews' },
  { id: 'webhooks:manage', label: 'Manage Webhooks', description: 'Create and manage webhooks' }
];

// Webhook event types
const WEBHOOK_EVENTS = [
  { id: 'application.created', label: 'Application Created', description: 'When a candidate applies' },
  { id: 'application.status_changed', label: 'Status Changed', description: 'Application status update' },
  { id: 'candidate.profile_updated', label: 'Profile Updated', description: 'Candidate updates profile' },
  { id: 'candidate.credential_verified', label: 'Credential Verified', description: 'Credential verification complete' },
  { id: 'job.posted', label: 'Job Posted', description: 'New job posting created' },
  { id: 'job.expired', label: 'Job Expired', description: 'Job posting expired' },
  { id: 'interview.scheduled', label: 'Interview Scheduled', description: 'Interview scheduled' },
  { id: 'interview.completed', label: 'Interview Completed', description: 'Interview finished' },
  { id: 'message.received', label: 'Message Received', description: 'New message from candidate' }
];

export default function EnterpriseAPIPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('api-keys');
  
  // API Keys state
  const [apiKeys, setApiKeys] = useState([]);
  const [showCreateKey, setShowCreateKey] = useState(false);
  const [newKeyData, setNewKeyData] = useState({ name: '', scopes: ['read:candidates'], expires_in_days: 365 });
  const [createdKey, setCreatedKey] = useState(null);
  const [showKey, setShowKey] = useState({});
  
  // Webhooks state
  const [webhooks, setWebhooks] = useState([]);
  const [showCreateWebhook, setShowCreateWebhook] = useState(false);
  const [newWebhookData, setNewWebhookData] = useState({ url: '', events: [], description: '' });
  const [createdWebhookSecret, setCreatedWebhookSecret] = useState(null);
  
  // ATS status
  const [atsStatus, setAtsStatus] = useState(null);

  const loadData = async () => {
    setLoading(true);
    const token = localStorage.getItem('access_token');
    const headers = { Authorization: `Bearer ${token}` };

    try {
      const [keysRes, webhooksRes, statusRes] = await Promise.all([
        axios.get(`${API}/api/enterprise/api-keys`, { headers }).catch(() => ({ data: { api_keys: [] } })),
        axios.get(`${API}/api/enterprise/webhooks`, { headers }).catch(() => ({ data: { webhooks: [] } })),
        axios.get(`${API}/api/enterprise/ats/status`, { headers }).catch(() => ({ data: null }))
      ]);

      setApiKeys(keysRes.data.api_keys || []);
      setWebhooks(webhooksRes.data.webhooks || []);
      setAtsStatus(statusRes.data);
    } catch (error) {
      console.error('Failed to load enterprise data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const createApiKey = async () => {
    const token = localStorage.getItem('access_token');
    try {
      const response = await axios.post(`${API}/api/enterprise/api-keys`, newKeyData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCreatedKey(response.data);
      toast.success('API key created successfully');
      loadData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create API key');
    }
  };

  const revokeApiKey = async (keyId) => {
    const token = localStorage.getItem('access_token');
    try {
      await axios.delete(`${API}/api/enterprise/api-keys/${keyId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('API key revoked');
      loadData();
    } catch (error) {
      toast.error('Failed to revoke API key');
    }
  };

  const rotateApiKey = async (keyId) => {
    const token = localStorage.getItem('access_token');
    try {
      const response = await axios.post(`${API}/api/enterprise/api-keys/${keyId}/rotate`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCreatedKey(response.data);
      toast.success('API key rotated successfully');
      loadData();
    } catch (error) {
      toast.error('Failed to rotate API key');
    }
  };

  const createWebhook = async () => {
    const token = localStorage.getItem('access_token');
    try {
      const response = await axios.post(`${API}/api/enterprise/webhooks`, newWebhookData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCreatedWebhookSecret(response.data.secret);
      toast.success('Webhook created successfully');
      setShowCreateWebhook(false);
      loadData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create webhook');
    }
  };

  const deleteWebhook = async (webhookId) => {
    const token = localStorage.getItem('access_token');
    try {
      await axios.delete(`${API}/api/enterprise/webhooks/${webhookId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Webhook deleted');
      loadData();
    } catch (error) {
      toast.error('Failed to delete webhook');
    }
  };

  const testWebhook = async (webhookId) => {
    const token = localStorage.getItem('access_token');
    try {
      const response = await axios.post(`${API}/api/enterprise/webhooks/${webhookId}/test`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.data.success) {
        toast.success('Test webhook delivered successfully');
      } else {
        toast.error(`Webhook test failed: ${response.data.message}`);
      }
    } catch (error) {
      toast.error('Failed to test webhook');
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]" data-testid="loading-spinner">
        <RefreshCw className="h-8 w-8 animate-spin text-turquoise" />
      </div>
    );
  }

  // Check if user has access
  if (atsStatus && !atsStatus.features?.api_access && !atsStatus.features?.webhooks) {
    return (
      <div className="container mx-auto p-6" data-testid="enterprise-upgrade-prompt">
        <Button variant="ghost" size="icon" onClick={() => navigate(-1)} className="mb-4">
          <ArrowLeft className="h-5 w-5" />
        </Button>
        
        <Card className="max-w-2xl mx-auto">
          <CardHeader className="text-center">
            <div className="mx-auto w-16 h-16 rounded-full bg-amber-100 flex items-center justify-center mb-4">
              <Lock className="h-8 w-8 text-amber-600" />
            </div>
            <CardTitle className="text-2xl">Enterprise Features</CardTitle>
            <CardDescription>
              API access, webhooks, and ATS integration require a Growth or Premium subscription
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-800">
                <Key className="h-6 w-6 text-turquoise mb-2" />
                <h3 className="font-semibold">API Keys</h3>
                <p className="text-sm text-muted-foreground">Programmatic access to candidate data</p>
                <Badge variant="outline" className="mt-2">Premium</Badge>
              </div>
              <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-800">
                <Webhook className="h-6 w-6 text-purple-500 mb-2" />
                <h3 className="font-semibold">Webhooks</h3>
                <p className="text-sm text-muted-foreground">Real-time event notifications</p>
                <Badge variant="outline" className="mt-2">Growth+</Badge>
              </div>
            </div>
            
            <Button className="w-full" onClick={() => navigate('/membership')}>
              Upgrade Your Plan
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6" data-testid="enterprise-api-page">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-3">
              <Settings className="h-8 w-8 text-turquoise" />
              Enterprise API
            </h1>
            <p className="text-muted-foreground mt-1">
              Manage API keys, webhooks, and ATS integrations
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="gap-1">
            <Zap className="h-3 w-3" />
            {atsStatus?.rate_limit || 100} req/hour
          </Badge>
          <Badge className="bg-turquoise text-white">
            {atsStatus?.tier?.replace('recruiter_', '').replace('_', ' ').toUpperCase() || 'FREE'}
          </Badge>
        </div>
      </div>

      {/* ATS Status Card */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg flex items-center gap-2">
            <Activity className="h-5 w-5 text-turquoise" />
            Integration Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="flex items-center gap-2">
              {atsStatus?.features?.api_access ? (
                <CheckCircle className="h-5 w-5 text-green-500" />
              ) : (
                <XCircle className="h-5 w-5 text-slate-300" />
              )}
              <span className="text-sm">API Access</span>
            </div>
            <div className="flex items-center gap-2">
              {atsStatus?.features?.webhooks ? (
                <CheckCircle className="h-5 w-5 text-green-500" />
              ) : (
                <XCircle className="h-5 w-5 text-slate-300" />
              )}
              <span className="text-sm">Webhooks</span>
            </div>
            <div className="flex items-center gap-2">
              {atsStatus?.features?.bulk_export ? (
                <CheckCircle className="h-5 w-5 text-green-500" />
              ) : (
                <XCircle className="h-5 w-5 text-slate-300" />
              )}
              <span className="text-sm">Bulk Export</span>
            </div>
            <div className="flex items-center gap-2">
              {atsStatus?.features?.bulk_import ? (
                <CheckCircle className="h-5 w-5 text-green-500" />
              ) : (
                <XCircle className="h-5 w-5 text-slate-300" />
              )}
              <span className="text-sm">Bulk Import</span>
            </div>
            <div className="flex items-center gap-2">
              {atsStatus?.features?.sso ? (
                <CheckCircle className="h-5 w-5 text-green-500" />
              ) : (
                <XCircle className="h-5 w-5 text-slate-300" />
              )}
              <span className="text-sm">SSO/SAML</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3 max-w-md">
          <TabsTrigger value="api-keys" className="gap-2">
            <Key className="h-4 w-4" />
            API Keys
          </TabsTrigger>
          <TabsTrigger value="webhooks" className="gap-2">
            <Webhook className="h-4 w-4" />
            Webhooks
          </TabsTrigger>
          <TabsTrigger value="docs" className="gap-2">
            <Code className="h-4 w-4" />
            Docs
          </TabsTrigger>
        </TabsList>

        {/* API Keys Tab */}
        <TabsContent value="api-keys" className="space-y-4">
          <div className="flex justify-between items-center">
            <p className="text-sm text-muted-foreground">
              {apiKeys.length} of 5 API keys used
            </p>
            <Dialog open={showCreateKey} onOpenChange={setShowCreateKey}>
              <DialogTrigger asChild>
                <Button className="gap-2" disabled={!atsStatus?.features?.api_access}>
                  <Plus className="h-4 w-4" />
                  Create API Key
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-md">
                <DialogHeader>
                  <DialogTitle>Create API Key</DialogTitle>
                  <DialogDescription>
                    Generate a new API key for programmatic access
                  </DialogDescription>
                </DialogHeader>
                
                {createdKey ? (
                  <div className="space-y-4">
                    <div className="p-4 rounded-lg bg-green-50 dark:bg-green-900/20 border border-green-200">
                      <div className="flex items-center gap-2 mb-2">
                        <CheckCircle className="h-5 w-5 text-green-500" />
                        <span className="font-semibold text-green-700 dark:text-green-300">Key Created</span>
                      </div>
                      <p className="text-sm text-muted-foreground mb-3">
                        Copy this key now. It won't be shown again.
                      </p>
                      <div className="flex items-center gap-2">
                        <code className="flex-1 p-2 bg-white dark:bg-slate-800 rounded text-xs break-all">
                          {createdKey.api_key}
                        </code>
                        <Button size="icon" variant="outline" onClick={() => copyToClipboard(createdKey.api_key)}>
                          <Copy className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                    <Button className="w-full" onClick={() => { setCreatedKey(null); setShowCreateKey(false); }}>
                      Done
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div>
                      <Label>Key Name</Label>
                      <Input
                        placeholder="e.g., Production ATS Integration"
                        value={newKeyData.name}
                        onChange={(e) => setNewKeyData({ ...newKeyData, name: e.target.value })}
                      />
                    </div>
                    
                    <div>
                      <Label className="mb-2 block">Scopes</Label>
                      <div className="space-y-2 max-h-48 overflow-y-auto">
                        {AVAILABLE_SCOPES.map((scope) => (
                          <div key={scope.id} className="flex items-center space-x-2">
                            <Checkbox
                              id={scope.id}
                              checked={newKeyData.scopes.includes(scope.id)}
                              onCheckedChange={(checked) => {
                                if (checked) {
                                  setNewKeyData({ ...newKeyData, scopes: [...newKeyData.scopes, scope.id] });
                                } else {
                                  setNewKeyData({ ...newKeyData, scopes: newKeyData.scopes.filter(s => s !== scope.id) });
                                }
                              }}
                            />
                            <label htmlFor={scope.id} className="text-sm">
                              {scope.label}
                              <span className="text-xs text-muted-foreground ml-1">({scope.description})</span>
                            </label>
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    <div>
                      <Label>Expires In</Label>
                      <Select
                        value={String(newKeyData.expires_in_days)}
                        onValueChange={(value) => setNewKeyData({ ...newKeyData, expires_in_days: parseInt(value) })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="30">30 days</SelectItem>
                          <SelectItem value="90">90 days</SelectItem>
                          <SelectItem value="365">1 year</SelectItem>
                          <SelectItem value="0">Never</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    
                    <DialogFooter>
                      <Button variant="outline" onClick={() => setShowCreateKey(false)}>Cancel</Button>
                      <Button onClick={createApiKey} disabled={!newKeyData.name || newKeyData.scopes.length === 0}>
                        Create Key
                      </Button>
                    </DialogFooter>
                  </div>
                )}
              </DialogContent>
            </Dialog>
          </div>

          {/* API Keys List */}
          <div className="space-y-3">
            {apiKeys.map((key) => (
              <Card key={key.id} data-testid={`api-key-${key.id}`}>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-lg bg-turquoise/10">
                        <Key className="h-5 w-5 text-turquoise" />
                      </div>
                      <div>
                        <h3 className="font-semibold">{key.name}</h3>
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <code>{key.key_preview}</code>
                          <span>•</span>
                          <span>{key.scopes?.length || 0} scopes</span>
                          {key.expires_at && (
                            <>
                              <span>•</span>
                              <Clock className="h-3 w-3" />
                              <span>Expires {new Date(key.expires_at).toLocaleDateString()}</span>
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="text-xs">
                        {key.usage_count || 0} uses
                      </Badge>
                      <Button size="sm" variant="outline" onClick={() => rotateApiKey(key.id)}>
                        <RefreshCw className="h-4 w-4" />
                      </Button>
                      <Button size="sm" variant="outline" className="text-red-500" onClick={() => revokeApiKey(key.id)}>
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
            
            {apiKeys.length === 0 && (
              <Card>
                <CardContent className="p-8 text-center">
                  <Key className="h-12 w-12 text-slate-300 mx-auto mb-4" />
                  <h3 className="font-semibold mb-2">No API Keys</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    Create an API key to integrate with your ATS
                  </p>
                  <Button onClick={() => setShowCreateKey(true)}>
                    <Plus className="h-4 w-4 mr-2" />
                    Create Your First Key
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        {/* Webhooks Tab */}
        <TabsContent value="webhooks" className="space-y-4">
          <div className="flex justify-between items-center">
            <p className="text-sm text-muted-foreground">
              {webhooks.length} webhooks configured
            </p>
            <Dialog open={showCreateWebhook} onOpenChange={setShowCreateWebhook}>
              <DialogTrigger asChild>
                <Button className="gap-2" disabled={!atsStatus?.features?.webhooks}>
                  <Plus className="h-4 w-4" />
                  Create Webhook
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-md">
                <DialogHeader>
                  <DialogTitle>Create Webhook</DialogTitle>
                  <DialogDescription>
                    Receive real-time notifications for events
                  </DialogDescription>
                </DialogHeader>
                
                {createdWebhookSecret ? (
                  <div className="space-y-4">
                    <div className="p-4 rounded-lg bg-green-50 dark:bg-green-900/20 border border-green-200">
                      <div className="flex items-center gap-2 mb-2">
                        <CheckCircle className="h-5 w-5 text-green-500" />
                        <span className="font-semibold text-green-700 dark:text-green-300">Webhook Created</span>
                      </div>
                      <p className="text-sm text-muted-foreground mb-3">
                        Store this secret for signature verification:
                      </p>
                      <div className="flex items-center gap-2">
                        <code className="flex-1 p-2 bg-white dark:bg-slate-800 rounded text-xs break-all">
                          {createdWebhookSecret}
                        </code>
                        <Button size="icon" variant="outline" onClick={() => copyToClipboard(createdWebhookSecret)}>
                          <Copy className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                    <Button className="w-full" onClick={() => { setCreatedWebhookSecret(null); setNewWebhookData({ url: '', events: [], description: '' }); }}>
                      Done
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div>
                      <Label>Endpoint URL</Label>
                      <Input
                        placeholder="https://your-ats.com/webhooks/medmatch"
                        value={newWebhookData.url}
                        onChange={(e) => setNewWebhookData({ ...newWebhookData, url: e.target.value })}
                      />
                    </div>
                    
                    <div>
                      <Label>Description (optional)</Label>
                      <Input
                        placeholder="e.g., Production ATS webhook"
                        value={newWebhookData.description}
                        onChange={(e) => setNewWebhookData({ ...newWebhookData, description: e.target.value })}
                      />
                    </div>
                    
                    <div>
                      <Label className="mb-2 block">Events</Label>
                      <div className="space-y-2 max-h-48 overflow-y-auto">
                        {WEBHOOK_EVENTS.map((event) => (
                          <div key={event.id} className="flex items-center space-x-2">
                            <Checkbox
                              id={event.id}
                              checked={newWebhookData.events.includes(event.id)}
                              onCheckedChange={(checked) => {
                                if (checked) {
                                  setNewWebhookData({ ...newWebhookData, events: [...newWebhookData.events, event.id] });
                                } else {
                                  setNewWebhookData({ ...newWebhookData, events: newWebhookData.events.filter(e => e !== event.id) });
                                }
                              }}
                            />
                            <label htmlFor={event.id} className="text-sm">
                              {event.label}
                              <span className="text-xs text-muted-foreground ml-1">({event.description})</span>
                            </label>
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    <DialogFooter>
                      <Button variant="outline" onClick={() => setShowCreateWebhook(false)}>Cancel</Button>
                      <Button onClick={createWebhook} disabled={!newWebhookData.url || newWebhookData.events.length === 0}>
                        Create Webhook
                      </Button>
                    </DialogFooter>
                  </div>
                )}
              </DialogContent>
            </Dialog>
          </div>

          {/* Webhooks List */}
          <div className="space-y-3">
            {webhooks.map((webhook) => (
              <Card key={webhook.id} data-testid={`webhook-${webhook.id}`}>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded-lg ${webhook.active ? 'bg-green-100' : 'bg-slate-100'}`}>
                        <Webhook className={`h-5 w-5 ${webhook.active ? 'text-green-600' : 'text-slate-400'}`} />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="font-semibold text-sm truncate max-w-xs">{webhook.url}</h3>
                          {webhook.active ? (
                            <Badge className="bg-green-100 text-green-700 text-xs">Active</Badge>
                          ) : (
                            <Badge variant="outline" className="text-xs">Inactive</Badge>
                          )}
                        </div>
                        <div className="flex items-center gap-2 text-xs text-muted-foreground mt-1">
                          <span>{webhook.events?.length || 0} events</span>
                          <span>•</span>
                          <span>{webhook.success_count || 0} delivered</span>
                          {webhook.failure_count > 0 && (
                            <>
                              <span>•</span>
                              <span className="text-red-500">{webhook.failure_count} failed</span>
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button size="sm" variant="outline" onClick={() => testWebhook(webhook.id)}>
                        Test
                      </Button>
                      <Button size="sm" variant="outline" className="text-red-500" onClick={() => deleteWebhook(webhook.id)}>
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
            
            {webhooks.length === 0 && (
              <Card>
                <CardContent className="p-8 text-center">
                  <Webhook className="h-12 w-12 text-slate-300 mx-auto mb-4" />
                  <h3 className="font-semibold mb-2">No Webhooks</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    Set up webhooks to receive real-time event notifications
                  </p>
                  <Button onClick={() => setShowCreateWebhook(true)}>
                    <Plus className="h-4 w-4 mr-2" />
                    Create Your First Webhook
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        {/* Documentation Tab */}
        <TabsContent value="docs" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Code className="h-5 w-5 text-turquoise" />
                API Documentation
              </CardTitle>
              <CardDescription>
                Integrate MedMatch-AI KARAU with your Applicant Tracking System
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h3 className="font-semibold mb-2">Authentication</h3>
                <div className="p-3 rounded-lg bg-slate-100 dark:bg-slate-800 font-mono text-sm">
                  Authorization: Bearer mm_live_xxxxx
                </div>
                <p className="text-sm text-muted-foreground mt-2">
                  Include your API key in the Authorization header for all requests.
                </p>
              </div>
              
              <div>
                <h3 className="font-semibold mb-2">Base URL</h3>
                <div className="p-3 rounded-lg bg-slate-100 dark:bg-slate-800 font-mono text-sm">
                  {API}/api
                </div>
              </div>
              
              <div>
                <h3 className="font-semibold mb-2">Endpoints</h3>
                <div className="space-y-2">
                  <div className="p-3 rounded-lg border">
                    <div className="flex items-center gap-2">
                      <Badge className="bg-green-500">GET</Badge>
                      <code className="text-sm">/api/recruiter/candidates</code>
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">List candidates matching search criteria</p>
                  </div>
                  <div className="p-3 rounded-lg border">
                    <div className="flex items-center gap-2">
                      <Badge className="bg-green-500">GET</Badge>
                      <code className="text-sm">/api/recruiter/applications</code>
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">List applications for your jobs</p>
                  </div>
                  <div className="p-3 rounded-lg border">
                    <div className="flex items-center gap-2">
                      <Badge className="bg-blue-500">POST</Badge>
                      <code className="text-sm">/api/recruiter/jobs</code>
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">Create a new job posting</p>
                  </div>
                  <div className="p-3 rounded-lg border">
                    <div className="flex items-center gap-2">
                      <Badge className="bg-amber-500">PUT</Badge>
                      <code className="text-sm">/api/recruiter/applications/{'{id}'}/status</code>
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">Update application status</p>
                  </div>
                </div>
              </div>
              
              <div>
                <h3 className="font-semibold mb-2">Webhook Signature Verification</h3>
                <p className="text-sm text-muted-foreground mb-2">
                  Verify webhook payloads using HMAC-SHA256:
                </p>
                <div className="p-3 rounded-lg bg-slate-100 dark:bg-slate-800 font-mono text-xs overflow-x-auto">
{`const crypto = require('crypto');

function verifySignature(payload, signature, secret) {
  const expected = 'sha256=' + crypto
    .createHmac('sha256', secret)
    .update(JSON.stringify(payload))
    .digest('hex');
  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(expected)
  );
}`}
                </div>
              </div>
              
              <div>
                <h3 className="font-semibold mb-2">Rate Limits</h3>
                <div className="grid grid-cols-3 gap-4">
                  <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800 text-center">
                    <p className="text-2xl font-bold">100</p>
                    <p className="text-xs text-muted-foreground">Starter (req/hr)</p>
                  </div>
                  <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800 text-center">
                    <p className="text-2xl font-bold">500</p>
                    <p className="text-xs text-muted-foreground">Growth (req/hr)</p>
                  </div>
                  <div className="p-3 rounded-lg bg-turquoise/10 text-center border border-turquoise/30">
                    <p className="text-2xl font-bold text-turquoise">2000</p>
                    <p className="text-xs text-muted-foreground">Premium (req/hr)</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
