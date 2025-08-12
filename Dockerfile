# Use Python 3.13 slim image
FROM python:3.13-slim

# Set working directory
WORKDIR /src

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy application code
COPY app/ /src/app/

# Create directories for database and logs
RUN mkdir -p /src/database /src/logs

# Add src directory to Python path
ENV PYTHONPATH=/src

# Set the default command
CMD ["python", "-m", "app.bot"]
