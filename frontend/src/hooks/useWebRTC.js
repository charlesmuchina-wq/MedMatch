import { useRef, useState, useCallback } from 'react';

const API = process.env.REACT_APP_BACKEND_URL;
const WS_URL = API.replace('https://', 'wss://').replace('http://', 'ws://');

export function useWebRTC(webinarId, speakerDetection) {
  const localVideoRef = useRef(null);
  const localStreamRef = useRef(null);
  const peerConnectionsRef = useRef({});
  const remoteStreamsRef = useRef({});
  const [remoteStreams, setRemoteStreams] = useState({});
  const wsRef = useRef(null);
  const reconnectRef = useRef(null);

  const createPeerConnection = useCallback(async (remoteUserId, remoteName, createOffer) => {
    if (peerConnectionsRef.current[remoteUserId]) return;
    const pc = new RTCPeerConnection({ iceServers: [{ urls: 'stun:stun.l.google.com:19302' }] });
    peerConnectionsRef.current[remoteUserId] = pc;

    if (localStreamRef.current) {
      localStreamRef.current.getTracks().forEach(track => pc.addTrack(track, localStreamRef.current));
    }

    pc.ontrack = (event) => {
      const [stream] = event.streams;
      remoteStreamsRef.current[remoteUserId] = stream;
      setRemoteStreams(prev => ({ ...prev, [remoteUserId]: { stream, name: remoteName } }));
      speakerDetection.addStream(remoteUserId, remoteName, stream);
    };

    pc.onicecandidate = (event) => {
      if (event.candidate && wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: 'ice_candidate', target_user_id: remoteUserId, candidate: event.candidate.toJSON() }));
      }
    };

    if (createOffer) {
      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);
      wsRef.current?.send(JSON.stringify({ type: 'offer', target_user_id: remoteUserId, sdp: offer.sdp }));
    }
  }, [speakerDetection]);

  const handleOffer = useCallback(async (msg) => {
    await createPeerConnection(msg.user_id, msg.user_name || 'Peer', false);
    const pc = peerConnectionsRef.current[msg.user_id];
    if (!pc) return;
    await pc.setRemoteDescription(new RTCSessionDescription({ type: 'offer', sdp: msg.sdp }));
    const answer = await pc.createAnswer();
    await pc.setLocalDescription(answer);
    wsRef.current?.send(JSON.stringify({ type: 'answer', target_user_id: msg.user_id, sdp: answer.sdp }));
  }, [createPeerConnection]);

  const handleAnswer = useCallback(async (msg) => {
    const pc = peerConnectionsRef.current[msg.user_id];
    if (pc) await pc.setRemoteDescription(new RTCSessionDescription({ type: 'answer', sdp: msg.sdp }));
  }, []);

  const handleIceCandidate = useCallback(async (msg) => {
    const pc = peerConnectionsRef.current[msg.user_id];
    if (pc && msg.candidate) await pc.addIceCandidate(new RTCIceCandidate(msg.candidate));
  }, []);

  const closePeerConnection = useCallback((userId) => {
    if (peerConnectionsRef.current[userId]) {
      peerConnectionsRef.current[userId].close();
      delete peerConnectionsRef.current[userId];
    }
    delete remoteStreamsRef.current[userId];
    speakerDetection.removeStream(userId);
    setRemoteStreams(prev => { const next = { ...prev }; delete next[userId]; return next; });
  }, [speakerDetection]);

  const connectWebSocket = useCallback((info, onSlideChange, fetchRoomInfo) => {
    const token = localStorage.getItem('token');
    const wsUrl = `${WS_URL}/api/karau-meet/ws/webinar-${webinarId}?token=${token}&user_name=${encodeURIComponent(info.host_name || 'User')}&is_host=${info.my_role === 'host'}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => console.log('WebRTC WS connected');
    ws.onmessage = async (event) => {
      try {
        const msg = JSON.parse(event.data);
        switch (msg.type) {
          case 'user_joined': if (info.can_stream_video) createPeerConnection(msg.user_id, msg.user_name, true); break;
          case 'user_left': closePeerConnection(msg.user_id); break;
          case 'offer': await handleOffer(msg); break;
          case 'answer': await handleAnswer(msg); break;
          case 'ice_candidate': await handleIceCandidate(msg); break;
          case 'role_changed': fetchRoomInfo(); break;
          case 'slide_change': onSlideChange(msg.slide_index || 0); break;
          default: break;
        }
      } catch (e) { console.error('WS message error:', e); }
    };
    ws.onclose = () => { reconnectRef.current = setTimeout(() => connectWebSocket(info, onSlideChange, fetchRoomInfo), 3000); };
  }, [webinarId, createPeerConnection, closePeerConnection, handleOffer, handleAnswer, handleIceCandidate]);

  const startLocalMedia = useCallback(async (video, audio, noiseCancellation, hostName) => {
    try {
      let stream = await navigator.mediaDevices.getUserMedia({ video, audio });
      if (noiseCancellation?.isSupported && audio) {
        try { stream = await noiseCancellation.applyToStream(stream); } catch {}
      }
      localStreamRef.current = stream;
      if (localVideoRef.current) localVideoRef.current.srcObject = stream;
      speakerDetection.addLocalStream(hostName || 'You', stream);
      return { video, audio };
    } catch (e) {
      console.error('Media error:', e);
      return null;
    }
  }, [speakerDetection]);

  const cleanup = useCallback(() => {
    if (localStreamRef.current) localStreamRef.current.getTracks().forEach(t => t.stop());
    Object.values(peerConnectionsRef.current).forEach(pc => pc.close());
    peerConnectionsRef.current = {};
    if (wsRef.current) wsRef.current.close();
    if (reconnectRef.current) clearTimeout(reconnectRef.current);
  }, []);

  return {
    localVideoRef, localStreamRef, wsRef,
    remoteStreams, cleanup,
    connectWebSocket, startLocalMedia,
  };
}
