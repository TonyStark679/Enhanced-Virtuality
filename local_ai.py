```python
#!/usr/bin/env python3

import os
import shutil
import subprocess
import sys
from pathlib import Path


# ============================================================
# E.V.
# ENHANCED VIRTUALITY
# LOCAL QWEN ENGINE
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

# Optional custom llama-cli path.
LLAMA_CLI = os.getenv(
    "JARVIS_LLAMA_CLI",
    "",
).strip()

DEFAULT_THREADS = os.getenv(
    "JARVIS_THREADS",
    str(min(6, os.cpu_count() or 6)),
)

DEFAULT_CONTEXT = os.getenv(
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

DEFAULT_TIMEOUT = int(
    os.getenv(
        "JARVIS_QWEN_TIMEOUT",
        "180",
    )
)


# ============================================================
# ANSI
# ============================================================

ANSI = {
    "reset": "\033[0m",
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


def color(
    text: str,
    name: str,
) -> str:

    return (
        f"{ANSI.get(name, '')}"
        f"{text}"
        f"{ANSI['reset']}"
    )


# ============================================================
# TERMINAL
# ============================================================

def terminal_width() -> int:

    try:

        return shutil.get_terminal_size(
            fallback=(80, 24)
        ).columns

    except Exception:

        return 80


def center(
    text: str,
) -> str:

    width = terminal_width()

    if len(text) >= width:
        return text

    return (
        " "
        * max(
            0,
            (width - len(text)) // 2,
        )
        + text
    )


def clear_screen() -> None:

    command = (
        "cls"
        if os.name == "nt"
        else "clear"
    )

    os.system(command)


# ============================================================
# E.V. LOGO
# ============================================================

LOGO = [
    "             ✦       ·          ✧",
    "",
    "                 ███████╗.   ██╗   ██╗",
    "                 ██╔════╝    ██║   ██║",
    "                 █████╗      ██║   ██║",
    "                 ██╔══╝      ╚██╗ ██╔╝",
    "                 ███████╗.    ╚████╔╝",
    "                 ╚══════╝      ╚═══╝",
    "",
    "                     E . V .",
    "",
    "             ✧       ·          ✦",
]


def print_logo() -> None:

    styles = [
        "purple",
        "magenta",
        "blue",
        "cyan",
        "blue",
        "magenta",
        "purple",
    ]

    for index, line in enumerate(LOGO):

        print(
            color(
                center(line),
                styles[
                    index
                    % len(styles)
                ],
            )
        )


# ============================================================
# STARTUP
# ============================================================

def startup() -> None:

    clear_screen()

    print()

    print(
        color(
            center(
                "E.V. // LOCAL NEURAL ENGINE"
            ),
            "cyan",
        )
    )

    print(
        color(
            center(
                "ENHANCED VIRTUALITY"
            ),
            "dim",
        )
    )

    print()

    checks = [
        (
            "Qwen model",
            MODEL_FILE.is_file(),
        ),
        (
            "llama-cli",
            find_llama_cli() is not None,
        ),
    ]

    for name, status in checks:

        if status:

            print(
                color(
                    "[ OK ]",
                    "green",
                )
                + " "
                + color(
                    name,
                    "white",
                )
            )

        else:

            print(
                color(
                    "[FAIL]",
                    "red",
                )
                + " "
                + color(
                    name,
                    "white",
                )
            )

    print()

    print_logo()

    print()

    print(
        color(
            center(
                "╭──────────────────────────────────────╮"
            ),
            "purple",
        )
    )

    print(
        color(
            center(
                "│      E.V. // QWEN CORE READY         │"
            ),
            "cyan",
        )
    )

    print(
        color(
            center(
                "│      100% LOCAL • NO OLLAMA           │"
            ),
            "dim",
        )
    )

    print(
        color(
            center(
                "╰──────────────────────────────────────╯"
            ),
            "purple",
        )
    )

    print()


# ============================================================
# LLAMA-CLI DISCOVERY
# ============================================================

def find_llama_cli():

    if LLAMA_CLI:

        configured = Path(
            LLAMA_CLI
        ).expanduser()

        if configured.is_file():

            return str(
                configured
            )

        # Also allow a command name
        # such as "llama-cli".
        found = shutil.which(
            LLAMA_CLI
        )

        if found:

            return found

        return None

    return shutil.which(
        "llama-cli"
    )


# ============================================================
# MODEL VALIDATION
# ============================================================

def validate_environment():

    problems = []

    if not MODEL_FILE.is_file():

        problems.append(
            f"Model not found: {MODEL_FILE}"
        )

    llama_cli = find_llama_cli()

    if not llama_cli:

        problems.append(
            "llama-cli was not found in PATH"
        )

    return (
        llama_cli,
        problems,
    )


# ============================================================
# PROMPT
# ============================================================

DEFAULT_SYSTEM_PROMPT = """You are E.V., short for Enhanced Virtuality.
You are a local AI assistant running directly on the user's device.

Be helpful, concise, friendly, and practical.
Answer naturally.
Do not claim internet access unless it is actually provided.
Do not claim to have performed actions you did not perform.
Do not invent facts or system capabilities.

When the user asks for a terminal command, provide the command clearly.
"""


def build_prompt(
    user_prompt: str,
    system_prompt: str,
) -> str:

    return (
        system_prompt.strip()
        + "\n\n"
        + "User: "
        + user_prompt.strip()
        + "\n"
        + "E.V.:"
    )


# ============================================================
# QWEN ENGINE
# ============================================================

def qwen(
    prompt: str,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    threads: str = DEFAULT_THREADS,
    context: str = DEFAULT_CONTEXT,
    max_tokens: str = DEFAULT_TOKENS,
    temperature: str = DEFAULT_TEMPERATURE,
):

    llama_cli, problems = (
        validate_environment()
    )

    if problems:

        return (
            None,
            "\n".join(
                problems
            ),
        )

    full_prompt = build_prompt(
        prompt,
        system_prompt,
    )

    command = [
        llama_cli,
        "-m",
        str(MODEL_FILE),
        "-p",
        full_prompt,
        "-n",
        str(max_tokens),
        "-c",
        str(context),
        "-t",
        str(threads),
        "--temp",
        str(temperature),
    ]

    try:

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=DEFAULT_TIMEOUT,
        )

    except subprocess.TimeoutExpired:

        return (
            None,
            "E.V. Qwen engine timed out.",
        )

    except FileNotFoundError:

        return (
            None,
            "llama-cli disappeared from PATH.",
        )

    except PermissionError:

        return (
            None,
            "Permission denied while starting llama-cli.",
        )

    except OSError as exc:

        return (
            None,
            f"Unable to start Qwen: {exc}",
        )

    except Exception as exc:

        return (
            None,
            f"Unexpected Qwen error: {exc}",
        )

    output = (
        result.stdout
        .strip()
    )

    error = (
        result.stderr
        .strip()
    )

    if result.returncode != 0:

        if error:

            return (
                None,
                error,
            )

        return (
            None,
            "llama-cli exited with "
            f"code {result.returncode}.",
        )

    if not output:

        if error:

            return (
                None,
                error,
            )

        return (
            None,
            "Qwen returned an empty response.",
        )

    return (
        clean_output(output),
        None,
    )


# ============================================================
# OUTPUT CLEANER
# ============================================================

def clean_output(
    output: str,
) -> str:

    lines = output.splitlines()

    cleaned = []

    for line in lines:

        stripped = line.strip()

        if not stripped:
            continue

        # Remove common llama.cpp prompt markers.
        if stripped in {
            ">",
            "User:",
            "E.V.:",
        }:

            continue

        if stripped.startswith(
            "[ Prompt:"
        ):

            continue

        cleaned.append(
            line
        )

    return "\n".join(
        cleaned
    ).strip()


# ============================================================
# INTERACTIVE MODE
# ============================================================

def interactive() -> int:

    startup()

    llama_cli, problems = (
        validate_environment()
    )

    if problems:

        print(
            color(
                "E.V. cannot start:",
                "red",
            )
        )

        for problem in problems:

            print(
                color(
                    f"  • {problem}",
                    "red",
                )
            )

        print()

        return 1

    print(
        color(
            "Local Qwen engine initialized.",
            "green",
        )
    )

    print(
        color(
            "Type /help for commands.",
            "dim",
        )
    )

    print()

    while True:

        try:

            user = input(
                color(
                    "You > ",
                    "cyan",
                )
            ).strip()

        except KeyboardInterrupt:

            print(
                "\n"
                + color(
                    "E.V. local engine offline. 👋",
                    "green",
                )
            )

            return 0

        except EOFError:

            print(
                "\n"
                + color(
                    "E.V. local engine offline. 👋",
                    "green",
                )
            )

            return 0

        if not user:
            continue

        command = user.lower()

        if command in {
            "exit",
            "quit",
            "/exit",
            "/quit",
        }:

            print(
                color(
                    "E.V. local engine offline. 👋",
                    "green",
                )
            )

            return 0

        if command == "/help":

            print()

            print(
                color(
                    "E.V. // LOCAL COMMANDS",
                    "purple",
                )
            )

            print(
                "  "
                + color(
                    "/help",
                    "cyan",
                )
                + "    Show this menu"
            )

            print(
                "  "
                + color(
                    "/status",
                    "cyan",
                )
                + "  Show local engine status"
            )

            print(
                "  "
                + color(
                    "/clear",
                    "cyan",
                )
                + "   Clear terminal"
            )

            print(
                "  "
                + color(
                    "/exit",
                    "cyan",
                )
                + "    Shut down E.V."
            )

            print()

            continue

        if command == "/clear":

            clear_screen()
            print_logo()
            print()

            continue

        if command == "/status":

            print()

            print(
                color(
                    "E.V. // LOCAL STATUS",
                    "purple",
                )
            )

            print(
                f"  Model: {MODEL_FILE}"
            )

            print(
                f"  llama-cli: {llama_cli}"
            )

            print(
                f"  Threads: {DEFAULT_THREADS}"
            )

            print(
                f"  Context: {DEFAULT_CONTEXT}"
            )

            print(
                f"  Max tokens: {DEFAULT_TOKENS}"
            )

            print(
                f"  Temperature: {DEFAULT_TEMPERATURE}"
            )

            print()

            continue

        print(
            color(
                "\n[E.V. // QWEN 🧠]\n",
                "blue",
            )
        )

        answer, error = qwen(
            user
        )

        if error:

            print(
                color(
                    f"Error: {error}",
                    "red",
                )
            )

            print()

            continue

        print(answer)
        print()


# ============================================================
# CLI ENTRY POINT
# ============================================================

def main() -> int:

    interactive()


if __name__ == "__main__":

    raise SystemExit(
        main()
    )
```
