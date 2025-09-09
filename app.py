from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import fitz  # PyMuPDF (lightweight PDF parser)
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Gemini response generator
def get_gemini_response(prompt_intro, pdf_text, job_desc):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([prompt_intro, pdf_text, job_desc])
    return response.text

# Extract text from PDF using PyMuPDF
def extract_text_from_pdf(uploaded_file):
    if uploaded_file is not None:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    else:
        raise FileNotFoundError("No file uploaded")

# --- Streamlit UI ---

st.set_page_config(page_title="ATS Resume Expert", layout="centered", initial_sidebar_state="collapsed")

# Inject custom CSS for a modern look
st.markdown("""
<style>
    .main {
        background-color: #f0f2f6;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1 {
        color: #1a73e8; /* Google blue */
        text-align: center;
        font-size: 2.5rem;
    }
    h3 {
        color: #333333;
        font-weight: 600;
    }
    .stButton>button {
        background-color: #1a73e8;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        font-size: 16px;
        font-weight: bold;
        transition: background-color 0.3s, transform 0.2s;
        width: 100%;
        margin-top: 10px;
    }
    .stButton>button:hover {
        background-color: #145cb8;
        transform: scale(1.05);
    }
    .stTextInput>div>div>input {
        border-radius: 8px;
        border: 1px solid #ddd;
    }
    .stTextArea>label {
        font-weight: bold;
        color: #333;
    }
    .stFileUploader>div>div>label {
        font-weight: bold;
        color: #333;
    }
    .stFileUploader>div>div>input {
        color: #1a73e8;
    }
    .stAlert {
        border-radius: 8px;
    }
    .footer {
        text-align: center;
        margin-top: 2rem;
        font-size: 0.85rem;
        color: #666;
    }
    .stMarkdown h3 {
        border-bottom: 2px solid #e0e0e0;
        padding-bottom: 5px;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Main container for the app content
with st.container():
    st.markdown("<h1 style='text-align: center;'>🤖 ATS Resume Expert</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.1rem; color: #555;'>Your AI-powered assistant for perfecting your resume.</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Input section
    st.markdown("### 📝 Enter Job Description & Upload Resume")
    
    job_description = st.text_area("💼 Paste the Job Description here...", key="input", height=200)
    
    uploaded_file = st.file_uploader("📎 Upload your Resume (PDF only)", type=["pdf"], key="file_uploader")
    
    if uploaded_file:
        st.success("✅ PDF uploaded successfully! Ready to analyze.")

    # Action buttons
    st.markdown("---")
    st.markdown("### ✨ Get Your Analysis")
    
    col1, col2 = st.columns(2)
    with col1:
        submit_eval = st.button("🔍 Review Resume", help="Get a professional evaluation of your resume's strengths and weaknesses.")

    with col2:
        submit_match = st.button("📊 Match Percentage", help="See how well your resume matches the job description, including missing keywords.")

    # Processing and results display
    if submit_eval or submit_match:
        if uploaded_file:
            # Use a spinner to show that the app is working
            with st.spinner('Analyzing your resume...'):
                pdf_text = extract_text_from_pdf(uploaded_file)
                if submit_eval:
                    response = get_gemini_response(evaluation_prompt, pdf_text, job_description)
                    st.markdown("---")
                    st.markdown("### 📄 Evaluation Result")
                    st.markdown(response)
                elif submit_match:
                    response = get_gemini_response(match_prompt, pdf_text, job_description)
                    st.markdown("---")
                    st.markdown("### 📊 Match Analysis")
                    st.markdown(response)
        else:
            st.warning("⚠️ Please upload your resume to proceed.")

# Gemini Prompt Templates (kept as is)
evaluation_prompt = """
You are an experienced Technical Human Resource Manager. Review the provided resume against the job description. 
Give a professional evaluation of how well the resume aligns with the role, highlighting strengths and weaknesses.
"""

match_prompt = """
You are an ATS (Applicant Tracking System) scanner with expertise in resume evaluation. Analyze the resume against the job description.
Return:
1. Percentage Match
2. Missing Keywords
3. Final Thoughts
Avoid giving percentage alone. Always follow up with detailed feedback.
"""

# Footer
st.markdown("---")
st.markdown(
    "<div class='footer'>© 2025 All rights reserved by <strong>Jeki Panchal</strong></div>",
    unsafe_allow_html=True
)
