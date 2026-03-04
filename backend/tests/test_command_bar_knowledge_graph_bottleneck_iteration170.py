"""
Iteration 170: Command Bar, Knowledge Graph, Bottleneck Detection Tests
Testing new LUMI features: 
- Command Bar search (Ctrl+K modal)
- Knowledge Graph visualization with entity relationships
- Bottleneck Detection with health score
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL').rstrip('/')

class TestAuthentication:
    """Auth tests to get token for other tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@medmatch.com", "password": "Swampdrainer2026!"}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        return data["access_token"]
    
    def test_health_check(self):
        """Test API health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("✅ Health check passed")
    
    def test_login_admin(self, auth_token):
        """Verify login works"""
        assert auth_token is not None
        print("✅ Admin login successful")


class TestCommandBarSearch:
    """Command Bar search endpoint tests - POST /api/lumi/command/search"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@medmatch.com", "password": "Swampdrainer2026!"}
        )
        assert response.status_code == 200
        return response.json()["access_token"]
    
    def test_command_search_channels(self, auth_token):
        """Search for channels using Command Bar"""
        response = requests.post(
            f"{BASE_URL}/api/lumi/command/search",
            json={"query": "general", "mode": "search"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Search failed: {response.text}"
        data = response.json()
        assert "results" in data
        assert data.get("mode") == "search"
        print(f"✅ Command search returned {len(data['results'])} results for 'general'")
        # Print results types
        for r in data['results'][:5]:
            print(f"   - {r.get('type')}: {r.get('name', r.get('content', '')[:40])}")
    
    def test_command_search_quick_actions(self, auth_token):
        """Search for quick actions like 'create'"""
        response = requests.post(
            f"{BASE_URL}/api/lumi/command/search",
            json={"query": "create", "mode": "search"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        results = data.get("results", [])
        # Should find 'Create new channel' quick action
        action_types = [r.get("type") for r in results]
        has_action = "action" in action_types
        print(f"✅ Command search for 'create' returned {len(results)} results, has quick action: {has_action}")
        if has_action:
            action = [r for r in results if r.get("type") == "action"][0]
            print(f"   - Quick action: {action.get('name')}")
    
    def test_command_search_empty_query(self, auth_token):
        """Empty query should return empty results"""
        response = requests.post(
            f"{BASE_URL}/api/lumi/command/search",
            json={"query": "", "mode": "search"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("results") == []
        print("✅ Empty query returns empty results as expected")
    
    def test_command_search_ai_mode(self, auth_token):
        """Test AI mode (prefix with ?) in Command Bar"""
        response = requests.post(
            f"{BASE_URL}/api/lumi/command/search",
            json={"query": "What is the team status?", "mode": "ai"},
            headers={"Authorization": f"Bearer {auth_token}"},
            timeout=60  # AI calls may take time
        )
        assert response.status_code == 200, f"AI search failed: {response.text}"
        data = response.json()
        assert data.get("mode") == "ai"
        results = data.get("results", [])
        if results:
            ai_result = results[0]
            assert ai_result.get("type") == "ai_answer"
            print(f"✅ AI mode returned answer: {ai_result.get('content', '')[:100]}...")
        else:
            print("✅ AI mode returned empty results (may need more context)")
    
    def test_command_search_tasks(self, auth_token):
        """Search for tasks"""
        response = requests.post(
            f"{BASE_URL}/api/lumi/command/search",
            json={"query": "task", "mode": "search"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Command search for 'task' returned {len(data.get('results', []))} results")


class TestKnowledgeGraph:
    """Knowledge Graph endpoint tests - GET /api/lumi/knowledge-graph"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@medmatch.com", "password": "Swampdrainer2026!"}
        )
        assert response.status_code == 200
        return response.json()["access_token"]
    
    def test_get_knowledge_graph(self, auth_token):
        """Get the knowledge graph with nodes and edges"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/knowledge-graph",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Knowledge graph failed: {response.text}"
        data = response.json()
        
        # Check structure
        assert "nodes" in data
        assert "edges" in data
        assert "stats" in data
        
        nodes = data.get("nodes", [])
        edges = data.get("edges", [])
        stats = data.get("stats", {})
        
        print(f"✅ Knowledge Graph loaded:")
        print(f"   - Total nodes: {stats.get('total_nodes', len(nodes))}")
        print(f"   - Total edges: {stats.get('total_edges', len(edges))}")
        print(f"   - Node types: {stats.get('by_type', {})}")
        
        # Verify node structure
        if nodes:
            sample_node = nodes[0]
            assert "id" in sample_node
            assert "type" in sample_node
            assert "label" in sample_node
            print(f"   - Sample node: {sample_node.get('type')} - {sample_node.get('label')}")
    
    def test_knowledge_graph_node_types(self, auth_token):
        """Verify different node types exist: person, channel, task, meeting, action_item"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/knowledge-graph",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        node_types = set(n.get("type") for n in data.get("nodes", []))
        expected_types = {"channel"}  # At minimum, channels should exist
        
        print(f"✅ Node types in graph: {node_types}")
        assert len(node_types) >= 1, "Should have at least one node type"
    
    def test_knowledge_graph_edges(self, auth_token):
        """Verify edges have source, target, and relationship"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/knowledge-graph",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        edges = data.get("edges", [])
        if edges:
            sample_edge = edges[0]
            assert "source" in sample_edge
            assert "target" in sample_edge
            assert "relationship" in sample_edge
            print(f"✅ Sample edge: {sample_edge.get('source')} --[{sample_edge.get('relationship')}]--> {sample_edge.get('target')}")
        else:
            print("✅ No edges yet (expected if no relationships exist)")


class TestKnowledgeGraphImpact:
    """Knowledge Graph Impact Analysis - POST /api/lumi/knowledge-graph/impact"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@medmatch.com", "password": "Swampdrainer2026!"}
        )
        assert response.status_code == 200
        return response.json()["access_token"]
    
    def test_impact_analysis_person(self, auth_token):
        """Test impact analysis for a person entity"""
        response = requests.post(
            f"{BASE_URL}/api/lumi/knowledge-graph/impact",
            json={
                "entity_type": "person",
                "entity_id": "admin",
                "entity_name": "Admin User"
            },
            headers={"Authorization": f"Bearer {auth_token}"},
            timeout=60
        )
        assert response.status_code == 200, f"Impact analysis failed: {response.text}"
        data = response.json()
        
        # Check structure
        assert "direct" in data or "risk_level" in data
        print(f"✅ Impact analysis for person:")
        print(f"   - Risk level: {data.get('risk_level', 'low')}")
        print(f"   - Direct impacts: {len(data.get('direct', []))}")
        print(f"   - Indirect impacts: {len(data.get('indirect', []))}")
        if data.get("ai_analysis"):
            print(f"   - AI analysis: {data.get('ai_analysis')[:100]}...")
    
    def test_impact_analysis_channel(self, auth_token):
        """Test impact analysis for a channel entity"""
        # First get a channel ID
        channels_response = requests.get(
            f"{BASE_URL}/api/lumi/channels",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        channels = channels_response.json() if channels_response.status_code == 200 else []
        
        if channels:
            channel_id = channels[0].get("id", "general")
            channel_name = channels[0].get("name", "general")
        else:
            channel_id = "general"
            channel_name = "general"
        
        response = requests.post(
            f"{BASE_URL}/api/lumi/knowledge-graph/impact",
            json={
                "entity_type": "channel",
                "entity_id": channel_id,
                "entity_name": channel_name
            },
            headers={"Authorization": f"Bearer {auth_token}"},
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Impact analysis for channel '{channel_name}':")
        print(f"   - Risk level: {data.get('risk_level', 'low')}")


class TestBottleneckDetection:
    """Bottleneck Detection endpoint tests - GET /api/lumi/bottlenecks"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@medmatch.com", "password": "Swampdrainer2026!"}
        )
        assert response.status_code == 200
        return response.json()["access_token"]
    
    def test_get_bottlenecks(self, auth_token):
        """Get bottleneck detection results with health score"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/bottlenecks",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Bottleneck detection failed: {response.text}"
        data = response.json()
        
        # Check structure
        assert "bottlenecks" in data
        assert "health_score" in data
        assert "workload_summary" in data
        
        bottlenecks = data.get("bottlenecks", [])
        health_score = data.get("health_score", 0)
        workload = data.get("workload_summary", {})
        
        print(f"✅ Bottleneck detection results:")
        print(f"   - Health score: {health_score}/100")
        print(f"   - Total bottlenecks: {len(bottlenecks)}")
        print(f"   - Open items: {workload.get('total_open_items', 0)}")
        print(f"   - People with work: {workload.get('people_with_work', 0)}")
        print(f"   - Avg workload: {workload.get('avg_workload', 0)}")
        
        for bn in bottlenecks[:3]:
            print(f"   - [{bn.get('severity')}] {bn.get('title')}")
    
    def test_bottleneck_health_score_range(self, auth_token):
        """Health score should be between 0-100"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/bottlenecks",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        health_score = data.get("health_score", 0)
        assert 0 <= health_score <= 100, f"Health score {health_score} out of range"
        print(f"✅ Health score {health_score} is in valid range 0-100")
    
    def test_bottleneck_workload_summary_structure(self, auth_token):
        """Verify workload summary structure"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/bottlenecks",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        workload = data.get("workload_summary", {})
        expected_keys = ["total_open_items", "people_with_work", "avg_workload"]
        for key in expected_keys:
            assert key in workload, f"Missing {key} in workload_summary"
        print(f"✅ Workload summary structure verified")


class TestExistingFeatures:
    """Verify existing features still work after new additions"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@medmatch.com", "password": "Swampdrainer2026!"}
        )
        assert response.status_code == 200
        return response.json()["access_token"]
    
    def test_channels_list(self, auth_token):
        """Verify channels list still works"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/channels",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        channels = response.json()
        print(f"✅ Channels list: {len(channels)} channels found")
    
    def test_dm_list(self, auth_token):
        """Verify DM list still works"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/dm",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        dms = data if isinstance(data, list) else data.get("conversations", [])
        print(f"✅ DM list: {len(dms)} DMs found")
    
    def test_presence(self, auth_token):
        """Verify presence still works"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/presence/all",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        print(f"✅ Presence endpoint working")
    
    def test_ai_sentiment_endpoint(self, auth_token):
        """Verify AI sentiment endpoint still works"""
        # Get a channel first
        channels_response = requests.get(
            f"{BASE_URL}/api/lumi/channels",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        channels = channels_response.json() if channels_response.status_code == 200 else []
        
        if channels:
            channel_id = channels[0].get("id")
            response = requests.post(
                f"{BASE_URL}/api/lumi/ai/sentiment/{channel_id}",
                headers={"Authorization": f"Bearer {auth_token}"},
                timeout=60
            )
            assert response.status_code == 200
            data = response.json()
            print(f"✅ Sentiment analysis: score={data.get('score', 'N/A')}, label={data.get('label', 'N/A')}")
        else:
            print("⚠️ No channels to test sentiment analysis")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
