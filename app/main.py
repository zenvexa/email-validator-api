"""
Professional Email Verification API
Simple, Fast & Accurate
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import re
from typing import Dict, List, Optional

app = FastAPI(
    title="Email Verification API",
    description="Professional email validation service",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Security - Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Professional disposable domains list
DISPOSABLE_DOMAINS = {
    "tempmail.com", "mailinator.com", "yopmail.com",
    "10minutemail.com", "guerrillamail.com", "trashmail.com",
    "fakeinbox.com", "throwawaymail.com", "getairmail.com",
    "sharklasers.com", "guerrillamail.info", "dispostable.com"
}

def validate_email_format(email: str) -> bool:
    """Validate email format professionally"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def is_disposable_domain(domain: str) -> bool:
    """Check if domain is disposable"""
    return domain.lower() in DISPOSABLE_DOMAINS

def get_email_score(email: str, valid: bool, disposable: bool) -> int:
    """Calculate email quality score (0-100)"""
    if not valid:
        return 0
    if disposable:
        return 30
    return 100

@app.get("/", tags=["Root"])
def root() -> Dict:
    """API Home - Information endpoint"""
    return {
        "api": "Email Verification API",
        "version": "2.0.0",
        "status": "active",
        "endpoints": {
            "/verify": "GET - Verify single email",
            "/batch": "POST - Verify multiple emails",
            "/health": "GET - Health check",
            "/stats": "GET - API statistics"
        }
    }

@app.get("/verify", tags=["Verification"])
def verify_email(
    email: str = Query(..., description="Email address to verify")
) -> Dict:
    """
    Verify a single email address
    
    - **Email Format Validation**
    - **Disposable Domain Detection**
    - **Quality Score Calculation**
    """
    if not email:
        raise HTTPException(
            status_code=400,
            detail="Email parameter is required"
        )
    
    # Basic validation
    if len(email) > 254:
        return {
            "email": email,
            "valid_format": False,
            "disposable": False,
            "score": 0,
            "error": "Email too long"
        }
    
    # Format validation
    valid_format = validate_email_format(email)
    
    # Domain analysis
    disposable = False
    domain = None
    
    if valid_format:
        domain = email.split('@')[1].lower()
        disposable = is_disposable_domain(domain)
    
    # Calculate score
    score = get_email_score(email, valid_format, disposable)
    
    # Prepare response
    response = {
        "email": email,
        "valid_format": valid_format,
        "disposable": disposable,
        "score": score,
        "timestamp": "auto_generated"
    }
    
    if domain:
        response["domain"] = domain
    
    return response

@app.get("/health", tags=["Health"])
def health_check() -> Dict:
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "email-verification-api",
        "uptime": "100%"
    }

@app.get("/stats", tags=["Statistics"])
def get_stats() -> Dict:
    """Get API statistics"""
    return {
        "total_disposable_domains": len(DISPOSABLE_DOMAINS),
        "api_version": "2.0.0",
        "features": ["format_check", "disposable_check", "scoring"],
        "rate_limit": "unlimited"
    }

@app.post("/batch", tags=["Batch Processing"])
def batch_verify(emails: List[str]) -> Dict:
    """
    Verify multiple emails at once
    
    - Accepts list of emails
    - Returns individual results
    - Suitable for bulk processing
    """
    if not emails:
        raise HTTPException(
            status_code=400,
            detail="Email list cannot be empty"
        )
    
    results = []
    for email in emails:
        try:
            valid_format = validate_email_format(email)
            disposable = False
            domain = None
            
            if valid_format:
                domain = email.split('@')[1].lower()
                disposable = is_disposable_domain(domain)
            
            score = get_email_score(email, valid_format, disposable)
            
            results.append({
                "email": email,
                "valid_format": valid_format,
                "disposable": disposable,
                "score": score,
                "domain": domain if domain else None
            })
        except Exception:
            results.append({
                "email": email,
                "valid_format": False,
                "disposable": False,
                "score": 0,
                "error": "Processing error"
            })
    
    return {
        "total_emails": len(emails),
        "processed": len(results),
        "results": results
    }

@app.get("/domains/list", tags=["Domains"])
def list_disposable_domains() -> Dict:
    """List all disposable domains detected by API"""
    return {
        "count": len(DISPOSABLE_DOMAINS),
        "domains": sorted(list(DISPOSABLE_DOMAINS))
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "error": True,
        "message": exc.detail,
        "status_code": exc.status_code
    }

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
)
