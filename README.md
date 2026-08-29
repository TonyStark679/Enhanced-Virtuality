⚡ E.V. | Enhanced Virtuality

«One assistant. Two brains. No Wi-Fi panic.»

E.V. (Enhanced Virtuality) is a lightweight personal AI assistant built for Android + Termux.

E.V. combines Google Gemini for online intelligence with a locally running Qwen 2.5 3B GGUF model for offline use. When configured for automatic mode, E.V. can use Gemini when available and fall back to local Qwen when Gemini cannot be used.

The philosophy is simple:

«Use the best available brain. 🧠»

---

✨ Features

- 🌐 Gemini integration for online AI
- 🧠 Qwen 2.5 3B for local/offline AI
- 🔄 Automatic Gemini → Qwen fallback
- 🎭 Customizable personality
- 💾 Persistent local memory
- ⚙️ Manual model selection
- 📱 Built specifically for Android + Termux
- 🖥️ Fully terminal-based
- 🔐 Local environment configuration
- 📴 Offline-capable through local Qwen
- ⚡ Lightweight architecture
- ☁️ No mandatory cloud dependency for local mode

---

🧠 How E.V. Works

E.V. has two AI engines:

flowchart TD
    A["⚡ E.V.<br/>Enhanced Virtuality"] --> B{"Choose Model"}

    B -->|AUTO| C["Check Gemini"]
    B -->|MANUAL| D{"Selected Model"}

    C -->|Available| E["🌐 GEMINI<br/>Cloud AI"]
    C -->|Unavailable| F["🧠 QWEN<br/>Local GGUF"]

    D -->|Gemini| E
    D -->|Qwen| F

    E --> G["⚡ E.V. Response"]
    F --> G

🌐 Gemini

Gemini is E.V.'s cloud-based AI engine.

When Gemini mode is active and a valid API key is available, E.V. sends the conversation to Google's Gemini API and uses the returned response.

🧠 Qwen

Qwen is E.V.'s local AI engine.

E.V. runs a compatible Qwen GGUF model locally through:

llama-cli

Because the model runs directly on the device, Qwen mode can operate without an internet connection.

---

🔄 Automatic Fallback

In:

auto

mode, E.V. attempts to use Gemini first.

If Gemini is unavailable, E.V. can switch to the local Qwen engine.

flowchart TD
    A["⚡ E.V."] --> B{"Internet / Gemini Available?"}

    B -->|YES| C["🌐 Gemini"]
    B -->|NO| D["🧠 Local Qwen"]

    C --> E["⚡ E.V. Response"]
    D --> E

Wi-Fi down? Qwen clocks in. 🫡

---

🎭 Personality

E.V.'s personality is stored separately from the Python source code.

personality.txt

This allows you to modify E.V.'s identity, behavior, and conversational style without modifying the main application.

Default identity:

E.V. | Enhanced Virtuality

You can customize this file to make E.V. behave the way you want.

---

💾 Memory

E.V. includes a lightweight persistent memory system.

Memory is stored locally in:

memory.json

Supported memory commands include:

/memory
/remember <fact>
/forget <number>
/forget all

Memory remains on the device and is excluded from Git through:

.gitignore

---

⚙️ Model Modes

E.V. supports three model modes.

Automatic

/model auto

E.V. prefers Gemini and falls back to Qwen when necessary.

Gemini

/model gemini

Forces E.V. to use Gemini.

Qwen

/model qwen

Forces E.V. to use the local Qwen model.

You can also select the model when launching E.V.:

python jarvis.py --model qwen

or:

python jarvis.py --model gemini

---

📦 Requirements

E.V. currently requires:

- 📱 Android
- 🖥️ Termux
- 🐍 Python 3
- 📦 Python "requests"
- 🧠 "llama.cpp" / "llama-cli"
- 🤖 A compatible Qwen GGUF model
- 🔑 A Gemini API key for Gemini mode

Qwen Model

The Qwen model is not included in this repository because GGUF model files can be very large.

You must provide your own compatible model.

The default model filename is:

Qwen2.5-3B-Instruct-Q4_K_M.gguf

---

🚀 Installation

1. Clone the repository

git clone https://github.com/TonyStark679/Tarmix-Jarvis-for-termux-

Enter the project directory:

cd Tarmix-Jarvis-for-termux-

2. Install Python dependencies

pip install requests

3. Create the environment file

Copy the provided template:

cp .env.example .env

4. Configure Gemini

Open:

.env

and add your Gemini API key:

GEMINI_API_KEY=your_gemini_api_key_here
JARVIS_MODEL=auto

«⚠️ Important: Never publish your real API key.»

---

🧠 Setting Up Local Qwen

E.V. uses:

llama-cli

to run the local GGUF model.

Create the model directory if necessary:

mkdir -p ~/jarvis/models

Place your Qwen GGUF model inside:

~/jarvis/models/

The default model path is:

~/jarvis/models/Qwen2.5-3B-Instruct-Q4_K_M.gguf

Check that the model exists:

ls -lh ~/jarvis/models/

Then check whether:

llama-cli

is available:

which llama-cli

If the command returns a valid executable path, the local Qwen engine should be available.

---

▶️ Running E.V.

Start E.V. with:

python jarvis.py

You should see the E.V. initialization interface followed by the main prompt.

Example:

        [ SYSTEM STATUS ]

    ◉ CORE ............... ON
    ◉ NETWORK ............ ONLINE
    ◉ GEMINI ............. READY
    ◉ QWEN ............... STANDBY
    ◉ MEMORY ............. LOADED

          E.V. ONLINE

You > Hello E.V.

Then start chatting.

---

⚙️ Commands

🤖 Model

/model auto
/model gemini
/model qwen

💾 Memory

/memory
/remember <fact>
/forget <number>
/forget all

🖥️ Session

/clear
/status
/help
/exit
/quit

---

📁 Project Structure

Tarmix-Jarvis-for-termux/
│
├── jarvis.py
├── local_ai.py
├── personality.txt
├── .env.example
├── .gitignore
│
├── memory.json
│
└── models/
    └── *.gguf

Main Files

File| Purpose
"jarvis.py"| Main E.V. application
"local_ai.py"| Local Qwen interface
"personality.txt"| E.V. personality configuration
".env.example"| Environment configuration template
".gitignore"| Git exclusions
"memory.json"| Persistent local memory
"models/"| Local GGUF models

---

🔐 Security

API keys should be stored in:

.env

Never place real API keys directly inside Python source code.

The repository is configured to ignore sensitive and local files such as:

.env
memory.json
models/*
__pycache__/
*.pyc
*.gguf
*.save
*.save.*

🚨 If an API key is exposed

Immediately:

1. Revoke the exposed key.
2. Generate a new key.
3. Replace the key in:

.env

4. Make sure the old key is not committed to Git.

---

🛠️ Troubleshooting

🌐 Gemini Isn't Working

Check your environment file:

cat .env

Make sure it contains:

GEMINI_API_KEY=your_key_here

Also check the selected model:

JARVIS_MODEL=auto

or:

JARVIS_MODEL=gemini

---

🧠 Qwen Isn't Working

Check that the model exists:

ls -lh ~/jarvis/models/

Then check:

llama-cli

with:

which llama-cli

You can force Qwen mode with:

python jarvis.py --model qwen

---

🔍 Check Repository State

git status

---

🎯 Project Goal

E.V. started as a simple terminal AI experiment and evolved into a hybrid assistant capable of switching between cloud and local intelligence.

The long-term goal is to build an assistant that remains useful regardless of network availability.

flowchart TD
    A["⚡ E.V.<br/>Enhanced Virtuality"] --> B{"Internet Available?"}

    B -->|YES| C["🌐 GEMINI<br/>Cloud AI"]
    B -->|NO| D["🧠 QWEN<br/>Local AI"]

    C --> E["⚡ E.V."]
    D --> E

The idea is straightforward:

Use cloud intelligence when available.
Use local intelligence when necessary.

---

🗺️ Roadmap

E.V. is still evolving.

Possible future improvements include:

- 🎨 More advanced terminal UI
- 🧠 Improved local model management
- 💾 Smarter memory
- 🔧 More terminal tools
- 🖥️ System information and device controls
- 🔌 Extensible AI provider system
- ⚡ Faster local inference
- 🤖 More capable autonomous workflows
- 🧩 Additional local and cloud models

---

🤝 Contributing

E.V. is a personal project, but improvements, ideas, bug reports, and experiments are welcome.

If you find a problem or have an idea for E.V., feel free to open an issue or contribute to the project.

---

📜 License

This project is licensed under the MIT License.

---

<div align="center">⚡ E.V.

Enhanced Virtuality

Built for Termux.
Powered by AI.
Backed by local intelligence.

🧠 🌐 ⚡

</div>