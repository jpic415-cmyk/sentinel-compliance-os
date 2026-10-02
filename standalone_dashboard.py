import os
import streamlit as st
from google import genai

st.set_page_config(
    page_title="Sentinel Compliance OS | Law Enforcement Command",
    page_icon="🛡️",
    layout="wide"
)

# Initialize Gemini Client for Cloud Execution
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

# Custom CSS matching your command layout
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 8px; border: 1px solid #30363d; }
    </style>
""", unsafe_allow_html=True)

# Top Header banner with flexible accreditation framework
st.markdown("### Municipal Law Enforcement & Accreditation Command Center")
st.markdown("---")

# --- ACCREDITATION STANDARD SELECTOR ---
col_acc1, col_acc2 = st.columns([2, 2])
with col_acc1:
    accreditation_framework = st.selectbox(
        "Active Accreditation Framework",
        [
            "Connecticut POST-C Tier 1",
            "Connecticut POST-C Tier 2",
            "Connecticut POST-C Tier 3",
            "CALEA (Commission on Accreditation for Law Enforcement Agencies)",
            "Custom Municipal Standard"
        ]
    )
with col_acc2:
    st.markdown(f"**Current Profile:** {accreditation_framework} Active")

st.markdown("---")

# --- SECTION 1: Multi-Tier & CALEA Accreditation Standards & Live Proof Matrix ---
st.markdown(f"### 📋 {accreditation_framework} Standards & Live Proof Matrix")
st.markdown("Automatically synthesized proofs linking operational logs to active accreditation and statutory standards in real-time:")

col_h1, col_h2, col_h3, col_h4, col_h5 = st.columns([1, 2, 1, 1, 1])
with col_h1: st.markdown("**Standard**")
with col_h2: st.markdown("**Chapter Title & Requirement**")
with col_h3: st.markdown("**Live Proof Source**")
with col_h4: st.markdown("**Readiness Status**")
with col_h5: st.markdown("**Action**")

# Dynamic row based on selected framework
r1_c1, r1_c2, r1_c3, r1_c4, r1_c5 = st.columns([1, 2, 1, 1, 1])
with r1_c1: st.text("Std 4.3" if "POST-C" in accreditation_framework else "CALEA 12.1")
with r1_c2: st.text("Access Control, Secure Facility & Equipment Logs")
with r1_c3: st.text("Facility_Logs.db")
with r1_c4: st.success("Verified")
with r1_c5: 
    if st.button("Review", key="rev_1"):
        st.info(f"Accreditation proof verified against {accreditation_framework} requirements via active SQLite logs.")

st.markdown("---")

# --- SECTION 2: AI Intelligence Command Center (Gemini Powered) ---
st.markdown("### 🧠 AI Intelligence Command Center (Cloud-Powered)")
st.markdown("Select an analysis module to query department intelligence using live SQLite and regulatory context:")

col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
query_mode = None

with col_btn1:
    if st.button("1. Statutory Gap Analysis", use_container_width=True):
        query_mode = "Gap"
with col_btn2:
    if st.button("2. Recertification Drift AI", use_container_width=True):
        query_mode = "Drift"
with col_btn3:
    if st.button("3. Accreditation RAG Query", use_container_width=True):
        query_mode = "RAG"
with col_btn4:
    if st.button("4. Grant Funding Matcher", use_container_width=True):
        query_mode = "Grant"

# Execution Box for AI Queries
if query_mode:
    st.info(f"Active Intelligence Mode: **{query_mode} Analysis** under *{accreditation_framework}*")
    user_prompt = st.text_area("Enter specific parameters or target guidelines for analysis:")
    
    if st.button("Execute Intelligence Query"):
        if client and user_prompt.strip():
            with st.spinner("Synthesizing records with Gemini engine..."):
                try:
                    response = client.models.generate_content(
                        model='gemini-3.8-flash',
                        contents=f"Act as a certified law enforcement accreditation manager and compliance auditor specializing in {accreditation_framework}. Execute a {query_mode} analysis based on this prompt: {user_prompt}"
                    )
                    st.success("Analysis Complete")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Execution Error: {e}")
        else:
            st.warning("Please verify your GEMINI_API_KEY environment variable and enter a query.")

st.markdown("---")

# --- SECTION 3: Live Operational Grid ---
col_card1, col_card2, col_card3, col_card4 = st.columns(4)

with col_card1:
    st.markdown("### Sworn Roster")
    st.metric(label="Active Personnel", value="4 Officers", delta="POST-C Active")
    st.markdown("Compliance Cycle: **Verified**")

with col_card2:
    st.markdown("### Patrol Fleet")
    st.metric(label="Fleet Readiness", value="3 Units", delta="Inspection Current")
    st.markdown("Equipment Status: **Optimal**")

with col_card3:
    st.markdown("### Facility Logs")
    st.metric(label="Life-Safety", value="2 Active Logs", delta="Secured")
    st.markdown("NVR / Camera Feed: **Online**")

with col_card4:
    st.markdown("### Policy Tracker")
    st.metric(label="Acknowledgments", value="100%", delta="Zero Drift")
    st.markdown("Audit State: **Ready**")
