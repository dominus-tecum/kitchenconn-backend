from typing import List, Optional
from datetime import datetime
import json
import os

# File to store daily order data
DATA_FILE = "orders_data.json"

# Load data from file if exists
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"date": None, "counter": 0, "orders": []}

# Save data to file
def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# Initialize
data = load_data()
today = datetime.now().strftime("%Y-%m-%d")

# Reset counter if new day
if data["date"] != today:
    data["date"] = today
    data["counter"] = 0
    data["orders"] = []
    save_data(data)

orders = data["orders"]
order_counter = data["counter"]

MENU = [
    {"id": 1, "name": "Special Pizza", "nameAm": "ስፔሻል ፒዛ"},
    {"id": 2, "name": "Meat Lovers (Beef) Pizza", "nameAm": "ሚት ላቨርስ ፒዛ"},
    {"id": 3, "name": "Al Tuna Pizza (Tuna with cheese)", "nameAm": "አል ቱና ፒዛ"},
    {"id": 4, "name": "Tuna Pizza (Tuna without cheese)", "nameAm": "ቱና ፒዛ"},
    {"id": 5, "name": "Vegetable Pizza", "nameAm": "ቬጂቴብል ፒዛ"},
    {"id": 6, "name": "Margarita Pizza", "nameAm": "ማርጋሪታ ፒዛ"},
    {"id": 7, "name": "Special Burger", "nameAm": "ስፔሻል በርገር"},
    {"id": 8, "name": "Double Burger", "nameAm": "ድብል በርገር"},
    {"id": 9, "name": "Cheese Burger", "nameAm": "ቺዝ በርገር"},
    {"id": 10, "name": "Beef Burger", "nameAm": "ቢፍ በርገር"},
    {"id": 11, "name": "Egg Sandwich", "nameAm": "ኤግ ሳንድዊች"},
    {"id": 12, "name": "Tuna With Cheese Sandwich", "nameAm": "ቱና ዊዝ ቺዝ ሳንድዊች"},
    {"id": 13, "name": "Chicken Burger", "nameAm": "ቺክን በርገር"},
    {"id": 14, "name": "Hummus Pizza", "nameAm": "ሁመስ ፒዛ"},
    {"id": 15, "name": "Special Fasting Pizza", "nameAm": "ስፔሻል ፆም ፒዛ"},
    {"id": 16, "name": "Chicken Wrap", "nameAm": "ቺክን ራፕ"},
    {"id": 17, "name": "Veggie Wrap", "nameAm": "ቬጂ ራፕ"},
    {"id": 18, "name": "Special Veggie Wrap", "nameAm": "ስፔሻል ቬጂ ራፕ"},
    {"id": 19, "name": "Hummus", "nameAm": "ሁመስ"},
    {"id": 20, "name": "Tuna Sandwich", "nameAm": "ቱና ሳንድዊች"},
    {"id": 21, "name": "Tuna Wrap", "nameAm": "ቱና ራፕ"},
    {"id": 22, "name": "Veggie Sandwich", "nameAm": "ቬጂ ሳንድዊች"},
    {"id": 23, "name": "Avocado Toast", "nameAm": "አቮካዶ ቶስት"},
]
def get_item_names(item_ids: List[int]) -> List[str]:
    names = []
    for item_id in item_ids:
        for item in MENU:
            if item["id"] == item_id:
                names.append(item["name"])
                break
    return names

class OrderService:
    @staticmethod
    def place_order(waiter: str, items: List[int]) -> dict:
        global order_counter, orders, data
        
        if not items:
            raise ValueError("No items in order")
        
        # Check if new day
        today = datetime.now().strftime("%Y-%m-%d")
        if data["date"] != today:
            data["date"] = today
            data["counter"] = 0
            data["orders"] = []
            orders = data["orders"]
        
        valid_ids = [item["id"] for item in MENU]
        for item_id in items:
            if item_id not in valid_ids:
                raise ValueError(f"Invalid item: {item_id}")
        
        data["counter"] += 1
        order_counter = data["counter"]
        order = {
            "id": order_counter,
            "items": items,
            "item_names": get_item_names(items),
            "waiter": waiter,
            "timestamp": datetime.now().strftime("%I:%M %p"),
            "date": today,
            "status": "pending",
            "confirmed_at": None,
            "ready_at": None,
            "served_at": None
        }
        data["orders"].append(order)
        orders = data["orders"]
        save_data(data)
        return order
    
    @staticmethod
    def get_pending() -> List[dict]:
        return [o for o in orders if o["status"] in ["pending", "confirmed"]]
    
    @staticmethod
    def get_ready() -> List[dict]:
        return [o for o in orders if o["status"] == "ready"]
    
    @staticmethod
    def get_all() -> List[dict]:
        return orders
    
    @staticmethod
    def get_today_orders() -> List[dict]:
        today = datetime.now().strftime("%Y-%m-%d")
        return [o for o in orders if o.get("date") == today]
    
    @staticmethod
    def confirm_order(order_id: int) -> Optional[dict]:
        for order in orders:
            if order["id"] == order_id:
                order["status"] = "confirmed"
                order["confirmed_at"] = datetime.now().strftime("%I:%M %p")
                save_data(data)
                return order
        return None
    
    @staticmethod
    def mark_ready(order_id: int) -> Optional[dict]:
        for order in orders:
            if order["id"] == order_id:
                order["status"] = "ready"
                order["ready_at"] = datetime.now().strftime("%I:%M %p")
                save_data(data)
                return order
        return None
    
    @staticmethod
    def serve_order(order_id: int) -> Optional[dict]:
        for order in orders:
            if order["id"] == order_id:
                order["status"] = "served"
                order["served_at"] = datetime.now().strftime("%I:%M %p")
                save_data(data)
                return order
        return None
    
    @staticmethod
    def delete_order(order_id: int) -> bool:
        global orders, data
        for i, order in enumerate(orders):
            if order["id"] == order_id:
                del orders[i]
                data["orders"] = orders
                save_data(data)
                return True
        return False
    
    @staticmethod
    def clear_all() -> int:
        global orders, data
        count = len(orders)
        orders = []
        data["orders"] = []
        data["counter"] = 0
        save_data(data)
        return count
    
    @staticmethod
    def get_stats() -> dict:
        total = len(orders)
        pending = len([o for o in orders if o["status"] == "pending"])
        confirmed = len([o for o in orders if o["status"] == "confirmed"])
        ready = len([o for o in orders if o["status"] == "ready"])
        served = len([o for o in orders if o["status"] == "served"])
        
        item_counts = {}
        for order in orders:
            for name in order["item_names"]:
                item_counts[name] = item_counts.get(name, 0) + 1
        
        popular = sorted(
            [{"name": k, "count": v} for k, v in item_counts.items()],
            key=lambda x: x["count"], reverse=True
        )[:10]
        
        return {
            "total": total,
            "pending": pending,
            "confirmed": confirmed,
            "ready": ready,
            "served": served,
            "popularItems": popular
        }