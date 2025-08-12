# Use Python 3.13 slim image
FROM python:3.13-slim

# Set working directory
WORKDIR /src

# Copy requirements file
COPY requirements.txt .

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    unzip \
    libatomic1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy application code
COPY app/ /src/app/

# Create directories for database, logs, and models
RUN mkdir -p /src/database /src/logs /src/models

# Add src directory to Python path
ENV PYTHONPATH=/src

# Set the default command
CMD ["python", "-m", "app.bot"]
