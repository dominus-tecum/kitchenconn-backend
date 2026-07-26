from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import router
from app.config import settings
import requests
from pydantic import BaseModel
from typing import Optional, List

# ============================================================
# PUSH NOTIFICATION MODELS
# ============================================================

class PushTokenRegister(BaseModel):
    token: str
    role: str  # 'chef' or 'waiter'

class PushNotification(BaseModel):
    title: str
    body: str
    data: Optional[dict] = {}
    role: str = 'chef'

# ============================================================
# STORE PUSH TOKENS (in-memory - use Redis/DB in production)
# ============================================================
push_tokens = []  # List of {token: str, role: str}

# ============================================================
# APP SETUP
# ============================================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Restaurant communication app"
)

# CORS - Allow all origins for ngrok
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
        "https://caca-196-189-154-137.ngrok-free.app",
        "http://localhost:19000",
        "http://localhost:19006",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)

# ============================================================
# PUSH NOTIFICATION ENDPOINTS
# ============================================================

@app.post("/api/register-push-token")
async def register_push_token(data: PushTokenRegister):
    """Register a device push token"""
    try:
        # Check if token already exists
        existing = next((t for t in push_tokens if t['token'] == data.token), None)
        if existing:
            existing['role'] = data.role
        else:
            push_tokens.append({'token': data.token, 'role': data.role})
        
        print(f'✅ Push token registered: {data.token[:20]}... for role: {data.role}')
        return {"success": True, "message": "Token registered"}
    except Exception as e:
        print(f'❌ Error registering token: {e}')
        return {"success": False, "error": str(e)}, 500

@app.get("/api/push-tokens")
async def get_push_tokens():
    """Get all registered push tokens (for debugging)"""
    return {"tokens": push_tokens, "count": len(push_tokens)}

# ============================================================
# PUSH NOTIFICATION FUNCTION
# ============================================================

def send_push_notification(title: str, body: str, data: dict = None, role: str = 'chef'):
    """Send a push notification to all devices with the given role"""
    if data is None:
        data = {}
    
    # Find tokens for the role
    tokens = [t['token'] for t in push_tokens if t['role'] == role]
    
    if not tokens:
        print(f'⚠️ No push tokens found for role: {role}')
        return {"success": False, "message": "No tokens found"}
    
    success_count = 0
    for token in tokens:
        payload = {
            'to': token,
            'title': title,
            'body': body,
            'sound': 'default',
            'priority': 'high',  # 🔥 Critical for waking device
            'data': data,
        }
        
        try:
            response = requests.post(
                'https://exp.host/--/api/v2/push/send',
                headers={'Content-Type': 'application/json'},
                json=payload
            )
            if response.status_code == 200:
                success_count += 1
                print(f'✅ Push sent to {token[:20]}...')
            else:
                print(f'❌ Push failed: {response.status_code} - {response.text}')
        except Exception as e:
            print(f'❌ Error sending push: {e}')
    
    return {"success": True, "sent": success_count, "total": len(tokens)}

# ============================================================
# ROOT ENDPOINTS
# ============================================================

@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "ngrok_url": "https://caca-196-189-154-137.ngrok-free.app",
        "push_tokens_registered": len(push_tokens),
        "endpoints": [
            "GET  /",
            "POST /api/register-push-token",
            "GET  /api/push-tokens",
            # ... other endpoints
        ]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "ngrok_url": "https://caca-196-189-154-137.ngrok-free.app",
        "push_tokens": len(push_tokens)
    }

if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("🍕 KitchenConn Backend")
    print("=" * 50)
    print("📋 Menu: 18 items loaded")
    print("🌐 http://localhost:8000")
    print("🔗 ngrok: https://caca-196-189-154-137.ngrok-free.app")
    print("📡 WebSocket routes:")
    print("   - ws://localhost:8000/ws/chef")
    print("   - wss://caca-196-189-154-137.ngrok-free.app/ws/chef")
    print("   - ws://localhost:8000/ws/waiter")
    print("   - wss://caca-196-189-154-137.ngrok-free.app/ws/waiter")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000)