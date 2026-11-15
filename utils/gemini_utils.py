"""
Gemini API helper functions.
Handles requests for AI skill extraction, candidate summaries, and RAG chats.
"""
import requests
import json

def call_gemini_api(api_key: str, system_instruction: str = None, prompt: str = None, conversation_history: list = None, json_mode: bool = False) -> str:
    """
    Call the Google Gemini API directly using requests.
    Supports single prompt OR full conversation history payload for multi-turn conversation with memory.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    contents = []

    if conversation_history:
        for message in conversation_history:
            role = "user" if message["role"] == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": message["content"]}]
            })
        if prompt:
            contents.append({
                "role": "user",
                "parts": [{"text": prompt}]
            })
    else:
        text_content = prompt if prompt else ""
        if system_instruction:
            text_content = f"{system_instruction}\n\n{text_content}"
        contents = [{
            "role": "user",
            "parts": [{"text": text_content}]
        }]

    payload = {
        "contents": contents
    }

    if system_instruction and not conversation_history:
        payload["systemInstruction"] = {
            "parts": [{"text": system_instruction}]
        }

    if json_mode:
        payload["generationConfig"] = {
            "responseMimeType": "application/json"
        }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            try:
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return text
            except (KeyError, IndexError):
                return ""
        else:
            print(f"⚠️ Gemini API returned status code {response.status_code}: {response.text}")
            return ""
    except Exception as e:
        print(f"❌ Gemini API request error: {str(e)}")
        return ""

def extract_skills_from_jd_with_ai(api_key: str, jd_text: str) -> list:
    """Uses Gemini API to dynamically extract required skills from Job Description."""
    prompt = f"""
You are an expert technical recruiter and skill taxonomist. Extract ALL required technical skills, tools, frameworks, programming languages, and soft skills from the following Job Description.

Return ONLY a JSON array of skill strings (e.g., ["Python", "React", "Docker", "Communication"]).
Do not include explanations, just the array.

Job Description:
{jd_text[:4000]}
"""
    result_text = call_gemini_api(api_key, prompt=prompt, json_mode=True)
    if not result_text.strip():
        return []
    try:
        cleaned_text = result_text.strip()
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:]
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]
        parsed = json.loads(cleaned_text.strip())
        if isinstance(parsed, list):
            return [str(s).strip() for s in parsed if s]
        return []
    except Exception:
        return []

def get_candidate_llm_analysis(api_key: str, resume_text: str, jd_text: str) -> dict:
    """Extract candidate executive summary of fit, strengths, gaps, and interview questions using Gemini."""
    prompt = f"""
You are an expert technical recruiter. Analyze the following candidate resume text against the job description.
Identify the candidate's executive summary of fit, top 3 strengths relative to the job, top 2 missing gaps or weaknesses, and 3 targeted technical or behavioral interview questions to probe their experience.

Return a JSON object matching this schema exactly:
{{
  "executive_summary": "2-3 sentences summarizing their fit",
  "strengths": ["strength 1", "strength 2", "strength 3"],
  "gaps": ["gap 1", "gap 2"],
  "interview_questions": ["question 1", "question 2", "question 3"]
}}

Job Description:
{jd_text[:3000]}

Candidate Resume:
{resume_text[:4000]}
"""
    result_text = call_gemini_api(api_key, prompt=prompt, json_mode=True)
    default_res = {
        "executive_summary": "Could not generate AI summary.",
        "strengths": ["N/A", "N/A", "N/A"],
        "gaps": ["N/A", "N/A"],
        "interview_questions": ["N/A", "N/A", "N/A"]
    }
    if not result_text.strip():
        return default_res
    try:
        cleaned_text = result_text.strip()
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:]
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]
        parsed = json.loads(cleaned_text.strip())
        for k in default_res:
            if k not in parsed:
                parsed[k] = default_res[k]
        return parsed
    except Exception:
        return default_res
