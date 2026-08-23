#!/usr/bin/env python3
import argparse
import json
import os
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

import requests


APP_NAME = "JARVIS"
ROOT = Path.home() / "jarvis"
MODEL_FILE = Path(os.getenv("JARVIS_MODEL_FILE", str(ROOT / "models" / "Qwen2.5-3B-Instruct-Q4_K_M.gguf")))
MEMORY_FILE = ROOT / "memory.json"
PERSONALITY_FILE = ROOT / "personality.txt"

DEFAULT_PERSONALITY = """You are Jarvis, a futuristic, concise, friendly terminal assistant.
Keep replies clear, useful, and a little cinematic.
When the user asks for a command, give the command directly.
When the user asks a factual question, answer plainly.
Never claim to have emotions or a body.
"""

ANSI = {
    "reset": "\033[0m",
    "dim": "\033[2m",
    "cyan": "\033[38;5;117m",
    "blue": "\033[38;5;111m",
    "purple": "\033[38;5;141m",
    "green": "\033[38;5;114m",
    "yellow": "\033[38;5;221m",
    "red": "\033[38;5;203m",
    "white": "\033[38;5;255m",
}

DEFAULT_THREADS = str(min(6, os.cpu_count() or 6))
DEFAULT_CTX = os.getenv("JARVIS_CTX", "2048")
DEFAULT_TOKENS = os.getenv("JARVIS_MAX_TOKENS", "256")

session = requests.Session()


def color(text: str, name: str) -> str:
    return f"{ANSI.get(name, '')}{text}{ANSI['reset']}"


def term_width() -> int:
    return shutil.get_terminal_size(fallback=(80, 20)).columns


def center_line(text: str) -> str:
    width = term_width()
    if len(text) >= width:
        return text
    left = max(0, (width - len(text)) // 2)
    return " " * left + text


def banner():
    os.system("clear")

    print()
    print(color(center_line("INITIALIZING JARVIS..."), "cyan"))
    print()

    startup_steps = [
        ("[ OK ]", "Loading neural interface"),
        ("[ OK ]", "Initializing memory core"),
        ("[ OK ]", "Loading personality matrix"),
        ("[ OK ]", "Checking network connection"),
        ("[ OK ]", "Preparing Gemini interface"),
        ("[ OK ]", "Preparing Qwen local engine"),
        ("[ OK ]", "All systems active"),
    ]

    import time

    for status, message in startup_steps:
        print(
            f"{color(status, 'green')} "
            f"{color(message, 'white')}"
        )
        time.sleep(0.15)

    print()

    art = [

      "     ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗",
      "     ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝",
      "     ██║███████║██████╔╝██║   ██║██║███████╗",
      "██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║",
      "╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║",
      " ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝",
      "",
      "             [ SYSTEM STATUS ]",
      "",
      "        ◉ CORE ............... ON",
      "        ◉ NETWORK ............ ONLINE",
      "        ◉ GEMINI ............. READY",
      "        ◉ QWEN ............... STANDBY",
      "        ◉ MEMORY ............. LOADED",
      "",
      "              ALL SYSTEMS ON",

    ]

    for line in art:
        print(color(center_line(line), "blue"))
        time.sleep(0.04)

    print()
    print(color(center_line("J A R V I S   O N L I N E"), "purple"))
    print()


def load_json(path: Path, default):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default


def save_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def load_personality() -> str:
    try:
        if PERSONALITY_FILE.exists():
            text = PERSONALITY_FILE.read_text(encoding="utf-8").strip()
            if text:
                return text
    except Exception:
        pass
    return DEFAULT_PERSONALITY.strip()


def normalize_memory(raw):
    if isinstance(raw, dict):
        facts = raw.get("facts", [])
        if not isinstance(facts, list):
            facts = []
        return {"facts": [str(x).strip() for x in facts if str(x).strip()]}
    return {"facts": []}


def build_memory_context(memory: dict) -> str:
    facts = memory.get("facts", [])
    if not facts:
        return "None"
    return "\n".join(f"- {item}" for item in facts[-20:])


def build_chat_history(history):
    if not history:
        return "None"
    lines = []
    for item in history[-12:]:
        role = "User" if item["role"] == "user" else "Jarvis"
        lines.append(f"{role}: {item['text']}")
    return "\n".join(lines)


def build_prompt(user_text: str, memory: dict, personality: str, history) -> str:
    return textwrap.dedent(
        f"""
        {personality}

        Known memory:
        {build_memory_context(memory)}

        Recent conversation:
        {build_chat_history(history)}

        User: {user_text}
        Jarvis:
        """
    ).strip()


def internet_available() -> bool:
    try:
        session.get("https://generativelanguage.googleapis.com", timeout=3)
        return True
    except requests.RequestException:
        return False


def ask_gemini(user_text: str, memory: dict, personality: str, history):
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return None, "GEMINI_API_KEY is not set"

    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        f"models/gemini-2.5-flash:generateContent?key={api_key}"
    )

    full_prompt = build_prompt(user_text, memory, personality, history)
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": full_prompt}],
            }
        ]
    }

    try:
        resp = session.post(url, json=payload, timeout=60)
        data = resp.json()

        if "candidates" in data:
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return text.strip(), None

        err = data.get("error", {}).get("message", "Unknown Gemini error")
        return None, err

    except requests.RequestException as e:
        return None, str(e)
    except Exception as e:
        return None, str(e)


def extract_llama_answer(stdout: str) -> str:
    lines = stdout.splitlines()

    prompt_indices = [i for i, line in enumerate(lines) if line.lstrip().startswith(">")]
    if not prompt_indices:
        cleaned = [line for line in lines if line.strip()]
        return "\n".join(cleaned[-8:]).strip()

    start = prompt_indices[-1] + 1
    answer_lines = []

    for line in lines[start:]:
        stripped = line.strip()

        if line.startswith("[ Prompt:"):
            break
        if line.lstrip().startswith(">"):
            break
        if stripped:
            answer_lines.append(line)

    return "\n".join(answer_lines).strip()


def ask_qwen(user_text: str, memory: dict, personality: str, history, threads: str):
    if not MODEL_FILE.exists():
        return None, f"Model not found: {MODEL_FILE}"

    full_prompt = build_prompt(user_text, memory, personality, history)

    cmd = [
        "llama-cli",
        "-m",
        str(MODEL_FILE),
        "-p",
        full_prompt,
        "-n",
        str(DEFAULT_TOKENS),
        "-c",
        str(DEFAULT_CTX),
        "-t",
        str(threads),
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=180,
        )
        answer = extract_llama_answer(result.stdout)

        if answer:
            return answer, None

        if result.stderr.strip():
            return None, result.stderr.strip()

        return None, "Empty response from Qwen"

    except subprocess.TimeoutExpired:
        return None, "Qwen timed out"
    except Exception as e:
        return None, str(e)


def print_status(mode: str, threads: str) -> None:
    online = internet_available()
    net = "online" if online else "offline"
    gemini_key = "set" if os.getenv("GEMINI_API_KEY", "").strip() else "missing"
    model_ok = "present" if MODEL_FILE.exists() else "missing"

    print(
        color(
            f"[status] mode={mode} | net={net} | key={gemini_key} | model={model_ok} | threads={threads}",
            "dim",
        )
    )


def save_memory(memory: dict) -> None:
    save_json(MEMORY_FILE, memory)


def handle_command(command: str, state: dict) -> bool:
    parts = command.strip().split(maxsplit=1)
    cmd = parts[0].lower()

    if cmd in {"/exit", "/quit"}:
        raise KeyboardInterrupt

    if cmd in {"/clear", "/reset"}:
        state["history"].clear()
        print(color("Session cleared.", "green"))
        return True

    if cmd == "/model":
        if len(parts) == 1:
            print(color(f"Current mode: {state['mode']}", "yellow"))
        else:
            value = parts[1].strip().lower()
            if value in {"auto", "gemini", "qwen"}:
                state["mode"] = value
                print(color(f"Mode set to: {value}", "green"))
            else:
                print(color("Use /model auto, /model gemini, or /model qwen", "red"))
        return True

    if cmd == "/status":
        print_status(state["mode"], state["threads"])
        return True

    if cmd == "/memory":
        facts = state["memory"].get("facts", [])
        if not facts:
            print(color("Memory is empty.", "yellow"))
        else:
            print(color("Memory:", "cyan"))
            for i, fact in enumerate(facts, 1):
                print(color(f"  {i}. {fact}", "white"))
        return True

    if cmd == "/remember":
        if len(parts) == 1 or not parts[1].strip():
            print(color("Use /remember <fact>", "red"))
            return True
        fact = parts[1].strip()
        state["memory"].setdefault("facts", []).append(fact)
        save_memory(state["memory"])
        print(color("Saved.", "green"))
        return True

    if cmd == "/forget":
        if len(parts) == 1 or not parts[1].strip():
            print(color("Use /forget all or /forget <number>", "red"))
            return True

        target = parts[1].strip().lower()
        facts = state["memory"].get("facts", [])

        if target == "all":
            state["memory"]["facts"] = []
            save_memory(state["memory"])
            print(color("Memory cleared.", "green"))
            return True

        if target.isdigit():
            idx = int(target) - 1
            if 0 <= idx < len(facts):
                removed = facts.pop(idx)
                save_memory(state["memory"])
                print(color(f"Forgot: {removed}", "green"))
            else:
                print(color("No memory item at that number.", "red"))
            return True

        removed = [f for f in facts if target.lower() not in f.lower()]
        state["memory"]["facts"] = removed
        save_memory(state["memory"])
        print(color("Filtered memory.", "green"))
        return True

    if cmd == "/help":
        print()
        print(color("╭────────────────────────────────────────────╮", "cyan"))
        print(color("│              J A R V I S  //  HELP        │", "cyan"))
        print(color("╰────────────────────────────────────────────╯", "cyan"))
        print()

        print(color("  MODEL CONTROL", "purple"))
        print(color("  /model auto", "white") + "      Automatic Gemini ↔ Qwen switching")
        print(color("  /model gemini", "white") + "    Force Gemini 🌐")
        print(color("  /model qwen", "white") + "      Force local Qwen 🧠")
        print()

        print(color("  MEMORY", "purple"))
        print(color("  /memory", "white") + "            Show saved memories")
        print(color("  /remember <fact>", "white") + "  Save something to Jarvis memory")
        print(color("  /forget <number>", "white") + " Remove a memory")
        print(color("  /forget all", "white") + "       Clear all memories")
        print()

        print(color("  SESSION", "purple"))
        print(color("  /clear", "white") + "             Clear current conversation")
        print(color("  /status", "white") + "            Show system status")
        print(color("  /help", "white") + "              Show this menu")
        print(color("  /exit", "white") + "              Shut down Jarvis")
        print()

        print(color("╭────────────────────────────────────────────╮", "cyan"))
        print(color("│  Gemini 🌐 Online AI  │  Qwen 🧠 Local AI │", "cyan"))
        print(color("╰────────────────────────────────────────────╯", "cyan"))
        print()

        return True

    print(color("Unknown command. Try /help", "red"))
    return True


def choose_mode(runtime_mode: str, api_key_present: bool) -> str:
    if runtime_mode in {"gemini", "qwen"}:
        return runtime_mode
    if internet_available() and api_key_present:
        return "gemini"
    return "qwen"


def main() -> int:
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument(
        "--model",
        choices=["auto", "gemini", "qwen"],
        default=os.getenv("JARVIS_MODEL", "auto").lower(),
        help="Choose auto, gemini, or qwen",
    )
    parser.add_argument(
        "--threads",
        default=os.getenv("JARVIS_THREADS", DEFAULT_THREADS),
        help="CPU threads for Qwen",
    )
    args = parser.parse_args()

    personality = load_personality()
    memory = normalize_memory(load_json(MEMORY_FILE, {"facts": []}))
    history = []
    state = {
        "mode": args.model,
        "threads": str(args.threads),
        "memory": memory,
        "history": history,
    }

    banner()
    print_status(state["mode"], state["threads"])
    print()

    while True:
        try:
            prompt = input(color("You > ", "cyan")).strip()

            if not prompt:
                continue

            if prompt.startswith("/"):
                handle_command(prompt, state)
                continue

            api_key_present = bool(os.getenv("GEMINI_API_KEY", "").strip())
            mode = choose_mode(state["mode"], api_key_present)

            if mode == "gemini":
                print(color("\n[Gemini 🌐]\n", "purple"))
                answer, err = ask_gemini(
                    prompt,
                    state["memory"],
                    personality,
                    state["history"],
                )

                if answer is None:
                    print(color(f"Gemini failed: {err}", "red"))
                    print(color("\n[Qwen fallback 🧠]\n", "blue"))

                    answer, qerr = ask_qwen(
                        prompt,
                        state["memory"],
                        personality,
                        state["history"],
                        state["threads"],
                    )

                    if answer is None:
                        print(color(f"Qwen failed: {qerr}", "red"))
                        continue

            else:
                print(color("\n[Qwen 🧠]\n", "blue"))

                answer, qerr = ask_qwen(
                    prompt,
                    state["memory"],
                    personality,
                    state["history"],
                    state["threads"],
                )

                if answer is None:
                    if api_key_present and internet_available():
                        print(color(f"Qwen failed: {qerr}", "red"))
                        print(color("\n[Gemini fallback 🌐]\n", "purple"))

                        answer, err = ask_gemini(
                            prompt,
                            state["memory"],
                            personality,
                            state["history"],
                        )

                        if answer is None:
                            print(color(f"Gemini failed: {err}", "red"))
                            continue
                    else:
                        print(color(f"Qwen failed: {qerr}", "red"))
                        continue

            print(answer)

            state["history"].append(
                {"role": "user", "text": prompt}
            )

            state["history"].append(
                {"role": "assistant", "text": answer}
            )

            state["history"] = state["history"][-12:]

        except KeyboardInterrupt:
            print("\n\n" + color("Jarvis shutting down...  👋", "green"))
            return 0

        except EOFError:
            print("\n\n" + color("Jarvis shutting down...  👋", "green"))
            return 0


if __name__ == "__main__":
    raise SystemExit(main())
