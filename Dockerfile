# Dockerfile — GT Landmarks Backend
# Build:  docker build -t gt-landmarks-backend .
# Run:    docker run -p 5001:5001 gt-landmarks-backend

FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

EXPOSE 5001

CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "4", "app:app"]
