"""
SIGNEX - Antideploy Production Server Entry Point
FastAPI backend serving both REST API (/api/*) and React SPA frontend.
Antideploy auto-detects uvicorn and runs: uvicorn server:app
"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

# Import all API routes from the existing server
from ntro_sigint.server.app import app

STATIC_DIR = PROJECT_ROOT / "frontend" / "dist"

# Mount static assets (JS/CSS/images)
if (STATIC_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(STATIC_DIR / "assets")), name="static_assets")

# Serve React SPA for all non-API routes
@app.get("/", include_in_schema=False)
async def root():
    index = STATIC_DIR / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return JSONResponse({"status": "SIGNEX API running", "docs": "/docs"})

@app.get("/{full_path:path}", include_in_schema=False)
async def catch_all(full_path: str):
    # Let /api/* and /docs/* fall through to FastAPI handlers
    if full_path.startswith(("api/", "docs", "openapi", "redoc")):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Not found")
    index = STATIC_DIR / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return JSONResponse({"error": "Frontend build not found"}, status_code=404)
