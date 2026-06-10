# app.py
import streamlit as st
import google.generativeai as genai
import utils
import agents

# Page Config Configuration Layout
st.set_page_config(page_title="AI Resume Screener Analyzer", page_icon="📄", layout="wide")

# Persistent Session State Storage Initialization Layer
if "candidate_pool" not in st.session_state:
    st.session_state.candidate_pool = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "target_profile" not in st.session_state:
    st.session_state.target_profile = None

st.title("📄 AI Resume Screener & Ranking Board")
st.write("Evaluate candidate fields against target corporate criteria utilizing automated multi-agent arbitration.")

# --- SIDEBAR: AUTHORIZATION & SYSTEM INGESTION CONFIGURATION ---
with st.sidebar:
    st.header("🔑 Authentication")
    api_key = st.text_input("Enter Gemini API Key:", type="password")
    
    st.markdown("---")
    st.header("📥 Data Ingestion")
    
    # Ingest Job Requirements Schema
    job_file = st.file_uploader("Upload Job Description (PDF) or Paste Below:", type=["pdf"])
    job_text_area = st.text_area("Paste Job Requirements Details manually:")
    
    # Ingest Candidate Data Profiles Batch
    resume_files = st.file_uploader("Upload Candidate Resumes (Multiple PDFs allowed):", type=["pdf"], accept_multiple_files=True)

# Main Dashboard Ingestion Activation Trigger
if not api_key:
    st.warning("⚠️ Access Blocked: Provide a valid Google Gemini API Key in the sidebar window to unlock execution models.")
else:
    # Set the Global configuration state token pointer globally
    genai.configure(api_key=api_key)
    
    # Resolve job details textual contents pipeline state variations
    job_description_content = ""
    if job_file:
        job_description_content = utils.extract_text_from_pdf(job_file)
    elif job_text_area:
        job_description_content = job_text_area

    # Primary Workflow trigger logic engine block
    if st.sidebar.button("🚀 Execute Multi-Agent Evaluation Loop", use_container_width=True):
        if not job_description_content.strip():
            st.error("❌ Process Halting: Missing target requirement attributes. Paste or upload a Job Description.")
        elif not resume_files:
            st.error("❌ Process Halting: Candidate queue vector array payload empty. Please upload resumes.")
        else:
            with st.spinner("🤖 System Node Alert: Profiling Job Matrix with specialized Core Model agent..."):
                try:
                    job_model = genai.GenerativeModel('gemini-3.1-flash-lite')
                    response = job_model.generate_content([agents.JOB_AGENT_PROMPT, job_description_content])
                    st.session_state.target_profile = response.text
                except Exception as e:
                    st.error(f"Error parsing job configurations parameters: {str(e)}")
            
            # Reset current candidate cache block state frame
            st.session_state.candidate_pool = []
            
            # Process incoming candidate arrays iteratively downstream
            progress_bar = st.progress(0)
            for index, resume in enumerate(resume_files):
                with st.spinner(f"🔄 Processing Core Agentic Loop for candidate record: {resume.name}..."):
                    raw_resume_text = utils.extract_text_from_pdf(resume)
                    
                    # Call Agent loop payload logic execution framework
                    evaluation_record = utils.run_agentic_screening_loop(
                        resume_name=resume.name,
                        resume_text=raw_resume_text,
                        target_profile=st.session_state.target_profile
                    )
                    
                    # Inject Lexical score matching calculations layer seamlessly
                    lexical_score = utils.calculate_similarity(job_description_content, raw_resume_text)
                    evaluation_record["lexical_similarity"] = lexical_score
                    
                    st.session_state.candidate_pool.append(evaluation_record)
                
                # Update visual metric increments indicators safely
                progress_bar.progress((index + 1) / len(resume_files))
            
            # Sort array configurations descending based on internal agent score allocations 
            st.session_state.candidate_pool = sorted(st.session_state.candidate_pool, key=lambda x: x["score"], reverse=True)
            st.success("🏆 Comprehensive Talent Acquisition Run Completed successfully!")

    # --- MAIN VIEW LAYOUT INTERFACE BUILDER ---
    if st.session_state.candidate_pool:
        st.write("## 🏆 Evaluation Ranking Matrix Dashboard")
        
        # Display Candidate breakdown summaries grid metrics maps
        for rank, candidate in enumerate(st.session_state.candidate_pool, start=1):
            with st.expander(f"🏅 Rank {rank}: {candidate['name']} — Consensus Score: {candidate['score']}/100 (Lexical Match: {candidate['lexical_similarity']}%)"):
                tab1, tab2, tab3 = st.tabs(["💻 Technical Lead Analysis", "🤝 HR Assessment", "🛡️ Audit Reports Trail"])
                with tab1:
                    st.markdown(candidate["tech_analysis"])
                with tab2:
                    st.markdown(candidate["hr_analysis"])
                with tab3:
                    st.info(f"Auditor Node Validation Response State: {candidate['audit_status']}")
        
        st.markdown("---")
        
        # --- CHAT INTERFACE SECTION WITH AUTOMATED INTENT ROUTER ---
        st.write("### 💬 System Assistant Communication Panel")
        st.caption("Ask questions about candidate portfolios or general knowledge queries (e.g. 'Who is the prime minister of india').")
        
        # Render historical interaction thread data frames inside active viewport state context
        for chat in st.session_state.chat_history:
            with st.chat_message(chat["role"]):
                st.markdown(chat["content"])
        
        # Ingest interactive stream context payloads via standard Chat Input UI frame
        if user_prompt := st.chat_input("Enter your request here..."):
            with st.chat_message("user"):
                st.markdown(user_prompt)
            st.session_state.chat_history.append({"role": "user", "content": user_prompt})
            
            # Step 1: Fire Intent Check using Router Matrix
            with st.spinner("Classifying intent topology..."):
                detected_intent = utils.route_user_intent(user_prompt)
            
            # Step 2: Branch Execution Stack depending on classification output
            if detected_intent == "CHITCHAT":
                with st.spinner("Consulting general chitchat knowledge graph..."):
                    agent_reply = utils.handle_chitchat(user_prompt)
            else:
                with st.spinner("Querying candidate contextual RAG vectors map..."):
                    agent_reply = utils.query_candidate_rag(user_prompt, st.session_state.candidate_pool)
            
            # Step 3: Stream generated response down to viewport buffer layers
            with st.chat_message("assistant"):
                st.markdown(agent_reply)
            st.session_state.chat_history.append({"role": "assistant", "content": agent_reply})
            
    else:
        st.info("💡 Application Idle State: Load your parameters data profile structures in the side configuration panels and hit execute to populate tracking models.")