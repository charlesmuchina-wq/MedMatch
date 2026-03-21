import { useState } from 'react';
import { Loader2, FileText, TestTube2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { toast } from 'sonner';
import { useTranslation } from '@/utils/i18n';

const API = process.env.REACT_APP_BACKEND_URL;

export const TSRTab = ({ tsrReports, setTsrReports }) => {
  const { t } = useTranslation();
  const [generatingTsr, setGeneratingTsr] = useState(false);
  const [latestTsr, setLatestTsr] = useState(null);

  const generateTsr = async () => {
    setGeneratingTsr(true);
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${API}/api/karau-meet/tsr/generate`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setLatestTsr(data);
        toast.success(t("karauMeet.tsrGenerated") || 'TSR Report Generated!');
        const listRes = await fetch(`${API}/api/karau-meet/tsr/reports`, { headers: { 'Authorization': `Bearer ${token}` } });
        if (listRes.ok) { const d = await listRes.json(); setTsrReports(d.reports || []); }
      }
    } catch { toast.error('Failed to generate TSR'); }
    setGeneratingTsr(false);
  };

  return (
    <div className="space-y-4" data-testid="tsr-tab-content">
      <Card className="bg-white/[0.03] border-white/[0.06]">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <TestTube2 className="w-5 h-5 text-teal-400" />
            {t("karauMeet.tsrTitle") || 'Test Summary Report (TSR)'}
          </CardTitle>
          <CardDescription className="text-slate-500">
            {t("karauMeet.tsrDescription") || 'Generate a comprehensive test summary report to assess platform release readiness.'}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Button onClick={generateTsr} disabled={generatingTsr}
            className="bg-gradient-to-r from-teal-600 to-cyan-600 hover:from-teal-500 hover:to-cyan-500 text-white rounded-xl"
            data-testid="generate-tsr-btn">
            {generatingTsr ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <TestTube2 className="w-4 h-4 mr-2" />}
            {t("karauMeet.generateTSR") || 'Generate TSR Report'}
          </Button>

          {latestTsr && (
            <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-5 space-y-4" data-testid="tsr-result">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-white">{t("karauMeet.tsrLatest") || 'Latest Report'}</h3>
                <Badge className={`text-xs ${
                  latestTsr.recommendation === 'RELEASE_READY' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                  latestTsr.recommendation === 'CONDITIONAL_RELEASE' ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' :
                  'bg-red-500/10 text-red-400 border-red-500/20'
                }`} data-testid="tsr-recommendation">{latestTsr.recommendation}</Badge>
              </div>

              <div className="grid grid-cols-4 gap-3">
                {[
                  { label: t("karauMeet.totalTests") || 'Total', value: latestTsr.test_metrics?.total_tests, color: 'text-blue-400' },
                  { label: t("karauMeet.passed") || 'Passed', value: latestTsr.test_metrics?.passed, color: 'text-emerald-400' },
                  { label: t("karauMeet.failed") || 'Failed', value: latestTsr.test_metrics?.failed, color: 'text-red-400' },
                  { label: t("karauMeet.passRate") || 'Pass Rate', value: `${latestTsr.test_metrics?.pass_rate}%`, color: 'text-violet-400' },
                ].map((m, i) => (
                  <div key={i} className="text-center p-2 rounded-lg bg-white/[0.02]">
                    <p className={`text-lg font-bold ${m.color}`}>{m.value}</p>
                    <p className="text-[10px] text-slate-600">{m.label}</p>
                  </div>
                ))}
              </div>

              <div>
                <h4 className="text-xs font-semibold text-slate-400 uppercase mb-2">{t("karauMeet.featureCoverage") || 'Feature Coverage'}</h4>
                <div className="space-y-1.5">
                  {latestTsr.feature_coverage?.map((f, i) => (
                    <div key={i} className="flex items-center justify-between px-3 py-1.5 rounded-lg bg-white/[0.01]" data-testid={`tsr-feature-${i}`}>
                      <div className="flex items-center gap-2">
                        <span className={`w-2 h-2 rounded-full ${f.status === 'pass' ? 'bg-emerald-400' : f.status === 'fail' ? 'bg-red-400' : 'bg-slate-500'}`} />
                        <span className="text-xs text-slate-300">{f.feature}</span>
                      </div>
                      <span className="text-[10px] text-slate-500">{f.tests_passed}/{f.tests_run}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className={`p-3 rounded-xl border ${
                latestTsr.recommendation === 'RELEASE_READY' ? 'bg-emerald-500/5 border-emerald-500/15' :
                latestTsr.recommendation === 'CONDITIONAL_RELEASE' ? 'bg-amber-500/5 border-amber-500/15' :
                'bg-red-500/5 border-red-500/15'
              }`}>
                <p className="text-xs text-slate-300">{latestTsr.recommendation_text}</p>
              </div>

              <Button
                onClick={() => {
                  const token = localStorage.getItem('token');
                  window.open(`${API}/api/karau-meet/tsr/download/${latestTsr.id}?token=${token}`, '_blank');
                }}
                variant="outline"
                className="border-white/[0.1] text-slate-300 hover:text-white hover:bg-white/[0.04] rounded-xl w-full"
                data-testid="download-tsr-btn">
                <FileText className="w-4 h-4 mr-2" />
                {t("karauMeet.downloadTSR") || 'Download TSR Report'}
              </Button>
            </div>
          )}

          {tsrReports.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-slate-400 uppercase mb-2">{t("karauMeet.previousReports") || 'Previous Reports'}</h4>
              <div className="space-y-1.5">
                {tsrReports.map((r, i) => (
                  <div key={r.id} className="flex items-center justify-between px-3 py-2 rounded-lg bg-white/[0.02] border border-white/[0.04]" data-testid={`tsr-history-${i}`}>
                    <div className="flex items-center gap-2">
                      <FileText className="w-3.5 h-3.5 text-slate-500" />
                      <span className="text-xs text-slate-300">{r.id}</span>
                      <span className="text-[10px] text-slate-600">{new Date(r.generated_at).toLocaleDateString()}</span>
                    </div>
                    <Badge className={`text-[9px] ${
                      r.recommendation === 'RELEASE_READY' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                      'bg-amber-500/10 text-amber-400 border-amber-500/20'
                    }`}>{r.test_metrics?.pass_rate}%</Badge>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
