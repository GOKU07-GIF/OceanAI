import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logger import logger

from app.middleware.performance import PerformanceLoggingMiddleware

# Routers
from app.routes.auth import router as auth_router
from app.routes.dashboard import router as dashboard_router
from app.routes.ocean import router as ocean_router
from app.routes.weather import router as weather_router
from app.routes.prediction import router as prediction_router
from app.routes.analytics import router as analytics_router
from app.routes.anomaly import router as anomaly_router
from app.routes.report import router as report_router
from app.routes.system import router as system_router
from app.routes.map import router as map_router
from app.routes.ai import router as ai_router
from app.routes.device import router as device_router
from app.routes.sensor_reading import router as sensor_reading_router
from app.routes.sos import router as sos_router
from app.routes import alert


# Exception handlers
from app.exceptions.handlers import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
)


# -----------------------------------------------------------------------------
# APP INITIALIZATION
# -----------------------------------------------------------------------------

app = FastAPI(
    title="OceanAI API",
    description="AI-powered Ocean Intelligence Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# -----------------------------------------------------------------------------
# MIDDLEWARE
# -----------------------------------------------------------------------------

app.add_middleware(PerformanceLoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[
        "X-Process-Time",
        "X-API-Version",
    ],
)


# -----------------------------------------------------------------------------
# EXCEPTION HANDLERS
# -----------------------------------------------------------------------------

app.add_exception_handler(
    StarletteHTTPException,
    http_exception_handler,
)

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)

app.add_exception_handler(
    Exception,
    general_exception_handler,
)


# -----------------------------------------------------------------------------
# ROUTERS
# -----------------------------------------------------------------------------

app.include_router(auth_router)
app.include_router(ocean_router)
app.include_router(dashboard_router)
app.include_router(weather_router)
app.include_router(prediction_router)
app.include_router(analytics_router)
app.include_router(anomaly_router)
app.include_router(report_router)
app.include_router(system_router)
app.include_router(map_router)
app.include_router(ai_router)
app.include_router(device_router)
app.include_router(sensor_reading_router)
app.include_router(sos_router)
app.include_router(alert.router)

# -----------------------------------------------------------------------------
# ROOT ENDPOINT
# -----------------------------------------------------------------------------

@app.get("/", tags=["Root"])
def root():
    logger.info("OceanAI API Started Successfully")

    return {
        "message": "Welcome to OceanAI API",
        "version": "1.0.0",
        "status": "Running",
    }