FROM python:3.11-slim
WORKDIR /app
RUN pip install google-genai streamlit
COPY standalone_dashboard.py /app/
RUN mkdir -p /app/proof_uploads
EXPOSE 8080
CMD ["streamlit", "run", "standalone_dashboard.py", "--server.port=8080", "--server.address=0.0.0.0"]

