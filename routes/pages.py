"""
Frontend page routes with botiquin support.
Handles dashboard views for multiple first aid kits.
"""

from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from flask_login import current_user, login_required, logout_user
from models.models import Medicine, Botiquin, Company, User
from datetime import datetime
from db import db

bp = Blueprint("pages", __name__)

"""
FIXES for Authentication Issues:

1. Fixed pages.py index() route - proper security check
2. Fixed user_routes.py login() route - handle both form and JSON data
"""

@bp.route("/")
def index():
    """Redirect to login or dashboard based on session - FIXED SECURITY"""
    if current_user.is_authenticated:
        if current_user.active:
            return redirect(url_for("pages.dashboard"))
        logout_user()

    return redirect(url_for("users.login"))


@bp.get("/dashboard")
@login_required
def dashboard():
    """
    Main dashboard showing all botiquines for the user's company.
    Super admin sees all botiquines from all companies.
    """
    user = current_user
    if not user.active:
        logout_user()
        flash("Tu cuenta está inactiva", "danger")
        return redirect(url_for("users.login"))

    # Get botiquines based on user type
    if user.is_super_admin():
        # Super admin sees all
        botiquines = Botiquin.query.filter_by(active=True).all()
        companies = Company.query.filter_by(active=True).all()
        show_company = True
    else:
        # Company admin sees only their company's botiquines
        if not user.company_id:
            return "User not assigned to any company", 403
        botiquines = Botiquin.query.filter_by(
            company_id=user.company_id, 
            active=True
        ).all()
        companies = [user.company] if user.company else []
        show_company = False
    
    # Collect statistics
    total_medicines = 0
    critical_count = 0
    warning_count = 0
    
    botiquines_data = []
    for bot in botiquines:
        medicines = bot.medicines
        bot_critical = sum(1 for m in medicines if m.status() in ["EXPIRED", "OUT_OF_STOCK"])
        bot_warning = sum(1 for m in medicines if m.status() in ["EXPIRES_SOON", "LOW_STOCK"])
        
        total_medicines += len(medicines)
        critical_count += bot_critical
        warning_count += bot_warning
        
        company_name = bot.company.name if bot.company else None

        botiquines_data.append({
            "id": bot.id,
            "name": bot.name,
            "location": bot.location,
            "company_name": company_name,
            "is_assigned": company_name is not None,
            "medicines_count": len(medicines),
            "critical": bot_critical,
            "warning": bot_warning,
            "compartments_total": bot.total_compartments,
            "last_sync": bot.last_sync_at.strftime("%Y-%m-%d %H:%M:%S") if bot.last_sync_at else "Never"
        })
    
    summary = {
        "total_botiquines": len(botiquines),
        "total_medicines": total_medicines,
        "critical": critical_count,
        "warning": warning_count,
        "companies": len(companies) if show_company else None
    }
    
    return render_template(
        "dashboard.html",
        summary=summary,
        botiquines=botiquines_data,
        show_company=show_company
    )


@bp.get("/botiquin/<int:botiquin_id>")
@login_required
def botiquin_detail(botiquin_id):
    """Detailed view of a specific botiquin with compartment visualization"""
    user = current_user
    if not user.active:
        logout_user()
        flash("Tu cuenta está inactiva", "danger")
        return redirect(url_for("users.login"))
    
    botiquin = Botiquin.query.get(botiquin_id)
    if not botiquin:
        return "Botiquin not found", 404
    
    # Check access permissions
    if not user.is_super_admin() and botiquin.company_id != user.company_id:
        return "Access denied", 403
    
    # Get filter parameters
    status_filter = request.args.get("status")
    
    # Build comp_map: list of dicts with keys: number, medicine_name, status, quantity
    comp_status = botiquin.get_compartment_status()
    comp_map = {}
    for number, data in comp_status.items():
        comp_map[number] = {
            "number": number,
            "medicine_name": data.get("medicine") if data else None,
            "status": data.get("status") if data else None,
            "quantity": data.get("quantity") if data else None,
        }
    
    # Get medicines list
    medicines = botiquin.medicines
    if status_filter:
        medicines = [m for m in medicines if m.status() == status_filter]
    
    # Build summary
    all_medicines = botiquin.medicines
    summary = {
        "total": len(all_medicines),
        "critical": sum(1 for m in all_medicines if m.status() in ["EXPIRED", "OUT_OF_STOCK"]),
        "warning": sum(1 for m in all_medicines if m.status() in ["EXPIRES_SOON", "LOW_STOCK"]),
        "ok": sum(1 for m in all_medicines if m.status() == "OK"),
        "total_compartments": botiquin.total_compartments,
        "last_sync": botiquin.last_sync_at.strftime("%Y-%m-%d %H:%M:%S") if botiquin.last_sync_at else "Never"
    }
    
    return render_template(
        "botiquin_detail.html",
        botiquin=botiquin,
        summary=summary,
        current_status=status_filter,
        comp_map=comp_map,
        grid_cols=botiquin.compartment_cols
    )


@bp.get("/botiquin/<int:botiquin_id>/inventory")
@login_required
def botiquin_inventory(botiquin_id):
    """Inventory view for a specific botiquin"""
    user = current_user
    if not user.active:
        logout_user()
        flash("Tu cuenta está inactiva", "danger")
        return redirect(url_for("users.login"))
    
    botiquin = Botiquin.query.get(botiquin_id)
    if not botiquin:
        return "Botiquin not found", 404
    
    # Check access permissions
    if not user.is_super_admin() and botiquin.company_id != user.company_id:
        return "Access denied", 403
    
    status_filter = request.args.get("status")
    
    medicines = botiquin.medicines
    if status_filter:
        medicines = [m for m in medicines if m.status() == status_filter]
    
    grouped_data = {botiquin.name: [med.to_dict() for med in medicines]}
    
    all_medicines = botiquin.medicines
    summary = {
        "total": len(all_medicines),
        "critical": sum(1 for m in all_medicines if m.status() in ["EXPIRED", "OUT_OF_STOCK"]),
        "low_stock": sum(1 for m in all_medicines if m.status() == "LOW_STOCK"),
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return render_template(
        "inventory.html",
        grouped_data=grouped_data,
        summary=summary,
        current_status=status_filter,
        show_company=False
    )


@bp.get("/inventory")
@login_required
def inventory():
    """Inventory view that lists botiquines accessible to the current user."""
    user = current_user
    if not user.active:
        logout_user()
        flash("Tu cuenta está inactiva", "danger")
        return redirect(url_for("users.login"))

    status_filter = request.args.get("status")

    # Determine scope based on role
    if user.is_super_admin():
        botiquines = Botiquin.query.filter_by(active=True).all()
        show_company = True
    else:
        if not user.company_id:
            return "User not assigned to any company", 403
        botiquines = Botiquin.query.filter_by(company_id=user.company_id, active=True).all()
        show_company = False

    grouped_data = {}

    total_medicines = 0
    total_critical = 0
    total_warning = 0
    latest_sync = None
    display_count = 0

    for bot in botiquines:
        medicines = bot.medicines
        med_total = len(medicines)

        total_medicines += med_total
        total_critical += sum(1 for m in medicines if m.status() in ["EXPIRED", "OUT_OF_STOCK"])
        total_warning += sum(1 for m in medicines if m.status() in ["EXPIRES_SOON", "EXPIRES_30", "LOW_STOCK"])

        if bot.last_sync_at and (latest_sync is None or bot.last_sync_at > latest_sync):
            latest_sync = bot.last_sync_at

        section_key = bot.name
        if show_company:
            company_label = bot.company.name if bot.company else "Sin asignar"
            section_key = f"{bot.name} · {company_label}"

        rows = []
        for compartment_number in range(1, bot.total_compartments + 1):
            med = next((m for m in medicines if m.compartment_number == compartment_number), None)

            if med is None and status_filter:
                continue

            status = med.status() if med else "EMPTY"
            if status_filter:
                if med is None:
                    continue
                if status_filter == "OK":
                    if status != "OK":
                        continue
                elif status != status_filter:
                    continue

            row = {
                "bot_id": bot.id,
                "bot_name": bot.name,
                "company_name": bot.company.name if bot.company else None,
                "location": bot.location,
                "compartment": compartment_number,
                "has_medicine": med is not None,
                "trade_name": med.trade_name if med else None,
                "generic_name": med.generic_name if med else None,
                "brand": med.brand if med else None,
                "strength": med.strength if med else None,
                "average_weight": med.unit_weight if med else None,
                "current_weight": med.current_weight if med else None,
                "quantity": med.quantity if med else 0,
                "reorder_level": med.reorder_level if med else None,
                "max_capacity": med.max_capacity if med else None,
                "expiry_date": med.expiry_date.isoformat() if med and med.expiry_date else None,
                "days_to_expiry": med.days_to_expiry() if med else None,
                "status": status,
                "last_scan": med.last_scan_at.strftime("%Y-%m-%d %H:%M:%S") if med and med.last_scan_at else None,
            }

            rows.append(row)
            display_count += 1

        if not rows:
            continue

        grouped_data[section_key] = {
            "bot": {
                "id": bot.id,
                "name": bot.name,
                "company_name": bot.company.name if bot.company else None,
                "location": bot.location,
                "last_sync": bot.last_sync_at.strftime("%Y-%m-%d %H:%M:%S") if bot.last_sync_at else "Never",
            },
            "rows": rows
        }

    summary = {
        "total_botiquines": len(botiquines),
        "total_medicines": total_medicines,
        "critical_alerts": total_critical,
        "warning_alerts": total_warning,
        "last_update": latest_sync.strftime("%Y-%m-%d %H:%M:%S") if latest_sync else "Nunca"
    }

    return render_template(
        "inventory.html",
        grouped_data=grouped_data,
        summary=summary,
        current_status=status_filter,
        show_company=show_company,
        display_count=display_count
    )


@bp.get("/companies")
@login_required
def companies():
    """Company management view (super admin only)"""
    user = current_user
    if not user.active:
        logout_user()
        flash("Tu cuenta está inactiva", "danger")
        return redirect(url_for("users.login"))

    if not user.is_super_admin():
        return "Access denied", 403
    
    companies = Company.query.all()
    companies_data = []
    
    for company in companies:
        companies_data.append({
            "id": company.id,
            "name": company.name,
            "email": company.contact_email,
            "phone": company.contact_phone,
            "active": company.active,
            "botiquines_count": len(company.botiquines),
            "users_count": len(company.users),
            "created": company.created_at.strftime("%Y-%m-%d")
        })
    
    # NOTE: companies.html template not created yet - will show basic info for now
    return render_template(
        "dashboard.html",  # Use dashboard as fallback until companies.html is created
        summary={"total_companies": len(companies)},
        companies=companies_data,
        show_company=True
    )

@bp.get("/botiquines/assign")
@login_required
def assign_botiquines():
    """View to list unassigned botiquines for super admins to assign"""
    user = current_user
    if not user.active:
        logout_user()
        flash("Tu cuenta está inactiva", "danger")
        return redirect(url_for("users.login"))

    if not user.is_super_admin():
        return "Access denied", 403
    
    unassigned_botiquines = Botiquin.query.filter_by(company_id=None).all()
    return render_template("assign_botiquines.html", unassigned=unassigned_botiquines)

@bp.route("/botiquin/<int:botiquin_id>/assign", methods=["GET", "POST"])
@login_required
def assign_single_botiquin(botiquin_id):
    """Assign a single botiquin to a company (super admin only)"""
    user = current_user
    if not user.active:
        logout_user()
        flash("Tu cuenta está inactiva", "danger")
        return redirect(url_for("users.login"))

    if not user.is_super_admin():
        return "Access denied", 403
    
    botiquin = Botiquin.query.get(botiquin_id)
    if not botiquin or not botiquin.active:
        return "Botiquin not found or inactive", 404
    
    if request.method == "GET":
        companies = Company.query.filter_by(active=True).all()
        return render_template("assign_single.html", botiquin=botiquin, companies=companies)
    
    # POST
    company_id = request.form.get("company_id")
    if not company_id:
        return "Company ID is required", 400
    
    company = Company.query.get(company_id)
    if not company or not company.active:
        return "Invalid company selected", 400
    
    botiquin.company_id = company.id
    db.session.commit()
    flash("Botiquín asignado correctamente", "success")
    return redirect(url_for("pages.dashboard"))
