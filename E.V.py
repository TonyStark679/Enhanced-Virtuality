#!/usr/bin/env python3

import argparse
import json
import os
import shutil
import subprocess
import textwrap
import time
from pathlib import Path

import requests


# ============================================================
# E.V.
# ENHANCED VIRTUALITY
# ============================================================

APP_NAME = "E.V."
APP_FULL_NAME = "Enhanced Virtuality"

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

# Optional logo asset.
# If assets/ev_logo.txt exists, E.V. will use it.
LOGO_FILE = Path(
    os.getenv(
        "JARVIS_LOGO_FILE",
        str(ROOT / "assets" / "ev_logo.txt"),
    )
).expanduser()


# ============================================================
# CONFIGURATION
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


ANSI = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "cyan": "\033[38;5;117m",
    "blue": "\033[38;5;111m",
    "purple": "\033[38;5;141m",
    "magenta": "\033[38;5;207m",
    "green": "\033[38;5;114m",
    "yellow": "\033[38;5;221m",
    "red": "\033[38;5;203m",
    "white": "\033[38;5;255m",
}


DEFAULT_THREADS = os.getenv(
    "JARVIS_THREADS",
    str(min(6, os.cpu_count() or 6)),
)

DEFAULT_CTX = os.getenv(
    "JARVIS_CTX",
    "2048",
)

DEFAULT_TOKENS = os.getenv(
    "JARVIS_MAX_TOKENS",
    "256",
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

session = requests.Session()


# ============================================================
# TERMINAL UI
# ============================================================

def color(text: str, name: str) -> str:
    return (
        f"{ANSI.get(name, '')}"
        f"{text}"
        f"{ANSI['reset']}"
    )


def term_width() -> int:
    return shutil.get_terminal_size(
        fallback=(80, 24)
    ).columns


def center_line(text: str) -> str:
    width = term_width()

    if len(text) >= width:
        return text

    padding = max(
        0,
        (width - len(text)) // 2,
    )

    return " " * padding + text


def clear_screen() -> None:
    command = (
        "cls"
        if os.name == "nt"
        else "clear"
    )

    os.system(command)


def print_centered(
    text: str,
    style: str = "white",
) -> None:

    print(
        color(
            center_line(text),
            style,
        )
    )


# ============================================================
# NEBULA LOGO
# ============================================================

NEBULA_LOGO = [
    "             ✦       ·          ✧",
    "       ·          .       ✦",
    "",
    "              ███████╗.   ██╗   ██╗",
    "              ██╔════╝    ██║   ██║",
    "              █████╗      ██║   ██║",
    "              ██╔══╝      ╚██╗ ██╔╝",
    "              ███████╗.    ╚████╔╝",
    "              ╚══════╝      ╚═══╝",
    "",
    "                   E . V .",
    "",
    "             ✧       ·          ✦",
]


def load_logo() -> list[str]:

    try:
        if LOGO_FILE.is_file():

            content = LOGO_FILE.read_text(
                encoding="utf-8"
            ).strip()

            if content:
                return content.splitlines()

    except OSError:
        pass

    return NEBULA_LOGO


def print_logo() -> None:

    logo = load_logo()

    styles = [
        "purple",
        "magenta",
        "blue",
        "cyan",
        "blue",
        "magenta",
        "purple",
    ]

    for index, line in enumerate(logo):

        style = styles[
            index % len(styles)
        ]

        print_centered(
            line,
            style,
        )

        time.sleep(0.025)


# ============================================================
# STARTUP
# ============================================================

def banner() -> None:

    clear_screen()

    print()

    print_centered(
        "INITIALIZING E.V.",
        "cyan",
    )

    print_centered(
        "ENHANCED VIRTUALITY",
        "dim",
    )

    print()

    startup_steps = [
        (
            "[ OK ]",
            "Loading neural interface",
        ),
        (
            "[ OK ]",
            "Initializing memory core",
        ),
        (
            "[ OK ]",
            "Loading personality matrix",
        ),
        (
            "[ OK ]",
            "Checking network interface",
        ),
        (
            "[ OK ]",
            "Preparing Gemini interface",
        ),
        (
            "[ OK ]",
            "Preparing Qwen local engine",
        ),
        (
            "[ OK ]",
            "Calibrating E.V. core",
        ),
    ]

    for status, message in startup_steps:

        print(
            f"{color(status, 'green')} "
            f"{color(message, 'white')}"
        )

        time.sleep(0.07)

    print()

    print_logo()

    print()

    print_centered(
        "╭──────────────────────────────────────╮",
        "purple",
    )

    print_centered(
        "│       E . V .  //  ONLINE            │",
        "cyan",
    )

    print_centered(
        "│       ENHANCED VIRTUALITY             │",
        "dim",
    )

    print_centered(
        "╰──────────────────────────────────────╯",
        "purple",
    )

    print()


# ============================================================
# JSON / MEMORY
# ============================================================

def load_json(
    path: Path,
    default,
):

    try:

        if path.exists():

            return json.loads(
                path.read_text(
                    encoding="utf-8"
                )
            )

    except (
        OSError,
        json.JSONDecodeError,
    ):
        pass

    return default


def save_json(
    path: Path,
    obj,
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
    raw,
) -> dict:

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


def build_memory_context(
    memory: dict,
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
    history,
) -> str:

    if not history:
        return "None"

    lines = []

    for item in history[-12:]:

        role = (
            "User"
            if item["role"] == "user"
            else "E.V."
        )

        lines.append(
            f"{role}: {item['text']}"
        )

    return "\n".join(
        lines
    )


def build_prompt(
    user_text: str,
    memory: dict,
    personality: str,
    history,
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
# NETWORK
# ============================================================

def internet_available() -> bool:

    try:

        response = session.get(
            "https://generativelanguage.googleapis.com",
            timeout=NETWORK_TIMEOUT,
        )

        return (
            response.ok
            or response.status_code < 500
        )

    except requests.RequestException:
        return False


# ============================================================
# GEMINI
# ============================================================

def ask_gemini(
    user_text: str,
    memory: dict,
    personality: str,
    history,
):

    api_key = os.getenv(
        "GEMINI_API_KEY",
        "",
    ).strip()

    if not api_key:

        return (
            None,
            "GEMINI_API_KEY is not set",
        )

    url = (
        "https://generativelanguage.googleapis.com/"
        "v1beta/models/"
        f"{GEMINI_MODEL}:generateContent"
        f"?key={api_key}"
    )

    prompt = build_prompt(
        user_text,
        memory,
        personality,
        history,
    )

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": prompt
                    }
                ],
            }
        ]
    }

    try:

        response = session.post(
            url,
            json=payload,
            timeout=60,
        )

        data = response.json()

        candidates = data.get(
            "candidates",
            [],
        )

        if candidates:

            content = candidates[0].get(
                "content",
                {},
            )

            parts = content.get(
                "parts",
                [],
            )

            for part in parts:

                text = part.get(
                    "text",
                    "",
                ).strip()

                if text:
                    return (
                        text,
                        None,
                    )

        error = (
            data
            .get("error", {})
            .get(
                "message",
                "Unknown Gemini error",
            )
        )

        return (
            None,
            error,
        )

    except requests.RequestException as exc:

        return (
            None,
            str(exc),
        )

    except ValueError as exc:

        return (
            None,
            f"Invalid Gemini response: {exc}",
        )

    except Exception as exc:

        return (
            None,
            str(exc),
        )


# ============================================================
# LOCAL QWEN
# ============================================================

def find_llama_cli():

    configured = os.getenv(
        "JARVIS_LLAMA_CLI",
        "",
    ).strip()

    if configured:
        return configured

    return shutil.which(
        "llama-cli"
    )


def extract_llama_answer(
    stdout: str,
) -> str:

    if not stdout:
        return ""

    lines = stdout.splitlines()

    prompt_indices = [
        index
        for index, line in enumerate(lines)
        if line.lstrip().startswith(">")
    ]

    if not prompt_indices:

        cleaned = []

        for line in lines:

            stripped = line.strip()

            if not stripped:
                continue

            if stripped.startswith(
                "llama_"
            ):
                continue

            cleaned.append(
                line
            )

        return "\n".join(
            cleaned[-8:]
        ).strip()

    start = (
        prompt_indices[-1] + 1
    )

    answer_lines = []

    for line in lines[start:]:

        stripped = line.strip()

        if line.startswith(
            "[ Prompt:"
        ):
            break

        if line.lstrip().startswith(">"):
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
    memory: dict,
    personality: str,
    history,
    threads: str,
):

    if not MODEL_FILE.is_file():

        return (
            None,
            f"Model not found: {MODEL_FILE}",
        )

    llama_cli = find_llama_cli()

    if not llama_cli:

        return (
            None,
            "llama-cli was not found in PATH",
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
    ]

    try:

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=180,
            encoding="utf-8",
            errors="replace",
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
                "llama-cli exited with "
                f"code {result.returncode}",
            )

        return (
            None,
            "Qwen returned an empty response",
        )

    except subprocess.TimeoutExpired:

        return (
            None,
            "Qwen timed out",
        )

    except OSError as exc:

        return (
            None,
            f"Unable to start Qwen: {exc}",
        )

    except Exception as exc:

        return (
            None,
            str(exc),
        )


# ============================================================
# STATUS
# ============================================================

def print_status(
    mode: str,
    threads: str,
) -> None:

    online = internet_available()

    network = (
        "online"
        if online
        else "offline"
    )

    gemini = (
        "ready"
        if os.getenv(
            "GEMINI_API_KEY",
            "",
        ).strip()
        else "missing"
    )

    qwen_model = (
        "present"
        if MODEL_FILE.is_file()
        else "missing"
    )

    llama = (
        "ready"
        if find_llama_cli()
        else "missing"
    )

    print(
        color(
            "[status] "
            f"mode={mode} | "
            f"net={network} | "
            f"gemini={gemini} | "
            f"qwen={qwen_model} | "
            f"llama-cli={llama} | "
            f"threads={threads}",
            "dim",
        )
    )


# ============================================================
# COMMANDS
# ============================================================

def handle_command(
    command: str,
    state: dict,
) -> bool:

    parts = (
        command
        .strip()
        .split(
            maxsplit=1
        )
    )

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

        print(
            color(
                "Session cleared.",
                "green",
            )
        )

        return True

    # --------------------------------------------------------
    # MODEL
    # --------------------------------------------------------

    if cmd == "/model":

        if len(parts) == 1:

            print(
                color(
                    f"Current mode: "
                    f"{state['mode']}",
                    "yellow",
                )
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
                color(
                    f"Mode set to: {value}",
                    "green",
                )
            )

        else:

            print(
                color(
                    "Use /model auto, "
                    "/model gemini, "
                    "or /model qwen",
                    "red",
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

            print(
                color(
                    "Memory is empty.",
                    "yellow",
                )
            )

        else:

            print(
                color(
                    "E.V. Memory:",
                    "cyan",
                )
            )

            for index, fact in enumerate(
                facts,
                1,
            ):

                print(
                    color(
                        f"  {index}. {fact}",
                        "white",
                    )
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
                color(
                    "Use /remember <fact>",
                    "red",
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

        save_memory(
            state["memory"]
        )

        print(
            color(
                "Memory saved.",
                "green",
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
                color(
                    "Use /forget all "
                    "or /forget <number>",
                    "red",
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
                color(
                    "Memory cleared.",
                    "green",
                )
            )

            return True

        if target.isdigit():

            index = (
                int(target) - 1
            )

            if 0 <= index < len(facts):

                removed = facts.pop(
                    index
                )

                save_memory(
                    state["memory"]
                )

                print(
                    color(
                        f"Forgot: {removed}",
                        "green",
                    )
                )

            else:

                print(
                    color(
                        "No memory item "
                        "at that number.",
                        "red",
                    )
                )

            return True

        filtered = [
            fact
            for fact in facts
            if target not in fact.lower()
        ]

        state[
            "memory"
        ]["facts"] = filtered

        save_memory(
            state["memory"]
        )

        print(
            color(
                "Filtered memory.",
                "green",
            )
        )

        return True

    # --------------------------------------------------------
    # HELP
    # --------------------------------------------------------

    if cmd == "/help":

        print()

        print_centered(
            "╭────────────────────────────────────────────╮",
            "purple",
        )

        print_centered(
            "│             E . V .  //  HELP             │",
            "cyan",
        )

        print_centered(
            "╰────────────────────────────────────────────╯",
            "purple",
        )

        print()

        print(
            color(
                "  MODEL CONTROL",
                "magenta",
            )
        )

        print(
            "  "
            + color(
                "/model auto",
                "white",
            )
            + "      Automatic Gemini ↔ Qwen"
        )

        print(
            "  "
            + color(
                "/model gemini",
                "white",
            )
            + "    Force Gemini 🌐"
        )

        print(
            "  "
            + color(
                "/model qwen",
                "white",
            )
            + "      Force local Qwen 🧠"
        )

        print()

        print(
            color(
                "  MEMORY",
                "magenta",
            )
        )

        print(
            "  "
            + color(
                "/memory",
                "white",
            )
            + "            Show memories"
        )

        print(
            "  "
            + color(
                "/remember <fact>",
                "white",
            )
            + "  Save a memory"
        )

        print(
            "  "
            + color(
                "/forget <number>",
                "white",
            )
            + " Remove a memory"
        )

        print(
            "  "
            + color(
                "/forget all",
                "white",
            )
            + "       Clear memory"
        )

        print()

        print(
            color(
                "  SESSION",
                "magenta",
            )
        )

        print(
            "  "
            + color(
                "/clear",
                "white",
            )
            + "             Clear conversation"
        )

        print(
            "  "
            + color(
                "/status",
                "white",
            )
            + "            System status"
        )

        print(
            "  "
            + color(
                "/help",
                "white",
            )
            + "              Show this menu"
        )

        print(
            "  "
            + color(
                "/exit",
                "white",
            )
            + "              Shut down E.V."
        )

        print()

        print_centered(
            "╭────────────────────────────────────────────╮",
            "purple",
        )

        print_centered(
            "│ Gemini 🌐 Cloud AI  │  Qwen 🧠 Local AI  │",
            "cyan",
        )

        print_centered(
            "╰────────────────────────────────────────────╯",
            "purple",
        )

        print()

        return True

    # --------------------------------------------------------
    # UNKNOWN
    # --------------------------------------------------------

    print(
        color(
            "Unknown command. Try /help",
            "red",
        )
    )

    return True


# ============================================================
# MEMORY SAVE
# ============================================================

def save_memory(
    memory: dict,
) -> None:

    save_json(
        MEMORY_FILE,
        memory,
    )


# ============================================================
# MODEL SELECTION
# ============================================================

def choose_mode(
    runtime_mode: str,
    api_key_present: bool,
) -> str:

    if runtime_mode in {
        "gemini",
        "qwen",
    }:
        return runtime_mode

    if (
        api_key_present
        and internet_available()
    ):
        return "gemini"

    return "qwen"


# ============================================================
# CHAT
# ============================================================

def run_chat(
    state: dict,
    personality: str,
) -> None:

    while True:

        try:

            prompt = input(
                color(
                    "You > ",
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

            api_key_present = bool(
                os.getenv(
                    "GEMINI_API_KEY",
                    "",
                ).strip()
            )

            mode = choose_mode(
                state["mode"],
                api_key_present,
            )

            # =================================================
            # GEMINI FIRST
            # =================================================

            if mode == "gemini":

                print(
                    color(
                        "\n[E.V. // Gemini 🌐]\n",
                        "purple",
                    )
                )

                answer, error = ask_gemini(
                    prompt,
                    state["memory"],
                    personality,
                    state["history"],
                )

                if answer is None:

                    print(
                        color(
                            f"Gemini failed: {error}",
                            "red",
                        )
                    )

                    print(
                        color(
                            "\n[E.V. // Qwen fallback 🧠]\n",
                            "blue",
                        )
                    )

                    answer, qwen_error = ask_qwen(
                        prompt,
                        state["memory"],
                        personality,
                        state["history"],
                        state["threads"],
                    )

                    if answer is None:

                        print(
                            color(
                                f"Qwen failed: {qwen_error}",
                                "red",
                            )
                        )

                        continue

            # =================================================
            # QWEN FIRST
            # =================================================

            else:

                print(
                    color(
                        "\n[E.V. // Qwen 🧠]\n",
                        "blue",
                    )
                )

                answer, qwen_error = ask_qwen(
                    prompt,
                    state["memory"],
                    personality,
                    state["history"],
                    state["threads"],
                )

                if answer is None:

                    if (
                        api_key_present
                        and internet_available()
                    ):

                        print(
                            color(
                                f"Qwen failed: {qwen_error}",
                                "red",
                            )
                        )

                        print(
                            color(
                                "\n[E.V. // Gemini fallback 🌐]\n",
                                "purple",
                            )
                        )

                        answer, error = ask_gemini(
                            prompt,
                            state["memory"],
                            personality,
                            state["history"],
                        )

                        if answer is None:

                            print(
                                color(
                                    f"Gemini failed: {error}",
                                    "red",
                                )
                            )

                            continue

                    else:

                        print(
                            color(
                                f"Qwen failed: {qwen_error}",
                                "red",
                            )
                        )

                        continue

            # =================================================
            # OUTPUT
            # =================================================

            print(answer)

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

            print(
                "\n\n"
                + color(
                    "E.V. shutting down... 👋",
                    "green",
                )
            )

            return

        except EOFError:

            print(
                "\n\n"
                + color(
                    "E.V. shutting down... 👋",
                    "green",
                )
            )

            return


# ============================================================
# MAIN
# ============================================================

def main() -> int:

    parser = argparse.ArgumentParser(
        description=(
            "E.V. - Enhanced Virtuality"
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
            "Choose auto, gemini, or qwen"
        ),
    )

    parser.add_argument(
        "--threads",
        default=DEFAULT_THREADS,
        help=(
            "CPU threads for Qwen"
        ),
    )

    args = parser.parse_args()

    personality = (
        load_personality()
    )

    memory = normalize_memory(
        load_json(
            MEMORY_FILE,
            {
                "facts": []
            },
        )
    )

    state = {
        "mode": args.model,
        "threads": str(
            args.threads
        ),
        "memory": memory,
        "history": [],
    }

    banner()

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
