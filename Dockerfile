# Use official Python runtime as base image
FROM python:3.11-slim

# Install system dependencies (ffmpeg, libsndfile, etc.)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    libportaudio2 \
    libjack-jackd2-0 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r falsifeye/requirements.txt

# Create uploads directory
RUN mkdir -p /app/falsifeye/uploads

# Expose port
EXPOSE 8081

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=falsifeye/app.py

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8081/')" || exit 1

# Run Flask app
CMD ["python", "falsifeye/app.py"]
