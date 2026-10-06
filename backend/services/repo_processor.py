import json
import os
import re
import shutil
import stat
import tempfile

from git import Repo


IGNORE_DIRS = {
    "node_modules",
    "__pycache__",
    "venv",
    "dist",
    "build",
    "vendor",
    "target",
    "out",
    "coverage",
    "site-packages",
}

IGNORE_FILES = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "poetry.lock",
    "pipfile.lock",
    "composer.lock",
    "cargo.lock",
}

CODE_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".kt",
    ".cpp",
    ".c",
    ".h",
    ".cs",
    ".go",
    ".rs",
    ".php",
    ".rb",
    ".swift",
    ".scala",
    ".r",
    ".m",
    ".sh",
    ".ps1",
    ".html",
    ".css",
    ".scss",
    ".sql",
    ".vue",
    ".dart",
}

DATA_EXTENSIONS = {
    ".csv",
    ".tsv",
}

TEXT_EXTENSIONS = {
    ".md",
    ".txt",
    ".rst",
    ".json",
    ".yml",
    ".yaml",
    ".toml",
    ".cfg",
    ".ini",
}

CONFIG_NAMES = {
    "requirements.txt",
    "package.json",
    "pyproject.toml",
    "setup.py",
    "pom.xml",
    "build.gradle",
    "dockerfile",
    "docker-compose.yml",
    "makefile",
    "cargo.toml",
    "go.mod",
    "gemfile",
    "composer.json",
}

ENTRY_NAMES = {
    "main",
    "app",
    "index",
    "server",
    "run",
    "manage",
    "cli",
    "__main__",
}


# Keep the amount of repository content sent to the AI manageable.
MAX_FILES = 20
MAX_CHARS_PER_FILE = 2000
MAX_TOTAL_CHARS = 4000
CSV_PREVIEW_LINES = 4
MAX_NOTEBOOK_BYTES = 20_000_000


def _force_remove(func, path, _exc_info):
    """
    Windows may keep .git files read-only.
    Clear the read-only flag and retry.
    """
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass


def cleanup_repository(repo_path):
    """
    Remove the temporary cloned repository.
    """
    if repo_path and os.path.exists(repo_path):
        shutil.rmtree(
            repo_path,
            onerror=_force_remove,
        )


def normalize_repo_url(url):
    """
    Accept common GitHub URL styles and return a clean clone URL.
    """

    url = (url or "").strip()

    # Remove trailing slash
    url = url.rstrip("/")

    match = re.match(
        r"^(?:https?://)?(?:www\.)?github\.com/"
        r"([^/\s]+)/([^/\s#?]+)",
        url,
    )

    if not match:
        raise ValueError(
            "Please enter a valid GitHub repository URL, "
            "for example: https://github.com/owner/repository"
        )

    owner = match.group(1)
    repo = match.group(2)

    if repo.endswith(".git"):
        repo = repo[:-4]

    return f"https://github.com/{owner}/{repo}.git"


def clone_repository(repo_url):
    """
    Clone a public GitHub repository into a temporary directory.
    """

    clone_url = normalize_repo_url(repo_url)

    temp_dir = tempfile.mkdtemp()

    # Prevent Git from waiting for username/password input.
    env = {
        **os.environ,
        "GIT_TERMINAL_PROMPT": "0",
    }

    try:
        Repo.clone_from(
            clone_url,
            temp_dir,
            depth=1,
            env=env,
        )

        return temp_dir

    except Exception as e:

        shutil.rmtree(
            temp_dir,
            onerror=_force_remove,
        )

        message = str(e)

        if (
            "not found" in message.lower()
            or "could not read username" in message.lower()
            or "authentication failed" in message.lower()
            or "repository not found" in message.lower()
        ):
            raise Exception(
                "Could not clone the repository. "
                "It may not exist, or it may be private. "
                "Only public repositories are supported."
            )

        raise Exception(
            f"Could not clone repository: {message}"
        )


def read_notebook(file_path):
    """
    Return only the code and markdown cells of a Jupyter notebook.
    """

    with open(
        file_path,
        "r",
        encoding="utf-8",
        errors="ignore",
    ) as f:

        notebook = json.load(f)

    parts = []

    for cell in notebook.get("cells", []):

        source = "".join(
            cell.get("source", [])
        )

        if not source.strip():
            continue

        if cell.get("cell_type") == "markdown":

            parts.append(
                "# " + source.replace(
                    "\n",
                    "\n# ",
                )
            )

        elif cell.get("cell_type") == "code":

            parts.append(source)

    return "\n\n".join(parts)


def _is_binary(path):
    """
    Detect whether a file appears to be binary.
    """

    try:

        with open(path, "rb") as f:
            return b"\0" in f.read(1024)

    except OSError:

        return True


def _read_text(path, limit):
    """
    Read a limited amount of text from a file.
    """

    with open(
        path,
        "r",
        encoding="utf-8",
        errors="ignore",
    ) as f:

        return f.read(limit)


def _read_data_preview(path):
    """
    Read the header and first few rows of a CSV/TSV file.
    """

    lines = []

    with open(
        path,
        "r",
        encoding="utf-8",
        errors="ignore",
    ) as f:

        for _, line in zip(
            range(CSV_PREVIEW_LINES),
            f,
        ):

            lines.append(
                line.rstrip()[:300]
            )

    return (
        "(data file preview: header and first rows)\n"
        + "\n".join(lines)
    )


def _priority(rel_path):
    """
    Lower tuple = more important.
    None = file is not worth reading.
    """

    name = os.path.basename(
        rel_path
    ).lower()

    stem, ext = os.path.splitext(name)

    depth = rel_path.count(
        os.sep
    )

    if name.startswith("readme"):

        group = 0

    elif name in CONFIG_NAMES:

        group = 1

    elif (
        ext in CODE_EXTENSIONS
        and stem in ENTRY_NAMES
    ):

        group = 2

    elif (
        ext in CODE_EXTENSIONS
        or ext == ".ipynb"
    ):

        group = 3

    elif ext in DATA_EXTENSIONS:

        group = 4

    elif ext in TEXT_EXTENSIONS:

        group = 5

    else:

        return None

    return (
        group,
        depth,
        rel_path,
    )


def _visible_dirs(dirs):
    """
    Remove directories that are not useful for analysis.
    """

    return sorted(
        d
        for d in dirs
        if d not in IGNORE_DIRS
        and not d.startswith(".")
    )


def get_file_tree(repo_path, max_entries=60):
    """
    Return a plain list of repository file paths.
    """

    paths = []

    for root, dirs, filenames in os.walk(
        repo_path
    ):

        dirs[:] = _visible_dirs(dirs)

        for filename in sorted(filenames):

            rel = os.path.relpath(
                os.path.join(
                    root,
                    filename,
                ),
                repo_path,
            )

            paths.append(
                rel.replace(
                    os.sep,
                    "/",
                )
            )

    text = "\n".join(
        paths[:max_entries]
    )

    if len(paths) > max_entries:

        text += (
            f"\n... and "
            f"{len(paths) - max_entries} more files"
        )

    return text


def extract_code(repo_path):
    """
    Pick the most informative files first,
    within a small size budget.
    """

    candidates = []

    for root, dirs, filenames in os.walk(
        repo_path
    ):

        dirs[:] = _visible_dirs(dirs)

        for filename in sorted(filenames):

            if filename.lower() in IGNORE_FILES:
                continue

            abs_path = os.path.join(
                root,
                filename,
            )

            rel_path = os.path.relpath(
                abs_path,
                repo_path,
            )

            priority = _priority(
                rel_path
            )

            if priority:

                candidates.append(
                    (
                        priority,
                        abs_path,
                        rel_path,
                    )
                )

    candidates.sort(
        key=lambda c: c[0]
    )

    files = []
    total = 0

    for _, abs_path, rel_path in candidates:

        if len(files) >= MAX_FILES:
            break

        if total >= MAX_TOTAL_CHARS:
            break

        ext = os.path.splitext(
            abs_path
        )[1].lower()

        try:

            if _is_binary(abs_path):
                continue

            if ext == ".ipynb":

                if (
                    os.path.getsize(abs_path)
                    > MAX_NOTEBOOK_BYTES
                ):
                    continue

                content = read_notebook(
                    abs_path
                )

            elif ext in DATA_EXTENSIONS:

                content = _read_data_preview(
                    abs_path
                )

            else:

                content = _read_text(
                    abs_path,
                    MAX_CHARS_PER_FILE,
                )

        except Exception:
            continue

        content = content.strip()

        if not content:
            continue

        remaining = (
            MAX_TOTAL_CHARS - total
        )

        content = content[
            :MAX_CHARS_PER_FILE
        ][:remaining]

        if not content:
            continue

        files.append(
            {
                "filename": rel_path.replace(
                    os.sep,
                    "/",
                ),
                "code": content,
            }
        )

        total += len(content)

    return files

