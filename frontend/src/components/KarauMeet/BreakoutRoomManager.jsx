/**
 * BreakoutRoomManager - Host UI for creating and managing breakout rooms
 * Supports manual assignment, AI auto-assign, timer, and room management
 */
import { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import {
  Users, Plus, Trash2, Shuffle, Clock, Play, Square,
  ArrowRight, ChevronDown, ChevronUp, Loader2, Sparkles, X
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ScrollArea } from '@/components/ui/scroll-area';

const API = process.env.REACT_APP_BACKEND_URL;

const BreakoutRoomManager = ({ meetingId, participants, isHost, onClose }) => {
  const [mode, setMode] = useState('setup'); // setup | active | closed
  const [rooms, setRooms] = useState([
    { room_name: 'Room 1', participant_ids: [] },
    { room_name: 'Room 2', participant_ids: [] },
  ]);
  const [timerMinutes, setTimerMinutes] = useState(5);
  const [useTimer, setUseTimer] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [activeSession, setActiveSession] = useState(null);
  const [timeRemaining, setTimeRemaining] = useState(null);
  const [expandedRoom, setExpandedRoom] = useState(null);

  const token = localStorage.getItem('token');
  const headers = { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` };

  // Non-host participants (excludable from assignment)
  const nonHostParticipants = participants.filter(p => !p.is_host);
  const assignedIds = rooms.flatMap(r => r.participant_ids);
  const unassigned = nonHostParticipants.filter(p => !assignedIds.includes(p.user_id));

  // Poll active session
  useEffect(() => {
    const checkSession = async () => {
      try {
        const res = await fetch(`${API}/api/karau-meet/meetings/${meetingId}/breakout-session`, { headers });
        if (res.ok) {
          const data = await res.json();
          if (data.status === 'active') {
            setActiveSession(data.session);
            setMode('active');
          } else if (data.status === 'expired') {
            setActiveSession(data.session);
            setMode('active');
          }
        }
      } catch {}
    };
    checkSession();
  }, [meetingId]);

  // Timer countdown
  useEffect(() => {
    if (!activeSession || !activeSession.ends_at) return;
    const tick = () => {
      const end = new Date(activeSession.ends_at).getTime();
      const now = Date.now();
      const diff = Math.max(0, Math.floor((end - now) / 1000));
      setTimeRemaining(diff);
      if (diff <= 0) {
        setTimeRemaining(0);
      }
    };
    tick();
    const interval = setInterval(tick, 1000);
    return () => clearInterval(interval);
  }, [activeSession]);

  // Add room
  const addRoom = () => {
    if (rooms.length >= 10) return toast.error('Maximum 10 rooms');
    setRooms([...rooms, { room_name: `Room ${rooms.length + 1}`, participant_ids: [] }]);
  };

  // Remove room
  const removeRoom = (idx) => {
    if (rooms.length <= 1) return;
    const removed = rooms[idx];
    const newRooms = rooms.filter((_, i) => i !== idx);
    // Return removed participants to unassigned
    setRooms(newRooms);
  };

  // Rename room
  const renameRoom = (idx, name) => {
    const newRooms = [...rooms];
    newRooms[idx] = { ...newRooms[idx], room_name: name };
    setRooms(newRooms);
  };

  // Assign participant to room
  const assignToRoom = (userId, roomIdx) => {
    // Remove from any current room
    const newRooms = rooms.map(r => ({
      ...r,
      participant_ids: r.participant_ids.filter(id => id !== userId)
    }));
    // Add to target room (max 10)
    if (newRooms[roomIdx].participant_ids.length >= 10) {
      toast.error('Room full (max 10)');
      return;
    }
    newRooms[roomIdx] = {
      ...newRooms[roomIdx],
      participant_ids: [...newRooms[roomIdx].participant_ids, userId]
    };
    setRooms(newRooms);
  };

  // Remove participant from room
  const removeFromRoom = (userId, roomIdx) => {
    const newRooms = [...rooms];
    newRooms[roomIdx] = {
      ...newRooms[roomIdx],
      participant_ids: newRooms[roomIdx].participant_ids.filter(id => id !== userId)
    };
    setRooms(newRooms);
  };

  // AI auto-assign
  const autoAssign = async () => {
    setIsLoading(true);
    try {
      const res = await fetch(
        `${API}/api/karau-meet/meetings/${meetingId}/breakout-session/auto-assign?num_rooms=${rooms.length}`,
        { method: 'POST', headers }
      );
      if (res.ok) {
        const data = await res.json();
        const newRooms = data.rooms.map((r, i) => ({
          room_name: rooms[i]?.room_name || r.room_name,
          participant_ids: r.participant_ids
        }));
        setRooms(newRooms);
        toast.success(`AI assigned ${data.total_participants} participants`);
      } else {
        toast.error('Auto-assign failed');
      }
    } catch {
      toast.error('Connection error');
    }
    setIsLoading(false);
  };

  // Start breakout session
  const startSession = async () => {
    const nonEmpty = rooms.filter(r => r.participant_ids.length > 0);
    if (nonEmpty.length === 0) {
      toast.error('Assign at least one participant');
      return;
    }
    setIsLoading(true);
    try {
      const res = await fetch(`${API}/api/karau-meet/meetings/${meetingId}/breakout-session/start`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          rooms: nonEmpty,
          timer_minutes: useTimer ? timerMinutes : 0,
          auto_assign: false
        })
      });
      if (res.ok) {
        const session = await res.json();
        setActiveSession(session);
        setMode('active');
        toast.success('Breakout rooms started!');
      } else {
        toast.error('Failed to start breakout rooms');
      }
    } catch {
      toast.error('Connection error');
    }
    setIsLoading(false);
  };

  // Close session
  const closeSession = async () => {
    setIsLoading(true);
    try {
      const res = await fetch(`${API}/api/karau-meet/meetings/${meetingId}/breakout-session/close`, {
        method: 'POST',
        headers
      });
      if (res.ok) {
        const data = await res.json();
        setMode('closed');
        setActiveSession(null);
        toast.success(`${data.returned_count} participants returned to main room`);
        setTimeout(() => onClose?.(), 1500);
      } else {
        toast.error('Failed to close breakout rooms');
      }
    } catch {
      toast.error('Connection error');
    }
    setIsLoading(false);
  };

  // Get participant name from ID
  const getName = (userId) => {
    const p = participants.find(pp => pp.user_id === userId);
    return p?.user_name || userId.slice(0, 8);
  };

  // Format seconds to mm:ss
  const formatTime = (secs) => {
    if (secs === null) return '--:--';
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  if (!isHost) return null;

  return (
    <div className="flex flex-col h-full bg-slate-900" data-testid="breakout-room-manager">
      {/* Header */}
      <div className="p-3 border-b border-slate-700 flex items-center justify-between">
        <h3 className="font-semibold text-white flex items-center gap-2 text-sm">
          <Users className="w-4 h-4 text-[#5b5fc7]" />
          Breakout Rooms
        </h3>
        <Button variant="ghost" size="sm" className="h-6 w-6 p-0 text-slate-400" onClick={onClose}>
          <X className="w-4 h-4" />
        </Button>
      </div>

      {/* Setup Mode */}
      {mode === 'setup' && (
        <ScrollArea className="flex-1">
          <div className="p-3 space-y-4">
            {/* Actions */}
            <div className="flex items-center gap-2">
              <Button
                size="sm"
                variant="outline"
                className="h-8 text-xs border-slate-600 text-slate-300 hover:text-white"
                onClick={addRoom}
                data-testid="add-room-btn"
              >
                <Plus className="w-3 h-3 mr-1" /> Add Room
              </Button>
              <Button
                size="sm"
                variant="outline"
                className="h-8 text-xs border-[#5b5fc7] text-[#5b5fc7] hover:bg-[#5b5fc7] hover:text-white"
                onClick={autoAssign}
                disabled={isLoading}
                data-testid="auto-assign-btn"
              >
                {isLoading ? <Loader2 className="w-3 h-3 mr-1 animate-spin" /> : <Sparkles className="w-3 h-3 mr-1" />}
                AI Auto-Assign
              </Button>
            </div>

            {/* Unassigned pool */}
            {unassigned.length > 0 && (
              <div className="bg-slate-800/50 rounded-lg p-3 border border-slate-700/50">
                <p className="text-xs text-slate-400 mb-2">Unassigned ({unassigned.length})</p>
                <div className="flex flex-wrap gap-1.5">
                  {unassigned.map(p => (
                    <div
                      key={p.user_id}
                      className="group relative"
                    >
                      <Badge className="bg-slate-700 text-slate-300 text-xs cursor-pointer hover:bg-slate-600" data-testid={`unassigned-${p.user_id}`}>
                        {p.user_name?.slice(0, 15)}
                      </Badge>
                      {/* Quick-assign dropdown */}
                      <div className="absolute top-full left-0 hidden group-hover:flex flex-col bg-slate-700 rounded-md shadow-lg z-20 mt-1 min-w-[100px]">
                        {rooms.map((r, rIdx) => (
                          <button
                            key={rIdx}
                            className="text-left px-2 py-1 text-[10px] text-slate-300 hover:bg-slate-600 whitespace-nowrap"
                            onClick={() => assignToRoom(p.user_id, rIdx)}
                          >
                            <ArrowRight className="w-2.5 h-2.5 inline mr-1" /> {r.room_name}
                          </button>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Room cards */}
            {rooms.map((room, idx) => (
              <div key={idx} className="bg-slate-800 rounded-lg border border-slate-700" data-testid={`room-card-${idx}`}>
                <div
                  className="flex items-center justify-between p-2.5 cursor-pointer"
                  onClick={() => setExpandedRoom(expandedRoom === idx ? null : idx)}
                >
                  <div className="flex items-center gap-2 min-w-0">
                    <Input
                      value={room.room_name}
                      onChange={e => renameRoom(idx, e.target.value)}
                      className="h-7 text-xs bg-transparent border-0 text-white p-0 focus-visible:ring-0 w-24"
                      onClick={e => e.stopPropagation()}
                      data-testid={`room-name-${idx}`}
                    />
                    <Badge className="bg-slate-700 text-slate-400 text-[10px]">
                      {room.participant_ids.length}/10
                    </Badge>
                  </div>
                  <div className="flex items-center gap-1">
                    {rooms.length > 1 && (
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-6 w-6 p-0 text-slate-500 hover:text-red-400"
                        onClick={e => { e.stopPropagation(); removeRoom(idx); }}
                        data-testid={`remove-room-${idx}`}
                      >
                        <Trash2 className="w-3 h-3" />
                      </Button>
                    )}
                    {expandedRoom === idx ? <ChevronUp className="w-3 h-3 text-slate-500" /> : <ChevronDown className="w-3 h-3 text-slate-500" />}
                  </div>
                </div>

                {expandedRoom === idx && (
                  <div className="px-2.5 pb-2.5 space-y-1.5 border-t border-slate-700/50 pt-2">
                    {room.participant_ids.length === 0 ? (
                      <p className="text-[10px] text-slate-500 italic">No participants assigned</p>
                    ) : (
                      room.participant_ids.map(uid => (
                        <div key={uid} className="flex items-center justify-between bg-slate-700/50 rounded px-2 py-1">
                          <span className="text-xs text-slate-300">{getName(uid)}</span>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-5 w-5 p-0 text-slate-500 hover:text-red-400"
                            onClick={() => removeFromRoom(uid, idx)}
                          >
                            <X className="w-3 h-3" />
                          </Button>
                        </div>
                      ))
                    )}

                    {/* Assign from unassigned */}
                    {unassigned.length > 0 && (
                      <Select onValueChange={(uid) => assignToRoom(uid, idx)}>
                        <SelectTrigger className="h-7 bg-slate-700/30 border-slate-600 text-xs text-slate-400">
                          <SelectValue placeholder="+ Add participant" />
                        </SelectTrigger>
                        <SelectContent className="bg-slate-700 border-slate-600">
                          {unassigned.map(p => (
                            <SelectItem key={p.user_id} value={p.user_id} className="text-xs text-slate-300">
                              {p.user_name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    )}
                  </div>
                )}
              </div>
            ))}

            {/* Timer setting */}
            <div className="bg-slate-800/50 rounded-lg p-3 border border-slate-700/50 space-y-2">
              <div className="flex items-center justify-between">
                <Label className="text-xs text-slate-300 flex items-center gap-1.5">
                  <Clock className="w-3 h-3" /> Auto-return timer
                </Label>
                <button
                  onClick={() => setUseTimer(!useTimer)}
                  className={`w-8 h-4 rounded-full transition-colors ${useTimer ? 'bg-[#5b5fc7]' : 'bg-slate-600'}`}
                  data-testid="timer-toggle"
                >
                  <div className={`w-3 h-3 bg-white rounded-full transition-transform ${useTimer ? 'translate-x-4' : 'translate-x-0.5'}`} />
                </button>
              </div>
              {useTimer && (
                <div className="flex items-center gap-2">
                  {[3, 5, 10, 15, 20].map(m => (
                    <button
                      key={m}
                      onClick={() => setTimerMinutes(m)}
                      className={`px-2 py-1 rounded text-[10px] transition-colors ${
                        timerMinutes === m
                          ? 'bg-[#5b5fc7] text-white'
                          : 'bg-slate-700 text-slate-400 hover:bg-slate-600'
                      }`}
                      data-testid={`timer-${m}m`}
                    >
                      {m}m
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Start button */}
            <Button
              className="w-full bg-[#5b5fc7] hover:bg-[#4e52b5] text-white h-10"
              onClick={startSession}
              disabled={isLoading}
              data-testid="start-breakout-btn"
            >
              {isLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Play className="w-4 h-4 mr-2" />}
              Open Rooms
            </Button>
          </div>
        </ScrollArea>
      )}

      {/* Active Mode */}
      {mode === 'active' && activeSession && (
        <ScrollArea className="flex-1">
          <div className="p-3 space-y-3">
            {/* Timer */}
            {activeSession.ends_at && (
              <div className={`rounded-lg p-3 text-center ${
                timeRemaining !== null && timeRemaining <= 60 ? 'bg-red-500/20 border border-red-500/30' : 'bg-slate-800 border border-slate-700'
              }`} data-testid="breakout-timer">
                <div className="flex items-center justify-center gap-2">
                  <Clock className={`w-4 h-4 ${timeRemaining !== null && timeRemaining <= 60 ? 'text-red-400' : 'text-slate-400'}`} />
                  <span className={`text-2xl font-mono font-bold ${
                    timeRemaining !== null && timeRemaining <= 60 ? 'text-red-400' : 'text-white'
                  }`}>
                    {formatTime(timeRemaining)}
                  </span>
                </div>
                <p className="text-xs text-slate-500 mt-1">
                  {timeRemaining === 0 ? 'Time expired — close rooms' : 'until auto-return'}
                </p>
              </div>
            )}

            {/* Active rooms */}
            {activeSession.rooms?.map((room, idx) => (
              <div key={room.room_id} className="bg-slate-800 rounded-lg border border-slate-700 p-3" data-testid={`active-room-${idx}`}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-white">{room.room_name}</span>
                  <Badge className="bg-slate-700 text-slate-400 text-[10px]">
                    {room.participants?.length || 0}/10
                  </Badge>
                </div>
                <div className="space-y-1">
                  {room.participants?.map(uid => (
                    <div key={uid} className="flex items-center justify-between bg-slate-700/50 rounded px-2 py-1">
                      <span className="text-xs text-slate-300">{getName(uid)}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}

            {/* Close button */}
            <Button
              variant="destructive"
              className="w-full h-10"
              onClick={closeSession}
              disabled={isLoading}
              data-testid="close-breakout-btn"
            >
              {isLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Square className="w-4 h-4 mr-2" />}
              Close All Rooms
            </Button>
          </div>
        </ScrollArea>
      )}

      {/* Closed state */}
      {mode === 'closed' && (
        <div className="flex-1 flex items-center justify-center p-6">
          <div className="text-center">
            <Users className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
            <p className="text-white text-sm font-medium">Everyone returned</p>
            <p className="text-slate-500 text-xs mt-1">Breakout session ended</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default BreakoutRoomManager;
