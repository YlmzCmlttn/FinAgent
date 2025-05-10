FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including PostgreSQL development files
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    postgresql-client \
    postgresql-server-dev-all \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 20.x
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g npm@latest


# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir mcp

# Copy the application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/sample_outputs

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Run the application
#CMD ["python", "find_duplicate_lines.py", "account_names.txt"] 
#CMD ["python", "update_excel_files.py"]
CMD ["python", "main.py"]