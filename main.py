from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import router
from app.config import settings

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

@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "ngrok_url": "https://caca-196-189-154-137.ngrok-free.app",
        "endpoints": [
            "GET  /",
            "GET  /menu",
            "POST /orders?waiter=name&items=[1,2,3]",
            "POST /orders/{id}/confirm",
            "POST /orders/{id}/ready",
            "POST /orders/{id}/serve",
            "GET  /orders/pending",
            "GET  /orders/ready",
            "GET  /orders",
            "DELETE /orders/{id}",
            "DELETE /orders/clear",
            "GET  /orders/stats",
            "WS   /ws/chef",
            "WS   /ws/waiter"
        ]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "ngrok_url": "https://caca-196-189-154-137.ngrok-free.app"
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