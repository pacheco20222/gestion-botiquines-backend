"""
Routes for Botiquin (First Aid Kit) management.
Handles CRUD operations and compartment visualization.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from db import db
from models.models import Botiquin, Company, Medicine

bp = Blueprint("botiquines", __name__)

# -------- Validation --------
def validate_botiquin_payload(data, partial=False):
    errors = []
    
    required = ["hardware_id", "name", "company_id"]
    
    if not partial:
        for f in required:
            if f not in data or data.get(f) in (None, ""):
                errors.append(f"'{f}' is required")
    
    # Validate company exists
    if "company_id" in data and data.get("company_id"):
        company = Company.query.get(data["company_id"])
        if not company:
            errors.append(f"Company with id {data['company_id']} does not exist")
    
    # Validate compartment configuration
    for field in ["total_compartments", "compartment_rows", "compartment_cols"]:
        if field in data and data[field] is not None:
            try:
                v = int(data[field])
                if field == "total_compartments":
                    if v < 4:
                        errors.append("'total_compartments' must be at least 4")
                elif v <= 0:
                    errors.append(f"'{field}' must be > 0")
            except (TypeError, ValueError):
                errors.append(f"'{field}' must be an integer")
    
    # Validate rows * cols = total_compartments if all are provided
    if all(f in data for f in ["total_compartments", "compartment_rows", "compartment_cols"]):
        try:
            total = int(data["total_compartments"])
            rows = int(data["compartment_rows"])
            cols = int(data["compartment_cols"])
            if rows * cols != total:
                errors.append(f"rows ({rows}) * cols ({cols}) must equal total_compartments ({total})")
        except (TypeError, ValueError):
            pass
    
    return (len(errors) == 0, errors)

# -------- Routes --------

@bp.get("/")
def list_botiquines():
    """List all botiquines, optionally filtered by company"""
    company_id = request.args.get("company_id")
    
    query = Botiquin.query
    if company_id:
        query = query.filter_by(company_id=company_id)
    
    botiquines = query.order_by(Botiquin.id.asc()).all()
    return jsonify([b.to_dict() for b in botiquines]), 200


@bp.post("/")
def create_botiquin():
    """Create a new botiquin"""
    data = request.get_json() or {}
    ok, errors = validate_botiquin_payload(data, partial=False)
    if not ok:
        return jsonify({"errors": errors}), 400
    
    # Check if hardware_id already exists
    existing = Botiquin.query.filter_by(hardware_id=data.get("hardware_id")).first()
    if existing:
        return jsonify({"error": f"Botiquin with hardware_id '{data.get('hardware_id')}' already exists"}), 400
    
    botiquin = Botiquin(
        hardware_id=data.get("hardware_id"),
        name=data.get("name"),
        location=data.get("location"),
        company_id=int(data.get("company_id")),
        total_compartments=int(data.get("total_compartments", 4)),
        compartment_rows=int(data.get("compartment_rows", 2)),
        compartment_cols=int(data.get("compartment_cols", 2)),
        active=data.get("active", True)
    )
    
    db.session.add(botiquin)
    db.session.commit()
    
    return jsonify(botiquin.to_dict()), 201


@bp.get("/<int:botiquin_id>")
def get_botiquin(botiquin_id):
    """Get a specific botiquin with its compartment status"""
    botiquin = Botiquin.query.get(botiquin_id)
    if not botiquin:
        return jsonify({"error": "Botiquin not found"}), 404
    
    return jsonify(botiquin.to_dict()), 200


@bp.get("/<int:botiquin_id>/compartments")
def get_compartments(botiquin_id):
    """
    Get detailed compartment visualization data.
    Returns a grid representation of the botiquin.
    """
    botiquin = Botiquin.query.get(botiquin_id)
    if not botiquin:
        return jsonify({"error": "Botiquin not found"}), 404
    
    # Create grid representation
    grid = []
    compartment_map = {}
    
    # Build map of compartment number to medicine
    for medicine in botiquin.medicines:
        if medicine.compartment_number:
            compartment_map[medicine.compartment_number] = {
                "id": medicine.id,
                "trade_name": medicine.trade_name,
                "generic_name": medicine.generic_name,
                "quantity": medicine.quantity,
                "status": medicine.status(),
                "status_color": medicine.get_status_color(),
                "days_to_expiry": medicine.days_to_expiry()
            }
    
    # Build grid
    compartment_num = 1
    for row in range(botiquin.compartment_rows):
        grid_row = []
        for col in range(botiquin.compartment_cols):
            if compartment_num <= botiquin.total_compartments:
                if compartment_num in compartment_map:
                    grid_row.append({
                        "compartment": compartment_num,
                        "occupied": True,
                        "medicine": compartment_map[compartment_num]
                    })
                else:
                    grid_row.append({
                        "compartment": compartment_num,
                        "occupied": False,
                        "medicine": None
                    })
            else:
                grid_row.append({
                    "compartment": None,
                    "occupied": False,
                    "medicine": None
                })
            compartment_num += 1
        grid.append(grid_row)
    
    return jsonify({
        "botiquin_id": botiquin.id,
        "botiquin_name": botiquin.name,
        "rows": botiquin.compartment_rows,
        "cols": botiquin.compartment_cols,
        "total_compartments": botiquin.total_compartments,
        "grid": grid,
        "summary": {
            "occupied": len(compartment_map),
            "empty": botiquin.total_compartments - len(compartment_map),
            "critical": sum(1 for m in compartment_map.values() if m["status"] in ["EXPIRED", "OUT_OF_STOCK"]),
            "warning": sum(1 for m in compartment_map.values() if m["status"] in ["EXPIRES_SOON", "LOW_STOCK"])
        }
    }), 200


@bp.put("/<int:botiquin_id>")
def update_botiquin(botiquin_id):
    """Update botiquin information"""
    botiquin = Botiquin.query.get(botiquin_id)
    if not botiquin:
        return jsonify({"error": "Botiquin not found"}), 404
    
    data = request.get_json() or {}
    ok, errors = validate_botiquin_payload(data, partial=True)
    if not ok:
        return jsonify({"errors": errors}), 400
    
    # Check if hardware_id is being changed and if it's unique
    if "hardware_id" in data and data["hardware_id"] != botiquin.hardware_id:
        existing = Botiquin.query.filter_by(hardware_id=data["hardware_id"]).first()
        if existing:
            return jsonify({"error": f"Hardware ID '{data['hardware_id']}' already in use"}), 400
    
    # Update fields
    fields = ["hardware_id", "name", "location", "company_id", 
              "total_compartments", "compartment_rows", "compartment_cols", "active"]
    
    for field in fields:
        if field in data:
            if field in ["company_id", "total_compartments", "compartment_rows", "compartment_cols"]:
                setattr(botiquin, field, int(data[field]))
            else:
                setattr(botiquin, field, data[field])
    
    db.session.commit()
    return jsonify(botiquin.to_dict()), 200


@bp.delete("/<int:botiquin_id>")
def delete_botiquin(botiquin_id):
    """
    Delete a botiquin.
    Note: This will cascade delete all medicines in the botiquin.
    """
    botiquin = Botiquin.query.get(botiquin_id)
    if not botiquin:
        return jsonify({"error": "Botiquin not found"}), 404
    
    # Check if it has medicines
    medicine_count = len(botiquin.medicines)
    
    db.session.delete(botiquin)
    db.session.commit()
    
    return jsonify({
        "message": f"Botiquin deleted successfully",
        "medicines_deleted": medicine_count
    }), 200


@bp.post("/<int:botiquin_id>/sync")
def sync_botiquin(botiquin_id):
    """
    Mark botiquin as synced with hardware.
    Updates last_sync_at timestamp.
    """
    botiquin = Botiquin.query.get(botiquin_id)
    if not botiquin:
        return jsonify({"error": "Botiquin not found"}), 404
    
    botiquin.last_sync_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        "message": "Sync timestamp updated",
        "last_sync_at": botiquin.last_sync_at.isoformat()
    }), 200


@bp.get("/<int:botiquin_id>/stats")
def get_botiquin_stats(botiquin_id):
    """Get statistics for a specific botiquin"""
    botiquin = Botiquin.query.get(botiquin_id)
    if not botiquin:
        return jsonify({"error": "Botiquin not found"}), 404
    
    medicines = botiquin.medicines
    
    stats = {
        "botiquin_id": botiquin.id,
        "botiquin_name": botiquin.name,
        "total_medicines": len(medicines),
        "compartments_used": sum(1 for m in medicines if m.compartment_number),
        "compartments_available": botiquin.total_compartments - sum(1 for m in medicines if m.compartment_number),
        "status_summary": {
            "expired": sum(1 for m in medicines if m.status() == "EXPIRED"),
            "expires_soon": sum(1 for m in medicines if m.status() == "EXPIRES_SOON"),
            "expires_30": sum(1 for m in medicines if m.status() == "EXPIRES_30"),
            "out_of_stock": sum(1 for m in medicines if m.status() == "OUT_OF_STOCK"),
            "low_stock": sum(1 for m in medicines if m.status() == "LOW_STOCK"),
            "ok": sum(1 for m in medicines if m.status() == "OK")
        },
        "total_value": {
            "items_in_stock": sum(m.quantity for m in medicines)
        },
        "last_sync": botiquin.last_sync_at.isoformat() if botiquin.last_sync_at else None
    }
    
    return jsonify(stats), 200
