from __future__ import annotations

from fastapi import FastAPI

from chiller.api import router as chiller_router

app = FastAPI()
app.include_router(chiller_router)
