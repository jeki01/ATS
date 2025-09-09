from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import fitz  # PyMuPDF (lightweight PDF parser)
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

st.set_page_config(page_title="ATS Resume Expert", layout="centered")

st.markdown("<h1 style='text-align: center; color: #4CAF50;'>📄 ATS Resume Expert</h1>", unsafe_allow_html=True)
st.markdown("### 👇 Upload your resume & paste the job description")

job_description = st.text_area("💼 Job Description", key="input")
uploaded_file = st.file_uploader("📎 Upload your Resume (PDF only)", type=["pdf"])

if uploaded_file:
    st.success("✅ PDF uploaded successfully!")

# Gemini Prompt Templates
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

col1, col2 = st.columns(2)
with col1:
    submit_eval = st.button("🔍 Review Resume")

with col2:
    submit_match = st.button("📊 Match Percentage")

if submit_eval or submit_match:
    if uploaded_file:
        pdf_text = extract_text_from_pdf(uploaded_file)
        if submit_eval:
            response = get_gemini_response(evaluation_prompt, pdf_text, job_description)
            st.subheader("📄 Evaluation Result")
            st.write(response)
        elif submit_match:
            response = get_gemini_response(match_prompt, pdf_text, job_description)
            st.subheader("📊 Match Analysis")
            st.write(response)
    else:
        st.warning("⚠️ Please upload your resume to proceed.")

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; font-size: 14px; color: gray;'>© 2025 All rights reserved by <strong>Jeki Panchal</strong></p>",
    unsafe_allow_html=True
)
