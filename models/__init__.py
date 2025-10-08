# backend/models/__init__.py
from app import db
from .models import User
from .models import Company
from .models import Botiquin
from .models import Medicine

__all__ = ["db", "User", "Company", "Botiquin", "Medicine"]