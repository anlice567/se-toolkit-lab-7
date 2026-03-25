"""Command handlers for the Telegram bot with backend integration and LLM routing."""

from typing import Callable
import httpx


def handle_start(command: str) -> str:
    """Handle /start command."""
    return """🤖 Welcome to the LMS Bot!

I can help you explore learning analytics data. Try asking:
• "What labs are available?"
• "Show me scores for lab 4"
• "Which lab has the lowest pass rate?"
• "Who are the top 5 students?"

Or use commands: /help, /health, /labs, /scores <lab>

[KEYBOARD:start]"""


def handle_help(command: str) -> str:
    """Handle /help command."""
    return """Available commands:
/start - Welcome message and bot info
/help - List all available commands
/health - Check backend connection status
/labs - List all available labs with titles
/scores <lab> - Show pass rates for a specific lab (e.g., /scores lab-04)

You can also ask questions in plain English:
• "What labs are available?"
• "Show me scores for lab 4"
• "Which lab has the lowest pass rate?"
• "Who are the top students in lab 3?"

[KEYBOARD:help]"""


def handle_health(command: str) -> str:
    """Handle /health command - calls backend."""
    from services.lms_client import LMSClient
    from config import load_config

    config = load_config()
    client = LMSClient(config["lms_api_base_url"], config["lms_api_key"])

    try:
        items = client.get_items()
        return (
            f"✅ Backend is healthy. {len(items)} items available.\n\n[KEYBOARD:back]"
        )
    except httpx.ConnectError:
        return "❌ Backend error: connection refused. Check that services are running.\n\n[KEYBOARD:back]"
    except httpx.HTTPStatusError as e:
        return f"❌ Backend error: HTTP {e.response.status_code}. The backend service may be down.\n\n[KEYBOARD:back]"
    except Exception as e:
        return f"❌ Backend error: {str(e)}\n\n[KEYBOARD:back]"
    finally:
        client.close()


def handle_labs(command: str) -> str:
    """Handle /labs command - lists labs from backend."""
    from services.lms_client import LMSClient
    from config import load_config

    config = load_config()
    client = LMSClient(config["lms_api_base_url"], config["lms_api_key"])

    try:
        items = client.get_items()
        labs = [item for item in items if item.get("type") == "lab"]

        if not labs:
            return "No labs found."

        result = "Available labs:\n"
        for lab in labs:
            title = lab.get("title", "Unknown")
            result += f"- {title}\n"
        return result.strip() + "\n\n[KEYBOARD:labs]"
    except httpx.ConnectError:
        return "❌ Backend error: connection refused.\n\n[KEYBOARD:back]"
    except httpx.HTTPStatusError as e:
        return f"❌ Backend error: HTTP {e.response.status_code}.\n\n[KEYBOARD:back]"
    except Exception as e:
        return f"❌ Backend error: {str(e)}\n\n[KEYBOARD:back]"
    finally:
        client.close()


def handle_scores(command: str) -> str:
    """Handle /scores <lab> command - shows pass rates."""
    from services.lms_client import LMSClient
    from config import load_config

    parts = command.split()
    if len(parts) < 2:
        return "Usage: /scores <lab-name>\nExample: /scores lab-04\n\n[KEYBOARD:scores]"

    lab_name = parts[1]

    config = load_config()
    client = LMSClient(config["lms_api_base_url"], config["lms_api_key"])

    try:
        data = client.get_pass_rates(lab_name)

        if not data:
            return f"No data found for lab: {lab_name}\n\n[KEYBOARD:back]"

        result = f"📊 Pass rates for {lab_name}:\n"
        for item in data:
            task = item.get("task", "Unknown")
            avg = item.get("avg_score", 0)
            attempts = item.get("attempts", 0)
            result += f"- {task}: {avg:.1f}% ({attempts} attempts)\n"

        return result.strip() + "\n\n[KEYBOARD:back]"
    except httpx.ConnectError:
        return "❌ Backend error: connection refused.\n\n[KEYBOARD:back]"
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"Lab not found: {lab_name}\n\n[KEYBOARD:back]"
        return f"❌ Backend error: HTTP {e.response.status_code}.\n\n[KEYBOARD:back]"
    except Exception as e:
        return f"❌ Backend error: {str(e)}\n\n[KEYBOARD:back]"
    finally:
        client.close()


def handle_natural_language(message: str) -> str:
    """Handle natural language queries via LLM intent router."""
    from services.llm_client import LLMClient
    from services.lms_client import LMSClient
    from services.intent_router import route
    from config import load_config

    config = load_config()

    # Check if LLM is configured
    llm_key = config.get("llm_api_key", "")
    if not llm_key or llm_key == "<llm-api-key>":
        return "LLM not configured. Please set LLM_API_KEY in .env.bot.secret"

    llm_client = LLMClient(
        config["llm_api_base_url"],
        llm_key,
        config["llm_api_model"],
    )
    lms_client = LMSClient(config["lms_api_base_url"], config["lms_api_key"])

    try:
        result = route(message, llm_client, lms_client)
        return result + "\n\n[KEYBOARD:back]"
    except httpx.ConnectError:
        return "❌ LLM service unavailable. Please try again later.\n\n[KEYBOARD:back]"
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            return (
                "❌ LLM authentication failed. Check your API key.\n\n[KEYBOARD:back]"
            )
        return f"❌ LLM error: HTTP {e.response.status_code}.\n\n[KEYBOARD:back]"
    except Exception as e:
        return f"❌ Error: {str(e)}\n\n[KEYBOARD:back]"
    finally:
        llm_client.close()
        lms_client.close()


# Command router
COMMANDS: dict[str, Callable[[str], str]] = {
    "/start": handle_start,
    "/help": handle_help,
    "/health": handle_health,
    "/labs": handle_labs,
    "/scores": handle_scores,
}


def run_command(command: str) -> str:
    """Route a command to the appropriate handler."""
    cmd_name = command.split()[0]
    cmd_name = cmd_name.split("@")[0]

    # Check if it's a known command
    handler = COMMANDS.get(cmd_name)
    if handler:
        return handler(command)

    # Otherwise, treat as natural language query
    return handle_natural_language(command)
