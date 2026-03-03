import { useState, useEffect, useCallback } from 'react';
import { Lightbulb, Thermometer, Blinds, Monitor, Volume2, Wand2, Mic, Wind, Droplets, Gauge } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;

const DEVICE_CONFIG = {
  lights_main: { icon: Lightbulb, label: 'Main Lights', unit: '%', color: 'amber', min: 0, max: 100 },
  lights_presentation: { icon: Lightbulb, label: 'Presentation', unit: '%', color: 'amber', min: 0, max: 100 },
  lights_ambient: { icon: Lightbulb, label: 'Ambient', unit: '%', color: 'amber', min: 0, max: 100 },
  temperature_main: { icon: Thermometer, label: 'Temperature', unit: 'C', color: 'blue', min: 16, max: 28 },
  shades_main: { icon: Blinds, label: 'Shades', unit: '%', color: 'slate', min: 0, max: 100 },
  display_main: { icon: Monitor, label: 'Display', unit: '%', color: 'violet', min: 0, max: 100 },
  speaker_volume_main: { icon: Volume2, label: 'Volume', unit: '%', color: 'emerald', min: 0, max: 100 },
};

const PRESETS = [
  { id: 'presentation', label: 'Presentation', desc: 'Dim lights, bright display' },
  { id: 'discussion', label: 'Discussion', desc: 'Balanced for conversation' },
  { id: 'break', label: 'Break', desc: 'Relaxed atmosphere' },
  { id: 'focus', label: 'Focus', desc: 'Minimal distractions' },
];

export default function RoomControlPanel({ meetingId }) {
  const [roomState, setRoomState] = useState(null);
  const [sensorData, setSensorData] = useState(null);
  const [voiceCmd, setVoiceCmd] = useState('');
  const [voiceResult, setVoiceResult] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchState = useCallback(async () => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau/iot/${meetingId}/state`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) setRoomState(await res.json());
    } catch {}
    setLoading(false);
  }, [meetingId]);

  const fetchSensors = useCallback(async () => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau/simulation/${meetingId}/iot-stream`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) setSensorData(await res.json());
    } catch {}
  }, [meetingId]);

  useEffect(() => {
    fetchState();
    fetchSensors();
    const interval = setInterval(fetchSensors, 2000);
    return () => clearInterval(interval);
  }, [fetchState, fetchSensors]);

  const controlDevice = async (type, zone, value) => {
    const token = localStorage.getItem('token');
    try {
      await fetch(`${API}/api/karau/iot/${meetingId}/device`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ device_type: type, zone, value })
      });
      fetchState();
    } catch {}
  };

  const applyPreset = async (presetName) => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau/iot/${meetingId}/preset?preset_name=${presetName}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) { toast.success(`${presetName} mode applied`); fetchState(); }
    } catch {}
  };

  const sendVoiceCommand = async () => {
    if (!voiceCmd.trim()) return;
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau/iot/${meetingId}/voice-control`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ command: voiceCmd, meeting_id: meetingId })
      });
      if (res.ok) {
        const data = await res.json();
        setVoiceResult(data);
        if (data.actions_taken > 0) { toast.success(`${data.actions_taken} action(s) applied`); fetchState(); }
        else toast.info(data.suggestion || 'Command not recognized');
        setVoiceCmd('');
      }
    } catch {}
  };

  if (loading) return <div className="p-3 text-[9px] text-slate-500 animate-soft-pulse">Connecting to room hub...</div>;

  const devices = roomState?.devices || {};
  const sensors = sensorData?.sensors || {};

  return (
    <div className="flex-1 flex flex-col overflow-hidden" data-testid="room-control-panel">
      <div className="p-3 border-b border-white/[0.06]">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-amber-500/20 to-yellow-500/10 flex items-center justify-center">
            <Wand2 className="w-3.5 h-3.5 text-amber-400" />
          </div>
          <div className="flex-1">
            <h3 className="text-xs font-semibold text-white">Room Control</h3>
            <p className="text-[9px] text-slate-500">Voice-activated environment</p>
          </div>
          {sensorData?.comfort_score && (
            <Badge className={`text-[7px] ${sensorData.comfort_score > 0.8 ? 'bg-emerald-500/10 text-emerald-400' : sensorData.comfort_score > 0.6 ? 'bg-amber-500/10 text-amber-400' : 'bg-red-500/10 text-red-400'}`}>
              <Gauge className="w-2 h-2 mr-0.5" />{Math.round(sensorData.comfort_score * 100)}%
            </Badge>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        {/* Live Sensors */}
        {sensors.temperature && (
          <div className="grid grid-cols-3 gap-1" data-testid="live-sensors">
            <div className="p-1.5 rounded-lg border border-white/[0.04] bg-white/[0.02] text-center">
              <Thermometer className="w-3 h-3 text-blue-400 mx-auto mb-0.5" />
              <p className="text-xs font-bold text-white">{sensors.temperature.value}&deg;</p>
              <p className="text-[6px] text-slate-500">{sensors.temperature.trend}</p>
            </div>
            <div className="p-1.5 rounded-lg border border-white/[0.04] bg-white/[0.02] text-center">
              <Droplets className="w-3 h-3 text-cyan-400 mx-auto mb-0.5" />
              <p className="text-xs font-bold text-white">{sensors.humidity?.value}%</p>
              <p className="text-[6px] text-slate-500">Humidity</p>
            </div>
            <div className={`p-1.5 rounded-lg border text-center ${sensors.co2?.alert ? 'border-amber-500/20 bg-amber-500/5' : 'border-white/[0.04] bg-white/[0.02]'}`}>
              <Wind className="w-3 h-3 text-emerald-400 mx-auto mb-0.5" />
              <p className={`text-xs font-bold ${sensors.co2?.alert ? 'text-amber-300' : 'text-white'}`}>{sensors.co2?.value}</p>
              <p className="text-[6px] text-slate-500">CO2 ppm</p>
            </div>
          </div>
        )}

        {/* Ventilation Alert */}
        {sensorData?.ventilation_alert && (
          <div className="p-1.5 bg-amber-500/5 border border-amber-500/15 rounded-lg text-[8px] text-amber-300 flex items-center gap-1.5" data-testid="ventilation-alert">
            <Wind className="w-3 h-3 shrink-0" />
            <span>CO2 elevated - auto-ventilation activated</span>
          </div>
        )}

        {/* Voice Command */}
        <div className="flex gap-1" data-testid="voice-command-input">
          <Input value={voiceCmd} onChange={e => setVoiceCmd(e.target.value)}
            placeholder={'"Dim the lights" or "presentation mode"'}
            onKeyDown={e => e.key === 'Enter' && sendVoiceCommand()}
            className="bg-karau-bg/60 border-white/10 text-white text-[9px] h-7 rounded-lg" />
          <Button size="sm" onClick={sendVoiceCommand} className="h-7 px-2 bg-amber-500/80 hover:bg-amber-400 rounded-lg" data-testid="voice-cmd-btn">
            <Mic className="w-3 h-3" />
          </Button>
        </div>

        {voiceResult?.actions?.length > 0 && (
          <div className="p-1.5 bg-amber-500/5 border border-amber-500/10 rounded-lg text-[8px]">
            {voiceResult.actions.map((a, i) => (<p key={i} className="text-amber-300">{a.label}</p>))}
          </div>
        )}

        {/* Presets */}
        <div className="grid grid-cols-2 gap-1" data-testid="room-presets">
          {PRESETS.map(p => (
            <button key={p.id} onClick={() => applyPreset(p.id)}
              className={`p-1.5 rounded-lg border text-left transition-all ${
                roomState?.active_preset === p.id ? 'bg-amber-500/10 border-amber-500/20 text-amber-300' : 'bg-karau-bg/30 border-white/5 text-slate-400 hover:bg-white/5'
              }`} data-testid={`preset-${p.id}`}>
              <p className="text-[9px] font-medium">{p.label}</p>
              <p className="text-[7px] opacity-60">{p.desc}</p>
            </button>
          ))}
        </div>

        {/* Device Sliders */}
        <div className="space-y-1.5" data-testid="device-controls">
          {Object.entries(DEVICE_CONFIG).map(([key, cfg]) => {
            const device = devices[key] || {};
            const val = device.value ?? 50;
            const Icon = cfg.icon;
            const colorMap = { amber: 'accent-amber-400', blue: 'accent-blue-400', slate: 'accent-slate-400', violet: 'accent-violet-400', emerald: 'accent-emerald-400' };
            const parts = key.split('_');
            const type = parts.slice(0, -1).join('_') || key;
            const zone = parts[parts.length - 1] || 'main';
            return (
              <div key={key} className="p-1.5 bg-karau-bg/30 rounded-lg border border-white/5" data-testid={`device-${key}`}>
                <div className="flex items-center justify-between mb-0.5">
                  <span className="text-[8px] text-white flex items-center gap-1"><Icon className="w-2.5 h-2.5 text-slate-400" />{cfg.label}</span>
                  <span className="text-[8px] text-slate-300 font-mono">{Math.round(val)}{cfg.unit}</span>
                </div>
                <input type="range" min={cfg.min} max={cfg.max} value={val}
                  onChange={e => controlDevice(type, zone, parseFloat(e.target.value))}
                  className={`w-full h-1 rounded-full appearance-none bg-white/10 ${colorMap[cfg.color] || 'accent-white'}`}
                  style={{ WebkitAppearance: 'none' }} />
              </div>
            );
          })}
        </div>

        {/* Hub Status */}
        <div className="p-1.5 bg-karau-bg/30 rounded-lg border border-white/5 text-[8px] flex items-center justify-between" data-testid="hub-status">
          <span className="text-slate-400">Hub: {roomState?.hub_type || 'AI KARAU IoT Bridge'}</span>
          <Badge className={`text-[7px] ${roomState?.hub_connected ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'}`}>
            {roomState?.hub_connected ? 'Connected' : 'Disconnected'}
          </Badge>
        </div>
      </div>
    </div>
  );
}
