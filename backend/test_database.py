"""
Quick test to verify SQLite database setup.
Run this to confirm database is working.
"""
from app.db.session import engine, SessionLocal
from app.models.database import Base, FraudLog
from datetime import datetime

def test_database():
    print("=" * 60)
    print("Testing SQLite Database Setup")
    print("=" * 60)
    
    # Create tables
    print("\n1. Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("   ✅ Tables created successfully")
    
    # Test connection
    print("\n2. Testing database connection...")
    db = SessionLocal()
    try:
        # Insert test record
        test_log = FraudLog(
            input_type="test",
            risk_score=0.5,
            prediction="Medium",
            confidence=0.85
        )
        db.add(test_log)
        db.commit()
        print("   ✅ Test record inserted")
        
        # Query test record
        count = db.query(FraudLog).count()
        print(f"   ✅ Database query successful - {count} record(s) found")
        
        # Clean up test record
        db.delete(test_log)
        db.commit()
        print("   ✅ Test record deleted")
        
    finally:
        db.close()
    
    print("\n" + "=" * 60)
    print("✅ DATABASE SETUP COMPLETE!")
    print("=" * 60)
    print("\nDatabase file: ./fraudguard.db")
    print("Status: Ready to use")
    print("\nYou can now start the backend server:")
    print("  python -m uvicorn app.main:app --reload")
    print("=" * 60)

if __name__ == "__main__":
    test_database()
