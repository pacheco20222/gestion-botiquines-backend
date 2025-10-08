# seed.py
from datetime import date, datetime, timedelta

from app import app, db
from models import User, Company, Botiquin, Medicine

def init_db():
    with app.app_context():
        # Drop and recreate all tables
        db.drop_all()
        db.create_all()

        # Seed superadmin user
        superadmin = User(
            username="admin",
            email="admin@example.com",
            user_type="super_admin"
        )
        superadmin.set_password("admin123")  # In production, hash this!
        db.session.add(superadmin)

        # Seed a company
        demo_company = Company(
            name="Demo Company"
        )
        db.session.add(demo_company)

        # Seed a company admin user for demo_company
        demo_admin = User(
            username="demo_admin",
            email="demo_admin@example.com",
            user_type="company_admin",
            company=demo_company
        )
        demo_admin.set_password("password123")
        db.session.add(demo_admin)

        # Seed a second company
        health_corp = Company(
            name="Health Corp"
        )
        db.session.add(health_corp)

        # Seed a company admin user for Health Corp
        health_admin = User(
            username="health_admin",
            email="health_admin@example.com",
            user_type="company_admin",
            company=health_corp
        )
        health_admin.set_password("healthpass456")
        db.session.add(health_admin)

        # Seed botiquines:
        # 1. Assigned to demo_company
        botiquin_demo_company = Botiquin(
            hardware_id="BOT_DEMO_COMP",
            name="Botiquín Demo Company",
            location="Demo HQ",
            total_compartments=4,
            last_sync_at=datetime.utcnow(),
            company=demo_company
        )
        db.session.add(botiquin_demo_company)
        db.session.flush()

        medicines_demo_company = [
            Medicine(
                compartment_number=1,
                trade_name="Paracetamol",
                generic_name="Acetaminophen",
                brand="Genéricos MX",
                strength="500 mg",
                unit_weight=0.55,
                current_weight=9.9,
                quantity=18,
                reorder_level=8,
                max_capacity=24,
                expiry_date=date.today() + timedelta(days=180),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_demo_company.id
            ),
            Medicine(
                compartment_number=2,
                trade_name="Ibuprofeno",
                generic_name="Ibuprofen",
                brand="Advil",
                strength="400 mg",
                unit_weight=0.40,
                current_weight=2.4,
                quantity=6,
                reorder_level=5,
                max_capacity=18,
                expiry_date=date.today() + timedelta(days=60),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_demo_company.id
            ),
            Medicine(
                compartment_number=3,
                trade_name="Aspirina",
                generic_name="Acetylsalicylic Acid",
                brand="Bayer",
                strength="300 mg",
                unit_weight=0.35,
                current_weight=0.35,
                quantity=1,
                reorder_level=6,
                max_capacity=18,
                expiry_date=date.today() - timedelta(days=5),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_demo_company.id
            ),
            Medicine(
                compartment_number=4,
                trade_name="Gel Antibacterial",
                generic_name="Ethanol",
                brand="PureHands",
                strength="60 ml",
                unit_weight=60.0,
                current_weight=180.0,
                quantity=3,
                reorder_level=2,
                max_capacity=6,
                expiry_date=date.today() + timedelta(days=365),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_demo_company.id
            ),
        ]
        db.session.add_all(medicines_demo_company)

        # 2. Assigned to Health Corp
        botiquin_health_corp = Botiquin(
            hardware_id="BOT_HEALTH_CORP",
            name="Botiquín Health Corp",
            location="Health Corp Clinic",
            total_compartments=4,
            last_sync_at=datetime.utcnow(),
            company=health_corp
        )
        db.session.add(botiquin_health_corp)
        db.session.flush()

        medicines_health_corp = [
            Medicine(
                compartment_number=1,
                trade_name="Loratadina",
                generic_name="Loratadine",
                brand="Claritin",
                strength="10 mg",
                unit_weight=0.012,
                current_weight=0.144,
                quantity=12,
                reorder_level=4,
                max_capacity=16,
                expiry_date=date.today() + timedelta(days=210),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_health_corp.id
            ),
            Medicine(
                compartment_number=2,
                trade_name="Diclofenaco",
                generic_name="Diclofenac",
                brand="Voltaren",
                strength="50 mg",
                unit_weight=0.05,
                current_weight=0.2,
                quantity=4,
                reorder_level=3,
                max_capacity=10,
                expiry_date=date.today() + timedelta(days=20),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_health_corp.id
            ),
            Medicine(
                compartment_number=3,
                trade_name="Omeprazol",
                generic_name="Omeprazole",
                brand="Prilosec",
                strength="20 mg",
                unit_weight=0.02,
                current_weight=0.06,
                quantity=3,
                reorder_level=4,
                max_capacity=12,
                expiry_date=date.today() + timedelta(days=6),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_health_corp.id
            ),
            Medicine(
                compartment_number=4,
                trade_name="Solución Salina",
                generic_name="Sodium Chloride",
                brand="Salimed",
                strength="100 ml",
                unit_weight=100.0,
                current_weight=300.0,
                quantity=3,
                reorder_level=2,
                max_capacity=6,
                expiry_date=date.today() + timedelta(days=120),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_health_corp.id
            ),
        ]
        db.session.add_all(medicines_health_corp)

        # 3. Unassigned botiquin (company_id=None) - still stocked with medicines
        botiquin_unassigned = Botiquin(
            hardware_id="BOT_UNASSIGNED",
            name="Botiquín Unassigned",
            location="Warehouse",
            total_compartments=4,
            last_sync_at=datetime.utcnow(),
            company_id=None
        )
        db.session.add(botiquin_unassigned)
        db.session.flush()

        medicines_unassigned = [
            Medicine(
                compartment_number=1,
                trade_name="Clorhexidina",
                generic_name="Chlorhexidine",
                brand="DermaClean",
                strength="120 ml",
                unit_weight=120.0,
                current_weight=240.0,
                quantity=2,
                reorder_level=1,
                max_capacity=4,
                expiry_date=date.today() + timedelta(days=300),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_unassigned.id
            ),
            Medicine(
                compartment_number=2,
                trade_name="Gasas Esterilizadas",
                generic_name="Sterile Gauze",
                brand="MediPack",
                strength="10 unidades",
                unit_weight=0.009,
                current_weight=0.045,
                quantity=5,
                reorder_level=4,
                max_capacity=12,
                expiry_date=date.today() + timedelta(days=150),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_unassigned.id
            ),
            Medicine(
                compartment_number=3,
                trade_name="Guantes Nitrilo",
                generic_name="Nitrile Gloves",
                brand="SafeHands",
                strength="Par",
                unit_weight=0.025,
                current_weight=0.075,
                quantity=3,
                reorder_level=6,
                max_capacity=12,
                expiry_date=None,
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_unassigned.id
            ),
            Medicine(
                compartment_number=4,
                trade_name="Vendaje Elástico",
                generic_name="Elastic Bandage",
                brand="FlexWrap",
                strength="5 cm x 4 m",
                unit_weight=0.08,
                current_weight=0.16,
                quantity=2,
                reorder_level=2,
                max_capacity=5,
                expiry_date=date.today() + timedelta(days=540),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_unassigned.id
            ),
        ]
        db.session.add_all(medicines_unassigned)

        db.session.commit()

if __name__ == "__main__":
    init_db()
    print("Database seeded successfully")
