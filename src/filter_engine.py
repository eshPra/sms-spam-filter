# src/filter_engine.py
import re
import json
import joblib
from pathlib import Path

# Paths
WHITELIST_FILE = Path(__file__).parent.parent / "config" / "whitelist.json"
MODEL_FILE = Path(__file__).parent.parent / "models" / "spam_model.pkl"
VECTORIZER_FILE = Path(__file__).parent.parent / "models" / "vectorizer.pkl"

# Load whitelist
with open(WHITELIST_FILE, 'r') as f:
    WHITELIST = json.load(f)

# ✅ Add SUSPICIOUS DOMAINS list here
SUSPICIOUS_DOMAINS = [
    "fakewebsite.com",
    "login-now-security.xyz",
    "verify-now.online",
    "get-rich-fast.biz",
    "iphone14winner.com",
    "winfreecash.com",
    "urgentupdate.co",
    "secure-update.cards",
    "confirm-payee.click",
    "netflix-support.com"
]

# Load model and vectorizer
MODEL = joblib.load(MODEL_FILE)
VECTORIZER = joblib.load(VECTORIZER_FILE)


def extract_domains(text):
    """Extract domains from URLs in the message."""
    urls = re.findall(r'https?://([^\s/]+)', text)
    return [url.strip('www.') for url in urls]


def is_whitelisted(message):
    """Check if message matches any whitelisted domain or phrase."""
    msg_lower = message.lower()

    # Check phrases
    for phrase in WHITELIST["phrases"]:
        if phrase in msg_lower:
            return True

    # Check domains
    domains = extract_domains(message)
    for domain in domains:
        if any(whitelisted in domain for whitelisted in WHITELIST["domains"]):
            return True

    return False


def classify_with_ai(message):
    """Use trained model to classify message."""
    cleaned = re.sub(r'\s+', ' ', message.lower().strip())
    vec = VECTORIZER.transform([cleaned])
    pred = MODEL.predict(vec)[0]
    proba = MODEL.predict_proba(vec)[0]
    confidence = max(proba)
    return pred, confidence


def filter_message(message):
    """Main filtering logic: whitelist → suspicious domain → AI → verdict"""
    if not message or not message.strip():
        return {"verdict": "blocked", "reason": "empty_message"}

    message = message.strip()

    # ✅ STEP 1: Whitelist Check (trusted messages)
    if is_whitelisted(message):
        return {"verdict": "allowed", "reason": "whitelisted"}

    # ✅ STEP 2: Suspicious Domain Check (block known bad domains)
    domains = extract_domains(message)
    for domain in domains:
        # Check if any suspicious domain is in the URL
        if any(suspicious in domain for suspicious in SUSPICIOUS_DOMAINS):
            return {
                "verdict": "blocked",
                "reason": "suspicious_domain",
                "matched_domain": domain
            }

    # ✅ STEP 3: AI Classification
    category, confidence = classify_with_ai(message)
    confidence = round(confidence, 2)

    if category == "Spam":
        return {
            "verdict": "blocked",
            "reason": "ai",
            "confidence": confidence
        }
    else:
        return {
            "verdict": "allowed",
            "reason": "ai",
            "category": category,
            "confidence": confidence
        }