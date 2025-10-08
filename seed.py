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

        # Additional users will be created after their companies are created
        # (We'll add them later in the seed process)

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
                initial_weight=13.2,  # Full bottle: 24 units × 0.55g
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
                initial_weight=7.2,  # Full bottle: 18 units × 0.40g
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
                initial_weight=6.3,  # Full bottle: 18 units × 0.35g
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
                initial_weight=360.0,  # Full bottle: 6 units × 60g
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
                initial_weight=0.192,  # Full bottle: 16 units × 0.012g
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
                initial_weight=0.5,  # Full bottle: 10 units × 0.05g
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
                initial_weight=0.24,  # Full bottle: 12 units × 0.02g
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
                initial_weight=600.0,  # Full bottle: 6 units × 100g
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
                initial_weight=480.0,  # Full bottle: 4 units × 120g
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
                initial_weight=0.108,  # Full pack: 12 units × 0.009g
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
                initial_weight=0.3,  # Full pack: 12 units × 0.025g
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
                initial_weight=0.4,  # Full pack: 5 units × 0.08g
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

        # 4. TechCorp - Tech company with 2 botiquines
        techcorp_company = Company(
            name="TechCorp Solutions",
            contact_email="admin@techcorp.com",
            contact_phone="+1-555-0101",
            active=True
        )
        db.session.add(techcorp_company)
        db.session.flush()

        # TechCorp Botiquin 1 - Office Floor
        botiquin_techcorp_office = Botiquin(
            hardware_id="BOT_TECHCORP_01",
            name="Botiquín Oficina Principal",
            location="Piso 3 - Oficina Principal",
            total_compartments=4,
            last_sync_at=datetime.utcnow(),
            company=techcorp_company
        )
        db.session.add(botiquin_techcorp_office)
        db.session.flush()

        medicines_techcorp_office = [
            Medicine(
                compartment_number=1,
                trade_name="Paracetamol",
                generic_name="Acetaminophen",
                brand="Tylenol",
                strength="500 mg",
                unit_weight=0.5,
                initial_weight=10.0,  # 20 units × 0.5g
                current_weight=7.5,   # 75% stock
                quantity=15,
                reorder_level=5,
                max_capacity=20,
                expiry_date=date.today() + timedelta(days=120),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_techcorp_office.id
            ),
            Medicine(
                compartment_number=2,
                trade_name="Ibuprofeno",
                generic_name="Ibuprofen",
                brand="Advil",
                strength="400 mg",
                unit_weight=0.4,
                initial_weight=8.0,   # 20 units × 0.4g
                current_weight=2.4,   # 30% stock
                quantity=6,
                reorder_level=5,
                max_capacity=20,
                expiry_date=date.today() + timedelta(days=45),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_techcorp_office.id
            ),
            Medicine(
                compartment_number=3,
                trade_name="Aspirina",
                generic_name="Acetylsalicylic Acid",
                brand="Bayer",
                strength="300 mg",
                unit_weight=0.35,
                initial_weight=7.0,   # 20 units × 0.35g
                current_weight=0.7,   # 10% stock
                quantity=2,
                reorder_level=5,
                max_capacity=20,
                expiry_date=date.today() + timedelta(days=15),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_techcorp_office.id
            ),
            Medicine(
                compartment_number=4,
                trade_name="Gel Antibacterial",
                generic_name="Ethanol",
                brand="PureHands",
                strength="60 ml",
                unit_weight=60.0,
                initial_weight=360.0, # 6 units × 60g
                current_weight=240.0, # 67% stock
                quantity=4,
                reorder_level=2,
                max_capacity=6,
                expiry_date=date.today() + timedelta(days=200),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_techcorp_office.id
            ),
        ]
        db.session.add_all(medicines_techcorp_office)

        # TechCorp Botiquin 2 - Break Room
        botiquin_techcorp_break = Botiquin(
            hardware_id="BOT_TECHCORP_02",
            name="Botiquín Sala de Descanso",
            location="Piso 2 - Sala de Descanso",
            total_compartments=4,
            last_sync_at=datetime.utcnow(),
            company=techcorp_company
        )
        db.session.add(botiquin_techcorp_break)
        db.session.flush()

        medicines_techcorp_break = [
            Medicine(
                compartment_number=1,
                trade_name="Paracetamol",
                generic_name="Acetaminophen",
                brand="Genéricos MX",
                strength="500 mg",
                unit_weight=0.5,
                initial_weight=10.0,  # 20 units × 0.5g
                current_weight=8.0,   # 80% stock
                quantity=16,
                reorder_level=5,
                max_capacity=20,
                expiry_date=date.today() + timedelta(days=90),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_techcorp_break.id
            ),
            Medicine(
                compartment_number=2,
                trade_name="Ibuprofeno",
                generic_name="Ibuprofen",
                brand="Advil",
                strength="400 mg",
                unit_weight=0.4,
                initial_weight=8.0,   # 20 units × 0.4g
                current_weight=6.4,   # 80% stock
                quantity=16,
                reorder_level=5,
                max_capacity=20,
                expiry_date=date.today() + timedelta(days=60),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_techcorp_break.id
            ),
            Medicine(
                compartment_number=3,
                trade_name="Aspirina",
                generic_name="Acetylsalicylic Acid",
                brand="Bayer",
                strength="300 mg",
                unit_weight=0.35,
                initial_weight=7.0,   # 20 units × 0.35g
                current_weight=4.9,   # 70% stock
                quantity=14,
                reorder_level=5,
                max_capacity=20,
                expiry_date=date.today() + timedelta(days=30),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_techcorp_break.id
            ),
            Medicine(
                compartment_number=4,
                trade_name="Gel Antibacterial",
                generic_name="Ethanol",
                brand="PureHands",
                strength="60 ml",
                unit_weight=60.0,
                initial_weight=360.0, # 6 units × 60g
                current_weight=300.0, # 83% stock
                quantity=5,
                reorder_level=2,
                max_capacity=6,
                expiry_date=date.today() + timedelta(days=180),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_techcorp_break.id
            ),
        ]
        db.session.add_all(medicines_techcorp_break)

        # Add TechCorp admin user
        tech_admin = User(
            username="tech_admin",
            email="admin@techcorp.com",
            user_type="company_admin",
            company=techcorp_company
        )
        tech_admin.set_password("techpass123")
        db.session.add(tech_admin)

        # 5. Manufacturing Inc - Manufacturing company
        manufacturing_company = Company(
            name="Manufacturing Inc",
            contact_email="safety@manufacturing.com",
            contact_phone="+1-555-0202",
            active=True
        )
        db.session.add(manufacturing_company)
        db.session.flush()

        botiquin_manufacturing = Botiquin(
            hardware_id="BOT_MFG_01",
            name="Botiquín Planta de Producción",
            location="Planta Principal - Área de Seguridad",
            total_compartments=4,
            last_sync_at=datetime.utcnow(),
            company=manufacturing_company
        )
        db.session.add(botiquin_manufacturing)
        db.session.flush()

        medicines_manufacturing = [
            Medicine(
                compartment_number=1,
                trade_name="Paracetamol",
                generic_name="Acetaminophen",
                brand="Genéricos MX",
                strength="500 mg",
                unit_weight=0.5,
                initial_weight=15.0,  # 30 units × 0.5g
                current_weight=5.0,   # 33% stock
                quantity=10,
                reorder_level=8,
                max_capacity=30,
                expiry_date=date.today() + timedelta(days=150),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_manufacturing.id
            ),
            Medicine(
                compartment_number=2,
                trade_name="Ibuprofeno",
                generic_name="Ibuprofen",
                brand="Advil",
                strength="400 mg",
                unit_weight=0.4,
                initial_weight=12.0,  # 30 units × 0.4g
                current_weight=1.6,   # 13% stock
                quantity=4,
                reorder_level=8,
                max_capacity=30,
                expiry_date=date.today() + timedelta(days=30),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_manufacturing.id
            ),
            Medicine(
                compartment_number=3,
                trade_name="Aspirina",
                generic_name="Acetylsalicylic Acid",
                brand="Bayer",
                strength="300 mg",
                unit_weight=0.35,
                initial_weight=10.5,  # 30 units × 0.35g
                current_weight=0.35,  # 3% stock
                quantity=1,
                reorder_level=8,
                max_capacity=30,
                expiry_date=date.today() + timedelta(days=10),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_manufacturing.id
            ),
            Medicine(
                compartment_number=4,
                trade_name="Gel Antibacterial",
                generic_name="Ethanol",
                brand="PureHands",
                strength="60 ml",
                unit_weight=60.0,
                initial_weight=480.0, # 8 units × 60g
                current_weight=120.0, # 25% stock
                quantity=2,
                reorder_level=3,
                max_capacity=8,
                expiry_date=date.today() + timedelta(days=250),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_manufacturing.id
            ),
        ]
        db.session.add_all(medicines_manufacturing)

        # Add Manufacturing admin user
        mfg_admin = User(
            username="mfg_admin",
            email="safety@manufacturing.com",
            user_type="company_admin",
            company=manufacturing_company
        )
        mfg_admin.set_password("mfgpass123")
        db.session.add(mfg_admin)

        # 6. Healthcare Plus - Healthcare company
        healthcare_company = Company(
            name="Healthcare Plus",
            contact_email="admin@healthcareplus.com",
            contact_phone="+1-555-0303",
            active=True
        )
        db.session.add(healthcare_company)
        db.session.flush()

        botiquin_healthcare = Botiquin(
            hardware_id="BOT_HEALTH_01",
            name="Botiquín Clínica Principal",
            location="Clínica - Recepción",
            total_compartments=4,
            last_sync_at=datetime.utcnow(),
            company=healthcare_company
        )
        db.session.add(botiquin_healthcare)
        db.session.flush()

        medicines_healthcare = [
            Medicine(
                compartment_number=1,
                trade_name="Paracetamol",
                generic_name="Acetaminophen",
                brand="Tylenol",
                strength="500 mg",
                unit_weight=0.5,
                initial_weight=20.0,  # 40 units × 0.5g
                current_weight=18.0,  # 90% stock
                quantity=36,
                reorder_level=10,
                max_capacity=40,
                expiry_date=date.today() + timedelta(days=200),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_healthcare.id
            ),
            Medicine(
                compartment_number=2,
                trade_name="Ibuprofeno",
                generic_name="Ibuprofen",
                brand="Advil",
                strength="400 mg",
                unit_weight=0.4,
                initial_weight=16.0,  # 40 units × 0.4g
                current_weight=14.4,  # 90% stock
                quantity=36,
                reorder_level=10,
                max_capacity=40,
                expiry_date=date.today() + timedelta(days=180),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_healthcare.id
            ),
            Medicine(
                compartment_number=3,
                trade_name="Aspirina",
                generic_name="Acetylsalicylic Acid",
                brand="Bayer",
                strength="300 mg",
                unit_weight=0.35,
                initial_weight=14.0,  # 40 units × 0.35g
                current_weight=12.6,  # 90% stock
                quantity=36,
                reorder_level=10,
                max_capacity=40,
                expiry_date=date.today() + timedelta(days=160),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_healthcare.id
            ),
            Medicine(
                compartment_number=4,
                trade_name="Gel Antibacterial",
                generic_name="Ethanol",
                brand="PureHands",
                strength="60 ml",
                unit_weight=60.0,
                initial_weight=600.0, # 10 units × 60g
                current_weight=540.0, # 90% stock
                quantity=9,
                reorder_level=3,
                max_capacity=10,
                expiry_date=date.today() + timedelta(days=300),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_healthcare.id
            ),
        ]
        db.session.add_all(medicines_healthcare)

        # Add Healthcare Plus admin user
        healthcare_admin = User(
            username="healthcare_admin",
            email="admin@healthcareplus.com",
            user_type="company_admin",
            company=healthcare_company
        )
        healthcare_admin.set_password("healthcarepass123")
        db.session.add(healthcare_admin)

        # 7. Additional unassigned botiquines for testing assignment
        botiquin_unassigned_2 = Botiquin(
            hardware_id="BOT_UNASSIGNED_02",
            name="Botiquín Sin Asignar #2",
            location="Almacén Central",
            total_compartments=4,
            last_sync_at=datetime.utcnow(),
            company_id=None
        )
        db.session.add(botiquin_unassigned_2)
        db.session.flush()

        medicines_unassigned_2 = [
            Medicine(
                compartment_number=1,
                trade_name="Paracetamol",
                generic_name="Acetaminophen",
                brand="Genéricos MX",
                strength="500 mg",
                unit_weight=0.5,
                initial_weight=10.0,  # 20 units × 0.5g
                current_weight=10.0,  # 100% stock (new)
                quantity=20,
                reorder_level=5,
                max_capacity=20,
                expiry_date=date.today() + timedelta(days=365),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_unassigned_2.id
            ),
            Medicine(
                compartment_number=2,
                trade_name="Ibuprofeno",
                generic_name="Ibuprofen",
                brand="Advil",
                strength="400 mg",
                unit_weight=0.4,
                initial_weight=8.0,   # 20 units × 0.4g
                current_weight=8.0,   # 100% stock (new)
                quantity=20,
                reorder_level=5,
                max_capacity=20,
                expiry_date=date.today() + timedelta(days=365),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_unassigned_2.id
            ),
            Medicine(
                compartment_number=3,
                trade_name="Aspirina",
                generic_name="Acetylsalicylic Acid",
                brand="Bayer",
                strength="300 mg",
                unit_weight=0.35,
                initial_weight=7.0,   # 20 units × 0.35g
                current_weight=7.0,   # 100% stock (new)
                quantity=20,
                reorder_level=5,
                max_capacity=20,
                expiry_date=date.today() + timedelta(days=365),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_unassigned_2.id
            ),
            Medicine(
                compartment_number=4,
                trade_name="Gel Antibacterial",
                generic_name="Ethanol",
                brand="PureHands",
                strength="60 ml",
                unit_weight=60.0,
                initial_weight=360.0, # 6 units × 60g
                current_weight=360.0, # 100% stock (new)
                quantity=6,
                reorder_level=2,
                max_capacity=6,
                expiry_date=date.today() + timedelta(days=365),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_unassigned_2.id
            ),
        ]
        db.session.add_all(medicines_unassigned_2)

        botiquin_unassigned_3 = Botiquin(
            hardware_id="BOT_UNASSIGNED_03",
            name="Botiquín Sin Asignar #3",
            location="Almacén Secundario",
            total_compartments=4,
            last_sync_at=datetime.utcnow(),
            company_id=None
        )
        db.session.add(botiquin_unassigned_3)
        db.session.flush()

        medicines_unassigned_3 = [
            Medicine(
                compartment_number=1,
                trade_name="Paracetamol",
                generic_name="Acetaminophen",
                brand="Tylenol",
                strength="500 mg",
                unit_weight=0.5,
                initial_weight=10.0,  # 20 units × 0.5g
                current_weight=5.0,   # 50% stock
                quantity=10,
                reorder_level=5,
                max_capacity=20,
                expiry_date=date.today() + timedelta(days=200),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_unassigned_3.id
            ),
            Medicine(
                compartment_number=2,
                trade_name="Ibuprofeno",
                generic_name="Ibuprofen",
                brand="Advil",
                strength="400 mg",
                unit_weight=0.4,
                initial_weight=8.0,   # 20 units × 0.4g
                current_weight=2.4,   # 30% stock
                quantity=6,
                reorder_level=5,
                max_capacity=20,
                expiry_date=date.today() + timedelta(days=150),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_unassigned_3.id
            ),
            Medicine(
                compartment_number=3,
                trade_name="Aspirina",
                generic_name="Acetylsalicylic Acid",
                brand="Bayer",
                strength="300 mg",
                unit_weight=0.35,
                initial_weight=7.0,   # 20 units × 0.35g
                current_weight=1.4,   # 20% stock
                quantity=4,
                reorder_level=5,
                max_capacity=20,
                expiry_date=date.today() + timedelta(days=100),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_unassigned_3.id
            ),
            Medicine(
                compartment_number=4,
                trade_name="Gel Antibacterial",
                generic_name="Ethanol",
                brand="PureHands",
                strength="60 ml",
                unit_weight=60.0,
                initial_weight=360.0, # 6 units × 60g
                current_weight=180.0, # 50% stock
                quantity=3,
                reorder_level=2,
                max_capacity=6,
                expiry_date=date.today() + timedelta(days=250),
                last_scan_at=datetime.utcnow(),
                botiquin_id=botiquin_unassigned_3.id
            ),
        ]
        db.session.add_all(medicines_unassigned_3)

        db.session.commit()

if __name__ == "__main__":
    init_db()
    print("Database seeded successfully")
