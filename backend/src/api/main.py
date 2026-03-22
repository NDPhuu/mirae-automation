import os
from fastapi import FastAPI, Depends, Security, HTTPException, status
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.api.routers import market, report
from src.scheduler import start_scheduler
from src.workers.market_streamer import start_streams
from src.cache import db

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from src.api.dependencies import limiter

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

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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

api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)
def get_api_key(api_key: str = Security(api_key_header)):
    expected_key = os.getenv("API_SECRET_KEY", "mirae-dev-key")
    if not api_key or api_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key"
        )
    return api_key

app.include_router(market.router, dependencies=[Depends(get_api_key)])
app.include_router(report.router, dependencies=[Depends(get_api_key)])

@app.get("/health", tags=["System"])
def health_check():
    """Endpoint for load balancers and deployment verification."""
    return {"status": "ok"}

# End of file
