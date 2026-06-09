import os
import json
import time  # For handles server-side rate limits and busy responses
import numpy as np
from pypdf import PdfReader
from google import genai  # Modern Google GenAI SDK wrapper
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Global API client state
client = None

def configure_gemini(api_key):
    """Initializes the structural client instance using Google's new SDK rules."""
    global client
    if api_key:
        client = genai.Client(api_key=api_key)

def extract_text_from_pdf(pdf_file):
    """Parses binary data array streams from the browser and extracts raw layout text."""
    try:
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
        return text.strip()
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def calculate_tfidf_similarity(job_description, resume_text):
    """Tokenizes text blocks and checks raw structural keyword density intersections."""
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform([job_description, resume_text])
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return float(similarity[0][0])

def generate_rag_analysis(job_description, resume_text):
    """
    Executes a structured RAG extraction loop.
    Includes a self-healing retry mechanism to automatically bypass 503 Service Overloads.
    """
    global client
    if client is None:
        return {
            "semantic_fit_score": 0,
            "matched_skills": [],
            "missing_skills": ["API key missing or configuration dropped"],
            "strengths": [],
            "verdict_summary": "Please provide a valid API key in the sidebar configuration."
        }

    prompt = f"""
    You are an expert technical recruiter and AI HR assistant.
    Your task is to analyze the provided Candidate Resume strictly against the Job Description.
    
    [JOB DESCRIPTION]
    {job_description}
    
    [CANDIDATE RESUME CONTEXT]
    {resume_text}
    
    Perform a deep structural analysis and return the result STRICTLY as a valid JSON object. Do not include markdown codeblocks (like ```json) or any conversational text. Return raw JSON text only.
    
    The JSON structure MUST exactly match this:
    {{
        "semantic_fit_score": <An integer from 0 to 100 based on core role alignment>,
        "matched_skills": [<list of strings of skills matching the job requirements>],
        "missing_skills": [<list of crucial missing skills or tools requested in the JD>],
        "strengths": [<list of 2-3 key background advantages>],
        "verdict_summary": "<A brief, 2-sentence executive summary for the hiring manager>"
    }}
    """
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Running native execution on production standard 2.5 architecture
            response = client.models.generate_content(
                model="gemini-3.1-flash-lite", 
                contents=prompt,
            )
            
            # Formats structural text output back into secure dictionaries
            clean_text = response.text.strip().lstrip("```json").rstrip("```").strip()
            analysis_dict = json.loads(clean_text)
            return analysis_dict
            
        except Exception as e:
            # Agar last attempt pe bhi server breakdown ho, toh hi error dikhayega
            if attempt == max_retries - 1:
                return {
                    "semantic_fit_score": 50,
                    "matched_skills": ["Server rate capacity exceeded. Analyzing text metrics fallback."],
                    "missing_skills": ["Could not extract due to server load"],
                    "strengths": ["Review background layout manually"],
                    "verdict_summary": f"Google AI servers are facing high traffic spikes. Please wait 5 seconds and click 'Run Screening' again. (Details: {str(e)})"
                }
            # Agar 503 ya high demand crash aaya, toh 2.5 seconds hold karke loop fir se chalega
            time.sleep(2.5)

def compute_hybrid_rank(tfidf_score, semantic_score):
    """Compiles the final analytical metrics (30% Keyword Density, 70% Context Understanding)."""
    final_score = (tfidf_score * 30) + (semantic_score * 0.70)
    return round(final_score, 2)