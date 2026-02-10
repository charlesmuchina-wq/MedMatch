import React, { useState, useEffect } from 'react';
import { 
  ExternalLink, CheckCircle2, XCircle, RefreshCw, Loader2,
  GraduationCap, Building2, BookOpen, Link2, Unlink
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// ORCID Logo SVG
const ORCIDLogo = ({ className = "h-5 w-5" }) => (
  <svg className={className} viewBox="0 0 256 256" xmlns="http://www.w3.org/2000/svg">
    <path fill="#A6CE39" d="M256 128c0 70.7-57.3 128-128 128S0 198.7 0 128 57.3 0 128 0s128 57.3 128 128z"/>
    <path fill="#fff" d="M86.3 186.2H70.9V79.1h15.4v107.1zM108.9 79.1h41.6c39.6 0 57 28.3 57 53.6 0 27.5-21.5 53.6-56.8 53.6h-41.8V79.1zm15.4 93.3h24.5c34.9 0 42.9-26.5 42.9-39.7C191.7 111.2 178 93 googl48.4 93h-24.1v79.4zM88.7 56.8c0 5.5-4.5 10.1-10.1 10.1s-10.1-4.5-10.1-10.1c0-5.6 4.5-10.1 10.1-10.1s10.1 4.5 10.1 10.1z"/>
  </svg>
);

const ORCIDConnect = ({ userId, onDataImported }) => {
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [config, setConfig] = useState(null);
  const [connection, setConnection] = useState(null);

  useEffect(() => {
    checkConfig();
    if (userId) {
      checkConnection();
    }
    
    // Check for callback params in URL
    const params = new URLSearchParams(window.location.search);
    if (params.get('orcid_connected') === 'true') {
      toast.success('ORCID connected successfully!');
      checkConnection();
      // Clean URL
      window.history.replaceState({}, '', window.location.pathname);
    }
    if (params.get('orcid_error')) {
      toast.error(`ORCID error: ${params.get('message') || params.get('orcid_error')}`);
      window.history.replaceState({}, '', window.location.pathname);
    }
  }, [userId]);

  const checkConfig = async () => {
    try {
      const res = await fetch(`${API_URL}/api/orcid/config`);
      const data = await res.json();
      setConfig(data);
    } catch (err) {
      console.error('Failed to check ORCID config:', err);
    }
  };

  const checkConnection = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API_URL}/api/orcid/connection/${userId}`);
      const data = await res.json();
      setConnection(data);
      if (data.connected && onDataImported) {
        onDataImported(data.record);
      }
    } catch (err) {
      console.error('Failed to check ORCID connection:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async () => {
    try {
      const res = await fetch(`${API_URL}/api/orcid/auth/url?user_id=${userId}`);
      const data = await res.json();
      if (data.auth_url) {
        window.location.href = data.auth_url;
      }
    } catch (err) {
      toast.error('Failed to start ORCID connection');
    }
  };

  const handleSync = async () => {
    try {
      setSyncing(true);
      const res = await fetch(`${API_URL}/api/orcid/sync/${userId}`, { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        toast.success('ORCID data synced successfully');
        setConnection(prev => ({ ...prev, record: data.record, last_synced: data.synced_at }));
        if (onDataImported) {
          onDataImported(data.record);
        }
      } else if (data.error === 'token_expired') {
        toast.error('ORCID token expired. Please reconnect.');
      } else {
        toast.error(data.error || 'Sync failed');
      }
    } catch (err) {
      toast.error('Failed to sync ORCID data');
    } finally {
      setSyncing(false);
    }
  };

  const handleDisconnect = async () => {
    if (!window.confirm('Are you sure you want to disconnect ORCID?')) return;
    
    try {
      const res = await fetch(`${API_URL}/api/orcid/disconnect/${userId}`, { method: 'DELETE' });
      const data = await res.json();
      if (data.success) {
        toast.success('ORCID disconnected');
        setConnection({ connected: false });
      }
    } catch (err) {
      toast.error('Failed to disconnect ORCID');
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-8">
          <Loader2 className="h-6 w-6 animate-spin text-slate-400" />
        </CardContent>
      </Card>
    );
  }

  // Not configured state
  if (config && !config.configured) {
    return (
      <Card className="border-amber-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ORCIDLogo />
            ORCID Integration
          </CardTitle>
          <CardDescription>Connect your ORCID to import verified credentials</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-sm text-amber-600 bg-amber-50 p-3 rounded-lg">
            <p className="font-medium mb-2">ORCID OAuth not configured</p>
            <p className="text-slate-600">Administrator setup required:</p>
            <ol className="list-decimal list-inside mt-2 text-slate-600 space-y-1">
              {Object.values(config.setup_instructions || {}).map((step, i) => (
                <li key={i}>{step}</li>
              ))}
            </ol>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Connected state
  if (connection?.connected) {
    const record = connection.record || {};
    
    return (
      <Card className="border-green-200">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <ORCIDLogo />
                ORCID Connected
                <CheckCircle2 className="h-5 w-5 text-green-500" />
              </CardTitle>
              <CardDescription className="flex items-center gap-2 mt-1">
                <a 
                  href={connection.orcid_url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-green-600 hover:underline flex items-center gap-1"
                >
                  {connection.orcid_id} <ExternalLink className="h-3 w-3" />
                </a>
              </CardDescription>
            </div>
            <div className="flex gap-2">
              <Button 
                variant="outline" 
                size="sm" 
                onClick={handleSync}
                disabled={syncing}
              >
                {syncing ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
                Sync
              </Button>
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={handleDisconnect}
                className="text-red-500 hover:text-red-600"
              >
                <Unlink className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Name */}
          {record.name && (
            <div className="text-lg font-medium">
              {record.name.given_names} {record.name.family_name}
              {record.name.credit_name && (
                <span className="text-sm text-slate-500 ml-2">({record.name.credit_name})</span>
              )}
            </div>
          )}

          {/* Education */}
          {record.education?.length > 0 && (
            <div>
              <h4 className="font-medium flex items-center gap-2 mb-2">
                <GraduationCap className="h-4 w-4" />
                Education ({record.education.length})
              </h4>
              <div className="space-y-2">
                {record.education.slice(0, 3).map((edu, i) => (
                  <div key={i} className="p-2 bg-slate-50 dark:bg-slate-800 rounded text-sm">
                    <div className="font-medium">{edu.institution}</div>
                    <div className="text-slate-600">{edu.degree}</div>
                    <div className="text-slate-500">
                      {edu.start_year}-{edu.end_year || 'Present'}
                      {edu.verified_by_institution && (
                        <Badge variant="success" className="ml-2 text-xs">Verified</Badge>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Employment */}
          {record.employment?.length > 0 && (
            <div>
              <h4 className="font-medium flex items-center gap-2 mb-2">
                <Building2 className="h-4 w-4" />
                Employment ({record.employment.length})
              </h4>
              <div className="space-y-2">
                {record.employment.slice(0, 3).map((emp, i) => (
                  <div key={i} className="p-2 bg-slate-50 dark:bg-slate-800 rounded text-sm">
                    <div className="font-medium">{emp.organization}</div>
                    <div className="text-slate-600">{emp.role}</div>
                    <div className="text-slate-500">{emp.start_year}-{emp.end_year || 'Present'}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Publications count */}
          {record.publications_count > 0 && (
            <div className="flex items-center gap-2 text-sm text-slate-600">
              <BookOpen className="h-4 w-4" />
              {record.publications_count} publications on ORCID
            </div>
          )}

          <p className="text-xs text-slate-500">
            Last synced: {new Date(connection.last_synced).toLocaleString()}
          </p>
        </CardContent>
      </Card>
    );
  }

  // Not connected state
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <ORCIDLogo />
          Connect ORCID
        </CardTitle>
        <CardDescription>
          Import your verified education, employment, and publications
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="text-sm text-slate-600">
            <p className="mb-2">ORCID provides verified researcher identity. Connecting will import:</p>
            <ul className="list-disc list-inside space-y-1">
              <li><strong>Education</strong> - Verified degrees and institutions</li>
              <li><strong>Employment</strong> - Work history from your ORCID profile</li>
              <li><strong>Publications</strong> - Your research publications count</li>
            </ul>
          </div>
          
          <Button onClick={handleConnect} className="w-full gap-2">
            <Link2 className="h-4 w-4" />
            Connect with ORCID
          </Button>
          
          <p className="text-xs text-slate-500 text-center">
            You'll be redirected to ORCID to authorize MedMatch
          </p>
        </div>
      </CardContent>
    </Card>
  );
};

export default ORCIDConnect;
