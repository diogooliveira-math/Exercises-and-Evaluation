from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from .api_router import router as api_router
import os

app = FastAPI(title="Exercises-and-Evaluation API")

# Simple API-key middleware: when `API_KEY` env var is set, enforce that all
# modifying requests (POST/PUT/DELETE) include header `X-API-Key: <API_KEY>`.
@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    api_key = os.environ.get("API_KEY")
    if api_key:
        # protect mutating methods
        if request.method in ("POST", "PUT", "DELETE") and request.url.path.startswith("/api/v1"):
            header = request.headers.get("x-api-key")
            if header != api_key:
                return JSONResponse(status_code=403, content={"detail": "Missing or invalid API key"})
    return await call_next(request)


app.include_router(api_router, prefix="/api/v1")


@app.get("/healthz")
def healthz():
    return {"status": "ok"}
