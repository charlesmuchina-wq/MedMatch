import { useState, useEffect, useCallback } from 'react';
import { Cpu, Wifi, WifiOff, Camera, Mic, MonitorSmartphone, Glasses, Speaker, ScanSearch, ToggleLeft, ToggleRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;

const TYPE_CONFIG = {
  camera_360: { icon: Camera, label: '360 Camera', color: 'orange' },
  mic_array: { icon: Mic, label: 'Mic Array', color: 'sky' },
  iot_hub: { icon: Cpu, label: 'IoT Hub', color: 'amber' },
  xr_headset: { icon: Glasses, label: 'XR Headset', color: 'violet' },
  display: { icon: MonitorSmartphone, label: 'Display', color: 'blue' },
  speaker_array: { icon: Speaker, label: 'Speakers', color: 'emerald' },
};

const STATUS_BADGE = {
  online: 'bg-emerald-500/10 text-emerald-400',
  offline: 'bg-red-500/10 text-red-400',
  standby: 'bg-amber-500/10 text-amber-400',
  error: 'bg-red-500/10 text-red-400',
};

export default function HardwareDiscoveryPanel({ meetingId }) {
  const [data, setData] = useState(null);
  const [scanning, setScanning] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchDevices = useCallback(async () => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau/hardware/${meetingId}/devices`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) setData(await res.json());
    } catch {}
    setLoading(false);
  }, [meetingId]);

  useEffect(() => { fetchDevices(); }, [fetchDevices]);

  const scanDevices = async () => {
    setScanning(true);
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau/hardware/${meetingId}/scan`, {
        method: 'POST', headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) { toast.success('Scan complete'); fetchDevices(); }
    } catch {}
    setScanning(false);
  };

  const toggleMode = async (deviceId, currentMode) => {
    const token = localStorage.getItem('token');
    const newMode = currentMode === 'live' ? 'simulation' : 'live';
    try {
      await fetch(`${API}/api/karau/hardware/${meetingId}/status`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ device_id: deviceId, status: 'online', mode: newMode })
      });
      toast.success(`${deviceId} switched to ${newMode}`);
      fetchDevices();
    } catch {}
  };

  if (loading) return <div className="p-3 text-[9px] text-slate-500 animate-soft-pulse">Discovering devices...</div>;

  const devices = data?.devices || [];

  return (
    <div className="flex-1 flex flex-col overflow-hidden" data-testid="hardware-discovery-panel">
      <div className="p-3 border-b border-white/[0.06]">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-lime-500/20 to-green-500/10 flex items-center justify-center">
            <Cpu className="w-3.5 h-3.5 text-lime-400" />
          </div>
          <div>
            <h3 className="text-xs font-semibold text-white">Hardware Discovery</h3>
            <p className="text-[9px] text-slate-500">Detect & manage devices</p>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        {/* Scan Button + Summary */}
        <div className="flex items-center justify-between">
          <Button size="sm" onClick={scanDevices} disabled={scanning}
            className={`h-6 text-[9px] bg-lime-500/80 hover:bg-lime-400 rounded-lg hover-scale transition-all ${scanning ? 'animate-pulse-glow' : ''}`} data-testid="scan-devices-btn">
            <ScanSearch className={`w-3 h-3 mr-1 ${scanning ? 'animate-scan-rotate' : ''}`} />{scanning ? 'Scanning...' : 'Scan Devices'}
          </Button>
          <div className="flex gap-2 text-[8px]">
            <span className="text-emerald-400">{data?.online || 0} online</span>
            <span className="text-slate-400">{data?.simulation_mode || 0} sim</span>
          </div>
        </div>

        {/* Device Cards */}
        <div className="space-y-1.5" data-testid="device-list">
          {devices.map(d => {
            const cfg = TYPE_CONFIG[d.device_type] || TYPE_CONFIG.display;
            const Icon = cfg.icon;
            const colorClass = {
              orange: 'border-orange-500/15 bg-orange-500/5',
              sky: 'border-sky-500/15 bg-sky-500/5',
              amber: 'border-amber-500/15 bg-amber-500/5',
              violet: 'border-violet-500/15 bg-violet-500/5',
              blue: 'border-blue-500/15 bg-blue-500/5',
              emerald: 'border-emerald-500/15 bg-emerald-500/5',
            };

            return (
              <div key={d.device_id} className={`p-2 rounded-lg border ${colorClass[cfg.color] || ''}`} data-testid={`device-${d.device_id}`}>
                <div className="flex items-center gap-2">
                  <Icon className="w-4 h-4 text-white shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-[10px] text-white font-medium truncate">{d.name}</p>
                    <p className="text-[8px] text-slate-400">{d.manufacturer} {d.model}</p>
                  </div>
                  <Badge className={`text-[7px] ${STATUS_BADGE[d.status] || STATUS_BADGE.offline}`}>
                    {d.status}
                  </Badge>
                </div>

                {/* Capabilities */}
                <div className="flex flex-wrap gap-0.5 mt-1.5">
                  {(d.capabilities || []).slice(0, 4).map(cap => (
                    <span key={cap} className="text-[6px] px-1 py-0.5 rounded bg-white/5 text-slate-400">{cap}</span>
                  ))}
                </div>

                {/* Mode Toggle + Battery */}
                <div className="flex items-center justify-between mt-1.5">
                  <button onClick={() => toggleMode(d.device_id, d.mode)}
                    className="flex items-center gap-1 text-[8px]"
                    data-testid={`toggle-${d.device_id}`}>
                    {d.mode === 'live' ? (
                      <><ToggleRight className="w-4 h-4 text-emerald-400" /><span className="text-emerald-400">Live</span></>
                    ) : (
                      <><ToggleLeft className="w-4 h-4 text-slate-400" /><span className="text-slate-400">Simulation</span></>
                    )}
                  </button>
                  <div className="flex items-center gap-2 text-[7px] text-slate-500">
                    {d.battery_percent !== null && d.battery_percent !== undefined && (
                      <span>{d.battery_percent}%</span>
                    )}
                    {d.signal_strength !== null && d.signal_strength !== undefined && (
                      <span className="flex items-center gap-0.5">
                        <Wifi className="w-2 h-2" />{Math.round(d.signal_strength * 100)}%
                      </span>
                    )}
                    <span className="text-[6px]">{d.connection_type}</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
