import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { FileText, Loader2, Sparkles, Copy, Check, Download, Building2 } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

export default function JobDescriptionGenerator() {
  const [title, setTitle] = useState('');
  const [department, setDepartment] = useState('');
  const [seniority, setSeniority] = useState('mid');
  const [companyName, setCompanyName] = useState('');
  const [industry, setIndustry] = useState('life sciences');
  const [skills, setSkills] = useState('');
  const [responsibilities, setResponsibilities] = useState('');
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleGenerate = async () => {
    if (!title) return;
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/ai-talent/generate-job-description`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, department, seniority, company_name: companyName, industry,
          required_skills: skills.split(',').map(s => s.trim()).filter(Boolean),
          key_responsibilities: responsibilities.split('\n').map(s => s.trim()).filter(Boolean)
        })
      });
      if (res.ok) { const d = await res.json(); setResult(d.job_description); }
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-slate-900 p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center gap-3 mb-8">
          <div className="p-2 bg-turquoise/10 rounded-lg"><FileText className="w-6 h-6 text-turquoise" /></div>
          <div>
            <h1 className="text-2xl font-bold text-white" data-testid="jd-gen-title">AI Job Description Generator</h1>
            <p className="text-slate-400 text-sm">Generate inclusive, professional job descriptions instantly</p>
          </div>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader><CardTitle className="text-white text-base flex items-center gap-2"><Building2 className="w-4 h-4 text-turquoise" /> Role Details</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <Input value={title} onChange={e => setTitle(e.target.value)} placeholder="Job Title *" className="bg-slate-700 border-slate-600 text-white" data-testid="jd-title-input" />
              <div className="grid grid-cols-2 gap-3">
                <Input value={department} onChange={e => setDepartment(e.target.value)} placeholder="Department" className="bg-slate-700 border-slate-600 text-white" />
                <Input value={companyName} onChange={e => setCompanyName(e.target.value)} placeholder="Company name" className="bg-slate-700 border-slate-600 text-white" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <Select value={seniority} onValueChange={setSeniority}>
                  <SelectTrigger className="bg-slate-700 border-slate-600 text-white"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="entry">Entry Level</SelectItem>
                    <SelectItem value="mid">Mid Level</SelectItem>
                    <SelectItem value="senior">Senior</SelectItem>
                    <SelectItem value="lead">Lead</SelectItem>
                    <SelectItem value="director">Director</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={industry} onValueChange={setIndustry}>
                  <SelectTrigger className="bg-slate-700 border-slate-600 text-white"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="life sciences">Life Sciences</SelectItem>
                    <SelectItem value="biotech">Biotechnology</SelectItem>
                    <SelectItem value="pharma">Pharmaceutical</SelectItem>
                    <SelectItem value="engineering">Engineering</SelectItem>
                    <SelectItem value="technology">Technology</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Input value={skills} onChange={e => setSkills(e.target.value)} placeholder="Required skills (comma-separated)" className="bg-slate-700 border-slate-600 text-white" />
              <textarea value={responsibilities} onChange={e => setResponsibilities(e.target.value)} placeholder="Key responsibilities (one per line)" rows={3} className="w-full bg-slate-700 border border-slate-600 text-white rounded-md px-3 py-2 text-sm" />
              <Button onClick={handleGenerate} disabled={loading || !title} className="w-full bg-turquoise hover:bg-turquoise/80 h-11" data-testid="generate-jd-btn">
                {loading ? <Loader2 className="w-5 h-5 animate-spin mr-2" /> : <Sparkles className="w-5 h-5 mr-2" />}
                {loading ? 'Generating...' : 'Generate Job Description'}
              </Button>
            </CardContent>
          </Card>
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-white text-base">Generated JD</CardTitle>
                {result && (
                  <div className="flex gap-2">
                    <Button size="sm" variant="ghost" className="h-7 text-xs text-slate-300" onClick={() => { navigator.clipboard.writeText(result); setCopied(true); setTimeout(() => setCopied(false), 2000); }}>
                      {copied ? <Check className="w-3 h-3 mr-1" /> : <Copy className="w-3 h-3 mr-1" />}{copied ? 'Copied' : 'Copy'}
                    </Button>
                    <Button size="sm" variant="ghost" className="h-7 text-xs text-slate-300" onClick={() => { const b = new Blob([result], {type:'text/markdown'}); const u = URL.createObjectURL(b); const a = document.createElement('a'); a.href=u; a.download=`${title}-JD.md`; a.click(); }}>
                      <Download className="w-3 h-3 mr-1" /> Download
                    </Button>
                  </div>
                )}
              </div>
            </CardHeader>
            <CardContent>
              {result ? (
                <pre className="whitespace-pre-wrap text-sm text-slate-300 font-sans leading-relaxed" data-testid="jd-result">{result}</pre>
              ) : (
                <div className="text-center py-16 text-slate-500"><FileText className="w-16 h-16 mx-auto mb-4 opacity-30" /><p>Enter a job title to generate</p></div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
