import subprocess

def qwen(prompt):
    result = subprocess.run(
        [
            "--simple-io",
            "--no-display-prompt",
            "llama-cli",
            "-m",
            "/data/data/com.termux/files/home/jarvis/models/Qwen2.5-3B-Instruct-Q4_K_M.gguf",
            "-p",
            prompt,
            "-n",
            "256",
            "-t",
            "4"
        ],
        capture_output=True,
        text=True
    )

    return result.stdout


if __name__ == "__main__":
    while True:
        user = input("You > ")

        if user == "exit":
            break

        print("\n[Qwen 🧠]\n")
        print(qwen(user))
