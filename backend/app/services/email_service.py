"""
C-suite impersonation and Business Email Compromise (BEC) detection service.
Uses hybrid NLP + rule-based approach with HARD GATING for BEC patterns.
Integrates FinBERT (ProsusAI/finbert) for financial text analysis.
"""
import re
import torch
from typing import Tuple, Dict, Optional
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from app.core.logging import get_logger

logger = get_logger(__name__)


# ========================================
# BUSINESS EMAIL COMPROMISE (BEC) PATTERNS
# ========================================
# High-risk payment/banking intent keywords
HIGH_RISK_PATTERNS = [
    "update bank",
    "updated banking",
    "new account",
    "change payment",
    "wire transfer",
    "process payment",
    "urgent transfer",
    "gift cards",
    "confidential payment",
    "keep this confidential",
    "cannot take calls",
    "unavailable on phone",
    "confirm once done",
    "update account",
    "change account",
    "new banking details",
    "revised payment",
    "payment details changed",
]

# Payment action signals (specific transaction requests)
PAYMENT_ACTIONS = [
    "transfer payment",
    "process payment",
    "clear invoice",
    "vendor payment",
    "settlement",
    "wire",
    "bank details",
    "payment today",
    "outstanding invoice",
    "make payment",
    "send payment",
    "approve payment",
    "release funds",
]

# Authority impersonation signals
AUTHORITY_TERMS = [
    "ceo",
    "cfo",
    "director",
    "executive",
    "board",
    "finance office",
    "management",
    "president",
    "chairman",
    "chief",
    "vp",
    "vice president",
]

# Business pressure indicators
PRESSURE_TERMS = [
    "priority",
    "do not delay",
    "today",
    "asap",
    "impacts approval",
    "contract approval",
    "time sensitive",
    "deadline",
    "critical",
    "immediately",
    "right away",
    "urgent",
]


class EmailService:
    """
    Service for detecting C-suite impersonation in emails.
    Uses hybrid approach: 60% FinBERT NLP + 40% rule-based scoring.
    """
    
    # Rule-based detection patterns
    URGENCY_KEYWORDS = [
        "urgent", "immediately", "asap", "right away", "time sensitive",
        "deadline", "critical", "emergency", "priority", "now", "today"
    ]
    
    FINANCIAL_KEYWORDS = [
        "wire transfer", "payment", "invoice", "bank account", "transaction",
        "funds", "money", "transfer", "pay", "account number", "routing number",
        "wire", "beneficiary", "swift", "iban"
    ]
    
    AUTHORITY_KEYWORDS = [
        "ceo", "cfo", "cto", "president", "director", "executive",
        "chairman", "chief", "vp", "vice president", "managing director",
        "founder", "owner"
    ]
    
    SECRECY_KEYWORDS = [
        "confidential", "secret", "private", "do not tell", "don't tell",
        "do not contact", "don't contact", "do not inform", "don't inform",
        "keep this between us", "off the record"
    ]
    
    def __init__(self):
        """Initialize email service with FinBERT model (singleton pattern)."""
        self.model: Optional[AutoModelForSequenceClassification] = None
        self.tokenizer: Optional[AutoTokenizer] = None
        self.device = torch.device("cpu")  # Production: CPU-only
        self._load_model()
        logger.info("Email service initialized with FinBERT")
    
    def _load_model(self) -> None:
        """Load FinBERT model once at startup."""
        try:
            model_name = "ProsusAI/finbert"
            logger.info(f"Loading FinBERT model: {model_name}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            self.model.to(self.device)
            self.model.eval()  # Set to evaluation mode
            
            logger.info("FinBERT model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load FinBERT model: {e}")
            logger.warning("Falling back to rule-based detection only")
            self.model = None
            self.tokenizer = None
    
    def _calculate_rule_score(self, text: str) -> float:
        """
        Calculate risk score based on BEC-focused rule patterns.
        
        ENHANCED SCORING LOGIC:
        - Payment actions: 0.35 (specific transaction requests)
        - Authority impersonation: 0.30 (executive terms)
        - Business pressure: 0.25 (urgency/deadline indicators)
        - COMBO BONUS: Payment + Authority = +0.30 (strong BEC signal)
        - EXECUTIVE SIGNATURE: CEO/CFO mention = +0.25 (very high risk)
        
        Returns:
            float: Risk score between 0.0 and 1.0
        """
        text_lower = text.lower()
        score = 0.0
        
        # Check for pattern categories
        payment_hit = any(p in text_lower for p in PAYMENT_ACTIONS)
        authority_hit = any(a in text_lower for a in AUTHORITY_TERMS)
        pressure_hit = any(p in text_lower for p in PRESSURE_TERMS)
        
        # Also check HIGH_RISK_PATTERNS for additional payment indicators
        high_risk_hit = any(h in text_lower for h in HIGH_RISK_PATTERNS)
        if high_risk_hit and not payment_hit:
            payment_hit = True  # Treat HIGH_RISK_PATTERNS as payment indicators
        
        # Base scoring
        if payment_hit:
            score += 0.35
            logger.debug("Payment action detected (+0.35)")
        
        if authority_hit:
            score += 0.30
            logger.debug("Authority term detected (+0.30)")
        
        if pressure_hit:
            score += 0.25
            logger.debug("Business pressure detected (+0.25)")
        
        # STRONG BEC SIGNAL: Payment + Authority combination
        # This is the classic BEC pattern (executive requesting payment)
        if payment_hit and authority_hit:
            score += 0.30
            logger.warning("🚨 STRONG BEC SIGNAL: Payment + Authority combination (+0.30)")
        
        # EXECUTIVE SIGNATURE: Specific CEO/CFO mention
        # These are the most commonly impersonated roles
        if "cfo" in text_lower or "ceo" in text_lower:
            score += 0.25
            logger.warning("🚨 Executive signature detected: CEO/CFO (+0.25)")
        
        # Secrecy/confidentiality indicators
        if "confidential" in text_lower or "discreet" in text_lower or "keep this" in text_lower:
            score += 0.15
            logger.debug("Secrecy indicator detected (+0.15)")
        
        # Unavailability excuse (common BEC tactic)
        if "cannot take calls" in text_lower or "unavailable on phone" in text_lower or "out of office" in text_lower:
            score += 0.15
            logger.debug("Unavailability excuse detected (+0.15)")
        
        # Suspicious command patterns
        if re.search(r'\b(do not|don\'t)\s+(tell|inform|contact|discuss|mention)', text_lower):
            score += 0.15
            logger.debug("Suspicious command pattern detected (+0.15)")
        
        final_score = min(score, 1.0)
        
        logger.info(
            f"Rule scoring - Payment: {payment_hit}, Authority: {authority_hit}, "
            f"Pressure: {pressure_hit}, Total: {final_score:.3f}"
        )
        
        return final_score
    
    def _calculate_model_score(self, text: str) -> Tuple[float, float]:
        """
        Calculate risk score using FinBERT model.
        
        Args:
            text: Email text to analyze
            
        Returns:
            Tuple of (risk_score, confidence)
        """
        if self.model is None or self.tokenizer is None:
            logger.warning("FinBERT model not available, using fallback score")
            return 0.35, 0.70
        
        try:
            # Tokenize input text
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Run inference (no gradient computation for production)
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                
                # Apply softmax to get probabilities
                probabilities = torch.nn.functional.softmax(logits, dim=-1)
                
                # FinBERT outputs: [negative, neutral, positive]
                # For fraud detection, we interpret:
                # - High negative sentiment = potential fraud (urgent/threatening)
                # - High positive sentiment = potential manipulation (overly friendly)
                # - Neutral = likely legitimate
                
                negative_prob = probabilities[0][0].item()
                neutral_prob = probabilities[0][1].item()
                positive_prob = probabilities[0][2].item()
                
                # Calculate risk score
                # High negative (urgent/threatening) is strong fraud indicator
                # High positive (overly friendly) is moderate fraud indicator
                # Neutral is low risk
                risk_score = (negative_prob * 1.0) + (positive_prob * 0.5)
                
                # Confidence is based on how decisive the prediction is
                confidence = max(probabilities[0]).item()
                
                logger.debug(f"FinBERT scores - neg: {negative_prob:.3f}, neu: {neutral_prob:.3f}, pos: {positive_prob:.3f}")
                logger.debug(f"Calculated risk_score: {risk_score:.3f}")
                
                return risk_score, confidence
                
        except Exception as e:
            logger.error(f"Error in FinBERT inference: {e}")
            return 0.35, 0.70
    
    def analyze_email(self, email_text: str) -> Tuple[float, float, Dict[str, float]]:
        """
        Analyze email for C-suite impersonation and BEC using hybrid approach.
        
        ENHANCED WITH HARD BEC GATING:
        - If rule_score > 0.55 → IMMEDIATE HIGH RISK (88%)
        - Otherwise: 70% rules + 30% model (rules dominate)
        
        Args:
            email_text: Email content to analyze
            
        Returns:
            Tuple of (final_risk_score, confidence, score_breakdown)
            
        Risk Thresholds:
            < 0.30: Low risk
            0.30 - 0.70: Medium risk
            > 0.70: High risk
        """
        logger.info("=== EMAIL ANALYSIS START (WITH BEC DETECTION) ===")
        
        try:
            # STEP 1: Calculate rule-based score
            rule_score = self._calculate_rule_score(email_text)
            logger.info(f"Rule-based score: {rule_score:.3f}")
            
            # ========================================
            # HARD BEC OVERRIDE (CRITICAL)
            # ========================================
            # If strong BEC pattern detected, immediately return HIGH RISK
            # LOWERED THRESHOLD: 0.60 (was 0.55) for more precision
            # Do NOT let model score dilute the risk
            
            if rule_score >= 0.60:
                logger.warning("🚨 BUSINESS EMAIL COMPROMISE DETECTED - HARD OVERRIDE ACTIVATED")
                logger.warning(f"   Rule score: {rule_score:.3f} (threshold: 0.60)")
                logger.warning("   Bypassing model weighting - returning HIGH RISK")
                
                score_breakdown = {
                    "rule_score": rule_score,
                    "model_score": None,  # Model not used in override
                    "final_score": 0.88,
                    "bec_override": True
                }
                
                logger.info("=== EMAIL ANALYSIS COMPLETE (BEC OVERRIDE) ===")
                
                return 0.88, 0.91, score_breakdown
            
            # STEP 2: If no BEC override, get model score
            logger.info("No BEC override - proceeding with model inference...")
            model_score, model_confidence = self._calculate_model_score(email_text)
            logger.info(f"FinBERT model score: {model_score:.3f}, confidence: {model_confidence:.3f}")
            
            # STEP 3: Combine scores with RULE DOMINANCE (70% rules, 30% model)
            # Rules must dominate for fraud detection
            final_score = (0.70 * rule_score) + (0.30 * model_score)
            
            # Boost if both indicators agree on high risk
            if rule_score > 0.4 and model_score > 0.4:
                final_score = min(final_score * 1.15, 1.0)  # 15% boost
                logger.info(f"Both indicators agree on risk - boosted to {final_score:.3f}")
            
            score_breakdown = {
                "rule_score": rule_score,
                "model_score": model_score,
                "final_score": final_score,
                "bec_override": False
            }
            
            logger.info(
                f"Score fusion - Rule: {rule_score:.3f} (70%), "
                f"Model: {model_score:.3f} (30%), "
                f"Final: {final_score:.3f}, "
                f"Confidence: {model_confidence:.3f}"
            )
            logger.info("=== EMAIL ANALYSIS COMPLETE ===")
            
            return final_score, model_confidence, score_breakdown
            
        except Exception as e:
            logger.error(f"Error analyzing email: {e}")
            logger.exception("Full traceback:")
            raise


# Singleton instance
email_service = EmailService()
