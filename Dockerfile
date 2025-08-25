# syntax=docker/dockerfile:1

# Base image
FROM python:3.13-slim

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.3

# Set work directory
WORKDIR /code

# Install system dependencies (build tools, PostgreSQL client libs, Pillow image libs, curl for Poetry)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       bash \
       build-essential \
       libpq-dev \
       curl \
       libjpeg62-turbo-dev \
       zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry \
    && poetry --version

# Copy dependency files first for smarter caching
COPY pyproject.toml poetry.lock* ./

# Configure Poetry to install into the system environment (no venv) and install deps
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Copy project
COPY . .

# Expose port (django dev server)
EXPOSE 8000

# Default command (docker-compose overrides this)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
