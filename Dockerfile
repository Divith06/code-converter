# Base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system-level compilers for Go, Java, C, C++, NodeJS
RUN apt-get update && apt-get install -y \
    gcc g++ openjdk-17-jdk golang nodejs npm \
    && apt-get clean

# Copy all project files into container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Collect static files (for Django)
RUN python manage.py collectstatic --noinput || true

# Expose port 8000
EXPOSE 8000

# Run Daphne (ASGI server)
CMD ["daphne", "backend.asgi:application", "--port", "8000", "--bind", "0.0.0.0"]
