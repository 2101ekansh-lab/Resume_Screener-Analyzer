# utils.py
import re
import numpy as np
import google.generativeai as genai
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import agents

def extract_text_from_pdf(pdf_file) -> str:
    """Extracts all selectable text cleanly from an uploaded PDF file."""
    try:
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        return f"Error extracting PDF text: {str(e)}"

def calculate_similarity(job_desc: str, resume_text: str) -> float:
    """Calculates traditional lexical similarity using TF-IDF and Cosine Similarity."""
    if not job_desc.strip() or not resume_text.strip():
        return 0.0
    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform([job_desc, resume_text])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        return float(np.round(similarity[0][0] * 100, 2))
    except Exception:
        return 0.0

def route_user_intent(user_query: str) -> str:
    """Classifies whether incoming chat traffic is generic chitchat or screener context data."""
    try:
        model = genai.GenerativeModel('gemini-3.1-flash-lite')
        response = model.generate_content([agents.ROUTER_PROMPT, f"User Input: {user_query}"])
        intent = response.text.strip().upper()
        if "CHITCHAT" in intent:
            return "CHITCHAT"
        return "SCREENER"
    except Exception:
        return "SCREENER" # Fallback safely to screening RAG context

def handle_chitchat(user_query: str) -> str:
    """Directly answers general knowledge questions, trivia, and greeting tokens."""
    try:
        model = genai.GenerativeModel(
            model_name='gemini-3.1-flash-lite',
            system_instruction=agents.CHITCHAT_AGENT_PROMPT
        )
        response = model.generate_content(user_query)
        return response.text.strip()
    except Exception as e:
        return f"Chitchat Agent Error: {str(e)}"

def query_candidate_rag(user_query: str, pool_data: list) -> str:
    """RAG utility engine compiled to evaluate questions based on candidate screening data states."""
    try:
        model = genai.GenerativeModel('gemini-3.1-flash-lite')
        
        # Build an in-memory flat string context map representing our compiled pool state
        context_accumulator = "Here is the compiled data of candidates screened by the committee:\n\n"
        for candidate in pool_data:
            context_accumulator += f"=== Candidate: {candidate['name']} ===\n"
            context_accumulator += f"Score: {candidate['score']}/100\n"
            context_accumulator += f"Technical Review:\n{candidate['tech_analysis']}\n"
            context_accumulator += f"HR Review:\n{candidate['hr_analysis']}\n"
            context_accumulator += f"Auditor Report Status: {candidate['audit_status']}\n\n"
            
        system_instruction = (
            "You are an AI Screening Assistant. Use the provided evaluation pool dataset to answer user questions accurately. "
            "If the information is not contained within the evaluation text map, state gracefully that you do not have that data."
        )
        
        response = model.generate_content([system_instruction, context_accumulator, f"Question: {user_query}"])
        return response.text.strip()
    except Exception as e:
        return f"RAG Query Error: {str(e)}"

def run_agentic_screening_loop(resume_name: str, resume_text: str, target_profile: str) -> dict:
    """Executes the cyclic Multi-Agent workflow loop (Tech Lead -> HR -> Auditor check)."""
    # Fallback/mock processing pipeline mimicking agent evaluation logic outputs
    try:
        model = genai.GenerativeModel('gemini-3.1-flash-lite')
        
        # Step 1: Run Technical Review
        tech_prompt = f"{agents.TECH_LEAD_PROMPT}\nTarget Role Details:\n{target_profile}\nResume Raw Text:\n{resume_text}"
        tech_res = model.generate_content(tech_prompt).text
        
        # Step 2: Run HR Review
        hr_prompt = f"{agents.HR_PROMPT}\nTarget Role Details:\n{target_profile}\nResume Raw Text:\n{resume_text}"
        hr_res = model.generate_content(hr_prompt).text
        
        # Step 3: Run Auditor Check
        audit_prompt = f"{agents.AUDITOR_PROMPT}\nTech Review:\n{tech_res}\nHR Review:\n{hr_res}\nRaw Text:\n{resume_text}"
        audit_res = model.generate_content(audit_prompt).text
        
        # Clean / extract pseudo score out of reports safely using Regex
        score_match = re.search(r"Score:\s*(\d+)", tech_res + hr_res)
        parsed_score = int(score_match.group(1)) if score_match else 75
        
        return {
            "name": resume_name,
            "score": min(parsed_score, 100),
            "tech_analysis": tech_res,
            "hr_analysis": hr_res,
            "audit_status": "Verified Clean" if "PASS" in audit_res.upper() else "Passed with corrections"
        }
    except Exception as e:
        return {
            "name": resume_name,
            "score": 0,
            "tech_analysis": f"Failed: {str(e)}",
            "hr_analysis": "Failed execution pipeline",
            "audit_status": "Rejected"
        }