# Stage 1: Build & install dependencies
FROM python:3.10-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install dependencies directly to system site-packages
RUN uv pip install --system --no-cache -r requirements.txt


# Stage 2: Tiny lightweight runtime image (leaves build headers/gcc behind!)
FROM python:3.10-slim

WORKDIR /app

# Copy python packages and binary tools from builder stage
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

ENTRYPOINT ["python", "main.py"]
CMD ["--help"]
