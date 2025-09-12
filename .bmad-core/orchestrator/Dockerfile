# BMAD Agent Container
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    jq \
    git \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Install Python dependencies for agents
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    sqlalchemy \
    pydantic \
    redis \
    prometheus-client \
    pytest \
    ruff \
    mypy

# Create agent script
COPY agent-runner.sh /usr/local/bin/agent-runner.sh
RUN chmod +x /usr/local/bin/agent-runner.sh

# Environment variables
ENV ARCHON_URL=http://host.docker.internal:3737
ENV WORKSPACE=/workspace
ENV BMAD_CORE=/workspace/.bmad-core

# Entry point
ENTRYPOINT ["/usr/local/bin/agent-runner.sh"]