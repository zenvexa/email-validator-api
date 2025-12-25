from flask import Flask, request, jsonify
import re
from datetime import datetime
import dns.resolver

from middleware import api_key_middleware

app = Flask(__name__)

DISPOSABLE_DOMAINS = {
    "tempmail.com", "mailinator.com", "yopmail.com",
    "10minutemail.com", "guerrillamail.com", "trashmail.com",
    "fakeinbox.com", "throwawaymail.com", "getairmail.com",
    "sharklasers.com", "guerrillamail.info", "dispostable.com",
    "temp-mail.org", "throwawaymail.com", "mailnesia.com"
}

ROLE_PREFIXES = {"admin", "info", "support", "sales", "contact"}
DOMAIN_CACHE = {}

PLANS = {
    "free": {"requests_per_day": 100, "strict_mode": False},
    "basic": {"requests_per_month": 10000, "strict_mode": True},
    "pro": {"requests_per_month": 50000, "strict_mode": True},
    "enterprise": {"requests_per_month": "Custom", "strict_mode": True}
}

def validate_email_format(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def is_disposable_domain(domain):
    if domain in DOMAIN_CACHE:
        return DOMAIN_CACHE[domain]['disposable']
    disposable = domain.lower() in DISPOSABLE_DOMAINS
    DOMAIN_CACHE[domain] = {"disposable": disposable, "mx_record": None}
    return disposable

def has_mx_record(domain):
    if domain in DOMAIN_CACHE and DOMAIN_CACHE[domain]['mx_record'] is not None:
        return DOMAIN_CACHE[domain]['mx_record']
    try:
        dns.resolver.resolve(domain, 'MX')
        DOMAIN_CACHE[domain]['mx_record'] = True
        return True
    except:
        DOMAIN_CACHE[domain]['mx_record'] = False
        return False

def is_role_email(email):
    return email.split("@")[0].lower() in ROLE_PREFIXES

def calculate_email_score(email, valid, disposable, mx_record, role_email):
    if not valid:
        return 0
    score = 85
    if disposable:
        score = 30
    if role_email:
        score -= 20
    if not mx_record:
        score -= 30
    domain = email.split('@')[1].lower()
    popular_domains = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com"}
    if domain in popular_domains:
        score = max(score, 95)
    score = max(0, min(100, score))
    return score

def determine_risk(disposable, role_email, mx_record):
    if disposable or not mx_record:
        return "high"
    if role_email:
        return "medium"
    return "low"

@app.before_request
def before_request():
    result = api_key_middleware()
    if result:
        return result

@app.route('/')
def home():
    return jsonify({
        "api": "Professional Email Validation API",
        "version": "2.1.0",
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
    plan = request.args.get('plan', 'free')
    strict = request.args.get('strict', 'false').lower() == 'true' and PLANS.get(plan, {}).get('strict_mode', False)

    if not email:
        return jsonify({"error": "Email parameter is required"}), 400
    if len(email) > 254:
        return jsonify({
            "email": email,
            "valid_format": False,
            "disposable": False,
            "mx_record": False,
            "role_email": False,
            "risk_level": "high",
            "score": 0,
            "message": "Email too long (max 254 characters)"
        })

    valid_format = validate_email_format(email)
    domain = email.split('@')[1].lower() if valid_format else None
    disposable = is_disposable_domain(domain) if valid_format else False
    mx_record = has_mx_record(domain) if valid_format else False
    role_email = is_role_email(email) if valid_format else False
    score = calculate_email_score(email, valid_format, disposable, mx_record, role_email)

    if strict and (disposable or role_email or not mx_record):
        score = 0

    response = {
        "email": email,
        "valid_format": valid_format,
        "disposable": disposable,
        "mx_record": mx_record,
        "role_email": role_email,
        "risk_level": determine_risk(disposable, role_email, mx_record),
        "score": score,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "suggestions": []
    }

    if disposable:
        response["suggestions"].append("Use a professional email provider (Gmail, Outlook, etc.)")
    if role_email:
        response["suggestions"].append("Avoid role-based emails like info@, admin@, support@")
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
            domain = email.split('@')[1].lower() if valid_format else None
            disposable = is_disposable_domain(domain) if valid_format else False
            mx_record = has_mx_record(domain) if valid_format else False
            role_email = is_role_email(email) if valid_format else False
            score = calculate_email_score(email, valid_format, disposable, mx_record, role_email)
            results.append({
                "email": email,
                "valid_format": valid_format,
                "disposable": disposable,
                "mx_record": mx_record,
                "role_email": role_email,
                "risk_level": determine_risk(disposable, role_email, mx_record),
                "score": score,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
        except Exception as e:
            results.append({
                "email": email,
                "valid_format": False,
                "disposable": False,
                "mx_record": False,
                "role_email": False,
                "risk_level": "high",
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
        "version": "2.1.0",
        "uptime": "100%"
    })

@app.route('/stats')
def get_stats():
    return jsonify({
        "total_disposable_domains": len(DISPOSABLE_DOMAINS),
        "api_version": "2.1.0",
        "features": [
            "email_format_validation",
            "disposable_domain_detection",
            "mx_record_check",
            "role_email_detection",
            "risk_level_scoring",
            "bulk_processing",
            "real_time_validation",
            "strict_mode_for_paid_plans"
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

if __name__ == "__main__":
    app.run(debug=True)
