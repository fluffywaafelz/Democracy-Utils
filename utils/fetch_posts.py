import requests
import os
import re
from datetime import datetime
from config import XENFORO_API_KEY, XENFORO_API_URL
import json

latest_thread_ids = {}  # Ensure it's a dictionary

def load_latest_thread_ids(filename='latest_thread_ids.json'):
    """Load the latest thread IDs from a JSON file."""
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                # Ensure all keys are strings
                return {str(k): v for k, v in data.items()}
        except json.JSONDecodeError as e:
            print(f'Error decoding JSON from file: {e}')
            return {}
    return {}

def save_latest_thread_ids(latest_thread_ids, filename='latest_thread_ids.json'):
    """Save the latest thread IDs to a JSON file."""
    try:
        # Ensure all keys are strings
        latest_thread_ids_str_keys = {str(k): v for k, v in latest_thread_ids.items()}
#        print(f"Saving latest thread IDs: {latest_thread_ids_str_keys}")  # Debugging line
        with open(filename, 'w') as f:
            json.dump(latest_thread_ids_str_keys, f, indent=4)
    except IOError as e:
        print(f"File I/O error occurred: {e}")
    except json.JSONDecodeError as e:
        print(f"JSON decode error occurred: {e}")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")

latest_thread_ids = load_latest_thread_ids()  # Initialize and load latest thread IDs
#print(f"Loaded latest thread IDs: {latest_thread_ids}")

def get_latest_post(forum_id):
    headers = {
        'XF-Api-Key': XENFORO_API_KEY
    }
    try:
        response = requests.get(f'{XENFORO_API_URL}forums/{forum_id}/threads', headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        threads = response.json()
        if threads and 'threads' in threads:
            latest_thread = threads['threads'][0]
            thread_id = latest_thread['thread_id']
            key = f"{forum_id}_{thread_id}"

            # Check if this is a new thread by comparing the key
            if key not in latest_thread_ids:
                # Update the latest_thread_id and remove old entries
                latest_thread_ids[key] = thread_id
                save_latest_thread_ids(latest_thread_ids)  # Save to JSON file

                # Fetch latest post and other details
                response = requests.get(f'{XENFORO_API_URL}threads/{thread_id}/posts', headers=headers)
                response.raise_for_status()
                posts = response.json()
                if posts and 'posts' in posts:
                    latest_post = posts['posts'][0]
                    user_id = latest_post['user_id']

                    # Fetch user data to get avatar URL
                    user_response = requests.get(f'{XENFORO_API_URL}users/{user_id}', headers=headers)
                    user_response.raise_for_status()
                    user_data = user_response.json()

                    # Check if 'avatar_urls' is in 'user_data'
                    user_info = user_data['user']
                    avatar_url = user_info['avatar_urls'].get('s') if 'avatar_urls' in user_info else None

                    thread_title = latest_thread['title']
                    view_url = latest_thread['view_url']
                    post_content = latest_post['message']
                    author_name = latest_post['username']
                    post_date = latest_post['post_date']
                    post_time = datetime.fromtimestamp(post_date)
                    attachments = latest_post.get('Attachments', [])
                    # Ensure attachments is always a list
                    if not isinstance(attachments, list):
                        attachments = []
                        
                    return thread_title, post_content, author_name, post_time, avatar_url, view_url, attachments
                else:
                    raise ValueError('No posts found in the API response')
            else:
                return None, None, None, None, None, None, None  # No new thread found
        else:
            raise ValueError('No threads found in the API response')
    except requests.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        print(f'Response content: {response.content}')
        print(f'Response headers: {response.headers}')
    except ValueError as value_err:
        print(f'Value error occurred: {value_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
    return None, None, None, None, None, None, None


def format_content(content):
    # Remove [COLOR] tags and format [B] tags to Discord Markdown
    content = re.sub(r'\[COLOR=rgb\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)\]', '', content)
    content = content.replace('[/COLOR]', '')
    content = content.replace('[B]', '**').replace('[/B]', '**')
    return content
