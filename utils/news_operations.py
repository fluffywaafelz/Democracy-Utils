import json
import uuid

def load_requests():
    with open('requests.json', 'r') as f:
        return json.load(f)

def save_request(requests):
    with open('requests.json', 'w') as f:
        json.dump(requests, f, indent=4)

def create_request(channel_id, discord_invite, user_id):
    request_id = str(uuid.uuid4())
    return {
        request_id: {
            "channel_id": channel_id,
            "discord_invite": discord_invite,
            "request_id": request_id,
            "requester_discord_id": user_id
        }
    }
