import os
import streamlit as st
from google import genai

st.set_page_config(
    page_title="Sentinel Compliance OS",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Gemini Client
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️️ GEMINI_API_KEY environment variable not found! Please configure it in your Railway service variables.")
else:
    client = genai.Client(api_key=api_key)

    # Sidebar Navigation
    st.sidebar.title("🛡️ Sentinel OS")
    st.sidebar.markdown("---")
    module = st.sidebar.radio(
        "Select Module", 
        [
            "🏠 Command Overview", 
            "📋 Municipal Compliance Query", 
            "📜 Directive & Policy Generator", 
            "🔍 Standard Operating Audit"
        ]
    )

    if module == "🏠 Command Overview":
        st.title("🛡️ Sentinel Compliance Operating System")
        st.markdown("### Advanced Municipal & Administrative Operational Intelligence")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="System Status", value="Online / Secure", delta="Railway Live")
        with col2:
            st.metric(label="Engine", value="Gemini Flash", delta="Active")
        with col3:
            st.metric(label="Environment", value="Production", delta="v1.0")

        st.markdown("---")
        st.markdown("""
        #### Operational Capabilities:
        * **Municipal Compliance Query:** Analyze public acts, local regulations, and operational constraints in real-time.
        * **Directive & Policy Generator:** Draft precise administrative directives, compliance memos, and department protocols.
        * **Standard Operating Audit:** Review operational procedures for liability mitigation and regulatory alignment.
        """)

    elif module == "📋 Municipal Compliance Query":
        st.subheader("📋 Municipal Directives & Standards Analyzer")
        st.markdown("Query regulations, public act mandates, and municipal standard operating procedures.")
        
        user_query = st.text_area("Enter compliance question or statute reference:", placeholder="e.g., Outline the reporting compliance requirements under Public Act mandates.")
        
        if st.button("Run Compliance Analysis"):
            if user_query.strip():
                with st.spinner("Synthesizing regulatory data..."):
                    try:
                        response = client.models.generate_content(
                            model='gemini-3.8-flash',
                            contents=f"Act as a municipal compliance expert and administrative officer. Provide a clear, structured analysis for: {user_query}",
                        )
                        st.success("Analysis Complete")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"API Error: {e}")
            else:
                st.warning("Please enter a query.")

    elif module == "📜 Directive & Policy Generator":
        st.subheader("📜 Administrative Directive & Policy Builder")
        st.markdown("Draft formal departmental orders, operational policies, and compliance procedures.")
        
        col_a, col_b = st.columns(2)
        with col_a:
            topic = st.text_input("Directive Subject / Title:", placeholder="e.g., Traffic Enforcement & LPR Protocol")
        with col_b:
            scope = st.selectbox("Directive Classification", ["General Order", "Administrative Memorandum", "Standard Operating Procedure", "Training Bulletin"])
            
        details = st.text_area("Key operational points or parameters to include:", placeholder="e.g., Mandate supervisory review, define data retention windows...")

        if st.button("Draft Official Directive"):
            if topic.strip():
                with st.spinner("Drafting administrative directive..."):
                    try:
                        prompt = f"Draft a formal municipal {scope.lower()} regarding '{topic}'. Incorporate these parameters: {details}. Ensure professional formatting with Purpose, Policy, Procedure, and Compliance sections."
                        response = client.models.generate_content(
                            model='gemini-3.8-flash',
                            contents=prompt,
                        )
                        st.success("Draft Generated Successfully")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"API Error: {e}")
            else:
                st.warning("Please specify a directive topic.")

    elif module == "🔍 Standard Operating Audit":
        st.subheader("🔍 Standard Operating Procedure Audit")
        st.markdown("Evaluate an existing procedure or draft policy for administrative risk, liability, and structural gaps.")
        
        procedure_text = st.text_area("Paste procedure text or outline for auditing:", placeholder="Paste draft policy text here...")
        
        if st.button("Perform Risk & Compliance Audit"):
            if procedure_text.strip():
                with st.spinner("Auditing operational parameters..."):
                    try:
                        audit_prompt = f"Perform a comprehensive compliance and risk audit on the following procedure text. Identify potential administrative gaps, liability points, and recommendations for improvement:\n\n{procedure_text}"
                        response = client.models.generate_content(
                            model='gemini-3.8-flash',
                            contents=audit_prompt,
                        )
                        st.success("Audit Complete")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"API Error: {e}")
            else:
                st.warning("Please provide text to audit.")
