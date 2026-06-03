# Voice RAG Bot - Multi-stage Dockerfile

FROM python:3.11-slim as base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose ports
# 8000 = FastAPI backend
# 8501 = Streamlit frontend
EXPOSE 8000 8501

# Create startup script
RUN echo '#!/bin/bash\n\
if [ "$APP_TYPE" = "backend" ]; then\n\
  uvicorn backend.main:app --host 0.0.0.0 --port 8000\n\
else\n\
  streamlit run frontend/streamlit_app.py --server.port 8501 --server.address 0.0.0.0\n\
fi' > /app/start.sh && chmod +x /app/start.sh

CMD ["/app/start.sh"]
