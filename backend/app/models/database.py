"""
SQLAlchemy database models.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class FraudLog(Base):
    """Model for storing fraud detection analysis logs."""
    
    __tablename__ = "fraud_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    input_type = Column(String, nullable=False, index=True)
    risk_score = Column(Float, nullable=False)
    prediction = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self) -> str:
        return f"<FraudLog(id={self.id}, type={self.input_type}, risk={self.risk_score})>"
