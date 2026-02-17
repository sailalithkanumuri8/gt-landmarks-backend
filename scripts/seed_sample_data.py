"""
Seed sample users and visits data into MongoDB.

Usage:
    python3 scripts/seed_sample_data.py
"""

import os
import sys
from pymongo import MongoClient
from datetime import datetime, timedelta
from dotenv import load_dotenv
from bson import ObjectId

# Load .env from project root
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Configuration
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = 'gt_landmarks'


def connect_db():
    """Connect to MongoDB and return db handle."""
    client = MongoClient(MONGO_URI)
    client.admin.command('ping')
    db = client[DB_NAME]
    return client, db


def seed_sample_data():
    """Add sample users and visits."""
    try:
        client, db = connect_db()
        print("✓ Connected to MongoDB")
    except Exception as e:
        print(f"✗ Could not connect to MongoDB: {e}")
        sys.exit(1)

    users_collection = db['users']
    landmarks_collection = db['landmarks']
    visits_collection = db['visits']

    # Get all landmarks
    landmarks = list(landmarks_collection.find())
    if not landmarks:
        print("✗ No landmarks found. Please run import_local_data.py first.")
        sys.exit(1)

    landmark_map = {lm['name']: lm['_id'] for lm in landmarks}
    print(f"\n✓ Found {len(landmarks)} landmarks")

    # Sample users data
    sample_users = [
        {
            'username': 'alice_johnson',
            'email': 'alice.johnson@gatech.edu',
            'created_at': datetime.utcnow() - timedelta(days=30)
        },
        {
            'username': 'bob_smith',
            'email': 'bob.smith@gatech.edu',
            'created_at': datetime.utcnow() - timedelta(days=25)
        },
        {
            'username': 'carol_williams',
            'email': 'carol.williams@gatech.edu',
            'created_at': datetime.utcnow() - timedelta(days=20)
        },
        {
            'username': 'david_brown',
            'email': 'david.brown@gatech.edu',
            'created_at': datetime.utcnow() - timedelta(days=15)
        },
        {
            'username': 'emma_davis',
            'email': 'emma.davis@gatech.edu',
            'created_at': datetime.utcnow() - timedelta(days=10)
        }
    ]

    print("\n" + "=" * 60)
    print("Creating Sample Users...")
    print("=" * 60)

    created_users = []
    for user_data in sample_users:
        # Check if user already exists
        existing = users_collection.find_one({'email': user_data['email']})
        if existing:
            print(f"✓ User already exists: {user_data['username']}")
            created_users.append(existing)
        else:
            result = users_collection.insert_one(user_data)
            user_data['_id'] = result.inserted_id
            created_users.append(user_data)
            print(f"✓ Created user: {user_data['username']}")

    # Sample visits data - each user visits different landmarks
    sample_visits = [
        # Alice visits 4 landmarks
        {'user': 'alice_johnson', 'landmark': 'Tech Tower', 'notes': 'Beautiful historic building!', 'days_ago': 28},
        {'user': 'alice_johnson', 'landmark': 'Clough Undergraduate Learning Commons', 'notes': 'Great study space', 'days_ago': 25},
        {'user': 'alice_johnson', 'landmark': 'Bobby Dodd Stadium', 'notes': 'Go Jackets!', 'days_ago': 20},
        {'user': 'alice_johnson', 'landmark': 'McCamish Pavilion', 'notes': 'Awesome basketball game', 'days_ago': 15},
        
        # Bob visits 3 landmarks
        {'user': 'bob_smith', 'landmark': 'Tech Tower', 'notes': 'Iconic GT landmark', 'days_ago': 23},
        {'user': 'bob_smith', 'landmark': 'Kendeda Building', 'notes': 'Amazing sustainable design', 'days_ago': 18},
        {'user': 'bob_smith', 'landmark': 'Bobby Dodd Stadium', 'notes': 'Great atmosphere on game day', 'days_ago': 12},
        
        # Carol visits 5 landmarks (all of them!)
        {'user': 'carol_williams', 'landmark': 'Tech Tower', 'notes': 'Must-see for every Yellow Jacket', 'days_ago': 19},
        {'user': 'carol_williams', 'landmark': 'Clough Undergraduate Learning Commons', 'notes': 'Love the modern architecture', 'days_ago': 17},
        {'user': 'carol_williams', 'landmark': 'Kendeda Building', 'notes': 'Living Building certified!', 'days_ago': 14},
        {'user': 'carol_williams', 'landmark': 'Bobby Dodd Stadium', 'notes': 'Historic Grant Field', 'days_ago': 10},
        {'user': 'carol_williams', 'landmark': 'McCamish Pavilion', 'notes': 'State-of-the-art facility', 'days_ago': 5},
        
        # David visits 2 landmarks
        {'user': 'david_brown', 'landmark': 'Tech Tower', 'notes': 'Perfect spot for photos', 'days_ago': 13},
        {'user': 'david_brown', 'landmark': 'Clough Undergraduate Learning Commons', 'notes': 'Best place to collaborate', 'days_ago': 8},
        
        # Emma visits 3 landmarks
        {'user': 'emma_davis', 'landmark': 'Kendeda Building', 'notes': 'So impressed by the green features', 'days_ago': 9},
        {'user': 'emma_davis', 'landmark': 'Bobby Dodd Stadium', 'notes': 'First football game - amazing!', 'days_ago': 6},
        {'user': 'emma_davis', 'landmark': 'McCamish Pavilion', 'notes': 'Great venue for basketball', 'days_ago': 3},
    ]

    print("\n" + "=" * 60)
    print("Creating Sample Visits...")
    print("=" * 60)

    user_map = {user['username']: user['_id'] for user in created_users}
    visits_created = 0

    for visit_data in sample_visits:
        user_id = user_map[visit_data['user']]
        landmark_id = landmark_map[visit_data['landmark']]
        
        # Check if visit already exists
        existing = visits_collection.find_one({
            'user_id': user_id,
            'landmark_id': landmark_id
        })
        
        if existing:
            print(f"  ↳ Visit already exists: {visit_data['user']} → {visit_data['landmark']}")
        else:
            visit = {
                'user_id': user_id,
                'landmark_id': landmark_id,
                'visited_at': datetime.utcnow() - timedelta(days=visit_data['days_ago']),
                'notes': visit_data['notes']
            }
            visits_collection.insert_one(visit)
            print(f"  ✓ {visit_data['user']} visited {visit_data['landmark']}")
            visits_created += 1

    print("\n" + "=" * 60)
    print("✓ Sample Data Seeding Complete!")
    print("=" * 60)
    print(f"  Users: {len(created_users)}")
    print(f"  New Visits: {visits_created}")
    print(f"  Total Visits: {visits_collection.count_documents({})}")
    print()
    
    # Show summary per user
    print("User Visit Summary:")
    for user in created_users:
        visit_count = visits_collection.count_documents({'user_id': user['_id']})
        visited_landmarks = []
        for visit in visits_collection.find({'user_id': user['_id']}):
            landmark = landmarks_collection.find_one({'_id': visit['landmark_id']})
            if landmark:
                visited_landmarks.append(landmark['name'])
        print(f"  • {user['username']}: {visit_count} visits")
        for lm_name in visited_landmarks:
            print(f"    - {lm_name}")

    client.close()


if __name__ == '__main__':
    seed_sample_data()
