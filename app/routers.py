from typing import List
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from app.services.order_service import OrderService, MENU
from app.services.websocket_manager import ConnectionManager
from main import send_push_notification  # ← ADD THIS

router = APIRouter()
ws_manager = ConnectionManager()

# ============================================================
# MENU
# ============================================================
@router.get("/menu")
async def get_menu():
    return {"menu": MENU}

# ============================================================
# ORDERS
# ============================================================
@router.post("/orders")
async def place_order(waiter: str, items: List[int]):
    try:
        order = OrderService.place_order(waiter, items)
        
        # 🔥 Broadcast to chefs via WebSocket
        await ws_manager.broadcast_to_chefs({
            "type": "NEW_ORDER",
            "order": order
        })
        
        # 🔥 Send push notification to chefs
        send_push_notification(
            title='🔔 New Order!',
            body=f'Order #{order["id"]} from {waiter}',
            data={'orderId': order["id"], 'type': 'new_order'},
            role='chef'
        )
        
        return {"success": True, "order_id": order["id"]}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/orders/{order_id}/confirm")
async def confirm_order(order_id: int):
    order = OrderService.confirm_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    await ws_manager.broadcast_to_waiters({
        "type": "ORDER_CONFIRMED",
        "order_id": order_id
    })
    
    return {"success": True}

@router.post("/orders/{order_id}/ready")
async def mark_ready(order_id: int):
    order = OrderService.mark_ready(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # 🔥 Broadcast to waiters via WebSocket
    await ws_manager.broadcast_to_waiters({
        "type": "ORDER_READY",
        "order_id": order_id,
        "order": order
    })
    
    # 🔥 Send push notification to waiters
    send_push_notification(
        title='✅ Order Ready!',
        body=f'Order #{order_id} is ready to serve',
        data={'orderId': order_id, 'type': 'order_ready'},
        role='waiter'
    )
    
    return {"success": True}

@router.post("/orders/{order_id}/serve")
async def serve_order(order_id: int):
    order = OrderService.serve_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    await ws_manager.broadcast_to_waiters({
        "type": "ORDER_SERVED",
        "order_id": order_id
    })
    
    return {"success": True}

@router.get("/orders/pending")
async def get_pending():
    return {"orders": OrderService.get_pending()}

@router.get("/orders/ready")
async def get_ready():
    return {"orders": OrderService.get_ready()}

@router.get("/orders")
async def get_all():
    return {"orders": OrderService.get_all()}

# ⚠️ IMPORTANT: Put /clear BEFORE /{order_id} ⚠️
@router.delete("/orders/clear")
async def clear_all():
    count = OrderService.clear_all()
    return {"success": True, "message": f"Cleared {count} orders"}

@router.delete("/orders/{order_id}")
async def delete_order(order_id: int):
    if not OrderService.delete_order(order_id):
        raise HTTPException(status_code=404, detail="Order not found")
    return {"success": True}

@router.get("/orders/stats")
async def get_stats():
    return OrderService.get_stats()

# ============================================================
# WEBSOCKETS
# ============================================================
@router.websocket("/ws/chef")
async def websocket_chef(websocket: WebSocket):
    await ws_manager.connect_chef(websocket)
    try:
        pending = OrderService.get_pending()
        await websocket.send_json({
            "type": "INITIAL_STATE",
            "pending_orders": pending
        })
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect_chef(websocket)

@router.websocket("/ws/waiter")
async def websocket_waiter(websocket: WebSocket):
    await ws_manager.connect_waiter(websocket)
    try:
        ready = OrderService.get_ready()
        await websocket.send_json({
            "type": "INITIAL_STATE",
            "ready_orders": ready
        })
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect_waiter(websocket)