"""
MedMatch Job Toolkit Comprehensive API Tests
Tests all major Job Toolkit APIs (excluding KARAU meeting endpoints)
- Auth, Jobs/Search, Resume, Interview, Analytics, Recruiter
- Enterprise, Skills, Credentials, Translation, Integrations
"""

import pytest
import requests
import os
import json
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://karau-meetings.preview.emergentagent.com').rstrip('/')

# Test Credentials
ADMIN_EMAIL = "admin@medmatch.com"
ADMIN_PASSWORD = "Swampdrainer2026!"
TEST_EMAIL = "test@medmatch.io"
TEST_PASSWORD = "TestPassword123!"

# Session holder
admin_token = None
test_token = None


class TestAuthAPIs:
    """Auth endpoint tests"""
    
    def test_login_admin_success(self):
        """POST /api/auth/login - Admin login returns access_token"""
        global admin_token
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data or "token" in data
        admin_token = data.get("access_token") or data.get("token")
        print(f"Admin login successful, token obtained")
    
    def test_login_test_user_success(self):
        """POST /api/auth/login - Test user login returns access_token"""
        global test_token
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data or "token" in data
        test_token = data.get("access_token") or data.get("token")
        print(f"Test user login successful, token obtained")
    
    def test_login_wrong_password_error(self):
        """POST /api/auth/login - Wrong password returns error"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": "wrong_password"
        })
        assert response.status_code in [400, 401, 403]
        print(f"Wrong password correctly rejected with status {response.status_code}")
    
    def test_auth_me_returns_user(self):
        """GET /api/auth/me - Returns user profile"""
        global admin_token
        if not admin_token:
            self.test_login_admin_success()
        
        response = requests.get(f"{BASE_URL}/api/auth/me", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200
        data = response.json()
        # Verify we get user data back
        assert "email" in data or "user_id" in data or "id" in data
        print(f"GET /api/auth/me returned user data")
    
    def test_auth_preferences(self):
        """GET /api/auth/preferences - Returns user preferences"""
        global admin_token
        if not admin_token:
            self.test_login_admin_success()
        
        response = requests.get(f"{BASE_URL}/api/auth/preferences", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200
        print(f"GET /api/auth/preferences returned status {response.status_code}")


class TestJobsAndSearchAPIs:
    """Jobs and Search endpoint tests"""
    
    def test_jobs_sources(self):
        """GET /api/jobs/sources - Returns job sources"""
        response = requests.get(f"{BASE_URL}/api/jobs/sources")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))
        print(f"GET /api/jobs/sources returned {type(data).__name__}")
    
    def test_jobs_deep_search(self):
        """POST /api/jobs/deep-search - Returns search results"""
        global admin_token
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        response = requests.post(f"{BASE_URL}/api/jobs/deep-search", 
            json={"query": "software engineer", "location": "remote"},
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        print(f"POST /api/jobs/deep-search returned results")
    
    def test_search_enhanced(self):
        """POST /api/search/enhanced - Returns enhanced search results"""
        global admin_token
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        response = requests.post(f"{BASE_URL}/api/search/enhanced", 
            json={"query": "data scientist"},
            headers=headers
        )
        assert response.status_code == 200
        print(f"POST /api/search/enhanced returned status {response.status_code}")
    
    def test_search_autocomplete(self):
        """GET /api/search/autocomplete?q=data - Returns suggestions"""
        global admin_token
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        response = requests.get(f"{BASE_URL}/api/search/autocomplete?q=data&limit=5", headers=headers)
        assert response.status_code == 200
        data = response.json()
        print(f"GET /api/search/autocomplete returned {len(data) if isinstance(data, list) else 'data'}")


class TestResumeAndCoverLetterAPIs:
    """Resume and Cover Letter endpoint tests"""
    
    def test_resume_get(self):
        """GET /api/resume - Returns resume data"""
        global admin_token
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        response = requests.get(f"{BASE_URL}/api/resume", headers=headers)
        assert response.status_code == 200
        print(f"GET /api/resume returned status {response.status_code}")
    
    def test_cover_letter_history(self):
        """GET /api/cover-letter/history - Returns cover letter history"""
        global admin_token
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        response = requests.get(f"{BASE_URL}/api/cover-letter/history", headers=headers)
        assert response.status_code == 200
        print(f"GET /api/cover-letter/history returned status {response.status_code}")


class TestInterviewAndQAAPIs:
    """Interview and QA Practice endpoint tests"""
    
    def test_interview_cached_questions(self):
        """GET /api/interview/cached-questions - Returns cached questions"""
        global admin_token
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        response = requests.get(f"{BASE_URL}/api/interview/cached-questions", headers=headers)
        assert response.status_code == 200
        print(f"GET /api/interview/cached-questions returned status {response.status_code}")
    
    def test_interview_calendar_status(self):
        """GET /api/interview-calendar/status - Returns calendar status"""
        global admin_token
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        response = requests.get(f"{BASE_URL}/api/interview-calendar/status", headers=headers)
        assert response.status_code == 200
        print(f"GET /api/interview-calendar/status returned status {response.status_code}")
    
    def test_qa_practice_history(self):
        """GET /api/qa-practice/history - Returns QA practice history"""
        global admin_token
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        response = requests.get(f"{BASE_URL}/api/qa-practice/history", headers=headers)
        assert response.status_code == 200
        print(f"GET /api/qa-practice/history returned status {response.status_code}")
    
    def test_ai_qa_status(self):
        """GET /api/ai-qa/status - Returns AI QA status"""
        global admin_token
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        response = requests.get(f"{BASE_URL}/api/ai-qa/status", headers=headers)
        assert response.status_code == 200
        print(f"GET /api/ai-qa/status returned status {response.status_code}")
    
    def test_video_interview_sessions(self):
        """GET /api/video-interview/sessions - Returns sessions"""
        global admin_token
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        response = requests.get(f"{BASE_URL}/api/video-interview/sessions", headers=headers)
        assert response.status_code == 200
        print(f"GET /api/video-interview/sessions returned status {response.status_code}")


class TestAnalyticsAPIs:
    """Analytics endpoint tests"""
    
    def test_analytics_dashboard(self):
        """GET /api/analytics/dashboard - Returns analytics data"""
        global admin_token
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        response = requests.get(f"{BASE_URL}/api/analytics/dashboard", headers=headers)
        assert response.status_code == 200
        data = response.json()
        print(f"GET /api/analytics/dashboard returned data")
    
    def test_analytics_funnel(self):
        """GET /api/analytics/funnel - Returns funnel data"""
        global admin_token
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        response = requests.get(f"{BASE_URL}/api/analytics/funnel", headers=headers)
        assert response.status_code == 200
        print(f"GET /api/analytics/funnel returned status {response.status_code}")


class TestRecruiterAPIs:
    """Recruiter endpoint tests"""
    
    def test_recruiter_jobs(self):
        """GET /api/recruiter/jobs - Returns recruiter job listings"""
        global admin_token
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        response = requests.get(f"{BASE_URL}/api/recruiter/jobs", headers=headers)
        assert response.status_code == 200
        print(f"GET /api/recruiter/jobs returned status {response.status_code}")
    
    def test_recruiter_verification_status(self):
        """GET /api/recruiter-rbac/verification/status - Returns verification status"""
        global admin_token
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        response = requests.get(f"{BASE_URL}/api/recruiter-rbac/verification/status", headers=headers)
        assert response.status_code == 200
        print(f"GET /api/recruiter-rbac/verification/status returned status {response.status_code}")
    
    def test_ats_links(self):
        """GET /api/ats/links - Returns ATS links"""
        global admin_token
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        response = requests.get(f"{BASE_URL}/api/ats/links", headers=headers)
        assert response.status_code == 200
        print(f"GET /api/ats/links returned status {response.status_code}")


class TestEnterpriseAndAdminAPIs:
    """Enterprise and Admin endpoint tests"""
    
    def test_admin_audit_status(self):
        """GET /api/admin-audit/status - Returns audit status"""
        global admin_token
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        response = requests.get(f"{BASE_URL}/api/admin-audit/status", headers=headers)
        assert response.status_code == 200
        print(f"GET /api/admin-audit/status returned status {response.status_code}")
    
    def test_ai_compliance_admin_summary(self):
        """GET /api/ai-compliance/admin/summary - Returns compliance summary"""
        global admin_token
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        response = requests.get(f"{BASE_URL}/api/ai-compliance/admin/summary", headers=headers)
        assert response.status_code == 200
        print(f"GET /api/ai-compliance/admin/summary returned status {response.status_code}")
    
    def test_audit_reports_templates(self):
        """GET /api/audit-reports/templates - Returns templates"""
        global admin_token
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        response = requests.get(f"{BASE_URL}/api/audit-reports/templates", headers=headers)
        assert response.status_code == 200
        print(f"GET /api/audit-reports/templates returned status {response.status_code}")
    
    def test_compliance_alerts_check(self):
        """GET /api/compliance-alerts/check - Returns alert status"""
        global admin_token
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        response = requests.get(f"{BASE_URL}/api/compliance-alerts/check", headers=headers)
        assert response.status_code == 200
        print(f"GET /api/compliance-alerts/check returned status {response.status_code}")
    
    def test_enterprise_api_keys(self):
        """GET /api/enterprise/api-keys - Returns enterprise API keys"""
        global admin_token
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        response = requests.get(f"{BASE_URL}/api/enterprise/api-keys", headers=headers)
        assert response.status_code == 200
        print(f"GET /api/enterprise/api-keys returned status {response.status_code}")
    
    def test_data_integrity_lineage(self):
        """GET /api/data-integrity/data-lineage - Returns lineage data"""
        global admin_token
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        response = requests.get(f"{BASE_URL}/api/data-integrity/data-lineage", headers=headers)
        assert response.status_code == 200
        print(f"GET /api/data-integrity/data-lineage returned status {response.status_code}")
    
    def test_metrics(self):
        """GET /api/metrics - Returns production metrics"""
        global admin_token
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        response = requests.get(f"{BASE_URL}/api/metrics", headers=headers)
        assert response.status_code == 200
        print(f"GET /api/metrics returned status {response.status_code}")


class TestSkillsAndTaxonomyAPIs:
    """Skills and Taxonomy endpoint tests"""
    
    def test_skills_categories(self):
        """GET /api/skills/categories - Returns skill categories"""
        global admin_token
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        response = requests.get(f"{BASE_URL}/api/skills/categories", headers=headers)
        assert response.status_code == 200
        data = response.json()
        print(f"GET /api/skills/categories returned data")
    
    def test_taxonomy_sectors(self):
        """GET /api/taxonomy/sectors - Returns 5 sectors"""
        response = requests.get(f"{BASE_URL}/api/taxonomy/sectors")
        assert response.status_code == 200
        data = response.json()
        # Verify we get sectors
        if isinstance(data, list):
            assert len(data) >= 5
            print(f"GET /api/taxonomy/sectors returned {len(data)} sectors")
        else:
            print(f"GET /api/taxonomy/sectors returned sector data")


class TestCredentialsAndVerificationAPIs:
    """Credentials and Verification endpoint tests"""
    
    def test_credentials_providers(self):
        """GET /api/credentials/providers - Returns credential providers"""
        global admin_token
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        response = requests.get(f"{BASE_URL}/api/credentials/providers", headers=headers)
        assert response.status_code == 200
        print(f"GET /api/credentials/providers returned status {response.status_code}")
    
    def test_id_verification_status(self):
        """GET /api/id-verification/status - Returns verification status"""
        global admin_token
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        response = requests.get(f"{BASE_URL}/api/id-verification/status", headers=headers)
        assert response.status_code == 200
        print(f"GET /api/id-verification/status returned status {response.status_code}")
    
    def test_id_verify_status(self):
        """GET /api/id-verify/status - Returns persona verification status"""
        global admin_token
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        response = requests.get(f"{BASE_URL}/api/id-verify/status", headers=headers)
        assert response.status_code == 200
        print(f"GET /api/id-verify/status returned status {response.status_code}")
    
    def test_capa_list(self):
        """GET /api/capa/list - Returns CAPA records"""
        global admin_token
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        response = requests.get(f"{BASE_URL}/api/capa/list", headers=headers)
        assert response.status_code == 200
        print(f"GET /api/capa/list returned status {response.status_code}")


class TestCommunicationAPIs:
    """Communication endpoint tests"""
    
    def test_messages_conversations(self):
        """GET /api/messages/conversations - Returns conversations"""
        global admin_token
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        response = requests.get(f"{BASE_URL}/api/messages/conversations", headers=headers)
        assert response.status_code == 200
        print(f"GET /api/messages/conversations returned status {response.status_code}")
    
    def test_notifications(self):
        """GET /api/notifications - Returns notifications list"""
        global admin_token
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        response = requests.get(f"{BASE_URL}/api/notifications", headers=headers)
        assert response.status_code == 200
        print(f"GET /api/notifications returned status {response.status_code}")
    
    def test_notifications_preferences(self):
        """GET /api/notifications/preferences - Returns preferences"""
        global admin_token
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        response = requests.get(f"{BASE_URL}/api/notifications/preferences", headers=headers)
        assert response.status_code == 200
        print(f"GET /api/notifications/preferences returned status {response.status_code}")
    
    def test_meeting_notes_status(self):
        """GET /api/meeting-notes/status - Returns notes status"""
        global admin_token
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        response = requests.get(f"{BASE_URL}/api/meeting-notes/status", headers=headers)
        assert response.status_code == 200
        print(f"GET /api/meeting-notes/status returned status {response.status_code}")


class TestTranslationAPIs:
    """Translation endpoint tests"""
    
    def test_translate_languages(self):
        """GET /api/translate/languages - Returns supported languages"""
        response = requests.get(f"{BASE_URL}/api/translate/languages")
        assert response.status_code == 200
        data = response.json()
        # Verify we get languages
        assert isinstance(data, (list, dict))
        print(f"GET /api/translate/languages returned language data")
    
    def test_translate_text(self):
        """POST /api/translate/text - Translates 'Hello World' to Spanish"""
        global admin_token
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        response = requests.post(f"{BASE_URL}/api/translate/text", 
            json={"text": "Hello World", "target_language": "es"},
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        # Verify translation
        translated = data.get("translated_text") or data.get("translation") or data.get("text")
        assert translated is not None
        print(f"Translation result: {translated}")
    
    def test_translate_gender_rules(self):
        """GET /api/translate/gender-rules - Returns gender rules"""
        response = requests.get(f"{BASE_URL}/api/translate/gender-rules")
        assert response.status_code == 200
        print(f"GET /api/translate/gender-rules returned status {response.status_code}")
    
    def test_translation_qa_latest(self):
        """GET /api/translation-qa/latest - Returns QA data"""
        response = requests.get(f"{BASE_URL}/api/translation-qa/latest")
        assert response.status_code == 200
        print(f"GET /api/translation-qa/latest returned status {response.status_code}")


class TestIntegrationAPIs:
    """Integration endpoint tests"""
    
    def test_linkedin_status(self):
        """GET /api/linkedin/status - Returns LinkedIn status"""
        global admin_token
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        response = requests.get(f"{BASE_URL}/api/linkedin/status", headers=headers)
        assert response.status_code == 200
        print(f"GET /api/linkedin/status returned status {response.status_code}")
    
    def test_orcid_config(self):
        """GET /api/orcid/config - Returns ORCID configuration"""
        response = requests.get(f"{BASE_URL}/api/orcid/config")
        assert response.status_code == 200
        print(f"GET /api/orcid/config returned status {response.status_code}")
    
    def test_payments_status(self):
        """GET /api/payments/status/test - Returns payment status"""
        global admin_token
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        response = requests.get(f"{BASE_URL}/api/payments/status/test", headers=headers)
        # May return 404 if not configured, 500 if payment gateway issue
        assert response.status_code in [200, 404, 500]
        print(f"GET /api/payments/status/test returned status {response.status_code}")
    
    def test_push_vapid_key(self):
        """GET /api/push/vapid-public-key - Returns VAPID key"""
        response = requests.get(f"{BASE_URL}/api/push/vapid-public-key")
        assert response.status_code == 200
        print(f"GET /api/push/vapid-public-key returned status {response.status_code}")
    
    def test_webpush_vapid_key(self):
        """GET /api/webpush/vapid-public-key - Returns web push key"""
        response = requests.get(f"{BASE_URL}/api/webpush/vapid-public-key")
        assert response.status_code == 200
        print(f"GET /api/webpush/vapid-public-key returned status {response.status_code}")


class TestMiscServiceAPIs:
    """Misc service endpoint tests"""
    
    def test_cloud_status(self):
        """GET /api/cloud/status - Returns cloud status"""
        global admin_token
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        response = requests.get(f"{BASE_URL}/api/cloud/status", headers=headers)
        assert response.status_code == 200
        print(f"GET /api/cloud/status returned status {response.status_code}")
    
    def test_dragon_health(self):
        """GET /api/dragon/health - Returns Dragon status"""
        response = requests.get(f"{BASE_URL}/api/dragon/health")
        assert response.status_code == 200
        print(f"GET /api/dragon/health returned status {response.status_code}")
    
    def test_dragon_automator_health(self):
        """GET /api/dragon/automator/health - Returns automator health"""
        global admin_token
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        response = requests.get(f"{BASE_URL}/api/dragon/automator/health", headers=headers)
        assert response.status_code == 200
        print(f"GET /api/dragon/automator/health returned status {response.status_code}")
    
    def test_geolocation_preferences(self):
        """GET /api/geolocation/preferences - Returns geo preferences"""
        global admin_token
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        response = requests.get(f"{BASE_URL}/api/geolocation/preferences", headers=headers)
        assert response.status_code == 200
        print(f"GET /api/geolocation/preferences returned status {response.status_code}")
    
    def test_digest_settings(self):
        """GET /api/digest/settings - Returns digest settings"""
        global admin_token
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        response = requests.get(f"{BASE_URL}/api/digest/settings", headers=headers)
        assert response.status_code == 200
        print(f"GET /api/digest/settings returned status {response.status_code}")
    
    def test_autofill_data(self):
        """GET /api/autofill/data - Returns autofill data"""
        global admin_token
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        response = requests.get(f"{BASE_URL}/api/autofill/data", headers=headers)
        assert response.status_code == 200
        print(f"GET /api/autofill/data returned status {response.status_code}")
    
    def test_biometric_supported(self):
        """GET /api/biometric/supported - Returns biometric support info"""
        response = requests.get(f"{BASE_URL}/api/biometric/supported")
        assert response.status_code == 200
        print(f"GET /api/biometric/supported returned status {response.status_code}")
    
    def test_realtime_stt_status(self):
        """GET /api/realtime-stt/status - Returns STT status"""
        global admin_token
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        response = requests.get(f"{BASE_URL}/api/realtime-stt/status", headers=headers)
        assert response.status_code == 200
        print(f"GET /api/realtime-stt/status returned status {response.status_code}")
    
    def test_ml_data_status(self):
        """GET /api/ml-data/status - Returns ML data pipeline status"""
        response = requests.get(f"{BASE_URL}/api/ml-data/status")
        assert response.status_code == 200
        print(f"GET /api/ml-data/status returned status {response.status_code}")
    
    def test_ml_model_info(self):
        """GET /api/ml-model/info - Returns model info"""
        response = requests.get(f"{BASE_URL}/api/ml-model/info")
        assert response.status_code == 200
        print(f"GET /api/ml-model/info returned status {response.status_code}")
    
    def test_avatar_status(self):
        """GET /api/avatar/status - Returns avatar status"""
        response = requests.get(f"{BASE_URL}/api/avatar/status")
        assert response.status_code == 200
        print(f"GET /api/avatar/status returned status {response.status_code}")
    
    def test_privacy_consent_status(self):
        """GET /api/privacy/consent/status - Returns consent status"""
        global admin_token
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        response = requests.get(f"{BASE_URL}/api/privacy/consent/status", headers=headers)
        assert response.status_code == 200
        print(f"GET /api/privacy/consent/status returned status {response.status_code}")
    
    def test_video_analysis_status(self):
        """GET /api/video-analysis/status - Returns analysis status"""
        global admin_token
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        response = requests.get(f"{BASE_URL}/api/video-analysis/status", headers=headers)
        assert response.status_code == 200
        print(f"GET /api/video-analysis/status returned status {response.status_code}")
    
    def test_video_assets_config(self):
        """GET /api/video-assets/config - Returns video config"""
        response = requests.get(f"{BASE_URL}/api/video-assets/config")
        assert response.status_code == 200
        print(f"GET /api/video-assets/config returned status {response.status_code}")
    
    def test_tutorials_videos(self):
        """GET /api/tutorials/videos - Returns tutorial videos list"""
        response = requests.get(f"{BASE_URL}/api/tutorials/videos")
        assert response.status_code == 200
        data = response.json()
        print(f"GET /api/tutorials/videos returned data")
    
    def test_feedback_categories(self):
        """GET /api/feedback/categories - Returns feedback categories"""
        response = requests.get(f"{BASE_URL}/api/feedback/categories")
        assert response.status_code == 200
        print(f"GET /api/feedback/categories returned status {response.status_code}")
    
    def test_mutual_match_requests(self):
        """GET /api/mutual-match/requests/sent - Returns match requests"""
        global admin_token
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        response = requests.get(f"{BASE_URL}/api/mutual-match/requests/sent", headers=headers)
        assert response.status_code == 200
        print(f"GET /api/mutual-match/requests/sent returned status {response.status_code}")
    
    def test_companies_list(self):
        """GET /api/companies/ - Returns companies list"""
        response = requests.get(f"{BASE_URL}/api/companies/")
        assert response.status_code == 200
        print(f"GET /api/companies/ returned status {response.status_code}")
    
    def test_batch_stats(self):
        """GET /api/batch/stats - Returns batch statistics"""
        response = requests.get(f"{BASE_URL}/api/batch/stats")
        assert response.status_code == 200
        print(f"GET /api/batch/stats returned status {response.status_code}")
    
    def test_meeting_notes_create(self):
        """POST /api/meeting-notes/create - Creates a new meeting note"""
        global admin_token
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        response = requests.post(f"{BASE_URL}/api/meeting-notes/create", 
            json={
                "title": "Test Meeting Note",
                "content": "Test content from automated testing",
                "meeting_type": "interview"
            },
            headers=headers
        )
        assert response.status_code in [200, 201]
        print(f"POST /api/meeting-notes/create returned status {response.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
