import json

import requests


OLLAMA_BASE = "http://localhost:11434"
OLLAMA_URL = f"{OLLAMA_BASE}/api/generate"

MODEL = "qwen2.5-coder:1.5b"


def check_model():
    """Fail fast with a clear message if Ollama is down or the model is missing."""
    try:
        response = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        raise Exception(
            "Cannot reach Ollama on port 11434. "
            "Start the Ollama app (or run 'ollama serve') and try again."
        )

    names = [m.get("name", "") for m in response.json().get("models", [])]

    if MODEL not in names and f"{MODEL}:latest" not in names:
        raise Exception(
            f"Model '{MODEL}' is not installed. "
            f"Run: ollama pull {MODEL}"
        )


def build_prompt(file_tree, code_files):
    combined = ""

    for file in code_files:
        combined += f"\n===== FILE: {file['filename']} =====\n{file['code']}\n"

    if not combined:
        combined = "(No readable text files were found. Use the file list only.)"

    return f"""You are a software engineer who explains GitHub repositories to beginners.

Below are the repository's file list and the contents of its most important files.
The repository may contain application code, notebooks, documentation, or mostly data.
Explain what you can actually see.

Write a simple, clear explanation in plain English with these sections:
1. Project Overview
2. What the project does
3. Main Technologies
4. Important Features
5. How it works (step by step)
6. Important files and their purpose

Only describe what is present. Do not invent features.

FILE LIST:
{file_tree}

FILE CONTENTS:
{combined}
"""


def stream_explanation(file_tree, code_files):
    """Yield the explanation in small pieces as the model writes it."""
    prompt = build_prompt(file_tree, code_files)

    try:
        with requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": True,
                "keep_alive": "30m",
                "options": {"num_ctx": 4096, "temperature": 0.2},
            },
            stream=True,
            timeout=(10, 600),
        ) as response:

            if response.status_code != 200:
                yield f"\n\n[Ollama error: {response.text}]"
                return

            for line in response.iter_lines():
                if not line:
                    continue

                data = json.loads(line)

                if "error" in data:
                    yield f"\n\n[Ollama error: {data['error']}]"
                    return

                chunk = data.get("response", "")
                if chunk:
                    yield chunk

                if data.get("done"):
                    break

    except Exception as e:
        yield f"\n\n[Error while generating explanation: {e}]"
