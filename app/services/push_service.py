import requests
import json
import os
from typing import List, Dict, Any

# Persistent storage path
DATA_DIR = os.environ.get('DATA_DIR', 'data')
TOKENS_FILE = os.path.join(DATA_DIR, 'push_tokens.json')

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

def load_tokens():
    """Load push tokens from persistent storage"""
    try:
        if os.path.exists(TOKENS_FILE):
            with open(TOKENS_FILE, 'r') as f:
                tokens = json.load(f)
                print(f'📱 Loaded {len(tokens)} tokens from storage')
                return tokens
    except Exception as e:
        print(f'⚠️ Error loading tokens: {e}')
    return []

def save_tokens(tokens):
    """Save push tokens to persistent storage"""
    try:
        with open(TOKENS_FILE, 'w') as f:
            json.dump(tokens, f, indent=2)
        print(f'💾 Tokens saved to {TOKENS_FILE}')
    except Exception as e:
        print(f'❌ Error saving tokens: {e}')

# Load tokens from persistent storage
push_tokens = load_tokens()

def register_push_token(token: str, role: str) -> Dict[str, Any]:
    """Register a device push token"""
    global push_tokens
    
    # Check if token already exists
    existing = next((t for t in push_tokens if t['token'] == token), None)
    if existing:
        existing['role'] = role
    else:
        push_tokens.append({'token': token, 'role': role})
    
    # Save to persistent storage
    save_tokens(push_tokens)
    
    print(f'✅ Push token registered: {token[:20]}... for role: {role}')
    return {"success": True, "message": "Token registered"}

def get_all_tokens() -> Dict[str, Any]:
    """Get all registered push tokens (for debugging)"""
    return {"tokens": push_tokens, "count": len(push_tokens)}

def send_push_notification(title: str, body: str, data: dict = None, role: str = 'chef'):
    """Send a push notification to all devices with the given role"""
    if data is None:
        data = {}
    
    # Determine channel ID based on role
    if role == 'chef':
        channel_id = 'orders_v2'
    else:
        channel_id = 'ready-orders_v2'
    
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
            'sound': 'default',          # 🔥 CHANGED from 'notification.mp3'
            'priority': 'high',
            'channelId': channel_id,     # 🔥 CHANGED from 'chef-alerts'
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