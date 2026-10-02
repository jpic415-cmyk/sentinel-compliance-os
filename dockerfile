FROM python:3.11-slim
WORKDIR /app
RUN pip install google-genai
COPY standalone_dashboard.py /app/
RUN mkdir -p /app/proof_uploads
EXPOSE 8080
CMD ["python", "standalone_dashboard.py"]
