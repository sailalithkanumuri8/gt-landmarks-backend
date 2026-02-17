from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import gridfs

load_dotenv()

app = Flask(__name__)
CORS(app)

# MongoDB setup
client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/'))
db = client['gt_landmarks']
landmarks_collection = db['landmarks']
users_collection = db['users']
visits_collection = db['visits']
fs = gridfs.GridFS(db)


def serialize(doc):
    """Convert MongoDB ObjectId fields to strings"""
    if doc:
        if '_id' in doc:
            doc['_id'] = str(doc['_id'])
        if 'user_id' in doc:
            doc['user_id'] = str(doc['user_id'])
        if 'landmark_id' in doc:
            doc['landmark_id'] = str(doc['landmark_id'])
    return doc


# ==================== LANDMARKS ====================

@app.route('/api/landmarks', methods=['GET'])
def get_landmarks():
    """Get all landmarks with stats"""
    landmarks = list(landmarks_collection.find())
    if not landmarks:
        return jsonify({'landmarks': []}), 200
    
    df = pd.DataFrame(landmarks)
    df['image_count'] = df['training_images'].apply(lambda x: len(x) if isinstance(x, list) else 0)
    
    visits = list(visits_collection.find())
    if visits:
        visits_df = pd.DataFrame(visits)
        visit_counts = visits_df.groupby('landmark_id').size().to_dict()
        df['visit_count'] = df['_id'].map(visit_counts).fillna(0).astype(int)
    else:
        df['visit_count'] = 0
    
    return jsonify({'landmarks': [serialize(lm) for lm in df.to_dict('records')]}), 200


@app.route('/api/landmarks/<landmark_id>', methods=['GET'])
def get_landmark(landmark_id):
    """Get specific landmark"""
    landmark = landmarks_collection.find_one({'_id': ObjectId(landmark_id)})
    if not landmark:
        return jsonify({'error': 'Not found'}), 404
    
    landmark['image_count'] = len(landmark.get('training_images', []))
    landmark['visit_count'] = visits_collection.count_documents({'landmark_id': ObjectId(landmark_id)})
    
    return jsonify({'landmark': serialize(landmark)}), 200


# ==================== USERS ====================

@app.route('/api/users', methods=['POST'])
def create_user():
    """Create new user"""
    data = request.json
    if not data.get('username') or not data.get('email'):
        return jsonify({'error': 'Username and email required'}), 400
    
    if users_collection.find_one({'email': data['email']}):
        return jsonify({'error': 'Email exists'}), 400
    
    user = {
        'username': data['username'],
        'email': data['email'],
        'created_at': datetime.utcnow()
    }
    result = users_collection.insert_one(user)
    user['_id'] = result.inserted_id
    
    return jsonify({'user': serialize(user)}), 201


@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users with stats"""
    users = list(users_collection.find())
    if not users:
        return jsonify({'users': []}), 200
    
    df = pd.DataFrame(users)
    visits = list(visits_collection.find())
    if visits:
        visits_df = pd.DataFrame(visits)
        visit_counts = visits_df.groupby('user_id').size().to_dict()
        df['visit_count'] = df['_id'].map(visit_counts).fillna(0).astype(int)
    else:
        df['visit_count'] = 0
    
    return jsonify({'users': [serialize(u) for u in df.to_dict('records')]}), 200


@app.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get specific user"""
    user = users_collection.find_one({'_id': ObjectId(user_id)})
    if not user:
        return jsonify({'error': 'Not found'}), 404
    
    user['visit_count'] = visits_collection.count_documents({'user_id': ObjectId(user_id)})
    return jsonify({'user': serialize(user)}), 200


# ==================== VISITS ====================

@app.route('/api/visits', methods=['POST'])
def record_visit():
    """Record a visit"""
    data = request.json
    if not data.get('user_id') or not data.get('landmark_id'):
        return jsonify({'error': 'user_id and landmark_id required'}), 400
    
    existing = visits_collection.find_one({
        'user_id': ObjectId(data['user_id']),
        'landmark_id': ObjectId(data['landmark_id'])
    })
    if existing:
        return jsonify({'message': 'Already recorded', 'visit': serialize(existing)}), 200
    
    visit = {
        'user_id': ObjectId(data['user_id']),
        'landmark_id': ObjectId(data['landmark_id']),
        'visited_at': datetime.utcnow(),
        'notes': data.get('notes', '')
    }
    result = visits_collection.insert_one(visit)
    visit['_id'] = result.inserted_id
    
    return jsonify({'visit': serialize(visit)}), 201


@app.route('/api/users/<user_id>/visits', methods=['GET'])
def get_user_visits(user_id):
    """Get user's visits"""
    visits = list(visits_collection.find({'user_id': ObjectId(user_id)}))
    if not visits:
        return jsonify({'visits': []}), 200
    
    result = []
    for visit in visits:
        landmark = landmarks_collection.find_one({'_id': visit['landmark_id']})
        if landmark:
            result.append({
                'visit_id': str(visit['_id']),
                'landmark': serialize(landmark),
                'visited_at': visit['visited_at'].isoformat(),
                'notes': visit.get('notes', '')
            })
    
    return jsonify({'visits': result}), 200


@app.route('/api/landmarks/<landmark_id>/visitors', methods=['GET'])
def get_landmark_visitors(landmark_id):
    """Get landmark visitors"""
    visits = list(visits_collection.find({'landmark_id': ObjectId(landmark_id)}))
    if not visits:
        return jsonify({'visitors': []}), 200
    
    result = []
    for visit in visits:
        user = users_collection.find_one({'_id': visit['user_id']})
        if user:
            result.append({
                'visit_id': str(visit['_id']),
                'user': serialize(user),
                'visited_at': visit['visited_at'].isoformat(),
                'notes': visit.get('notes', '')
            })
    
    return jsonify({'visitors': result}), 200


# ==================== ANALYTICS ====================

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get analytics summary"""
    landmarks = list(landmarks_collection.find())
    users = list(users_collection.find())
    visits = list(visits_collection.find())
    
    analytics = {
        'total_landmarks': len(landmarks),
        'total_users': len(users),
        'total_visits': len(visits)
    }
    
    if landmarks:
        image_counts = [len(lm.get('training_images', [])) for lm in landmarks]
        analytics['total_images'] = int(np.sum(image_counts))
        analytics['avg_images_per_landmark'] = float(np.mean(image_counts))
    
    if visits:
        visits_df = pd.DataFrame(visits)
        
        # Most visited landmarks
        top_landmarks = []
        for landmark_id, count in visits_df['landmark_id'].value_counts().head(5).items():
            landmark = landmarks_collection.find_one({'_id': landmark_id})
            if landmark:
                top_landmarks.append({'name': landmark['name'], 'visits': int(count)})
        analytics['top_landmarks'] = top_landmarks
        
        # Most active users
        top_users = []
        for user_id, count in visits_df['user_id'].value_counts().head(5).items():
            user = users_collection.find_one({'_id': user_id})
            if user:
                top_users.append({'username': user['username'], 'visits': int(count)})
        analytics['top_users'] = top_users
    
    return jsonify({'analytics': analytics}), 200


# ==================== IMAGES ====================

@app.route('/api/images/<path:filename>')
def get_image(filename):
    """Serve image stored in GridFS"""
    try:
        grid_file = fs.find_one({'filename': filename})
        if not grid_file:
            return jsonify({'error': 'Image not found'}), 404

        content_type = grid_file.content_type or 'application/octet-stream'
        return Response(
            grid_file.read(),
            mimetype=content_type,
            headers={'Cache-Control': 'public, max-age=86400'}
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({'status': 'ok'}), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

