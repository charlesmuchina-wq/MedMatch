import React, { useState, useEffect } from 'react';
import { 
  Shield, CheckCircle, Clock, AlertTriangle, Upload, 
  Award, ChevronRight, RefreshCw, FileText, X, Check,
  ShieldCheck, AlertCircle, Info, Link2, ExternalLink, Unlink
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Status badge component
const StatusBadge = ({ status }) => {
  const statusConfig = {
    verified: { icon: CheckCircle, color: 'bg-green-100 text-green-700', label: 'Verified' },
    pending: { icon: Clock, color: 'bg-yellow-100 text-yellow-700', label: 'Pending' },
    manual_review: { icon: Clock, color: 'bg-blue-100 text-blue-700', label: 'Under Review' },
    expired: { icon: AlertTriangle, color: 'bg-red-100 text-red-700', label: 'Expired' },
    failed: { icon: X, color: 'bg-gray-100 text-gray-700', label: 'Failed' },
  };
  
  const config = statusConfig[status] || statusConfig.pending;
  const Icon = config.icon;
  
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${config.color}`}>
      <Icon className="w-3 h-3" />
      {config.label}
    </span>
  );
};

// Consent Screen Component
export const VerificationConsentScreen = ({ onConsent, onCancel }) => {
  const [agreed, setAgreed] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleConsent = async () => {
    if (!agreed) {
      toast.error('Please agree to the terms to continue');
      return;
    }
    
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/credentials/consent`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          consent_given: true,
          purposes: [
            'primary_source_verification',
            'credential_sharing_with_employers',
            'automated_reverification'
          ]
        })
      });
      
      if (response.ok) {
        toast.success('Consent recorded successfully');
        onConsent?.();
      } else {
        throw new Error('Failed to record consent');
      }
    } catch (error) {
      toast.error('Failed to submit consent');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 max-w-2xl mx-auto" data-testid="verification-consent">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-xl flex items-center justify-center">
          <Shield className="w-6 h-6 text-blue-600" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">
            Credential Verification Consent
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Please review how your data will be verified and shared
          </p>
        </div>
      </div>

      <div className="space-y-4 mb-6">
        <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
          <h3 className="font-medium text-gray-900 dark:text-white mb-2 flex items-center gap-2">
            <Info className="w-4 h-4 text-blue-500" />
            What data is collected?
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-300">
            We collect your personal identifying information (name, address), professional details 
            (licenses, certifications), and technical data related to the verification process.
          </p>
        </div>

        <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
          <h3 className="font-medium text-gray-900 dark:text-white mb-2 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-green-500" />
            How is my data protected?
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-300">
            We use industry-standard security measures including AES-256 encryption at rest and 
            TLS 1.3 in transit. Only authorized personnel can access your verified credentials.
          </p>
        </div>

        <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
          <h3 className="font-medium text-gray-900 dark:text-white mb-2 flex items-center gap-2">
            <Award className="w-4 h-4 text-amber-500" />
            Who do we share data with?
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-300">
            Your verified credentials may be shared with potential employers (hospitals, aerospace firms, 
            pharmaceutical companies). We also use trusted third-party verification services 
            (Credly, Verisys, FSMB) to verify your credentials at the source.
          </p>
        </div>
      </div>

      <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
        <label className="flex items-start gap-3 cursor-pointer mb-4">
          <input
            type="checkbox"
            checked={agreed}
            onChange={(e) => setAgreed(e.target.checked)}
            className="mt-1 w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <span className="text-sm text-gray-700 dark:text-gray-300">
            I have read and understand how my data will be used for credential verification. 
            I consent to the collection, verification, and sharing of my data as described above.
            I understand I can withdraw consent at any time.
          </span>
        </label>

        <div className="flex gap-3">
          <Button
            onClick={handleConsent}
            disabled={!agreed || loading}
            className="flex-1 bg-blue-600 hover:bg-blue-700"
          >
            {loading ? 'Submitting...' : 'I Agree'}
          </Button>
          <Button
            variant="outline"
            onClick={onCancel}
          >
            Cancel
          </Button>
        </div>
      </div>
    </div>
  );
};

// Trust Score Component
export const TrustScoreBadge = ({ score, badgeLevel }) => {
  const badgeColors = {
    gold: 'from-yellow-400 to-amber-500',
    silver: 'from-gray-300 to-gray-400',
    bronze: 'from-orange-400 to-orange-500',
    none: 'from-gray-200 to-gray-300'
  };

  return (
    <div className="flex items-center gap-3">
      <div className={`w-12 h-12 rounded-full bg-gradient-to-br ${badgeColors[badgeLevel]} flex items-center justify-center text-white font-bold shadow-lg`}>
        {score}
      </div>
      <div>
        <div className="text-sm font-medium text-gray-900 dark:text-white capitalize">
          {badgeLevel} Badge
        </div>
        <div className="text-xs text-gray-500">Trust Score</div>
      </div>
    </div>
  );
};

// Credential Card Component
const CredentialCard = ({ credential, onVerify, onUpload }) => {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-amber-100 dark:bg-amber-900/30 rounded-lg flex items-center justify-center">
            <Award className="w-5 h-5 text-amber-600" />
          </div>
          <div>
            <h4 className="font-medium text-gray-900 dark:text-white">
              {credential.credential_name || credential.credential_code}
            </h4>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {credential.issuing_authority || credential.provider}
            </p>
          </div>
        </div>
        <StatusBadge status={credential.status} />
      </div>

      <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400 mb-3">
        {credential.issue_date && (
          <span>Issued: {credential.issue_date}</span>
        )}
        {credential.expiry_date && (
          <>
            <span>•</span>
            <span>Expires: {credential.expiry_date}</span>
          </>
        )}
      </div>

      <div className="flex gap-2">
        {credential.status === 'pending' && (
          <>
            <Button 
              size="sm" 
              variant="outline"
              onClick={() => onVerify?.(credential)}
              className="flex-1"
            >
              <RefreshCw className="w-3 h-3 mr-1" />
              Verify Now
            </Button>
            <Button 
              size="sm" 
              variant="outline"
              onClick={() => onUpload?.(credential)}
            >
              <Upload className="w-3 h-3" />
            </Button>
          </>
        )}
        {credential.status === 'verified' && (
          <Button size="sm" variant="ghost" className="text-green-600" disabled>
            <CheckCircle className="w-3 h-3 mr-1" />
            MedMatch Verified
          </Button>
        )}
      </div>
    </div>
  );
};

// Main Credentials Manager Component
const CredentialsManager = () => {
  const [credentials, setCredentials] = useState([]);
  const [trustScore, setTrustScore] = useState(null);
  const [consentStatus, setConsentStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showConsent, setShowConsent] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [credlyStatus, setCredlyStatus] = useState(null);
  const [credlyLoading, setCredlyLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);

  useEffect(() => {
    fetchCredentials();
    fetchTrustScore();
    fetchConsentStatus();
    fetchCredlyStatus();
  }, []);

  const fetchCredlyStatus = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/credentials/credly/status`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setCredlyStatus(data);
    } catch (error) {
      console.error('Failed to fetch Credly status:', error);
    }
  };

  const handleConnectCredly = async () => {
    setCredlyLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/credentials/credly/auth`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      
      if (data.auth_url) {
        // For demo mode, simulate the OAuth callback
        if (data.auth_url.includes('DEMO_CLIENT')) {
          // Simulate OAuth callback for demo
          const callbackResponse = await fetch(
            `${API_URL}/api/credentials/credly/callback?code=demo_code&state=${data.state}`,
            { headers: { 'Authorization': `Bearer ${token}` } }
          );
          const callbackData = await callbackResponse.json();
          
          if (callbackData.success) {
            toast.success(`Connected! Imported ${callbackData.imported_count} badges`);
            fetchCredentials();
            fetchCredlyStatus();
            fetchTrustScore();
          } else {
            toast.error('Failed to connect to Credly');
          }
        } else {
          // Production: redirect to Credly OAuth
          window.location.href = data.auth_url;
        }
      }
    } catch (error) {
      toast.error('Failed to initiate Credly connection');
      console.error('Credly connection error:', error);
    } finally {
      setCredlyLoading(false);
    }
  };

  const handleSyncCredly = async () => {
    setSyncing(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/credentials/credly/sync`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      
      if (data.success) {
        toast.success(data.message);
        fetchCredentials();
        fetchTrustScore();
      } else {
        toast.error('Failed to sync badges');
      }
    } catch (error) {
      toast.error('Failed to sync Credly badges');
      console.error('Credly sync error:', error);
    } finally {
      setSyncing(false);
    }
  };

  const handleDisconnectCredly = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/credentials/credly/disconnect`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      
      if (data.success) {
        toast.success('Credly disconnected');
        setCredlyStatus({ connected: false });
      }
    } catch (error) {
      toast.error('Failed to disconnect Credly');
      console.error('Credly disconnect error:', error);
    }
  };

  const fetchCredentials = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/credentials/my-credentials`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setCredentials(data.credentials || []);
    } catch (error) {
      console.error('Failed to fetch credentials:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchTrustScore = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/credentials/trust-score`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setTrustScore(data);
    } catch (error) {
      console.error('Failed to fetch trust score:', error);
    }
  };

  const fetchConsentStatus = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/credentials/consent/status`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setConsentStatus(data);
    } catch (error) {
      console.error('Failed to fetch consent status:', error);
    }
  };

  const handleVerify = async (credential) => {
    if (!consentStatus?.has_consent) {
      setShowConsent(true);
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/credentials/verify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          credential_code: credential.credential_code,
          credential_number: credential.credential_number
        })
      });
      
      const data = await response.json();
      if (data.status === 'verified') {
        toast.success('Credential verified successfully!');
      } else {
        toast.info(`Verification status: ${data.status}`);
      }
      fetchCredentials();
      fetchTrustScore();
    } catch (error) {
      toast.error('Verification failed');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-500"></div>
      </div>
    );
  }

  if (showConsent) {
    return (
      <VerificationConsentScreen
        onConsent={() => {
          setShowConsent(false);
          fetchConsentStatus();
        }}
        onCancel={() => setShowConsent(false)}
      />
    );
  }

  return (
    <div className="space-y-6" data-testid="credentials-manager">
      {/* Header with Trust Score */}
      <div className="bg-gradient-to-r from-teal-600 to-blue-600 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold mb-2">My Credentials</h2>
            <p className="text-teal-100">
              Manage and verify your professional certifications
            </p>
          </div>
          {trustScore && (
            <TrustScoreBadge 
              score={trustScore.trust_score} 
              badgeLevel={trustScore.badge_level}
            />
          )}
        </div>
      </div>

      {/* Consent Banner */}
      {!consentStatus?.has_consent && (
        <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-amber-600" />
            <span className="text-sm text-amber-800 dark:text-amber-200">
              Grant consent to enable automatic credential verification
            </span>
          </div>
          <Button 
            size="sm" 
            onClick={() => setShowConsent(true)}
            className="bg-amber-600 hover:bg-amber-700"
          >
            Grant Consent
          </Button>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
          <div className="text-2xl font-bold text-gray-900 dark:text-white">
            {credentials.length}
          </div>
          <div className="text-sm text-gray-500">Total Credentials</div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
          <div className="text-2xl font-bold text-green-600">
            {credentials.filter(c => c.status === 'verified').length}
          </div>
          <div className="text-sm text-gray-500">Verified</div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
          <div className="text-2xl font-bold text-yellow-600">
            {credentials.filter(c => c.status === 'pending' || c.status === 'manual_review').length}
          </div>
          <div className="text-sm text-gray-500">Pending</div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
          <div className="text-2xl font-bold text-red-600">
            {credentials.filter(c => c.status === 'expired').length}
          </div>
          <div className="text-sm text-gray-500">Expired</div>
        </div>
      </div>

      {/* Add Credential Button */}
      <div className="flex justify-end">
        <Button onClick={() => setShowAddModal(true)} className="gap-2">
          <Award className="w-4 h-4" />
          Add Credential
        </Button>
      </div>

      {/* Credentials Grid */}
      {credentials.length > 0 ? (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {credentials.map((cred, idx) => (
            <CredentialCard
              key={cred.id || idx}
              credential={cred}
              onVerify={handleVerify}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-12 bg-gray-50 dark:bg-gray-800/50 rounded-xl">
          <Award className="w-12 h-12 mx-auto text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            No credentials added yet
          </h3>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
            Add your professional certifications to build your trust profile
          </p>
          <Button onClick={() => setShowAddModal(true)}>
            Add Your First Credential
          </Button>
        </div>
      )}

      {/* Trust Score Recommendations */}
      {trustScore?.recommendations?.filter(Boolean).length > 0 && (
        <div className="bg-blue-50 dark:bg-blue-900/20 rounded-xl p-5 border border-blue-200 dark:border-blue-800">
          <h3 className="font-medium text-blue-900 dark:text-blue-100 mb-3">
            Improve Your Trust Score
          </h3>
          <ul className="space-y-2">
            {trustScore.recommendations.filter(Boolean).map((rec, idx) => (
              <li key={idx} className="flex items-center gap-2 text-sm text-blue-800 dark:text-blue-200">
                <ChevronRight className="w-4 h-4" />
                {rec}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default CredentialsManager;
