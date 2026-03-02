#!/usr/bin/env python3
"""
Comprehensive backend API testing for MedMatch Job Finder App
Tests all CRUD operations, job search APIs, and AI integrations
"""

import requests
import sys
import json
from datetime import datetime

class MedMatchAPITester:
    def __init__(self, base_url="https://cinematic-meet.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details="", response_data=None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details,
            "response_data": response_data
        })

    def test_api_health(self):
        """Test basic API connectivity"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                details += f", Response: {response.json()}"
            self.log_test("API Health Check", success, details, response.json() if success else None)
            return success
        except Exception as e:
            self.log_test("API Health Check", False, f"Connection error: {str(e)}")
            return False

    def test_resume_upload(self):
        """Test resume upload with a sample PDF"""
        try:
            # Create a simple PDF-like content for testing
            # In real scenario, we'd download the actual resume from the URL
            pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Charles Muchina Resume) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000206 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n299\n%%EOF"
            
            files = {'file': ('charles_resume.pdf', pdf_content, 'application/pdf')}
            response = requests.post(f"{self.api_url}/resume/upload", files=files, timeout=30)
            
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            response_data = None
            
            if success:
                response_data = response.json()
                details += f", Parsed name: {response_data.get('full_name', 'N/A')}"
                details += f", Skills count: {len(response_data.get('skills', []))}"
            else:
                details += f", Error: {response.text}"
                
            self.log_test("Resume Upload & AI Parsing", success, details, response_data)
            return success, response_data
            
        except Exception as e:
            self.log_test("Resume Upload & AI Parsing", False, f"Error: {str(e)}")
            return False, None

    def test_resume_retrieval(self):
        """Test getting uploaded resume"""
        try:
            response = requests.get(f"{self.api_url}/resume", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            response_data = None
            
            if success:
                response_data = response.json()
                if response_data:
                    details += f", Resume found for: {response_data.get('full_name', 'Unknown')}"
                else:
                    details += ", No resume found"
            else:
                details += f", Error: {response.text}"
                
            self.log_test("Resume Retrieval", success, details, response_data)
            return success, response_data
            
        except Exception as e:
            self.log_test("Resume Retrieval", False, f"Error: {str(e)}")
            return False, None

    def test_job_search_remoteok(self):
        """Test RemoteOK job search"""
        try:
            response = requests.get(f"{self.api_url}/jobs/search", 
                                  params={"query": "quality assurance", "source": "remoteok"}, 
                                  timeout=20)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            response_data = None
            
            if success:
                response_data = response.json()
                job_count = len(response_data)
                details += f", Jobs found: {job_count}"
                if job_count > 0:
                    details += f", First job: {response_data[0].get('title', 'N/A')}"
            else:
                details += f", Error: {response.text}"
                
            self.log_test("Job Search - RemoteOK", success, details, response_data)
            return success, response_data
            
        except Exception as e:
            self.log_test("Job Search - RemoteOK", False, f"Error: {str(e)}")
            return False, None

    def test_job_search_remotive(self):
        """Test Remotive job search"""
        try:
            response = requests.get(f"{self.api_url}/jobs/search", 
                                  params={"query": "qa", "source": "remotive"}, 
                                  timeout=20)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            response_data = None
            
            if success:
                response_data = response.json()
                job_count = len(response_data)
                details += f", Jobs found: {job_count}"
                if job_count > 0:
                    details += f", First job: {response_data[0].get('title', 'N/A')}"
            else:
                details += f", Error: {response.text}"
                
            self.log_test("Job Search - Remotive", success, details, response_data)
            return success, response_data
            
        except Exception as e:
            self.log_test("Job Search - Remotive", False, f"Error: {str(e)}")
            return False, None

    def test_job_search_all_sources(self):
        """Test job search from all sources"""
        try:
            response = requests.get(f"{self.api_url}/jobs/search", 
                                  params={"query": "remote", "source": "all"}, 
                                  timeout=25)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            response_data = None
            
            if success:
                response_data = response.json()
                job_count = len(response_data)
                details += f", Total jobs found: {job_count}"
                
                # Count jobs by source
                sources = {}
                for job in response_data:
                    source = job.get('source', 'Unknown')
                    sources[source] = sources.get(source, 0) + 1
                details += f", Sources: {sources}"
            else:
                details += f", Error: {response.text}"
                
            self.log_test("Job Search - All Sources", success, details, response_data)
            return success, response_data
            
        except Exception as e:
            self.log_test("Job Search - All Sources", False, f"Error: {str(e)}")
            return False, None

    def test_job_analysis(self, sample_job=None):
        """Test AI job matching analysis"""
        try:
            # Use a sample job or create one for testing
            if not sample_job:
                sample_job = {
                    "job_title": "Quality Assurance Engineer",
                    "job_description": "We are looking for a QA Engineer with experience in medical device testing, automation, and regulatory compliance.",
                    "company": "MedTech Solutions"
                }
            
            response = requests.post(f"{self.api_url}/jobs/analyze", 
                                   json=sample_job, 
                                   timeout=30)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            response_data = None
            
            if success:
                response_data = response.json()
                match_score = response_data.get('match_score', 0)
                analysis = response_data.get('analysis', '')
                details += f", Match Score: {match_score}%, Analysis: {analysis[:100]}..."
            else:
                details += f", Error: {response.text}"
                
            self.log_test("AI Job Analysis", success, details, response_data)
            return success, response_data
            
        except Exception as e:
            self.log_test("AI Job Analysis", False, f"Error: {str(e)}")
            return False, None

    def test_save_job(self, sample_job=None):
        """Test saving a job"""
        try:
            if not sample_job:
                sample_job = {
                    "id": "test-job-123",
                    "title": "Senior QA Engineer",
                    "company": "TechCorp",
                    "location": "Remote",
                    "description": "Quality assurance role for medical devices",
                    "url": "https://example.com/job",
                    "salary": "$80,000 - $120,000",
                    "tags": ["QA", "Medical", "Remote"],
                    "source": "Test"
                }
            
            response = requests.post(f"{self.api_url}/jobs/save", json=sample_job, timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            response_data = None
            
            if success:
                response_data = response.json()
                details += f", Saved job: {sample_job['title']}"
            else:
                details += f", Error: {response.text}"
                
            self.log_test("Save Job", success, details, response_data)
            return success, response_data
            
        except Exception as e:
            self.log_test("Save Job", False, f"Error: {str(e)}")
            return False, None

    def test_get_saved_jobs(self):
        """Test retrieving saved jobs"""
        try:
            response = requests.get(f"{self.api_url}/jobs/saved", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            response_data = None
            
            if success:
                response_data = response.json()
                job_count = len(response_data)
                details += f", Saved jobs count: {job_count}"
            else:
                details += f", Error: {response.text}"
                
            self.log_test("Get Saved Jobs", success, details, response_data)
            return success, response_data
            
        except Exception as e:
            self.log_test("Get Saved Jobs", False, f"Error: {str(e)}")
            return False, None

    def test_create_application(self, sample_job=None):
        """Test creating a job application"""
        try:
            if not sample_job:
                sample_job = {
                    "id": "app-job-456",
                    "title": "QA Specialist",
                    "company": "HealthTech Inc",
                    "location": "Remote",
                    "description": "Medical device QA position",
                    "url": "https://example.com/job2",
                    "salary": "$70,000 - $100,000",
                    "tags": ["QA", "Healthcare"],
                    "source": "Test"
                }
            
            application_data = {
                "job": sample_job,
                "notes": "Applied through company website"
            }
            
            response = requests.post(f"{self.api_url}/applications", json=application_data, timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            response_data = None
            
            if success:
                response_data = response.json()
                details += f", Application created for: {sample_job['title']}"
            else:
                details += f", Error: {response.text}"
                
            self.log_test("Create Application", success, details, response_data)
            return success, response_data
            
        except Exception as e:
            self.log_test("Create Application", False, f"Error: {str(e)}")
            return False, None

    def test_get_applications(self):
        """Test retrieving applications"""
        try:
            response = requests.get(f"{self.api_url}/applications", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            response_data = None
            
            if success:
                response_data = response.json()
                app_count = len(response_data)
                details += f", Applications count: {app_count}"
                if app_count > 0:
                    statuses = [app.get('status') for app in response_data]
                    details += f", Statuses: {set(statuses)}"
            else:
                details += f", Error: {response.text}"
                
            self.log_test("Get Applications", success, details, response_data)
            return success, response_data
            
        except Exception as e:
            self.log_test("Get Applications", False, f"Error: {str(e)}")
            return False, None

    def test_update_application_status(self, app_id=None):
        """Test updating application status"""
        if not app_id:
            # Get applications first to find an ID
            _, apps = self.test_get_applications()
            if not apps or len(apps) == 0:
                self.log_test("Update Application Status", False, "No applications found to update")
                return False, None
            app_id = apps[0]['id']
        
        try:
            update_data = {
                "status": "Interview",
                "notes": "Scheduled for next week"
            }
            
            response = requests.put(f"{self.api_url}/applications/{app_id}", json=update_data, timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            response_data = None
            
            if success:
                response_data = response.json()
                details += f", Updated application {app_id} to Interview status"
            else:
                details += f", Error: {response.text}"
                
            self.log_test("Update Application Status", success, details, response_data)
            return success, response_data
            
        except Exception as e:
            self.log_test("Update Application Status", False, f"Error: {str(e)}")
            return False, None

    def test_job_search_presets(self):
        """Test quick search presets for Supplier Quality roles"""
        try:
            response = requests.get(f"{self.api_url}/jobs/presets", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            response_data = None
            
            if success:
                response_data = response.json()
                presets = response_data.get('presets', [])
                locations = response_data.get('locations', [])
                
                # Check for Supplier Quality presets
                supplier_presets = [p for p in presets if 'supplier' in p.get('name', '').lower() or 'quality' in p.get('name', '').lower()]
                details += f", Total presets: {len(presets)}, Supplier Quality presets: {len(supplier_presets)}"
                details += f", Locations: {len(locations)}"
                
                # Verify specific presets exist
                preset_names = [p.get('name', '') for p in presets]
                if 'Supplier Quality Manager' in preset_names:
                    details += ", ✓ Supplier Quality Manager preset found"
                if 'Supplier Quality Director' in preset_names:
                    details += ", ✓ Supplier Quality Director preset found"
                    
            else:
                details += f", Error: {response.text}"
                
            self.log_test("Job Search Presets", success, details, response_data)
            return success, response_data
            
        except Exception as e:
            self.log_test("Job Search Presets", False, f"Error: {str(e)}")
            return False, None

    def test_job_search_with_filters(self):
        """Test job search with location and date filters"""
        try:
            # Test with location filter
            response = requests.get(f"{self.api_url}/jobs/search", 
                                  params={"query": "quality", "location": "usa", "days": 7}, 
                                  timeout=20)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            response_data = None
            
            if success:
                response_data = response.json()
                job_count = len(response_data)
                details += f", Jobs found with filters: {job_count}"
                
                # Check if jobs have posted dates
                jobs_with_dates = [j for j in response_data if j.get('posted_at')]
                details += f", Jobs with posted dates: {len(jobs_with_dates)}"
                
            else:
                details += f", Error: {response.text}"
                
            self.log_test("Job Search with Filters", success, details, response_data)
            return success, response_data
            
        except Exception as e:
            self.log_test("Job Search with Filters", False, f"Error: {str(e)}")
            return False, None

    def test_all_job_sources(self):
        """Test all 5 job sources individually"""
        sources = ["remoteok", "remotive", "jobicy", "arbeitnow", "himalayas"]
        all_success = True
        
        for source in sources:
            try:
                response = requests.get(f"{self.api_url}/jobs/search", 
                                      params={"query": "engineer", "source": source}, 
                                      timeout=20)
                success = response.status_code == 200
                details = f"Status: {response.status_code}"
                
                if success:
                    jobs = response.json()
                    job_count = len(jobs)
                    details += f", Jobs found: {job_count}"
                    if job_count > 0:
                        details += f", Sample job: {jobs[0].get('title', 'N/A')}"
                else:
                    details += f", Error: {response.text}"
                    all_success = False
                    
                self.log_test(f"Job Source - {source.title()}", success, details, jobs if success else None)
                
            except Exception as e:
                self.log_test(f"Job Source - {source.title()}", False, f"Error: {str(e)}")
                all_success = False
        
        return all_success

    def test_ai_enhanced_search(self):
        """Test AI-enhanced job search (Deep Search)"""
        try:
            response = requests.post(f"{self.api_url}/jobs/deep-search", 
                                   json={"use_ai": True}, 
                                   timeout=30)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            response_data = None
            
            if success:
                response_data = response.json()
                jobs = response_data.get('jobs', [])
                total_found = response_data.get('total_found', 0)
                search_strategy = response_data.get('search_strategy', {})
                queries_used = response_data.get('queries_used', [])
                
                details += f", AI Deep Search jobs found: {len(jobs)}"
                details += f", Total found: {total_found}"
                if search_strategy:
                    related_titles = search_strategy.get('related_titles', [])
                    keywords = search_strategy.get('keywords', [])
                    details += f", AI strategy - Related titles: {len(related_titles)}, Keywords: {len(keywords)}"
                details += f", Queries used: {len(queries_used)}"
                    
            else:
                details += f", Error: {response.text}"
                
            self.log_test("AI Deep Search", success, details, response_data)
            return success, response_data
            
        except Exception as e:
            self.log_test("AI Deep Search", False, f"Error: {str(e)}")
            return False, None

    def test_email_alert_system(self):
        """Test email alert system"""
        try:
            # Test sending alert to the specified recipient
            alert_data = {"email": "cmuchina@outlook.com"}
            
            response = requests.post(f"{self.api_url}/alerts/send-now", 
                                   json=alert_data, 
                                   timeout=30)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            response_data = None
            
            if success:
                response_data = response.json()
                message = response_data.get('message', '')
                jobs_count = response_data.get('jobs_count', 0)
                details += f", {message}, Jobs sent: {jobs_count}"
            else:
                details += f", Error: {response.text}"
                
            self.log_test("Email Alert System", success, details, response_data)
            return success, response_data
            
        except Exception as e:
            self.log_test("Email Alert System", False, f"Error: {str(e)}")
            return False, None

    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🚀 Starting MedMatch API Test Suite - New Features Testing")
        print("=" * 60)
        
        # Test basic connectivity
        if not self.test_api_health():
            print("❌ API is not accessible. Stopping tests.")
            return False
        
        # Test resume functionality
        print("\n📄 Testing Resume Features...")
        resume_uploaded, resume_data = self.test_resume_upload()
        self.test_resume_retrieval()
        
        # Test NEW FEATURE: Quick search presets
        print("\n🎯 Testing NEW FEATURE: Quick Search Presets...")
        self.test_job_search_presets()
        
        # Test NEW FEATURE: All 5 job sources
        print("\n🌐 Testing NEW FEATURE: All Job Sources (5 APIs)...")
        self.test_all_job_sources()
        
        # Test NEW FEATURE: Job search with filters
        print("\n🔍 Testing NEW FEATURE: Job Search with Filters...")
        self.test_job_search_with_filters()
        _, all_jobs = self.test_job_search_all_sources()
        
        # Test NEW FEATURE: AI deep search
        print("\n🤖 Testing NEW FEATURE: AI Deep Search...")
        self.test_ai_enhanced_search()
        
        # Test AI analysis (only if resume was uploaded)
        print("\n🧠 Testing AI Job Analysis...")
        if resume_uploaded:
            sample_job = None
            if all_jobs and len(all_jobs) > 0:
                # Use a real job from search results
                sample_job = {
                    "job_title": all_jobs[0]['title'],
                    "job_description": all_jobs[0]['description'],
                    "company": all_jobs[0]['company']
                }
            self.test_job_analysis(sample_job)
        else:
            self.log_test("AI Job Analysis", False, "Skipped - no resume uploaded")
        
        # Test saved jobs functionality
        print("\n💾 Testing Saved Jobs Features...")
        sample_job = None
        if all_jobs and len(all_jobs) > 0:
            sample_job = all_jobs[0]
        _, saved_job = self.test_save_job(sample_job)
        self.test_get_saved_jobs()
        
        # Test applications functionality
        print("\n📋 Testing Applications Features...")
        _, app_data = self.test_create_application(sample_job)
        _, apps = self.test_get_applications()
        if apps and len(apps) > 0:
            self.test_update_application_status(apps[0]['id'])
        
        # Test NEW FEATURE: Email alert system
        print("\n📧 Testing NEW FEATURE: Email Alert System...")
        self.test_email_alert_system()
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
            return False

def main():
    """Main test execution"""
    tester = MedMatchAPITester()
    success = tester.run_all_tests()
    
    # Save detailed results
    results = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": tester.tests_run,
        "passed_tests": tester.tests_passed,
        "success_rate": (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0,
        "test_details": tester.test_results
    }
    
    with open('/app/backend_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n📁 Detailed results saved to: /app/backend_test_results.json")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())