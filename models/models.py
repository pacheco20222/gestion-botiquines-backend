"""
Database models for Smart First Aid Kit Management System.

Updated structure includes:
- Company management (for SaaS model)
- Multiple first aid kits (botiquines) per company
- Medicine inventory with weight-based calculations
- Compartment assignments for visual representation
"""

from datetime import datetime, date
from db import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Company(db.Model):
    """
    Company/Organization that owns one or more first aid kits.
    For SaaS model where multiple companies use the system.
    """
    __tablename__= "companies"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    contact_email = db.Column(db.String(120), unique=True)
    contact_phone = db.Column(db.String(30))
    active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    botiquines = db.relationship('Botiquin', backref='company', lazy=True, cascade='all, delete-orphan')
    users = db.relationship('User', backref='company', lazy=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "contact_email": self.contact_email,
            "contact_phone": self.contact_phone,
            "active": self.active,
            "botiquines_count": len(self.botiquines),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class User(db.Model, UserMixin):
    """
    System users - administrators for companies.
    Two levels: super_admin (manages all) and company_admin (manages their company).
    """
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # User type: 'super_admin' or 'company_admin'
    user_type = db.Column(db.String(20), default="company_admin", nullable=False)
    
    # Foreign key to company (null for super_admin)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=True)

    active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def is_active(self) -> bool:  # Flask-Login compatibility
        return bool(self.active)

    def set_password(self, password: str):
        """Hash and store a plain password"""
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password: str) -> bool:
        """Verify a password against the stored hash."""
        return check_password_hash(self.password_hash, password)
    
    def is_super_admin(self) -> bool:
        """Check if user is a super administrator"""
        return self.user_type == 'super_admin'

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "user_type": self.user_type,
            "company_id": self.company_id,
            "company_name": self.company.name if self.company else None,
            "active": self.active,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "created_at": self.created_at.isoformat()
        }
        
class Botiquin(db.Model):
    """
    First Aid Kit (Botiquín) - physical unit.
    Data is sent as a whole, not by compartments individually.
    Each company can have multiple botiquines.
    """
    __tablename__ = "botiquines"
    
    id = db.Column(db.Integer, primary_key=True)
    # Unique identifier for hardware communication
    hardware_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False) # e.g., "Botiquín 1", "Planta Baja",
    location = db.Column(db.String(120)) # Physical location description
    
    # Foreign key to company
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=True)

    # Compartment configuration
    total_compartments = db.Column(db.Integer, default=4, nullable=False)  # Default 4 compartments for MVP
    
    active = db.Column(db.Boolean, default=True)
    last_sync_at = db.Column(db.DateTime)  # Last hardware sync
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    medicines = db.relationship('Medicine', backref='botiquin', lazy=True, cascade='all, delete-orphan')
    
    def get_compartment_status(self):
        """Deprecated: compartment-level status is not used currently."""
        return {}
    
    def to_dict(self):
        return {
            "id": self.id,
            "hardware_id": self.hardware_id,
            "name": self.name,
            "location": self.location,
            "company_id": self.company_id,
            "company_name": self.company.name if self.company else None,
            "total_compartments": self.total_compartments,
            "active": self.active,
            "last_sync_at": self.last_sync_at.isoformat() if self.last_sync_at else None,
            "medicines_count": len(self.medicines),
            "compartments_status": self.get_compartment_status(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class Medicine(db.Model):
    """
    Medicine inventory in a specific botiquin compartment.
    Enhanced with weight-based quantity calculation and compartment assignment.
    """
    __tablename__ = "medicines"

    id = db.Column(db.Integer, primary_key=True)
    
    # ForeignKey to botiquin
    botiquin_id = db.Column(db.Integer, db.ForeignKey("botiquines.id"), nullable=False)
    
    # Compartment assignment (1 to total_compartments)
    compartment_number = db.Column(db.Integer, nullable=True)
    # Medicine information
    trade_name = db.Column(db.String(120), nullable=False)   # Commercial name
    generic_name = db.Column(db.String(120), nullable=False)  # Generic name
    brand = db.Column(db.String(120))                         # Brand or lab
    strength = db.Column(db.String(80))                       # Presentation/strength
    
    # Weight management for automatic quantity calculation (peso promedio por unidad)
    unit_weight = db.Column(db.Float, nullable=True)
    current_weight = db.Column(db.Float, nullable=True)  # Total weight from sensor
    
    # Quantity and stock management
    quantity = db.Column(db.Integer, default=0, nullable=False)  # Calculated from weight if unit_weight exists
    reorder_level = db.Column(db.Integer, default=5, nullable=False)
    max_capacity = db.Column(db.Integer, nullable=True)  # Max units that fit in compartment
    
    # Dates and tracking
    expiry_date = db.Column(db.Date)
    batch_number = db.Column(db.String(50))  # Lote number
    last_scan_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def calculate_quantity_from_weight(self):
        """
        Calculate quantity based on weight sensor reading.
        Updates quantity field automatically.
        """
        if self.unit_weight and self.current_weight and self.unit_weight > 0:
            calculated_qty = int(self.current_weight / self.unit_weight)
            self.quantity = calculated_qty
            return calculated_qty
        return self.quantity
    
    def update_from_sensor(self, weight_reading: float):
        """
        Update medicine data from sensor reading.
        Called when hardware sends weight data.
        """
        self.current_weight = weight_reading
        self.calculate_quantity_from_weight()
        self.last_scan_at = datetime.utcnow()
        return self.quantity

    @property
    def average_weight(self):
        return self.unit_weight

    @average_weight.setter
    def average_weight(self, value):
        self.unit_weight = value

    # --- Helper methods ---

    def days_to_expiry(self):
        """
        Returns the number of days until the medicine expires.
        - Negative value if already expired.
        - None if expiry_date is not set.
        """
        if not self.expiry_date:
            return None
        return (self.expiry_date - date.today()).days

    def status(self) -> str:
        """
        Returns a detailed status string for the medicine.
        - "OUT_OF_STOCK" if quantity = 0
        - "EXPIRED" if already expired
        - "EXPIRES_SOON" if expiry_date ≤ 7 days
        - "EXPIRES_30" if expiry_date ≤ 30 days
        - "LOW_STOCK" if quantity ≤ reorder_level
        - Otherwise "OK"
        """
        if self.quantity <= 0:
            return "OUT_OF_STOCK"

        days = self.days_to_expiry()
        if days is not None:
            if days < 0:
                return "EXPIRED"
            if days <= 7:
                return "EXPIRES_SOON"
            if days <= 30:
                return "EXPIRES_30"

        if self.quantity <= self.reorder_level:
            return "LOW_STOCK"

        return "OK"
    
    def get_status_color(self) -> str:
        """Returns Bootstrap color class based on status"""
        status = self.status()
        color_map = {
            "OUT_OF_STOCK": "dark",
            "EXPIRED": "danger",
            "EXPIRES_SOON": "warning",
            "EXPIRES_30": "secondary",
            "LOW_STOCK": "warning",
            "OK": "success"
        }
        return color_map.get(status, "secondary")

    def to_dict(self) -> dict:
        """
        Serialize the model to a dictionary (for JSON responses).
        """
        return {
            "id": self.id,
            "botiquin_id": self.botiquin_id,
            "botiquin_name": self.botiquin.name if self.botiquin else None,
            "compartment_number": self.compartment_number,
            "trade_name": self.trade_name,
            "generic_name": self.generic_name,
            "brand": self.brand,
            "strength": self.strength,
        "average_weight": self.unit_weight,
            "current_weight": self.current_weight,
            "quantity": self.quantity,
            "reorder_level": self.reorder_level,
            "max_capacity": self.max_capacity,
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
            "batch_number": self.batch_number,
            "last_scan_at": self.last_scan_at.isoformat() if self.last_scan_at else None,
            "status": self.status(),
            "status_color": self.get_status_color(),
            "days_to_expiry": self.days_to_expiry(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
class HardwareLog(db.Model):
    """
    Log of all hardware sensor readings for audit and debugging.
    Stores raw data received from hardware.
    """
    __tablename__ = "hardware_logs"
    
    id = db.Column(db.Integer, primary_key=True)
    botiquin_id = db.Column(db.Integer, db.ForeignKey('botiquines.id'), nullable=False)
    
    # Raw data from hardware
    compartment_number = db.Column(db.Integer)
    weight_reading = db.Column(db.Float)
    sensor_type = db.Column(db.String(30))  # 'weight', 'door', 'infrared'
    raw_data = db.Column(db.Text)  # JSON string of complete payload
    
    processed = db.Column(db.Boolean, default=False)
    error_message = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        return {
            "id": self.id,
            "botiquin_id": self.botiquin_id,
            "compartment_number": self.compartment_number,
            "weight_reading": self.weight_reading,
            "sensor_type": self.sensor_type,
            "raw_data": self.raw_data,
            "processed": self.processed,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat()
        }
