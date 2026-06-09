# app.py
import streamlit as st
import google.generativeai as genai
import re
from agents import (
    JD_AGENT_SYSTEM_INSTRUCTION, 
    TECH_LEAD_SYSTEM_INSTRUCTION, 
    HR_CULTURE_SYSTEM_INSTRUCTION, 
    AUDITOR_AGENT_SYSTEM_INSTRUCTION,
    CHAT_AGENT_SYSTEM_INSTRUCTION
)

def extract_text_from_uploaded_file(uploaded_file):
    """Extracts text content from an uploaded binary PDF document."""
    try:
        import pypdf
        reader = pypdf.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        st.error(f"Error reading {uploaded_file.name}: {e}")
        return ""

def parse_score_from_output(text):
    """Parses out the structural score integer from the Auditor's JSON tracking payload."""
    try:
        match = re.search(r'\{"final_score":\s*(\d+)\}', text)
        if match:
            return int(match.group(1))
        pct_match = re.search(r'(\d+)%', text)
        if pct_match:
            return int(pct_match.group(1))
    except Exception:
        pass
    return 0

st.set_page_config(page_title="AI based Resume Screener and ranking system", layout="wide")

st.title("🔄 AI based Resume Screener and ranking system")
st.caption("Features a self-correcting graph topology where an Auditor can reject, critique, and iterate evaluations dynamically.")

# Persistent data structures initialized into global memory space
if "talent_pool" not in st.session_state:
    st.session_state["talent_pool"] = []
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Sidebar Configuration Control Room
st.sidebar.header("Setup & Inputs")
gemini_api_key = st.sidebar.text_input("Enter your Gemini API Key", type="password")

# Dual Options for entering the target benchmark Job Description
jd_input = st.sidebar.text_area("Option A: Paste Job Description Here", height=150)
jd_file = st.sidebar.file_uploader("Option B: Or Upload Job Description PDF", type=["pdf"])

uploaded_files = st.sidebar.file_uploader("Upload Resumes (Select Multiple PDFs)", type=["pdf"], accept_multiple_files=True)

if st.sidebar.button("Run Assessment"):
    # Determine configuration payload context source dynamically
    final_jd_text = ""
    if jd_file is not None:
        final_jd_text = extract_text_from_uploaded_file(jd_file)
    elif jd_input.strip():
        final_jd_text = jd_input

    if not gemini_api_key or not final_jd_text or not uploaded_files:
        st.error("Please ensure the API Key, Job Description (Text or PDF), and at least one Resume are provided.")
    else:
        try:
            # Clean alignment spacing setup for the underlying model configurations
            genai.configure(api_key=gemini_api_key)
            
            # --- STEP 1: Job Description Analyst ---
            with st.status("Agent 1: Extracting Target Job Profile...", expanded=True) as status:
                jd_model = genai.GenerativeModel(model_name="gemini-3.1-flash-lite", system_instruction=JD_AGENT_SYSTEM_INSTRUCTION)
                jd_agent_response = jd_model.generate_content(f"Analyze this job description:\n\n{final_jd_text}")
                extracted_jd_criteria = jd_agent_response.text
                status.update(label=" Job DNA Extracted!", state="complete")
            
            with st.expander("🔍 View Extracted Target Job Profile Structure"):
                st.markdown(extracted_jd_criteria)

            # Flush current cache maps to prepare memory slots for a fresh calculation cycle run
            st.session_state["talent_pool"] = []
            st.session_state["chat_history"] = []
            
            st.subheader("⏳ Evaluating Data...")
            
            # --- CORE CYCLIC LOOP MATRIX PER RESUME ---
            for index, file in enumerate(uploaded_files):
                resume_text = extract_text_from_uploaded_file(file)
                if not resume_text.strip():
                    continue
                
                # Internal execution loop graph tracking conditions
                is_approved = False
                loop_count = 0
                max_loops = 3  # Protect infrastructure ceiling threshold limits
                last_critique = "None. This is the initial valuation run."
                
                tech_evaluation = ""
                hr_evaluation = ""
                audited_output = ""
                
                with st.status(f"Evaluating {file.name}...", expanded=False) as status:
                    
                    while not is_approved and loop_count < max_loops:
                        loop_count += 1
                        status.update(label=f"🔄 Processing {file.name} - Loop Iteration #{loop_count}...")
                        
                        # Pipeline Invocation: Technical Specialist Persona Agent
                        tech_model = genai.GenerativeModel(model_name="gemini-3.1-flash-lite", system_instruction=TECH_LEAD_SYSTEM_INSTRUCTION)
                        tech_prompt = f"Job Criteria:\n{extracted_jd_criteria}\n\nResume:\n{resume_text}\n\nPrior Auditor Feedback/Critique:\n{last_critique}\n\nPrevious Tech Log:\n{tech_evaluation}"
                        tech_evaluation = tech_model.generate_content(tech_prompt).text
                        
                        # Pipeline Invocation: HR/Culture Persona Agent
                        hr_model = genai.GenerativeModel(model_name="gemini-3.1-flash-lite", system_instruction=HR_CULTURE_SYSTEM_INSTRUCTION)
                        hr_prompt = f"Job Criteria:\n{extracted_jd_criteria}\n\nResume:\n{resume_text}\n\nPrior Auditor Feedback/Critique:\n{last_critique}\n\nPrevious HR Log:\n{hr_evaluation}"
                        hr_evaluation = hr_model.generate_content(hr_prompt).text
                        
                        # Graph Layer Routing Check: Reconciling Auditor Agent
                        auditor_model = genai.GenerativeModel(model_name="gemini-3.1-flash-lite", system_instruction=AUDITOR_AGENT_SYSTEM_INSTRUCTION)
                        audit_prompt = f"--- RAW RESUME ---\n{resume_text}\n\n--- CURRENT TECH LOG ---\n{tech_evaluation}\n\n--- CURRENT HR LOG ---\n{hr_evaluation}"
                        audited_output = auditor_model.generate_content(audit_prompt).text
                        
                        # Inspect verification flags inside edge loop pathways
                        if "STATUS: REJECTED" in audited_output:
                            critique_match = re.search(r"CRITIQUE:(.*?)$", audited_output, re.DOTALL | re.IGNORECASE)
                            last_critique = critique_match.group(1).strip() if critique_match else audited_output
                            st.toast(f"⚠️ Audit Rejected {file.name} on loop {loop_count}. Self-correcting...", icon="🔄")
                        else:
                            is_approved = True
                    
                    final_score = parse_score_from_output(audited_output)
                    
                    # Clean out operational token headers before pushing structural strings to memory registers
                    cleaned_report = audited_output.replace("STATUS: APPROVED", "").replace("FINAL REPORT:", "")
                    cleaned_report = re.sub(r"2\.\s+METADATA:.*?(```json.*?```)?$", "", cleaned_report, flags=re.DOTALL | re.IGNORECASE)
                    cleaned_report = re.sub(r"```json.*?```$", "", cleaned_report, flags=re.DOTALL).strip()
                    
                    # Append completed profile properties directly into persistent cache space
                    st.session_state["talent_pool"].append({
                        "filename": file.name,
                        "score": final_score,
                        "clean_report": cleaned_report,
                        "tech_log": tech_evaluation,
                        "hr_log": hr_evaluation,
                        "raw_resume_text": resume_text,
                        "loops_taken": loop_count
                    })
                    
                    status.update(label=f"✅ {file.name} Finalized on iteration {loop_count} (Score: {final_score}%)", state="complete")
                    
        except Exception as e:
            st.error(f"An infrastructure error occurred: {e}")

# --- STEP 4: DISPLAY DASHBOARD & RENDERING ---
if st.session_state["talent_pool"]:
    pool = st.session_state["talent_pool"]
    pool.sort(key=lambda x: x['score'], reverse=True)
    
    st.success("🎉 Evaluation Complete! Standings rendered below.")
    st.header("🏆 Final Candidate Standings")
    
    # Render crisp clean score blocks without any trailing red lines/arrows underneath
    cols = st.columns(min(len(pool), 4))
    for idx, candidate in enumerate(pool[:4]):
        with cols[idx]:
            st.metric(
                label=f"#{idx+1} {candidate['filename']}", 
                value=f"{candidate['score']}%"
            )
            
    st.write("---")
    st.subheader("📄 Deep Analysis Candidate Records")
    for idx, candidate in enumerate(pool):
        with st.expander(f"Rank #{idx+1}: {candidate['filename']} — [Score: {candidate['score']}%] [Loops: {candidate['loops_taken']}]"):
            tab_audited, tab_tech, tab_hr = st.tabs(["🛡️ Verified Report", "💻 Tech Lead Transcript", "👔 HR Director Transcript"])
            with tab_audited:
                st.markdown(candidate['clean_report'])
            with tab_tech:
                st.markdown(candidate['tech_log'])
            with tab_hr:
                st.markdown(candidate['hr_log'])
                
    # --- OPTION 5 FEATURE LAYER: INTERACTIVE CHAT POOL REPOSITORY ---
    st.write("---")
    st.header("💬 Interactive Query Assistant")
    for chat in st.session_state["chat_history"]:
        with st.chat_message(chat["role"]):
            st.markdown(chat["content"])

    if user_query := st.chat_input("Query your Candidates..."):
        with st.chat_message("user"):
            st.markdown(user_query)
        st.session_state["chat_history"].append({"role": "user", "content": user_query})
        
        db_context_string = ""
        for candidate in pool:
            db_context_string += f"\nFILE: {candidate['filename']} | SCORE: {candidate['score']}%\nREPORT:\n{candidate['clean_report']}\n"
            
        with st.spinner("Analyzing..."):
            try:
                chat_agent_model = genai.GenerativeModel(model_name="gemini-3.1-flash-lite", system_instruction=CHAT_AGENT_SYSTEM_INSTRUCTION)
                agent_response = chat_agent_model.generate_content(f"Database Context:\n{db_context_string}\n\nQuery: {user_query}").text
                with st.chat_message("assistant"):
                    st.markdown(agent_response)
                st.session_state["chat_history"].append({"role": "assistant", "content": agent_response})
            except Exception as e:
                st.error(f"Chat error: {e}")
else:
    st.info("Upload inputs and click 'Run Assessment' to activate your AI-powered resume screening and ranking system!")