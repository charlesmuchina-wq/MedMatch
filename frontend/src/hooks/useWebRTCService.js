/**
 * WebRTC Peer Connection Service Hook
 * Manages peer-to-peer connections via the signaling server.
 * Features: ICE candidate handling, reconnection, media track management.
 */
import { useRef, useCallback, useState, useEffect } from 'react';

const API = process.env.REACT_APP_BACKEND_URL;

// Default ICE servers (STUN)
const DEFAULT_ICE_SERVERS = [
  { urls: ['stun:stun.l.google.com:19302'] },
  { urls: ['stun:stun1.l.google.com:19302'] },
];

export function useWebRTCService({ meetingId, userId, userName, isHost = false }) {
  const [peers, setPeers] = useState({});       // userId -> { pc, streams, state }
  const [connected, setConnected] = useState(false);
  const [participants, setParticipants] = useState([]);
  const wsRef = useRef(null);
  const peerConnectionsRef = useRef({});
  const localStreamRef = useRef(null);
  const iceServersRef = useRef(DEFAULT_ICE_SERVERS);
  const sessionTokenRef = useRef(null);
  const reconnectRef = useRef(null);

  /**
   * Create a new peer connection for a remote user
   */
  const createPeerConnection = useCallback((remoteUserId) => {
    const config = { iceServers: iceServersRef.current };
    const pc = new RTCPeerConnection(config);

    // Add local tracks
    if (localStreamRef.current) {
      localStreamRef.current.getTracks().forEach(track => {
        pc.addTrack(track, localStreamRef.current);
      });
    }

    // ICE candidate events
    pc.onicecandidate = (event) => {
      if (event.candidate && wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({
          type: 'ice_candidate',
          target: remoteUserId,
          candidate: event.candidate.toJSON()
        }));
      }
    };

    // Track events
    pc.ontrack = (event) => {
      setPeers(prev => ({
        ...prev,
        [remoteUserId]: {
          ...prev[remoteUserId],
          streams: event.streams,
          state: 'connected'
        }
      }));
    };

    // Connection state
    pc.onconnectionstatechange = () => {
      setPeers(prev => ({
        ...prev,
        [remoteUserId]: {
          ...prev[remoteUserId],
          state: pc.connectionState
        }
      }));

      if (pc.connectionState === 'failed') {
        // Attempt ICE restart
        pc.restartIce();
      }
    };

    peerConnectionsRef.current[remoteUserId] = pc;
    return pc;
  }, []);

  /**
   * Connect to signaling server
   */
  const connect = useCallback(async (localStream) => {
    localStreamRef.current = localStream;

    // Fetch ICE servers
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${API}/api/karau/webrtc/ice-servers`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        if (data.ice_servers?.length) {
          iceServersRef.current = data.ice_servers;
        }
      }
    } catch {}

    // Connect WebSocket
    const wsProtocol = API.startsWith('https') ? 'wss' : 'ws';
    const wsUrl = `${wsProtocol}://${API.replace(/^https?:\/\//, '')}/api/karau-meet/ws/${meetingId}?user_id=${userId}&user_name=${encodeURIComponent(userName)}&is_host=${isHost}${sessionTokenRef.current ? `&session_token=${sessionTokenRef.current}` : ''}`;

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
      // Start ping interval
      const pingInterval = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: 'ping' }));
        }
      }, 10000);
      ws._pingInterval = pingInterval;
    };

    ws.onmessage = async (event) => {
      const data = JSON.parse(event.data);

      switch (data.type) {
        case 'room_state':
          sessionTokenRef.current = data.session_token;
          setParticipants(data.participants || []);
          // Create offers to existing participants
          for (const participant of data.participants || []) {
            if (participant.user_id !== userId) {
              const pc = createPeerConnection(participant.user_id);
              const offer = await pc.createOffer();
              await pc.setLocalDescription(offer);
              ws.send(JSON.stringify({
                type: 'offer',
                target: participant.user_id,
                offer: pc.localDescription.toJSON()
              }));
            }
          }
          break;

        case 'user_joined':
          setParticipants(data.participants || []);
          break;

        case 'user_left':
          setParticipants(data.participants || []);
          // Cleanup peer connection
          const leavingPc = peerConnectionsRef.current[data.user_id];
          if (leavingPc) {
            leavingPc.close();
            delete peerConnectionsRef.current[data.user_id];
            setPeers(prev => {
              const next = { ...prev };
              delete next[data.user_id];
              return next;
            });
          }
          break;

        case 'offer':
          {
            let pc = peerConnectionsRef.current[data.from_user] || createPeerConnection(data.from_user);
            await pc.setRemoteDescription(new RTCSessionDescription(data.offer));
            const answer = await pc.createAnswer();
            await pc.setLocalDescription(answer);
            ws.send(JSON.stringify({
              type: 'answer',
              target: data.from_user,
              answer: pc.localDescription.toJSON()
            }));
          }
          break;

        case 'answer':
          {
            const pc = peerConnectionsRef.current[data.from_user];
            if (pc) await pc.setRemoteDescription(new RTCSessionDescription(data.answer));
          }
          break;

        case 'ice_candidate':
          {
            const pc = peerConnectionsRef.current[data.from_user];
            if (pc && data.candidate) {
              await pc.addIceCandidate(new RTCIceCandidate(data.candidate));
            }
          }
          break;

        case 'participant_state_changed':
          setParticipants(data.participants || []);
          break;

        case 'pong':
          // Heartbeat acknowledged
          break;

        default:
          break;
      }
    };

    ws.onclose = () => {
      setConnected(false);
      clearInterval(ws._pingInterval);
      // Auto-reconnect after 3s
      reconnectRef.current = setTimeout(() => {
        if (localStreamRef.current) {
          connect(localStreamRef.current);
        }
      }, 3000);
    };

    ws.onerror = () => {
      console.warn('WebRTC signaling WebSocket error');
    };
  }, [meetingId, userId, userName, isHost, createPeerConnection]);

  /**
   * Disconnect from signaling server and cleanup
   */
  const disconnect = useCallback(() => {
    if (reconnectRef.current) clearTimeout(reconnectRef.current);
    Object.values(peerConnectionsRef.current).forEach(pc => pc.close());
    peerConnectionsRef.current = {};
    setPeers({});
    if (wsRef.current) {
      clearInterval(wsRef.current._pingInterval);
      wsRef.current.close();
      wsRef.current = null;
    }
    setConnected(false);
  }, []);

  /**
   * Send media state update (mute/video toggle)
   */
  const sendMediaState = useCallback((state) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'state_update', state }));
    }
  }, []);

  /**
   * Replace a track (e.g., switching camera, adding screen share)
   */
  const replaceTrack = useCallback(async (newTrack, kind) => {
    for (const pc of Object.values(peerConnectionsRef.current)) {
      const sender = pc.getSenders().find(s => s.track?.kind === kind);
      if (sender) {
        await sender.replaceTrack(newTrack);
      }
    }
  }, []);

  useEffect(() => {
    return () => disconnect();
  }, [disconnect]);

  return {
    connect,
    disconnect,
    connected,
    peers,
    participants,
    sendMediaState,
    replaceTrack,
    ws: wsRef
  };
}

export default useWebRTCService;
