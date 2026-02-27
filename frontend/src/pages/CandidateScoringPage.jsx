import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Brain, Target, AlertTriangle, CheckCircle, Loader2, Sparkles, User, Briefcase } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const ScoreGauge = ({ score, label, color }) => (
  <div className="flex flex-col items-center">
    <div className={`relative w-16 h-16 rounded-full border-4 ${color} flex items-center justify-center`}>
      <span className="text-lg font-bold text-white">{score}</span>
    </div>
    <span className="text-xs text-slate-400 mt-1">{label}</span>
  </div>
);

export default function CandidateScoringPage() {
  const [jobTitle, setJobTitle] = useState('');
  const [jobDesc, setJobDesc] = useState('');
  const [requiredSkills, setRequiredSkills] = useState('');
  const [candidateName, setCandidateName] = useState('');
  const [candidateResume, setCandidateResume] = useState('');
  const [candidateSkills, setCandidateSkills] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleScore = async () => {
    if (!jobTitle || !candidateResume) return;
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/ai-talent/score-candidate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          job_title: jobTitle, job_description: jobDesc,
          required_skills: requiredSkills.split(',').map(s => s.trim()).filter(Boolean),
          candidate_name: candidateName || 'Candidate',
          candidate_resume: candidateResume,
          candidate_skills: candidateSkills.split(',').map(s => s.trim()).filter(Boolean)
        })
      });
      if (res.ok) setResult(await res.json());
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  const getScoreColor = (s) => s >= 80 ? 'border-emerald-500' : s >= 60 ? 'border-yellow-500' : 'border-red-500';

  return (
    <div className="min-h-screen bg-slate-900 p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center gap-3 mb-8">
          <div className="p-2 bg-turquoise/10 rounded-lg"><Brain className="w-6 h-6 text-turquoise" /></div>
          <div>
            <h1 className="text-2xl font-bold text-white" data-testid="scoring-page-title">AI Candidate Scoring</h1>
            <p className="text-slate-400 text-sm">Score candidates against job requirements using AI</p>
          </div>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="space-y-4">
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader className="pb-3"><CardTitle className="text-white text-base flex items-center gap-2"><Briefcase className="w-4 h-4 text-turquoise" /> Job Details</CardTitle></CardHeader>
              <CardContent className="space-y-3">
                <Input value={jobTitle} onChange={e => setJobTitle(e.target.value)} placeholder="Job Title" className="bg-slate-700 border-slate-600 text-white" data-testid="job-title-input" />
                <Textarea value={jobDesc} onChange={e => setJobDesc(e.target.value)} placeholder="Job description..." className="bg-slate-700 border-slate-600 text-white min-h-[80px]" data-testid="job-desc-input" />
                <Input value={requiredSkills} onChange={e => setRequiredSkills(e.target.value)} placeholder="Required skills (comma-separated)" className="bg-slate-700 border-slate-600 text-white" />
              </CardContent>
            </Card>
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader className="pb-3"><CardTitle className="text-white text-base flex items-center gap-2"><User className="w-4 h-4 text-turquoise" /> Candidate</CardTitle></CardHeader>
              <CardContent className="space-y-3">
                <Input value={candidateName} onChange={e => setCandidateName(e.target.value)} placeholder="Candidate name" className="bg-slate-700 border-slate-600 text-white" data-testid="candidate-name-input" />
                <Textarea value={candidateResume} onChange={e => setCandidateResume(e.target.value)} placeholder="Paste resume text..." className="bg-slate-700 border-slate-600 text-white min-h-[100px]" data-testid="candidate-resume-input" />
                <Input value={candidateSkills} onChange={e => setCandidateSkills(e.target.value)} placeholder="Candidate skills (comma-separated)" className="bg-slate-700 border-slate-600 text-white" />
              </CardContent>
            </Card>
            <Button onClick={handleScore} disabled={loading || !jobTitle || !candidateResume} className="w-full bg-turquoise hover:bg-turquoise/80 h-12" data-testid="score-btn">
              {loading ? <Loader2 className="w-5 h-5 animate-spin mr-2" /> : <Sparkles className="w-5 h-5 mr-2" />}
              {loading ? 'Analyzing...' : 'Score Candidate'}
            </Button>
          </div>
          <div>
            {result ? (
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader><CardTitle className="text-white flex items-center justify-between"><span>Scoring Results</span>
                  <Badge className={result.overall_score >= 80 ? 'bg-emerald-500/20 text-emerald-400' : result.overall_score >= 60 ? 'bg-yellow-500/20 text-yellow-400' : 'bg-red-500/20 text-red-400'} data-testid="score-result">{result.recommendation}</Badge>
                </CardTitle></CardHeader>
                <CardContent>
                  <div className="flex justify-around mb-6" data-testid="score-gauges">
                    <ScoreGauge score={result.overall_score} label="Overall" color={getScoreColor(result.overall_score)} />
                    <ScoreGauge score={result.skill_match_score} label="Skills" color={getScoreColor(result.skill_match_score)} />
                    <ScoreGauge score={result.experience_match_score} label="Experience" color={getScoreColor(result.experience_match_score)} />
                    <ScoreGauge score={result.culture_fit_score} label="Culture" color={getScoreColor(result.culture_fit_score)} />
                  </div>
                  <div className="mb-4">
                    <h4 className="text-sm font-medium text-emerald-400 mb-2 flex items-center gap-1"><CheckCircle className="w-4 h-4" /> Strengths</h4>
                    {result.strengths.map((s, i) => <div key={i} className="text-sm text-slate-300 pl-4 border-l-2 border-emerald-500/30 mb-1">{s}</div>)}
                  </div>
                  <div className="mb-4">
                    <h4 className="text-sm font-medium text-orange-400 mb-2 flex items-center gap-1"><AlertTriangle className="w-4 h-4" /> Gaps</h4>
                    {result.gaps.map((g, i) => <div key={i} className="text-sm text-slate-300 pl-4 border-l-2 border-orange-500/30 mb-1">{g}</div>)}
                  </div>
                  <h4 className="text-sm font-medium text-slate-300 mb-2">Detailed Analysis</h4>
                  <p className="text-sm text-slate-400 leading-relaxed">{result.detailed_analysis}</p>
                </CardContent>
              </Card>
            ) : (
              <div className="flex items-center justify-center h-full"><div className="text-center text-slate-500">
                <Target className="w-16 h-16 mx-auto mb-4 opacity-30" /><p>Enter job and candidate details</p>
              </div></div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
