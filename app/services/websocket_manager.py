from typing import List
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.chefs: List[WebSocket] = []
        self.waiters: List[WebSocket] = []

    async def connect_chef(self, websocket: WebSocket):
        await websocket.accept()
        self.chefs.append(websocket)

    async def connect_waiter(self, websocket: WebSocket):
        await websocket.accept()
        self.waiters.append(websocket)

    def disconnect_chef(self, websocket: WebSocket):
        if websocket in self.chefs:
            self.chefs.remove(websocket)

    def disconnect_waiter(self, websocket: WebSocket):
        if websocket in self.waiters:
            self.waiters.remove(websocket)

    async def broadcast_to_chefs(self, message: dict):
        for chef in self.chefs:
            try:
                await chef.send_json(message)
            except:
                pass

    async def broadcast_to_waiters(self, message: dict):
        for waiter in self.waiters:
            try:
                await waiter.send_json(message)
            except:
                pass