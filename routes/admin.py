"""
Admin routes for system management.
Only accessible by super admins.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from db import db
from models.models import User, Company, Botiquin, Medicine, HardwareLog
from werkzeug.security import generate_password_hash
import os

bp = Blueprint("admin", __name__)

def get_current_user():
    """Get current user from Basic Auth or session"""
    from flask_login import current_user
    import base64
    
    # Try Basic Auth first (for API calls)
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Basic '):
        try:
            # Decode Basic Auth
            encoded_credentials = auth_header.split(' ')[1]
            credentials = base64.b64decode(encoded_credentials).decode('utf-8')
            username, password = credentials.split(':', 1)
            
            # Find user
            user = User.query.filter_by(username=username, active=True).first()
            if user and user.check_password(password):
                return user
        except Exception as e:
            print(f"Basic Auth error: {e}")
            pass
    
    # Fallback to session-based auth
    if current_user.is_authenticated and getattr(current_user, "active", False):
        return current_user
    
    return None

@bp.post("/reset-demo")
def reset_demo_data():
    """
    Reset all database tables to demo state.
    Only accessible by super admins.
    """
    user = get_current_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    
    if not user.is_super_admin():
        return jsonify({"error": "Access denied. Super admin required."}), 403
    
    try:
        # Delete all data in correct order (respecting foreign keys)
        print("Starting demo data reset...")
        
        # 1. Delete hardware logs
        HardwareLog.query.delete()
        print("Deleted hardware logs")
        
        # 2. Delete medicines
        Medicine.query.delete()
        print("Deleted medicines")
        
        # 3. Delete botiquines
        Botiquin.query.delete()
        print("Deleted botiquines")
        
        # 4. Delete users (except super admin)
        User.query.filter(User.user_type != 'super_admin').delete()
        print("Deleted non-super-admin users")
        
        # 5. Delete companies
        Company.query.delete()
        print("Deleted companies")
        
        # 6. Create demo companies (matching seed.py exactly)
        demo_company = Company(
            name="Demo Company"
        )
        db.session.add(demo_company)

        health_corp = Company(
            name="Health Corp"
        )
        db.session.add(health_corp)

        techcorp = Company(
            name="TechCorp Solutions"
        )
        db.session.add(techcorp)

        manufacturing = Company(
            name="Manufacturing Inc"
        )
        db.session.add(manufacturing)

        healthcare_plus = Company(
            name="Healthcare Plus"
        )
        db.session.add(healthcare_plus)
        
        db.session.flush()  # Get company IDs
        
        # 7. Create demo company admin users (matching seed.py exactly)
        demo_admin = User(
            username="demo_admin",
            email="demo_admin@example.com",
            user_type="company_admin",
            company_id=demo_company.id,
            active=True
        )
        demo_admin.set_password("password123")
        db.session.add(demo_admin)

        health_admin = User(
            username="health_admin",
            email="health_admin@example.com",
            user_type="company_admin",
            company_id=health_corp.id,
            active=True
        )
        health_admin.set_password("healthpass456")
        db.session.add(health_admin)

        tech_admin = User(
            username="tech_admin",
            email="tech_admin@example.com",
            user_type="company_admin",
            company_id=techcorp.id,
            active=True
        )
        tech_admin.set_password("techpass123")
        db.session.add(tech_admin)

        mfg_admin = User(
            username="mfg_admin",
            email="mfg_admin@example.com",
            user_type="company_admin",
            company_id=manufacturing.id,
            active=True
        )
        mfg_admin.set_password("mfgpass123")
        db.session.add(mfg_admin)

        healthcare_admin = User(
            username="healthcare_admin",
            email="healthcare_admin@example.com",
            user_type="company_admin",
            company_id=healthcare_plus.id,
            active=True
        )
        healthcare_admin.set_password("healthcarepass123")
        db.session.add(healthcare_admin)
        
        # 8. Create demo botiquines (matching seed.py exactly)
        botiquin_demo = Botiquin(
            hardware_id="BOT_DEMO_COMP",
            name="Botiquín Demo Company",
            location="Demo HQ",
            total_compartments=4,
            last_sync_at=datetime.utcnow(),
            company_id=demo_company.id,
            active=True
        )
        db.session.add(botiquin_demo)

        botiquin_health = Botiquin(
            hardware_id="BOT_HEALTH_CORP",
            name="Botiquín Health Corp",
            location="Health Corp Main Office",
            total_compartments=4,
            last_sync_at=datetime.utcnow(),
            company_id=health_corp.id,
            active=True
        )
        db.session.add(botiquin_health)

        botiquin_tech = Botiquin(
            hardware_id="BOT_TECHCORP",
            name="Botiquín TechCorp",
            location="TechCorp Office",
            total_compartments=4,
            last_sync_at=datetime.utcnow(),
            company_id=techcorp.id,
            active=True
        )
        db.session.add(botiquin_tech)

        botiquin_mfg = Botiquin(
            hardware_id="BOT_MANUFACTURING",
            name="Botiquín Manufacturing",
            location="Manufacturing Plant",
            total_compartments=4,
            last_sync_at=datetime.utcnow(),
            company_id=manufacturing.id,
            active=True
        )
        db.session.add(botiquin_mfg)

        botiquin_healthcare = Botiquin(
            hardware_id="BOT_HEALTHCARE_PLUS",
            name="Botiquín Healthcare Plus",
            location="Healthcare Plus Clinic",
            total_compartments=4,
            last_sync_at=datetime.utcnow(),
            company_id=healthcare_plus.id,
            active=True
        )
        db.session.add(botiquin_healthcare)

        # Unassigned botiquines (with realistic weight data from hardware)
        botiquin_unassigned1 = Botiquin(
            hardware_id="BOT_UNASSIGNED_1",
            name="Botiquín Unassigned 1",
            location="Warehouse",
            total_compartments=4,
            last_sync_at=datetime.utcnow(),
            company_id=None,
            active=True
        )
        db.session.add(botiquin_unassigned1)

        botiquin_unassigned2 = Botiquin(
            hardware_id="BOT_UNASSIGNED_2",
            name="Botiquín Unassigned 2",
            location="Storage Room",
            total_compartments=4,
            last_sync_at=datetime.utcnow(),
            company_id=None,
            active=True
        )
        db.session.add(botiquin_unassigned2)

        botiquin_unassigned3 = Botiquin(
            hardware_id="BOT_UNASSIGNED_3",
            name="Botiquín Unassigned 3",
            location="Distribution Center",
            total_compartments=4,
            last_sync_at=datetime.utcnow(),
            company_id=None,
            active=True
        )
        db.session.add(botiquin_unassigned3)
        
        db.session.flush()  # Get botiquin IDs
        
        # 9. Create demo medicines (matching seed.py exactly - ALL with realistic weight data)
        from datetime import date, timedelta
        
        # Medicines for Demo Company botiquin
        medicines_demo = [
            Medicine(
                compartment_number=1,
                medicine_name="tylenol",
                initial_weight=13.2,
                current_weight=9.9,
                reorder_level=8,
                max_capacity=24,
                expiry_date=date.today() + timedelta(days=180),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_demo.id
            ),
            Medicine(
                compartment_number=2,
                medicine_name="ibuprofen",
                initial_weight=7.2,
                current_weight=2.4,
                reorder_level=5,
                max_capacity=18,
                expiry_date=date.today() + timedelta(days=60),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_demo.id
            ),
            Medicine(
                compartment_number=3,
                medicine_name="aspirin",
                initial_weight=6.3,
                current_weight=0.35,
                reorder_level=6,
                max_capacity=18,
                expiry_date=date.today() - timedelta(days=5),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_demo.id
            ),
            Medicine(
                compartment_number=4,
                medicine_name="gel",
                initial_weight=360.0,
                current_weight=180.0,
                reorder_level=2,
                max_capacity=6,
                expiry_date=date.today() + timedelta(days=365),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_demo.id
            )
        ]

        # Medicines for Health Corp botiquin
        medicines_health = [
            Medicine(
                compartment_number=1,
                medicine_name="paracetamol",
                initial_weight=12.0,
                current_weight=8.0,
                reorder_level=10,
                max_capacity=24,
                expiry_date=date.today() + timedelta(days=120),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_health.id
            ),
            Medicine(
                compartment_number=2,
                medicine_name="diclofenac",
                initial_weight=9.0,
                current_weight=6.75,
                reorder_level=8,
                max_capacity=20,
                expiry_date=date.today() + timedelta(days=200),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_health.id
            ),
            Medicine(
                compartment_number=3,
                medicine_name="omeprazole",
                initial_weight=6.0,
                current_weight=0.6,
                reorder_level=10,
                max_capacity=20,
                expiry_date=date.today() + timedelta(days=90),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_health.id
            ),
            Medicine(
                compartment_number=4,
                medicine_name="bandages",
                initial_weight=100.0,
                current_weight=75.0,
                reorder_level=5,
                max_capacity=20,
                expiry_date=date.today() + timedelta(days=730),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_health.id
            )
        ]

        # Medicines for TechCorp botiquin
        medicines_tech = [
            Medicine(
                compartment_number=1,
                medicine_name="acetaminophen",
                initial_weight=10.4,
                current_weight=7.8,
                reorder_level=8,
                max_capacity=20,
                expiry_date=date.today() + timedelta(days=150),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_tech.id
            ),
            Medicine(
                compartment_number=2,
                medicine_name="naproxen",
                initial_weight=7.6,
                current_weight=3.8,
                reorder_level=6,
                max_capacity=20,
                expiry_date=date.today() + timedelta(days=100),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_tech.id
            ),
            Medicine(
                compartment_number=3,
                medicine_name="loratadine",
                initial_weight=5.0,
                current_weight=2.5,
                reorder_level=8,
                max_capacity=20,
                expiry_date=date.today() + timedelta(days=25),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_tech.id
            ),
            Medicine(
                compartment_number=4,
                medicine_name="antiseptic",
                initial_weight=250.0,
                current_weight=125.0,
                reorder_level=3,
                max_capacity=10,
                expiry_date=date.today() + timedelta(days=400),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_tech.id
            )
        ]

        # Medicines for Manufacturing botiquin
        medicines_mfg = [
            Medicine(
                compartment_number=1,
                medicine_name=None,  # No medicine name assigned yet
                initial_weight=16.0,
                current_weight=12.8,
                reorder_level=8,
                max_capacity=20,
                expiry_date=date.today() + timedelta(days=180),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_mfg.id
            ),
            Medicine(
                compartment_number=2,
                medicine_name=None,
                initial_weight=9.5,
                current_weight=7.1,
                reorder_level=5,
                max_capacity=15,
                expiry_date=date.today() + timedelta(days=120),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_mfg.id
            ),
            Medicine(
                compartment_number=3,
                medicine_name=None,
                initial_weight=11.0,
                current_weight=2.2,
                reorder_level=6,
                max_capacity=18,
                expiry_date=date.today() + timedelta(days=90),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_mfg.id
            ),
            Medicine(
                compartment_number=4,
                medicine_name=None,
                initial_weight=190.0,
                current_weight=142.5,
                reorder_level=3,
                max_capacity=8,
                expiry_date=date.today() + timedelta(days=280),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_mfg.id
            )
        ]

        # Medicines for Healthcare Plus botiquin
        medicines_healthcare = [
            Medicine(
                compartment_number=1,
                medicine_name=None,  # No medicine name assigned yet
                initial_weight=14.5,
                current_weight=11.6,
                reorder_level=9,
                max_capacity=22,
                expiry_date=date.today() + timedelta(days=160),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_healthcare.id
            ),
            Medicine(
                compartment_number=2,
                medicine_name=None,
                initial_weight=8.8,
                current_weight=6.6,
                reorder_level=7,
                max_capacity=16,
                expiry_date=date.today() + timedelta(days=140),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_healthcare.id
            ),
            Medicine(
                compartment_number=3,
                medicine_name=None,
                initial_weight=12.5,
                current_weight=1.9,
                reorder_level=9,
                max_capacity=19,
                expiry_date=date.today() + timedelta(days=80),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_healthcare.id
            ),
            Medicine(
                compartment_number=4,
                medicine_name=None,
                initial_weight=210.0,
                current_weight=157.5,
                reorder_level=5,
                max_capacity=12,
                expiry_date=date.today() + timedelta(days=270),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_healthcare.id
            )
        ]

        # Medicines for unassigned botiquines (with realistic weight data)
        medicines_unassigned1 = [
            Medicine(
                compartment_number=1,
                medicine_name=None,  # No medicine name assigned yet
                initial_weight=15.0,
                current_weight=12.5,
                reorder_level=8,
                max_capacity=20,
                expiry_date=date.today() + timedelta(days=200),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_unassigned1.id
            ),
            Medicine(
                compartment_number=2,
                medicine_name=None,
                initial_weight=8.5,
                current_weight=6.2,
                reorder_level=5,
                max_capacity=15,
                expiry_date=date.today() + timedelta(days=150),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_unassigned1.id
            ),
            Medicine(
                compartment_number=3,
                medicine_name=None,
                initial_weight=12.0,
                current_weight=3.8,
                reorder_level=6,
                max_capacity=18,
                expiry_date=date.today() + timedelta(days=100),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_unassigned1.id
            ),
            Medicine(
                compartment_number=4,
                medicine_name=None,
                initial_weight=200.0,
                current_weight=150.0,
                reorder_level=3,
                max_capacity=8,
                expiry_date=date.today() + timedelta(days=300),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_unassigned1.id
            )
        ]

        medicines_unassigned2 = [
            Medicine(
                compartment_number=1,
                medicine_name=None,
                initial_weight=18.0,
                current_weight=14.5,
                reorder_level=10,
                max_capacity=25,
                expiry_date=date.today() + timedelta(days=180),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_unassigned2.id
            ),
            Medicine(
                compartment_number=2,
                medicine_name=None,
                initial_weight=10.5,
                current_weight=7.8,
                reorder_level=6,
                max_capacity=18,
                expiry_date=date.today() + timedelta(days=120),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_unassigned2.id
            ),
            Medicine(
                compartment_number=3,
                medicine_name=None,
                initial_weight=14.0,
                current_weight=2.1,
                reorder_level=8,
                max_capacity=20,
                expiry_date=date.today() + timedelta(days=90),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_unassigned2.id
            ),
            Medicine(
                compartment_number=4,
                medicine_name=None,
                initial_weight=180.0,
                current_weight=120.0,
                reorder_level=4,
                max_capacity=10,
                expiry_date=date.today() + timedelta(days=250),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_unassigned2.id
            )
        ]

        medicines_unassigned3 = [
            Medicine(
                compartment_number=1,
                medicine_name=None,
                initial_weight=16.5,
                current_weight=11.2,
                reorder_level=9,
                max_capacity=22,
                expiry_date=date.today() + timedelta(days=160),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_unassigned3.id
            ),
            Medicine(
                compartment_number=2,
                medicine_name=None,
                initial_weight=9.0,
                current_weight=5.5,
                reorder_level=7,
                max_capacity=16,
                expiry_date=date.today() + timedelta(days=140),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_unassigned3.id
            ),
            Medicine(
                compartment_number=3,
                medicine_name=None,
                initial_weight=13.5,
                current_weight=1.8,
                reorder_level=9,
                max_capacity=19,
                expiry_date=date.today() + timedelta(days=80),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_unassigned3.id
            ),
            Medicine(
                compartment_number=4,
                medicine_name=None,
                initial_weight=220.0,
                current_weight=165.0,
                reorder_level=5,
                max_capacity=12,
                expiry_date=date.today() + timedelta(days=280),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_unassigned3.id
            )
        ]

        # Add all medicines to session
        all_medicines = medicines_demo + medicines_health + medicines_tech + medicines_mfg + medicines_healthcare + medicines_unassigned1 + medicines_unassigned2 + medicines_unassigned3
        for medicine in all_medicines:
            db.session.add(medicine)
        
        # Commit all changes
        db.session.commit()
        
        print("Demo data reset completed successfully")
        
        return jsonify({
            "success": True,
            "message": "Demo data reset successfully",
            "reset_at": datetime.utcnow().isoformat(),
            "created": {
                "companies": 5,
                "users": 5,
                "botiquines": 8,
                "medicines": 32
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error resetting demo data: {str(e)}")
        return jsonify({
            "error": f"Failed to reset demo data: {str(e)}"
        }), 500

@bp.get("/demo-status")
def get_demo_status():
    """
    Get current demo data status.
    Only accessible by super admins.
    """
    user = get_current_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    
    if not user.is_super_admin():
        return jsonify({"error": "Access denied. Super admin required."}), 403
    
    try:
        stats = {
            "companies": Company.query.count(),
            "users": User.query.count(),
            "botiquines": Botiquin.query.count(),
            "medicines": Medicine.query.count(),
            "hardware_logs": HardwareLog.query.count()
        }
        
        return jsonify({
            "success": True,
            "stats": stats,
            "checked_at": datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to get demo status: {str(e)}"
        }), 500
