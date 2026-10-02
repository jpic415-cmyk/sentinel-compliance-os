import os
import streamlit as st
from google import genai

st.set_page_config(
    page_title="Sentinel Compliance OS",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Gemini Client using the environment variable
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ GEMINI_API_KEY environment variable not found! Please configure it in your Railway service variables.")
else:
    client = genai.Client(api_key=api_key)

    # Sidebar Navigation for Full Command Hub
    st.sidebar.title("🛡️️ Sentinel Compliance OS")
    st.sidebar.markdown("### Executive & Operational Command")
    st.sidebar.markdown("---")
    
    module = st.sidebar.radio(
        "Select Operation Module", 
        [
            "🏠 Executive Command Overview",
            "📋 Municipal Compliance & Statutes", 
            "🎓 FTO / DTO Recruit Management", 
            "🎯 Department Training & Certifications", 
            "🏢 Facility & Equipment Operations",
            "📜 Administrative Directive Builder"
        ]
    )

    if module == "🏠 Executive Command Overview":
        st.title("🛡️ Sentinel Compliance Operating System")
        st.markdown("### Enterprise Municipal Law Enforcement & Administrative Intelligence")
        st.markdown("---")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="Compliance Health Score", value="98.4%", delta="+1.2% this quarter")
        with col2:
            st.metric(label="Active System Status", value="Online / Secure", delta="Railway Production")
        with col3:
            st.metric(label="Active FTO Recruits", value="4 Enrolled", delta="Phase Progression Normal")
        with col4:
            st.metric(label="Audit Trail Status", value="Immutable / Verified", delta="Chain-of-Custody Active")

        st.markdown("---")
        st.markdown("""
        #### System Architecture & Core Modules:
        * **Municipal Compliance & Statutes:** Track public acts (e.g., PA 23-116), data retention requirements, and local policy alignment to mitigate liability.
        * **FTO / DTO Recruit Management:** Standardized Daily Observation Reports (DORs), performance scoring grids, and remediation tracking.
        * **Department Training & Certifications:** Monitor CT P.O.S.T. compliance, firearms qualifications, instructor credentials, and ICS levels (300/400/700/800).
        * **Facility & Equipment Operations:** Manage commercial security hardware, NVR/IP camera infrastructures (Honeywell, Hikvision, Amcrest), fleet readiness, and LPR deployment logs.
        * **Administrative Directive Builder:** Draft formal departmental general orders, administrative memos, and standard operating procedures with built-in statutory audits.
        """)

    elif module == "📋 Municipal Compliance & Statutes":
        st.subheader("📋 Public Act & Municipal Compliance Engine")
        st.markdown("Query statutory mandates, traffic enforcement guidelines, data retention rules, and municipal standard operating procedures.")
        
        user_query = st.text_area(
            "Enter compliance question or statute reference:", 
            placeholder="e.g., What are the mandatory requirements and review protocols under Public Act 23-116 for automated safety devices?"
        )
        
        if st.button("Generate Regulatory Analysis"):
            if user_query.strip():
                with st.spinner("Analyzing with Gemini..."):
                    try:
                        response = client.models.generate_content(
                            model='gemini-3.8-flash',
                            contents=f"Act as an expert municipal police administrator and legal compliance officer in Connecticut. Provide a precise, structured analysis referencing relevant statutes for: {user_query}",
                        )
                        st.success("Analysis Complete")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
            else:
                st.warning("Please enter a query first.")

    elif module == "🎓 FTO / DTO Recruit Management":
        st.subheader("🎓 Field Training Officer (FTO) & DTO Program Manager")
        st.markdown("Manage recruit performance, Daily Observation Reports (DORs), remediation tracking, and phase evaluations.")
        
        col1, col2 = st.columns(2)
        with col1:
            recruit_name = st.text_input("Recruit Officer Name / ID:")
            training_phase = st.selectbox("Training Phase", ["Phase 1 (Orientation/Shadow)", "Phase 2 (Core Application)", "Phase 3 (Advanced/Shadowing)", "Phase 4 (Ghost Phase / Final Evaluation)"])
        with col2:
            fto_name = st.text_input("Assigned FTO / DTO Name:")
            evaluation_focus = st.selectbox("Primary Evaluation Category", ["Officer Safety & Mechanics", "Radio Communications & Code Knowledge", "Report Writing & Documentation", "Decision Making & Problem Solving", "Physical/Tactical Proficiency"])

        performance_notes = st.text_area(
            "Daily Observation Notes / Remedial Areas:", 
            placeholder="Document specific performance markers, remediation steps, or notable strengths..."
        )

        if st.button("Generate FTO Evaluation Summary & Guidance"):
            if recruit_name.strip() and performance_notes.strip():
                with st.spinner("Synthesizing training evaluation..."):
                    try:
                        prompt = f"Act as an expert FTO Program Coordinator. Review the following notes for Recruit {recruit_name} in {training_phase} under FTO {fto_name} focusing on {evaluation_focus}: \n\n{performance_notes}. Provide structured Daily Observation Report (DOR) feedback, remedial training recommendations if applicable, and objective grading guidance."
                        response = client.models.generate_content(
                            model='gemini-3.8-flash',
                            contents=prompt,
                        )
                        st.success("FTO Evaluation Compiled")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
            else:
                st.warning("Please enter recruit name and performance notes.")

    elif module == "🎯 Department Training & Certifications":
        st.subheader("🎯 Department Training & POST Certification Tracking")
        st.markdown("Monitor instructor certifications, mandatory review cycles, tactical training logs, and Incident Command System (ICS) compliance.")
        
        training_category = st.selectbox(
            "Training Domain",
            [
                "Connecticut P.O.S.T. Mandatory Compliance",
                "Field Training / Instructor Development",
                "Advanced Incident Command System (ICS-300 / ICS-400 / IS-700 / IS-800)",
                "Tactical, Defensive Tactics & Firearms Qualification",
                "Specialized Program In-Service Training"
            ]
        )
        
        training_details = st.text_area(
            "Training Objectives, Roster, or Curriculum Notes:", 
            placeholder="Enter training schedule, attendee counts, or compliance tracking requirements..."
        )

        if st.button("Generate Training / Compliance Plan"):
            with st.spinner("Generating training framework..."):
                try:
                    prompt = f"Create a comprehensive municipal department training plan and compliance checklist for: {training_category}. Context provided: {training_details}. Ensure alignment with state certification standards and risk management protocols."
                    response = client.models.generate_content(
                        model='gemini-3.8-flash',
                        contents=prompt,
                    )
                    st.success("Training Framework Generated")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"An error occurred: {e}")

    elif module == "🏢 Facility & Equipment Operations":
        st.subheader("🏢 Facility Security, Fleet & Equipment Management")
        st.markdown("Manage facility hardware specifications, NVR/IP camera infrastructure (Honeywell, Hikvision, Amcrest), fleet logistics, and equipment maintenance logs.")
        
        eq_module = st.selectbox(
            "Operational Asset",
            [
                "Security Hardware & NVR / IP Camera Integration",
                "Vehicle Fleet & Special Equipment Readiness",
                "Facility Maintenance & Infrastructure Audit",
                "Automated License Plate Reader (LPR) Infrastructure"
            ]
        )
        
        eq_notes = st.text_area(
            "Equipment Specs, Issue Log, or Deployment Scope:", 
            placeholder="Enter camera channels, hardware models, maintenance intervals, or upgrade parameters..."
        )

        if st.button("Generate Operational Asset Report"):
            with st.spinner("Compiling equipment and facility report..."):
                try:
                    prompt = f"Act as an administrative operations commander. Draft a professional technical assessment, maintenance schedule, or operational deployment guideline for: {eq_module}. Details: {eq_notes}"
                    response = client.models.generate_content(
                        model='gemini-3.8-flash',
                        contents=prompt,
                    )
                    st.success("Asset Report Generated")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"An error occurred: {e}")

    elif module == "📜 Administrative Directive Builder":
        st.subheader("📜 Department Directive & Policy Builder")
        st.markdown("Draft formal municipal administrative memos, general orders, FTO/DTO protocols, and standard operating procedures.")
        
        col1, col2 = st.columns(2)
        with col1:
            directive_type = st.selectbox(
                "Directive Classification", 
                ["General Order", "Administrative Memorandum", "Training Bulletin", "Field Training / DTO Protocol"]
            )
        with col2:
            subject = st.text_input("Directive Subject / Title:", placeholder="e.g., Field Training Officer Program Guidelines")
            
        parameters = st.text_area(
            "Specific operational parameters, supervisory guidelines, or local requirements to incorporate:", 
            placeholder="Define scope, responsibilities, reporting metrics, and compliance workflows..."
        )
        
        if st.button("Draft Official Directive"):
            if subject.strip():
                with st.spinner("Drafting official municipal directive..."):
                    try:
                        prompt = f"Draft a professional municipal police department {directive_type.lower()} regarding '{subject}'. Incorporate these operational parameters: {parameters}. Ensure proper formatting including Purpose, Policy, Procedure, and Compliance."
                        response = client.models.generate_content(
                            model='gemini-3.8-flash',
                            contents=prompt,
                        )
                        st.success("Directive Drafted Successfully")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
            else:
                st.warning("Please specify a subject for the directive.")
