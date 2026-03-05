"""
LUMI Visualizations & ComplianceWidget Tests - Iteration 177
Tests for:
- Analytics/Visualizations API endpoint (activity, timeline, graph tabs)
- ComplianceWidget (sidebar compliance score)
- Tagline verification
"""

import pytest
import requests
import os

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
assert BASE_URL, "REACT_APP_BACKEND_URL must be set"


class TestAuth:
    """Get auth token for subsequent tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Login and get token"""
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        assert resp.status_code == 200, f"Login failed: {resp.text}"
        data = resp.json()
        assert "access_token" in data, "No access_token in response"
        return data["access_token"]
    
    def test_login(self, auth_token):
        """Verify login works and token is valid"""
        assert auth_token is not None
        assert len(auth_token) > 0
        print(f"✅ Login successful, token obtained")


class TestVisualizationsActivityTab:
    """Test Visualizations API - Activity tab"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        return resp.json()["access_token"]
    
    def test_activity_tab_endpoint(self, auth_token):
        """GET /api/lumi/analytics/visualizations?tab=activity returns expected structure"""
        resp = requests.get(
            f"{BASE_URL}/api/lumi/analytics/visualizations?tab=activity",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        
        # Verify team_stats (4 KPI cards)
        assert "team_stats" in data, "Missing team_stats"
        assert len(data["team_stats"]) == 4, f"Expected 4 team_stats, got {len(data['team_stats'])}"
        
        # Check KPI structure
        for stat in data["team_stats"]:
            assert "label" in stat, "KPI missing label"
            assert "value" in stat, "KPI missing value"
        
        labels = [s["label"] for s in data["team_stats"]]
        assert "Messages" in labels, "Missing Messages KPI"
        assert "Active Users" in labels, "Missing Active Users KPI"
        assert "Channels" in labels, "Missing Channels KPI"
        assert "Avg Response" in labels, "Missing Avg Response KPI"
        print(f"✅ Activity tab team_stats: {labels}")
    
    def test_activity_tab_daily_messages(self, auth_token):
        """Verify daily_messages structure for area chart"""
        resp = requests.get(
            f"{BASE_URL}/api/lumi/analytics/visualizations?tab=activity",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = resp.json()
        
        assert "daily_messages" in data, "Missing daily_messages"
        assert len(data["daily_messages"]) == 7, f"Expected 7 days, got {len(data['daily_messages'])}"
        
        for entry in data["daily_messages"]:
            assert "day" in entry, "daily_messages entry missing 'day'"
            assert "count" in entry, "daily_messages entry missing 'count'"
        print(f"✅ Activity tab daily_messages: {[d['day'] for d in data['daily_messages']]}")
    
    def test_activity_tab_channel_activity(self, auth_token):
        """Verify channel_activity structure for horizontal bar chart"""
        resp = requests.get(
            f"{BASE_URL}/api/lumi/analytics/visualizations?tab=activity",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = resp.json()
        
        assert "channel_activity" in data, "Missing channel_activity"
        for entry in data["channel_activity"]:
            assert "name" in entry, "channel_activity entry missing 'name'"
            assert "messages" in entry, "channel_activity entry missing 'messages'"
        print(f"✅ Activity tab channel_activity: {[c['name'] for c in data['channel_activity']]}")
    
    def test_activity_tab_hourly_heatmap(self, auth_token):
        """Verify hourly_heatmap structure for heatmap"""
        resp = requests.get(
            f"{BASE_URL}/api/lumi/analytics/visualizations?tab=activity",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = resp.json()
        
        assert "hourly_heatmap" in data, "Missing hourly_heatmap"
        assert len(data["hourly_heatmap"]) == 24, f"Expected 24 hours, got {len(data['hourly_heatmap'])}"
        
        for entry in data["hourly_heatmap"]:
            assert "hour" in entry, "hourly_heatmap entry missing 'hour'"
            assert "count" in entry, "hourly_heatmap entry missing 'count'"
        print(f"✅ Activity tab hourly_heatmap: 24 hours covered")


class TestVisualizationsTimelineTab:
    """Test Visualizations API - Timeline tab"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        return resp.json()["access_token"]
    
    def test_timeline_tab_endpoint(self, auth_token):
        """GET /api/lumi/analytics/visualizations?tab=timeline returns expected structure"""
        resp = requests.get(
            f"{BASE_URL}/api/lumi/analytics/visualizations?tab=timeline",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        
        assert "milestones" in data, "Missing milestones"
        assert "burndown" in data, "Missing burndown"
        assert "team_radar" in data, "Missing team_radar"
        print(f"✅ Timeline tab has all required fields")
    
    def test_timeline_milestones(self, auth_token):
        """Verify milestones have done/active/upcoming states"""
        resp = requests.get(
            f"{BASE_URL}/api/lumi/analytics/visualizations?tab=timeline",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = resp.json()
        
        milestones = data["milestones"]
        assert len(milestones) == 6, f"Expected 6 milestones, got {len(milestones)}"
        
        statuses = [m["status"] for m in milestones]
        assert "done" in statuses, "No 'done' milestone found"
        assert "active" in statuses, "No 'active' milestone found"
        assert "upcoming" in statuses, "No 'upcoming' milestone found"
        
        for m in milestones:
            assert "title" in m, "Milestone missing title"
            assert "description" in m, "Milestone missing description"
            assert "date" in m, "Milestone missing date"
            assert "status" in m, "Milestone missing status"
        print(f"✅ Timeline milestones: {[m['title'] for m in milestones]}")
        print(f"✅ Milestone statuses: {statuses}")
    
    def test_timeline_burndown(self, auth_token):
        """Verify burndown chart data"""
        resp = requests.get(
            f"{BASE_URL}/api/lumi/analytics/visualizations?tab=timeline",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = resp.json()
        
        burndown = data["burndown"]
        assert len(burndown) >= 5, f"Expected at least 5 burndown points, got {len(burndown)}"
        
        for entry in burndown:
            assert "day" in entry, "Burndown entry missing 'day'"
            assert "ideal" in entry, "Burndown entry missing 'ideal'"
            assert "actual" in entry, "Burndown entry missing 'actual'"
        print(f"✅ Timeline burndown: {len(burndown)} data points")
    
    def test_timeline_team_radar(self, auth_token):
        """Verify team radar chart data"""
        resp = requests.get(
            f"{BASE_URL}/api/lumi/analytics/visualizations?tab=timeline",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = resp.json()
        
        radar = data["team_radar"]
        assert len(radar) >= 4, f"Expected at least 4 radar skills, got {len(radar)}"
        
        for entry in radar:
            assert "skill" in entry, "Radar entry missing 'skill'"
            assert "score" in entry, "Radar entry missing 'score'"
        
        skills = [r["skill"] for r in radar]
        print(f"✅ Timeline team_radar skills: {skills}")


class TestVisualizationsGraphTab:
    """Test Visualizations API - Knowledge Graph tab"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        return resp.json()["access_token"]
    
    def test_graph_tab_endpoint(self, auth_token):
        """GET /api/lumi/analytics/visualizations?tab=graph returns expected structure"""
        resp = requests.get(
            f"{BASE_URL}/api/lumi/analytics/visualizations?tab=graph",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        
        assert "nodes" in data, "Missing nodes"
        assert "connections" in data, "Missing connections"
        assert "categories" in data, "Missing categories"
        print(f"✅ Graph tab has all required fields")
    
    def test_graph_nodes(self, auth_token):
        """Verify nodes have correct structure (12 nodes expected)"""
        resp = requests.get(
            f"{BASE_URL}/api/lumi/analytics/visualizations?tab=graph",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = resp.json()
        
        nodes = data["nodes"]
        assert len(nodes) == 12, f"Expected 12 nodes, got {len(nodes)}"
        
        for node in nodes:
            assert "label" in node, "Node missing 'label'"
            assert "x" in node, "Node missing 'x' position"
            assert "y" in node, "Node missing 'y' position"
            assert "size" in node, "Node missing 'size'"
            assert "category" in node, "Node missing 'category'"
            assert "links" in node, "Node missing 'links'"
        
        labels = [n["label"] for n in nodes]
        print(f"✅ Graph nodes: {labels}")
    
    def test_graph_connections(self, auth_token):
        """Verify connections (connection strength bar chart data)"""
        resp = requests.get(
            f"{BASE_URL}/api/lumi/analytics/visualizations?tab=graph",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = resp.json()
        
        connections = data["connections"]
        for conn in connections:
            assert "type" in conn, "Connection missing 'type'"
            assert "strength" in conn, "Connection missing 'strength'"
        
        types = [c["type"] for c in connections]
        print(f"✅ Graph connections: {types}")
    
    def test_graph_categories(self, auth_token):
        """Verify categories (entity distribution pie chart data)"""
        resp = requests.get(
            f"{BASE_URL}/api/lumi/analytics/visualizations?tab=graph",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = resp.json()
        
        categories = data["categories"]
        for cat in categories:
            assert "name" in cat, "Category missing 'name'"
            assert "count" in cat, "Category missing 'count'"
        
        names = [c["name"] for c in categories]
        expected = ["People", "Projects", "Tasks", "Channels"]
        for exp in expected:
            assert exp in names, f"Missing category: {exp}"
        print(f"✅ Graph categories: {names}")


class TestComplianceWidget:
    """Test Compliance Widget API (used in sidebar)"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        return resp.json()["access_token"]
    
    def test_compliance_status_endpoint(self, auth_token):
        """GET /api/lumi/compliance/status returns overall_score for widget"""
        resp = requests.get(
            f"{BASE_URL}/api/lumi/compliance/status",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        
        assert "overall_score" in data, "Missing overall_score"
        score = data["overall_score"]
        assert isinstance(score, (int, float)), f"Score should be numeric, got {type(score)}"
        assert 0 <= score <= 100, f"Score should be 0-100, got {score}"
        print(f"✅ Compliance score: {score}%")


class TestExistingFeaturesStillWork:
    """Quick verification that existing features still open"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        return resp.json()["access_token"]
    
    def test_compliance_frameworks(self, auth_token):
        """Compliance frameworks endpoint still works"""
        resp = requests.get(
            f"{BASE_URL}/api/lumi/compliance/frameworks",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert resp.status_code == 200, f"Compliance frameworks failed: {resp.status_code}"
        print(f"✅ Compliance frameworks endpoint works")
    
    def test_audit_log(self, auth_token):
        """Audit log endpoint still works"""
        resp = requests.get(
            f"{BASE_URL}/api/lumi/admin/audit-log",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert resp.status_code == 200, f"Audit log failed: {resp.status_code}"
        print(f"✅ Audit log endpoint works")
    
    def test_moderation_settings(self, auth_token):
        """Moderation settings endpoint still works"""
        resp = requests.get(
            f"{BASE_URL}/api/lumi/moderation/settings",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert resp.status_code == 200, f"Moderation settings failed: {resp.status_code}"
        print(f"✅ Moderation settings endpoint works")
    
    def test_channels_endpoint(self, auth_token):
        """Channels endpoint still works"""
        resp = requests.get(
            f"{BASE_URL}/api/lumi/channels",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert resp.status_code == 200, f"Channels failed: {resp.status_code}"
        print(f"✅ Channels endpoint works")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
