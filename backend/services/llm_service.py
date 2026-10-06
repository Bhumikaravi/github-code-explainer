import os
import streamlit as st
from google import genai
from google.genai import types


MODEL = "gemini-2.5-flash"


def get_api_key():
    """Get Gemini API key from Streamlit Secrets or environment variables."""

    try:
        key = st.secrets.get("GEMINI_API_KEY")
        if key:
            return key
    except Exception:
        pass

    key = os.getenv("GEMINI_API_KEY")

    if key:
        return key

    raise Exception(
        "GEMINI_API_KEY is not configured. "
        "Add it to Streamlit Cloud Secrets."
    )


def get_client():
    """Create the Gemini client."""

    api_key = get_api_key()
    return genai.Client(api_key=api_key)


def check_model():
    """Check that the Gemini API key is available."""

    get_api_key()


def build_prompt(file_tree, code_files):
    """Build the prompt used to explain the repository."""

    combined = ""

    for file in code_files:
        combined += (
            f"\n===== FILE: {file['filename']} =====\n"
            f"{file['code']}\n"
        )

    if not combined:
        combined = (
            "(No readable text files were found. "
            "Use the file list only.)"
        )

    return f"""
You are a software engineer who explains GitHub repositories to beginners.

Below are the repository's file list and the contents of its most important
files.

The repository may contain application code, notebooks, documentation,
configuration files, or data.

Explain only what you can actually see.

Write a simple, clear explanation in plain English using these sections:

1. Project Overview
2. What the project does
3. Main Technologies
4. Important Features
5. How it works (step by step)
6. Important files and their purpose

Only describe what is present in the repository.
Do not invent features or functionality.

FILE LIST:
{file_tree}

FILE CONTENTS:
{combined}
"""


def stream_explanation(file_tree, code_files):
    """Generate the repository explanation using Gemini."""

    try:
        client = get_client()
        prompt = build_prompt(file_tree, code_files)

        response = client.models.generate_content_stream(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=4096,
            ),
        )

        for chunk in response:
            text = getattr(chunk, "text", None)

            if text:
                yield text

    except Exception as e:
        yield f"\n\n[Gemini error: {e}]"