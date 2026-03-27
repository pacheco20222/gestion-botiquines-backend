#!/usr/bin/env python3
"""
Test script to verify PostgreSQL connection using Flask application config.
Run this after updating the .env file with the DATABASE_URL.
"""

from app import create_app

def test_connection():
    """Test connection to PostgreSQL via Flask app configuration"""
    print("🔍 Testing PostgreSQL Connection (via Flask app)...")
    print("-" * 50)
    
    try:
        app = create_app()
        
        with app.app_context():
            from db import db
            from sqlalchemy import text
            
            # Test connection through Flask
            print("Step 1: Connecting to PostgreSQL server...")
            result = db.session.execute(text('SELECT 1'))
            print("✅ Connected to PostgreSQL server successfully!")
            
            # Test database operations
            result = db.session.execute(text('SELECT current_database()'))
            db_name = result.fetchone()
            print(f"✅ Flask app connected to database: {db_name[0]}")
            
        print("\n🎉 All tests passed! Database is ready for use.")
        return True
        
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        print("\n🔧 Troubleshooting steps:")
        print("1. Check PostgreSQL database URL in .env file")
        print("2. Ensure PostgreSQL port 5432 is open")
        print("3. Verify PostgreSQL instance is running")
        print("4. Check if your IP is allowed in security group")
        return False

if __name__ == "__main__":
    test_connection()
