"""
Routes for hardware integration.
Receives sensor data and updates medicine inventory.
"""

from flask import Blueprint, request, jsonify
from flask_login import current_user
from datetime import datetime
import json
from db import db
from models.models import Botiquin, Medicine, HardwareLog
from utils.auth import require_auth

bp = Blueprint("hardware", __name__)


@bp.post("/sensor_data")
@require_auth
def receive_sensor_data():
    """
    Main endpoint to receive data from hardware sensors.
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Log raw data for debugging
    log_entry = HardwareLog(
        raw_data=json.dumps(data),
        sensor_type=data.get("sensor_type", "unknown"),
        created_at=datetime.utcnow()
    )
    
    try:
        # Validate required fields
        required = ["hardware_id", "compartments"]
        missing = [f for f in required if f not in data]
        if missing:
            log_entry.error_message = f"Missing fields: {missing}"
            db.session.add(log_entry)
            db.session.commit()
            return jsonify({"error": f"Missing required fields: {missing}"}), 400
        
        # Find botiquin by hardware_id
        botiquin = Botiquin.query.filter_by(hardware_id=data["hardware_id"]).first()
        if not botiquin:
            log_entry.error_message = f"Botiquin with hardware_id '{data['hardware_id']}' not found"
            db.session.add(log_entry)
            db.session.commit()
            return jsonify({"error": f"Botiquin not found for hardware_id: {data['hardware_id']}"}), 404
        
        # Enforce company isolation
        if not current_user.is_super_admin() and botiquin.company_id != current_user.company_id:
            return jsonify({"error": "Access denied: botiquin belongs to another company"}), 403

        log_entry.botiquin_id = botiquin.id
        
        results = []
        errors = []

        # Iterate through compartments
        for comp in data["compartments"]:
            compartment_number = comp.get("compartment")
            weight = comp.get("weight")
            medicine_name = comp.get("medicine_name")
            
            # Create individual log entries per compartment
            comp_log = HardwareLog(
                botiquin_id=botiquin.id,
                compartment_number=compartment_number,
                weight_reading=weight,
                sensor_type=data.get("sensor_type", "unknown"),
                raw_data=json.dumps(comp),
                created_at=datetime.utcnow()
            )
            
            if compartment_number is None or weight is None:
                comp_log.error_message = "Missing compartment or weight data"
                comp_log.processed = False
                db.session.add(comp_log)
                errors.append({
                    "compartment": compartment_number,
                    "error": "Missing compartment or weight data"
                })
                continue
            
            # Find medicine in the compartment
            medicine = Medicine.query.filter_by(
                botiquin_id=botiquin.id,
                compartment_number=compartment_number
            ).first()
            
            if not medicine:
                # Create a new medicine record for this compartment
                medicine = Medicine(
                    botiquin_id=botiquin.id,
                    compartment_number=compartment_number,
                    medicine_name=medicine_name,
                    current_weight=weight,
                    initial_weight=weight,
                    quantity=0,
                    reorder_level=5,
                    last_scan_at=datetime.utcnow()
                )
                db.session.add(medicine)
                db.session.flush()
                
                comp_log.processed = True
                db.session.add(comp_log)
                
                results.append({
                    "compartment": compartment_number,
                    "medicine": medicine.medicine_name or "No asignado",
                    "status": "NEW_MEDICINE"
                })
                continue
            
            old_quantity = medicine.quantity
            old_weight = medicine.current_weight

            new_quantity = medicine.update_from_sensor(weight, medicine_name)
            
            comp_log.processed = True
            db.session.add(comp_log)
            
            results.append({
                "compartment": compartment_number,
                "medicine": medicine.medicine_name or "No asignado",
                "old_weight": old_weight,
                "new_weight": medicine.current_weight,
                "old_quantity": old_quantity,
                "new_quantity": new_quantity,
                "status": medicine.status()
            })
        
        # Update botiquin sync timestamp
        botiquin.last_sync_at = datetime.utcnow()
        log_entry.processed = True
        
        db.session.add(log_entry)
        db.session.commit()
        
        return jsonify({
            "success": len(errors) == 0,
            "botiquin": botiquin.name,
            "results": results,
            "errors": errors if errors else None
        }), 200
        
    except Exception as e:
        log_entry.error_message = str(e)
        db.session.add(log_entry)
        db.session.commit()
        return jsonify({"error": str(e)}), 500


@bp.get("/logs")
@require_auth
def get_hardware_logs():
    """Get hardware communication logs for debugging."""
    botiquin_id = request.args.get("botiquin_id")
    limit = request.args.get("limit", 100, type=int)
    
    query = HardwareLog.query
    
    # Enforce company isolation for logs
    if not current_user.is_super_admin():
        query = query.join(Botiquin).filter(Botiquin.company_id == current_user.company_id)
        if botiquin_id:
            # require_auth already verifies botiquin_id in request.args
            query = query.filter(HardwareLog.botiquin_id == botiquin_id)
    elif botiquin_id:
        query = query.filter_by(botiquin_id=botiquin_id)
    
    logs = query.order_by(HardwareLog.created_at.desc()).limit(limit).all()
    return jsonify([log.to_dict() for log in logs]), 200


@bp.post("/test_connection")
@require_auth
def test_hardware_connection():
    """Test endpoint for hardware to verify connection."""
    data = request.get_json() or {}
    hardware_id = data.get("hardware_id", "unknown")
    
    botiquin = Botiquin.query.filter_by(hardware_id=hardware_id).first()
    
    # Isolation check
    if botiquin and not current_user.is_super_admin() and botiquin.company_id != current_user.company_id:
        return jsonify({"error": "Access denied"}), 403

    return jsonify({
        "status": "connected",
        "botiquin_found": botiquin is not None,
        "botiquin_name": botiquin.name if botiquin else None
    }), 200


@bp.post("/register_hardware")
@require_auth
def register_hardware():
    """Register new hardware with the system."""
    data = request.get_json()
    if not data or "hardware_id" not in data or "name" not in data:
        return jsonify({"error": "hardware_id and name required"}), 400
    
    existing = Botiquin.query.filter_by(hardware_id=data["hardware_id"]).first()
    if existing:
        return jsonify({"status": "already_registered", "botiquin": existing.to_dict()}), 200
    
    # Enforce company assignment
    company_id = data.get("company_id")
    if not current_user.is_super_admin():
        company_id = current_user.company_id
    
    botiquin = Botiquin(
        hardware_id=data["hardware_id"],
        name=data["name"],
        location=data.get("location", ""),
        company_id=company_id,
        total_compartments=int(data.get("compartments", 4)),
        active=True,
        last_sync_at=datetime.utcnow()
    )
    
    db.session.add(botiquin)
    db.session.commit()
    
    return jsonify({"status": "registered", "botiquin": botiquin.to_dict()}), 201
