# Use Python 3.11 slim image as base
FROM python:3.11-slim AS base

# Set environment variables early for better caching
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies in a single layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip, setuptools, and wheel in a separate layer
# This layer rarely changes and will be cached
RUN pip install --no-cache-dir --upgrade \
    pip==24.0 \
    setuptools==69.0.3 \
    wheel==0.42.0

# Copy only dependency files first
# These change less frequently than source code
COPY requirements.txt pyproject.toml ./

# Install dependencies in a separate layer
# This layer is cached unless requirements change
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code last
# This changes most frequently, so it's the last step
COPY src ./src

# Install the application in editable mode
# Since dependencies are already installed, this is fast
RUN pip install --no-cache-dir -e . --no-deps

# Set Python path
ENV PYTHONPATH=/app/src

# Expose the application port
EXPOSE 8000

# Run the application
CMD ["python", "-m", "hello_world_app.main"]
