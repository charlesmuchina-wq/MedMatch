/**
 * OrganizationAdmin - IT Admin panel for enterprise org management
 * Tiers, domain verification, conference rooms, branding
 */
import { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import {
  Building2, Shield, MapPin, Plus, Trash2, Edit2, Check, X,
  Monitor, Users, Crown, Sparkles, Globe, Search, ChevronDown,
  ChevronUp, Loader2, Upload
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ScrollArea } from '@/components/ui/scroll-area';

const API = process.env.REACT_APP_BACKEND_URL;

const TIER_BADGES = {
  tier_1: { label: 'Basic', color: 'bg-slate-600' },
  tier_2: { label: 'Professional', color: 'bg-blue-600' },
  tier_grande: { label: 'Grande', color: 'bg-amber-600' },
  recruiter: { label: 'Recruiter', color: 'bg-purple-600' },
  personal: { label: 'Personal', color: 'bg-slate-500' },
};

const EQUIPMENT_OPTIONS = [
  { id: 'projector', label: 'Projector' },
  { id: 'whiteboard', label: 'Whiteboard' },
  { id: 'video_conf', label: 'Video Conference' },
  { id: 'phone', label: 'Conference Phone' },
  { id: 'screen_share', label: 'Screen Share' },
  { id: 'webcam', label: 'Webcam' },
];


/**
 * EmployeesTab - Enhanced employee directory with CSV upload, LDAP, and management
 */
const EmployeesTab = ({ org, employees, employeeSearch, setEmployeeSearch, headers, onRefresh }) => {
  const [showCsvUpload, setShowCsvUpload] = useState(false);
  const [showLdapConfig, setShowLdapConfig] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);
  const [csvFile, setCsvFile] = useState(null);
  const [csvUploading, setCsvUploading] = useState(false);
  const [csvResult, setCsvResult] = useState(null);
  const [stats, setStats] = useState(null);
  const [ldapConfig, setLdapConfig] = useState(null);
  const [ldapForm, setLdapForm] = useState({
    server_url: '', bind_dn: '', bind_password: '', base_dn: '',
    user_filter: '(objectClass=person)', email_attr: 'mail',
    first_name_attr: 'givenName', last_name_attr: 'sn',
    department_attr: 'department', title_attr: 'title', enabled: true
  });
  const [ldapTesting, setLdapTesting] = useState(false);
  const [ldapSyncing, setLdapSyncing] = useState(false);
  const [newEmp, setNewEmp] = useState({ email: '', first_name: '', last_name: '', department: '', title: '' });

  // Fetch stats and LDAP config
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, ldapRes] = await Promise.all([
          fetch(`${API}/api/karau-meet/organizations/${org.org_id}/employees/stats`, { headers }),
          fetch(`${API}/api/karau-meet/organizations/${org.org_id}/ldap/config`, { headers })
        ]);
        if (statsRes.ok) setStats(await statsRes.json());
        if (ldapRes.ok) {
          const ld = await ldapRes.json();
          if (ld.configured) setLdapConfig(ld.config);
        }
      } catch {}
    };
    fetchData();
  }, [org.org_id]);

  // CSV upload
  const handleCsvUpload = async () => {
    if (!csvFile) return;
    setCsvUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', csvFile);
      const res = await fetch(`${API}/api/karau-meet/organizations/${org.org_id}/employees/csv-upload`, {
        method: 'POST',
        headers: { 'Authorization': headers['Authorization'] },
        body: formData
      });
      if (res.ok) {
        const data = await res.json();
        setCsvResult(data);
        toast.success(`Imported ${data.added} employees`);
        onRefresh();
      } else {
        const err = await res.json();
        toast.error(err.detail || 'Upload failed');
      }
    } catch { toast.error('Connection error'); }
    setCsvUploading(false);
  };

  // Add single employee
  const handleAddEmployee = async () => {
    try {
      const res = await fetch(`${API}/api/karau-meet/organizations/${org.org_id}/employees`, {
        method: 'POST', headers,
        body: JSON.stringify(newEmp)
      });
      if (res.ok) {
        toast.success('Employee added');
        setNewEmp({ email: '', first_name: '', last_name: '', department: '', title: '' });
        setShowAddForm(false);
        onRefresh();
      } else {
        const err = await res.json();
        toast.error(err.detail || 'Failed');
      }
    } catch { toast.error('Connection error'); }
  };

  // Delete employee
  const deleteEmployee = async (empId) => {
    try {
      await fetch(`${API}/api/karau-meet/organizations/${org.org_id}/employees/${empId}`, {
        method: 'DELETE', headers
      });
      toast.success('Employee removed');
      onRefresh();
    } catch { toast.error('Failed'); }
  };

  // Toggle status
  const toggleStatus = async (empId, currentStatus) => {
    const newStatus = currentStatus === 'active' ? 'inactive' : 'active';
    try {
      await fetch(`${API}/api/karau-meet/organizations/${org.org_id}/employees/${empId}/status?status=${newStatus}`, {
        method: 'PUT', headers
      });
      toast.success(`Employee ${newStatus}`);
      onRefresh();
    } catch { toast.error('Failed'); }
  };

  // Save LDAP config
  const saveLdapConfig = async () => {
    try {
      const res = await fetch(`${API}/api/karau-meet/organizations/${org.org_id}/ldap/configure`, {
        method: 'POST', headers,
        body: JSON.stringify(ldapForm)
      });
      if (res.ok) {
        toast.success('LDAP configuration saved');
        setLdapConfig(ldapForm);
        setShowLdapConfig(false);
      } else toast.error('Failed to save');
    } catch { toast.error('Connection error'); }
  };

  // Test LDAP
  const testLdap = async () => {
    setLdapTesting(true);
    try {
      const res = await fetch(`${API}/api/karau-meet/organizations/${org.org_id}/ldap/test`, {
        method: 'POST', headers
      });
      const data = await res.json();
      if (data.success) toast.success(data.message);
      else toast.error(data.message);
    } catch { toast.error('Test failed'); }
    setLdapTesting(false);
  };

  // Sync LDAP
  const syncLdap = async () => {
    setLdapSyncing(true);
    try {
      const res = await fetch(`${API}/api/karau-meet/organizations/${org.org_id}/ldap/sync`, {
        method: 'POST', headers
      });
      const data = await res.json();
      if (data.success) {
        toast.success(`Synced: ${data.added} new, ${data.updated} updated`);
        onRefresh();
      } else toast.error(data.message);
    } catch { toast.error('Sync failed'); }
    setLdapSyncing(false);
  };

  return (
    <div className="space-y-4" data-testid="org-employees">
      {/* Stats bar */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          <div className="bg-slate-900 rounded-lg p-2.5 text-center">
            <p className="text-lg font-bold text-white">{stats.active}</p>
            <p className="text-[10px] text-slate-400">Active</p>
          </div>
          <div className="bg-slate-900 rounded-lg p-2.5 text-center">
            <p className="text-lg font-bold text-slate-400">{stats.inactive}</p>
            <p className="text-[10px] text-slate-400">Inactive</p>
          </div>
          <div className="bg-slate-900 rounded-lg p-2.5 text-center">
            <p className="text-lg font-bold text-white">{stats.departments?.length || 0}</p>
            <p className="text-[10px] text-slate-400">Departments</p>
          </div>
          <div className="bg-slate-900 rounded-lg p-2.5 text-center">
            <p className="text-lg font-bold text-white">{Object.values(stats.sources || {}).reduce((a, b) => a + b, 0)}</p>
            <p className="text-[10px] text-slate-400">Total Records</p>
          </div>
        </div>
      )}

      {/* Action buttons */}
      <div className="flex flex-wrap items-center gap-2">
        <Button size="sm" variant="outline" className="h-8 text-xs border-slate-600 text-slate-300" onClick={() => setShowAddForm(!showAddForm)} data-testid="add-employee-btn">
          <Plus className="w-3 h-3 mr-1" /> Add Employee
        </Button>
        <Button size="sm" variant="outline" className="h-8 text-xs border-[#5b5fc7] text-[#5b5fc7]" onClick={() => setShowCsvUpload(!showCsvUpload)} data-testid="csv-upload-btn">
          <Upload className="w-3 h-3 mr-1" /> CSV Import
        </Button>
        <Button size="sm" variant="outline" className="h-8 text-xs border-amber-500 text-amber-400" onClick={() => setShowLdapConfig(!showLdapConfig)} data-testid="ldap-config-btn">
          <Globe className="w-3 h-3 mr-1" /> LDAP / AD
        </Button>
        {ldapConfig && (
          <>
            <Button size="sm" className="h-8 text-xs bg-amber-600 text-white" onClick={testLdap} disabled={ldapTesting}>
              {ldapTesting ? <Loader2 className="w-3 h-3 animate-spin mr-1" /> : null} Test
            </Button>
            <Button size="sm" className="h-8 text-xs bg-emerald-600 text-white" onClick={syncLdap} disabled={ldapSyncing} data-testid="ldap-sync-btn">
              {ldapSyncing ? <Loader2 className="w-3 h-3 animate-spin mr-1" /> : null} Sync Now
            </Button>
          </>
        )}
      </div>

      {/* Add single employee form */}
      {showAddForm && (
        <div className="bg-slate-900 rounded-lg p-3 border border-slate-700 space-y-2" data-testid="add-employee-form">
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
            <Input value={newEmp.email} onChange={e => setNewEmp({...newEmp, email: e.target.value})} placeholder="Email" className="bg-slate-800 border-slate-600 text-white text-sm h-8" />
            <Input value={newEmp.first_name} onChange={e => setNewEmp({...newEmp, first_name: e.target.value})} placeholder="First Name" className="bg-slate-800 border-slate-600 text-white text-sm h-8" />
            <Input value={newEmp.last_name} onChange={e => setNewEmp({...newEmp, last_name: e.target.value})} placeholder="Last Name" className="bg-slate-800 border-slate-600 text-white text-sm h-8" />
            <Input value={newEmp.department} onChange={e => setNewEmp({...newEmp, department: e.target.value})} placeholder="Department" className="bg-slate-800 border-slate-600 text-white text-sm h-8" />
            <Input value={newEmp.title} onChange={e => setNewEmp({...newEmp, title: e.target.value})} placeholder="Title" className="bg-slate-800 border-slate-600 text-white text-sm h-8" />
            <Button size="sm" className="h-8 bg-[#5b5fc7] text-white" onClick={handleAddEmployee} disabled={!newEmp.email}>Add</Button>
          </div>
        </div>
      )}

      {/* CSV upload */}
      {showCsvUpload && (
        <div className="bg-slate-900 rounded-lg p-4 border border-dashed border-slate-600 space-y-3" data-testid="csv-upload-area">
          <div className="text-center">
            <Upload className="w-6 h-6 text-slate-400 mx-auto mb-1" />
            <p className="text-xs text-slate-400">Upload CSV with columns: email, first_name, last_name, department, title</p>
          </div>
          <input
            type="file"
            accept=".csv"
            onChange={e => setCsvFile(e.target.files[0])}
            className="block w-full text-xs text-slate-400 file:mr-3 file:py-1.5 file:px-3 file:rounded file:border-0 file:text-xs file:bg-[#5b5fc7] file:text-white cursor-pointer"
            data-testid="csv-file-input"
          />
          {csvFile && (
            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-300">{csvFile.name} ({Math.round(csvFile.size / 1024)}KB)</span>
              <Button size="sm" className="h-7 bg-[#5b5fc7] text-white text-xs" onClick={handleCsvUpload} disabled={csvUploading}>
                {csvUploading ? <Loader2 className="w-3 h-3 animate-spin mr-1" /> : null} Import
              </Button>
            </div>
          )}
          {csvResult && (
            <div className="bg-slate-800 rounded p-2 text-xs space-y-1">
              <p className="text-emerald-400">Added: {csvResult.added} employees</p>
              {csvResult.error_count > 0 && <p className="text-amber-400">Errors: {csvResult.error_count}</p>}
              {csvResult.detected_columns && (
                <p className="text-slate-500">Columns detected: {Object.keys(csvResult.detected_columns).join(', ')}</p>
              )}
            </div>
          )}
        </div>
      )}

      {/* LDAP Configuration */}
      {showLdapConfig && (
        <div className="bg-slate-900 rounded-lg p-4 border border-amber-500/30 space-y-3" data-testid="ldap-config-form">
          <h4 className="text-sm font-medium text-amber-400 flex items-center gap-1"><Globe className="w-4 h-4" /> Active Directory / LDAP</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            <div>
              <Label className="text-[10px] text-slate-400">Server URL</Label>
              <Input value={ldapForm.server_url} onChange={e => setLdapForm({...ldapForm, server_url: e.target.value})} placeholder="ldap://ad.company.com:389" className="bg-slate-800 border-slate-600 text-white text-sm h-8" />
            </div>
            <div>
              <Label className="text-[10px] text-slate-400">Bind DN</Label>
              <Input value={ldapForm.bind_dn} onChange={e => setLdapForm({...ldapForm, bind_dn: e.target.value})} placeholder="cn=admin,dc=company,dc=com" className="bg-slate-800 border-slate-600 text-white text-sm h-8" />
            </div>
            <div>
              <Label className="text-[10px] text-slate-400">Bind Password</Label>
              <Input type="password" value={ldapForm.bind_password} onChange={e => setLdapForm({...ldapForm, bind_password: e.target.value})} className="bg-slate-800 border-slate-600 text-white text-sm h-8" />
            </div>
            <div>
              <Label className="text-[10px] text-slate-400">Base DN</Label>
              <Input value={ldapForm.base_dn} onChange={e => setLdapForm({...ldapForm, base_dn: e.target.value})} placeholder="ou=users,dc=company,dc=com" className="bg-slate-800 border-slate-600 text-white text-sm h-8" />
            </div>
            <div>
              <Label className="text-[10px] text-slate-400">User Filter</Label>
              <Input value={ldapForm.user_filter} onChange={e => setLdapForm({...ldapForm, user_filter: e.target.value})} className="bg-slate-800 border-slate-600 text-white text-sm h-8" />
            </div>
            <div>
              <Label className="text-[10px] text-slate-400">Email Attribute</Label>
              <Input value={ldapForm.email_attr} onChange={e => setLdapForm({...ldapForm, email_attr: e.target.value})} className="bg-slate-800 border-slate-600 text-white text-sm h-8" />
            </div>
          </div>
          <div className="flex gap-2 justify-end">
            <Button variant="outline" size="sm" className="border-slate-600 text-slate-300 text-xs" onClick={() => setShowLdapConfig(false)}>Cancel</Button>
            <Button size="sm" className="bg-amber-600 text-white text-xs" onClick={saveLdapConfig} disabled={!ldapForm.server_url}>Save Configuration</Button>
          </div>
          {ldapConfig?.last_sync && (
            <p className="text-[10px] text-slate-500">Last sync: {new Date(ldapConfig.last_sync).toLocaleString()}</p>
          )}
        </div>
      )}

      {/* Search bar */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
        <Input
          value={employeeSearch}
          onChange={e => setEmployeeSearch(e.target.value)}
          placeholder="Search by last name..."
          className="pl-9 bg-slate-900 border-slate-600 text-white"
          data-testid="employee-search"
        />
      </div>

      {/* Employee list */}
      <div className="space-y-1.5">
        {employees.map(emp => (
          <div key={emp.employee_id} className="flex items-center justify-between bg-slate-900 rounded-lg px-3 py-2 group" data-testid={`emp-${emp.employee_id}`}>
            <div className="flex items-center gap-2 min-w-0">
              <div className={`w-2 h-2 rounded-full flex-shrink-0 ${emp.status === 'active' ? 'bg-emerald-500' : 'bg-slate-500'}`} />
              <div className="min-w-0">
                <p className="text-sm text-white truncate">{emp.first_name} {emp.last_name}</p>
                <div className="flex items-center gap-2 text-xs text-slate-400">
                  <span className="truncate">{emp.email}</span>
                  {emp.department && <span>- {emp.department}</span>}
                  {emp.source === 'ldap_sync' && <Badge className="text-[8px] bg-amber-600/30 text-amber-400 px-1">LDAP</Badge>}
                  {emp.source === 'csv_import' && <Badge className="text-[8px] bg-blue-600/30 text-blue-400 px-1">CSV</Badge>}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
              <Badge className="text-[10px] bg-slate-700">{emp.title || 'Employee'}</Badge>
              <Button variant="ghost" size="sm" className="h-6 w-6 p-0 text-slate-500 hover:text-amber-400" onClick={() => toggleStatus(emp.employee_id, emp.status)} title={emp.status === 'active' ? 'Deactivate' : 'Activate'}>
                {emp.status === 'active' ? <Check className="w-3 h-3" /> : <X className="w-3 h-3" />}
              </Button>
              <Button variant="ghost" size="sm" className="h-6 w-6 p-0 text-slate-500 hover:text-red-400" onClick={() => deleteEmployee(emp.employee_id)}>
                <Trash2 className="w-3 h-3" />
              </Button>
            </div>
          </div>
        ))}
        {employees.length === 0 && (
          <p className="text-slate-500 text-sm text-center py-6">
            {employeeSearch ? 'No matches found' : 'No employees added yet. Use CSV import or add manually.'}
          </p>
        )}
      </div>

      {/* Department breakdown */}
      {stats?.departments?.length > 0 && (
        <div className="bg-slate-900 rounded-lg p-3 border border-slate-700">
          <h4 className="text-xs text-slate-400 mb-2">Departments</h4>
          <div className="flex flex-wrap gap-1.5">
            {stats.departments.map(d => (
              <Badge key={d.department} className="bg-slate-800 text-slate-300 text-[10px]">
                {d.department} ({d.count})
              </Badge>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

const OrganizationAdmin = ({ user }) => {
  const [orgs, setOrgs] = useState([]);
  const [selectedOrg, setSelectedOrg] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  // Create org form
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newOrg, setNewOrg] = useState({ name: '', email_domains: '', tier: 'tier_1', logo_url: '', watermark_text: '', primary_color: '#5b5fc7' });

  // Room form
  const [showRoomForm, setShowRoomForm] = useState(false);
  const [newRoom, setNewRoom] = useState({ name: '', building: '', floor: '', capacity: 10, equipment: [], location_type: 'physical', address: '' });

  // Employee search
  const [employeeSearch, setEmployeeSearch] = useState('');
  const [employees, setEmployees] = useState([]);

  const token = localStorage.getItem('token');
  const headers = { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` };

  // Fetch orgs
  const fetchOrgs = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/karau-meet/organizations`, { headers });
      if (res.ok) {
        const data = await res.json();
        setOrgs(data.organizations || []);
        if (data.organizations?.length > 0 && !selectedOrg) {
          setSelectedOrg(data.organizations[0]);
        }
      }
    } catch {
      toast.error('Failed to load organizations');
    }
    setLoading(false);
  }, []);

  useEffect(() => { fetchOrgs(); }, [fetchOrgs]);

  // Create org
  const handleCreateOrg = async () => {
    try {
      const res = await fetch(`${API}/api/karau-meet/organizations`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          ...newOrg,
          email_domains: newOrg.email_domains.split(',').map(d => d.trim()).filter(Boolean)
        })
      });
      if (res.ok) {
        const org = await res.json();
        setOrgs(prev => [...prev, org]);
        setSelectedOrg(org);
        setShowCreateForm(false);
        setNewOrg({ name: '', email_domains: '', tier: 'tier_1', logo_url: '', watermark_text: '', primary_color: '#5b5fc7' });
        toast.success('Organization created');
      } else {
        const err = await res.json();
        toast.error(err.detail || 'Failed to create');
      }
    } catch {
      toast.error('Connection error');
    }
  };

  // Verify domain
  const verifyDomain = async (domain) => {
    try {
      const res = await fetch(`${API}/api/karau-meet/organizations/${selectedOrg.org_id}/verify-domain?domain=${domain}`, {
        method: 'POST', headers
      });
      if (res.ok) {
        toast.success(`${domain} verified`);
        fetchOrgs();
      }
    } catch { toast.error('Verification failed'); }
  };

  // Create room
  const handleCreateRoom = async () => {
    try {
      const res = await fetch(`${API}/api/karau-meet/organizations/${selectedOrg.org_id}/rooms`, {
        method: 'POST',
        headers,
        body: JSON.stringify(newRoom)
      });
      if (res.ok) {
        toast.success('Room created');
        fetchOrgs();
        setShowRoomForm(false);
        setNewRoom({ name: '', building: '', floor: '', capacity: 10, equipment: [], location_type: 'physical', address: '' });
      } else {
        const err = await res.json();
        toast.error(err.detail || 'Failed');
      }
    } catch { toast.error('Connection error'); }
  };

  // Delete room
  const deleteRoom = async (roomId) => {
    try {
      await fetch(`${API}/api/karau-meet/organizations/${selectedOrg.org_id}/rooms/${roomId}`, {
        method: 'DELETE', headers
      });
      toast.success('Room deleted');
      fetchOrgs();
    } catch { toast.error('Failed'); }
  };

  // Search employees
  const searchEmployees = useCallback(async (query) => {
    if (!selectedOrg) return;
    try {
      const res = await fetch(`${API}/api/karau-meet/organizations/${selectedOrg.org_id}/employees?search=${query}`, { headers });
      if (res.ok) {
        const data = await res.json();
        setEmployees(data.employees || []);
      }
    } catch {}
  }, [selectedOrg]);

  useEffect(() => {
    if (activeTab === 'employees' && selectedOrg) {
      searchEmployees(employeeSearch);
    }
  }, [activeTab, selectedOrg, employeeSearch, searchEmployees]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-6 h-6 animate-spin text-[#5b5fc7]" />
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="org-admin-panel">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-white flex items-center gap-2">
            <Building2 className="w-5 h-5 text-[#5b5fc7]" />
            Enterprise Organizations
          </h2>
          <p className="text-sm text-slate-400 mt-1">Manage tiers, domains, rooms, and branding</p>
        </div>
        <Button
          className="bg-[#5b5fc7] hover:bg-[#4e52b5] text-white"
          onClick={() => setShowCreateForm(true)}
          data-testid="create-org-btn"
        >
          <Plus className="w-4 h-4 mr-1" /> New Organization
        </Button>
      </div>

      {/* Create Form */}
      {showCreateForm && (
        <div className="bg-slate-800 rounded-xl p-5 border border-slate-700 space-y-4" data-testid="create-org-form">
          <h3 className="text-white font-medium">Create Organization</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <Label className="text-xs text-slate-400">Company Name</Label>
              <Input value={newOrg.name} onChange={e => setNewOrg({...newOrg, name: e.target.value})} className="bg-slate-900 border-slate-600 text-white" placeholder="Acme Corp" />
            </div>
            <div>
              <Label className="text-xs text-slate-400">Email Domains (comma-separated)</Label>
              <Input value={newOrg.email_domains} onChange={e => setNewOrg({...newOrg, email_domains: e.target.value})} className="bg-slate-900 border-slate-600 text-white" placeholder="acme.com, acme.io" />
            </div>
            <div>
              <Label className="text-xs text-slate-400">Tier</Label>
              <Select value={newOrg.tier} onValueChange={v => setNewOrg({...newOrg, tier: v})}>
                <SelectTrigger className="bg-slate-900 border-slate-600 text-white"><SelectValue /></SelectTrigger>
                <SelectContent className="bg-slate-800 border-slate-600">
                  <SelectItem value="tier_1" className="text-white">Tier 1 — Basic (50 users, 10 rooms)</SelectItem>
                  <SelectItem value="tier_2" className="text-white">Tier 2 — Professional (100 users, 25 rooms)</SelectItem>
                  <SelectItem value="tier_grande" className="text-white">Tier Grande (1000 users, unlimited rooms)</SelectItem>
                  <SelectItem value="recruiter" className="text-white">Recruiter (50 users, 5 rooms)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label className="text-xs text-slate-400">Brand Color</Label>
              <div className="flex items-center gap-2">
                <input type="color" value={newOrg.primary_color} onChange={e => setNewOrg({...newOrg, primary_color: e.target.value})} className="w-9 h-9 rounded cursor-pointer" />
                <Input value={newOrg.primary_color} onChange={e => setNewOrg({...newOrg, primary_color: e.target.value})} className="bg-slate-900 border-slate-600 text-white flex-1" />
              </div>
            </div>
            <div>
              <Label className="text-xs text-slate-400">Logo URL</Label>
              <Input value={newOrg.logo_url} onChange={e => setNewOrg({...newOrg, logo_url: e.target.value})} className="bg-slate-900 border-slate-600 text-white" placeholder="https://..." />
            </div>
            <div>
              <Label className="text-xs text-slate-400">Watermark Text</Label>
              <Input value={newOrg.watermark_text} onChange={e => setNewOrg({...newOrg, watermark_text: e.target.value})} className="bg-slate-900 border-slate-600 text-white" placeholder="Company Name" />
            </div>
          </div>
          <div className="flex gap-2 justify-end">
            <Button variant="outline" className="border-slate-600 text-slate-300" onClick={() => setShowCreateForm(false)}>Cancel</Button>
            <Button className="bg-[#5b5fc7] text-white" onClick={handleCreateOrg} disabled={!newOrg.name || !newOrg.email_domains}>Create</Button>
          </div>
        </div>
      )}

      {/* Org selector + details */}
      {orgs.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
          {/* Org list */}
          <div className="space-y-2">
            {orgs.map(org => (
              <button
                key={org.org_id}
                onClick={() => setSelectedOrg(org)}
                className={`w-full text-left p-3 rounded-lg border transition-all ${
                  selectedOrg?.org_id === org.org_id
                    ? 'bg-[#5b5fc7]/10 border-[#5b5fc7]/50'
                    : 'bg-slate-800 border-slate-700 hover:border-slate-600'
                }`}
                data-testid={`org-${org.org_id}`}
              >
                <div className="flex items-center gap-2">
                  {org.logo_url ? (
                    <img src={org.logo_url} alt="" className="w-8 h-8 rounded object-cover" />
                  ) : (
                    <div className="w-8 h-8 rounded flex items-center justify-center text-white text-xs font-bold" style={{ backgroundColor: org.primary_color || '#5b5fc7' }}>
                      {org.name?.charAt(0)}
                    </div>
                  )}
                  <div className="min-w-0">
                    <p className="text-sm text-white font-medium truncate">{org.name}</p>
                    <Badge className={`text-[10px] ${TIER_BADGES[org.tier]?.color || 'bg-slate-600'}`}>
                      {TIER_BADGES[org.tier]?.label || org.tier}
                    </Badge>
                  </div>
                </div>
              </button>
            ))}
          </div>

          {/* Org details */}
          {selectedOrg && (
            <div className="lg:col-span-3 bg-slate-800 rounded-xl border border-slate-700">
              {/* Tabs */}
              <div className="flex border-b border-slate-700 overflow-x-auto">
                {['overview', 'rooms', 'employees', 'branding'].map(tab => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={`px-4 py-3 text-sm font-medium capitalize whitespace-nowrap transition-colors ${
                      activeTab === tab
                        ? 'text-[#5b5fc7] border-b-2 border-[#5b5fc7]'
                        : 'text-slate-400 hover:text-white'
                    }`}
                    data-testid={`tab-${tab}`}
                  >
                    {tab}
                  </button>
                ))}
              </div>

              <div className="p-5">
                {/* Overview */}
                {activeTab === 'overview' && (
                  <div className="space-y-4" data-testid="org-overview">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      <div className="bg-slate-900 rounded-lg p-3 text-center">
                        <p className="text-2xl font-bold text-white">{selectedOrg.employee_count || 0}</p>
                        <p className="text-xs text-slate-400">/ {selectedOrg.max_users} Users</p>
                      </div>
                      <div className="bg-slate-900 rounded-lg p-3 text-center">
                        <p className="text-2xl font-bold text-white">{selectedOrg.conference_rooms?.length || 0}</p>
                        <p className="text-xs text-slate-400">/ {selectedOrg.max_rooms === -1 ? 'Unlimited' : selectedOrg.max_rooms} Rooms</p>
                      </div>
                      <div className="bg-slate-900 rounded-lg p-3 text-center">
                        <p className="text-2xl font-bold text-white">{selectedOrg.email_domains?.length || 0}</p>
                        <p className="text-xs text-slate-400">Domains</p>
                      </div>
                      <div className="bg-slate-900 rounded-lg p-3 text-center">
                        <Badge className={`text-sm ${TIER_BADGES[selectedOrg.tier]?.color}`}>
                          {TIER_BADGES[selectedOrg.tier]?.label}
                        </Badge>
                        <p className="text-xs text-slate-400 mt-1">License Tier</p>
                      </div>
                    </div>

                    {/* Domains */}
                    <div>
                      <h4 className="text-sm font-medium text-white mb-2 flex items-center gap-1"><Globe className="w-4 h-4" /> Email Domains</h4>
                      <div className="flex flex-wrap gap-2">
                        {selectedOrg.email_domains?.map(d => {
                          const isVerified = selectedOrg.verified_domains?.includes(d);
                          return (
                            <div key={d} className="flex items-center gap-1 bg-slate-900 rounded-full px-3 py-1">
                              <span className="text-sm text-slate-300">{d}</span>
                              {isVerified ? (
                                <Badge className="bg-emerald-600 text-[9px] px-1">Verified</Badge>
                              ) : (
                                <Button variant="ghost" size="sm" className="h-5 text-[10px] text-amber-400 p-0 px-1" onClick={() => verifyDomain(d)}>
                                  Verify
                                </Button>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    </div>

                    {/* Features */}
                    <div>
                      <h4 className="text-sm font-medium text-white mb-2 flex items-center gap-1"><Sparkles className="w-4 h-4" /> Features</h4>
                      <div className="flex flex-wrap gap-1.5">
                        {selectedOrg.features?.map(f => (
                          <Badge key={f} className="bg-slate-700 text-slate-300 text-xs">
                            {f.replace(/_/g, ' ')}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {/* Rooms */}
                {activeTab === 'rooms' && (
                  <div className="space-y-3" data-testid="org-rooms">
                    <div className="flex justify-between items-center">
                      <p className="text-sm text-slate-400">{selectedOrg.conference_rooms?.length || 0} rooms configured</p>
                      <Button size="sm" className="bg-[#5b5fc7] text-white" onClick={() => setShowRoomForm(true)} data-testid="add-room-btn">
                        <Plus className="w-3 h-3 mr-1" /> Add Room
                      </Button>
                    </div>

                    {showRoomForm && (
                      <div className="bg-slate-900 rounded-lg p-4 space-y-3 border border-slate-700">
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                          <div>
                            <Label className="text-xs text-slate-400">Room Name</Label>
                            <Input value={newRoom.name} onChange={e => setNewRoom({...newRoom, name: e.target.value})} className="bg-slate-800 border-slate-600 text-white" placeholder="Board Room A" />
                          </div>
                          <div>
                            <Label className="text-xs text-slate-400">Building</Label>
                            <Input value={newRoom.building} onChange={e => setNewRoom({...newRoom, building: e.target.value})} className="bg-slate-800 border-slate-600 text-white" placeholder="HQ" />
                          </div>
                          <div>
                            <Label className="text-xs text-slate-400">Floor</Label>
                            <Input value={newRoom.floor} onChange={e => setNewRoom({...newRoom, floor: e.target.value})} className="bg-slate-800 border-slate-600 text-white" placeholder="3rd" />
                          </div>
                          <div>
                            <Label className="text-xs text-slate-400">Capacity</Label>
                            <Input type="number" value={newRoom.capacity} onChange={e => setNewRoom({...newRoom, capacity: parseInt(e.target.value) || 10})} className="bg-slate-800 border-slate-600 text-white" />
                          </div>
                          <div>
                            <Label className="text-xs text-slate-400">Type</Label>
                            <Select value={newRoom.location_type} onValueChange={v => setNewRoom({...newRoom, location_type: v})}>
                              <SelectTrigger className="bg-slate-800 border-slate-600 text-white"><SelectValue /></SelectTrigger>
                              <SelectContent className="bg-slate-800 border-slate-600">
                                <SelectItem value="physical" className="text-white">Physical</SelectItem>
                                <SelectItem value="virtual" className="text-white">Virtual</SelectItem>
                                <SelectItem value="hybrid" className="text-white">Hybrid</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>
                          <div>
                            <Label className="text-xs text-slate-400">Address</Label>
                            <Input value={newRoom.address} onChange={e => setNewRoom({...newRoom, address: e.target.value})} className="bg-slate-800 border-slate-600 text-white" placeholder="123 Main St" />
                          </div>
                        </div>
                        <div>
                          <Label className="text-xs text-slate-400 mb-1 block">Equipment</Label>
                          <div className="flex flex-wrap gap-1.5">
                            {EQUIPMENT_OPTIONS.map(eq => (
                              <button
                                key={eq.id}
                                onClick={() => {
                                  const has = newRoom.equipment.includes(eq.id);
                                  setNewRoom({...newRoom, equipment: has ? newRoom.equipment.filter(e => e !== eq.id) : [...newRoom.equipment, eq.id]});
                                }}
                                className={`px-2 py-1 rounded text-xs transition-colors ${newRoom.equipment.includes(eq.id) ? 'bg-[#5b5fc7] text-white' : 'bg-slate-700 text-slate-400'}`}
                              >
                                {eq.label}
                              </button>
                            ))}
                          </div>
                        </div>
                        <div className="flex gap-2 justify-end">
                          <Button variant="outline" size="sm" className="border-slate-600 text-slate-300" onClick={() => setShowRoomForm(false)}>Cancel</Button>
                          <Button size="sm" className="bg-[#5b5fc7] text-white" onClick={handleCreateRoom} disabled={!newRoom.name}>Create Room</Button>
                        </div>
                      </div>
                    )}

                    {/* Room list */}
                    <div className="space-y-2">
                      {selectedOrg.conference_rooms?.map(room => (
                        <div key={room.room_id} className="bg-slate-900 rounded-lg p-3 flex items-center justify-between" data-testid={`room-${room.room_id}`}>
                          <div className="flex items-center gap-3">
                            <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                              room.location_type === 'virtual' ? 'bg-blue-500/20' : room.location_type === 'hybrid' ? 'bg-purple-500/20' : 'bg-emerald-500/20'
                            }`}>
                              {room.location_type === 'virtual' ? <Monitor className="w-5 h-5 text-blue-400" /> :
                               room.location_type === 'hybrid' ? <Globe className="w-5 h-5 text-purple-400" /> :
                               <MapPin className="w-5 h-5 text-emerald-400" />}
                            </div>
                            <div>
                              <p className="text-sm text-white font-medium">{room.name}</p>
                              <div className="flex items-center gap-2 text-xs text-slate-400">
                                {room.building && <span>{room.building}</span>}
                                {room.floor && <span>Floor {room.floor}</span>}
                                <span><Users className="w-3 h-3 inline" /> {room.capacity}</span>
                                <Badge className="text-[9px] bg-slate-700">{room.location_type}</Badge>
                              </div>
                            </div>
                          </div>
                          <Button variant="ghost" size="sm" className="text-red-400 hover:text-red-300 h-8 w-8 p-0" onClick={() => deleteRoom(room.room_id)}>
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      ))}
                      {(!selectedOrg.conference_rooms || selectedOrg.conference_rooms.length === 0) && (
                        <p className="text-slate-500 text-sm text-center py-6">No conference rooms configured yet</p>
                      )}
                    </div>
                  </div>
                )}

                {/* Employees */}
                {activeTab === 'employees' && (
                  <EmployeesTab
                    org={selectedOrg}
                    employees={employees}
                    employeeSearch={employeeSearch}
                    setEmployeeSearch={setEmployeeSearch}
                    headers={headers}
                    onRefresh={() => { fetchOrgs(); searchEmployees(employeeSearch); }}
                  />
                )}

                {/* Branding */}
                {activeTab === 'branding' && (
                  <div className="space-y-4" data-testid="org-branding">
                    <div className="bg-slate-900 rounded-lg p-4 border border-slate-700">
                      <h4 className="text-sm font-medium text-white mb-3">Meeting Footer Preview</h4>
                      {/* Preview */}
                      <div className="bg-slate-950 rounded-lg p-3 flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          {selectedOrg.logo_url ? (
                            <img src={selectedOrg.logo_url} alt="" className="h-6 object-contain" />
                          ) : (
                            <div className="w-6 h-6 rounded flex items-center justify-center text-white text-xs font-bold" style={{ backgroundColor: selectedOrg.primary_color }}>
                              {selectedOrg.name?.charAt(0)}
                            </div>
                          )}
                          <span className="text-xs text-slate-400">{selectedOrg.watermark_text || selectedOrg.name}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Shield className="w-3 h-3" style={{ color: selectedOrg.primary_color }} />
                          <span className="text-[10px]" style={{ color: selectedOrg.primary_color }}>Enterprise Verified</span>
                        </div>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <Label className="text-xs text-slate-400">Logo URL</Label>
                        <Input value={selectedOrg.logo_url || ''} readOnly className="bg-slate-900 border-slate-600 text-slate-300" />
                      </div>
                      <div>
                        <Label className="text-xs text-slate-400">Watermark Text</Label>
                        <Input value={selectedOrg.watermark_text || ''} readOnly className="bg-slate-900 border-slate-600 text-slate-300" />
                      </div>
                      <div>
                        <Label className="text-xs text-slate-400">Brand Color</Label>
                        <div className="flex items-center gap-2">
                          <div className="w-8 h-8 rounded" style={{ backgroundColor: selectedOrg.primary_color }} />
                          <Input value={selectedOrg.primary_color || ''} readOnly className="bg-slate-900 border-slate-600 text-slate-300" />
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {orgs.length === 0 && !showCreateForm && (
        <div className="text-center py-12 bg-slate-800 rounded-xl border border-slate-700">
          <Building2 className="w-10 h-10 text-slate-500 mx-auto mb-3" />
          <p className="text-white font-medium">No organizations yet</p>
          <p className="text-sm text-slate-400 mt-1">Create your first enterprise organization</p>
          <Button className="mt-4 bg-[#5b5fc7] text-white" onClick={() => setShowCreateForm(true)}>
            <Plus className="w-4 h-4 mr-1" /> Create Organization
          </Button>
        </div>
      )}
    </div>
  );
};

export default OrganizationAdmin;
