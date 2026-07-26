import requests
from typing import List, Dict, Any

# Store push tokens (in-memory - use Redis/DB in production)
push_tokens = []  # List of {token: str, role: str}

def register_push_token(token: str, role: str) -> Dict[str, Any]:
    """Register a device push token"""
    # Check if token already exists
    existing = next((t for t in push_tokens if t['token'] == token), None)
    if existing:
        existing['role'] = role
    else:
        push_tokens.append({'token': token, 'role': role})
    
    print(f'✅ Push token registered: {token[:20]}... for role: {role}')
    return {"success": True, "message": "Token registered"}

def get_all_tokens() -> Dict[str, Any]:
    """Get all registered push tokens (for debugging)"""
    return {"tokens": push_tokens, "count": len(push_tokens)}

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