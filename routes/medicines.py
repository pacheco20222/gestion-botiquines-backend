"""
Routes for the Medicine resource.
Updated to support botiquines and weight-based calculations.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, date
from db import db
from models.models import Medicine, Botiquin

bp = Blueprint("medicines", __name__)

# -------- Helpers --------
def parse_date(value):
    if isinstance(value, date):
        return value
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None

def validate_payload(data, *, partial=False):
    errors = []
    
    # Updated required fields to include botiquin_id
    required = ["botiquin_id", "trade_name", "generic_name", "strength", "expiry_date", "quantity", "reorder_level"]
    
    if not partial:
        for f in required:
            if f not in data or data.get(f) in (None, ""):
                if f == "botiquin_id":
                    errors.append("'botiquin_id' is required (must assign to a botiquin)")
                elif f == "reorder_level":
                    errors.append("'reorder_level' is required (minimum stock threshold)")
                elif f == "quantity":
                    errors.append("'quantity' is required (stock count)")
                else:
                    errors.append(f"'{f}' is required")
    
    # Validate botiquin exists
    if "botiquin_id" in data and data.get("botiquin_id"):
        bot = Botiquin.query.get(data["botiquin_id"])
        if not bot:
            errors.append(f"Botiquin with id {data['botiquin_id']} does not exist")
    
    # Validate numeric fields
    for num_field in ["quantity", "reorder_level", "compartment_number", "max_capacity"]:
        if num_field in data and data[num_field] is not None:
            try:
                v = int(data[num_field])
                if v < 0:
                    errors.append(f"'{num_field}' must be >= 0")
            except (TypeError, ValueError):
                errors.append(f"'{num_field}' must be an integer")
    
    # Validate float fields
    weight_key = "average_weight" if "average_weight" in data else ("unit_weight" if "unit_weight" in data else None)
    if weight_key and data[weight_key] is not None:
        try:
            unit_w = float(data[weight_key])
            if unit_w <= 0:
                errors.append("'average_weight' must be greater than 0")
        except (TypeError, ValueError):
            errors.append("'average_weight' must be a number")

    if "current_weight" in data and data["current_weight"] is not None:
        try:
            curr_w = float(data["current_weight"])
            if curr_w < 0:
                errors.append("'current_weight' must be >= 0")
        except (TypeError, ValueError):
            errors.append("'current_weight' must be a number")
    
    # Validate expiry date
    if "expiry_date" in data and data.get("expiry_date"):
        exp = parse_date(data["expiry_date"])
        if exp is None:
            errors.append("'expiry_date' must be YYYY-MM-DD")
        # Note: We allow past dates for already expired medicines in inventory

    return (len(errors) == 0, errors)

# -------- Routes --------

@bp.get("/")
def list_medicines():
    """List all medicines, optionally filtered by botiquin"""
    botiquin_id = request.args.get("botiquin_id")
    
    query = Medicine.query
    if botiquin_id:
        query = query.filter_by(botiquin_id=botiquin_id)
    
    meds = query.order_by(Medicine.id.asc()).all()
    return jsonify([m.to_dict() for m in meds]), 200


@bp.get("/botiquin/<int:botiquin_id>")
def list_medicines_by_botiquin(botiquin_id):
    """List all medicines in a specific botiquin"""
    botiquin = Botiquin.query.get(botiquin_id)
    if not botiquin:
        return jsonify({"error": "Botiquin not found"}), 404
    
    meds = Medicine.query.filter_by(botiquin_id=botiquin_id).order_by(Medicine.compartment_number.asc()).all()
    return jsonify({
        "botiquin": botiquin.to_dict(),
        "medicines": [m.to_dict() for m in meds]
    }), 200


@bp.get("/filter")
def filter_medicines():
    """
    Returns medicines filtered by status and/or botiquin.
    Example: /api/medicines/filter?status=EXPIRED&botiquin_id=1
    Valid statuses: OUT_OF_STOCK, EXPIRED, EXPIRES_SOON, EXPIRES_30, LOW_STOCK, OK
    """
    status = request.args.get("status")
    botiquin_id = request.args.get("botiquin_id")
    
    query = Medicine.query
    if botiquin_id:
        query = query.filter_by(botiquin_id=botiquin_id)
    
    meds = query.order_by(Medicine.id.asc()).all()
    
    if status:
        results = [m.to_dict() for m in meds if m.status() == status]
    else:
        results = [m.to_dict() for m in meds]
    
    return jsonify(results), 200


@bp.get("/alerts")
def get_alerts():
    """
    Returns medicines grouped by alert category.
    Can be filtered by botiquin_id.
    """
    botiquin_id = request.args.get("botiquin_id")
    
    query = Medicine.query
    if botiquin_id:
        query = query.filter_by(botiquin_id=botiquin_id)
    
    meds = query.order_by(Medicine.id.asc()).all()
    
    alerts = {
        "critical": [],
        "preventive": [],
        "normal": []
    }

    for m in meds:
        status = m.status()
        med_dict = m.to_dict()
        if status in ["OUT_OF_STOCK", "EXPIRED", "EXPIRES_SOON"]:
            alerts["critical"].append(med_dict)
        elif status in ["EXPIRES_30", "LOW_STOCK"]:
            alerts["preventive"].append(med_dict)
        else:
            alerts["normal"].append(med_dict)

    return jsonify(alerts), 200


@bp.post("/")
def create_medicine():
    """Create a new medicine in a botiquin"""
    data = request.get_json() or {}
    ok, errors = validate_payload(data, partial=False)
    if not ok:
        return jsonify({"errors": errors}), 400

    weight_value = data.get("average_weight", data.get("unit_weight"))

    med = Medicine(
        botiquin_id=int(data.get("botiquin_id")),
        compartment_number=int(data.get("compartment_number")) if data.get("compartment_number") else None,
        trade_name=data.get("trade_name"),
        generic_name=data.get("generic_name"),
        brand=data.get("brand"),
        strength=data.get("strength"),
        unit_weight=float(weight_value) if weight_value else None,
        current_weight=float(data.get("current_weight")) if data.get("current_weight") else None,
        quantity=int(data.get("quantity")),
        reorder_level=int(data.get("reorder_level")),
        max_capacity=int(data.get("max_capacity")) if data.get("max_capacity") else None,
        expiry_date=parse_date(data.get("expiry_date")),
        batch_number=data.get("batch_number"),
        last_scan_at=datetime.utcnow(),
    )
    
    # Calculate quantity from weight if both weights are provided
    if med.unit_weight and med.current_weight:
        med.calculate_quantity_from_weight()
    
    db.session.add(med)
    db.session.commit()
    return jsonify(med.to_dict()), 201


@bp.get("/<int:med_id>")
def get_medicine(med_id):
    med = Medicine.query.get(med_id)
    if not med:
        return jsonify({"error": "Medicine not found"}), 404
    return jsonify(med.to_dict()), 200


@bp.put("/<int:med_id>")
def update_medicine(med_id):
    med = Medicine.query.get(med_id)
    if not med:
        return jsonify({"error": "Medicine not found"}), 404

    data = request.get_json() or {}
    ok, errors = validate_payload(data, partial=True)
    if not ok:
        return jsonify({"errors": errors}), 400

    # List of fields that can be updated
    fields = [
        "botiquin_id", "compartment_number", "trade_name", "generic_name", 
        "brand", "strength", "average_weight", "unit_weight", "current_weight", "quantity", 
        "reorder_level", "max_capacity", "expiry_date", "batch_number", "last_scan_at"
    ]
    
    for f in fields:
        if f in data:
            if f == "expiry_date":
                setattr(med, f, parse_date(data[f]))
            elif f in ["quantity", "reorder_level", "compartment_number", "max_capacity", "botiquin_id"]:
                setattr(med, f, int(data[f]) if data[f] is not None else None)
            elif f in ["average_weight", "unit_weight", "current_weight"]:
                value = float(data[f]) if data[f] is not None else None
                if f in ["average_weight", "unit_weight"]:
                    med.unit_weight = value
                else:
                    med.current_weight = value
            elif f == "last_scan_at":
                val = data[f]
                if val is True:
                    setattr(med, f, datetime.utcnow())
                elif isinstance(val, str):
                    try:
                        setattr(med, f, datetime.fromisoformat(val))
                    except ValueError:
                        pass
            else:
                setattr(med, f, data[f])
    
    # Recalculate quantity if weights changed
    if any(k in data for k in ["average_weight", "unit_weight", "current_weight"]):
        if med.unit_weight and med.current_weight:
            med.calculate_quantity_from_weight()

    db.session.commit()
    return jsonify(med.to_dict()), 200


@bp.delete("/<int:med_id>")
def delete_medicine(med_id):
    med = Medicine.query.get(med_id)
    if not med:
        return jsonify({"error": "Medicine not found"}), 404

    db.session.delete(med)
    db.session.commit()
    return jsonify({"message": "Medicine deleted"}), 200


@bp.post("/<int:med_id>/update_weight")
def update_medicine_weight(med_id):
    """
    Special endpoint to update medicine weight from hardware.
    Automatically calculates new quantity.
    """
    med = Medicine.query.get(med_id)
    if not med:
        return jsonify({"error": "Medicine not found"}), 404
    
    data = request.get_json() or {}
    weight = data.get("weight")
    
    if weight is None:
        return jsonify({"error": "Weight is required"}), 400
    
    try:
        weight = float(weight)
        if weight < 0:
            return jsonify({"error": "Weight must be >= 0"}), 400
    except (TypeError, ValueError):
        return jsonify({"error": "Weight must be a number"}), 400
    
    # Update weight and calculate new quantity
    old_quantity = med.quantity
    new_quantity = med.update_from_sensor(weight)
    
    db.session.commit()
    
    return jsonify({
        "medicine": med.to_dict(),
        "old_quantity": old_quantity,
        "new_quantity": new_quantity,
        "quantity_change": new_quantity - old_quantity
    }), 200
