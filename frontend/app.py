import html
import re
 
import requests
import streamlit as st
 
 
API_URL = "http://127.0.0.1:8000/explain"
 
st.set_page_config(
    page_title="GitHub Code Explainer",
    page_icon="💻",
    layout="centered",
)
 
 
# ---------------------------------------------------------------------------
# Colour themes. Pick one from the dropdown on the page, or change the
# default by editing DEFAULT_THEME. To make your own, copy a block and
# change the hex colours.
# ---------------------------------------------------------------------------
DEFAULT_THEME = "Sunset"
 
THEMES = {
    # Purple to orange gradient background
    "Sunset": {
        "bg": "#3B1C5A",
        "bg-image": "radial-gradient(var(--dot) 1px, transparent 1px), linear-gradient(160deg, #3B1C5A 0%, #8A2F5B 55%, #B8482F 100%)",
        "bg-size": "24px 24px, 100% 100%",
        "panel": "#3A1A52", "edge": "#A8629B",
        "text": "#FFF1F5", "muted": "#F2C8D6", "title": "#FFFFFF",
        "accent": "#FFB36B", "accent-hover": "#FFC48A", "accent-ink": "#3A1500",
        "badge": "#FFE08A", "badge-ink": "#3A2A00",
        "paper": "#FFF8F3", "ink": "#3A1A2E", "field": "#2C1040",
        "steps-bg": "rgba(58,26,82,0.65)", "dot": "rgba(255,255,255,0.10)",
        "focus": "rgba(255,179,107,0.35)", "shadow": "rgba(0,0,0,0.4)",
    },
    # Dark blue to teal gradient background
    "Aurora": {
        "bg": "#0A1A3F",
        "bg-image": "radial-gradient(var(--dot) 1px, transparent 1px), linear-gradient(160deg, #0A1A3F 0%, #0E4A5C 55%, #14705F 100%)",
        "bg-size": "24px 24px, 100% 100%",
        "panel": "#0F2F45", "edge": "#2E6A7E",
        "text": "#E7FAF5", "muted": "#A9D9D0", "title": "#FFFFFF",
        "accent": "#5EEAD4", "accent-hover": "#8CF2E1", "accent-ink": "#032B27",
        "badge": "#FDE68A", "badge-ink": "#3A2A00",
        "paper": "#F4FBFA", "ink": "#0F2A33", "field": "#0A2230",
        "steps-bg": "rgba(15,47,69,0.7)", "dot": "rgba(169,217,208,0.12)",
        "focus": "rgba(94,234,212,0.28)", "shadow": "rgba(0,0,0,0.4)",
    },
    # Light pink, peach and lavender gradient background
    "Peach": {
        "bg": "#FFE9DC",
        "bg-image": "radial-gradient(var(--dot) 1px, transparent 1px), linear-gradient(135deg, #FFE9DC 0%, #FFD9E8 50%, #DCE6FF 100%)",
        "bg-size": "24px 24px, 100% 100%",
        "panel": "#FFFFFF", "edge": "#F0C9D6",
        "text": "#3A2230", "muted": "#7A5A68", "title": "#2A1420",
        "accent": "#D6336C", "accent-hover": "#BF2A5E", "accent-ink": "#FFFFFF",
        "badge": "#FFC857", "badge-ink": "#2A1E00",
        "paper": "#FFFFFF", "ink": "#3A2230", "field": "#FFF7F2",
        "steps-bg": "rgba(255,255,255,0.7)", "dot": "rgba(214,51,108,0.10)",
        "focus": "rgba(214,51,108,0.25)", "shadow": "rgba(120,40,70,0.15)",
    },
    # Plain white with black accents
    "Mono": {
        "bg": "#FFFFFF",
        "panel": "#F4F4F5", "edge": "#D4D4D8",
        "text": "#18181B", "muted": "#52525B", "title": "#000000",
        "accent": "#111111", "accent-hover": "#333333", "accent-ink": "#FFFFFF",
        "badge": "#111111", "badge-ink": "#FFFFFF",
        "paper": "#FFFFFF", "ink": "#18181B", "field": "#FFFFFF",
        "steps-bg": "#FAFAFA", "dot": "rgba(0,0,0,0.09)",
        "focus": "rgba(0,0,0,0.2)", "shadow": "rgba(0,0,0,0.12)",
    },
    # Light blue background, white panels
    "Ocean": {
        "bg": "#E8F1FF", "panel": "#FFFFFF", "edge": "#C3D5F0",
        "text": "#16233F", "muted": "#4B6088", "title": "#0E1A33",
        "accent": "#1F6FEB", "accent-hover": "#1A5ECB", "accent-ink": "#FFFFFF",
        "badge": "#FFC857", "badge-ink": "#2A1E00",
        "paper": "#FFFFFF", "ink": "#16233F", "field": "#F3F8FF",
        "steps-bg": "rgba(255,255,255,0.75)", "dot": "rgba(31,111,235,0.15)",
        "focus": "rgba(31,111,235,0.25)", "shadow": "rgba(22,44,100,0.14)",
    },
    # Deep green background
    "Forest": {
        "bg": "#0D2B22", "panel": "#143A2D", "edge": "#2A5E4B",
        "text": "#E6F4EC", "muted": "#A5C7B6", "title": "#FFFFFF",
        "accent": "#7FD8AC", "accent-hover": "#9BE3BF", "accent-ink": "#06251A",
        "badge": "#F2C14E", "badge-ink": "#2A1E00",
        "paper": "#F6FAF7", "ink": "#14281F", "field": "#0A221A",
        "steps-bg": "rgba(20,58,45,0.7)", "dot": "rgba(165,199,182,0.14)",
        "focus": "rgba(127,216,172,0.28)", "shadow": "rgba(0,0,0,0.35)",
    },
    # Purple background
    "Plum": {
        "bg": "#2A1038", "panel": "#3B1A4F", "edge": "#5E3680",
        "text": "#F5E9FA", "muted": "#CBB0D8", "title": "#FFFFFF",
        "accent": "#FF8FC7", "accent-hover": "#FFA9D4", "accent-ink": "#3A0A25",
        "badge": "#FFD166", "badge-ink": "#2A1E00",
        "paper": "#FBF7FD", "ink": "#2A1536", "field": "#220C2D",
        "steps-bg": "rgba(59,26,79,0.7)", "dot": "rgba(203,176,216,0.15)",
        "focus": "rgba(255,143,199,0.28)", "shadow": "rgba(0,0,0,0.38)",
    },
    # Neutral dark grey background
    "Graphite": {
        "bg": "#1D1F24", "panel": "#272A31", "edge": "#3F434D",
        "text": "#ECEEF2", "muted": "#A7ADBA", "title": "#FFFFFF",
        "accent": "#FF9F43", "accent-hover": "#FFB264", "accent-ink": "#2B1700",
        "badge": "#8AB4FF", "badge-ink": "#0B1A33",
        "paper": "#F5F5F7", "ink": "#1D1F24", "field": "#17191D",
        "steps-bg": "rgba(39,42,49,0.7)", "dot": "rgba(167,173,186,0.12)",
        "focus": "rgba(255,159,67,0.28)", "shadow": "rgba(0,0,0,0.4)",
    },
}
 
 
DEFAULT_BACKGROUND = {
    "bg-image": "radial-gradient(var(--dot) 1px, transparent 1px)",
    "bg-size": "24px 24px",
}
 
 
def theme_variables(theme):
    merged = {**DEFAULT_BACKGROUND, **theme}
    return ":root{" + "".join(f"--{k}:{v};" for k, v in merged.items()) + "}"
 
 
CSS = """
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&family=Sora:wght@600;700&display=swap');
 
/* ---------- Page background with a faint dot grid ---------- */
.stApp {
    background-color: var(--bg);
    background-image: var(--bg-image);
    background-size: var(--bg-size);
    background-attachment: fixed;
    font-family: 'DM Sans', system-ui, sans-serif;
    color: var(--text);
}
 
.stApp header[data-testid="stHeader"] { background: transparent; }
.stApp .stAppDeployButton,
.stApp [data-testid="stMainMenu"] { display: none; }
.stApp footer { visibility: hidden; }
.stApp [data-testid="stStatusWidget"] * { color: var(--muted); }
.stApp [data-testid="stSpinner"] * { color: var(--muted); }
 
.stApp .block-container {
    max-width: 860px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}
 
/* ---------- Theme dropdown ---------- */
.stApp div[data-baseweb="select"] > div {
    background: var(--panel);
    border: 1px solid var(--edge);
    border-radius: 10px;
}
.stApp div[data-baseweb="select"] * { color: var(--text); }
.stApp div[data-baseweb="select"] svg { fill: var(--muted); }
 
/* ---------- Title section ---------- */
.stApp .hero-title {
    font-family: 'Sora', system-ui, sans-serif;
    font-weight: 700;
    font-size: 2.6rem;
    line-height: 1.12;
    letter-spacing: -0.02em;
    color: var(--title);
    margin: 0.6rem 0 0.9rem 0;
}
 
.stApp .hero-sub {
    color: var(--muted);
    font-size: 1.1rem;
    line-height: 1.6;
    max-width: 58ch;
    margin: 0;
}
 
.stApp .steps {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    margin: 1.9rem 0 2rem 0;
    border: 1px solid var(--edge);
    border-radius: 14px;
    overflow: hidden;
    background: var(--steps-bg);
}
 
.stApp .step {
    display: flex;
    gap: 0.8rem;
    align-items: flex-start;
    padding: 1rem 1.15rem;
    border-right: 1px solid var(--edge);
}
 
.stApp .step:last-child { border-right: none; }
 
.stApp .step-num {
    flex: 0 0 auto;
    width: 1.7rem;
    height: 1.7rem;
    border-radius: 50%;
    background: var(--badge);
    color: var(--badge-ink);
    font-family: 'JetBrains Mono', monospace;
    font-weight: 500;
    font-size: 0.85rem;
    display: flex;
    align-items: center;
    justify-content: center;
}
 
.stApp .step-title { font-weight: 600; color: var(--title); margin-bottom: 0.15rem; }
.stApp .step-text { color: var(--muted); font-size: 0.9rem; line-height: 1.45; }
 
/* ---------- Input section ---------- */
.stApp .st-key-input_panel {
    background: var(--panel);
    border: 1px solid var(--edge);
    border-radius: 16px;
    padding: 1.4rem 1.5rem 1.5rem 1.5rem;
}
 
.stApp .panel-title {
    font-family: 'Sora', system-ui, sans-serif;
    font-weight: 600;
    font-size: 1.15rem;
    color: var(--title);
    margin-bottom: 0.25rem;
}
 
.stApp .panel-hint {
    color: var(--muted);
    font-size: 0.92rem;
    margin-bottom: 0.9rem;
}
 
.stApp div[data-baseweb="input"] {
    background: var(--field);
    border: 1px solid var(--edge);
    border-radius: 10px;
}
 
.stApp div[data-baseweb="base-input"] { background: transparent; }
 
.stApp div[data-baseweb="input"]:focus-within {
    border-color: var(--accent);
    box-shadow: 0 0 0 3px var(--focus);
}
 
.stApp div[data-baseweb="input"] input {
    color: var(--text);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.92rem;
}
 
.stApp div[data-baseweb="input"] input::placeholder { color: var(--muted); opacity: 0.8; }
 
.stApp .stButton > button {
    background: var(--accent);
    color: var(--accent-ink);
    border: 0;
    border-radius: 10px;
    font-family: 'DM Sans', system-ui, sans-serif;
    font-weight: 600;
    padding: 0.65rem 1.5rem;
}
 
.stApp .stButton > button p { color: inherit; font-weight: 600; }
.stApp .stButton > button:hover { background: var(--accent-hover); color: var(--accent-ink); }
.stApp .stButton > button:focus-visible { outline: 3px solid var(--badge); outline-offset: 2px; }
 
/* ---------- Messages ---------- */
.stApp [data-testid="stAlert"] {
    background: var(--panel);
    border: 1px solid var(--edge);
    border-left: 5px solid var(--accent);
    border-radius: 12px;
}
.stApp [data-testid="stAlert"] * { color: var(--text); }
 
/* ---------- Result section ---------- */
.stApp .summary {
    display: flex;
    flex-wrap: wrap;
    align-items: baseline;
    gap: 0.4rem 1.4rem;
    width: fit-content;
    max-width: 100%;
    margin: 2rem 0 0.9rem 0;
    padding: 0.5rem 1rem;
    background: var(--panel);
    border: 1px solid var(--edge);
    border-radius: 999px;
    color: var(--muted);
}
 
.stApp .summary .repo {
    font-family: 'JetBrains Mono', monospace;
    color: var(--accent);
    font-weight: 500;
    font-size: 1rem;
}
 
.stApp .st-key-explanation {
    background: var(--paper);
    border: 1px solid var(--edge);
    border-left: 6px solid var(--badge);
    border-radius: 14px;
    padding: 1.8rem 2.1rem;
    box-shadow: 0 18px 40px var(--shadow);
}
 
.stApp .st-key-explanation,
.stApp .st-key-explanation p,
.stApp .st-key-explanation li,
.stApp .st-key-explanation span,
.stApp .st-key-explanation strong {
    color: var(--ink);
}
 
.stApp .st-key-explanation p,
.stApp .st-key-explanation li {
    font-size: 1.02rem;
    line-height: 1.7;
    max-width: 72ch;
}
 
.stApp .st-key-explanation h1,
.stApp .st-key-explanation h2,
.stApp .st-key-explanation h3,
.stApp .st-key-explanation h4 {
    font-family: 'Sora', system-ui, sans-serif;
    color: var(--ink);
    margin-top: 1.4rem;
}
 
.stApp .st-key-explanation code {
    background: rgba(120, 130, 160, 0.18);
    color: var(--ink);
    padding: 0.1rem 0.35rem;
    border-radius: 5px;
}
 
.stApp .stDownloadButton > button {
    margin-top: 1rem;
    background: transparent;
    color: var(--accent);
    border: 1px solid var(--edge);
    border-radius: 10px;
    font-weight: 600;
}
 
.stApp .stDownloadButton > button p { color: inherit; }
.stApp .stDownloadButton > button:hover { border-color: var(--accent); color: var(--accent-hover); }
.stApp .stDownloadButton > button:focus-visible { outline: 3px solid var(--badge); outline-offset: 2px; }
 
/* ---------- Small screens ---------- */
@media (max-width: 640px) {
    .stApp .hero-title { font-size: 2rem; }
    .stApp .steps { grid-template-columns: 1fr; }
    .stApp .step { border-right: none; border-bottom: 1px solid var(--edge); }
    .stApp .step:last-child { border-bottom: none; }
    .stApp .st-key-explanation { padding: 1.2rem 1.2rem; }
}
"""
 
HERO_HTML = (
    '<div class="hero">'
    '<div class="hero-title">Understand any GitHub repository in plain English</div>'
    '<p class="hero-sub">Paste a public repository link. A model running on your own '
    'computer reads the key files and explains what the project does, how it works, '
    'and where to start.</p>'
    '<div class="steps">'
    '<div class="step"><span class="step-num">1</span><div>'
    '<div class="step-title">Paste a link</div>'
    '<div class="step-text">Any public GitHub repository.</div></div></div>'
    '<div class="step"><span class="step-num">2</span><div>'
    '<div class="step-title">Key files are picked</div>'
    '<div class="step-text">README, config, code, notebooks and data previews.</div></div></div>'
    '<div class="step"><span class="step-num">3</span><div>'
    '<div class="step-title">Read the explanation</div>'
    '<div class="step-text">Written for beginners. Download it as Markdown.</div></div></div>'
    '</div></div>'
)
 
 
def repo_name(url):
    match = re.search(r"github\.com/([^/\s]+/[^/\s#?]+)", url)
    if not match:
        return url
    name = match.group(1)
    return name[:-4] if name.endswith(".git") else name
 
 
def render_summary(url, files_read):
    st.markdown(
        '<div class="summary">'
        f'<span class="repo">{html.escape(repo_name(url))}</span>'
        f'<span>{html.escape(str(files_read))} files read</span>'
        '</div>',
        unsafe_allow_html=True,
    )
 
 
# The dropdown below stores its value under the key "theme", so we can read
# the choice here, before the dropdown is drawn, and style the whole page.
theme_name = st.session_state.get("theme", DEFAULT_THEME)
if theme_name not in THEMES:
    theme_name = DEFAULT_THEME
 
st.markdown(
    "<style>" + theme_variables(THEMES[theme_name]) + CSS + "</style>",
    unsafe_allow_html=True,
)
 
if "result" not in st.session_state:
    st.session_state.result = None
 
 
_, theme_col = st.columns([4, 1])
with theme_col:
    st.selectbox(
        "Theme",
        list(THEMES),
        index=list(THEMES).index(DEFAULT_THEME),
        key="theme",
        label_visibility="collapsed",
    )
 
st.markdown(HERO_HTML, unsafe_allow_html=True)
 
 
# ---------------- Input section ----------------
with st.container(key="input_panel"):
    st.markdown(
        '<div class="panel-title">Choose a repository</div>'
        '<div class="panel-hint">Public repositories only. '
        'Try a small one first, like https://github.com/octocat/Hello-World</div>',
        unsafe_allow_html=True,
    )
    repo_url = st.text_input(
        "GitHub repository URL",
        placeholder="https://github.com/username/repository",
        label_visibility="collapsed",
    )
    clicked = st.button("Explain repository")
 
 
# ---------------- Result section ----------------
if clicked:
    url = repo_url.strip()
    st.session_state.result = None
 
    if not url:
        st.warning("Enter a GitHub repository URL to continue.")
 
    else:
        try:
            with st.spinner("Cloning the repository and picking the key files..."):
                response = requests.post(
                    API_URL,
                    json={"repo_url": url},
                    stream=True,
                    timeout=(10, 900),
                )
 
            if response.status_code != 200:
                try:
                    detail = response.json().get("detail", "Something went wrong.")
                except ValueError:
                    detail = response.text or "Something went wrong."
                st.error(detail)
 
            else:
                files_read = response.headers.get("X-Files-Analyzed", "?")
                render_summary(url, files_read)
 
                response.encoding = "utf-8"
 
                with st.container(key="explanation"):
                    with st.spinner(
                        "The model is reading the code. "
                        "The first words can take a minute on a laptop."
                    ):
                        text = st.write_stream(
                            response.iter_content(
                                chunk_size=None, decode_unicode=True
                            )
                        )
 
                st.session_state.result = {
                    "url": url,
                    "files_read": files_read,
                    "text": text,
                }
 
        except requests.exceptions.ReadTimeout:
            st.error(
                "The model took too long to respond. "
                "Try again, or switch to a smaller model."
            )
 
        except requests.exceptions.ConnectionError:
            st.error(
                "Could not reach the backend. Start it with: "
                "uvicorn backend.main:app --reload"
            )
 
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")
 
elif st.session_state.result:
    saved = st.session_state.result
    render_summary(saved["url"], saved["files_read"])
    with st.container(key="explanation"):
        st.markdown(saved["text"])
 
 
if st.session_state.result:
    saved = st.session_state.result
    st.download_button(
        "Download as Markdown",
        data=saved["text"],
        file_name=repo_name(saved["url"]).replace("/", "-") + "-explanation.md",
        mime="text/markdown",
    )
 








