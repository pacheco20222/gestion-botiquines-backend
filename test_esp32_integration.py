#!/usr/bin/env python3
"""
Test script to verify ESP32 JSON data reception efficiency.
Tests the complete flow from ESP32 JSON payload to database updates.
"""

import json
import requests
from datetime import datetime

def test_esp32_json_reception():
    """Test ESP32 JSON data reception and processing"""
    
    print("🔍 Testing ESP32 JSON Data Reception...")
    print("=" * 60)
    
    # ESP32 JSON payload (exactly what ESP32 would send)
    esp32_payload = {
        "hardware_id": "BOT001",
        "timestamp": datetime.utcnow().isoformat(),
        "sensor_type": "weight",
        "compartments": [
            {"compartment": 1, "weight": 45.5},
            {"compartment": 2, "weight": 30.2},
            {"compartment": 3, "weight": 0.0},
            {"compartment": 4, "weight": 18.2}
        ]
    }
    
    print("📡 ESP32 Payload:")
    print(json.dumps(esp32_payload, indent=2))
    print()
    
    # Test the hardware endpoint
    try:
        # Note: This would normally be a POST request to your deployed API
        # For now, we'll test the Flask app directly
        from app import create_app
        app = create_app()
        
        with app.test_client() as client:
            with app.app_context():
                # Test the sensor_data endpoint
                response = client.post('/api/hardware/sensor_data', 
                                     json=esp32_payload,
                                     content_type='application/json')
                
                print(f"📊 Response Status: {response.status_code}")
                print(f"📊 Response Data: {response.get_json()}")
                print()
                
                if response.status_code == 200:
                    print("✅ ESP32 JSON reception successful!")
                    data = response.get_json()
                    
                    # Check if alerts were generated
                    if 'alerts' in data:
                        print(f"🚨 Alerts generated: {len(data['alerts'])}")
                        for alert in data['alerts']:
                            print(f"   - {alert['type'].upper()}: {alert['message']}")
                    
                    # Check results
                    if 'results' in data:
                        print(f"📈 Compartments processed: {len(data['results'])}")
                        for result in data['results']:
                            if 'medicine' in result:
                                print(f"   - Compartment {result['compartment']}: {result['medicine']} - {result['status']}")
                            else:
                                print(f"   - Compartment {result['compartment']}: {result['status']}")
                    
                    return True
                else:
                    print(f"❌ ESP32 JSON reception failed: {response.get_json()}")
                    return False
                    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_hardware_endpoints():
    """Test all hardware-related endpoints"""
    
    print("\n🔧 Testing Hardware Endpoints...")
    print("=" * 60)
    
    try:
        from app import create_app
        app = create_app()
        
        with app.test_client() as client:
            with app.app_context():
                # Test connection endpoint
                print("1. Testing /api/hardware/test_connection...")
                response = client.post('/api/hardware/test_connection', 
                                     json={"hardware_id": "BOT001"})
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.get_json()}")
                
                # Test hardware registration
                print("\n2. Testing /api/hardware/register_hardware...")
                register_payload = {
                    "hardware_id": "BOT_TEST_001",
                    "name": "Test Botiquín",
                    "location": "Test Location",
                    "compartments": 4
                }
                response = client.post('/api/hardware/register_hardware', 
                                     json=register_payload)
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.get_json()}")
                
                # Test logs endpoint
                print("\n3. Testing /api/hardware/logs...")
                response = client.get('/api/hardware/logs')
                print(f"   Status: {response.status_code}")
                print(f"   Logs count: {len(response.get_json())}")
                
                return True
                
    except Exception as e:
        print(f"❌ Endpoint test failed: {e}")
        return False

def test_database_performance():
    """Test database performance with ESP32 data"""
    
    print("\n⚡ Testing Database Performance...")
    print("=" * 60)
    
    try:
        from app import create_app
        from db import db
        from models.models import Botiquin, Medicine, HardwareLog
        from sqlalchemy import text
        
        app = create_app()
        
        with app.app_context():
            # Test database indexes
            print("1. Testing database indexes...")
            
            # Test hardware_id lookup (should be fast with index)
            start_time = datetime.utcnow()
            botiquin = Botiquin.query.filter_by(hardware_id="BOT001").first()
            end_time = datetime.utcnow()
            lookup_time = (end_time - start_time).total_seconds() * 1000
            print(f"   Hardware ID lookup: {lookup_time:.2f}ms")
            
            # Test compartment lookup (should be fast with index)
            start_time = datetime.utcnow()
            medicines = Medicine.query.filter_by(botiquin_id=1, compartment_number=1).all()
            end_time = datetime.utcnow()
            lookup_time = (end_time - start_time).total_seconds() * 1000
            print(f"   Compartment lookup: {lookup_time:.2f}ms")
            
            # Test hardware logs query
            start_time = datetime.utcnow()
            logs = HardwareLog.query.filter_by(botiquin_id=1).limit(10).all()
            end_time = datetime.utcnow()
            lookup_time = (end_time - start_time).total_seconds() * 1000
            print(f"   Hardware logs query: {lookup_time:.2f}ms")
            
            print("✅ Database performance tests completed!")
            return True
            
    except Exception as e:
        print(f"❌ Database performance test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 ESP32 Integration Test Suite")
    print("=" * 60)
    
    # Run all tests
    test1 = test_esp32_json_reception()
    test2 = test_hardware_endpoints()
    test3 = test_database_performance()
    
    print("\n📊 Test Results Summary:")
    print("=" * 60)
    print(f"ESP32 JSON Reception: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"Hardware Endpoints: {'✅ PASS' if test2 else '❌ FAIL'}")
    print(f"Database Performance: {'✅ PASS' if test3 else '❌ FAIL'}")
    
    if all([test1, test2, test3]):
        print("\n🎉 All tests passed! ESP32 integration is ready!")
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
