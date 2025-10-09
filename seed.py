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
        superadmin.set_password("admin123")
        db.session.add(superadmin)

        # Seed companies
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

        # Seed company admin users
        demo_admin = User(
            username="demo_admin",
            email="demo_admin@example.com",
            user_type="company_admin",
            company=demo_company
        )
        demo_admin.set_password("password123")
        db.session.add(demo_admin)

        health_admin = User(
            username="health_admin",
            email="health_admin@example.com",
            user_type="company_admin",
            company=health_corp
        )
        health_admin.set_password("healthpass456")
        db.session.add(health_admin)

        tech_admin = User(
            username="tech_admin",
            email="tech_admin@example.com",
            user_type="company_admin",
            company=techcorp
        )
        tech_admin.set_password("techpass123")
        db.session.add(tech_admin)

        mfg_admin = User(
            username="mfg_admin",
            email="mfg_admin@example.com",
            user_type="company_admin",
            company=manufacturing
        )
        mfg_admin.set_password("mfgpass123")
        db.session.add(mfg_admin)

        healthcare_admin = User(
            username="healthcare_admin",
            email="healthcare_admin@example.com",
            user_type="company_admin",
            company=healthcare_plus
        )
        healthcare_admin.set_password("healthcarepass123")
        db.session.add(healthcare_admin)

        # Seed botiquines
        # 1. Demo Company botiquin
        botiquin_demo = Botiquin(
            hardware_id="BOT_DEMO_COMP",
            name="Botiquín Demo Company",
            location="Demo HQ",
            total_compartments=4,
            last_sync_at=datetime.utcnow(),
            company=demo_company
        )
        db.session.add(botiquin_demo)
        db.session.flush()

        # 2. Health Corp botiquin
        botiquin_health = Botiquin(
            hardware_id="BOT_HEALTH_CORP",
            name="Botiquín Health Corp",
            location="Health Corp Main Office",
            total_compartments=4,
            last_sync_at=datetime.utcnow(),
            company=health_corp
        )
        db.session.add(botiquin_health)
        db.session.flush()

        # 3. TechCorp botiquin
        botiquin_tech = Botiquin(
            hardware_id="BOT_TECHCORP",
            name="Botiquín TechCorp",
            location="TechCorp Office",
            total_compartments=4,
            last_sync_at=datetime.utcnow(),
            company=techcorp
        )
        db.session.add(botiquin_tech)
        db.session.flush()

        # 4. Manufacturing botiquin
        botiquin_mfg = Botiquin(
            hardware_id="BOT_MANUFACTURING",
            name="Botiquín Manufacturing",
            location="Manufacturing Plant",
            total_compartments=4,
            last_sync_at=datetime.utcnow(),
            company=manufacturing
        )
        db.session.add(botiquin_mfg)
        db.session.flush()

        # 5. Healthcare Plus botiquin
        botiquin_healthcare = Botiquin(
            hardware_id="BOT_HEALTHCARE_PLUS",
            name="Botiquín Healthcare Plus",
            location="Healthcare Plus Clinic",
            total_compartments=4,
            last_sync_at=datetime.utcnow(),
            company=healthcare_plus
        )
        db.session.add(botiquin_healthcare)
        db.session.flush()

        # 6. Unassigned botiquines (with realistic weight data from hardware)
        botiquin_unassigned1 = Botiquin(
            hardware_id="BOT_UNASSIGNED_1",
            name="Botiquín Unassigned 1",
            location="Warehouse",
            total_compartments=4,
            last_sync_at=datetime.utcnow(),
            company=None
        )
        db.session.add(botiquin_unassigned1)
        db.session.flush()

        botiquin_unassigned2 = Botiquin(
            hardware_id="BOT_UNASSIGNED_2",
            name="Botiquín Unassigned 2",
            location="Storage Room",
            total_compartments=4,
            last_sync_at=datetime.utcnow(),
            company=None
        )
        db.session.add(botiquin_unassigned2)
        db.session.flush()

        botiquin_unassigned3 = Botiquin(
            hardware_id="BOT_UNASSIGNED_3",
            name="Botiquín Unassigned 3",
            location="Distribution Center",
            total_compartments=4,
            last_sync_at=datetime.utcnow(),
            company=None
        )
        db.session.add(botiquin_unassigned3)
        db.session.flush()

        # Seed medicines for Demo Company botiquin
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

        # Seed medicines for Health Corp botiquin
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

        # Seed medicines for TechCorp botiquin
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

        # Seed medicines for unassigned botiquines (with realistic weight data)
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

        # Seed medicines for Manufacturing botiquin
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

        # Seed medicines for Healthcare Plus botiquin
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

        # Add all medicines to session
        for medicine in medicines_demo + medicines_health + medicines_tech + medicines_mfg + medicines_healthcare + medicines_unassigned1 + medicines_unassigned2 + medicines_unassigned3:
            db.session.add(medicine)

        # Commit all changes
        db.session.commit()
        print("✅ Database seeded successfully!")
        print(f"📊 Created:")
        print(f"   - 1 Super Admin user")
        print(f"   - 5 Companies")
        print(f"   - 5 Company Admin users")
        print(f"   - 8 Botiquines (5 assigned, 3 unassigned)")
        print(f"   - 32 Medicines with realistic weight data (ALL botiquines have weight data)")
        print()
        print("🔑 Login Credentials:")
        print("   Super Admin: admin / admin123")
        print("   Demo Company: demo_admin / password123")
        print("   Health Corp: health_admin / healthpass456")
        print("   TechCorp: tech_admin / techpass123")
        print("   Manufacturing: mfg_admin / mfgpass123")
        print("   Healthcare Plus: healthcare_admin / healthcarepass123")

if __name__ == "__main__":
    init_db()