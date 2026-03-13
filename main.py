from __future__ import annotations

import os
import threading
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI

from chiller.chiller import Chiller
from chiller.http.http_controller import router
from chiller.modbus.modbus_controller import ModbusChillerServer

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

_HTTP_PORT = int(os.getenv("HTTP_PORT", "8000"))
_MODBUS_PORT = int(os.getenv("MODBUS_PORT", "5020"))

_chiller = Chiller()
_modbus_server = ModbusChillerServer(_chiller)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    threading.Thread(target=_chiller.run, args=(1.0,), daemon=True).start()
    threading.Thread(
        target=_modbus_server.start, kwargs={"port": _MODBUS_PORT}, daemon=True
    ).start()
    yield


app = FastAPI(lifespan=lifespan)
app.state.chiller = _chiller
app.include_router(router)
