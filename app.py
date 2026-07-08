from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import fitz
from google import genai

# -------------------------
# Streamlit Config
# -------------------------
st.set_page_config(
    page_title="ATS Resume Expert",
    page_icon="📄",
    layout="centered"
)

# -------------------------
# Get API Key
# -------------------------
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("GOOGLE_API_KEY not found in Streamlit Secrets.")
    st.stop()

# Gemini Client
client = genai.Client(api_key=api_key)


# -------------------------
# Extract text from PDF
# -------------------------
def extract_text_from_pdf(uploaded_file):
    text = ""

    try:
        pdf_document = fitz.open(
            stream=uploaded_file.read(),
            filetype="pdf"
        )

        for page in pdf_document:
            text += page.get_text()

        pdf_document.close()

    except Exception as e:
        st.error(f"Error reading PDF: {e}")

    return text


# -------------------------
# Gemini Response
# -------------------------
def get_gemini_response(prompt, resume_text, job_description):

    final_prompt = f"""
{prompt}

==========================
RESUME
==========================

{resume_text}

==========================
JOB DESCRIPTION
==========================

{job_description}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=final_prompt
    )

    return response.text


# -------------------------
# Prompt Templates
# -------------------------
evaluation_prompt = """
You are an experienced HR Manager and Technical Recruiter.

Analyze the resume against the job description and provide:

1. Overall evaluation
2. Strengths
3. Weaknesses
4. Missing skills
5. Suggestions for improvement
"""

match_prompt = """
You are an ATS system.

Analyze the resume against the job description and provide:

1. ATS Match Percentage
2. Matching Skills
3. Missing Keywords
4. Areas to Improve
5. Final Recommendation

Return response in detailed format.
"""


# -------------------------
# UI
# -------------------------
st.title("📄 ATS Resume Expert")

st.write(
    "Upload your resume and compare it with the job description."
)

job_description = st.text_area(
    "💼 Paste Job Description",
    height=250
)

uploaded_file = st.file_uploader(
    "📎 Upload Resume (PDF only)",
    type=["pdf"]
)

if uploaded_file:
    st.success("Resume uploaded successfully ✅")

col1, col2 = st.columns(2)

with col1:
    review_button = st.button(
        "🔍 Review Resume",
        use_container_width=True
    )

with col2:
    match_button = st.button(
        "📊 ATS Match",
        use_container_width=True
    )


# -------------------------
# Actions
# -------------------------
if review_button or match_button:

    if uploaded_file is None:
        st.warning("Please upload your resume.")
        st.stop()

    if not job_description.strip():
        st.warning("Please enter the job description.")
        st.stop()

    with st.spinner("Analyzing Resume..."):

        resume_text = extract_text_from_pdf(uploaded_file)

        if len(resume_text.strip()) == 0:
            st.error("Unable to extract text from PDF.")
            st.stop()

        try:
            if review_button:
                result = get_gemini_response(
                    evaluation_prompt,
                    resume_text,
                    job_description
                )

                st.subheader("📄 Resume Review")
                st.write(result)

            if match_button:
                result = get_gemini_response(
                    match_prompt,
                    resume_text,
                    job_description
                )

                st.subheader("📊 ATS Match Result")
                st.write(result)

        except Exception as e:
            st.error(f"Gemini Error: {e}")


# -------------------------
# Footer
# -------------------------
st.markdown("---")
st.markdown(
    """
    <center>
    © 2026 ATS Resume Expert | Developed by <b>Jeki Panchal</b>
    </center>
    """,
    unsafe_allow_html=True
)
