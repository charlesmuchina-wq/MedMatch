import { useState } from 'react';
import { Copy, Calendar, Check, Link2, Download, ExternalLink } from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { useTranslation } from '@/utils/i18n';

const API = process.env.REACT_APP_BACKEND_URL;

const ShareMeetingDialog = ({ isOpen, onClose, meetingId, meetingTitle }) => {
  const { t } = useTranslation();
  const [copied, setCopied] = useState(false);

  const joinLink = `${window.location.origin}/karau-meet/join/${meetingId}`;

  const copyLink = async () => {
    try {
      await navigator.clipboard.writeText(joinLink);
      setCopied(true);
      toast.success(t('share.linkCopied'));
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback
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
    const now = new Date();
    const end = new Date(now.getTime() + 60 * 60 * 1000);
    const fmt = (d) => d.toISOString().replace(/[-:]/g, '').replace(/\.\d{3}/, '');

    const ics = [
      'BEGIN:VCALENDAR',
      'VERSION:2.0',
      'PRODID:-//AI KARAU Meeting//EN',
      'CALSCALE:GREGORIAN',
      'METHOD:REQUEST',
      'BEGIN:VEVENT',
      `UID:${meetingId}@karau-meet`,
      `DTSTAMP:${fmt(now)}`,
      `DTSTART:${fmt(now)}`,
      `DTEND:${fmt(end)}`,
      `SUMMARY:${meetingTitle || 'AI KARAU Meeting'}`,
      `DESCRIPTION:Join AI KARAU Meeting:\\n${joinLink}`,
      `URL:${joinLink}`,
      'STATUS:CONFIRMED',
      'END:VEVENT',
      'END:VCALENDAR'
    ].join('\r\n');

    const blob = new Blob([ics], { type: 'text/calendar;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `karau-meeting-${meetingId}.ics`;
    a.click();
    URL.revokeObjectURL(url);
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

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-slate-800 border-slate-700 max-w-md">
        <DialogHeader>
          <DialogTitle className="text-white flex items-center gap-2">
            <Link2 className="w-5 h-5 text-turquoise" />
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
              <div className="flex-1 bg-slate-900 border border-slate-600 rounded-lg px-3 py-2.5 text-sm text-slate-300 truncate font-mono" data-testid="share-link-text">
                {joinLink}
              </div>
              <Button
                onClick={copyLink}
                size="sm"
                className={copied 
                  ? "bg-green-600 hover:bg-green-600 min-w-[80px]" 
                  : "bg-turquoise hover:bg-turquoise/80 min-w-[80px]"
                }
                data-testid="share-copy-link-btn"
              >
                {copied ? <Check className="w-4 h-4 mr-1" /> : <Copy className="w-4 h-4 mr-1" />}
                {copied ? t('share.copied') : t('share.copy')}
              </Button>
            </div>
          </div>

          {/* Meeting ID */}
          <div className="flex items-center gap-3 p-3 bg-slate-900/60 rounded-lg border border-slate-700/50">
            <div className="text-xs text-slate-400">{t('share.meetingId')}</div>
            <div className="font-mono font-bold text-turquoise tracking-wider" data-testid="share-meeting-id">{meetingId}</div>
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
                className="border-slate-600 text-slate-300 hover:bg-slate-700 hover:text-white justify-start"
                data-testid="share-download-ics-btn"
              >
                <Download className="w-4 h-4 mr-2 text-blue-400" />
                {t('share.downloadICS')}
              </Button>
              <Button
                variant="outline"
                onClick={openGoogleCalendar}
                className="border-slate-600 text-slate-300 hover:bg-slate-700 hover:text-white justify-start"
                data-testid="share-google-calendar-btn"
              >
                <ExternalLink className="w-4 h-4 mr-2 text-green-400" />
                Google Calendar
              </Button>
            </div>
          </div>

          {/* Tip */}
          <div className="text-xs text-slate-500 bg-slate-900/40 rounded-lg p-3 border border-slate-700/30">
            {t('share.guestTip')}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default ShareMeetingDialog;
