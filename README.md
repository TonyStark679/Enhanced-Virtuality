# 🤖 JARVIS

> A lightweight AI assistant for Termux with automatic Gemini ↔ Qwen fallback.

JARVIS is a personal AI assistant designed to run directly on Android through Termux.

### ✨ Features

- 🌐 **Gemini** when internet is available
- 🧠 **Qwen 2.5 3B** locally when offline
- 🔄 Automatic online/offline model switching
- 💾 Simple persistent memory
- 🎭 Custom personality
- ⚙️ Manual model selection with `/model`

### ✍🏻 NOTE:
-Add api key to .env.

-To use qwen (offline mode) turn off your internet/Wi-Fi 
and then type into the prompt area.

### 🚀 Setup

Requires **Termux, Python 3, `requests`, `llama-cli`, a Qwen GGUF model, and a Gemini API key.**

```bash
git clone https://github.com/TonyStark679/jarvis.git
cd jarvis
pip install requests
cp .env.example .env
python jarvis.py

