# ⚡ E.V. | Enhanced Virtuality

> A personal hybrid AI assistant for Termux with automatic **Gemini ↔ local Qwen** fallback.

**E.V. (Enhanced Virtuality)** is a lightweight personal AI assistant designed to run directly on Android through **Termux**.

E.V. combines a cloud-based **Gemini** model with a locally running **Qwen 2.5 3B** model, allowing it to remain useful both online and offline.

The philosophy is simple:

> **Use the best available brain. 🧠**

When the network is available, E.V. can communicate with Gemini through the Gemini API. When Gemini is unavailable, E.V. can fall back to the local Qwen GGUF model through `llama-cli`.

**One assistant. Two brains. No Wi-Fi panic.** ⚡

---

## ✨ Features

* 🌐 **Gemini integration** for online AI
* 🧠 **Qwen 2.5 3B** for local/offline AI
* 🔄 **Automatic Gemini ↔ Qwen fallback**
* 🎭 Customizable E.V. personality
* 💾 Persistent local memory
* ⚙️ Manual model selection
* 📱 Designed for Android + Termux
* 🖥️ Fully terminal-based
* 🔐 API keys stored locally through `.env`
* 📴 Qwen can operate without an internet connection
* ⚡ Lightweight architecture with no unnecessary cloud dependency

---

## 🧠 How It Works

```
      ┌─────────────────────┐
      │  E.V.               │
      │  Enhanced Virtuality│
      └──────────┬──────────┘
                   │
               Choose Model
                   │                                            ┌───────────────┴───────────────┐ 
│                                    │
AUTO                              MANUAL
  │                                    │
Check Gemini                  Gemini / Qwen
          │
  ┌──────┴──────┐
  │               │
AVAILABLE     UNAVAILABLE
  │             │
  ▼             ▼
🌐 GEMINI       🧠 QWEN
  Cloud AI       Local GGUF
  │               │
  └──────┬──────┘
          │
          ▼
    ⚡ E.V. RESPONSE
```

---

## 🧩 Architecture

E.V. currently consists of two primary AI paths:

### 🌐 Gemini

The online AI engine.

E.V. sends the conversation context to Google's Gemini API when Gemini mode is active and a valid API key is available.

### 🧠 Qwen

The local AI engine.

E.V. runs a compatible Qwen GGUF model locally through `llama-cli`.

This means Qwen mode does not require an internet connection.

---

## 🎭 Personality

E.V.'s behavior is controlled through:

```text
personality.txt
```

This allows the assistant's identity and behavior to be modified without changing the Python source code.

The default identity is:

> **E.V. | Enhanced Virtuality**

---

## 💾 Memory

E.V. includes a lightweight persistent memory system.

Memory is stored locally in:

```text
memory.json
```

Built-in commands allow memories to be viewed, added, removed, or completely cleared.

Memory remains local and is excluded from Git through `.gitignore`.

---

## ⚙️ Model Modes

E.V. supports three model modes:

```text
/model auto
```

Automatically prefers Gemini when available and falls back to Qwen when necessary.

```text
/model gemini
```

Forces Gemini.

```text
/model qwen
```

Forces local Qwen.

You can also start E.V. directly with:

```bash
python jarvis.py --model qwen
```

or:

```bash
python jarvis.py --model gemini
```

---

## 📦 Requirements

E.V. currently requires:

* 📱 Termux
* 🐍 Python 3
* 📦 Python `requests`
* 🧠 `llama.cpp` / `llama-cli`
* 🤖 A compatible Qwen GGUF model
* 🔑 A Gemini API key if Gemini mode is desired

### ⚠️ About the Qwen model

The Qwen GGUF model is **not included in this repository** because model files can be very large.

You must provide your own compatible model.

---

# 🚀 Installation

## 1. Clone the repository

```bash
git clone https://github.com/TonyStark679/Tarmix-Jarvis-for-termux-
cd Tarmix-Jarvis-for-termux-
```

## 2. Install Python dependencies

```bash
pip install requests
```

## 3. Create your environment file

Copy the provided template:

```bash
cp .env.example .env
```

## 4. Configure Gemini

Open `.env` and add your Gemini API key:

```text
GEMINI_API_KEY=your_gemini_api_key_here
JARVIS_MODEL=auto
```

### 🔐 Security

**Never share or commit your real API key.**

The `.env` file is intentionally excluded from Git.

---

# 🧠 Setting Up Qwen

E.V. uses a local GGUF model through `llama-cli`.

Place your model inside:

```text
~/jarvis/models/
```

The default configuration expects:

```text
~/jarvis/models/Qwen2.5-3B-Instruct-Q4_K_M.gguf
```

Check that the model exists:

```bash
ls -lh ~/jarvis/models/
```

Then check that `llama-cli` is available:

```bash
which llama-cli
```

If it returns a valid executable path, the local Qwen engine can be used.

---

# ▶️ Running E.V.

Start the assistant with:

```bash
python jarvis.py
```

You should see the E.V. initialization interface followed by the main prompt.

Example:

```text
        [ SYSTEM STATUS ]

    ◉ CORE ............... ON
    ◉ NETWORK ............ ONLINE
    ◉ GEMINI ............. READY
    ◉ QWEN ............... STANDBY
    ◉ MEMORY ............. LOADED

          E.V. ONLINE

You > Hello E.V.
```

Then simply start chatting.

---

# ⚙️ Commands

## Model Control

```text
/model auto
/model gemini
/model qwen
```

## Memory

```text
/memory
/remember <fact>
/forget <number>
/forget all
```

## Session

```text
/clear
/status
/help
/exit
/quit
```

---

# 🧩 Project Structure

```text
Tarmix-Jarvis-for-termux/
│
├── jarvis.py              # Main E.V. application
├── local_ai.py            # Local Qwen interface
├── personality.txt        # E.V. personality and behavior
├── .env.example           # Environment configuration template
├── .gitignore             # Git exclusions
│
├── memory.json            # Local persistent memory
│
└── models/
    └── *.gguf             # Local AI models
```

---

# 🔐 Security

Your Gemini API key belongs in:

```text
.env
```

Never put your real API key directly into Python source code or commit it to GitHub.

The repository ignores sensitive and local files including:

```text
.env
memory.json
models/*
__pycache__/
*.pyc
*.gguf
*.save
*.save.*
```

If you accidentally expose an API key, **revoke it immediately and generate a new one.**

---

# 🛠️ Troubleshooting

## Gemini isn't working

Check that your environment contains a Gemini key.

```bash
cat .env
```

It should contain:

```text
GEMINI_API_KEY=your_key_here
```

Also check your selected model:

```text
JARVIS_MODEL=auto
```

or:

```text
JARVIS_MODEL=gemini
```

---

## Qwen isn't working

Check the model:

```bash
ls -lh ~/jarvis/models/
```

Then check `llama-cli`:

```bash
which llama-cli
```

You can also force Qwen:

```bash
python jarvis.py --model qwen
```

---

## Check the repository state

```bash
git status
```

---

# 🎯 Project Goal

E.V. started as a simple terminal AI experiment and evolved into a hybrid assistant capable of using both cloud AI and local AI.

The long-term goal is simple:

```text
                 E.V.
                  │
        ┌─────────┴─────────┐
        │                      │
     INTERNET             NO INTERNET
        │                      │
        ▼                      ▼
    🌐 GEMINI             🧠 QWEN
     Cloud AI              Local AI
        │                      │
        └─────────┬─────────┘
                  │
                  ▼
             ⚡ E.V.
       Enhanced Virtuality
```

The assistant should remain useful regardless of whether the device has an internet connection.

**One assistant.
Two brains.
Local fallback.
No Wi-Fi panic.**

---

# 🗺️ Roadmap

E.V. is still evolving.

Potential future improvements include:

* 🎨 More advanced terminal UI
* 🧠 Improved local model management
* 💾 Smarter memory
* 🔧 More terminal tools
* 🖥️ System information and control
* 🔌 Extensible AI providers
* ⚡ Faster local inference
* 🤖 More capable autonomous workflows

---

# 📜 License

MIT License.

---

<div align="center">

# ⚡ E.V.

### Enhanced Virtuality

**Built for Termux.
Powered by AI.
Backed by local intelligence.**

🧠 🌐 ⚡

</div>
```
