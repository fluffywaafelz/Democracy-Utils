import json
import os

def ensure_json_file(filename):
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            json.dump({}, f)
    else:
        with open(filename, 'r') as f:
            if not f.read().strip():
                with open(filename, 'w') as f:
                    json.dump({}, f)

def load_channels():
    ensure_json_file('channels.json')
    with open('channels.json', 'r') as f:
        return json.load(f)

def get_review_channel_id():
    try:
        with open('main.json', 'r') as f:
            data = json.load(f)
            return data.get('review_channel_id')
    except FileNotFoundError:
        return None
