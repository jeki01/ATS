import os
import streamlit as st
import fitz  # PyMuPDF
from dotenv import load_dotenv

load_dotenv()

try:
    from google import genai
except ImportError:
    st.error("Package missing: Add google-genai in requirements.txt and reboot Streamlit app.")
    st.stop()


# ---------------- Gemini API Setup ----------------

api_key = os.getenv("GOOGLE_API_KEY")

try:
    api_key = api_key or st.secrets["GOOGLE_API_KEY"]
except Exception:
    pass

if not api_key:
    st.error("GOOGLE_API_KEY missing. Add it in Streamlit Secrets or .env file.")
    st.stop()

client = genai.Client(api_key=api_key)


# ---------------- Helper Functions ----------------

def get_gemini_response(prompt_intro, pdf_text, job_desc):
    final_prompt = f"""
{prompt_intro}

Resume Text:
{pdf_text}

Job Description:
{job_desc}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=final_prompt
    )

    return response.text


def extract_text_from_pdf(uploaded_file):
    if uploaded_file is None:
        raise FileNotFoundError("No file uploaded")

    uploaded_file.seek(0)
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")

    text = ""
    for page in doc:
        text += page.get_text()

    doc.close()
    return text


# ---------------- Streamlit UI ----------------

st.set_page_config(
    page_title="ATS Resume Expert",
    layout="centered"
)

st.markdown(
    "<h1 style='text-align: center; color: #4CAF50;'>📄 ATS Resume Expert</h1>",
    unsafe_allow_html=True
)

st.markdown("### 👇 Upload your resume & paste the job description")

job_description = st.text_area("💼 Job Description", key="input")

uploaded_file = st.file_uploader(
    "📎 Upload your Resume (PDF only)",
    type=["pdf"]
)

if uploaded_file:
    st.success("✅ PDF uploaded successfully!")


# ---------------- Prompt Templates ----------------

evaluation_prompt = """
You are an experienced Technical Human Resource Manager.
Review the provided resume against the job description.
Give a professional evaluation of how well the resume aligns with the role.
Highlight strengths, weaknesses, and improvement suggestions.
"""

match_prompt = """
You are an ATS Applicant Tracking System scanner with expertise in resume evaluation.
Analyze the resume against the job description.

Return the response in this format:

1. Percentage Match
2. Missing Keywords
3. Strong Matching Skills
4. Weak Areas
5. Final Thoughts

Do not give percentage alone. Always provide detailed feedback.
"""


# ---------------- Buttons ----------------

col1, col2 = st.columns(2)

with col1:
    submit_eval = st.button("🔍 Review Resume")

with col2:
    submit_match = st.button("📊 Match Percentage")


# ---------------- Main Logic ----------------

if submit_eval or submit_match:

    if not uploaded_file:
        st.warning("⚠️ Please upload your resume to proceed.")
        st.stop()

    if not job_description.strip():
        st.warning("⚠️ Please paste the job description.")
        st.stop()

    try:
        with st.spinner("Analyzing your resume..."):
            pdf_text = extract_text_from_pdf(uploaded_file)

            if not pdf_text.strip():
                st.error("Could not extract text from this PDF. Please upload a text-based resume PDF.")
                st.stop()

            if submit_eval:
                response = get_gemini_response(
                    evaluation_prompt,
                    pdf_text,
                    job_description
                )
                st.subheader("📄 Evaluation Result")
                st.write(response)

            elif submit_match:
                response = get_gemini_response(
                    match_prompt,
                    pdf_text,
                    job_description
                )
                st.subheader("📊 Match Analysis")
                st.write(response)

    except Exception as e:
        st.error("Something went wrong while processing.")
        st.exception(e)


# ---------------- Footer ----------------

st.markdown("---")

st.markdown(
    "<p style='text-align: center; font-size: 14px; color: gray;'>© 2026 All rights reserved by <strong>Jeki Panchal</strong></p>",
    unsafe_allow_html=True
)
