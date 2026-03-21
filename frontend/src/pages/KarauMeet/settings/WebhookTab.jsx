import { useState, useEffect } from 'react';
import { Loader2, Webhook, Plus, Trash2, TestTube2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { toast } from 'sonner';
import { useTranslation } from '@/utils/i18n';

const API = process.env.REACT_APP_BACKEND_URL;

export const WebhookTab = () => {
  const { t } = useTranslation();
  const [webhooks, setWebhooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newUrl, setNewUrl] = useState('');
  const [newName, setNewName] = useState('');
  const [showAdd, setShowAdd] = useState(false);

  const fetchWebhooks = async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${API}/api/karau-features/webhooks`, { headers: { 'Authorization': `Bearer ${token}` } });
      if (res.ok) { const data = await res.json(); setWebhooks(data.webhooks || []); }
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  useEffect(() => { fetchWebhooks(); }, []);

  const addWebhook = async () => {
    if (!newUrl.trim()) return;
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${API}/api/karau-features/webhooks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ webhook_url: newUrl, name: newName || 'Custom CRM', events: ['meeting_ended', 'meeting_created'] })
      });
      if (res.ok) { toast.success(t("karauMeet.webhookAdded")); setNewUrl(''); setNewName(''); setShowAdd(false); fetchWebhooks(); }
    } catch { toast.error(t("karauMeet.failedAddWebhook")); }
  };

  const deleteWebhook = async (id) => {
    try {
      const token = localStorage.getItem('token');
      await fetch(`${API}/api/karau-features/webhooks/${id}`, { method: 'DELETE', headers: { 'Authorization': `Bearer ${token}` } });
      toast.success(t("karauMeet.webhookDeleted")); fetchWebhooks();
    } catch { toast.error(t("karauMeet.failedDeleteWebhook")); }
  };

  const testWebhook = async (id) => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${API}/api/karau-features/webhooks/test/${id}`, { method: 'POST', headers: { 'Authorization': `Bearer ${token}` } });
      const data = await res.json();
      if (data.success) toast.success(t("karauMeet.testSuccessful", { code: data.status_code }));
      else toast.error(`${t("karauMeet.testFailed")}: ${data.error || data.status_code}`);
    } catch { toast.error(t("karauMeet.testFailed")); }
  };

  return (
    <div className="space-y-4">
      <Card className="bg-karau-card/50 border-karau-border rounded-2xl">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-white">{t("karauMeet.crmWebhookIntegration")}</CardTitle>
              <CardDescription className="text-karau-muted">{t("karauMeet.crmWebhookDesc")}</CardDescription>
            </div>
            <Button onClick={() => setShowAdd(!showAdd)} className="bg-emerald-500/80 hover:bg-emerald-400 text-white rounded-xl" data-testid="add-webhook-btn">
              <Plus className="w-4 h-4 mr-1" />{t("karauMeet.addWebhook")}
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          {showAdd && (
            <div className="p-4 bg-karau-bg/50 rounded-xl border border-white/5 space-y-3">
              <Input placeholder={t("karauMeet.webhookNamePlaceholder")} value={newName} onChange={e => setNewName(e.target.value)}
                className="bg-karau-card border-white/10 text-white rounded-xl" data-testid="webhook-name-input" />
              <Input placeholder={t("karauMeet.webhookUrlPlaceholder")} value={newUrl} onChange={e => setNewUrl(e.target.value)}
                className="bg-karau-card border-white/10 text-white rounded-xl" data-testid="webhook-url-input" />
              <div className="flex gap-2">
                <Button onClick={addWebhook} className="bg-emerald-500 text-white rounded-xl" data-testid="save-webhook-btn">{t("karauMeet.save")}</Button>
                <Button variant="ghost" onClick={() => setShowAdd(false)} className="text-karau-muted rounded-xl">{t("karauMeet.cancel")}</Button>
              </div>
            </div>
          )}
          {loading ? (
            <div className="flex justify-center py-8"><Loader2 className="w-5 h-5 animate-spin text-purple-400" /></div>
          ) : webhooks.length === 0 ? (
            <div className="text-center py-8 text-karau-muted">
              <Webhook className="w-10 h-10 mx-auto mb-2 opacity-30" />
              <p>{t("karauMeet.noWebhooks")}</p>
              <p className="text-xs mt-1">{t("karauMeet.noWebhooksDesc")}</p>
            </div>
          ) : (
            webhooks.map(wh => (
              <div key={wh.webhook_id} className="flex items-center justify-between p-3 bg-karau-bg/30 rounded-xl border border-white/5" data-testid={`webhook-${wh.webhook_id}`}>
                <div className="flex-1 min-w-0">
                  <p className="text-white text-sm font-medium">{wh.name}</p>
                  <p className="text-slate-500 text-xs truncate">{wh.webhook_url}</p>
                  <div className="flex gap-1 mt-1">
                    {wh.events?.map(ev => (
                      <Badge key={ev} className="bg-karau-surface text-karau-muted text-[10px]">{ev}</Badge>
                    ))}
                  </div>
                </div>
                <div className="flex gap-1 ml-3">
                  <Button variant="ghost" size="sm" onClick={() => testWebhook(wh.webhook_id)} className="text-amber-400 hover:bg-amber-500/10 h-8 w-8 p-0" title="Test">
                    <TestTube2 className="w-3.5 h-3.5" />
                  </Button>
                  <Button variant="ghost" size="sm" onClick={() => deleteWebhook(wh.webhook_id)} className="text-red-400 hover:bg-red-500/10 h-8 w-8 p-0" title="Delete">
                    <Trash2 className="w-3.5 h-3.5" />
                  </Button>
                </div>
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  );
};
