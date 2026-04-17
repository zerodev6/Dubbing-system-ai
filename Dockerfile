# Python base image ekak gannawa
FROM python:3.10-slim

# System dependencies (FFmpeg wage ewa ona unoth)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Working directory eka set karanawa
WORKDIR /app

# Requirements install karanawa
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code eka copy karanawa
COPY main.py .

# VPS eke port eka expose karanawa
EXPOSE 8080

# App eka run karanawa
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
