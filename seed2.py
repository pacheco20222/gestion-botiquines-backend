from datetime import datetime, timedelta
from db import db
from models.models import User, Medicine
from app import app

# Run all DB work inside the Flask app context
with app.app_context():
    # Reset schema for a clean seed
    db.drop_all()
    db.create_all()

    # --- Single demo user ---
    demo_user = User(username='demo')
    demo_user.set_password('demo123')  # hashes the password
    db.session.add(demo_user)

    # --- Medicines dataset (realistic mix) ---
    now = datetime.utcnow()
    medicines = [
        Medicine(
            trade_name='Paracetamol 500mg',
            generic_name='Paracetamol',
            brand='Genfar',
            strength='500mg',
            expiry_date=now + timedelta(days=365),
            quantity=30,
            reorder_level=10,
            last_scan_at=now
        ),
        Medicine(
            trade_name='Ibuprofeno 400mg',
            generic_name='Ibuprofeno',
            brand='MK',
            strength='400mg',
            expiry_date=now + timedelta(days=180),
            quantity=25,
            reorder_level=8,
            last_scan_at=now
        ),
        Medicine(
            trade_name='Amoxicilina 500mg',
            generic_name='Amoxicilina',
            brand='Sandoz',
            strength='500mg',
            expiry_date=now + timedelta(days=90),
            quantity=20,
            reorder_level=5,
            last_scan_at=now
        ),
        Medicine(
            trade_name='Omeprazol 20mg',
            generic_name='Omeprazol',
            brand='Pfizer',
            strength='20mg',
            expiry_date=now + timedelta(days=30),
            quantity=15,
            reorder_level=5,
            last_scan_at=now
        ),
        Medicine(
            trade_name='Loratadina 10mg',
            generic_name='Loratadina',
            brand='Bayer',
            strength='10mg',
            expiry_date=now + timedelta(days=10),  # expiring soon
            quantity=12,
            reorder_level=4,
            last_scan_at=now
        ),
        Medicine(
            trade_name='Diclofenaco 50mg',
            generic_name='Diclofenaco',
            brand='Tecnoquímicas',
            strength='50mg',
            expiry_date=now - timedelta(days=5),  # expired
            quantity=8,
            reorder_level=5,
            last_scan_at=now
        ),
        Medicine(
            trade_name='Metformina 850mg',
            generic_name='Metformina',
            brand='Sanofi',
            strength='850mg',
            expiry_date=now + timedelta(days=200),
            quantity=2,  # low stock
            reorder_level=5,
            last_scan_at=now
        ),
        Medicine(
            trade_name='Salbutamol Inhalador',
            generic_name='Salbutamol',
            brand='GlaxoSmithKline',
            strength='100mcg/dosis',
            expiry_date=now + timedelta(days=270),
            quantity=5,
            reorder_level=2,
            last_scan_at=now
        ),
        Medicine(
            trade_name='Aspirina 100mg',
            generic_name='Ácido acetilsalicílico',
            brand='Bayer',
            strength='100mg',
            expiry_date=now + timedelta(days=60),
            quantity=16,
            reorder_level=6,
            last_scan_at=now
        ),
        Medicine(
            trade_name='Lansoprazol 30mg',
            generic_name='Lansoprazol',
            brand='Takeda',
            strength='30mg',
            expiry_date=now + timedelta(days=15),  # expiring soon
            quantity=10,
            reorder_level=3,
            last_scan_at=now
        ),
    ]

    db.session.bulk_save_objects(medicines)
    db.session.commit()

    print("seed2: created 1 demo user and 10 medicines.")
