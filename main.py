from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI

from chiller.api import router as chiller_router
from chiller.api import start_simulation

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    start_simulation()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(chiller_router)
