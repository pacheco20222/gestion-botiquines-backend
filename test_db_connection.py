#!/usr/bin/env python3
"""
Test script to verify AWS RDS connection and create botiquines database
Run this after fixing the security group rules
"""

import pymysql
import os
from dotenv import load_dotenv

def test_connection():
    """Test connection to AWS RDS and create botiquines database"""
    
    # Load environment variables
    load_dotenv()
    
    print("🔍 Testing AWS RDS Connection...")
    print(f"Host: pacheco-mysql-aws.cx028yiy8o56.us-east-2.rds.amazonaws.com")
    print(f"Port: 3306")
    print(f"User: bentheblaster")
    print("-" * 50)
    
    try:
        # Step 1: Connect without specifying database
        print("Step 1: Connecting to MySQL server...")
        connection = pymysql.connect(
            host='pacheco-mysql-aws.cx028yiy8o56.us-east-2.rds.amazonaws.com',
            port=3306,
            user='bentheblaster',
            password='Pajarito1234#'
        )
        print("✅ Connected to MySQL server successfully!")
        
        cursor = connection.cursor()
        
        # Step 2: Show existing databases
        print("\nStep 2: Checking existing databases...")
        cursor.execute('SHOW DATABASES')
        databases = cursor.fetchall()
        print(f"Existing databases: {[db[0] for db in databases]}")
        
        # Step 3: Create botiquines database if it doesn't exist
        print("\nStep 3: Creating botiquines database...")
        cursor.execute('CREATE DATABASE IF NOT EXISTS botiquines')
        print("✅ Created botiquines database!")
        
        # Step 4: Switch to botiquines database
        print("\nStep 4: Switching to botiquines database...")
        cursor.execute('USE botiquines')
        print("✅ Switched to botiquines database!")
        
        # Step 5: Verify we're in the right database
        cursor.execute('SELECT DATABASE()')
        current_db = cursor.fetchone()
        print(f"✅ Current database: {current_db[0]}")
        
        # Step 6: Test Flask app connection
        print("\nStep 6: Testing Flask app connection...")
        cursor.close()
        connection.close()
        
        # Now test with Flask app
        from app import create_app
        app = create_app()
        
        with app.app_context():
            from db import db
            from sqlalchemy import text
            
            # Test connection through Flask
            result = db.session.execute(text('SELECT 1'))
            print("✅ Flask app can connect to database!")
            
            # Test database operations
            result = db.session.execute(text('SELECT DATABASE()'))
            db_name = result.fetchone()
            print(f"✅ Flask connected to database: {db_name[0]}")
        
        print("\n🎉 All tests passed! Database is ready for use.")
        return True
        
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        print("\n🔧 Troubleshooting steps:")
        print("1. Check AWS RDS Security Group rules")
        print("2. Ensure MySQL port 3306 is open")
        print("3. Verify RDS instance is running")
        print("4. Check if your IP is allowed in security group")
        return False

if __name__ == "__main__":
    test_connection()
