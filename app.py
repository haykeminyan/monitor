import asyncio
from zoneinfo import ZoneInfo

from contextlib import asynccontextmanager
from datetime import datetime, timezone
import uvicorn
from fastapi import Request

from aiohttp import ClientSession
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
import logging
from constants import projects


logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(monitor_loop())

    yield

    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
app = FastAPI(lifespan=lifespan)

templates = Jinja2Templates(directory="html")

monitor_data = []


async def check_project(session: ClientSession, project: str):
    try:
        async with session.get(project, timeout=5) as response:
            return {
                "project": project,
                "status_code": response.status,
                "current_time": datetime.now(
    ZoneInfo("Europe/Lisbon")
).isoformat()
            }
    except Exception as exc:
        return {
            "project": project,
            "status_code": None,
            "error": str(exc),
            "current_time": datetime.now(
                ZoneInfo("Europe/Lisbon")
            ).isoformat()
        }


async def monitor_loop():
    global monitor_data

    async with ClientSession() as session:
        while True:
            monitor_data = await asyncio.gather(
                *(check_project(session, project) for project in projects)
            )

            await asyncio.sleep(60)

@app.get("/api")
async def monitor():
    return monitor_data


@app.get('/')
async def main(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )

