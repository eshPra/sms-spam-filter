# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
from datetime import datetime
import sys
from pathlib import Path

# Add src to path so we can import filter_engine
sys.path.append(str(Path(__file__).parent / "src"))

# Import filtering logic
from filter_engine import filter_message

# ================================
# Logging Setup
# ================================

# Ensure logs directory exists
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("SMSFilter")

# ================================
# FastAPI App
# ================================

app = FastAPI(
    title="SMS Spam Filter API",
    description="A lightweight AI-powered filter to detect spam in business SMS messages",
    version="1.0.0"
)

# ================================
# Request Model
# ================================

class SMSCheckRequest(BaseModel):
    message: str

# ================================
# Health Check Endpoint
# ================================

@app.get("/")
def health_check():
    return {
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "model_loaded": True
    }

# ================================
# Main Filtering Endpoint
# ================================

@app.post("/check_sms")
def check_sms(request: SMSCheckRequest):
    """
    Endpoint to check if an SMS should be allowed or blocked.
    
    Input: {"message": "Your OTP is 123..."}
    Output: {"verdict": "allowed", "reason": "whitelisted"} OR
            {"verdict": "blocked", "reason": "ai"}
    """
    msg = request.message.strip()
    
    # Validate input
    if not msg:
        logger.warning("Blocked: Empty message received")
        raise HTTPException(status_code=400, detail="Empty message")
    
    if len(msg) > 1000:
        logger.warning(f"Blocked: Message too long ({len(msg)} chars)")
        raise HTTPException(status_code=400, detail="Message too long")

    # Run the filter (whitelist → AI)
    result = filter_message(msg)
    
    # Log the decision
    logger.info(f"{result['verdict'].upper()} | '{msg[:100]}...' | {result['reason']}")
    
    return result

# ================================
# Optional: View Logs
# ================================

@app.get("/logs")
def get_logs():
    try:
        with open("logs/app.log", "r") as f:
            logs = f.readlines()
        return {"logs": [log.strip() for log in logs[-50:]]}  # Last 50 lines
    except Exception as e:
        return {"error": str(e)}