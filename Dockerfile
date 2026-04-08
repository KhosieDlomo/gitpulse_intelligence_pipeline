# Use a slim Python image to keep it lightweight
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies (needed for some Python libs)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data into the container
RUN python -m nltk.downloader punkt

# Copy the rest of your application code
COPY . .

# Create the data directory for the SQLite DB
RUN mkdir -p data

# Streamlit uses port 8501 by default
EXPOSE 8501

# Command to run the dashboard
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]