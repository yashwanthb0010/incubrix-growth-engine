# Dockerfile for IncuBrix Social Growth Engine & Content Pipeline
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Install system dependencies (ffmpeg for video generation, libgl for OpenCV, curl for health check)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    curl \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application directories and files
COPY src/ ./src/
COPY config/ ./config/
COPY data/ ./data/
COPY tests/ ./tests/
COPY app.py .
COPY README.md .
COPY .env.example .env

# Create output directories for assets, sources, and reports
RUN mkdir -p output/assets output/editable_sources output/reports submission

EXPOSE 8501

# Healthcheck for Streamlit service
HEALTHCHECK --interval=20s --timeout=10s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Launch the IncuBrix Creator Studio & Content Engine interface
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
