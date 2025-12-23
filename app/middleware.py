from flask import request, jsonify
from datetime import date
from db import get_api_key, get_usage, increment_usage

EXCLUDED_PATHS = ["/", "/health"]

def api_key_middleware():
    if request.path in EXCLUDED_PATHS:
        return None

    api_key = request.headers.get("X-API-Key")
    if not api_key:
        return jsonify({"error": "API key missing"}), 401

    key_data = get_api_key(api_key)
    if not key_data:
        return jsonify({"error": "Invalid API key"}), 403

    if key_data["status"] != "active":
        return jsonify({"error": "API key suspended"}), 403

    today = date.today()
    used = get_usage(api_key, today)

    if used >= key_data["daily_quota"]:
        return jsonify({"error": "Daily quota exceeded"}), 429

    increment_usage(api_key, today)
    return None
