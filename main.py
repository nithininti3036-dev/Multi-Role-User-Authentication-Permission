from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.db.session import SessionLocal
from app.db.init_db import init_db
from app.api.v1.router import api_router

logger = logging.getLogger("rbac.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables and seed data exist
    logger.info("Initializing database tables and seed records...")
    db = SessionLocal()
    try:
        init_db(db)
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
    finally:
        db.close()
    yield
    # Shutdown logic (if any)
    logger.info("Application shutting down.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
## Multi-Role User Authentication & Permission System (RBAC)
A backend service built with **Python**, **FastAPI**, and **MySQL**.

### Key Features:
* 🔐 **Secure Authentication**: JWT (JSON Web Tokens) with Bcrypt password hashing.
* 👥 **Multi-Role RBAC**: Users can possess multiple roles; roles possess granular permissions.
* 🛡️ **Dynamic Permissions**: Instant authorization checks without requiring hardcoded roles.
* 👑 **SuperAdmin Override**: Built-in wildcard (`*:*`) capability for root system administrators.
* 📝 **Audit Trail**: Full security event logging for logins, role updates, and user modifications.
* 🚀 **Interactive Swagger UI**: Easily test endpoints with the **Authorize** button.
    """,
    openapi_tags=[
        {"name": "Authentication", "description": "User registration, JWT login, token refresh & profile"},
        {"name": "User Management", "description": "Manage user accounts, status, and role assignments"},
        {"name": "Role Management (RBAC)", "description": "Create, update, delete roles and grant permissions"},
        {"name": "Permission Catalog", "description": "Query available granular permissions"},
        {"name": "Protected Demo Resources", "description": "Test permission barrier enforcement with live resources"},
        {"name": "Audit Logs", "description": "Review security audit trails"},
    ],
    lifespan=lifespan
)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"])
def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "documentation": "/docs",
        "redoc": "/redoc",
        "api_v1_prefix": settings.API_V1_STR,
        "default_admin": {
            "email": settings.FIRST_SUPERADMIN_EMAIL,
            "password": settings.FIRST_SUPERADMIN_PASSWORD,
            "role": "SuperAdmin / Admin"
        }
    }


@app.get("/health", tags=["Root"])
def health_check():
    return {"status": "healthy"}
