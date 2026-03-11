from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.api.routers import market, report
from src.scheduler import start_scheduler
from src.workers.market_streamer import start_streams
from src.cache import db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start APScheduler & Streams
    scheduler = start_scheduler()
    mqtt_client = start_streams()
    yield
    # Shutdown: Stop Scheduler, Flusher, & MQTT
    scheduler.shutdown()
    if mqtt_client:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
    db.stop_flusher()

app = FastAPI(
    title="Mirae Asset Automation API",
    description="Backend API phục vụ Analyst Dashboard",
    version="2.0.0",
    lifespan=lifespan
)

import os

# CORS middleware for Next.js frontend calls
origins = ["http://localhost:3000"]
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(market.router)
app.include_router(report.router)

@app.get("/health", tags=["System"])
def health_check():
    """Endpoint for load balancers and deployment verification."""
    return {"status": "ok"}

# End of file
