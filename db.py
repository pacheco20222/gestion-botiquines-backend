"""
Database bootstrap for the MVP.
- Exposes a single SQLAlchemy instance: `db`
- Provides `init_db(app)` to configure the Flask app with the DB URL
- Loads .env (if present) so DATABASE_URL works locally and in Docker
"""

import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

# Load variables from a local .env when running outside Docker
load_dotenv()

# Single shared SQLAlchemy instance for the whole app
db = SQLAlchemy()


def get_database_uri() -> str:
    """
    Returns the SQLAlchemy connection string.
    Priority:
      1) DATABASE_URL env var (recommended)
      2) Fallback to a sensible default for Docker Compose
    Notes:
      - We use the PyMySQL driver (pure Python, easy to install)
      - In Docker Compose, the MySQL service is named 'db'
    """
    return os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://botuser:botpass@db:3306/botiquines",
    )


def init_db(app) -> None:
    """
    Bind SQLAlchemy to the Flask app.
    Keeps config minimal (MVP), but adds a couple of stable MySQL options.
    """
    app.config["SQLALCHEMY_DATABASE_URI"] = get_database_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Optional but good practice for MySQL connections:
    app.config.setdefault("SQLALCHEMY_ENGINE_OPTIONS", {
        "pool_pre_ping": True,   # Avoids 'MySQL server has gone away' on idle
        "pool_recycle": 280,     # Recycle connections regularly (in seconds)
    })

    db.init_app(app)