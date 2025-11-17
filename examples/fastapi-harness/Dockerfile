# Minimal Dockerfile for CI smoke test of the FastAPI contract validation harness
# This is NOT intended for production deployment

FROM python:3.11-slim

WORKDIR /app

# Copy only the necessary files for the harness
COPY app/ ./app/
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the application port
EXPOSE 8080

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
