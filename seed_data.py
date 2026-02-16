"""Seed MongoDB with GT landmarks data"""

from pymongo import MongoClient
import os
from datetime import datetime
from dotenv import load_dotenv
from image_urls import TECH_TOWER_IMAGES, CULC_IMAGES

load_dotenv()

# MongoDB setup
client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/'))
db = client['gt_landmarks']
landmarks_collection = db['landmarks']
users_collection = db['users']
visits_collection = db['visits']


def clear_database():
    """Clear all collections"""
    print("Clearing database...")
    landmarks_collection.delete_many({})
    users_collection.delete_many({})
    visits_collection.delete_many({})
    print("✓ Cleared")


def seed_landmarks():
    """Add landmarks with training images"""
    print("\nSeeding landmarks...")
    
    landmarks = [
        {
            'name': 'Tech Tower',
            'full_name': 'Tech Tower',
            'description': 'The iconic administration building and symbol of Georgia Tech since 1888.',
            'location': {'latitude': 33.7756, 'longitude': -84.3985},
            'fun_facts': [
                'Built in 1888',
                'Originally called the Academic Building',
                'Famous for the "Stealing the T" tradition',
                'Listed on the National Register of Historic Places'
            ],
            'training_images': TECH_TOWER_IMAGES,
            'thumbnail_url': TECH_TOWER_IMAGES[0]['url'],
            'created_at': datetime.utcnow()
        },
        {
            'name': 'CULC',
            'full_name': 'Clough Undergraduate Learning Commons',
            'description': 'A modern learning and collaboration space at the heart of campus.',
            'location': {'latitude': 33.7749, 'longitude': -84.3963},
            'fun_facts': [
                'Opened in 2011',
                'Named after G. Wayne Clough, former GT President',
                'Features a 3-story glass facade',
                'Open 24 hours a day'
            ],
            'training_images': CULC_IMAGES,
            'thumbnail_url': CULC_IMAGES[0]['url'],
            'created_at': datetime.utcnow()
        }
    ]
    
    result = landmarks_collection.insert_many(landmarks)
    print(f"✓ Added {len(result.inserted_ids)} landmarks")
    print(f"  - Tech Tower: {len(TECH_TOWER_IMAGES)} images")
    print(f"  - CULC: {len(CULC_IMAGES)} images")
    return result.inserted_ids


def seed_users():
    """Add sample users"""
    print("\nSeeding users...")
    
    users = [
        {'username': 'buzz', 'email': 'buzz@gatech.edu', 'created_at': datetime.utcnow()},
        {'username': 'ramblin_wreck', 'email': 'wreck@gatech.edu', 'created_at': datetime.utcnow()}
    ]
    
    result = users_collection.insert_many(users)
    print(f"✓ Added {len(result.inserted_ids)} users")
    return result.inserted_ids


def seed_visits(landmark_ids, user_ids):
    """Add sample visits"""
    print("\nSeeding visits...")
    
    visits = [
        {
            'user_id': user_ids[0],
            'landmark_id': landmark_ids[0],
            'visited_at': datetime.utcnow(),
            'notes': 'Amazing historic building!'
        },
        {
            'user_id': user_ids[0],
            'landmark_id': landmark_ids[1],
            'visited_at': datetime.utcnow(),
            'notes': 'Great study spot!'
        },
        {
            'user_id': user_ids[1],
            'landmark_id': landmark_ids[0],
            'visited_at': datetime.utcnow(),
            'notes': 'Love the architecture'
        }
    ]
    
    result = visits_collection.insert_many(visits)
    print(f"✓ Added {len(result.inserted_ids)} visits")


def main():
    print("="*50)
    print("GT LANDMARKS DATABASE SEEDING")
    print("="*50)
    
    try:
        client.admin.command('ping')
        print("✓ Connected to MongoDB")
        
        clear_database()
        landmark_ids = seed_landmarks()
        user_ids = seed_users()
        seed_visits(landmark_ids, user_ids)
        
        print("\n" + "="*50)
        print("✓ SEEDING COMPLETE!")
        print("="*50)
        print(f"\nTotal: {len(TECH_TOWER_IMAGES) + len(CULC_IMAGES)} training images")
        print("\nRun: python app.py")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nCheck:")
        print("  1. MongoDB is running")
        print("  2. MONGO_URI in .env is correct")
    finally:
        client.close()


if __name__ == '__main__':
    main()
