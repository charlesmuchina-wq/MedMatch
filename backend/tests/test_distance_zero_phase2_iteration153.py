"""
Distance Zero Phase 2 Backend API Tests - Iteration 153
Tests for: SLAM Spatial, 360 Framing, WebXR, IoT Control, Beamforming, Meeting Replay
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAuth:
    """Authentication to get token for subsequent tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token for admin user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
        pytest.skip("Authentication failed - skipping authenticated tests")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Auth headers fixture"""
        return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}


class TestSLAMSpatialTracking(TestAuth):
    """SLAM Spatial Awareness & 360 Framing API Tests"""
    
    MEETING_ID = "test-slam-meeting-153"
    
    def test_get_spatial_tracking(self, auth_headers):
        """GET /api/karau/spatial/{meeting_id}/tracking - Get SLAM tracking data"""
        response = requests.get(
            f"{BASE_URL}/api/karau/spatial/{self.MEETING_ID}/tracking",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        # Verify structure
        assert "meeting_id" in data
        assert "positions" in data
        assert "frame_adjustments" in data
        assert "room_lighting" in data
        assert "slam_status" in data
        # Verify positions have user data
        positions = data["positions"]
        assert len(positions) > 0, "Expected simulated positions"
        first_pos = positions[0]
        assert "user_id" in first_pos
        assert "x" in first_pos
        assert "y" in first_pos
        assert "z" in first_pos
        assert "face_confidence" in first_pos
        # Verify frame adjustments match positions
        adjustments = data["frame_adjustments"]
        assert len(adjustments) == len(positions)
        print(f"PASS - Tracking data: {len(positions)} positions, {len(adjustments)} adjustments")
    
    def test_get_spatial_tracking_requires_auth(self):
        """GET /api/karau/spatial/{meeting_id}/tracking requires auth"""
        response = requests.get(f"{BASE_URL}/api/karau/spatial/{self.MEETING_ID}/tracking")
        assert response.status_code == 401, f"Expected 401 without auth, got {response.status_code}"
        print("PASS - Spatial tracking requires auth")
    
    def test_post_room_map_update(self, auth_headers):
        """POST /api/karau/spatial/{meeting_id}/room-map - Update room map"""
        payload = {
            "meeting_id": self.MEETING_ID,
            "room_dimensions": {"width": 6.0, "depth": 5.0, "height": 3.0},
            "positions": [
                {"user_id": "test-user-1", "x": 1.0, "y": 0.1, "z": 2.0, "yaw": 45.0, "pitch": 0.0, "face_confidence": 0.95},
                {"user_id": "test-user-2", "x": -1.0, "y": 0.0, "z": 2.5, "yaw": 135.0, "pitch": 5.0, "face_confidence": 0.92}
            ],
            "lighting_quality": 0.85
        }
        response = requests.post(
            f"{BASE_URL}/api/karau/spatial/{self.MEETING_ID}/room-map",
            headers=auth_headers,
            json=payload
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert data.get("room_map_updated") == True
        assert "frame_adjustments" in data
        assert data.get("tracking_points") == 2
        print(f"PASS - Room map updated with {data['tracking_points']} tracking points")
    
    def test_get_panoramic_headshots(self, auth_headers):
        """GET /api/karau/spatial/{meeting_id}/panoramic/headshots - Get 360 headshots"""
        response = requests.get(
            f"{BASE_URL}/api/karau/spatial/{self.MEETING_ID}/panoramic/headshots",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "meeting_id" in data
        assert "headshots" in data
        assert "panoramic_status" in data
        headshots = data["headshots"]
        assert len(headshots) > 0, "Expected simulated headshots"
        first_hs = headshots[0]
        assert "user_id" in first_hs
        assert "crop_region" in first_hs
        assert "quality_score" in first_hs
        assert "is_speaking" in first_hs
        print(f"PASS - Got {len(headshots)} headshots from panoramic feed")
    
    def test_panoramic_headshots_requires_auth(self):
        """GET /api/karau/spatial/{meeting_id}/panoramic/headshots requires auth"""
        response = requests.get(f"{BASE_URL}/api/karau/spatial/{self.MEETING_ID}/panoramic/headshots")
        assert response.status_code == 401
        print("PASS - Panoramic headshots requires auth")


class TestWebXRSpatialMeetings(TestAuth):
    """Apple Vision Pro / WebXR Spatial Meeting API Tests"""
    
    MEETING_ID = "test-webxr-meeting-153"
    
    def test_post_create_xr_session(self, auth_headers):
        """POST /api/karau/webxr/{meeting_id}/session - Create XR session"""
        payload = {
            "meeting_id": self.MEETING_ID,
            "room_environment": {
                "room_type": "boardroom",
                "capacity": 12,
                "ambient_lighting": 0.7,
                "skybox": "corporate_day"
            },
            "enable_hand_tracking": True,
            "enable_eye_tracking": True,
            "spatial_audio": True
        }
        response = requests.post(
            f"{BASE_URL}/api/karau/webxr/{self.MEETING_ID}/session",
            headers=auth_headers,
            json=payload
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "session_id" in data
        assert "room_environment" in data
        assert "seats" in data
        assert "features" in data
        assert "xr_capabilities" in data
        # Verify XR capabilities
        xr_caps = data["xr_capabilities"]
        assert xr_caps.get("webxr_supported") == True
        assert xr_caps.get("hand_tracking") == True
        print(f"PASS - XR session created with {len(data['seats'])} seats")
    
    def test_get_xr_session(self, auth_headers):
        """GET /api/karau/webxr/{meeting_id}/session - Get XR session"""
        response = requests.get(
            f"{BASE_URL}/api/karau/webxr/{self.MEETING_ID}/session",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "meeting_id" in data
        assert "room_environment" in data
        assert "personas" in data
        assert "features" in data
        print(f"PASS - Got XR session with {len(data.get('personas', []))} personas")
    
    def test_xr_session_requires_auth(self):
        """GET /api/karau/webxr/{meeting_id}/session requires auth"""
        response = requests.get(f"{BASE_URL}/api/karau/webxr/{self.MEETING_ID}/session")
        assert response.status_code == 401
        print("PASS - XR session GET requires auth")
    
    def test_get_spatial_personas(self, auth_headers):
        """GET /api/karau/webxr/{meeting_id}/personas - Get all spatial personas"""
        response = requests.get(
            f"{BASE_URL}/api/karau/webxr/{self.MEETING_ID}/personas",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "meeting_id" in data
        assert "personas" in data
        assert "count" in data
        personas = data["personas"]
        if len(personas) > 0:
            first_p = personas[0]
            assert "user_id" in first_p
            assert "position" in first_p
            assert "headset_type" in first_p
        print(f"PASS - Got {data['count']} spatial personas")
    
    def test_get_room_layout_public(self):
        """GET /api/karau/webxr/{meeting_id}/room-layout - Public endpoint (no auth)"""
        response = requests.get(f"{BASE_URL}/api/karau/webxr/{self.MEETING_ID}/room-layout")
        assert response.status_code == 200, f"Expected 200 (public), got {response.status_code}"
        data = response.json()
        assert "room_type" in data
        assert "dimensions" in data
        assert "seats" in data
        assert "objects" in data
        assert "lighting" in data
        print(f"PASS - Room layout is public, {len(data['seats'])} seats, {len(data['objects'])} objects")


class TestIoTRoomControl(TestAuth):
    """IoT Room Environmental Control API Tests"""
    
    MEETING_ID = "test-iot-meeting-153"
    
    def test_get_room_state(self, auth_headers):
        """GET /api/karau/iot/{meeting_id}/state - Get room device states"""
        response = requests.get(
            f"{BASE_URL}/api/karau/iot/{self.MEETING_ID}/state",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "meeting_id" in data
        assert "devices" in data
        devices = data["devices"]
        # Verify expected device types
        assert "lights_main" in devices or len(devices) > 0
        assert "hub_connected" in data or "hub_type" in data
        print(f"PASS - Room state has {len(devices)} devices")
    
    def test_room_state_requires_auth(self):
        """GET /api/karau/iot/{meeting_id}/state requires auth"""
        response = requests.get(f"{BASE_URL}/api/karau/iot/{self.MEETING_ID}/state")
        assert response.status_code == 401
        print("PASS - IoT room state requires auth")
    
    def test_post_control_device(self, auth_headers):
        """POST /api/karau/iot/{meeting_id}/device - Control a device"""
        payload = {
            "device_type": "lights",
            "zone": "main",
            "value": 75.0
        }
        response = requests.post(
            f"{BASE_URL}/api/karau/iot/{self.MEETING_ID}/device",
            headers=auth_headers,
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert data.get("device") == "lights_main"
        assert data.get("value") == 75.0
        print(f"PASS - Device controlled: {data['device']} = {data['value']}")
    
    def test_post_apply_preset(self, auth_headers):
        """POST /api/karau/iot/{meeting_id}/preset?preset_name=presentation - Apply preset"""
        response = requests.post(
            f"{BASE_URL}/api/karau/iot/{self.MEETING_ID}/preset?preset_name=presentation",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert data.get("preset") == "presentation"
        assert "devices_updated" in data
        print(f"PASS - Preset 'presentation' applied, {data['devices_updated']} devices updated")
    
    def test_post_apply_invalid_preset(self, auth_headers):
        """POST /api/karau/iot/{meeting_id}/preset - Invalid preset returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/karau/iot/{self.MEETING_ID}/preset?preset_name=invalid_preset",
            headers=auth_headers
        )
        assert response.status_code == 400, f"Expected 400 for invalid preset, got {response.status_code}"
        print("PASS - Invalid preset returns 400")
    
    def test_post_voice_control_dim_lights(self, auth_headers):
        """POST /api/karau/iot/{meeting_id}/voice-control - 'dim lights' command"""
        payload = {
            "command": "dim the lights please",
            "meeting_id": self.MEETING_ID
        }
        response = requests.post(
            f"{BASE_URL}/api/karau/iot/{self.MEETING_ID}/voice-control",
            headers=auth_headers,
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert "command" in data
        assert "actions_taken" in data
        assert "actions" in data
        assert data["actions_taken"] >= 1, "Expected at least 1 action for 'dim lights'"
        actions = data["actions"]
        assert any("lights" in a.get("device", "") for a in actions), "Expected lights action"
        print(f"PASS - Voice 'dim lights': {data['actions_taken']} actions - {[a['label'] for a in actions]}")
    
    def test_post_voice_control_close_shades(self, auth_headers):
        """POST /api/karau/iot/{meeting_id}/voice-control - 'close shades' command"""
        payload = {
            "command": "close the shades",
            "meeting_id": self.MEETING_ID
        }
        response = requests.post(
            f"{BASE_URL}/api/karau/iot/{self.MEETING_ID}/voice-control",
            headers=auth_headers,
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data["actions_taken"] >= 1, "Expected at least 1 action for 'close shades'"
        actions = data["actions"]
        assert any("shades" in a.get("device", "") for a in actions), "Expected shades action"
        print(f"PASS - Voice 'close shades': {data['actions_taken']} actions - {[a['label'] for a in actions]}")
    
    def test_post_voice_control_unrecognized(self, auth_headers):
        """POST /api/karau/iot/{meeting_id}/voice-control - Unrecognized command"""
        payload = {
            "command": "play some music",
            "meeting_id": self.MEETING_ID
        }
        response = requests.post(
            f"{BASE_URL}/api/karau/iot/{self.MEETING_ID}/voice-control",
            headers=auth_headers,
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data["actions_taken"] == 0
        assert data.get("unrecognized") == True
        assert "suggestion" in data
        print(f"PASS - Unrecognized command handled with suggestion: {data['suggestion'][:50]}...")


class TestAdaptiveBeamforming(TestAuth):
    """Adaptive Beamforming Audio API Tests"""
    
    MEETING_ID = "test-beamforming-meeting-153"
    
    def test_get_beamforming_status(self, auth_headers):
        """GET /api/karau/beamforming/{meeting_id}/status - Get beamforming status"""
        response = requests.get(
            f"{BASE_URL}/api/karau/beamforming/{self.MEETING_ID}/status",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "meeting_id" in data
        assert "config" in data
        assert "audio_profiles" in data
        assert "health" in data
        assert "beam_pattern" in data
        # Verify health metrics
        health = data["health"]
        assert "overall_snr_db" in health
        assert "quality_rating" in health
        assert "processing_latency_ms" in health
        # Verify beam pattern has polar data
        beam_pattern = data["beam_pattern"]
        assert len(beam_pattern) > 0, "Expected beam pattern data"
        first_point = beam_pattern[0]
        assert "angle" in first_point
        assert "gain" in first_point
        print(f"PASS - Beamforming status: SNR={health['overall_snr_db']}dB, quality={health['quality_rating']}, {len(beam_pattern)} pattern points")
    
    def test_beamforming_requires_auth(self):
        """GET /api/karau/beamforming/{meeting_id}/status requires auth"""
        response = requests.get(f"{BASE_URL}/api/karau/beamforming/{self.MEETING_ID}/status")
        assert response.status_code == 401
        print("PASS - Beamforming status requires auth")
    
    def test_post_beamforming_config(self, auth_headers):
        """POST /api/karau/beamforming/{meeting_id}/config - Update beamforming config"""
        payload = {
            "mode": "directional",
            "target_angle": 45.0,
            "beam_width": 50.0,
            "noise_gate_threshold": -40.0,
            "echo_cancellation": True,
            "wind_filter": False
        }
        response = requests.post(
            f"{BASE_URL}/api/karau/beamforming/{self.MEETING_ID}/config",
            headers=auth_headers,
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "config" in data
        assert "beam_pattern" in data
        config = data["config"]
        assert config.get("mode") == "directional"
        print(f"PASS - Beamforming config updated to mode={config['mode']}")
    
    def test_post_audio_profile(self, auth_headers):
        """POST /api/karau/beamforming/{meeting_id}/profile - Update audio profile"""
        payload = {
            "meeting_id": self.MEETING_ID,
            "user_id": "test-user-profile",
            "noise_floor_db": -58.0,
            "signal_level_db": -22.0,
            "snr_db": 36.0,
            "dominant_noise_freq": 120.0,
            "noise_type": "hvac"
        }
        response = requests.post(
            f"{BASE_URL}/api/karau/beamforming/{self.MEETING_ID}/profile",
            headers=auth_headers,
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "user_id" in data
        assert "snr_db" in data
        assert "quality" in data
        assert "adaptive_recommendations" in data
        print(f"PASS - Audio profile updated for {data['user_id']}, quality={data['quality']}")
    
    def test_get_audio_analysis(self, auth_headers):
        """GET /api/karau/beamforming/{meeting_id}/analysis - Get audio analysis"""
        response = requests.get(
            f"{BASE_URL}/api/karau/beamforming/{self.MEETING_ID}/analysis",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "meeting_id" in data
        assert "spectrum" in data
        assert "profiles" in data
        assert "noise_sources" in data
        assert "active_processing" in data
        # Verify spectrum data
        spectrum = data["spectrum"]
        assert len(spectrum) > 0, "Expected frequency spectrum data"
        first_band = spectrum[0]
        assert "frequency" in first_band
        assert "level_db" in first_band
        print(f"PASS - Audio analysis: {len(spectrum)} frequency bands, {len(data['noise_sources'])} noise sources")


class TestMeetingReplay(TestAuth):
    """Meeting Replay with Director Cuts API Tests"""
    
    MEETING_ID = "demo-meeting-123"
    
    def test_get_replay_demo(self, auth_headers):
        """GET /api/karau/replay/{meeting_id} - Get demo meeting replay"""
        response = requests.get(
            f"{BASE_URL}/api/karau/replay/{self.MEETING_ID}",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200 (demo generated), got {response.status_code}: {response.text}"
        data = response.json()
        assert "meeting_id" in data
        assert "title" in data
        assert "duration_seconds" in data
        assert "director_cuts" in data
        assert "key_moments" in data
        assert "view_distribution" in data
        # Verify director cuts
        cuts = data["director_cuts"]
        assert len(cuts) > 0, "Expected director cuts"
        first_cut = cuts[0]
        assert "timestamp_seconds" in first_cut
        assert "view_mode" in first_cut
        assert "transition" in first_cut
        # Verify key moments
        moments = data["key_moments"]
        assert len(moments) > 0, "Expected key moments"
        first_moment = moments[0]
        assert "ts" in first_moment
        assert "type" in first_moment
        assert "label" in first_moment
        print(f"PASS - Demo replay: {data['title']}, {len(cuts)} cuts, {len(moments)} moments, {data['duration_seconds']}s duration")
    
    def test_replay_requires_auth(self):
        """GET /api/karau/replay/{meeting_id} requires auth"""
        response = requests.get(f"{BASE_URL}/api/karau/replay/{self.MEETING_ID}")
        assert response.status_code == 401
        print("PASS - Replay requires auth")
    
    def test_get_replay_list(self, auth_headers):
        """GET /api/karau/replay/list - List all replays"""
        response = requests.get(
            f"{BASE_URL}/api/karau/replay/list",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "replays" in data
        print(f"PASS - Replay list: {len(data['replays'])} replays")
    
    def test_post_save_replay(self, auth_headers):
        """POST /api/karau/replay/save - Save a replay"""
        payload = {
            "meeting_id": "test-save-replay-153",
            "title": "Test Replay - Iteration 153",
            "duration_seconds": 1200,
            "director_cuts": [
                {"timestamp_seconds": 0, "view_mode": "panoramic", "focus_users": [], "active_speaker_count": 0, "transition": "smooth"},
                {"timestamp_seconds": 30, "view_mode": "speaker_closeup", "focus_users": ["Alex Chen"], "active_speaker_count": 1, "transition": "smooth"},
                {"timestamp_seconds": 120, "view_mode": "conversation", "focus_users": ["Alex Chen", "Sarah Miller"], "active_speaker_count": 2, "transition": "dissolve"}
            ],
            "transcript_segments": [
                {"ts": 0, "speaker": "Host", "text": "Welcome to the meeting"},
                {"ts": 30, "speaker": "Alex Chen", "text": "Let me present the Q4 results"}
            ],
            "key_moments": [
                {"ts": 0, "type": "intro", "label": "Meeting started"},
                {"ts": 30, "type": "presentation", "label": "Q4 results presentation"}
            ]
        }
        response = requests.post(
            f"{BASE_URL}/api/karau/replay/save",
            headers=auth_headers,
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "meeting_id" in data
        assert "cut_count" in data
        assert "replay_url" in data
        print(f"PASS - Replay saved: {data['cut_count']} cuts, URL: {data['replay_url']}")
    
    def test_get_replay_timeline(self, auth_headers):
        """GET /api/karau/replay/{meeting_id}/timeline - Get timeline"""
        response = requests.get(
            f"{BASE_URL}/api/karau/replay/{self.MEETING_ID}/timeline",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "meeting_id" in data
        assert "director_cuts" in data
        assert "key_moments" in data
        assert "duration_seconds" in data
        print(f"PASS - Timeline: {len(data['director_cuts'])} cuts, {len(data['key_moments'])} moments")
    
    def test_post_generate_highlights(self, auth_headers):
        """POST /api/karau/replay/generate-highlights - AI highlight generation"""
        payload = {
            "meeting_id": self.MEETING_ID,
            "style": "executive_summary"
        }
        response = requests.post(
            f"{BASE_URL}/api/karau/replay/generate-highlights",
            headers=auth_headers,
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert "meeting_id" in data
        assert "style" in data
        assert "highlights" in data
        assert "key_moments" in data
        # Highlights should be non-empty
        assert len(data["highlights"]) > 0, "Expected highlights text"
        print(f"PASS - AI highlights generated ({data['style']}): {len(data['highlights'])} chars")
    
    def test_delete_replay(self, auth_headers):
        """DELETE /api/karau/replay/{meeting_id} - Delete replay"""
        # First save a test replay
        save_response = requests.post(
            f"{BASE_URL}/api/karau/replay/save",
            headers=auth_headers,
            json={
                "meeting_id": "test-delete-replay-153",
                "title": "To Be Deleted",
                "duration_seconds": 600,
                "director_cuts": [],
                "transcript_segments": [],
                "key_moments": []
            }
        )
        assert save_response.status_code == 200
        
        # Now delete it
        response = requests.delete(
            f"{BASE_URL}/api/karau/replay/test-delete-replay-153",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert data.get("deleted") == "test-delete-replay-153"
        print("PASS - Replay deleted successfully")


class TestAPIRequiresAuth:
    """Verify all new endpoints require authentication"""
    
    def test_slam_tracking_requires_auth(self):
        """Spatial tracking requires auth"""
        r = requests.get(f"{BASE_URL}/api/karau/spatial/test/tracking")
        assert r.status_code == 401
    
    def test_slam_room_map_requires_auth(self):
        """Room map POST requires auth"""
        r = requests.post(f"{BASE_URL}/api/karau/spatial/test/room-map", json={})
        assert r.status_code == 401
    
    def test_panoramic_headshots_requires_auth(self):
        """Panoramic headshots requires auth"""
        r = requests.get(f"{BASE_URL}/api/karau/spatial/test/panoramic/headshots")
        assert r.status_code == 401
    
    def test_webxr_session_post_requires_auth(self):
        """WebXR session POST requires auth"""
        r = requests.post(f"{BASE_URL}/api/karau/webxr/test/session", json={})
        assert r.status_code == 401
    
    def test_webxr_session_get_requires_auth(self):
        """WebXR session GET requires auth"""
        r = requests.get(f"{BASE_URL}/api/karau/webxr/test/session")
        assert r.status_code == 401
    
    def test_webxr_personas_requires_auth(self):
        """WebXR personas requires auth"""
        r = requests.get(f"{BASE_URL}/api/karau/webxr/test/personas")
        assert r.status_code == 401
    
    def test_iot_state_requires_auth(self):
        """IoT state requires auth"""
        r = requests.get(f"{BASE_URL}/api/karau/iot/test/state")
        assert r.status_code == 401
    
    def test_iot_device_requires_auth(self):
        """IoT device control requires auth"""
        r = requests.post(f"{BASE_URL}/api/karau/iot/test/device", json={})
        assert r.status_code == 401
    
    def test_iot_preset_requires_auth(self):
        """IoT preset requires auth"""
        r = requests.post(f"{BASE_URL}/api/karau/iot/test/preset?preset_name=presentation")
        assert r.status_code == 401
    
    def test_iot_voice_requires_auth(self):
        """IoT voice control requires auth"""
        r = requests.post(f"{BASE_URL}/api/karau/iot/test/voice-control", json={})
        assert r.status_code == 401
    
    def test_beamforming_status_requires_auth(self):
        """Beamforming status requires auth"""
        r = requests.get(f"{BASE_URL}/api/karau/beamforming/test/status")
        assert r.status_code == 401
    
    def test_beamforming_config_requires_auth(self):
        """Beamforming config requires auth"""
        r = requests.post(f"{BASE_URL}/api/karau/beamforming/test/config", json={})
        assert r.status_code == 401
    
    def test_beamforming_profile_requires_auth(self):
        """Beamforming profile requires auth"""
        r = requests.post(f"{BASE_URL}/api/karau/beamforming/test/profile", json={})
        assert r.status_code == 401
    
    def test_beamforming_analysis_requires_auth(self):
        """Beamforming analysis requires auth"""
        r = requests.get(f"{BASE_URL}/api/karau/beamforming/test/analysis")
        assert r.status_code == 401
    
    def test_replay_requires_auth(self):
        """Replay GET requires auth"""
        r = requests.get(f"{BASE_URL}/api/karau/replay/test")
        assert r.status_code == 401
    
    def test_replay_list_requires_auth(self):
        """Replay list requires auth"""
        r = requests.get(f"{BASE_URL}/api/karau/replay/list")
        assert r.status_code == 401
    
    def test_replay_save_requires_auth(self):
        """Replay save requires auth"""
        r = requests.post(f"{BASE_URL}/api/karau/replay/save", json={})
        assert r.status_code == 401
    
    def test_replay_timeline_requires_auth(self):
        """Replay timeline requires auth"""
        r = requests.get(f"{BASE_URL}/api/karau/replay/test/timeline")
        assert r.status_code == 401
    
    def test_replay_highlights_requires_auth(self):
        """Replay highlights requires auth"""
        r = requests.post(f"{BASE_URL}/api/karau/replay/generate-highlights", json={})
        assert r.status_code == 401
    
    def test_replay_delete_requires_auth(self):
        """Replay delete requires auth"""
        r = requests.delete(f"{BASE_URL}/api/karau/replay/test")
        assert r.status_code == 401
    
    def test_webxr_room_layout_public(self):
        """WebXR room-layout is PUBLIC (no auth required)"""
        r = requests.get(f"{BASE_URL}/api/karau/webxr/test/room-layout")
        assert r.status_code == 200, "room-layout should be public"
        print("PASS - WebXR room-layout endpoint is public (no auth)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
