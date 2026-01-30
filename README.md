# ✈️ AI Flight Booking Assistant

A conversational AI assistant that helps users search for flights, check flight status, and find schedules using real-time data from the Aviationstack API. Built with **OpenRouter** (GPT-4o-mini), **Streamlit**, and a **Jupyter/Gradio** notebook.

[![GitHub](https://img.shields.io/badge/GitHub-repo-24292e?logo=github)](https://github.com/techVasanthsmart/AI-Flight-Booking-Assistant)
[![Live Demo](https://img.shields.io/badge/Live_Demo-Streamlit-ff4b4b?logo=streamlit)](https://ai-flight-booking-assistant-qwyknk3lgu6qgjgaab7qvb.streamlit.app/)
[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/techVasanthsmart/AI-Flight-Booking-Assistant/blob/master/ai-flight-booking-assistant.ipynb)

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![OpenRouter](https://img.shields.io/badge/OpenRouter-API-green.svg)

## Features

- **Natural language chat** – Ask about flights in plain English (e.g. “Flights from JFK to LAX today”, “Status of flight AA100”).
- **Real-time flight data** – Powered by the [Aviationstack](https://aviationstack.com/) API.
- **Tool calling** – The assistant uses a flight search tool to fetch live data instead of guessing.
- **Streamlit UI** – Clean chat interface; [**try the live app**](https://ai-flight-booking-assistant-qwyknk3lgu6qgjgaab7qvb.streamlit.app/) or deploy on [Streamlit Cloud](https://share.streamlit.io).
- **Jupyter + Gradio** – Alternative notebook UI in `ai-flight-booking-assistant.ipynb`.

## Project structure

```
AI-Assistant/
├── streamlit_app.py              # Main Streamlit app (deploy to Streamlit Cloud)
├── ai-flight-booking-assistant.ipynb  # Jupyter notebook with Gradio chat UI
├── requirements.txt              # Python dependencies (Streamlit + Gradio)
├── .env.example                   # Sample env vars (copy to .env)
├── .streamlit/
│   └── config.toml               # Streamlit theme & config
└── README.md                      # This file
```

## Quick start

### 1. Clone and enter the repo

```bash
git clone https://github.com/techVasanthsmart/AI-Flight-Booking-Assistant.git
cd AI-Flight-Booking-Assistant
```

### 2. Create and activate virtual environment

**Windows (PowerShell):**

```bash
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Windows (CMD):**

```bash
py -m venv .venv
.venv\Scripts\activate.bat
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

Copy the sample env file and add your API keys:

```bash
copy .env.example .env   # Windows
# cp .env.example .env   # macOS / Linux
```

Edit `.env` and set:

- `OPENROUTER_API_KEY` – Your [OpenRouter](https://openrouter.ai/) API key (used for chat/tool calling).
- `CLIENTSECRET` – Your [Aviationstack](https://aviationstack.com/) API key (used for flight search).

Do not commit `.env`; it is listed in `.gitignore`.

### 5. Run the app

**Streamlit (recommended):**

```bash
streamlit run streamlit_app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

**Jupyter notebook (Gradio):**

1. Open `ai-flight-booking-assistant.ipynb` and select the `.venv` kernel.
2. Run all cells; the last cell launches the Gradio chat UI.

## Deploy on Streamlit Cloud

1. Push this repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. **New app** → select this repo, branch `main`, main file `streamlit_app.py`.
4. In **Settings → Secrets**, add:

   ```toml
   OPENROUTER_API_KEY = "your-openrouter-api-key"
   CLIENTSECRET = "your-aviationstack-api-key"
   ```

5. Deploy. Your app will get a URL like `https://your-app-name.streamlit.app/`.  
   **Live demo:** [ai-flight-booking-assistant.streamlit.app](https://ai-flight-booking-assistant-qwyknk3lgu6qgjgaab7qvb.streamlit.app/)  
   See [DEPLOY_STREAMLIT.md](DEPLOY_STREAMLIT.md) for full steps.

## Tech stack

- **Python 3.9+**
- **Streamlit** – Web UI (Streamlit app)
- **Gradio** – Chat UI in Jupyter notebook
- **OpenRouter API** – LLM (GPT-4o-mini) with function/tool calling
- **Aviationstack API** – Flight data
- **python-dotenv** – Local env loading

## API keys

| Variable             | Purpose                       | Get it from                                     |
| -------------------- | ----------------------------- | ----------------------------------------------- |
| `OPENROUTER_API_KEY` | Chat and tool calling         | [openrouter.ai](https://openrouter.ai/)         |
| `CLIENTSECRET`       | Flight search (Aviationstack) | [aviationstack.com](https://aviationstack.com/) |

## License

MIT (or your chosen license).

## Contributing

1. Fork the repo.
2. Create a branch (`git checkout -b feature/your-feature`).
3. Commit changes (`git commit -m 'feat: add your feature'`).
4. Push and open a Pull Request.
