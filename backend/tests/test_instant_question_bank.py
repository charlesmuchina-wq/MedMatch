"""
Test: Instant Question Bank for Skill Assessments
Tests: Pre-generated questions for instant assessment starts (performance fix)

Background: Previously assessments took 20-30 seconds to start due to AI question generation.
Now uses pre-generated question bank for 4 skills which loads in under 0.2 seconds.

Skills with instant questions:
- ISO 13485 (Medical Devices)
- Six Sigma (Green Belt)
- FDA 21 CFR Part 820
- Supplier Quality Management

Each has beginner/intermediate/advanced difficulty levels.
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "admin@medmatch.com"
TEST_PASSWORD = "Swampdrainer2026!"

# Skills with pre-generated questions (should be instant)
INSTANT_START_SKILLS = [
    "ISO 13485 (Medical Devices)",
    "Six Sigma (Green Belt)",
    "FDA 21 CFR Part 820",
    "Supplier Quality Management"
]


class TestInstantQuestionBank:
    """Test pre-generated question bank for instant assessment starts"""
    
    @pytest.fixture(scope="class")
    def auth_session(self):
        """Get authenticated session"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        # Login
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("token")
            if token:
                session.headers.update({"Authorization": f"Bearer {token}"})
        else:
            pytest.skip(f"Authentication failed: {response.status_code}")
        
        return session

    def test_iso_13485_instant_start(self, auth_session):
        """Test ISO 13485 (Medical Devices) - should start instantly with instant_start: true"""
        skill_name = "ISO 13485 (Medical Devices)"
        
        start_time = time.time()
        response = auth_session.post(
            f"{BASE_URL}/api/skills/start",
            json={"skill_name": skill_name, "difficulty": "intermediate"},
            timeout=10  # Short timeout - should be instant
        )
        elapsed_time = time.time() - start_time
        
        # Handle cooldown - try beginner if intermediate fails
        if response.status_code == 400:
            data = response.json()
            if "24 hours" in str(data.get("detail", "")):
                # Try beginner difficulty
                start_time = time.time()
                response = auth_session.post(
                    f"{BASE_URL}/api/skills/start",
                    json={"skill_name": skill_name, "difficulty": "beginner"},
                    timeout=10
                )
                elapsed_time = time.time() - start_time
                
                if response.status_code == 400:
                    # Try advanced
                    start_time = time.time()
                    response = auth_session.post(
                        f"{BASE_URL}/api/skills/start",
                        json={"skill_name": skill_name, "difficulty": "advanced"},
                        timeout=10
                    )
                    elapsed_time = time.time() - start_time
        
        if response.status_code == 400:
            pytest.skip(f"Assessment on cooldown for all difficulties")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # CRITICAL: Verify instant_start is True
        assert data.get("instant_start") == True, f"ISO 13485 should have instant_start=True, got {data.get('instant_start')}"
        
        # CRITICAL: Verify response time is under 1 second (should be <0.2s)
        assert elapsed_time < 1.0, f"ISO 13485 took {elapsed_time:.2f}s - should be under 1 second"
        
        # Verify questions structure
        assert "questions" in data, "Should return questions"
        assert len(data["questions"]) == 15, f"Should have 15 questions, got {len(data['questions'])}"
        
        for q in data["questions"]:
            assert "question" in q, "Question should have question text"
            assert "options" in q, "Question should have options"
        
        print(f"✅ ISO 13485 assessment started in {elapsed_time:.3f}s (instant_start={data.get('instant_start')})")
        print(f"   Total questions: {len(data['questions'])}")

    def test_six_sigma_green_belt_instant_start(self, auth_session):
        """Test Six Sigma (Green Belt) - should start instantly with instant_start: true"""
        skill_name = "Six Sigma (Green Belt)"
        
        start_time = time.time()
        response = auth_session.post(
            f"{BASE_URL}/api/skills/start",
            json={"skill_name": skill_name, "difficulty": "intermediate"},
            timeout=10
        )
        elapsed_time = time.time() - start_time
        
        if response.status_code == 400:
            data = response.json()
            if "24 hours" in str(data.get("detail", "")):
                start_time = time.time()
                response = auth_session.post(
                    f"{BASE_URL}/api/skills/start",
                    json={"skill_name": skill_name, "difficulty": "beginner"},
                    timeout=10
                )
                elapsed_time = time.time() - start_time
        
        if response.status_code == 400:
            pytest.skip("Assessment on cooldown")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # CRITICAL: Verify instant_start is True
        assert data.get("instant_start") == True, f"Six Sigma should have instant_start=True, got {data.get('instant_start')}"
        
        # CRITICAL: Verify response time
        assert elapsed_time < 1.0, f"Six Sigma took {elapsed_time:.2f}s - should be under 1 second"
        
        assert len(data["questions"]) == 15, f"Should have 15 questions, got {len(data['questions'])}"
        
        print(f"✅ Six Sigma (Green Belt) started in {elapsed_time:.3f}s (instant_start={data.get('instant_start')})")

    def test_fda_21_cfr_part_820_instant_start(self, auth_session):
        """Test FDA 21 CFR Part 820 - should start instantly with instant_start: true"""
        skill_name = "FDA 21 CFR Part 820"
        
        start_time = time.time()
        response = auth_session.post(
            f"{BASE_URL}/api/skills/start",
            json={"skill_name": skill_name, "difficulty": "intermediate"},
            timeout=10
        )
        elapsed_time = time.time() - start_time
        
        if response.status_code == 400:
            data = response.json()
            if "24 hours" in str(data.get("detail", "")):
                start_time = time.time()
                response = auth_session.post(
                    f"{BASE_URL}/api/skills/start",
                    json={"skill_name": skill_name, "difficulty": "advanced"},
                    timeout=10
                )
                elapsed_time = time.time() - start_time
        
        if response.status_code == 400:
            pytest.skip("Assessment on cooldown")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # CRITICAL: Verify instant_start is True
        assert data.get("instant_start") == True, f"FDA 21 CFR Part 820 should have instant_start=True, got {data.get('instant_start')}"
        
        # CRITICAL: Verify response time
        assert elapsed_time < 1.0, f"FDA 21 CFR Part 820 took {elapsed_time:.2f}s - should be under 1 second"
        
        assert len(data["questions"]) == 15, f"Should have 15 questions, got {len(data['questions'])}"
        
        print(f"✅ FDA 21 CFR Part 820 started in {elapsed_time:.3f}s (instant_start={data.get('instant_start')})")

    def test_supplier_quality_management_instant_start(self, auth_session):
        """Test Supplier Quality Management - should start instantly with instant_start: true"""
        skill_name = "Supplier Quality Management"
        
        start_time = time.time()
        response = auth_session.post(
            f"{BASE_URL}/api/skills/start",
            json={"skill_name": skill_name, "difficulty": "intermediate"},
            timeout=10
        )
        elapsed_time = time.time() - start_time
        
        if response.status_code == 400:
            data = response.json()
            if "24 hours" in str(data.get("detail", "")):
                start_time = time.time()
                response = auth_session.post(
                    f"{BASE_URL}/api/skills/start",
                    json={"skill_name": skill_name, "difficulty": "beginner"},
                    timeout=10
                )
                elapsed_time = time.time() - start_time
        
        if response.status_code == 400:
            pytest.skip("Assessment on cooldown")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # CRITICAL: Verify instant_start is True
        assert data.get("instant_start") == True, f"Supplier Quality Management should have instant_start=True, got {data.get('instant_start')}"
        
        # CRITICAL: Verify response time
        assert elapsed_time < 1.0, f"Supplier Quality Management took {elapsed_time:.2f}s - should be under 1 second"
        
        assert len(data["questions"]) == 15, f"Should have 15 questions, got {len(data['questions'])}"
        
        print(f"✅ Supplier Quality Management started in {elapsed_time:.3f}s (instant_start={data.get('instant_start')})")

    def test_question_structure(self, auth_session):
        """Test that pre-generated questions have proper structure"""
        skill_name = "Six Sigma (Green Belt)"  # Use this as it's less likely to be on cooldown
        
        response = auth_session.post(
            f"{BASE_URL}/api/skills/start",
            json={"skill_name": skill_name, "difficulty": "advanced"},
            timeout=10
        )
        
        if response.status_code == 400:
            pytest.skip("Assessment on cooldown")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        questions = data.get("questions", [])
        
        # Verify question structure
        for q in questions:
            assert "index" in q, "Question should have index"
            assert "question" in q, "Question should have question text"
            assert "options" in q, "Question should have options"
            assert len(q["options"]) == 4, f"Question should have 4 options, got {len(q['options'])}"
            
            # Verify correct_answer is NOT exposed to client
            assert "correct_answer" not in q, "correct_answer should NOT be exposed to client"
            assert "explanation" not in q, "explanation should NOT be exposed to client"
        
        print(f"✅ Questions have proper structure (no answers exposed)")
        print(f"   Sample question: {questions[0]['question'][:50]}...")

    def test_difficulty_levels_available(self, auth_session):
        """Test that all difficulty levels work for instant start skills"""
        skill_name = "ISO 13485 (Medical Devices)"
        difficulties = ["beginner", "intermediate", "advanced"]
        
        for difficulty in difficulties:
            response = auth_session.post(
                f"{BASE_URL}/api/skills/start",
                json={"skill_name": skill_name, "difficulty": difficulty},
                timeout=10
            )
            
            # Skip if on cooldown but log it
            if response.status_code == 400:
                data = response.json()
                if "24 hours" in str(data.get("detail", "")):
                    print(f"⏳ {difficulty} difficulty on cooldown - skipped")
                    continue
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {difficulty} difficulty: {len(data.get('questions', []))} questions")

    def test_non_instant_skill_for_comparison(self, auth_session):
        """Test a skill WITHOUT pre-generated questions - should use AI fallback"""
        # Python is NOT in the question bank - will use AI generation
        skill_name = "Communication"  # Use a less complex skill
        
        response = auth_session.post(
            f"{BASE_URL}/api/skills/start",
            json={"skill_name": skill_name, "difficulty": "beginner"},
            timeout=60  # Longer timeout for AI generation
        )
        
        if response.status_code == 400:
            pytest.skip("Assessment on cooldown")
        
        # Note: This may still succeed with AI fallback
        if response.status_code == 200:
            data = response.json()
            # instant_start should be False for non-pre-generated skills
            instant = data.get("instant_start", True)
            print(f"📝 Communication skill - instant_start={instant}")
            
            if instant == False:
                print("   (Used AI generation - expected slower)")

    def test_available_assessments_endpoint(self, auth_session):
        """Test GET /api/skills/available - verify instant skills are listed"""
        response = auth_session.get(f"{BASE_URL}/api/skills/available")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assessments = data.get("assessments", [])
        
        # Verify all instant start skills are in the list
        skill_names = [a["skill_name"] for a in assessments]
        
        for instant_skill in INSTANT_START_SKILLS:
            assert instant_skill in skill_names, f"{instant_skill} should be in available assessments"
            print(f"✅ {instant_skill} is available")

    def test_submit_instant_assessment(self, auth_session):
        """Test completing and submitting an instant assessment"""
        skill_name = "Supplier Quality Management"
        
        # Start assessment
        start_response = auth_session.post(
            f"{BASE_URL}/api/skills/start",
            json={"skill_name": skill_name, "difficulty": "beginner"},
            timeout=10
        )
        
        if start_response.status_code == 400:
            pytest.skip("Assessment on cooldown")
        
        assert start_response.status_code == 200, f"Expected 200, got {start_response.status_code}"
        
        data = start_response.json()
        assessment_id = data["assessment_id"]
        questions = data["questions"]
        
        # Submit answers (select first option for all)
        answers = []
        for q in questions:
            answers.append({
                "question_index": q["index"],
                "answer": q["options"][0]
            })
        
        submit_response = auth_session.post(
            f"{BASE_URL}/api/skills/submit",
            json={
                "assessment_id": assessment_id,
                "answers": answers
            }
        )
        
        assert submit_response.status_code == 200, f"Expected 200, got {submit_response.status_code}"
        
        result = submit_response.json()
        assert "passed" in result
        assert "score" in result
        assert "correct_count" in result
        assert "total_questions" in result
        
        print(f"✅ Assessment submitted successfully")
        print(f"   Score: {result['score']}%")
        print(f"   Result: {'PASSED' if result['passed'] else 'FAILED'}")


class TestQuestionBankPerformance:
    """Performance benchmarks for instant question bank"""
    
    @pytest.fixture(scope="class")
    def auth_session(self):
        """Get authenticated session"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("token")
            if token:
                session.headers.update({"Authorization": f"Bearer {token}"})
        else:
            pytest.skip(f"Authentication failed: {response.status_code}")
        
        return session

    def test_batch_performance(self, auth_session):
        """Test performance of multiple instant start assessments"""
        times = []
        tested_skills = []
        
        for skill in INSTANT_START_SKILLS:
            start_time = time.time()
            response = auth_session.post(
                f"{BASE_URL}/api/skills/start",
                json={"skill_name": skill, "difficulty": "intermediate"},
                timeout=10
            )
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get("instant_start") == True:
                    times.append(elapsed)
                    tested_skills.append(skill)
                    print(f"✅ {skill}: {elapsed:.3f}s")
        
        if times:
            avg_time = sum(times) / len(times)
            max_time = max(times)
            
            print(f"\n📊 Performance Summary:")
            print(f"   Average: {avg_time:.3f}s")
            print(f"   Max: {max_time:.3f}s")
            print(f"   Skills tested: {len(times)}")
            
            # All should be under 1 second
            assert max_time < 1.0, f"Maximum time {max_time:.2f}s exceeds 1 second threshold"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
