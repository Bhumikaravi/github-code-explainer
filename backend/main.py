from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from backend.services.repo_processor import (
    clone_repository,
    extract_code,
    get_file_tree,
    cleanup_repository,
)
from backend.services.llm_service import check_model, stream_explanation


app = FastAPI(
    title="GitHub Repository Code Explainer"
)


class RepositoryRequest(BaseModel):
    repo_url: str


@app.get("/")
def home():
    return {
        "message": "GitHub Repository Code Explainer API is running"
    }


@app.post("/explain")
def explain_repository(request: RepositoryRequest):

    repo_path = None

    try:
        # Fail fast if Ollama is down or the model is missing
        check_model()

        repo_path = clone_repository(request.repo_url)

        file_tree = get_file_tree(repo_path)
        code_files = extract_code(repo_path)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Everything we need is already in memory
        if repo_path:
            cleanup_repository(repo_path)

    if not file_tree.strip():
        raise HTTPException(
            status_code=400,
            detail="The repository appears to be empty."
        )

    return StreamingResponse(
        stream_explanation(file_tree, code_files),
        media_type="text/plain; charset=utf-8",
        headers={"X-Files-Analyzed": str(len(code_files))},
    )
