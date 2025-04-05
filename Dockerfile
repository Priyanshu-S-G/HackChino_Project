# Dockerfile

FROM python:3.9-slim

# Environment configs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Copy everything from current dir into /app
COPY . .

# Install Python packages
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Expose Flask default port
EXPOSE 5000

# Start the Flask app
CMD ["python", "app.py"]
