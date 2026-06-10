# Resume Screener Analyzer

A Streamlit-based AI resume screening and ranking app that compares uploaded resumes against a job description using Google Gemini. The app extracts text from PDF resumes, runs a multi-agent evaluation workflow, ranks candidates, and provides a chat assistant for querying the final candidate pool.

## Live App

Use the deployed version here: [https://resumin-ai.streamlit.app/](https://resuminda.streamlit.app/)

## Tech Stack

- Streamlit for the web UI and interactive dashboard
- Google Generative AI for analysis, scoring, and chat responses
- PyPDF for extracting text from uploaded PDF resumes and job descriptions
- Regular expressions for score parsing and report cleanup
- scikit-learn for TF-IDF and cosine-similarity based utility analysis
- NumPy and Requests as supporting libraries

## How It Works

1. The user enters a Gemini API key in the sidebar.
2. The user provides a job description either by pasting text or uploading a PDF.
3. One or more resume PDFs are uploaded.
4. The app extracts text from every PDF using PyPDF.
5. The job description is first analyzed by a dedicated job-description agent to extract the target role profile.
6. Each resume then goes through a cyclic evaluation loop:
   - a Technical Lead agent reviews the resume against the extracted job criteria,
   - an HR and Culture agent evaluates soft skills and trajectory,
   - an Auditor agent checks both outputs for inconsistencies or hallucinations,
   - if the Auditor rejects the result, the system revises the evaluation up to a small retry limit.
7. The final score is parsed, cleaned, and stored in Streamlit session state.
8. Candidates are ranked and displayed in the dashboard with detailed tabs for verified reports, technical analysis, and HR analysis.
9. After ranking, the built-in chat assistant can answer questions about the candidate pool.

## Implementation Notes

- The main application logic lives in [app.py](app.py).
- Agent prompts and role definitions are stored in [agents.py](agents.py).
- Supporting analysis helpers, including TF-IDF similarity and RAG-style utilities, are implemented in [utils.py](utils.py).
- Uploaded resumes are processed in memory during the session; refreshing the page clears the current candidate pool.
- The app currently expects a valid Gemini API key from the user before it can run an assessment.

## Local Setup

1. Create and activate a Python virtual environment.
2. Install the dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
streamlit run app.py
```

4. Open the local Streamlit URL shown in the terminal and provide:
   - your Gemini API key,
   - a job description,
   - one or more PDF resumes.

## Project Structure

- [app.py](app.py) - Streamlit UI and end-to-end screening workflow
- [agents.py](agents.py) - system instructions for the different Gemini agents
- [utils.py](utils.py) - reusable text extraction and scoring helpers
- [requirements.txt](requirements.txt) - Python dependencies

## Notes

- Resume screening quality depends heavily on the job description and the uploaded PDF text quality.
- For best results, use clean PDF resumes with selectable text rather than scanned images.
- The app is designed for screening assistance, not final hiring decisions.
