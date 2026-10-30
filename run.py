import argparse
import sys
import uvicorn

# Ensure UTF-8 output encoding on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from app.core.config import settings
from app.db.session import SessionLocal
from app.db.init_db import init_db


def main():
    parser = argparse.ArgumentParser(description="Multi-Role RBAC Backend Service")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on (default: 8000)")
    parser.add_argument("--reload", action="store_true", default=True, help="Enable auto-reload on code change")
    parser.add_argument("--init-db-only", action="store_true", help="Only initialize and seed database, then exit")
    args = parser.parse_args()

    print("=" * 70)
    print(" 🚀 Starting Multi-Role User Authentication & RBAC Backend")
    print("=" * 70)
    print(f" * Project:       {settings.PROJECT_NAME} (v{settings.VERSION})")
    if "sqlite" in settings.sync_database_url:
        print(f" * Active DB:     SQLite (Local file: rbac.db - zero installation required)")
    else:
        print(f" * Active DB:     MySQL ({settings.MYSQL_USER}@{settings.MYSQL_SERVER}:{settings.MYSQL_PORT}/{settings.MYSQL_DB})")
    print(f" * Admin User:    {settings.FIRST_SUPERADMIN_EMAIL} (Password: {settings.FIRST_SUPERADMIN_PASSWORD})")
    print("=" * 70)

    # Pre-flight DB initialization
    try:
        db = SessionLocal()
        init_db(db)
        db.close()
    except Exception as e:
        print(f" ⚠️  Database initialization warning: {e}")

    if args.init_db_only:
        print(" Database initialized successfully. Exiting.")
        sys.exit(0)

    print(f" 🌐 Interactive API Docs: http://{args.host}:{args.port}/docs")
    print(f" 🌐 ReDoc API Docs:       http://{args.host}:{args.port}/redoc")
    print("=" * 70)

    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )


if __name__ == "__main__":
    main()
