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

    # Sidebar Navigation for Department Operations
    st.sidebar.title("🛡️ Sentinel Compliance OS")
    st.sidebar.markdown("### Municipal & Operational Hub")
    st.sidebar.markdown("---")
    
    module = st.sidebar.radio(
        "Select Operation Module", 
        [
            "📋 PA 23-116 & Compliance Query", 
            "📜 Administrative Directive Builder", 
            "🚗 LPR & Traffic Enforcement Protocol", 
            "⚖️ Operational Document Review & Audit"
        ]
    )

    if module == "📋 PA 23-116 & Compliance Query":
        st.subheader("📋 Public Act 23-116 & Municipal Compliance Engine")
        st.markdown("Query statutory mandates, traffic enforcement guidelines, data retention rules, and municipal standard operating procedures.")
        
        user_query = st.text_area(
            "Enter compliance question or statute reference:", 
            placeholder="e.g., What are the mandatory 30-day grace period and review requirements under Public Act 23-116 for automated safety devices?"
        )
        
        if st.button("Generate Regulatory Analysis"):
            if user_query.strip():
                with st.spinner("Analyzing with Gemini..."):
                    try:
                        response = client.models.generate_content(
                            model='gemini-3.8-flash',
                            contents=f"Act as an expert municipal police administrator and legal compliance officer in Connecticut. Provide a precise, structured analysis referencing relevant statutes like PA 23-116 for: {user_query}",
                        )
                        st.success("Analysis Complete")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
            else:
                st.warning("Please enter a query first.")
                
    elif module == "📜 Administrative Directive Builder":
        st.subheader("📜 Department Directive & Policy Builder")
        st.markdown("Draft formal municipal administrative memos, general orders, FTO/DTO protocols, and standard operating procedures.")
        
        col1, col2 = st.columns(2)
        with col1:
            directive_type = st.selectbox(
                "Directive Classification", 
                ["General Order", "Administrative Memorandum", "Training Bulletin", "Field Training/DTO Protocol"]
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

    elif module == "🚗 LPR & Traffic Enforcement Protocol":
        st.subheader("🚗 LPR & Automated Traffic Enforcement Safety (ATESD)")
        st.markdown("Generate specialized procurement proposals, ordinance frameworks, data privacy policies, and deployment protocols compliant with CT DOT guidelines.")
        
        lpr_option = st.selectbox(
            "Select Protocol Focus",
            [
                "Flock Safety LPR & Camera Deployment Proposal",
                "Automated Traffic Enforcement Safety Device (ATESD) Ordinance Template",
                "Data Privacy, FOIA, and Retention Protocol (CGS § 1-200)",
                "School Zone Speed Enforcement & Warning Period Workflow"
            ]
        )
        
        context_notes = st.text_area(
            "Specific location data or custom department notes:", 
            placeholder="e.g., Target school zone corridors, specific speed thresholds (10+ mph over limit), etc."
        )

        if st.button("Generate LPR / Traffic Protocol"):
            with st.spinner("Compiling administrative protocol..."):
                try:
                    prompt = f"Draft a comprehensive, legally rigorous municipal police document for: {lpr_option}. Local context provided: {context_notes}. Ensure strict alignment with Connecticut statutory requirements and DOT standards."
                    response = client.models.generate_content(
                        model='gemini-3.8-flash',
                        contents=prompt,
                    )
                    st.success("Protocol Generated")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"An error occurred: {e}")

    elif module == "⚖️ Operational Document Review & Audit":
        st.subheader("⚖️ Operational Document & Proposal Audit")
        st.markdown("Evaluate draft memos, policy changes, or procurement proposals for administrative liability, operational risk, and regulatory alignment.")
        
        doc_text = st.text_area(
            "Paste draft text, policy, or municipal proposal for review:", 
            placeholder="Paste text here..."
        )
        
        if st.button("Execute Compliance Audit"):
            if doc_text.strip():
                with st.spinner("Running administrative and statutory risk audit..."):
                    try:
                        audit_prompt = f"Perform a rigorous municipal administrative and compliance audit on the following text. Identify potential liability points, administrative gaps, and statutory requirements:\n\n{doc_text}"
                        response = client.models.generate_content(
                            model='gemini-3.8-flash',
                            contents=audit_prompt,
                        )
                        st.success("Audit Complete")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
            else:
                st.warning("Please provide text to audit.")
