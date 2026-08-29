⚡ E.V. | Enhanced Virtuality

«One assistant. Two brains. No Wi-Fi panic.»

E.V. (Enhanced Virtuality) is a lightweight personal AI assistant designed to run directly on Android through Termux.

It combines two AI engines:

Gemini for cloud-based AI when internet access is available, and Qwen 2.5 3B running locally through "llama-cli" when local inference is needed.

The core idea is simple:
```
             ⚡ E.V.
                │
        ┌───────┴───────┐
        │               │
     ONLINE           OFFLINE
        │               │
        ▼               ▼
   🌐 GEMINI        🧠 QWEN
   Cloud AI        Local AI
        │               │
        └───────┬───────┘
                │
                ▼
           ⚡ E.V. RESPONSE
```
E.V. is built around one goal:

«Use the best available brain. 🧠»

---

✨ Features

🌐 Gemini integration
🧠 Local Qwen 2.5 3B inference
🔄 Automatic Gemini → Qwen fallback
🎭 Customizable personality
💾 Persistent local memory
⚙️ Manual model selection
📱 Android + Termux support
🖥️ Terminal-based interface
🔐 Local environment configuration
📴 Offline-capable local AI
⚡ Lightweight architecture

---

🧠 Architecture
```
E.V. currently has two primary AI paths.

                           ┌───────────────────────────┐
                           │        ⚡ E.V.             │
                           │   Enhanced Virtuality     │
                           └─────────────┬─────────────┘
                                         │
                                  ┌──────▼──────┐
                                  │ MODEL MODE  │
                                  └──────┬──────┘
                                         │
                        ┌────────────────┼────────────────┐
                        │                │                │
                      AUTO            GEMINI            QWEN
                        │                │                │
                        │                │                │
                        ▼                ▼                ▼
                ┌──────────────┐   ┌───────────┐   ┌───────────┐
                │ Check Gemini  │   │  Gemini   │   │   Qwen    │
                │ Availability  │   │ Cloud AI  │   │ Local AI  │
                └──────┬───────┘   └─────┬─────┘   └─────┬─────┘
                       │                 │               │
                ┌──────┴──────┐          │               │
                │             │          │               │
             READY         FAILED        │               │
                │             │          │               │
                ▼             ▼          │               │
             🌐 Gemini     🧠 Qwen ──────┴───────┬───────┘
                                                  │
                                                  ▼
                                         ⚡ E.V. RESPONSE
```
---

🌐 Gemini

Gemini is E.V.'s online AI engine.

When Gemini mode is selected and a valid API key is configured, E.V. communicates with the Gemini API and uses the returned response.

Gemini provides the cloud-based intelligence path of E.V.
```
Internet available
        │
        ▼
   🌐 Gemini API
        │
        ▼
   E.V. processes response
        │
        ▼
    ⚡ Response
```
---

🧠 Qwen

Qwen is E.V.'s local AI engine.

E.V. runs a compatible Qwen GGUF model locally through:

llama-cli

The model runs directly on the Android device through Termux.
```
Qwen GGUF Model
       │
       ▼
   llama-cli
       │
       ▼
    🧠 Qwen
       │
       ▼
   ⚡ E.V.
```
Because the model is local, Qwen can operate without an active internet connection.

---

🔄 Automatic Fallback

The "auto" mode is the main hybrid mode.

E.V. first checks whether Gemini can be used.
```
                    ⚡ E.V.
                       │
                       ▼
                ┌──────────────┐
                │  AUTO MODE   │
                └──────┬───────┘
                       │
                       ▼
              Is Gemini available?
                       │
              ┌────────┴────────┐
              │                 │
             YES                NO
              │                 │
              ▼                 ▼
         🌐 GEMINI          🧠 QWEN
         Cloud AI          Local AI
              │                 │
              └────────┬────────┘
                       │
                       ▼
                ⚡ E.V. RESPONSE
```
So the behavior is:

ONLINE  →  Gemini
OFFLINE →  Qwen

That is the heart of E.V.

---

🎭 Personality

E.V.'s personality is stored separately from the Python source code.
```
personality.txt
```
This means the assistant's personality can be changed without editing the main application.

The default identity is:

E.V. | Enhanced Virtuality

You can customize the personality configuration to change how E.V. behaves and communicates.

---

💾 Memory

E.V. includes a lightweight persistent memory system.

Memory is stored locally in:
```
memory.json
```

The memory system allows E.V. to remember information between sessions.

Available memory commands:
```
/memory
```
```
/remember <fact>
```
```
/forget <number>
```
```
/forget all
```
The memory file remains local and is excluded from Git.

---

⚙️ Model Modes

E.V. supports three model modes.

AUTO
```
/model auto
```

Automatic mode prefers Gemini and falls back to local Qwen when necessary.

```
           AUTO
             │
             ▼
      Check Gemini
        │       │
      YES       NO
        │       │
        ▼       ▼
     Gemini   Qwen
```
GEMINI

```
/model gemini
```
Forces E.V. to use Gemini.

```
E.V.
 │
 ▼
🌐 Gemini
 │
 ▼
Response
```

QWEN

```
/model qwen
```

Forces E.V. to use the local Qwen engine.
```
E.V.
 │
 ▼
🧠 Qwen
 │
 ▼
Response
```
You can also choose a model when launching E.V.

```
python jarvis.py --model gemini
```
```
python jarvis.py --model qwen
```
---

📦 Requirements

E.V. currently requires:

📱 Android
🖥️ Termux
🐍 Python 3
📦 requests
🧠 llama.cpp / llama-cli
🤖 Compatible Qwen GGUF model
🔑 Gemini API key

The Gemini API key is only required when using Gemini.

The local Qwen engine does not require a Gemini API key.

---

🧠 Qwen Model Setup

The Qwen model is not included in the repository because GGUF model files can be very large.

You must provide your own compatible model.

E.V. expects the local model inside:
```
~/jarvis/models/
```
The default model filename is:

Qwen2.5-3B-Instruct-Q4_K_M.gguf

Therefore the default full path is:
```
~/jarvis/models/Qwen2.5-3B-Instruct-Q4_K_M.gguf
```
Check the model directory:
```
ls -lh ~/jarvis/models/
```
Check whether "llama-cli" is available:
```
which llama-cli
```
A valid executable path should be returned.

---

🚀 Installation

1. Clone E.V.
```
git clone https://github.com/TonyStark679/Tarmix-Jarvis-for-termux-
```
Enter the project directory:
```
cd Tarmix-Jarvis-for-termux-
```
---

2. Install Python dependencies
```
pip install requests
```
---

3. Create the environment file

Copy the provided example:
```
cp .env.example .env
```
---

4. Configure Gemini

Open:
```
.env
```
Add your Gemini API key:
```
GEMINI_API_KEY=your_gemini_api_key_here
```
Set the default model mode:
```
JARVIS_MODEL=auto
```
Your final ".env" can look like:
```
GEMINI_API_KEY=your_gemini_api_key_here
JARVIS_MODEL=auto
```
«⚠️ Never publish your real API key.»

---

🧠 Installing the Local Model

Create the models directory if it does not already exist:
```
mkdir -p ~/jarvis/models
```
Place your Qwen GGUF model inside:
```
~/jarvis/models/
```
For the default configuration, the file should be:
```
~/jarvis/models/Qwen2.5-3B-Instruct-Q4_K_M.gguf
```
Verify it:
```
ls -lh ~/jarvis/models/
```
Then verify "llama-cli":
```
which llama-cli
```
---

▶️ Running E.V.

Start E.V. normally:
```
python E.V.py
```
You should see an initialization interface similar to:
```
        [ SYSTEM STATUS ]

    ◉ CORE ............... ON
    ◉ NETWORK ............ ONLINE
    ◉ GEMINI ............. READY
    ◉ QWEN ............... STANDBY
    ◉ MEMORY ............. LOADED

          E.V. ONLINE

You > Hello E.V.

Then simply start chatting.
```
---

🎮 Commands

Model
```
/model auto
```
/model gemini
```
/model qwen
```
Memory
```
/memory
```
/remember <fact>
```
/forget <number>
```
/forget all
```
Session
```
/clear
```
/status
```
/help
```
/exit
```
/quit
```
---

📁 Project Structure
```
Tarmix-Jarvis-for-termux-/
│
├── jarvis.py
│
├── local_ai.py
│
├── personality.txt
│
├── .env.example
│
├── .gitignore
│
├── memory.json
│
└── models/
    │
    └── *.gguf
```
File Overview
```
jarvis.py
    Main E.V. application

local_ai.py
    Local Qwen interface

personality.txt
    E.V. personality configuration

.env.example
    Environment configuration template

.gitignore
    Git exclusions

memory.json
    Persistent local memory

models/
    Local GGUF models
```
---

🔐 Security

Keep your API key inside:
```
.env
```
Never hard-code your real API key inside Python files.

Sensitive and local files should remain excluded from Git:
```
.env

memory.json

models/*

__pycache__/

*.pyc

*.gguf

*.save

*.save.*
```
🚨 If your API key is exposed

Immediately revoke the exposed key and generate a new one.

Then update:
```
.env
```
Never commit the old key to GitHub.

---

🛠️ Troubleshooting

🌐 Gemini is not working

Check your environment file:
``|
cat .env
```
Make sure a Gemini API key is present:
```
GEMINI_API_KEY=your_key_here
```
Check the selected model:
```
JARVIS_MODEL=auto
```
or:
```
JARVIS_MODEL=gemini
```
---

🧠 Qwen is not working

Check the model directory:
```
ls -lh ~/jarvis/models/
```
Check whether the model exists:
```
~/jarvis/models/Qwen2.5-3B-Instruct-Q4_K_M.gguf
```
Check "llama-cli":
```
which llama-cli
```
Force Qwen mode:
```
python jarvis.py --model qwen
```
---

🔍 Check Git status
```
git status
```
---

🎯 Project Goal

E.V. began as a simple terminal AI experiment and evolved into a hybrid assistant that can combine cloud intelligence with local inference.

The long-term goal is to make E.V. useful in both connected and disconnected environments.
```
                         ⚡ E.V.
                            │
                   ┌────────┴────────┐
                   │                 │
                INTERNET          NO INTERNET
                   │                 │
                   ▼                 ▼
              🌐 GEMINI          🧠 QWEN
              Cloud AI          Local AI
                   │                 │
                   └────────┬────────┘
                            │
                            ▼
                      ⚡ E.V. RESPONSE
```
The principle:

Cloud when available.
Local when necessary.
E.V. either way.

---

🗺️ Roadmap

E.V. is still evolving.

Planned or possible improvements include:

🎨 Advanced terminal UI

🧠 Improved local model management

💾 Smarter memory

🔧 More terminal tools

🖥️ System information and controls

🔌 Extensible AI provider system

⚡ Faster local inference

🤖 More capable autonomous workflows

🧩 Additional AI models

---

🤝 Contributing

E.V. is a personal project, but ideas, bug reports, improvements, and experiments are welcome.

You can contribute by improving the code, suggesting features, fixing bugs, or experimenting with new AI providers and local models.

---

📜 License

This project is licensed under the:

MIT License

---

<div align="center">⚡ E.V.

Enhanced Virtuality

Built for Termux.
Powered by AI.
Backed by local intelligence.

🧠 🌐 ⚡

</div>