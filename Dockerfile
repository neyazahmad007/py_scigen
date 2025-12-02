"""Dockerfile for SCIgen-py."""

FROM python:3.11-slim

# Install LaTeX and Graphviz
RUN apt-get update && apt-get install -y \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    graphviz \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy package files
COPY pyproject.toml README.md ./
COPY src/ src/
COPY tests/ tests/

# Install package
RUN pip install --no-cache-dir -e ".[dev]"

# Create output directory
RUN mkdir -p /output

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["scigen", "--help"]
