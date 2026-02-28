import { useState, useEffect } from 'react';
import { Copy, Calendar, Check, Link2, Download, ExternalLink, Share2 } from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { useTranslation } from '@/utils/i18n';

const API = process.env.REACT_APP_BACKEND_URL;

const ShareMeetingDialog = ({ isOpen, onClose, meetingId, meetingTitle }) => {
  const { t } = useTranslation();
  const [copied, setCopied] = useState(false);
  const [shareLinks, setShareLinks] = useState(null);

  const joinLink = `${window.location.origin}/karau-meet/join/${meetingId}`;

  useEffect(() => {
    if (isOpen && meetingId) fetchShareLinks();
  }, [isOpen, meetingId]);

  const fetchShareLinks = async () => {
    try {
      const res = await fetch(`${API}/api/karau-meet/share/social/${meetingId}`);
      if (res.ok) setShareLinks(await res.json());
    } catch {
      // Use client-generated fallbacks
    }
  };

  const copyLink = async () => {
    try {
      await navigator.clipboard.writeText(joinLink);
      setCopied(true);
      toast.success(t('share.linkCopied'));
      setTimeout(() => setCopied(false), 2000);
    } catch {
      const input = document.createElement('input');
      input.value = joinLink;
      document.body.appendChild(input);
      input.select();
      document.execCommand('copy');
      document.body.removeChild(input);
      setCopied(true);
      toast.success(t('share.linkCopied'));
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const downloadICS = () => {
    // Use backend endpoint if available
    window.open(`${API}/api/karau-meet/share/calendar/${meetingId}.ics`, '_blank');
    toast.success(t('share.calendarDownloaded'));
  };

  const openGoogleCalendar = () => {
    const now = new Date();
    const end = new Date(now.getTime() + 60 * 60 * 1000);
    const fmt = (d) => d.toISOString().replace(/[-:]/g, '').replace(/\.\d{3}/, '');
    const params = new URLSearchParams({
      action: 'TEMPLATE',
      text: meetingTitle || 'AI KARAU Meeting',
      dates: `${fmt(now)}/${fmt(end)}`,
      details: `Join AI KARAU Meeting:\n${joinLink}`,
      sf: 'true'
    });
    window.open(`https://calendar.google.com/calendar/render?${params}`, '_blank');
  };

  // Generate share URLs (use backend data if available, otherwise client-side fallback)
  const title = meetingTitle || 'AI KARAU Meeting';
  const shareText = `Join my AI KARAU meeting: ${title}`;
  const encUrl = encodeURIComponent(joinLink);
  const encText = encodeURIComponent(shareText);

  const socialPlatforms = [
    {
      name: 'LinkedIn',
      url: shareLinks?.share_links?.linkedin || `https://www.linkedin.com/sharing/share-offsite/?url=${encUrl}`,
      color: 'bg-[#0A66C2]',
      icon: (
        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
          <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
        </svg>
      ),
    },
    {
      name: 'Twitter/X',
      url: shareLinks?.share_links?.twitter || `https://twitter.com/intent/tweet?text=${encText}&url=${encUrl}`,
      color: 'bg-[#1DA1F2]',
      icon: (
        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
          <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
        </svg>
      ),
    },
    {
      name: 'WhatsApp',
      url: shareLinks?.share_links?.whatsapp || `https://wa.me/?text=${encodeURIComponent(`${shareText} - ${joinLink}`)}`,
      color: 'bg-[#25D366]',
      icon: (
        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
          <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
        </svg>
      ),
    },
    {
      name: 'Email',
      url: shareLinks?.share_links?.email || `mailto:?subject=${encodeURIComponent(title)}&body=${encodeURIComponent(`Join my AI KARAU meeting: ${title}\n\nJoin here: ${joinLink}`)}`,
      color: 'bg-slate-600',
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
        </svg>
      ),
    },
  ];

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-karau-card border-karau-border max-w-md">
        <DialogHeader>
          <DialogTitle className="text-white flex items-center gap-2">
            <Link2 className="w-5 h-5 text-purple-400" />
            {t('share.shareMeeting')}
          </DialogTitle>
          <DialogDescription className="text-slate-400">
            {t('share.shareDescription')}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-2">
          {/* Meeting Link */}
          <div>
            <label className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-2 block">
              {t('share.meetingLink')}
            </label>
            <div className="flex items-center gap-2">
              <div className="flex-1 bg-karau-bg border border-white/10 rounded-lg px-3 py-2.5 text-sm text-slate-300 truncate font-mono" data-testid="share-link-text">
                {joinLink}
              </div>
              <Button
                onClick={copyLink}
                size="sm"
                className={copied
                  ? "bg-green-600 hover:bg-green-600 min-w-[80px]"
                  : "bg-purple-500 hover:bg-purple-500/80 min-w-[80px]"
                }
                data-testid="share-copy-link-btn"
              >
                {copied ? <Check className="w-4 h-4 mr-1" /> : <Copy className="w-4 h-4 mr-1" />}
                {copied ? t('share.copied') : t('share.copy')}
              </Button>
            </div>
          </div>

          {/* Meeting ID */}
          <div className="flex items-center gap-3 p-3 bg-karau-bg/60 rounded-lg border border-karau-border/50">
            <div className="text-xs text-slate-400">{t('share.meetingId')}</div>
            <div className="font-mono font-bold text-purple-400 tracking-wider" data-testid="share-meeting-id">{meetingId}</div>
          </div>

          {/* Social Sharing */}
          <div>
            <label className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-2 block">
              Share via
            </label>
            <div className="grid grid-cols-4 gap-2" data-testid="share-social-buttons">
              {socialPlatforms.map((p) => (
                <a
                  key={p.name}
                  href={p.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={`${p.color} hover:opacity-80 text-white flex flex-col items-center gap-1.5 py-2.5 px-2 rounded-lg transition-opacity`}
                  data-testid={`share-${p.name.toLowerCase().replace(/[\/]/g, '-')}-btn`}
                >
                  {p.icon}
                  <span className="text-[10px] font-medium">{p.name}</span>
                </a>
              ))}
            </div>
          </div>

          {/* Calendar Options */}
          <div>
            <label className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-2 block">
              {t('share.addToCalendar')}
            </label>
            <div className="grid grid-cols-2 gap-2">
              <Button
                variant="outline"
                onClick={downloadICS}
                className="border-white/10 text-slate-300 hover:bg-karau-surface hover:text-white justify-start"
                data-testid="share-download-ics-btn"
              >
                <Download className="w-4 h-4 mr-2 text-blue-400" />
                {t('share.downloadICS')}
              </Button>
              <Button
                variant="outline"
                onClick={openGoogleCalendar}
                className="border-white/10 text-slate-300 hover:bg-karau-surface hover:text-white justify-start"
                data-testid="share-google-calendar-btn"
              >
                <ExternalLink className="w-4 h-4 mr-2 text-green-400" />
                Google Calendar
              </Button>
            </div>
          </div>

          {/* Tip */}
          <div className="text-xs text-slate-500 bg-karau-bg/40 rounded-lg p-3 border border-karau-border/30">
            {t('share.guestTip')}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default ShareMeetingDialog;
