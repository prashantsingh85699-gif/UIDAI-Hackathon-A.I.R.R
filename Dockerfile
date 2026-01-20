FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if any (none for now)
# RUN apt-get update && apt-get install -y gcc

# Copy requirements first to leverage cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Default command (will be overridden by docker-compose)
CMD ["bash"]
