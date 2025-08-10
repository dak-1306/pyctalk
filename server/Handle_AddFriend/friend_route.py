from flask import Blueprint, request, jsonify
import json
import os

friend_bp = Blueprint('friend', __name__)

DATA_PATH = 'server/data'
FRIEND_FILE = os.path.join(DATA_PATH, 'friends.json')

# Đảm bảo file tồn tại
if not os.path.exists(FRIEND_FILE):
    with open(FRIEND_FILE, 'w') as f:
        json.dump([], f)

def load_friends():
    with open(FRIEND_FILE, 'r') as f:
        return json.load(f)

def save_friends(data):
    with open(FRIEND_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@friend_bp.route('/api/friend/request', methods=['POST'])
def send_friend_request():
    data = request.get_json()
    from_id = data.get('from_id')
    to_id = data.get('to_id')

    friends = load_friends()
    for f in friends:
        if (f['from_id'] == from_id and f['to_id'] == to_id) or (f['from_id'] == to_id and f['to_id'] == from_id):
            return jsonify({'status': 'exists'})

    friends.append({'from_id': from_id, 'to_id': to_id, 'status': 'pending'})
    save_friends(friends)
    return jsonify({'status': 'sent'})

@friend_bp.route('/api/friend/accept', methods=['POST'])
def accept_friend_request():
    data = request.get_json()
    from_id = data.get('from_id')
    to_id = data.get('to_id')

    friends = load_friends()
    for f in friends:
        if f['from_id'] == from_id and f['to_id'] == to_id and f['status'] == 'pending':
            f['status'] = 'accepted'
            save_friends(friends)
            return jsonify({'status': 'accepted'})

    return jsonify({'status': 'not_found'})

@friend_bp.route('/api/friend/list', methods=['GET'])
def get_friend_list():
    user_id = request.args.get('user_id')
    friends = load_friends()
    result = []
    for f in friends:
        if f['status'] == 'accepted':
            if f['from_id'] == user_id:
                result.append(f['to_id'])
            elif f['to_id'] == user_id:
                result.append(f['from_id'])
    return jsonify({'friends': result})

@friend_bp.route('/api/friend/requests', methods=['GET'])
def get_pending_requests():
    user_id = request.args.get('user_id')
    friends = load_friends()
    result = [f['from_id'] for f in friends if f['to_id'] == user_id and f['status'] == 'pending']
    return jsonify({'requests': result})
