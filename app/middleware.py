from fastapi import Request, HTTPException
from datetime import date
from db import get_api_key, get_usage, increment_usage

async def api_key_middleware(request: Request, call_next):
    api_key = request.headers.get("X-API-Key")

    if not api_key:
        raise HTTPException(status_code=401, detail="API key missing")

    key_data = get_api_key(api_key)

    if not key_data:
        raise HTTPException(status_code=403, detail="Invalid API key")

    if key_data.status != "active":
        raise HTTPException(status_code=403, detail="API key suspended")

    today = date.today()
    used = get_usage(api_key, today)

    if used >= key_data.daily_quota:
        raise HTTPException(status_code=429, detail="Daily quota exceeded")

    response = await call_next(request)

    increment_usage(api_key, today)
    return response
