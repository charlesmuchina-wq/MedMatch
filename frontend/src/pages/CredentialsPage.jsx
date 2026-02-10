import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Award, Shield, CheckCircle, Clock, Upload, Search,
  ChevronRight, Building, FileText, AlertCircle, Plus, Link2
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { toast } from 'sonner';
import CredentialsManager, { VerificationConsentScreen } from '@/components/CredentialsManager';
import TrustScoreDisplay, { TrustScoreBadge } from '@/components/TrustScoreDisplay';
import ORCIDConnect from '@/components/ORCIDConnect';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const CredentialsPage = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('my-credentials');
  const [certifications, setCertifications] = useState([]);
  const [hierarchy, setHierarchy] = useState([]);
  const [providers, setProviders] = useState({});
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchCertifications();
    fetchHierarchy();
    fetchProviders();
  }, []);

  const fetchCertifications = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/credentials/certifications`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setCertifications(data.certifications || []);
    } catch (error) {
      console.error('Failed to fetch certifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchHierarchy = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/credentials/hierarchy`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setHierarchy(data.hierarchy || []);
    } catch (error) {
      console.error('Failed to fetch hierarchy:', error);
    }
  };

  const fetchProviders = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/credentials/providers`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setProviders(data.providers || {});
    } catch (error) {
      console.error('Failed to fetch providers:', error);
    }
  };

  const filteredCertifications = certifications.filter(cert =>
    cert.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    cert.code?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const tabs = [
    { id: 'my-credentials', label: 'My Credentials', icon: Award },
    { id: 'orcid', label: 'ORCID', icon: Link2 },
    { id: 'browse', label: 'Browse Certifications', icon: Search },
    { id: 'hierarchy', label: 'Quality Hierarchy', icon: Building },
    { id: 'providers', label: 'Verification Providers', icon: Shield }
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6" data-testid="credentials-page">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Credential Verification
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Primary Source Verification (PSV) for Healthcare, Engineering & Quality Professionals
        </p>
      </div>

      {/* Tabs */}
      <div className="max-w-7xl mx-auto mb-6">
        <div className="flex gap-2 overflow-x-auto pb-2">
          {tabs.map(tab => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'bg-teal-600 text-white'
                    : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto">
        {/* My Credentials Tab */}
        {activeTab === 'my-credentials' && (
          <CredentialsManager />
        )}

        {/* ORCID Tab */}
        {activeTab === 'orcid' && (
          <div className="max-w-2xl mx-auto space-y-6">
            <ORCIDConnect 
              userId={localStorage.getItem('userId') || 'current-user'}
              onDataImported={(data) => {
                console.log('ORCID data imported:', data);
                toast.success('ORCID credentials imported!');
              }}
            />
            
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-4">
              <h3 className="font-medium text-blue-900 dark:text-blue-200 mb-2">Why Connect ORCID?</h3>
              <ul className="text-sm text-blue-800 dark:text-blue-300 space-y-1">
                <li>• <strong>Verified credentials</strong> - Education verified by institutions</li>
                <li>• <strong>Instant import</strong> - No manual data entry needed</li>
                <li>• <strong>Global standard</strong> - ORCID is the researcher identity standard</li>
                <li>• <strong>Publications</strong> - Show your research contributions</li>
                <li>• <strong>Free</strong> - ORCID is free for researchers</li>
              </ul>
            </div>
          </div>
        )}

        {/* Browse Certifications Tab */}
        {activeTab === 'browse' && (
          <div className="space-y-6">
            {/* Search */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <Input
                  placeholder="Search certifications (e.g., CQE, ISO 13485, RN)..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            {/* Certifications Grid */}
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredCertifications.map((cert, idx) => (
                <div
                  key={cert.code || idx}
                  className="bg-white dark:bg-gray-800 rounded-xl p-5 border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-shadow"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <span className="inline-block px-2 py-1 bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300 rounded text-xs font-bold mb-2">
                        {cert.code}
                      </span>
                      <h3 className="font-semibold text-gray-900 dark:text-white">
                        {cert.name}
                      </h3>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      cert.tier === 1 ? 'bg-green-100 text-green-700' :
                      cert.tier === 2 ? 'bg-blue-100 text-blue-700' :
                      cert.tier === 3 ? 'bg-yellow-100 text-yellow-700' :
                      cert.tier === 4 ? 'bg-orange-100 text-orange-700' :
                      'bg-red-100 text-red-700'
                    }`}>
                      Tier {cert.tier}
                    </span>
                  </div>
                  
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                    {cert.description}
                  </p>
                  
                  <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                    <span>{cert.provider}</span>
                    <span>{cert.category?.replace('_', ' ')}</span>
                  </div>
                  
                  <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                    <Button
                      size="sm"
                      variant="outline"
                      className="w-full"
                      onClick={() => {
                        setActiveTab('my-credentials');
                        // Could trigger add credential modal here
                      }}
                    >
                      <Plus className="w-3 h-3 mr-1" />
                      Add to My Credentials
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Quality Hierarchy Tab */}
        {activeTab === 'hierarchy' && (
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6">
              Unified Quality Hierarchy
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              The Quality Engineering & Audit career ladder from Entry-Level to Executive
            </p>
            
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200 dark:border-gray-700">
                    <th className="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">Tier</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">Level</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">Representative Title</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">Key Certifications</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">Experience</th>
                  </tr>
                </thead>
                <tbody>
                  {hierarchy.map((tier) => (
                    <tr key={tier.tier} className="border-b border-gray-100 dark:border-gray-700/50 hover:bg-gray-50 dark:hover:bg-gray-700/30">
                      <td className="py-4 px-4">
                        <span className={`inline-flex items-center justify-center w-8 h-8 rounded-full font-bold text-white ${
                          tier.tier === 1 ? 'bg-green-500' :
                          tier.tier === 2 ? 'bg-blue-500' :
                          tier.tier === 3 ? 'bg-yellow-500' :
                          tier.tier === 4 ? 'bg-orange-500' :
                          'bg-red-500'
                        }`}>
                          {tier.tier}
                        </span>
                      </td>
                      <td className="py-4 px-4 font-medium text-gray-900 dark:text-white">
                        {tier.name}
                      </td>
                      <td className="py-4 px-4 text-gray-700 dark:text-gray-300">
                        {tier.representative_title}
                      </td>
                      <td className="py-4 px-4">
                        <div className="flex flex-wrap gap-1">
                          {tier.key_certifications?.map((cert, idx) => (
                            <span
                              key={idx}
                              className="px-2 py-0.5 bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300 rounded text-xs font-medium"
                            >
                              {cert}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td className="py-4 px-4 text-gray-600 dark:text-gray-400 text-sm">
                        {tier.years_experience} years
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Verification Providers Tab */}
        {activeTab === 'providers' && (
          <div className="space-y-6">
            {Object.entries(providers).map(([type, providerList]) => (
              <div key={type} className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 capitalize">
                  {type.replace('_', ' ')} Providers
                </h3>
                <div className="grid md:grid-cols-2 gap-4">
                  {providerList.map((provider) => (
                    <div
                      key={provider.id}
                      className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:border-teal-300 transition-colors"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <h4 className="font-medium text-gray-900 dark:text-white">
                          {provider.name}
                        </h4>
                        <Shield className="w-4 h-4 text-teal-500" />
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                        {provider.description}
                      </p>
                      <div className="flex flex-wrap gap-1">
                        {provider.supports?.slice(0, 3).map((item, idx) => (
                          <span
                            key={idx}
                            className="px-2 py-0.5 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 rounded text-xs"
                          >
                            {item}
                          </span>
                        ))}
                        {provider.supports?.length > 3 && (
                          <span className="px-2 py-0.5 text-gray-500 text-xs">
                            +{provider.supports.length - 3} more
                          </span>
                        )}
                      </div>
                      <div className="mt-3 pt-3 border-t border-gray-100 dark:border-gray-700 text-xs text-gray-500">
                        Regions: {provider.regions?.join(', ')}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default CredentialsPage;
