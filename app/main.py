from flask import Flask, request, jsonify
import re
from datetime import datetime

app = Flask(__name__)

DISPOSABLE_DOMAINS = {
    "tempmail.com", "mailinator.com", "yopmail.com",
    "10minutemail.com", "guerrillamail.com", "trashmail.com",
    "fakeinbox.com", "throwawaymail.com", "getairmail.com",
    "sharklasers.com", "guerrillamail.info", "dispostable.com",
    "temp-mail.org", "throwawaymail.com", "mailnesia.com"
}

def validate_email_format(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def is_disposable_domain(domain):
    return domain.lower() in DISPOSABLE_DOMAINS

def calculate_email_score(email, valid, disposable):
    if not valid:
        return 0
    if disposable:
        return 30
    popular_domains = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com"}
    domain = email.split('@')[1].lower()
    if domain in popular_domains:
        return 95
    return 85

@app.route('/')
def home():
    return jsonify({
        "api": "Professional Email Validation API",
        "version": "2.0.0",
        "status": "active",
        "documentation": {
            "endpoints": {
                "/verify?email=test@example.com": "Single email validation",
                "/batch (POST)": "Bulk email validation",
                "/health": "API health check",
                "/stats": "API statistics",
                "/domains": "List disposable domains"
            }
        },
        "pricing": {
            "free": "100 requests/day",
            "basic": "$9.99/month - 10,000 requests",
            "pro": "$29.99/month - 50,000 requests",
            "enterprise": "Custom pricing"
        },
        "support": "contact@example.com"
    })

@app.route('/verify')
def verify_email():
    email = request.args.get('email', '').strip()
    if not email:
        return jsonify({"error": "Email parameter is required"}), 400
    if len(email) > 254:
        return jsonify({
            "email": email,
            "valid_format": False,
            "disposable": False,
            "score": 0,
            "message": "Email too long (max 254 characters)"
        })
    valid_format = validate_email_format(email)
    if not valid_format:
        return jsonify({
            "email": email,
            "valid_format": False,
            "disposable": False,
            "score": 0,
            "message": "Invalid email format"
        })
    domain = email.split('@')[1].lower()
    disposable = is_disposable_domain(domain)
    score = calculate_email_score(email, valid_format, disposable)
    response = {
        "email": email,
        "valid_format": True,
        "disposable": disposable,
        "domain": domain,
        "score": score,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "suggestions": []
    }
    if disposable:
        response["suggestions"].append("Use a professional email provider (Gmail, Outlook, etc.)")
    if score < 50:
        response["suggestions"].append("Consider using a more reputable email domain")
    return jsonify(response)

@app.route('/batch', methods=['POST'])
def batch_verify():
    data = request.get_json()
    if not data or 'emails' not in data:
        return jsonify({"error": "JSON payload with 'emails' array is required"}), 400
    emails = data['emails']
    if not isinstance(emails, list):
        return jsonify({"error": "'emails' must be an array"}), 400
    if len(emails) > 100:
        return jsonify({"error": "Maximum 100 emails per batch"}), 400
    results = []
    for email in emails:
        try:
            email = str(email).strip()
            valid_format = validate_email_format(email)
            disposable = False
            domain = None
            if valid_format:
                domain = email.split('@')[1].lower()
                disposable = is_disposable_domain(domain)
            score = calculate_email_score(email, valid_format, disposable)
            results.append({
                "email": email,
                "valid_format": valid_format,
                "disposable": disposable,
                "score": score,
                "domain": domain,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
        except Exception as e:
            results.append({
                "email": email,
                "valid_format": False,
                "disposable": False,
                "score": 0,
                "error": "Processing error",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
    return jsonify({
        "total_emails": len(emails),
        "processed": len(results),
        "results": results,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "email-validation-api",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "2.0.0",
        "uptime": "100%"
    })

@app.route('/stats')
def get_stats():
    return jsonify({
        "total_disposable_domains": len(DISPOSABLE_DOMAINS),
        "api_version": "2.0.0",
        "features": [
            "email_format_validation",
            "disposable_domain_detection",
            "quality_scoring",
            "bulk_processing",
            "real_time_validation"
        ],
        "rate_limits": {
            "free": "100 requests/day",
            "authenticated": "1,000 requests/hour"
        },
        "performance": "high",
        "supported_formats": ["JSON"]
    })

@app.route('/domains')
def list_disposable_domains():
    return jsonify({
        "count": len(DISPOSABLE_DOMAINS),
        "domains": sorted(list(DISPOSABLE_DOMAINS)),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500
