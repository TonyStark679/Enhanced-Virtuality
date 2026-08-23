# 🤖 JARVIS

> A personal AI assistant for Termux with automatic **Gemini ↔ local Qwen** fallback.

JARVIS is a lightweight AI assistant designed to run directly on Android through **Termux**.

It combines a cloud-based **Gemini** model with a locally running **Qwen 2.5 3B** model, allowing JARVIS to keep working even when the internet disappears.

The idea is simple:

**Use the best available brain. 🧠**

When the network is available, JARVIS communicates with Gemini through the Gemini API. When the network is unavailable, it automatically falls back to the local Qwen GGUF model through `llama-cli`.

---

## ✨ Features

- 🌐 **Gemini integration** for online AI
- 🧠 **Qwen 2.5 3B** for local/offline AI
- 🔄 **Automatic online/offline switching**
- 🎭 Customizable assistant personality
- 💾 Persistent memory system
- ⚙️ Manual model selection
- 📱 Built for Android + Termux
- 🖥️ Fully terminal-based
- 🔐 API keys stored locally through `.env`
- 🚫 No cloud connection required for Qwen mode

---

## 🧠 How It Works

```text
                       ┌─────────────┐
                       │   JARVIS      │
                       └──────┬──────┘
                               │
                         Check Network
                               │
                ┌─────────────┴─────────────┐
                │                                │
             ONLINE                          OFFLINE
                │                                │
                ▼                                ▼
           ☁️ GEMINI                         🧠 QWEN
            Gemini API                  Local GGUF Model
                │                                │
                └─────────────┬─────────────┘
                                │
                                ▼
                         🤖 JARVIS RESPONSE
```
## ✍🏻 NOTE
- 🖥️ Add your Gemini API key to the .env file.
- 🤖 To manually test Qwen offline mode, turn
     off your internet/Wi-Fi and type your 
     message into the prompt.
- 🔄 auto mode handles the Gemini ↔ Qwen 
     switching automatically.
-🧠 Qwen requires a compatible GGUF model 
    and llama-cli.

### 📦 Requirements
JARVIS currently requires:
- 📱 Termux
- 🐍 Python 3
- 📦 Python requests
- 🧠 llama.cpp / llama-cli
- 🤖 A compatible Qwen GGUF model
- 🔑 A Gemini API key
- ⚠️ The Qwen model is not included in 
     this repository because GGUF model
     files can be very large.

### 🚀 Setup

1. Clone the repository
git clone https://github.com/TonyStark679/jarvis.git
cd jarvis
2. Install Python dependencies
pip install requests
3. Create your environment file
Copy the provided template:
cp .env.example .env

# Gemini setup:

4. Add your Gemini API key:
Open .env and add your API key:
GEMINI_API_KEY=your_gemini_api_key_here
JARVIS_MODEL=auto
## **🔐 Never share or commit your real API key.**

# 🧠 Setting Up Qwen:

JARVIS uses a local GGUF model through llama-cli.
Place your Qwen model inside:
```
~/jarvis/models/
The current configuration expects:
~/jarvis/models/Qwen2.5-3B-Instruct-Q4_K_M.gguf
```
Make sure llama-cli is available:
which llama-cli
If it returns a valid path, JARVIS can use the local Qwen engine.
▶️ Running JARVIS
Start JARVIS with:
```
python jarvis.py
```
You should see the system initialize:
```
[ SYSTEM STATUS ]

◉ CORE ............... ON
◉ NETWORK ............ ONLINE
◉ GEMINI ............. READY
◉ QWEN ............... STANDBY
◉ MEMORY ............. LOADED

J A R V I S   O N L I N E
Then simply type your message.
You > Hello Jarvis
```
## ⚙️ Commands
JARVIS supports several built-in commands:
```
Model selection
/model auto
/model gemini
/model qwen
Clear conversation
/clear
Exit
/exit
or:
/quit
🧩 Project Structure
jarvis/
├── jarvis.py          # Main JARVIS application
├── local_ai.py        # Local Qwen interface
├── personality.txt    # Assistant personality
├── .env.example       # Environment variable template
├── .gitignore         # Git exclusions
├── memory.json        # Local memory
└── models/            # Local GGUF models
```
🔐 Security
- Your Gemini API key belongs in:
  .env
- Never put your real API key directly
  into Python source code or commit it 
  to GitHub.
- The repository ignores sensitive/local
  files such as:
  1..env
  2.memory.json
  3.models/*
  4.__pycache__/
  5.*.pyc
  6.*.save
  7.*.save.*
**If you accidentally expose an API key, revoke it immediately and generate a new one.**

## 🛠️ Troubleshooting
Gemini isn't working
Check that your API key exists:
```
cat .env
```
Make sure it contains:
```
GEMINI_API_KEY=your_key_here
```
Qwen isn't working
Check that the model exists:
```
ls -lh ~/jarvis/models/
```
Then check llama-cli:
```
which llama-cli
```
Check the current repository state
```
git status
```
### 🎯 Project Goal
JARVIS started as a simple terminal AI experiment and evolved into a hybrid assistant capable of using both cloud AI and local AI.
The goal is to keep the assistant useful regardless of whether the phone has:

🌐 Internet
     ↓
   Gemini

or

📴 No Internet
     ↓
   Qwen

One assistant.
Two brains.
No Wi-Fi panic. 🤖🧠

### 📜 License
MIT License.

⚡ Built for Termux. Powered by Gemini.
   Backed up by Qwen.

# JARVIS either way!