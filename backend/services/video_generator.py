"""
Video Generator Service using Sora 2
Generates instructional videos for MedMatch app navigation
"""
import os
import asyncio
from dotenv import load_dotenv
from emergentintegrations.llm.openai.video_generation import OpenAIVideoGeneration

load_dotenv()

def generate_video(prompt: str, output_path: str, duration: int = 4) -> str:
    """Generate a video using Sora 2"""
    try:
        video_gen = OpenAIVideoGeneration(api_key=os.environ['EMERGENT_LLM_KEY'])
        
        video_bytes = video_gen.text_to_video(
            prompt=prompt,
            model="sora-2",
            size="1280x720",
            duration=duration,
            max_wait_time=600
        )
        
        if video_bytes:
            video_gen.save_video(video_bytes, output_path)
            return output_path
        return None
    except Exception as e:
        print(f"Error generating video: {e}")
        return None


# Job Seeker Video Prompts
JOB_SEEKER_PROMPTS = {
    "intro": """A professional, modern animated explainer video showing a job seeker using a laptop to access MedMatch, 
    a life sciences job platform. The scene shows a clean, teal-colored interface with the MedMatch logo. 
    The user smoothly navigates through a dashboard showing job matches, trust scores, and quick action buttons.
    Modern UI design with smooth transitions. Professional healthcare/biotech aesthetic.""",
    
    "job_search": """An animated tutorial showing a job seeker searching for jobs on MedMatch platform. 
    The user types in a search bar, filters appear showing location, job type, and salary options.
    Job listings appear with match percentage indicators (50%, 75%, 90%). 
    The user clicks on a job card to see details. Clean, modern UI with teal accents.""",
    
    "application": """A smooth animation showing a job application process on a modern job platform.
    A professional fills out an application form with name, email, phone, and resume upload fields.
    The form has a clean white background with teal accent colors.
    A success confirmation appears after submission with a tracking ID."""
}

# Recruiter Video Prompts  
RECRUITER_PROMPTS = {
    "dashboard": """An animated explainer showing a recruiter's dashboard on MedMatch platform.
    The dashboard displays key metrics: total applications, active job postings, pending interviews.
    The recruiter navigates through a sidebar menu showing job postings, applicant tracking, and candidate search.
    Professional corporate aesthetic with teal and white color scheme.""",
    
    "ats": """A tutorial animation showing an Applicant Tracking System (ATS) interface.
    The recruiter creates shareable application links, views application statistics,
    and updates candidate statuses through different stages: Received, Reviewing, Interview, Offered.
    Clean UI with status badges and progress indicators.""",
    
    "candidate_review": """An animated sequence showing a recruiter reviewing job applications.
    The interface shows candidate profiles with resumes, skills, and match scores.
    The recruiter clicks to schedule interviews, send messages, and update application statuses.
    Professional recruitment platform aesthetic with smooth transitions."""
}


if __name__ == "__main__":
    # Test video generation
    print("Testing Sora 2 Video Generation...")
    result = generate_video(
        JOB_SEEKER_PROMPTS["intro"],
        "/app/videos/jobseeker_intro.mp4",
        duration=4
    )
    print(f"Result: {result}")
