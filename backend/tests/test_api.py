"""
API endpoint tests.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from io import BytesIO

from app.main import app
from app.models.database import Base
from app.db.session import get_db

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data


def test_image_analysis_endpoint():
    """Test image analysis endpoint with valid image."""
    # Create a simple test image
    from PIL import Image
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    response = client.post(
        "/api/v1/analyze/image",
        files={"file": ("test.png", img_bytes, "image/png")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "risk_score" in data
    assert "prediction" in data
    assert "confidence" in data
    assert "explanation" in data
    assert data["prediction"] in ["Low", "Medium", "High"]
    assert 0 <= data["risk_score"] <= 1
    assert 0 <= data["confidence"] <= 1


def test_invalid_file_upload():
    """Test image endpoint with invalid file type."""
    response = client.post(
        "/api/v1/analyze/image",
        files={"file": ("test.txt", BytesIO(b"not an image"), "text/plain")}
    )
    
    assert response.status_code == 400
    assert "must be an image" in response.json()["detail"]


def test_email_analysis_endpoint():
    """Test email analysis endpoint with high-risk email."""
    email_text = """
    URGENT: Wire Transfer Required
    
    Dear Finance Team,
    
    This is the CEO. I need you to immediately wire $50,000 to the following account.
    This is time sensitive and confidential. Do not contact anyone about this.
    
    Account: 123456789
    """
    
    response = client.post(
        "/api/v1/analyze/email",
        data={"email_text": email_text}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "risk_score" in data
    assert "prediction" in data
    assert "confidence" in data
    assert "explanation" in data
    assert data["prediction"] in ["Low", "Medium", "High"]
    assert 0 <= data["risk_score"] <= 1
    assert 0 <= data["confidence"] <= 1
    # This email should be high risk
    assert data["risk_score"] > 0.5


def test_email_analysis_legitimate():
    """Test email analysis with legitimate email."""
    email_text = """
    Hi Team,
    
    Just wanted to follow up on the quarterly report we discussed in yesterday's meeting.
    Could you please send me the updated figures when you have a chance?
    
    Thanks,
    John
    """
    
    response = client.post(
        "/api/v1/analyze/email",
        data={"email_text": email_text}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["prediction"] in ["Low", "Medium", "High"]
    # This email should be low risk
    assert data["risk_score"] < 0.5


def test_email_analysis_authority_keywords():
    """Test email with authority keywords."""
    email_text = """
    This is the CFO. Please process the invoice payment immediately.
    The CEO has approved this transaction. Wire the funds today.
    """
    
    response = client.post(
        "/api/v1/analyze/email",
        data={"email_text": email_text}
    )
    
    assert response.status_code == 200
    data = response.json()
    # Should detect authority + urgency + financial keywords
    assert data["risk_score"] > 0.4


def test_email_analysis_secrecy_pattern():
    """Test email with secrecy patterns."""
    email_text = """
    Please transfer the funds to the account below.
    This is confidential - do not tell anyone about this transaction.
    Do not contact me about this, just proceed immediately.
    """
    
    response = client.post(
        "/api/v1/analyze/email",
        data={"email_text": email_text}
    )
    
    assert response.status_code == 200
    data = response.json()
    # Should detect secrecy patterns
    assert data["risk_score"] > 0.5


def test_email_analysis_too_short():
    """Test email endpoint with too short text."""
    response = client.post(
        "/api/v1/analyze/email",
        data={"email_text": "Hi"}
    )
    
    assert response.status_code == 400
    assert "too short" in response.json()["detail"]


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
