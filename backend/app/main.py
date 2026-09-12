import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import init_db
from app.core.middleware import setup_cors, RequestLoggingMiddleware
from app.routers.tasks import router as tasks_router
from app.routers.employees import router as employees_router
from app.routers.recommendations import router as recommendations_router
from app.routers.optimize import router as optimize_router
from app.routers.settings import router as settings_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    logger.info("TITANS API started successfully")
    yield
    logger.info("TITANS API shutting down")


app = FastAPI(
    title="TITANS API",
    description="AI-Powered Workforce Recommendation & Optimization",
    version="1.0.0",
    lifespan=lifespan,
)

setup_cors(app)
app.add_middleware(RequestLoggingMiddleware)

app.include_router(tasks_router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(employees_router, prefix="/api/employees", tags=["Employees"])
app.include_router(recommendations_router, prefix="/api/recommendations", tags=["Recommendations"])
app.include_router(optimize_router, prefix="/api/optimize", tags=["Optimization"])
app.include_router(settings_router, prefix="/api/settings", tags=["Settings"])


@app.get("/")
async def root():
    return {"name": "TITANS API", "version": "1.0.0", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
