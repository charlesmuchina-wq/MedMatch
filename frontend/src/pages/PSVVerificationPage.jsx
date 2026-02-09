import React, { useState } from 'react';
import { useTranslation } from '@/utils/i18n';
import { 
  Search, Shield, GraduationCap, FlaskConical, Building2, 
  Globe, ExternalLink, CheckCircle2, AlertTriangle, Loader2,
  User, FileCheck, BookOpen, Stethoscope
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Badge } from '../components/ui/badge';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const PSVVerificationPage = () => {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState('npi');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  // Form states
  const [npiForm, setNpiForm] = useState({ last_name: '', first_name: '', state: '', npi: '' });
  const [orcidForm, setOrcidForm] = useState({ orcid_id: '', family_name: '', given_names: '' });
  const [uniForm, setUniForm] = useState({ name: '', country: '' });
  const [oigForm, setOigForm] = useState({ last_name: '', first_name: '', state: '' });

  const handleNPISearch = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/api/psv/npi/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(npiForm)
      });
      const data = await res.json();
      setResults({ type: 'npi', data });
    } catch (err) {
      setError('Failed to search NPI registry');
    }
    setLoading(false);
  };

  const handleORCIDSearch = async () => {
    setLoading(true);
    setError(null);
    try {
      let endpoint = `${API_URL}/api/psv/orcid/search`;
      let body = orcidForm;
      
      if (orcidForm.orcid_id && orcidForm.orcid_id.length === 19) {
        endpoint = `${API_URL}/api/psv/orcid/${orcidForm.orcid_id}`;
        const res = await fetch(endpoint);
        const data = await res.json();
        setResults({ type: 'orcid_record', data });
      } else {
        const res = await fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body)
        });
        const data = await res.json();
        setResults({ type: 'orcid', data });
      }
    } catch (err) {
      setError('Failed to search ORCID registry');
    }
    setLoading(false);
  };

  const handleUniversitySearch = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/api/psv/universities/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(uniForm)
      });
      const data = await res.json();
      setResults({ type: 'university', data });
    } catch (err) {
      setError('Failed to search universities');
    }
    setLoading(false);
  };

  const handleOIGSearch = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/api/psv/oig/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(oigForm)
      });
      const data = await res.json();
      setResults({ type: 'oig', data });
    } catch (err) {
      setError('Failed to get OIG search instructions');
    }
    setLoading(false);
  };

  const renderResults = () => {
    if (!results) return null;

    switch (results.type) {
      case 'npi':
        return (
          <Card className="mt-4">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-green-500" />
                NPI Registry Results
              </CardTitle>
              <CardDescription>Found {results.data.results_count} provider(s)</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {results.data.results?.slice(0, 10).map((r, i) => (
                  <div key={i} className="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
                    <div className="font-medium">
                      {r.name?.first} {r.name?.last} {r.name?.credential && <Badge variant="outline">{r.name.credential}</Badge>}
                    </div>
                    <div className="text-sm text-slate-600 dark:text-slate-400">
                      NPI: {r.npi} | {r.entity_type}
                    </div>
                    {r.primary_taxonomy && (
                      <div className="text-sm text-slate-500">
                        {r.primary_taxonomy.description} ({r.primary_taxonomy.state})
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        );

      case 'orcid':
        return (
          <Card className="mt-4">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FlaskConical className="h-5 w-5 text-green-500" />
                ORCID Search Results
              </CardTitle>
              <CardDescription>Found {results.data.results_count} researcher(s)</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {results.data.results?.map((r, i) => (
                  <div key={i} className="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg flex justify-between items-center">
                    <span className="font-mono">{r.orcid_id}</span>
                    <a href={r.orcid_url} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline flex items-center gap-1">
                      View Profile <ExternalLink className="h-4 w-4" />
                    </a>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        );

      case 'orcid_record':
        const d = results.data;
        return (
          <Card className="mt-4">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-green-500" />
                ORCID Verified Record
              </CardTitle>
              <CardDescription>
                {d.name?.given_names} {d.name?.family_name}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h4 className="font-semibold mb-2 flex items-center gap-2"><GraduationCap className="h-4 w-4" /> Education ({d.education?.length || 0})</h4>
                {d.education?.map((edu, i) => (
                  <div key={i} className="p-2 bg-slate-50 dark:bg-slate-800 rounded mb-2">
                    <div className="font-medium">{edu.institution}</div>
                    <div className="text-sm text-slate-600">{edu.degree} • {edu.start_year}-{edu.end_year || 'Present'}</div>
                    {edu.verified && <Badge variant="success" className="mt-1">Source Verified</Badge>}
                  </div>
                ))}
              </div>
              <div>
                <h4 className="font-semibold mb-2 flex items-center gap-2"><Building2 className="h-4 w-4" /> Employment ({d.employment?.length || 0})</h4>
                {d.employment?.map((emp, i) => (
                  <div key={i} className="p-2 bg-slate-50 dark:bg-slate-800 rounded mb-2">
                    <div className="font-medium">{emp.organization}</div>
                    <div className="text-sm text-slate-600">{emp.role} • {emp.start_year}-{emp.end_year || 'Present'}</div>
                  </div>
                ))}
              </div>
              <div>
                <h4 className="font-semibold mb-2 flex items-center gap-2"><BookOpen className="h-4 w-4" /> Publications: {d.publications_count}</h4>
              </div>
            </CardContent>
          </Card>
        );

      case 'university':
        return (
          <Card className="mt-4">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <GraduationCap className="h-5 w-5 text-green-500" />
                University Search Results
              </CardTitle>
              <CardDescription>Found {results.data.results_count} institution(s)</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {results.data.results?.slice(0, 20).map((uni, i) => (
                  <div key={i} className="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
                    <div className="font-medium">{uni.name}</div>
                    <div className="text-sm text-slate-600 dark:text-slate-400">
                      {uni.country} {uni.state_province && `• ${uni.state_province}`}
                    </div>
                    {uni.web_pages?.[0] && (
                      <a href={uni.web_pages[0]} target="_blank" rel="noopener noreferrer" className="text-sm text-blue-500 hover:underline flex items-center gap-1">
                        {uni.domains?.[0]} <ExternalLink className="h-3 w-3" />
                      </a>
                    )}
                  </div>
                ))}
              </div>
              <p className="text-sm text-amber-600 mt-3 flex items-center gap-1">
                <AlertTriangle className="h-4 w-4" />
                Note: Verify accreditation status at whed.net
              </p>
            </CardContent>
          </Card>
        );

      case 'oig':
        return (
          <Card className="mt-4 border-amber-200">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5 text-amber-500" />
                OIG Exclusion Check - Manual Verification Required
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <p className="text-sm text-slate-600">The OIG does not provide a public API. Please verify manually:</p>
                <ol className="list-decimal list-inside space-y-2 text-sm">
                  {Object.values(results.data.instructions || {}).map((step, i) => (
                    <li key={i}>{step}</li>
                  ))}
                </ol>
                <div className="flex gap-2 mt-4">
                  <a href={results.data.search_url} target="_blank" rel="noopener noreferrer">
                    <Button className="gap-2">
                      <ExternalLink className="h-4 w-4" /> Search OIG Database
                    </Button>
                  </a>
                  <a href={results.data.download_url} target="_blank" rel="noopener noreferrer">
                    <Button variant="outline" className="gap-2">
                      Download CSV
                    </Button>
                  </a>
                </div>
              </div>
            </CardContent>
          </Card>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white flex items-center justify-center gap-3">
            <FileCheck className="h-8 w-8 text-blue-500" />
            Primary Source Verification Hub
          </h1>
          <p className="text-slate-600 dark:text-slate-400 mt-2">
            Free self-service verification using public databases
          </p>
          <div className="flex justify-center gap-2 mt-3">
            <Badge variant="secondary">3 Free APIs</Badge>
            <Badge variant="outline">Global Coverage</Badge>
            <Badge variant="outline">No Cost</Badge>
          </div>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="npi" className="gap-2" data-testid="tab-npi">
              <Stethoscope className="h-4 w-4" /> NPI
            </TabsTrigger>
            <TabsTrigger value="orcid" className="gap-2" data-testid="tab-orcid">
              <FlaskConical className="h-4 w-4" /> ORCID
            </TabsTrigger>
            <TabsTrigger value="university" className="gap-2" data-testid="tab-university">
              <GraduationCap className="h-4 w-4" /> University
            </TabsTrigger>
            <TabsTrigger value="oig" className="gap-2" data-testid="tab-oig">
              <Shield className="h-4 w-4" /> OIG
            </TabsTrigger>
          </TabsList>

          {/* NPI Search */}
          <TabsContent value="npi">
            <Card>
              <CardHeader>
                <CardTitle>CMS NPI Registry Search</CardTitle>
                <CardDescription>
                  Verify National Provider Identifiers for healthcare providers (FREE API)
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <Input
                    placeholder="Last Name"
                    value={npiForm.last_name}
                    onChange={(e) => setNpiForm({ ...npiForm, last_name: e.target.value })}
                    data-testid="npi-last-name"
                  />
                  <Input
                    placeholder="First Name"
                    value={npiForm.first_name}
                    onChange={(e) => setNpiForm({ ...npiForm, first_name: e.target.value })}
                    data-testid="npi-first-name"
                  />
                  <Input
                    placeholder="State (e.g., CA, NY)"
                    value={npiForm.state}
                    onChange={(e) => setNpiForm({ ...npiForm, state: e.target.value })}
                    data-testid="npi-state"
                  />
                  <Input
                    placeholder="NPI Number (optional)"
                    value={npiForm.npi}
                    onChange={(e) => setNpiForm({ ...npiForm, npi: e.target.value })}
                    data-testid="npi-number"
                  />
                </div>
                <Button 
                  className="mt-4 w-full gap-2" 
                  onClick={handleNPISearch}
                  disabled={loading}
                  data-testid="npi-search-btn"
                >
                  {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
                  Search NPI Registry
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          {/* ORCID Search */}
          <TabsContent value="orcid">
            <Card>
              <CardHeader>
                <CardTitle>ORCID Researcher Registry</CardTitle>
                <CardDescription>
                  Verify researcher identity, education, and publications (FREE API)
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 gap-4">
                  <Input
                    placeholder="ORCID ID (e.g., 0000-0002-1825-0097)"
                    value={orcidForm.orcid_id}
                    onChange={(e) => setOrcidForm({ ...orcidForm, orcid_id: e.target.value })}
                    data-testid="orcid-id"
                  />
                  <p className="text-sm text-slate-500 text-center">— or search by name —</p>
                  <div className="grid grid-cols-2 gap-4">
                    <Input
                      placeholder="Family Name"
                      value={orcidForm.family_name}
                      onChange={(e) => setOrcidForm({ ...orcidForm, family_name: e.target.value })}
                      data-testid="orcid-family-name"
                    />
                    <Input
                      placeholder="Given Names"
                      value={orcidForm.given_names}
                      onChange={(e) => setOrcidForm({ ...orcidForm, given_names: e.target.value })}
                      data-testid="orcid-given-names"
                    />
                  </div>
                </div>
                <Button 
                  className="mt-4 w-full gap-2" 
                  onClick={handleORCIDSearch}
                  disabled={loading}
                  data-testid="orcid-search-btn"
                >
                  {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
                  Search ORCID Registry
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          {/* University Search */}
          <TabsContent value="university">
            <Card>
              <CardHeader>
                <CardTitle>Global University Search</CardTitle>
                <CardDescription>
                  Search universities worldwide to validate institution names (FREE API)
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <Input
                    placeholder="University Name"
                    value={uniForm.name}
                    onChange={(e) => setUniForm({ ...uniForm, name: e.target.value })}
                    data-testid="uni-name"
                  />
                  <Input
                    placeholder="Country (optional)"
                    value={uniForm.country}
                    onChange={(e) => setUniForm({ ...uniForm, country: e.target.value })}
                    data-testid="uni-country"
                  />
                </div>
                <Button 
                  className="mt-4 w-full gap-2" 
                  onClick={handleUniversitySearch}
                  disabled={loading}
                  data-testid="uni-search-btn"
                >
                  {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
                  Search Universities
                </Button>
                <p className="text-xs text-amber-600 mt-2 flex items-center gap-1">
                  <AlertTriangle className="h-3 w-3" />
                  To verify accreditation, use <a href="https://www.whed.net" target="_blank" rel="noopener noreferrer" className="underline">WHED</a>
                </p>
              </CardContent>
            </Card>
          </TabsContent>

          {/* OIG Search */}
          <TabsContent value="oig">
            <Card>
              <CardHeader>
                <CardTitle>OIG LEIE Exclusion Check</CardTitle>
                <CardDescription>
                  Check if an individual is excluded from federal healthcare programs
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-3 gap-4">
                  <Input
                    placeholder="Last Name"
                    value={oigForm.last_name}
                    onChange={(e) => setOigForm({ ...oigForm, last_name: e.target.value })}
                    data-testid="oig-last-name"
                  />
                  <Input
                    placeholder="First Name"
                    value={oigForm.first_name}
                    onChange={(e) => setOigForm({ ...oigForm, first_name: e.target.value })}
                    data-testid="oig-first-name"
                  />
                  <Input
                    placeholder="State"
                    value={oigForm.state}
                    onChange={(e) => setOigForm({ ...oigForm, state: e.target.value })}
                    data-testid="oig-state"
                  />
                </div>
                <Button 
                  className="mt-4 w-full gap-2" 
                  onClick={handleOIGSearch}
                  disabled={loading}
                  data-testid="oig-search-btn"
                >
                  {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Shield className="h-4 w-4" />}
                  Get Verification Instructions
                </Button>
                <p className="text-xs text-slate-500 mt-2">
                  Note: OIG does not provide a public API. You'll be directed to the official website.
                </p>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {error && (
          <div className="mt-4 p-4 bg-red-50 text-red-600 rounded-lg flex items-center gap-2">
            <AlertTriangle className="h-5 w-5" />
            {error}
          </div>
        )}

        {renderResults()}

        {/* Quick Links */}
        <Card className="mt-6">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Globe className="h-5 w-5" />
              Additional Verification Resources
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {[
                { name: 'WHED (Intl. Degrees)', url: 'https://www.whed.net' },
                { name: 'NCEES (Engineering)', url: 'https://account.ncees.org/profile/verification' },
                { name: 'FSMB (Medical)', url: 'https://www.fsmb.org/physician-data-center/' },
                { name: 'Nursys (Nursing)', url: 'https://www.nursys.com/' },
                { name: 'SAM.gov Exclusions', url: 'https://sam.gov/content/exclusions' },
                { name: 'FDA Debarment', url: 'https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/compliance-actions-and-activities/fda-debarment-list-drug-product-applications' }
              ].map((link, i) => (
                <a
                  key={i}
                  href={link.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 p-2 bg-slate-50 dark:bg-slate-800 rounded hover:bg-slate-100 dark:hover:bg-slate-700 text-sm"
                >
                  <ExternalLink className="h-3 w-3" />
                  {link.name}
                </a>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default PSVVerificationPage;
