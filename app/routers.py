from typing import List, Optional
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from app.services.order_service import OrderService, MENU
from app.services.websocket_manager import ConnectionManager
from app.services.push_service import send_push_notification
import csv
import io
from datetime import datetime
from pydantic import BaseModel

router = APIRouter()
ws_manager = ConnectionManager()


# ============================================================
# PYDANTIC MODEL - ADD THIS
# ============================================================
class OrderRequest(BaseModel):
    waiter: str
    items: List[int]
    item_names: Optional[List[str]] = None
    item_names_am: Optional[List[str]] = None


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
async def place_order(order_data: OrderRequest):
    try:
        # If item_names and item_names_am are provided, use them
        if order_data.item_names is not None and order_data.item_names_am is not None:
            order = OrderService.place_order_with_names(
                waiter=order_data.waiter,
                items=order_data.items,
                item_names=order_data.item_names,
                item_names_am=order_data.item_names_am
            )
        else:
            # Legacy: use the menu to look up names
            order = OrderService.place_order(order_data.waiter, order_data.items)
        
        await ws_manager.broadcast_to_chefs({
            "type": "NEW_ORDER",
            "order": order
        })
        
        send_push_notification(
            title='🔔 New Order!',
            body=f'Order #{order["id"]} from {order_data.waiter}',
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
    
    await ws_manager.broadcast_to_waiters({
        "type": "ORDER_READY",
        "order_id": order_id,
        "order": order
    })
    
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
# SUMMARY & EXPORT
# ============================================================

@router.get("/orders/summary/today")
async def get_today_summary():
    """Get summary of today's orders - simplified"""
    today = datetime.now().strftime("%Y-%m-%d")
    orders = OrderService.get_today_orders()
    
    item_counts = {}
    for order in orders:
        for name in order["item_names"]:
            item_counts[name] = item_counts.get(name, 0) + 1
    
    sorted_items = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)
    
    return {
        "date": today,
        "total_orders": len(orders),
        "items": [{"name": name, "count": count} for name, count in sorted_items]
    }

@router.get("/orders/export/csv")
async def export_orders_csv():
    """Export all orders as CSV file"""
    orders = OrderService.get_all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Order ID', 'Waiter', 'Items', 'Status', 'Date', 'Time', 'Confirmed At', 'Ready At', 'Served At'])
    
    for order in orders:
        writer.writerow([
            order['id'],
            order['waiter'],
            '; '.join(order['item_names']),
            order['status'],
            order.get('date', ''),
            order['timestamp'],
            order.get('confirmed_at', ''),
            order.get('ready_at', ''),
            order.get('served_at', '')
        ])
    
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=orders_{datetime.now().strftime('%Y-%m-%d')}.csv"}
    )

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