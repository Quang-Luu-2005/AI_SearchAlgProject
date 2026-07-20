from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.router import router


app = FastAPI(
    title="FloodRoute HCMC API",
    version="0.1.0",
    description="Explainable route-search API for the FloodRoute HCMC lab project.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router, prefix="/api/v1")


@app.get("/", tags=["system"])
def project_info() -> dict[str, str]:
    return {
        "name": "FloodRoute HCMC",
        "version": app.version,
        "docs": "/docs",
    }

