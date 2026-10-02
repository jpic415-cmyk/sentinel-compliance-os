import os
import streamlit as st
from google import genai

st.set_page_config(page_title="Sentinel Compliance OS", layout="wide")

st.title("🛡️ Sentinel Compliance OS")
st.markdown("### AI-Powered Municipal & Administrative Compliance Dashboard")

# Initialize Gemini Client using the environment variable
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ GEMINI_API_KEY environment variable not found! Please configure it in your Railway service variables.")
else:
    client = genai.Client(api_key=api_key)
    
    st.sidebar.header("Navigation & Controls")
    option = st.sidebar.selectbox("Select Tool", ["Compliance Query", "Directive Assistant"])

    if option == "Compliance Query":
        st.subheader("Query Municipal Directives & Standards")
        user_prompt = st.text_area("Enter your compliance or administrative question:", placeholder="e.g., What are the public act requirements for our operations?")
        
        if st.button("Generate Response"):
            if user_prompt.strip():
                with st.spinner("Analyzing with Gemini..."):
                    try:
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=user_prompt,
                        )
                        st.success("Analysis Complete")
                        st.write(response.text)
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
            else:
                st.warning("Please enter a query first.")
                
    elif option == "Directive Assistant":
        st.subheader("Administrative Directive Builder")
        topic = st.text_input("Directive Topic:", placeholder="e.g., Traffic Enforcement Policy")
        if st.button("Draft Directive"):
            if topic.strip():
                with st.spinner("Drafting official directive..."):
                    try:
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=f"Draft a professional municipal administrative directive or policy regarding: {topic}",
                        )
                        st.success("Directive Drafted")
                        st.write(response.text)
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
            else:
                st.warning("Please enter a topic.")
