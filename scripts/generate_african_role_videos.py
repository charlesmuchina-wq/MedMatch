#!/usr/bin/env python3
"""
Generate African Language Tutorial Videos with Regional Diversity
Plus Role-Specific Tutorials (Job Seeker, Recruiter, Admin)
"""
import os
import httpx
import asyncio
import json
from pathlib import Path

D_ID_API_KEY = os.environ.get("D_ID_API_KEY", "")
D_ID_BASE_URL = "https://api.d-id.com"
VIDEOS_DIR = Path("/app/backend/static/videos/tutorials")

def get_headers():
    return {
        "Authorization": f"Basic {D_ID_API_KEY}",
        "Content-Type": "application/json"
    }

# African Language Videos with Diverse Presenters
AFRICAN_VIDEOS = {
    "sw": {
        "name": "Swahili",
        "voice_id": "sw-KE-ZuriNeural",  # Female Kenyan voice
        "presenter_id": "v2_public_diana@tftp6k9s9u",  # Diana - diverse female
        "gender": "female",
        "script": "Karibu MedMatch! Niruhusu nikuonyeshe jinsi ya kuanza. Pakia CV yako na AI yetu itapata kazi zinazolingana kutoka tovuti zaidi ya 15 za kazi maalum. Pata alama za kuaminika kwa kila nafasi, jiandae kwa mahojiano na mafunzo ya AI, na upate arifa za kazi karibu nawe. Inapatikana kwenye Wavuti, iOS, Android na kompyuta. MedMatch - Uajiri wa busara. Anza leo!"
    },
    "af": {
        "name": "Afrikaans",
        "voice_id": "af-ZA-WillemNeural",  # Male South African voice
        "presenter_id": "v2_public_Matt_NoHands_GreyTshirt_Outdoor@rwE9avfhZE",  # Matt - male
        "gender": "male",
        "script": "Welkom by MedMatch! Laat my jou wys hoe om te begin. Laai jou CV op en ons KI sal ooreenstemmende werk vind van meer as 15 gespesialiseerde werkwebwerwe. Kry vertroue-tellings vir elke pos, berei voor vir onderhoude met KI-afrigting, en ontvang kennisgewings vir werk naby jou. Beskikbaar op Web, iOS, Android en rekenaar. MedMatch - Slim werwing. Begin vandag!"
    },
    "ha": {
        "name": "Hausa",
        "voice_id": "en-NG-AbeoNeural",  # Nigerian English male voice (closest)
        "presenter_id": "v2_public_eugene_black_shirt_lobby@CthhIOV7vW",  # Eugene - male
        "gender": "male",
        "script": "Barka da zuwa MedMatch! Bari in nuna muku yadda za ku fara. Sanya CV dinku kuma AI dinmu za ta samo ayyukan da suka dace daga fiye da shafukan ayyuka na musamman 15. Sami maki amincewa ga kowane matsayi, shirya don tambayoyi tare da horar da AI, kuma ku sami sanarwa game da ayyuka kusa da ku. Akwai akan Yanar Gizo, iOS, Android da kwamfuta. MedMatch - Daukar ma'aikata mai wayo. Fara yau!"
    },
    "yo": {
        "name": "Yoruba",
        "voice_id": "en-NG-EzinneNeural",  # Nigerian English female voice
        "presenter_id": "v2_public_Anita_Pink_Shirt Classroom@w0TKk10XrO",  # Anita - female
        "gender": "female",
        "script": "Kaabo si MedMatch! Jẹ ki n fi ọ han bi o ṣe le bẹrẹ. Gbe CV rẹ soke ati AI wa yoo wa awọn iṣẹ ti o baamu lati awọn aaye iṣẹ pataki ju 15 lọ. Gba awọn ikun igbẹkẹle fun gbogbo ipo, mura silẹ fun awọn ifọrọwanilẹnuwo pẹlu ikẹkọ AI, ki o si gba awọn akiyesi fun awọn iṣẹ ti o sunmọ ọ. O wa lori Wẹẹbu, iOS, Android ati kọmputa. MedMatch - Gbigba oṣiṣẹ ọlọgbọn. Bẹrẹ loni!"
    },
    "zu": {
        "name": "Zulu",
        "voice_id": "zu-ZA-ThandoNeural",  # Female Zulu voice
        "presenter_id": "v2_public_Kayla_NoHands_BlackShirt_CoffeeShop@u1un3hTUDJ",  # Kayla - female
        "gender": "female",
        "script": "Siyakwamukela ku-MedMatch! Ake ngikukhombise ukuthi uqala kanjani. Layisha i-CV yakho futhi i-AI yethu izothola imisebenzi efanayo kusuka kumawebhusayithi emisebenzi ekhethekile angaphezu kuka-15. Thola amaphuzu okwethemba esikhundleni ngasinye, lungela izingxoxo ngokuqeqeshwa kwe-AI, futhi uthola izaziso zemisebenzi eduze nawe. Iyatholakala ku-Web, iOS, Android nekhompuyutha. MedMatch - Ukuqasha okuhlakaniphile. Qala namuhla!"
    },
    "xh": {
        "name": "Xhosa",
        "voice_id": "en-ZA-LeahNeural",  # South African English female
        "presenter_id": "v2_public_Lily_NoHands_RedShirt_Office@JDOtgQlb_L",  # Lily - female
        "gender": "female",
        "script": "Wamkelekile ku-MedMatch! Makhe ndikubonise ukuba uqala njani. Layisha i-CV yakho kwaye i-AI yethu iya kufumana imisebenzi ehambelanayo kwiiwebhusayithi zemisebenzi ezikhethekileyo ezingaphezu kwe-15. Fumana amanqaku okuthembeka kwisikhundla ngasinye, lungisa udliwanondlebe ngokuqeqesha nge-AI, kwaye ufumane izaziso zemisebenzi ekufutshane nawe. Iyafumaneka kwiWebhu, iOS, Android nekhompyutha. MedMatch - Ukuqesha okuchubekileyo. Qala namhlanje!"
    }
}

# Role-Specific Tutorial Videos
ROLE_TUTORIALS = {
    "jobseeker": {
        "name": "Job Seeker Guide",
        "voice_id": "en-US-JennyNeural",
        "presenter_id": "v2_public_Sophia@CtvJYUo9MA",  # Sophia - female
        "gender": "female",
        "script": "Welcome, Job Seeker! Here's your guide to MedMatch. Upload your resume and our AI instantly parses your skills. Search 15+ job boards at once - no more ghost jobs. Get a Trust Score for every match showing your chances. Prepare for interviews with our AI coach. Set alerts for jobs near you. Track all your applications in one place. Available on web, mobile, and desktop. MedMatch - Your AI career partner. Start your job search today!"
    },
    "recruiter": {
        "name": "Recruiter Guide",
        "voice_id": "en-US-GuyNeural",
        "presenter_id": "v2_public_benjamin@vxbdlxieyn",  # Benjamin - male professional
        "gender": "male",
        "script": "Welcome, Recruiter! Here's your guide to MedMatch. Post jobs and reach qualified candidates instantly. Track applicants through 11 status stages in our ATS. Use blind screening to eliminate bias. Generate shareable application links. Send automated notifications to candidates. Monitor AI compliance with EU AI Act built-in. Every decision is logged and auditable. Enterprise-ready with GDPR compliance. MedMatch - Intelligent hiring. Transform your recruitment today!"
    },
    "admin": {
        "name": "Admin Guide",
        "voice_id": "en-GB-SoniaNeural",
        "presenter_id": "v2_public_Fiona_Blue_Shirt Lab@FQBA_hemBB",  # Fiona - professional female
        "gender": "female",
        "script": "Welcome, Administrator! Here's your guide to MedMatch admin features. Manage all users across your organization. Monitor system health and performance. Configure AI settings and compliance rules. Access comprehensive audit logs. Manage translation QA and localization. Control privacy settings and data retention. Set up enterprise SSO if needed. View analytics and usage reports. MedMatch Admin - Complete control over your talent platform. Get started now!"
    }
}

async def create_video(config, filename_prefix):
    """Create a video with D-ID API."""
    print(f"Creating {config['name']}...", end=" ")
    
    payload = {
        "presenter_id": config["presenter_id"],
        "script": {
            "type": "text",
            "input": config["script"],
            "provider": {
                "type": "microsoft",
                "voice_id": config["voice_id"]
            }
        },
        "config": {
            "fluent": True,
            "pad_audio": 0.5,
            "stitch": True
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{D_ID_BASE_URL}/clips",
            headers=get_headers(),
            json=payload,
            timeout=60.0
        )
        
        if response.status_code == 201:
            data = response.json()
            talk_id = data.get("id")
            print(f"✅ Created: {talk_id}")
            return {"name": config["name"], "talk_id": talk_id, "gender": config["gender"], "filename": filename_prefix}
        else:
            print(f"❌ Error: {response.status_code}")
            return {"name": config["name"], "error": response.text[:100], "filename": filename_prefix}

async def main():
    print("=" * 60)
    print("Generating African Language & Role-Specific Tutorial Videos")
    print("=" * 60)
    
    results = []
    
    # Generate African language videos
    print("\n--- African Languages ---")
    for lang_code, config in AFRICAN_VIDEOS.items():
        result = await create_video(config, f"tutorial_{lang_code}")
        result["lang_code"] = lang_code
        results.append(result)
        await asyncio.sleep(2)
    
    # Generate role-specific videos
    print("\n--- Role-Specific Tutorials ---")
    for role, config in ROLE_TUTORIALS.items():
        result = await create_video(config, f"role_{role}")
        result["role"] = role
        results.append(result)
        await asyncio.sleep(2)
    
    # Summary
    print("\n" + "=" * 60)
    created = [r for r in results if "talk_id" in r]
    failed = [r for r in results if "error" in r]
    print(f"Created: {len(created)}, Failed: {len(failed)}")
    
    # Save results
    with open("/tmp/african_role_videos.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("Results saved to /tmp/african_role_videos.json")
    return results

if __name__ == "__main__":
    asyncio.run(main())
