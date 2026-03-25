# LMS Telegram Bot - Implementation Plan

## Overview

This document outlines the implementation plan for the LMS Telegram Bot, which provides students with access to their learning management system data through a Telegram interface.

## Architecture

The bot follows a **separation of concerns** pattern:

1. **Handlers** (`bot/handlers/`) - Pure functions that take command input and return text responses. These are independent of Telegram and can be tested locally via `--test` mode.

2. **Services** (`bot/services/`) - API clients for external services (LMS backend, LLM API). These handle HTTP requests, authentication, and error handling.

3. **Bot layer** (`bot/bot.py`) - Telegram-specific code that receives updates from Telegram and routes them to handlers.

## Task Breakdown

### Task 1: Base Structure (Current)
- Create `bot.py` with `--test` mode
- Implement placeholder handlers for `/start`, `/help`, `/health`, `/labs`, `/scores`
- Set up `config.py` for environment variable loading
- Create `bot/handlers/__init__.py` with command router

### Task 2: Backend Integration
- Create `bot/services/lms_client.py` for LMS API communication
- Implement Bearer token authentication
- Connect `/labs` and `/scores` handlers to real API endpoints
- Handle API errors gracefully

### Task 3: LLM Intent Routing
- Create `bot/services/llm_client.py` for Qwen Code API
- Implement tool descriptions for each command
- Add natural language intent detection
- Allow users to ask questions like "What are my scores?" instead of `/scores`

### Task 4: Telegram Deployment
- Implement actual Telegram bot client using aiogram
- Set up webhook or polling
- Deploy to VM with Docker
- Configure environment variables securely

## Testing Strategy

- All handlers are testable via `--test` mode without Telegram
- Unit tests for service clients
- Integration tests for full bot flow

## Acceptance Criteria

- [x] `--test "/start"` returns welcome message
- [x] `--test "/help"` returns command list
- [x] `--test "/health"` returns bot status
- [ ] `/labs` returns real data from backend
- [ ] `/scores` returns real scores from backend
- [ ] Natural language queries work via LLM
- [ ] Bot runs in production on Telegram
