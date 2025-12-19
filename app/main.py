cp main.py main.py.error

cat > main.py << 'EOF'
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DISPOSABLE_DOMAINS = {
    "tempmail.com", "mailinator.com", "yopmail.com",
    "10minutemail.com", "guerrillamail.com", "trashmail.com"
}

@app.get("/")
def home():
    return {"API": "Email Validator", "status": "active"}

@app.get("/verify")
def verify(email: str = Query(...)):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    valid = bool(re.match(pattern, email))
    
    if not valid:
        return {"email": email, "valid": False}
    
    domain = email.split('@')[1].lower()
    disposable = domain in DISPOSABLE_DOMAINS
    
    return {
        "email": email,
        "valid": True,
        "disposable": disposable,
        "domain": domain
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF
