"""Inline keyboard buttons for the Telegram bot."""

from typing import List, Tuple


def get_start_keyboard() -> List[List[Tuple[str, str]]]:
    """Get inline keyboard for /start command."""
    return [
        [
            ("📚 Available Labs", "labs"),
            ("💻 My Scores", "scores"),
        ],
        [
            ("📊 Lab Statistics", "stats"),
            ("🏆 Top Learners", "top"),
        ],
        [
            ("❓ Help", "help"),
            ("❤️ Health Check", "health"),
        ],
    ]


def get_labs_keyboard(labs: List[dict]) -> List[List[Tuple[str, str]]]:
    """Get inline keyboard with lab buttons."""
    keyboard = []
    row = []
    
    for lab in labs[:10]:  # Max 10 buttons
        lab_id = lab.get("id", "")
        lab_title = lab.get("title", f"Lab {lab_id}")
        # Shorten title for button
        short_title = lab_title.split("—")[0].split("–")[0].strip()
        if len(short_title) > 20:
            short_title = short_title[:17] + "..."
        
        row.append((short_title, f"lab_{lab_id}"))
        
        if len(row) >= 2:  # 2 buttons per row
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    return keyboard


def get_scores_keyboard() -> List[List[Tuple[str, str]]]:
    """Get inline keyboard for scores selection."""
    return [
        [("Lab 01", "scores_lab-01"), ("Lab 02", "scores_lab-02")],
        [("Lab 03", "scores_lab-03"), ("Lab 04", "scores_lab-04")],
        [("Lab 05", "scores_lab-05"), ("Lab 06", "scores_lab-06")],
        [("Lab 07", "scores_lab-07")],
        [("🔙 Back", "back_start")],
    ]


def get_back_keyboard() -> List[List[Tuple[str, str]]]:
    """Get simple back button."""
    return [[("🔙 Back to Start", "back_start")]]


def format_keyboard_message(keyboard: List[List[Tuple[str, str]]]) -> str:
    """Format keyboard as text for --test mode."""
    lines = ["\nQuick actions:"]
    for row in keyboard:
        line = " | ".join([f"[{text}]" for text, _ in row])
        lines.append(line)
    return "\n".join(lines)
