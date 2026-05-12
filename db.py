"""
Database bootstrap for the MVP.
- Exposes a single SQLAlchemy instance: `db`
- Provides `init_db(app)` to configure the Flask app with the DB URL
- Loads .env (if present) so DATABASE_URL works locally and in Docker
"""

import os
from dotenv import load_dotenv
from extensions import db

# Load variables from a local .env when running outside Docker
load_dotenv()


def get_database_uri() -> str:
    """
    Returns the SQLAlchemy connection string.
    Priority:
      1) DATABASE_URL env var (recommended)
      2) Fallback to a sensible default for Docker Compose
    """
    return os.getenv(
        "DATABASE_URL",
        "postgresql://botuser:botpass@db:5432/botiquines",
    )


def init_db(app) -> None:
    """
    Bind SQLAlchemy to the Flask app.
    Keeps config minimal (MVP).
    """
    app.config["SQLALCHEMY_DATABASE_URI"] = get_database_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config.setdefault("SQLALCHEMY_ENGINE_OPTIONS", {
        "pool_pre_ping": True,   # Avoids connection drops for idle connections
    })

    db.init_app(app)