"""
Routes for Company management.
Essential for SaaS model - manages multiple companies with their botiquines.
"""

from flask import Blueprint, request, jsonify
from flask_login import current_user
from datetime import datetime
from db import db
from models.models import Company, User, Botiquin, Medicine
from utils.auth import require_auth

bp = Blueprint("companies", __name__)


@bp.route("/")
@require_auth
def list_companies():
    """
    List all companies.
    Super admin sees all, company admin sees only their company.
    """
    if current_user.is_super_admin():
        # Super admin sees all companies
        companies = Company.query.all()
    else:
        # Company admin sees only their company
        if not current_user.company_id:
            return jsonify({"error": "User not assigned to any company"}), 400
        companies = [current_user.company]
    
    return jsonify([c.to_dict() for c in companies]), 200


@bp.route("/", methods=["POST"])
@require_auth
def create_company():
    """
    Create a new company.
    Only super admin can create companies.
    """
    if not current_user.is_super_admin():
        return jsonify({"error": "Only super admin can create companies"}), 403
    
    data = request.get_json() or {}
    
    # Validate required fields
    if "name" not in data or not data["name"]:
        return jsonify({"error": "Company name is required"}), 400
    
    # Check if name already exists
    if Company.query.filter_by(name=data["name"]).first():
        return jsonify({"error": f"Company '{data['name']}' already exists"}), 400
    
    # Create company
    company = Company(
        name=data["name"],
        contact_email=data.get("contact_email"),
        contact_phone=data.get("contact_phone"),
        active=data.get("active", True)
    )
    
    db.session.add(company)
    db.session.commit()
    
    return jsonify(company.to_dict()), 201


@bp.route("/<int:company_id>")
@require_auth
def get_company(company_id):
    """
    Get company details.
    Users can only see their own company unless they're super admin.
    """
    company = Company.query.get(company_id)
    if not company:
        return jsonify({"error": "Company not found"}), 404
    
    return jsonify(company.to_dict()), 200


@bp.route("/<int:company_id>", methods=["PUT"])
@require_auth
def update_company(company_id):
    """
    Update company information.
    Only super admin can update companies.
    """
    if not current_user.is_super_admin():
        return jsonify({"error": "Only super admin can update companies"}), 403
    
    company = Company.query.get(company_id)
    if not company:
        return jsonify({"error": "Company not found"}), 404
    
    data = request.get_json() or {}
    
    # Check if name is being changed and if it's unique
    if "name" in data and data["name"] != company.name:
        if Company.query.filter_by(name=data["name"]).first():
            return jsonify({"error": f"Company name '{data['name']}' already exists"}), 400
    
    # Update fields
    if "name" in data:
        company.name = data["name"]
    if "contact_email" in data:
        company.contact_email = data["contact_email"]
    if "contact_phone" in data:
        company.contact_phone = data["contact_phone"]
    if "active" in data:
        company.active = data["active"]
    
    db.session.commit()
    return jsonify(company.to_dict()), 200


@bp.route("/<int:company_id>", methods=["DELETE"])
@require_auth
def delete_company(company_id):
    """
    Delete (deactivate) a company.
    Only super admin can delete companies.
    """
    if not current_user.is_super_admin():
        return jsonify({"error": "Only super admin can delete companies"}), 403
    
    company = Company.query.get(company_id)
    if not company:
        return jsonify({"error": "Company not found"}), 404
    
    # Check if company has active botiquines
    active_botiquines = Botiquin.query.filter_by(company_id=company_id, active=True).count()
    if active_botiquines > 0:
        return jsonify({
            "error": f"Cannot delete company with {active_botiquines} active botiquines. Deactivate them first."
        }), 400
    
    # Check if company has active users
    active_users = User.query.filter_by(company_id=company_id, active=True).count()
    if active_users > 0:
        return jsonify({
            "error": f"Cannot delete company with {active_users} active users. Deactivate them first."
        }), 400
    
    # Soft delete (deactivate)
    company.active = False
    db.session.commit()
    
    return jsonify({"message": "Company deactivated successfully"}), 200


@bp.route("/<int:company_id>/stats")
@require_auth
def get_company_stats(company_id):
    """
    Get detailed statistics for a company.
    """
    company = Company.query.get(company_id)
    if not company:
        return jsonify({"error": "Company not found"}), 404
    
    # Gather statistics
    botiquines = Botiquin.query.filter_by(company_id=company_id, active=True).all()
    users = User.query.filter_by(company_id=company_id, active=True).all()
    
    # Medicine statistics
    total_medicines = 0
    expired = 0
    expires_soon = 0
    low_stock = 0
    out_of_stock = 0
    
    for bot in botiquines:
        for med in bot.medicines:
            total_medicines += 1
            status = med.status()
            if status == "EXPIRED":
                expired += 1
            elif status == "EXPIRES_SOON":
                expires_soon += 1
            elif status == "LOW_STOCK":
                low_stock += 1
            elif status == "OUT_OF_STOCK":
                out_of_stock += 1
    
    stats = {
        "company": {
            "id": company.id,
            "name": company.name,
            "active": company.active
        },
        "counts": {
            "botiquines": len(botiquines),
            "users": len(users),
            "total_medicines": total_medicines,
            "total_compartments": sum(b.total_compartments for b in botiquines),
            "used_compartments": sum(
                sum(1 for m in b.medicines if m.compartment_number) 
                for b in botiquines
            )
        },
        "alerts": {
            "critical": expired + out_of_stock,
            "warning": expires_soon + low_stock,
            "expired": expired,
            "expires_soon": expires_soon,
            "low_stock": low_stock,
            "out_of_stock": out_of_stock
        },
        "botiquines_summary": [
            {
                "id": b.id,
                "name": b.name,
                "location": b.location,
                "medicines_count": len(b.medicines),
                "last_sync": b.last_sync_at.isoformat() if b.last_sync_at else None
            }
            for b in botiquines
        ]
    }
    
    return jsonify(stats), 200


@bp.route("/<int:company_id>/botiquines")
@require_auth
def get_company_botiquines(company_id):
    """
    Get all botiquines for a company.
    """
    botiquines = Botiquin.query.filter_by(company_id=company_id).all()
    return jsonify([b.to_dict() for b in botiquines]), 200


@bp.route("/<int:company_id>/users")
@require_auth
def get_company_users(company_id):
    """
    Get all users for a company.
    """
    users = User.query.filter_by(company_id=company_id).all()
    return jsonify([u.to_dict() for u in users]), 200


@bp.route("/<int:company_id>/alerts")
@require_auth
def get_company_alerts(company_id):
    """
    Get all active alerts for a company's botiquines.
    """
    company = Company.query.get(company_id)
    if not company:
        return jsonify({"error": "Company not found"}), 404

    botiquines = Botiquin.query.filter_by(company_id=company_id, active=True).all()
    
    alerts = {
        "critical": [],
        "warning": [],
        "info": []
    }
    
    for bot in botiquines:
        for med in bot.medicines:
            status = med.status()
            if status in ["EXPIRED", "OUT_OF_STOCK"]:
                alerts["critical"].append({
                    "botiquin": bot.name,
                    "medicine": med.medicine_name,
                    "status": status,
                    "compartment": med.compartment_number
                })
            elif status in ["EXPIRES_SOON", "LOW_STOCK"]:
                alerts["warning"].append({
                    "botiquin": bot.name,
                    "medicine": med.medicine_name,
                    "status": status,
                    "compartment": med.compartment_number,
                    "days_to_expiry": med.days_to_expiry() if status == "EXPIRES_SOON" else None
                })
    
    return jsonify({
        "company_id": company_id,
        "company_name": company.name,
        "alerts": alerts,
        "summary": {
            "critical_count": len(alerts["critical"]),
            "warning_count": len(alerts["warning"])
        }
    }), 200
