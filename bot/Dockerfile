# Bot Dockerfile
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim

WORKDIR /app

# Copy bot package files
COPY bot/pyproject.toml bot/uv.lock ./

# Install dependencies using uv
RUN uv sync --frozen

# Copy bot source code
COPY bot/ ./bot/

# Set environment variables
ENV PYTHONPATH=/app

# Run the bot
CMD ["uv", "run", "bot/bot.py"]
