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

    # Sidebar Navigation for Municipal Operations
    st.sidebar.title("🛡️ Sentinel Compliance OS")
    st.sidebar.markdown("---")
    module = st.sidebar.radio(
        "Select Operation Module", 
        [
            "📋 Municipal Compliance Query", 
            "📜 Administrative Directive Builder", 
            "🚗 LPR & Traffic Enforcement Policy", 
            "⚖️ Public Act Compliance Audit"
        ]
    )

    if module == "📋 Municipal Compliance Query":
        st.subheader("📋 Municipal Directives & Standards Analyzer")
        st.markdown("Query regulations, public act mandates, and municipal standard operating procedures.")
        
        user_query = st.text_area(
            "Enter your compliance or administrative question:", 
            placeholder="e.g., What are the operational reporting requirements under Public Act mandates?"
        )
        
        if st.button("Generate Analysis"):
            if user_query.strip():
                with st.spinner("Analyzing with Gemini..."):
                    try:
                        response = client.models.generate_content(
                            model='gemini-3.8-flash',
                            contents=f"Act as a municipal compliance expert and administrative officer. Provide a clear, structured analysis for: {user_query}",
                        )
                        st.success("Analysis Complete")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
            else:
                st.warning("Please enter a query first.")
                
    elif module == "📜 Administrative Directive Builder":
        st.subheader("📜 Administrative Directive & Policy Builder")
        st.markdown("Draft formal departmental orders, operational policies, and administrative memos.")
        
        topic = st.text_input("Directive Topic / Subject:", placeholder="e.g., Department Training & Field Officer Standards")
        details = st.text_area("Key operational parameters or specific requirements to incorporate:", placeholder="Define scope, supervisory responsibilities, and compliance guidelines...")
        
        if st.button("Draft Directive"):
            if topic.strip():
                with st.spinner("Drafting official directive..."):
                    try:
                        prompt = f"Draft a professional municipal administrative directive or policy regarding: {topic}. Incorporate these operational parameters: {details}"
                        response = client.models.generate_content(
                            model='gemini-3.8-flash',
                            contents=prompt,
                        )
                        st.success("Directive Drafted")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
            else:
                st.warning("Please enter a topic.")

    elif module == "🚗 LPR & Traffic Enforcement Policy":
        st.subheader("🚗 LPR & Traffic Enforcement Directives")
        st.markdown("Generate specialized protocols, data retention policies, and procurement frameworks for traffic enforcement and automated technology.")
        
        lpr_focus = st.selectbox(
            "Select Operational Focus",
            [
                "Flock Safety LPR Deployment Protocol",
                "Public Act 23-116 Compliance Guidelines",
                "Traffic Enforcement Strategy & Data Retention",
                "Automated Plate Reader Standard Operating Procedure"
            ]
        )
        
        additional_notes = st.text_area("Specific department guidelines or local parameters:", placeholder="Optional context to tailor the policy...")

        if st.button("Generate LPR Protocol"):
            with st.spinner("Generating operational protocol..."):
                try:
                    prompt = f"Draft a comprehensive, professional municipal policy document for: {lpr_focus}. Additional department context: {additional_notes}"
                    response = client.models.generate_content(
                        model='gemini-3.8-flash',
                        contents=prompt,
                    )
                    st.success("Protocol Generated")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"An error occurred: {e}")

    elif module == "⚖️ Public Act Compliance Audit":
        st.subheader("⚖️ Public Act & Regulatory Compliance Audit")
        st.markdown("Evaluate administrative directives, memos, or operational proposals for statutory alignment and compliance.")
        
        audit_text = st.text_area("Paste policy text, memo, or proposal for compliance review:", placeholder="Paste draft text here...")
        
        if st.button("Run Compliance Audit"):
            if audit_text.strip():
                with st.spinner("Executing compliance audit..."):
                    try:
                        audit_prompt = f"Perform a rigorous municipal administrative and legal compliance audit on the following text. Identify potential gaps, liability points, and statutory requirements:\n\n{audit_text}"
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
