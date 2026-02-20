"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal


class AnalysisResponse(BaseModel):
    """Standard response schema for all analysis endpoints."""
    
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Risk score between 0 and 1")
    prediction: Literal["Low", "Medium", "High"] = Field(..., description="Risk level classification")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model confidence score")
    explanation: str = Field(..., description="Human-readable explanation of the prediction")


class HealthResponse(BaseModel):
    """Health check response schema."""
    
    status: str
    version: str
    timestamp: datetime
