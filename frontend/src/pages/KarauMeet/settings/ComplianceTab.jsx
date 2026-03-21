import { FileText, Shield } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useTranslation } from '@/utils/i18n';

export const ComplianceTab = ({ complianceStatus }) => {
  const { t } = useTranslation();

  if (!complianceStatus) return null;

  return (
    <div className="space-y-4">
      <Card className="bg-karau-card/50 border-karau-border rounded-2xl">
        <CardHeader>
          <CardTitle className="text-white text-lg flex items-center gap-2">
            <FileText className="w-5 h-5 text-purple-400" />
            {t("karauMeet.gdprCompliance")}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2 mb-4">
            <Badge className={complianceStatus.gdpr?.compliant ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'} data-testid="gdpr-status">
              {complianceStatus.gdpr?.compliant ? t("karauMeet.compliant") : t("karauMeet.nonCompliant")}
            </Badge>
          </div>
          <div className="grid gap-2">
            {complianceStatus.gdpr?.features?.map((feature, idx) => (
              <div key={idx} className="flex items-center justify-between p-2 bg-karau-bg/50 rounded-lg">
                <span className="text-sm text-slate-300">{feature.name}</span>
                <Badge variant="outline" className="text-emerald-400 border-emerald-400/30 text-xs">{feature.status}</Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card className="bg-karau-card/50 border-karau-border rounded-2xl">
        <CardHeader>
          <CardTitle className="text-white text-lg flex items-center gap-2">
            <Shield className="w-5 h-5 text-violet-400" />
            {t("karauMeet.hipaaCompliance")}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2 mb-4">
            <Badge className={complianceStatus.hipaa?.compliant ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'} data-testid="hipaa-status">
              {complianceStatus.hipaa?.compliant ? t("karauMeet.compliant") : t("karauMeet.nonCompliant")}
            </Badge>
          </div>
          <div className="grid gap-2">
            {complianceStatus.hipaa?.features?.map((feature, idx) => (
              <div key={idx} className="flex items-center justify-between p-2 bg-karau-bg/50 rounded-lg">
                <span className="text-sm text-slate-300">{feature.name}</span>
                <Badge variant="outline" className="text-emerald-400 border-emerald-400/30 text-xs">{feature.status}</Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
