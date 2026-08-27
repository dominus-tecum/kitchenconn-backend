from typing import List, Optional
from datetime import datetime
import json
import os
import pytz

# ============================================================
# PERSISTENT STORAGE
# ============================================================
DATA_DIR = os.environ.get('DATA_DIR', 'data')
DATA_FILE = os.path.join(DATA_DIR, 'orders_data.json')

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# ============================================================
# TIMEZONE CONFIGURATION
# ============================================================
TIMEZONE_STR = os.environ.get('TIMEZONE', 'Africa/Addis_Ababa')
TIMEZONE = pytz.timezone(TIMEZONE_STR)

def get_current_time():
    """Get current time in local timezone"""
    return datetime.now(TIMEZONE)

# ============================================================
# DATA STORAGE
# ============================================================
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"date": None, "counter": 0, "orders": [], "start_number": None, "start_number_set_today": False}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# Initialize
data = load_data()
today = get_current_time().strftime("%Y-%m-%d")

# Reset counter if new day
if data.get("date") != today:
    data["date"] = today
    data["counter"] = 0
    data["orders"] = []
    data["start_number"] = None
    data["start_number_set_today"] = False
    save_data(data)

orders = data["orders"]
order_counter = data["counter"]

# ============================================================
# MENU
# ============================================================
MENU = [
    {"id": 1, "name": "Special Pizza", "nameAm": "ስፔሻል ፒዛ"},
    {"id": 2, "name": "Meat Lovers (Beef) Pizza", "nameAm": "ሚት ላቨርስ ፒዛ"},
    {"id": 3, "name": "Al Tuna Pizza (Tuna with cheese)", "nameAm": "አል ቱና ፒዛ"},
    {"id": 4, "name": "Steak Cheese Sandwich", "nameAm": "ስቲክ ቺዝ ሳንድዊች"},
    {"id": 5, "name": "Vegetable Pizza", "nameAm": "ቬጂቴብል ፒዛ"},
    {"id": 6, "name": "Margarita Pizza", "nameAm": "ማርጋሪታ ፒዛ"},
    {"id": 7, "name": "Special Burger", "nameAm": "ስፔሻል በርገር"},
    {"id": 8, "name": "Double Burger", "nameAm": "ድብል በርገር"},
    {"id": 9, "name": "Cheese Burger", "nameAm": "ቺዝ በርገር"},
    {"id": 10, "name": "Beef Burger", "nameAm": "ቢፍ በርገር"},
    {"id": 11, "name": "Egg Twist", "nameAm": "ኤግ ትዊስት"},
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
    {"id": 23, "name": "Club Sandwich", "nameAm": "ክለብ ሳንድዊች"},
    {"id": 24, "name": "Chicken Sandwich", "nameAm": "ቺክን ሳንድዊች"},
    {"id": 25, "name": "Chicken Pesto Sandwich", "nameAm": "ቺክን ፔስቶ ሳንድዊች"},
    {"id": 26, "name": "Chicken Pesto Wrap", "nameAm": "ቺክን ፔስቶ ራፕ"},
    # REMOVED: Meat Omelet (id: 29) and Meat With Egg Omelet (id: 30)
    {"id": 31, "name": "Barbeque Chicken", "nameAm": "ባርቤኪው ቺክን"},
    {"id": 32, "name": "Barbeque Beef", "nameAm": "ባርቤኪው ቢፍ"},
    {"id": 33, "name": "Barbeque Pizza", "nameAm": "ባርቤኪው ፒዛ"},
    # ADDED: Chicken Pizza
    {"id": 34, "name": "Chicken Pizza", "nameAm": "ቺክን ፒዛ"},
]

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def get_item_names(item_ids: List[int]) -> List[str]:
    names = []
    for item_id in item_ids:
        for item in MENU:
            if item["id"] == item_id:
                names.append(item["name"])
                break
    return names

def get_item_names_am(item_ids: List[int]) -> List[str]:
    names = []
    for item_id in item_ids:
        for item in MENU:
            if item["id"] == item_id:
                names.append(item["nameAm"])
                break
    return names

def format_time(dt: datetime) -> str:
    return dt.strftime("%I:%M %p")

def format_date(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")

# ============================================================
# ORDER SERVICE
# ============================================================
class OrderService:
    @staticmethod
    def place_order(waiter: str, items: List[int]) -> dict:
        global order_counter, orders, data
        
        if not items:
            raise ValueError("No items in order")
        
        # Check if new day
        now = get_current_time()
        today = format_date(now)
        if data.get("date") != today:
            data["date"] = today
            data["counter"] = 0
            data["orders"] = []
            data["start_number"] = None
            data["start_number_set_today"] = False
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
            "item_names_am": get_item_names_am(items),
            "waiter": waiter,
            "timestamp": format_time(now),
            "date": today,
            "datetime": now.isoformat(),
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
        return orders
    
    @staticmethod
    def get_ready() -> List[dict]:
        return [o for o in orders if o["status"] == "ready"]
    
    @staticmethod
    def get_all() -> List[dict]:
        return orders
    
    @staticmethod
    def get_today_orders() -> List[dict]:
        today = format_date(get_current_time())
        return [o for o in orders if o.get("date") == today]
    
    @staticmethod
    def confirm_order(order_id: int) -> Optional[dict]:
        for order in orders:
            if order["id"] == order_id:
                order["status"] = "confirmed"
                order["confirmed_at"] = format_time(get_current_time())
                save_data(data)
                return order
        return None
    
    @staticmethod
    def mark_ready(order_id: int) -> Optional[dict]:
        for order in orders:
            if order["id"] == order_id:
                order["status"] = "ready"
                order["ready_at"] = format_time(get_current_time())
                save_data(data)
                return order
        return None
    
    @staticmethod
    def serve_order(order_id: int) -> Optional[dict]:
        for order in orders:
            if order["id"] == order_id:
                order["status"] = "served"
                order["served_at"] = format_time(get_current_time())
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
        data["start_number"] = None
        data["start_number_set_today"] = False
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

    @staticmethod
    def place_order_with_names(waiter: str, items: List[int], item_names: List[str], item_names_am: List[str]) -> dict:
        global order_counter, orders, data
        
        if not items:
            raise ValueError("No items in order")
        
        # Check if new day
        now = get_current_time()
        today = format_date(now)
        if data.get("date") != today:
            data["date"] = today
            data["counter"] = 0
            data["orders"] = []
            data["start_number"] = None
            data["start_number_set_today"] = False
            orders = data["orders"]
        
        data["counter"] += 1
        order_counter = data["counter"]
        order = {
            "id": order_counter,
            "items": items,
            "item_names": item_names,
            "item_names_am": item_names_am,
            "waiter": waiter,
            "timestamp": format_time(now),
            "date": today,
            "datetime": now.isoformat(),
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
    def set_start_number(start_number: int) -> dict:
        """Set the starting order number for the day"""
        global data, order_counter, orders
        
        if start_number < 1:
            raise ValueError("Start number must be at least 1")
        
        # Check if new day
        now = get_current_time()
        today = format_date(now)
        if data.get("date") != today:
            data["date"] = today
            data["counter"] = 0
            data["orders"] = []
            data["start_number"] = None
            data["start_number_set_today"] = False
            orders = data["orders"]
        
        # Set the start number
        data["start_number"] = start_number
        data["counter"] = start_number - 1
        data["start_number_set_today"] = True
        order_counter = data["counter"]
        save_data(data)
        
        return {"success": True, "start_number": start_number}

    @staticmethod
    def get_start_number_status() -> dict:
        """Get the current start number status for today"""
        global data
        return {
            "is_set": data.get("start_number_set_today", False),
            "start_number": data.get("start_number")
        }

    @staticmethod
    def renumber_orders(new_start_number: int) -> dict:
        """Renumber all existing orders based on new start number"""
        global orders, data, order_counter
        
        if new_start_number < 1:
            raise ValueError("Start number must be at least 1")
        
        if not orders:
            return {"success": True, "message": "No orders to renumber", "renumbered": 0}
        
        # Get the current first order number
        current_first_order = orders[0]["id"]
        
        # Calculate the offset
        offset = new_start_number - current_first_order
        
        # Renumber all orders
        for order in orders:
            order["id"] = order["id"] + offset
        
        # Update the counter
        last_order_id = orders[-1]["id"]
        data["counter"] = last_order_id
        order_counter = data["counter"]
        data["start_number"] = new_start_number
        data["start_number_set_today"] = True
        
        save_data(data)
        
        return {
            "success": True,
            "message": f"Renumbered {len(orders)} orders",
            "renumbered": len(orders),
            "new_start_number": new_start_number,
            "last_order": last_order_id
        }