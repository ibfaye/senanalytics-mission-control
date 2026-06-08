# Sen'Analytics Mission Control — Backend Dockerfile
# FastAPI + uvicorn, with PostgreSQL, Neo4j, Redis connections

FROM python:3.13-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Create .env if not present (Docker Compose provides env vars)
RUN echo "DATABASE_URL=postgresql://senanalytics:senanalytics_dev@postgres:5432/senanalytics" > .env && \
    echo "NEO4J_URI=bolt://neo4j:7687" >> .env && \
    echo "NEO4J_USER=neo4j" >> .env && \
    echo "NEO4J_PASSWORD=senanalytics_dev" >> .env && \
    echo "REDIS_URL=redis://redis:6379" >> .env && \
    echo "HOST=0.0.0.0" >> .env && \
    echo "PORT=8001" >> .env

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8001/api/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
