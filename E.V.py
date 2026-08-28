#!/usr/bin/env python3

"""
E.V. // Enhanced Virtuality

Personal hybrid AI assistant with:
- Gemini cloud inference
- Local Qwen GGUF inference through llama-cli
- Automatic provider fallback
- Persistent local memory
- Configurable personality
- Nebula terminal UI
- Optional Oh My Logo asset
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import textwrap
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import requests


# ============================================================
# E.V. // ENVIRONMENT LOADING
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parent


def load_env_file(path: Path) -> None:
    """
    Load a simple .env file without requiring python-dotenv.

    Existing process environment variables always win.
    """

    if not path.is_file():
        return

    try:
        content = path.read_text(
            encoding="utf-8"
        )
    except OSError:
        return

    for raw_line in content.splitlines():

        line = raw_line.strip()

        if not line:
            continue

        if line.startswith("#"):
            continue

        if "=" not in line:
            continue

        key, value = line.split(
            "=",
            1,
        )

        key = key.strip()
        value = value.strip()

        if not key:
            continue

        # Never overwrite an already-exported environment value.
        if key in os.environ:
            continue

        # Remove matching quotes.
        if (
            len(value) >= 2
            and value[0] == value[-1]
            and value[0] in {"'", '"'}
        ):
            value = value[1:-1]

        os.environ[key] = value


load_env_file(
    PROJECT_DIR / ".env"
)


# ============================================================
# E.V. // IDENTITY
# ============================================================

APP_NAME = "E.V."
APP_FULL_NAME = "Enhanced Virtuality"

APP_VERSION = os.getenv(
    "EV_VERSION",
    "2.0.0",
)


# ============================================================
# E.V. // PATHS
# ============================================================

ROOT = Path(
    os.getenv(
        "JARVIS_HOME",
        str(Path.home() / "jarvis"),
    )
).expanduser()

MODEL_FILE = Path(
    os.getenv(
        "JARVIS_MODEL_FILE",
        str(
            ROOT
            / "models"
            / "Qwen2.5-3B-Instruct-Q4_K_M.gguf"
        ),
    )
).expanduser()

MEMORY_FILE = Path(
    os.getenv(
        "JARVIS_MEMORY_FILE",
        str(ROOT / "memory.json"),
    )
).expanduser()

PERSONALITY_FILE = Path(
    os.getenv(
        "JARVIS_PERSONALITY_FILE",
        str(ROOT / "personality.txt"),
    )
).expanduser()

LOGO_FILE = Path(
    os.getenv(
        "JARVIS_LOGO_FILE",
        str(
            PROJECT_DIR
            / "assets"
            / "ev_logo.txt"
        ),
    )
).expanduser()


# ============================================================
# E.V. // AI CONFIGURATION
# ============================================================

DEFAULT_THREADS = os.getenv(
    "JARVIS_THREADS",
    str(
        min(
            6,
            os.cpu_count() or 6,
        )
    ),
)

DEFAULT_CTX = os.getenv(
    "JARVIS_CTX",
    "2048",
)

DEFAULT_TOKENS = os.getenv(
    "JARVIS_MAX_TOKENS",
    "256",
)

DEFAULT_TEMPERATURE = os.getenv(
    "JARVIS_TEMPERATURE",
    "0.7",
)

QWEN_TIMEOUT = int(
    os.getenv(
        "JARVIS_QWEN_TIMEOUT",
        "180",
    )
)

GEMINI_TIMEOUT = int(
    os.getenv(
        "JARVIS_GEMINI_TIMEOUT",
        "60",
    )
)

NETWORK_TIMEOUT = float(
    os.getenv(
        "JARVIS_NETWORK_TIMEOUT",
        "3",
    )
)

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash",
)

GEMINI_BASE_URL = os.getenv(
    "GEMINI_BASE_URL",
    "https://generativelanguage.googleapis.com/v1beta",
)


# ============================================================
# E.V. // FALLBACK PERSONALITY
# ============================================================

DEFAULT_PERSONALITY = """You are E.V., short for Enhanced Virtuality.

You are a capable personal AI assistant.

Be friendly, witty, calm, and confident.
Speak naturally and clearly.
Keep simple answers concise.
Give detailed explanations when the user asks for them.

Never claim to have performed an action unless you actually performed it.
Never invent information.
Never claim access to files, devices, accounts, or services you cannot access.

When the user asks for a terminal command, provide it clearly.
Use conversation history and memory when relevant.
"""


# ============================================================
# E.V. // TERMINAL COLORS
# ============================================================

ESC = "\033["

RESET = f"{ESC}0m"

ANSI = {
    "reset": RESET,
    "bold": f"{ESC}1m",
    "dim": f"{ESC}2m",
    "black": f"{ESC}30m",
    "white": f"{ESC}38;5;255m",
    "gray": f"{ESC}38;5;245m",
    "cyan": f"{ESC}38;5;117m",
    "blue": f"{ESC}38;5;111m",
    "purple": f"{ESC}38;5;141m",
    "magenta": f"{ESC}38;5;207m",
    "pink": f"{ESC}38;5;212m",
    "green": f"{ESC}38;5;114m",
    "yellow": f"{ESC}38;5;221m",
    "red": f"{ESC}38;5;203m",
}


# ============================================================
# E.V. // NERD FONT GLYPHS
# ============================================================

GLYPHS = {
    "core": "󰘧",
    "brain": "󰧑",
    "network": "󰖩",
    "cpu": "󰍛",
    "memory": "󰘚",
    "terminal": "",
    "spark": "✦",
    "diamond": "◆",
    "chevron": "",
    "arrow": "➜",
    "check": "✓",
    "cross": "✗",
    "dot": "●",
    "bolt": "󰐷",
}


FALLBACK_GLYPHS = {
    "core": "◎",
    "brain": "◈",
    "network": "⌁",
    "cpu": "▣",
    "memory": "▤",
    "terminal": ">_",
    "spark": "✦",
    "diamond": "◆",
    "chevron": ">",
    "arrow": "→",
    "check": "✓",
    "cross": "✗",
    "dot": "•",
    "bolt": "⚡",
}


def glyph(name: str) -> str:
    """
    Return a Nerd Font glyph when enabled,
    otherwise use a safe Unicode fallback.
    """

    use_nerd = os.getenv(
        "JARVIS_NERD_FONT",
        "true",
    ).strip().lower() not in {
        "0",
        "false",
        "no",
        "off",
    }

    if use_nerd:
        return GLYPHS.get(
            name,
            FALLBACK_GLYPHS.get(
                name,
                "•",
            ),
        )

    return FALLBACK_GLYPHS.get(
        name,
        "•",
    )


# ============================================================
# E.V. // MASCOT
# ============================================================

MASCOT = [
    "👾",
]


# ============================================================
# E.V. // REQUEST SESSION
# ============================================================

session = requests.Session()

session.headers.update(
    {
        "User-Agent": (
            "EV-Enhanced-Virtuality/"
            f"{APP_VERSION}"
        )
    }
)


# ============================================================
# E.V. // COLOR HELPERS
# ============================================================

def color(
    text: str,
    name: str,
) -> str:

    return (
        f"{ANSI.get(name, '')}"
        f"{text}"
        f"{RESET}"
    )


def rgb(
    text: str,
    red_value: int,
    green_value: int,
    blue_value: int,
    bold: bool = False,
) -> str:

    prefix = (
        f"{ESC}"
        f"{'1;' if bold else ''}"
        f"38;2;"
        f"{red_value};"
        f"{green_value};"
        f"{blue_value}m"
    )

    return (
        prefix
        + text
        + RESET
    )


def gradient(
    text: str,
    start: Tuple[int, int, int] = (
        175,
        87,
        255,
    ),
    end: Tuple[int, int, int] = (
        62,
        218,
        255,
    ),
) -> str:

    if not text:
        return ""

    length = len(text)

    if length == 1:
        return rgb(
            text,
            *start,
            bold=True,
        )

    result = []

    for index, character in enumerate(text):

        ratio = index / (
            length - 1
        )

        red_value = int(
            start[0]
            + (
                end[0]
                - start[0]
            )
            * ratio
        )

        green_value = int(
            start[1]
            + (
                end[1]
                - start[1]
            )
            * ratio
        )

        blue_value = int(
            start[2]
            + (
                end[2]
                - start[2]
            )
            * ratio
        )

        result.append(
            rgb(
                character,
                red_value,
                green_value,
                blue_value,
                bold=True,
            )
        )

    return "".join(
        result
    )


# ============================================================
# E.V. // TERMINAL HELPERS
# ============================================================

def terminal_dimensions() -> Tuple[int, int]:

    size = shutil.get_terminal_size(
        fallback=(100, 30)
    )

    return (
        max(
            size.columns,
            60,
        ),
        max(
            size.lines,
            20,
        ),
    )


def terminal_width() -> int:
    return terminal_dimensions()[0]


def center_text(
    text: str,
) -> str:

    width = terminal_width()

    if len(text) >= width:
        return text

    return (
        " "
        * max(
            0,
            (
                width
                - len(text)
            )
            // 2,
        )
        + text
    )


def clear_screen() -> None:

    command = (
        "cls"
        if os.name == "nt"
        else "clear"
    )

    try:

        subprocess.run(
            command,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )

    except OSError:

        print(
            "\n" * 4
        )


# ============================================================
# E.V. // BOX RENDERING
# ============================================================

def fit_line(
    text: str,
    width: int,
) -> str:

    plain_width = max(
        width - 4,
        1,
    )

    if len(text) <= plain_width:
        return text

    return (
        text[
            : max(
                plain_width - 3,
                1,
            )
        ]
        + "..."
    )


def boxed(
    title: str,
    lines: Sequence[str],
    width: Optional[int] = None,
) -> List[str]:

    target_width = width or min(
        max(
            terminal_width() - 8,
            54,
        ),
        96,
    )

    inner_width = (
        target_width - 2
    )

    title_text = (
        f" {title} "
    )

    if len(title_text) > inner_width:
        title_text = title_text[
            :inner_width
        ]

    top_remaining = max(
        inner_width
        - len(title_text),
        0,
    )

    left_border = (
        "╭"
        + "─"
        * (top_remaining // 2)
        + title_text
        + "─"
        * (
            top_remaining
            - (
                top_remaining
                // 2
            )
        )
        + "╮"
    )

    bottom_border = (
        "╰"
        + "─"
        * inner_width
        + "╯"
    )

    rendered = [
        color(
            left_border,
            "purple",
        )
    ]

    for item in lines:

        line = fit_line(
            str(item),
            target_width,
        )

        rendered.append(
            color(
                "│",
                "purple",
            )
            + " "
            + line.ljust(
                target_width - 3
            )
            + " "
            + color(
                "│",
                "purple",
            )
        )

    rendered.append(
        color(
            bottom_border,
            "purple",
        )
    )

    return rendered


def print_box(
    title: str,
    lines: Sequence[str],
    width: Optional[int] = None,
) -> None:

    for line in boxed(
        title,
        lines,
        width,
    ):
        print(
            center_text(
                line
            )
        )


# ============================================================
# E.V. // LOGO
# ============================================================

FALLBACK_LOGO = [
    "        ✦             ·              ✧",
    "",
    "             ███████╗ ██╗   ██╗",
    "             ██╔════╝ ██║   ██║",
    "             █████╗   ██║   ██║",
    "             ██╔══╝   ╚██╗ ██╔╝",
    "             ███████╗  ╚████╔╝",
    "             ╚══════╝   ╚═══╝",
    "",
    "                    E . V .",
    "",
    "            ENHANCED VIRTUALITY",
    "",
    "        ✧             ·              ✦",
]


def load_logo() -> List[str]:

    possible_files = [
        LOGO_FILE,
        PROJECT_DIR
        / "assets"
        / "ev_logo.txt",
    ]

    for path in possible_files:

        try:

            if not path.is_file():
                continue

            contents = (
                path.read_text(
                    encoding="utf-8"
                )
                .strip()
            )

            if contents:
                return contents.splitlines()

        except OSError:
            continue

    return FALLBACK_LOGO


def print_logo() -> None:

    logo = load_logo()

    palette = [
        (153, 78, 255),
        (171, 82, 255),
        (192, 91, 255),
        (131, 145, 255),
        (84, 201, 255),
        (70, 222, 255),
        (84, 201, 255),
        (131, 145, 255),
        (192, 91, 255),
        (171, 82, 255),
        (153, 78, 255),
    ]

    for index, line in enumerate(logo):

        current_color = palette[
            index
            % len(palette)
        ]

        print(
            center_text(
                rgb(
                    line,
                    *current_color,
                    bold=True,
                )
            )
        )

        time.sleep(
            0.015
        )


def print_mascot() -> None:

    mascot_palette = [
        "purple",
        "magenta",
        "cyan",
        "blue",
        "magenta",
        "purple",
    ]

    for index, line in enumerate(
        MASCOT
    ):

        print(
            center_text(
                color(
                    line,
                    mascot_palette[
                        index
                        % len(
                            mascot_palette
                        )
                    ],
                )
            )
        )


# ============================================================
# E.V. // STATUS HELPERS
# ============================================================

def gemini_key_present() -> bool:
    return bool(
        os.getenv(
            "GEMINI_API_KEY",
            "",
        ).strip()
    )


def find_llama_cli() -> Optional[str]:

    configured = os.getenv(
        "JARVIS_LLAMA_CLI",
        "",
    ).strip()

    if configured:

        possible_path = Path(
            configured
        ).expanduser()

        if possible_path.is_file():
            return str(
                possible_path
            )

        discovered = shutil.which(
            configured
        )

        if discovered:
            return discovered

        return None

    return shutil.which(
        "llama-cli"
    )


def qwen_model_present() -> bool:

    return MODEL_FILE.is_file()


def qwen_ready() -> bool:

    return (
        qwen_model_present()
        and find_llama_cli()
        is not None
    )


def internet_available() -> bool:

    try:

        response = session.get(
            "https://generativelanguage.googleapis.com",
            timeout=NETWORK_TIMEOUT,
        )

        return response.status_code < 500

    except requests.RequestException:
        return False


def readiness(
    ready: bool,
) -> str:

    return (
        color(
            "READY",
            "green",
        )
        if ready
        else color(
            "MISSING",
            "yellow",
        )
    )


# ============================================================
# E.V. // STARTUP
# ============================================================

def startup() -> None:

    clear_screen()

    print()

    print(
        center_text(
            gradient(
                "E . V .",
            )
        )
    )

    print(
        center_text(
            color(
                "ENHANCED VIRTUALITY",
                "dim",
            )
        )
    )

    print()

    startup_checks = [
        (
            glyph("check"),
            "neural interface",
        ),
        (
            glyph("check"),
            "memory core",
        ),
        (
            glyph("check"),
            "personality matrix",
        ),
        (
            glyph("check"),
            "Gemini interface",
        ),
        (
            glyph("check"),
            "Qwen interface",
        ),
        (
            glyph("check"),
            "terminal renderer",
        ),
    ]

    for icon, label in startup_checks:

        print(
            center_text(
                color(
                    f"{icon} {label:<24} ONLINE",
                    "white",
                )
            )
        )

        time.sleep(
            0.035
        )

    print()

    print_logo()

    print()

    print_mascot()

    print()

    print_box(
        "E.V. // CORE ONLINE",
        [
            (
                f"{glyph('core')} identity      : "
                f"{APP_FULL_NAME}"
            ),
            (
                f"{glyph('brain')} local brain   : "
                "Qwen 2.5 3B"
            ),
            (
                f"{glyph('network')} cloud brain   : "
                "Gemini"
            ),
            (
                f"{glyph('terminal')} interface     : "
                "terminal"
            ),
            (
                f"{glyph('spark')} version       : "
                f"{APP_VERSION}"
            ),
        ],
    )

    print()

    print(
        center_text(
            color(
                "◆  ALL SYSTEMS NOMINAL  ◆",
                "cyan",
            )
        )
    )

    print(
        center_text(
            color(
                "type /help to open the command matrix",
                "dim",
            )
        )
    )

    print()


# ============================================================
# E.V. // JSON + MEMORY
# ============================================================

def load_json(
    path: Path,
    default: Any,
) -> Any:

    try:

        if not path.is_file():
            return default

        return json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

    except (
        OSError,
        json.JSONDecodeError,
        TypeError,
        ValueError,
    ):

        return default


def save_json(
    path: Path,
    obj: Any,
) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            obj,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def load_personality() -> str:

    try:

        if PERSONALITY_FILE.is_file():

            content = (
                PERSONALITY_FILE
                .read_text(
                    encoding="utf-8"
                )
                .strip()
            )

            if content:
                return content

    except OSError:
        pass

    return DEFAULT_PERSONALITY.strip()


def normalize_memory(
    raw: Any,
) -> Dict[str, List[str]]:

    if not isinstance(
        raw,
        dict,
    ):
        return {
            "facts": []
        }

    facts = raw.get(
        "facts",
        [],
    )

    if not isinstance(
        facts,
        list,
    ):
        facts = []

    cleaned = []

    for fact in facts:

        value = str(
            fact
        ).strip()

        if value:
            cleaned.append(
                value
            )

    return {
        "facts": cleaned
    }


def save_memory(
    memory: Dict[str, List[str]],
) -> bool:

    try:

        save_json(
            MEMORY_FILE,
            memory,
        )

        return True

    except OSError as exc:

        print_box(
            "MEMORY ERROR",
            [
                (
                    f"{glyph('cross')} "
                    f"{exc}"
                )
            ],
        )

        return False


def build_memory_context(
    memory: Dict[str, List[str]],
) -> str:

    facts = memory.get(
        "facts",
        [],
    )

    if not facts:
        return "None"

    return "\n".join(
        f"- {fact}"
        for fact in facts[-20:]
    )


def build_chat_history(
    history: Sequence[
        Dict[str, str]
    ],
) -> str:

    if not history:
        return "None"

    lines = []

    for item in history[-12:]:

        role = (
            "User"
            if item.get("role")
            == "user"
            else "E.V."
        )

        text = item.get(
            "text",
            "",
        )

        lines.append(
            f"{role}: {text}"
        )

    return "\n".join(
        lines
    )


# ============================================================
# E.V. // PROMPT
# ============================================================

def build_prompt(
    user_text: str,
    memory: Dict[str, List[str]],
    personality: str,
    history: Sequence[
        Dict[str, str]
    ],
) -> str:

    return textwrap.dedent(
        f"""
        {personality}

        Known memory:
        {build_memory_context(memory)}

        Recent conversation:
        {build_chat_history(history)}

        User: {user_text}
        E.V.:
        """
    ).strip()


# ============================================================
# E.V. // GEMINI
# ============================================================

def parse_gemini_response(
    data: Any,
) -> Tuple[
    Optional[str],
    Optional[str],
]:

    if not isinstance(
        data,
        dict,
    ):
        return (
            None,
            "Invalid Gemini response",
        )

    candidates = data.get(
        "candidates"
    )

    if (
        isinstance(
            candidates,
            list,
        )
        and candidates
    ):

        candidate = candidates[0]

        if isinstance(
            candidate,
            dict,
        ):

            content = candidate.get(
                "content",
                {},
            )

            if isinstance(
                content,
                dict,
            ):

                parts = content.get(
                    "parts",
                    [],
                )

                if isinstance(
                    parts,
                    list,
                ):

                    texts = []

                    for part in parts:

                        if not isinstance(
                            part,
                            dict,
                        ):
                            continue

                        text = part.get(
                            "text"
                        )

                        if (
                            isinstance(
                                text,
                                str,
                            )
                            and text.strip()
                        ):

                            texts.append(
                                text
                            )

                    if texts:
                        return (
                            "".join(
                                texts
                            ).strip(),
                            None,
                        )

            reason = candidate.get(
                "finishReason"
            )

            if reason:

                return (
                    None,
                    (
                        "Gemini returned "
                        "no text "
                        f"(finish reason: "
                        f"{reason})"
                    ),
                )

        return (
            None,
            "Gemini returned an empty response",
        )

    error_data = data.get(
        "error"
    )

    if isinstance(
        error_data,
        dict,
    ):

        message = str(
            error_data.get(
                "message",
                "Unknown Gemini error",
            )
        )

        code = error_data.get(
            "code"
        )

        if code:
            message = (
                f"{message} "
                f"(HTTP {code})"
            )

        return (
            None,
            message,
        )

    return (
        None,
        "Unknown Gemini response",
    )


def ask_gemini(
    user_text: str,
    memory: Dict[str, List[str]],
    personality: str,
    history: Sequence[
        Dict[str, str]
    ],
) -> Tuple[
    Optional[str],
    Optional[str],
]:

    api_key = os.getenv(
        "GEMINI_API_KEY",
        "",
    ).strip()

    if not api_key:

        return (
            None,
            "GEMINI_API_KEY is not set",
        )

    endpoint = (
        f"{GEMINI_BASE_URL.rstrip('/')}"
        f"/models/{GEMINI_MODEL}"
        ":generateContent"
    )

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": build_prompt(
                            user_text,
                            memory,
                            personality,
                            history,
                        )
                    }
                ],
            }
        ]
    }

    try:

        response = session.post(
            endpoint,
            params={
                "key": api_key,
            },
            headers={
                "Content-Type":
                    "application/json",
            },
            json=payload,
            timeout=GEMINI_TIMEOUT,
        )

        try:

            data = response.json()

        except ValueError:

            return (
                None,
                (
                    "Gemini returned "
                    "invalid JSON "
                    f"(HTTP "
                    f"{response.status_code})"
                ),
            )

        if not response.ok:

            _, error = (
                parse_gemini_response(
                    data
                )
            )

            return (
                None,
                error
                or (
                    "Gemini request "
                    "failed "
                    f"(HTTP "
                    f"{response.status_code})"
                ),
            )

        return parse_gemini_response(
            data
        )

    except requests.Timeout:

        return (
            None,
            "Gemini request timed out",
        )

    except requests.ConnectionError:

        return (
            None,
            "Unable to connect to Gemini",
        )

    except requests.RequestException as exc:

        return (
            None,
            f"Gemini network error: {exc}",
        )

    except Exception as exc:

        return (
            None,
            f"Gemini error: {exc}",
        )


# ============================================================
# E.V. // QWEN
# ============================================================

def extract_llama_answer(
    stdout: str,
) -> str:

    if not stdout:
        return ""

    lines = stdout.splitlines()

    prompt_indices = [
        index
        for index, line
        in enumerate(lines)
        if line.lstrip().startswith(
            ">"
        )
    ]

    if not prompt_indices:

        cleaned = []

        for line in lines:

            stripped = line.strip()

            if not stripped:
                continue

            lowered = stripped.lower()

            if lowered.startswith(
                "llama_"
            ):
                continue

            cleaned.append(
                line
            )

        return "\n".join(
            cleaned[-12:]
        ).strip()

    start = (
        prompt_indices[-1]
        + 1
    )

    answer_lines = []

    for line in lines[start:]:

        stripped = line.strip()

        if line.startswith(
            "[ Prompt:"
        ):
            break

        if line.lstrip().startswith(
            ">"
        ):
            break

        if stripped:
            answer_lines.append(
                line
            )

    return "\n".join(
        answer_lines
    ).strip()


def ask_qwen(
    user_text: str,
    memory: Dict[str, List[str]],
    personality: str,
    history: Sequence[
        Dict[str, str]
    ],
    threads: str,
) -> Tuple[
    Optional[str],
    Optional[str],
]:

    if not MODEL_FILE.is_file():

        return (
            None,
            f"Model not found: {MODEL_FILE}",
        )

    llama_cli = find_llama_cli()

    if llama_cli is None:

        return (
            None,
            (
                "llama-cli was not "
                "found in PATH. "
                "Set "
                "JARVIS_LLAMA_CLI "
                "if needed."
            ),
        )

    prompt = build_prompt(
        user_text,
        memory,
        personality,
        history,
    )

    command = [
        llama_cli,
        "-m",
        str(MODEL_FILE),
        "-p",
        prompt,
        "-n",
        str(DEFAULT_TOKENS),
        "-c",
        str(DEFAULT_CTX),
        "-t",
        str(threads),
        "--temp",
        str(DEFAULT_TEMPERATURE),
    ]

    try:

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=QWEN_TIMEOUT,
        )

    except subprocess.TimeoutExpired:

        return (
            None,
            (
                "Qwen timed out after "
                f"{QWEN_TIMEOUT} seconds"
            ),
        )

    except FileNotFoundError:

        return (
            None,
            f"Unable to execute: {llama_cli}",
        )

    except PermissionError:

        return (
            None,
            f"Permission denied: {llama_cli}",
        )

    except OSError as exc:

        return (
            None,
            f"Unable to start Qwen: {exc}",
        )

    except Exception as exc:

        return (
            None,
            f"Qwen error: {exc}",
        )

    answer = extract_llama_answer(
        result.stdout
    )

    if answer:
        return (
            answer,
            None,
        )

    stderr = (
        result.stderr.strip()
    )

    if stderr:

        return (
            None,
            stderr,
        )

    if result.returncode != 0:

        return (
            None,
            (
                "llama-cli exited "
                f"with code "
                f"{result.returncode}"
            ),
        )

    return (
        None,
        "Qwen returned an empty response",
    )


# ============================================================
# E.V. // PROVIDER ROUTING
# ============================================================

def choose_mode(
    runtime_mode: str,
) -> str:

    if runtime_mode in {
        "gemini",
        "qwen",
    }:

        return runtime_mode

    if (
        gemini_key_present()
        and internet_available()
    ):

        return "gemini"

    return "qwen"


def request_ai(
    prompt: str,
    state: Dict[str, Any],
    personality: str,
) -> Tuple[
    Optional[str],
    Optional[str],
    Optional[str],
]:

    selected_mode = choose_mode(
        state["mode"]
    )

    memory = state["memory"]
    history = state["history"]
    threads = state["threads"]

    if selected_mode == "gemini":

        print(
            center_text(
                color(
                    (
                        f"╭─ "
                        f"{glyph('network')} "
                        "E.V. // GEMINI "
                        "─╮"
                    ),
                    "purple",
                )
            )
        )

        answer, error = ask_gemini(
            prompt,
            memory,
            personality,
            history,
        )

        if answer is not None:

            return (
                answer,
                "gemini",
                None,
            )

        print(
            center_text(
                color(
                    (
                        f"│ "
                        f"{glyph('cross')} "
                        f"Gemini failed: "
                        f"{error}"
                    ),
                    "red",
                )
            )
        )

        if qwen_ready():

            print(
                center_text(
                    color(
                        (
                            "╰─ "
                            f"{glyph('arrow')} "
                            "falling back "
                            "to local Qwen "
                            "─╯"
                        ),
                        "blue",
                    )
                )
            )

            answer, qwen_error = (
                ask_qwen(
                    prompt,
                    memory,
                    personality,
                    history,
                    threads,
                )
            )

            if answer is not None:

                return (
                    answer,
                    "qwen",
                    None,
                )

            return (
                None,
                "qwen",
                qwen_error,
            )

        return (
            None,
            "gemini",
            error,
        )

    print(
        center_text(
            color(
                (
                    f"╭─ "
                    f"{glyph('brain')} "
                    "E.V. // QWEN "
                    "─╮"
                ),
                "blue",
            )
        )
    )

    answer, qwen_error = ask_qwen(
        prompt,
        memory,
        personality,
        history,
        threads,
    )

    if answer is not None:

        return (
            answer,
            "qwen",
            None,
        )

    print(
        center_text(
            color(
                (
                    f"│ "
                    f"{glyph('cross')} "
                    f"Qwen failed: "
                    f"{qwen_error}"
                ),
                "red",
            )
        )
    )

    if (
        gemini_key_present()
        and internet_available()
    ):

        print(
            center_text(
                color(
                    (
                        "╰─ "
                        f"{glyph('arrow')} "
                        "falling back "
                        "to Gemini "
                        "─╯"
                    ),
                    "purple",
                )
            )
        )

        answer, gemini_error = (
            ask_gemini(
                prompt,
                memory,
                personality,
                history,
            )
        )

        if answer is not None:

            return (
                answer,
                "gemini",
                None,
            )

        return (
            None,
            "gemini",
            gemini_error,
        )

    return (
        None,
        "qwen",
        qwen_error,
    )


# ============================================================
# E.V. // STATUS
# ============================================================

def print_status(
    mode: str,
    threads: str,
) -> None:

    gemini_ready = (
        gemini_key_present()
    )

    network_ready = (
        internet_available()
    )

    qwen_model_ready = (
        qwen_model_present()
    )

    llama_ready = (
        find_llama_cli()
        is not None
    )

    print_box(
        "SYSTEM STATUS",
        [
            (
                f"{glyph('core')} core         : "
                f"{color('ONLINE', 'green')}"
            ),
            (
                f"{glyph('network')} network      : "
                f"{'online' if network_ready else 'offline'}"
            ),
            (
                f"{glyph('network')} Gemini       : "
                f"{readiness(gemini_ready)}"
            ),
            (
                f"{glyph('brain')} Qwen model   : "
                f"{readiness(qwen_model_ready)}"
            ),
            (
                f"{glyph('terminal')} llama-cli    : "
                f"{readiness(llama_ready)}"
            ),
            (
                f"{glyph('diamond')} mode         : "
                f"{mode}"
            ),
            (
                f"{glyph('cpu')} threads      : "
                f"{threads}"
            ),
            (
                f"{glyph('brain')} context      : "
                f"{DEFAULT_CTX}"
            ),
            (
                f"{glyph('arrow')} max tokens   : "
                f"{DEFAULT_TOKENS}"
            ),
            (
                f"{glyph('spark')} temperature  : "
                f"{DEFAULT_TEMPERATURE}"
            ),
            (
                f"{glyph('diamond')} version      : "
                f"{APP_VERSION}"
            ),
        ],
    )


# ============================================================
# E.V. // COMMANDS
# ============================================================

def handle_command(
    command: str,
    state: Dict[str, Any],
) -> bool:

    parts = (
        command
        .strip()
        .split(
            maxsplit=1
        )
    )

    if not parts:
        return True

    cmd = parts[0].lower()

    # --------------------------------------------------------
    # EXIT
    # --------------------------------------------------------

    if cmd in {
        "/exit",
        "/quit",
    }:

        raise KeyboardInterrupt

    # --------------------------------------------------------
    # CLEAR
    # --------------------------------------------------------

    if cmd in {
        "/clear",
        "/reset",
    }:

        state[
            "history"
        ].clear()

        clear_screen()
        print_logo()

        print()

        print_box(
            "SESSION",
            [
                (
                    f"{glyph('check')} "
                    "conversation cleared"
                )
            ],
        )

        print()

        return True

    # --------------------------------------------------------
    # MODEL
    # --------------------------------------------------------

    if cmd == "/model":

        if len(parts) == 1:

            print_box(
                "MODEL CONTROL",
                [
                    (
                        f"{glyph('diamond')} "
                        f"current: "
                        f"{state['mode']}"
                    ),
                    (
                        f"{glyph('chevron')} "
                        "/model auto"
                    ),
                    (
                        f"{glyph('chevron')} "
                        "/model gemini"
                    ),
                    (
                        f"{glyph('chevron')} "
                        "/model qwen"
                    ),
                ],
            )

            return True

        value = (
            parts[1]
            .strip()
            .lower()
        )

        if value in {
            "auto",
            "gemini",
            "qwen",
        }:

            state[
                "mode"
            ] = value

            print(
                center_text(
                    color(
                        (
                            f"{glyph('check')} "
                            f"model mode "
                            f"→ {value}"
                        ),
                        "green",
                    )
                )
            )

        else:

            print(
                center_text(
                    color(
                        (
                            f"{glyph('cross')} "
                            "valid modes: "
                            "auto, gemini, qwen"
                        ),
                        "red",
                    )
                )
            )

        return True

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    if cmd == "/status":

        print_status(
            state["mode"],
            state["threads"],
        )

        return True

    # --------------------------------------------------------
    # MEMORY
    # --------------------------------------------------------

    if cmd == "/memory":

        facts = state[
            "memory"
        ].get(
            "facts",
            [],
        )

        if not facts:

            print_box(
                "E.V. MEMORY",
                [
                    (
                        f"{glyph('dot')} "
                        "memory is empty"
                    )
                ],
            )

        else:

            memory_lines = []

            for index, fact in enumerate(
                facts,
                1,
            ):

                memory_lines.append(
                    f"{index:02d}  {fact}"
                )

            print_box(
                "E.V. MEMORY",
                memory_lines,
            )

        return True

    # --------------------------------------------------------
    # REMEMBER
    # --------------------------------------------------------

    if cmd == "/remember":

        if (
            len(parts) == 1
            or not parts[1].strip()
        ):

            print(
                center_text(
                    color(
                        (
                            f"{glyph('cross')} "
                            "usage: "
                            "/remember <fact>"
                        ),
                        "red",
                    )
                )
            )

            return True

        fact = parts[1].strip()

        state[
            "memory"
        ].setdefault(
            "facts",
            [],
        ).append(
            fact
        )

        if save_memory(
            state["memory"]
        ):

            print(
                center_text(
                    color(
                        (
                            f"{glyph('check')} "
                            "memory saved"
                        ),
                        "green",
                    )
                )
            )

        return True

    # --------------------------------------------------------
    # FORGET
    # --------------------------------------------------------

    if cmd == "/forget":

        if (
            len(parts) == 1
            or not parts[1].strip()
        ):

            print(
                center_text(
                    color(
                        (
                            f"{glyph('cross')} "
                            "usage: "
                            "/forget <number> "
                            "| /forget all"
                        ),
                        "red",
                    )
                )
            )

            return True

        target = (
            parts[1]
            .strip()
            .lower()
        )

        facts = state[
            "memory"
        ].get(
            "facts",
            [],
        )

        if target == "all":

            state[
                "memory"
            ]["facts"] = []

            save_memory(
                state["memory"]
            )

            print(
                center_text(
                    color(
                        (
                            f"{glyph('check')} "
                            "all memory cleared"
                        ),
                        "green",
                    )
                )
            )

            return True

        if target.isdigit():

            index = (
                int(target)
                - 1
            )

            if (
                0
                <= index
                < len(facts)
            ):

                removed = facts.pop(
                    index
                )

                save_memory(
                    state["memory"]
                )

                print(
                    center_text(
                        color(
                            (
                                f"{glyph('check')} "
                                f"forgot: "
                                f"{removed}"
                            ),
                            "green",
                        )
                    )
                )

            else:

                print(
                    center_text(
                        color(
                            (
                                f"{glyph('cross')} "
                                f"no memory item "
                                f"at {target}"
                            ),
                            "red",
                        )
                    )
                )

            return True

        filtered = [
            fact
            for fact in facts
            if target
            not in fact.lower()
        ]

        if (
            len(filtered)
            == len(facts)
        ):

            print(
                center_text(
                    color(
                        (
                            f"{glyph('dot')} "
                            "no matching "
                            "memory found"
                        ),
                        "yellow",
                    )
                )
            )

            return True

        state[
            "memory"
        ]["facts"] = filtered

        save_memory(
            state["memory"]
        )

        print(
            center_text(
                color(
                    (
                        f"{glyph('check')} "
                        "matching memory "
                        "removed"
                    ),
                    "green",
                )
            )
        )

        return True

    # --------------------------------------------------------
    # HELP
    # --------------------------------------------------------

    if cmd == "/help":

        print()

        print_box(
            "E.V. // COMMAND MATRIX",
            [
                (
                    f"{glyph('diamond')} "
                    "MODEL CONTROL"
                ),
                (
                    "  /model auto"
                    "       automatic "
                    "Gemini ↔ Qwen"
                ),
                (
                    "  /model gemini"
                    "     force Gemini"
                ),
                (
                    "  /model qwen"
                    "       force local Qwen"
                ),
                "",
                (
                    f"{glyph('diamond')} "
                    "MEMORY"
                ),
                (
                    "  /memory"
                    "             show memories"
                ),
                (
                    "  /remember <fact>"
                    "   save a memory"
                ),
                (
                    "  /forget <number>"
                    "   remove a memory"
                ),
                (
                    "  /forget all"
                    "        clear memory"
                ),
                "",
                (
                    f"{glyph('diamond')} "
                    "SESSION"
                ),
                (
                    "  /clear"
                    "              clear conversation"
                ),
                (
                    "  /status"
                    "             system diagnostics"
                ),
                (
                    "  /help"
                    "               show this matrix"
                ),
                (
                    "  /exit"
                    "               shut down E.V."
                ),
            ],
        )

        print()

        print_mascot()

        print()

        return True

    # --------------------------------------------------------
    # UNKNOWN
    # --------------------------------------------------------

    print(
        center_text(
            color(
                (
                    f"{glyph('cross')} "
                    "unknown command — "
                    "try /help"
                ),
                "red",
            )
        )
    )

    return True


# ============================================================
# E.V. // CHAT LOOP
# ============================================================

def run_chat(
    state: Dict[str, Any],
    personality: str,
) -> None:

    while True:

        try:

            prompt = input(
                color(
                    (
                        f"{glyph('terminal')} "
                        " You › "
                    ),
                    "cyan",
                )
            ).strip()

            if not prompt:
                continue

            if prompt.startswith("/"):
                handle_command(
                    prompt,
                    state,
                )
                continue

            print()

            answer, provider, error = (
                request_ai(
                    prompt,
                    state,
                    personality,
                )
            )

            if answer is None:

                print_box(
                    "E.V. // ERROR",
                    [
                        (
                            f"{glyph('cross')} "
                            f"provider: "
                            f"{provider or 'unknown'}"
                        ),
                        (
                            f"{glyph('cross')} "
                            f"reason: "
                            f"{error or 'unknown error'}"
                        ),
                    ],
                )

                print()

                continue

            provider_name = (
                "GEMINI"
                if provider
                == "gemini"
                else "QWEN"
            )

            provider_color = (
                "purple"
                if provider
                == "gemini"
                else "blue"
            )

            print(
                center_text(
                    color(
                        (
                            f"╭─ E.V. // "
                            f"{provider_name} ─╮"
                        ),
                        provider_color,
                    )
                )
            )

            print()

            for line in answer.splitlines():

                print(
                    color(
                        line,
                        "white",
                    )
                )

            print()

            state[
                "history"
            ].append(
                {
                    "role": "user",
                    "text": prompt,
                }
            )

            state[
                "history"
            ].append(
                {
                    "role": "assistant",
                    "text": answer,
                }
            )

            state[
                "history"
            ] = state[
                "history"
            ][-12:]

        except KeyboardInterrupt:

            print()

            print_box(
                "E.V. // OFFLINE",
                [
                    (
                        f"{glyph('spark')} "
                        "neural core standing by"
                    ),
                    (
                        f"{glyph('check')} "
                        "session terminated cleanly"
                    ),
                ],
            )

            print()

            return

        except EOFError:

            print()

            return

        except Exception as exc:

            print()

            print_box(
                "UNEXPECTED ERROR",
                [
                    (
                        f"{glyph('cross')} "
                        f"{exc}"
                    )
                ],
            )

            print()


# ============================================================
# E.V. // ARGUMENTS
# ============================================================

def build_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        description=(
            "E.V. — Enhanced Virtuality"
        )
    )

    parser.add_argument(
        "--model",
        choices=[
            "auto",
            "gemini",
            "qwen",
        ],
        default=os.getenv(
            "JARVIS_MODEL",
            "auto",
        ).lower(),
        help=(
            "choose auto, gemini, "
            "or qwen"
        ),
    )

    parser.add_argument(
        "--threads",
        default=DEFAULT_THREADS,
        help=(
            "CPU threads for local Qwen"
        ),
    )

    parser.add_argument(
        "--no-banner",
        action="store_true",
        help=(
            "skip the E.V. startup UI"
        ),
    )

    return parser


# ============================================================
# E.V. // MAIN
# ============================================================

def main() -> int:

    parser = build_parser()

    args = parser.parse_args()

    personality = load_personality()

    if not personality:
        personality = (
            DEFAULT_PERSONALITY
            .strip()
        )

    memory = normalize_memory(
        load_json(
            MEMORY_FILE,
            {
                "facts": []
            },
        )
    )

    state: Dict[
        str,
        Any,
    ] = {
        "mode": args.model,
        "threads": str(
            args.threads
        ),
        "memory": memory,
        "history": [],
    }

    if not args.no_banner:

        startup()

        print_status(
            state["mode"],
            state["threads"],
        )

        print()

    run_chat(
        state,
        personality,
    )

    return 0


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    raise SystemExit(
        main()
    )
