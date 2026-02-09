"""
CAPA System API Tests
Tests for Corrective Action Preventive Action management system
Part of Karau Automator
"""

import pytest
import requests
import os
import time
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestCAPADashboard:
    """Test CAPA Dashboard endpoint"""
    
    def test_dashboard_returns_summary(self):
        """Test /api/capa/dashboard returns correct summary structure"""
        response = requests.get(f"{BASE_URL}/api/capa/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        # Verify required fields
        assert "total_capas" in data
        assert "open_capas" in data
        assert "status_distribution" in data
        assert "severity_distribution" in data
        assert "average_days_to_close" in data
        assert "recent_capas" in data
        
        # Verify status distribution has all statuses
        status_dist = data["status_distribution"]
        expected_statuses = ["draft", "investigation", "containment", "resolution", 
                           "voe_pending", "voe_in_progress", "closed", "cancelled"]
        for status in expected_statuses:
            assert status in status_dist
        
        # Verify severity distribution
        severity_dist = data["severity_distribution"]
        expected_severities = ["critical", "high", "medium", "low"]
        for severity in expected_severities:
            assert severity in severity_dist
        
        print(f"Dashboard: {data['total_capas']} total CAPAs, {data['open_capas']} open")


class TestCAPAList:
    """Test CAPA List endpoint"""
    
    def test_list_returns_all_capas(self):
        """Test /api/capa/list returns all CAPAs"""
        response = requests.get(f"{BASE_URL}/api/capa/list")
        assert response.status_code == 200
        
        data = response.json()
        assert "capas" in data
        assert "total" in data
        assert isinstance(data["capas"], list)
        assert data["total"] == len(data["capas"])
        
        print(f"List: Found {data['total']} CAPAs")
    
    def test_list_filter_by_status(self):
        """Test filtering CAPAs by status"""
        response = requests.get(f"{BASE_URL}/api/capa/list?status=investigation")
        assert response.status_code == 200
        
        data = response.json()
        # All returned CAPAs should have investigation status
        for capa in data["capas"]:
            assert capa["status"] == "investigation"
        
        print(f"Filter by status: Found {data['total']} CAPAs in investigation")


class TestCAPACreate:
    """Test CAPA Create endpoint"""
    
    def test_create_capa_success(self):
        """Test creating a new CAPA"""
        payload = {
            "title": "TEST_CAPA_Automated Test Issue",
            "problem_statement": "This is an automated test CAPA created by pytest",
            "capa_type": "corrective",
            "severity": "low",
            "source": "Automated Testing",
            "impacted_processes": ["Testing", "QA"],
            "tags": ["test", "automated"]
        }
        
        response = requests.post(f"{BASE_URL}/api/capa/create", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "capa" in data
        
        capa = data["capa"]
        assert capa["title"] == payload["title"]
        assert capa["problem_statement"] == payload["problem_statement"]
        assert capa["capa_type"] == payload["capa_type"]
        assert capa["severity"] == payload["severity"]
        assert capa["status"] == "draft"  # New CAPAs start in draft
        assert capa["id"].startswith("CAPA-")
        
        print(f"Created CAPA: {capa['id']}")
        return capa["id"]
    
    def test_create_capa_minimal_fields(self):
        """Test creating CAPA with minimal required fields"""
        payload = {
            "title": "TEST_CAPA_Minimal Fields Test",
            "problem_statement": "Minimal test CAPA"
        }
        
        response = requests.post(f"{BASE_URL}/api/capa/create", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        
        capa = data["capa"]
        # Verify defaults are applied
        assert capa["capa_type"] == "both"  # default
        assert capa["severity"] == "medium"  # default
        
        print(f"Created minimal CAPA: {capa['id']}")


class TestCAPAGetById:
    """Test CAPA Get by ID endpoint"""
    
    def test_get_existing_capa(self):
        """Test getting an existing CAPA by ID"""
        # First get list to find an existing CAPA
        list_response = requests.get(f"{BASE_URL}/api/capa/list")
        capas = list_response.json()["capas"]
        
        if len(capas) == 0:
            pytest.skip("No CAPAs exist to test")
        
        capa_id = capas[0]["id"]
        response = requests.get(f"{BASE_URL}/api/capa/{capa_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == capa_id
        assert "title" in data
        assert "problem_statement" in data
        assert "status" in data
        assert "investigation" in data
        assert "containment" in data
        assert "resolution" in data
        assert "voe" in data
        assert "history" in data
        
        print(f"Retrieved CAPA: {capa_id}")
    
    def test_get_nonexistent_capa(self):
        """Test getting a non-existent CAPA returns 404"""
        response = requests.get(f"{BASE_URL}/api/capa/CAPA-NONEXISTENT-12345678")
        assert response.status_code == 404


class TestCAPAStatusUpdate:
    """Test CAPA Status Update endpoint"""
    
    def test_update_status_to_investigation(self):
        """Test updating CAPA status to investigation"""
        # Create a new CAPA first
        create_payload = {
            "title": "TEST_CAPA_Status Update Test",
            "problem_statement": "Testing status transitions"
        }
        create_response = requests.post(f"{BASE_URL}/api/capa/create", json=create_payload)
        capa_id = create_response.json()["capa"]["id"]
        
        # Update status to investigation
        update_payload = {
            "status": "investigation",
            "user": "test_user",
            "notes": "Starting investigation"
        }
        response = requests.put(f"{BASE_URL}/api/capa/{capa_id}/status", json=update_payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["capa"]["status"] == "investigation"
        assert data["capa"]["investigation"]["started_at"] is not None
        
        print(f"Updated CAPA {capa_id} to investigation status")
    
    def test_update_status_nonexistent_capa(self):
        """Test updating status of non-existent CAPA returns 404"""
        update_payload = {
            "status": "investigation",
            "user": "test_user"
        }
        response = requests.put(f"{BASE_URL}/api/capa/CAPA-NONEXISTENT-12345678/status", json=update_payload)
        assert response.status_code == 404


class TestCAPAInvestigation:
    """Test CAPA Investigation endpoints"""
    
    def test_add_probable_cause(self):
        """Test adding a probable cause to a CAPA"""
        # Get existing CAPA in investigation status
        list_response = requests.get(f"{BASE_URL}/api/capa/list?status=investigation")
        capas = list_response.json()["capas"]
        
        if len(capas) == 0:
            # Create one and move to investigation
            create_payload = {
                "title": "TEST_CAPA_Investigation Test",
                "problem_statement": "Testing investigation features"
            }
            create_response = requests.post(f"{BASE_URL}/api/capa/create", json=create_payload)
            capa_id = create_response.json()["capa"]["id"]
            
            # Move to investigation
            requests.put(f"{BASE_URL}/api/capa/{capa_id}/status", json={"status": "investigation"})
        else:
            capa_id = capas[0]["id"]
        
        # Add probable cause
        cause_payload = {
            "description": "TEST_CAUSE_Root cause from automated testing",
            "category": "technical",
            "evidence": "Evidence from automated test",
            "added_by": "pytest"
        }
        response = requests.post(f"{BASE_URL}/api/capa/{capa_id}/investigation/probable-cause", json=cause_payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "cause" in data
        assert data["cause"]["description"] == cause_payload["description"]
        assert data["cause"]["status"] == "probable"
        
        print(f"Added probable cause to CAPA {capa_id}")
        return capa_id, data["cause"]["id"]
    
    def test_add_probable_cause_nonexistent_capa(self):
        """Test adding cause to non-existent CAPA returns 404"""
        cause_payload = {
            "description": "Test cause",
            "category": "technical"
        }
        response = requests.post(f"{BASE_URL}/api/capa/CAPA-NONEXISTENT-12345678/investigation/probable-cause", json=cause_payload)
        assert response.status_code == 404


class TestCAPAContainment:
    """Test CAPA Containment endpoints"""
    
    def test_add_containment_action(self):
        """Test adding a containment action"""
        # Get or create a CAPA
        list_response = requests.get(f"{BASE_URL}/api/capa/list")
        capas = list_response.json()["capas"]
        
        if len(capas) == 0:
            create_payload = {
                "title": "TEST_CAPA_Containment Test",
                "problem_statement": "Testing containment features"
            }
            create_response = requests.post(f"{BASE_URL}/api/capa/create", json=create_payload)
            capa_id = create_response.json()["capa"]["id"]
        else:
            capa_id = capas[0]["id"]
        
        # Add containment action
        action_payload = {
            "description": "TEST_ACTION_Immediate containment action from automated test",
            "responsible": "Test Engineer",
            "due_date": "2026-02-15"
        }
        response = requests.post(f"{BASE_URL}/api/capa/{capa_id}/containment/action", json=action_payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "action" in data
        assert data["action"]["description"] == action_payload["description"]
        assert data["action"]["status"] == "planned"
        
        print(f"Added containment action to CAPA {capa_id}")


class TestCAPAResolution:
    """Test CAPA Resolution endpoints"""
    
    def test_add_corrective_action(self):
        """Test adding a corrective action"""
        list_response = requests.get(f"{BASE_URL}/api/capa/list")
        capas = list_response.json()["capas"]
        
        if len(capas) == 0:
            pytest.skip("No CAPAs exist")
        
        capa_id = capas[0]["id"]
        
        action_payload = {
            "description": "TEST_ACTION_Corrective action from automated test",
            "how_it_addresses_problem": "Fixes the root cause",
            "how_it_prevents_recurrence": "Prevents future occurrence",
            "responsible": "Test Engineer"
        }
        response = requests.post(f"{BASE_URL}/api/capa/{capa_id}/resolution/corrective-action", json=action_payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "action" in data
        assert data["action"]["action_type"] == "corrective"
        
        print(f"Added corrective action to CAPA {capa_id}")
    
    def test_add_preventive_action(self):
        """Test adding a preventive action"""
        list_response = requests.get(f"{BASE_URL}/api/capa/list")
        capas = list_response.json()["capas"]
        
        if len(capas) == 0:
            pytest.skip("No CAPAs exist")
        
        capa_id = capas[0]["id"]
        
        action_payload = {
            "description": "TEST_ACTION_Preventive action from automated test",
            "safeguard_type": "process",
            "how_it_prevents_future": "Adds safeguard to prevent future issues",
            "responsible": "Test Engineer"
        }
        response = requests.post(f"{BASE_URL}/api/capa/{capa_id}/resolution/preventive-action", json=action_payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "action" in data
        assert data["action"]["action_type"] == "preventive"
        
        print(f"Added preventive action to CAPA {capa_id}")


class TestCAPAVOE:
    """Test CAPA VOE (Verification of Effectiveness) endpoints"""
    
    def test_add_voe(self):
        """Test adding a VOE entry"""
        list_response = requests.get(f"{BASE_URL}/api/capa/list")
        capas = list_response.json()["capas"]
        
        if len(capas) == 0:
            pytest.skip("No CAPAs exist")
        
        capa_id = capas[0]["id"]
        
        voe_payload = {
            "action_id": "test_action",
            "verification_method": "TEST_VOE_Automated verification method",
            "acceptance_criteria": "All tests pass",
            "test_procedure": "Run automated tests",
            "responsible": "QA Engineer"
        }
        response = requests.post(f"{BASE_URL}/api/capa/{capa_id}/voe", json=voe_payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "voe" in data
        assert data["voe"]["status"] == "pending"
        
        print(f"Added VOE to CAPA {capa_id}")


class TestCAPAAutomatorIntegration:
    """Test CAPA Automator Integration endpoint"""
    
    def test_create_from_qa(self):
        """Test creating CAPA from QA findings"""
        params = {
            "title": "TEST_CAPA_QA Finding from Automated Test",
            "problem_statement": "Automated QA detected an issue",
            "source": "Automated Testing",
            "severity": "low"
        }
        response = requests.post(f"{BASE_URL}/api/capa/automator/create-from-qa", params=params)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["capa"]["source"] == "Automated Testing"
        assert data["capa"]["created_by"] == "Karau Automator"
        
        print(f"Created CAPA from QA: {data['capa']['id']}")


class TestCAPAFullWorkflow:
    """Test complete CAPA workflow"""
    
    def test_full_capa_lifecycle(self):
        """Test creating and progressing a CAPA through its lifecycle"""
        # 1. Create CAPA
        create_payload = {
            "title": "TEST_CAPA_Full Lifecycle Test",
            "problem_statement": "Testing complete CAPA workflow",
            "severity": "low",
            "source": "Automated Testing"
        }
        create_response = requests.post(f"{BASE_URL}/api/capa/create", json=create_payload)
        assert create_response.status_code == 200
        capa_id = create_response.json()["capa"]["id"]
        print(f"1. Created CAPA: {capa_id}")
        
        # 2. Move to Investigation
        status_response = requests.put(f"{BASE_URL}/api/capa/{capa_id}/status", 
                                       json={"status": "investigation"})
        assert status_response.status_code == 200
        print("2. Moved to Investigation")
        
        # 3. Add probable cause
        cause_response = requests.post(f"{BASE_URL}/api/capa/{capa_id}/investigation/probable-cause",
                                       json={"description": "Test root cause", "category": "process"})
        assert cause_response.status_code == 200
        print("3. Added probable cause")
        
        # 4. Move to Containment
        status_response = requests.put(f"{BASE_URL}/api/capa/{capa_id}/status",
                                       json={"status": "containment"})
        assert status_response.status_code == 200
        print("4. Moved to Containment")
        
        # 5. Add containment action
        action_response = requests.post(f"{BASE_URL}/api/capa/{capa_id}/containment/action",
                                        json={"description": "Immediate fix", "responsible": "Test"})
        assert action_response.status_code == 200
        print("5. Added containment action")
        
        # 6. Verify final state
        final_response = requests.get(f"{BASE_URL}/api/capa/{capa_id}")
        assert final_response.status_code == 200
        final_capa = final_response.json()
        
        assert final_capa["status"] == "containment"
        assert len(final_capa["investigation"]["probable_causes"]) >= 1
        assert len(final_capa["containment"]["actions"]) >= 1
        assert len(final_capa["history"]) >= 3  # created + 2 status changes
        
        print(f"6. Verified CAPA lifecycle - Final status: {final_capa['status']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
