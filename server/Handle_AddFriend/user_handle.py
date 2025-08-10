from flask import Blueprint, request, jsonify
import json
import os
from collections import Counter

user_bp = Blueprint('user', __name__)

DATA_PATH = 'server/data'
USER_FILE = os.path.join(DATA_PATH, 'users.json')
FRIEND_FILE = os.path.join(DATA_PATH, 'friends.json')

# Load user data
def load_users():
    with open(USER_FILE, 'r') as f:
        return json.load(f)

# Load friend data
def load_friends():
    with open(FRIEND_FILE, 'r') as f:
        return json.load(f)

@user_bp.route('/api/user/suggestions', methods=['GET'])
def suggest_friends():
    user_id = request.args.get('user_id')
    users = load_users()
    friends = load_friends()

    # Danh sách ID người dùng
    all_user_ids = [u['id'] for u in users if u['id'] != user_id]

    # Danh sách bạn bè hiện tại
    current_friends = set()
    pending = set()
    for f in friends:
        if f['status'] == 'accepted':
            if f['from_id'] == user_id:
                current_friends.add(f['to_id'])
            elif f['to_id'] == user_id:
                current_friends.add(f['from_id'])
        elif f['status'] == 'pending':
            if f['from_id'] == user_id:
                pending.add(f['to_id'])
            elif f['to_id'] == user_id:
                pending.add(f['from_id'])

    exclude = current_friends.union(pending).union({user_id})

    # Thông tin user hiện tại
    current_user = next((u for u in users if u['id'] == user_id), None)
    if not current_user:
        return jsonify({'suggestions': []})

    # Đếm bạn chung
    friend_map = {}
    for f in friends:
        if f['status'] == 'accepted':
            friend_map.setdefault(f['from_id'], set()).add(f['to_id'])
            friend_map.setdefault(f['to_id'], set()).add(f['from_id'])

    mutual_counts = Counter()
    for uid in all_user_ids:
        if uid in exclude:
            continue
        mutual = friend_map.get(user_id, set()).intersection(friend_map.get(uid, set()))
        mutual_counts[uid] = len(mutual)

    # Tính điểm đề xuất
    suggestions = []
    for u in users:
        uid = u['id']
        if uid in exclude:
            continue
        score = 0
        if u.get('location') == current_user.get('location'):
            score += 1
        score += mutual_counts[uid]
        suggestions.append({'id': uid, 'name': u.get('name'), 'score': score})

    # Sắp xếp theo điểm
    suggestions.sort(key=lambda x: x['score'], reverse=True)
    return jsonify({'suggestions': suggestions})
