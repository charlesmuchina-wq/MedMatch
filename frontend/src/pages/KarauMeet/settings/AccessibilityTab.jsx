import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { useTranslation } from '@/utils/i18n';

export const AccessibilityTab = ({ settings, onUpdate }) => {
  const { t } = useTranslation();

  return (
    <div className="space-y-4">
      <Card className="bg-karau-card/50 border-karau-border rounded-2xl">
        <CardHeader><CardTitle className="text-white text-lg">{t("karauMeet.displaySettings")}</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div><Label className="text-white">{t("karauMeet.highContrastMode")}</Label><p className="text-xs text-karau-muted">{t("karauMeet.highContrastDesc")}</p></div>
            <Switch checked={settings.high_contrast} onCheckedChange={(v) => onUpdate('high_contrast', v)} data-testid="switch-high-contrast" />
          </div>
          <div className="flex items-center justify-between">
            <div><Label className="text-white">{t("karauMeet.largeText")}</Label><p className="text-xs text-karau-muted">{t("karauMeet.largeTextDesc")}</p></div>
            <Switch checked={settings.large_text} onCheckedChange={(v) => onUpdate('large_text', v)} data-testid="switch-large-text" />
          </div>
          <div className="flex items-center justify-between">
            <div><Label className="text-white">{t("karauMeet.reduceMotion")}</Label><p className="text-xs text-karau-muted">{t("karauMeet.reduceMotionDesc")}</p></div>
            <Switch checked={settings.reduce_motion} onCheckedChange={(v) => onUpdate('reduce_motion', v)} />
          </div>
          <div>
            <Label className="text-white mb-2 block">{t("karauMeet.colorBlindMode")}</Label>
            <select value={settings.color_blind_mode} onChange={(e) => onUpdate('color_blind_mode', e.target.value)}
              className="bg-karau-bg border border-white/10 text-white rounded-xl px-3 py-2 w-full" data-testid="select-color-blind">
              <option value="none">{t("karauMeet.colorBlindNone")}</option>
              <option value="protanopia">{t("karauMeet.colorBlindProtanopia")}</option>
              <option value="deuteranopia">{t("karauMeet.colorBlindDeuteranopia")}</option>
              <option value="tritanopia">{t("karauMeet.colorBlindTritanopia")}</option>
            </select>
          </div>
        </CardContent>
      </Card>

      <Card className="bg-karau-card/50 border-karau-border rounded-2xl">
        <CardHeader>
          <CardTitle className="text-white text-lg">{t("karauMeet.liveCaptions")}</CardTitle>
          <CardDescription className="text-karau-muted">{t("karauMeet.liveCaptionsDesc")}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div><Label className="text-white">{t("karauMeet.enableLiveCaptions")}</Label><p className="text-xs text-karau-muted">{t("karauMeet.enableLiveCaptionsDesc")}</p></div>
            <Switch checked={settings.live_captions_enabled} onCheckedChange={(v) => onUpdate('live_captions_enabled', v)} />
          </div>
          <div>
            <Label className="text-white mb-2 block">{t("karauMeet.captionFontSize")}</Label>
            <select value={settings.caption_font_size} onChange={(e) => onUpdate('caption_font_size', e.target.value)}
              className="bg-karau-bg border border-white/10 text-white rounded-xl px-3 py-2 w-full">
              <option value="small">{t("karauMeet.fontSizeSmall")}</option>
              <option value="medium">{t("karauMeet.fontSizeMedium")}</option>
              <option value="large">{t("karauMeet.fontSizeLarge")}</option>
              <option value="x-large">{t("karauMeet.fontSizeXLarge")}</option>
            </select>
          </div>
        </CardContent>
      </Card>

      <Card className="bg-karau-card/50 border-karau-border rounded-2xl">
        <CardHeader><CardTitle className="text-white text-lg">{t("karauMeet.keyboardShortcuts")}</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div><Label className="text-white">{t("karauMeet.enableKeyboardShortcuts")}</Label><p className="text-xs text-karau-muted">{t("karauMeet.enableKeyboardShortcutsDesc")}</p></div>
            <Switch checked={settings.keyboard_shortcuts_enabled} onCheckedChange={(v) => onUpdate('keyboard_shortcuts_enabled', v)} />
          </div>
          <div className="grid grid-cols-2 gap-2 mt-4">
            {[
              { keys: 'Ctrl+M', action: t("karauMeet.toggleMute") },
              { keys: 'Ctrl+V', action: t("karauMeet.toggleVideo") },
              { keys: 'Ctrl+L', action: t("karauMeet.toggleCaptions") },
              { keys: 'Ctrl+C', action: t("karauMeet.toggleChat") },
              { keys: 'Ctrl+H', action: t("karauMeet.raiseHandShortcut") },
              { keys: 'Ctrl+Shift+Q', action: t("karauMeet.leaveShortcut") }
            ].map((shortcut, idx) => (
              <div key={idx} className="flex items-center justify-between p-2 bg-karau-bg/50 rounded-lg">
                <span className="text-xs text-karau-muted">{shortcut.action}</span>
                <Badge variant="outline" className="text-purple-400 border-purple-500/30 text-xs">{shortcut.keys}</Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
