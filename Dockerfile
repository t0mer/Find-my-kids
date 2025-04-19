# Use Python 3.9 as base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app .

# Create necessary directories
# RUN mkdir -p /app/images/trainer /app/images/downloaded /app/config /app/classifiers && chmod -R 777 .
RUN chmod -R 777 .
# Set environment variables
ENV GREEN_API_INSTANCE=
ENV GREEN_API_TOKEN=
ENV PROBABILITY_THRESHOLD=

# Expose port for FastAPI
EXPOSE 80

# Command to run the application
# CMD ["python", "-m", "/app/app.py"] 

ENTRYPOINT python app.py