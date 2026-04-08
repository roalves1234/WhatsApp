FROM python:3.12-slim

# Install uv from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml ./

# Install dependencies (will create .venv in /app)
RUN uv sync --no-dev --no-install-project

# Copy application source code
COPY execution /app/execution

# Open Port 8000 for FastAPI
EXPOSE 8000

# Run Uvicorn directly using the env created by uv
CMD ["/app/.venv/bin/uvicorn", "execution.main:app", "--host", "0.0.0.0", "--port", "8000"]
