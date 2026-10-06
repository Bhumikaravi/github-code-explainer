# GitHub Repository Code Explainer

Paste a public GitHub repository URL and get a simple, beginner-friendly
explanation written by a local AI model (Ollama). Nothing leaves your computer.

## How it works

1. You enter a GitHub URL in the Streamlit page.
2. The FastAPI backend clones the repo (latest snapshot only).
3. It picks the most useful files (README, config, code, notebooks, CSV previews).
4. It sends them to a local Ollama model, which streams the explanation back.

## Project structure

```
github-code-explainer/
├── backend/
│   ├── main.py                  # FastAPI app (POST /explain)
│   └── services/
│       ├── repo_processor.py    # clone repo, choose and read files
│       └── llm_service.py       # talk to Ollama, stream the answer
├── frontend/
│   └── app.py                   # Streamlit page
└── requirements.txt
```

## Setup (one time)

1. Install [Ollama](https://ollama.com) and [Git](https://git-scm.com).
2. Download the model:
   ```powershell
   ollama pull qwen2.5-coder:1.5b
   ```
3. Create a virtual environment and install packages:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

## Run (two terminals, both from the project root)

Terminal 1 - backend:
```powershell
.\venv\Scripts\Activate.ps1
uvicorn backend.main:app --reload
```

Terminal 2 - frontend:
```powershell
.\venv\Scripts\Activate.ps1
streamlit run frontend/app.py
```

Open http://localhost:8501, paste a repo URL, and click **Explain Repository**.

Ollama must be running. If you see "port already in use" when running
`ollama serve`, it is already running and you can ignore that.

## Tips

- First request is the slowest (the model loads into memory).
- To make it faster, lower `MAX_TOTAL_CHARS` in `backend/services/repo_processor.py`.
- To change the model, edit `MODEL` in `backend/services/llm_service.py`.
- Only public repositories are supported.
