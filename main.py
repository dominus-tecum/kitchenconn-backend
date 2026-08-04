import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import router
from app.config import settings
from app.services.push_service import register_push_token, get_all_tokens, send_push_notification, push_tokens
from pydantic import BaseModel
from typing import Optional, List

# ============================================================
# SET DATA DIRECTORY FOR PERSISTENT STORAGE
# ============================================================
os.environ['DATA_DIR'] = '/opt/render/project/src/data'

# ============================================================
# PUSH NOTIFICATION MODELS
# ============================================================

class PushTokenRegister(BaseModel):
    token: str
    role: str  # 'chef' or 'waiter'

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
        " https://08bf-196-189-56-125.ngrok-free.app",
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
async def register_push_token_endpoint(data: PushTokenRegister):
    """Register a device push token"""
    return register_push_token(data.token, data.role)

@app.get("/api/push-tokens")
async def get_push_tokens():
    """Get all registered push tokens (for debugging)"""
    return get_all_tokens()

# ============================================================
# ROOT ENDPOINTS
# ============================================================

@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "ngrok_url": "https://08bf-196-189-56-125.ngrok-free.app",
        "push_tokens_registered": len(push_tokens),
        "endpoints": [
            "GET  /",
            "POST /api/register-push-token",
            "GET  /api/push-tokens",
        ]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "ngrok_url": "https://08bf-196-189-56-125.ngrok-free.app",
        "push_tokens": len(push_tokens)
    }

if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("🍕 KitchenConn Backend")
    print("=" * 50)
    print("📋 Menu: 18 items loaded")
    print("🌐 http://localhost:8000")
    print("🔗 ngrok:  https://08bf-196-189-56-125.ngrok-free.app")
    print("📡 WebSocket routes:")
    print("   - ws://localhost:8000/ws/chef")
    print("   - wss://08bf-196-189-56-125.ngrok-free.app/ws/chef")
    print("   - ws://localhost:8000/ws/waiter")
    print("   - wss://08bf-196-189-56-125.ngrok-free.app/ws/waiter")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000)