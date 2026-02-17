"""
Import local image data into MongoDB using GridFS.

Usage:
    python scripts/import_local_data.py

Expects a 'data/' folder at project root with subfolder per landmark:
    data/
    ├── bobby_dodd/
    │   ├── Image_1.jpg
    │   └── ...
    ├── culc/
    │   └── ...
    └── tech_tower/
        └── ...
"""

import os
import sys
import mimetypes
from urllib.parse import quote
from pymongo import MongoClient
import gridfs
from datetime import datetime
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Configuration
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = 'gt_landmarks'
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

# Human-readable landmark names (folder name -> display name)
LANDMARK_NAMES = {
    'bobby_dodd': 'Bobby Dodd Stadium',
    'culc': 'Clough Undergraduate Learning Commons',
    'kendeda': 'Kendeda Building',
    'mccamish': 'McCamish Pavilion',
    'tech_tower': 'Tech Tower',
}

# Descriptions for each landmark
LANDMARK_DESCRIPTIONS = {
    'bobby_dodd': 'Bobby Dodd Stadium at Historic Grant Field is the football stadium for Georgia Tech.',
    'culc': 'A modern learning and collaboration space at the heart of campus, opened in 2011.',
    'kendeda': 'The Kendeda Building for Innovative Sustainable Design is a Living Building on campus.',
    'mccamish': 'McCamish Pavilion is the home arena for Georgia Tech Yellow Jackets basketball.',
    'tech_tower': 'The iconic administration building and symbol of Georgia Tech since 1888.',
}


def connect_db():
    """Connect to MongoDB and return db handle + GridFS handle."""
    client = MongoClient(MONGO_URI)
    # Quick connectivity check
    client.admin.command('ping')
    db = client[DB_NAME]
    return client, db, gridfs.GridFS(db)


def import_data():
    data_dir = os.path.abspath(DATA_DIR)

    if not os.path.exists(data_dir):
        print(f"✗ Error: Data directory not found at: {data_dir}")
        print("  Please create a 'data/' folder with landmark subfolders.")
        sys.exit(1)

    try:
        client, db, fs = connect_db()
        print("✓ Connected to MongoDB")
    except Exception as e:
        print(f"✗ Could not connect to MongoDB: {e}")
        print("  Check that MongoDB is running and MONGO_URI in .env is correct.")
        sys.exit(1)

    landmarks_collection = db['landmarks']

    print(f"\nScanning '{data_dir}' for landmarks...\n")
    print("=" * 60)

    total_images = 0
    total_landmarks = 0

    # Sort for consistent ordering
    for folder_name in sorted(os.listdir(data_dir)):
        folder_path = os.path.join(data_dir, folder_name)

        # Skip non-directories and hidden folders
        if not os.path.isdir(folder_path) or folder_name.startswith('.'):
            continue

        display_name = LANDMARK_NAMES.get(folder_name, folder_name.replace('_', ' ').title())
        description = LANDMARK_DESCRIPTIONS.get(folder_name, f'A landmark at Georgia Tech.')

        print(f"📍 {display_name} (folder: {folder_name})")

        # Upsert landmark document
        landmark_doc = landmarks_collection.find_one({'name': display_name})
        if landmark_doc:
            landmark_id = landmark_doc['_id']
            print(f"   Found existing document")
        else:
            landmark_doc = {
                'name': display_name,
                'full_name': display_name,
                'description': description,
                'location': {},
                'fun_facts': [],
                'training_images': [],
                'thumbnail_url': '',
                'created_at': datetime.utcnow()
            }
            result = landmarks_collection.insert_one(landmark_doc)
            landmark_id = result.inserted_id
            print(f"   Created new document")

        # Collect and upload images
        image_entries = []
        image_files = sorted(os.listdir(folder_path))

        for filename in image_files:
            if filename.startswith('.'):
                continue

            file_path = os.path.join(folder_path, filename)

            # Check if it's actually an image
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type or not mime_type.startswith('image'):
                print(f"   ⚠ Skipping non-image: {filename}")
                continue

            # Use landmark folder + filename for unique GridFS key
            gridfs_filename = f"{folder_name}/{filename}"

            # Check for duplicate
            existing = fs.find_one({'filename': gridfs_filename})
            if existing:
                print(f"   ↳ Already in GridFS: {filename}")
            else:
                with open(file_path, 'rb') as f:
                    fs.put(
                        f,
                        filename=gridfs_filename,
                        content_type=mime_type,
                        landmark_name=display_name,
                    )
                print(f"   ↳ Uploaded: {filename}")

            # Build the URL - encode the filename for safe URL usage
            encoded_filename = quote(gridfs_filename, safe='/')
            url = f"/api/images/{encoded_filename}"
            image_entries.append({
                'url': url,
                'description': filename,
                'content_type': mime_type,
            })

        # Update landmark document
        if image_entries:
            update_fields = {
                'training_images': image_entries,
                'thumbnail_url': image_entries[0]['url'],
            }
            landmarks_collection.update_one(
                {'_id': landmark_id},
                {'$set': update_fields}
            )
            print(f"   ✓ {len(image_entries)} images linked")
            total_images += len(image_entries)
        else:
            print(f"   ⚠ No images found")

        total_landmarks += 1
        print()

    print("=" * 60)
    print(f"✓ Import complete!")
    print(f"  Landmarks: {total_landmarks}")
    print(f"  Images:    {total_images}")
    print(f"\n  Run: python app.py")
    print(f"  Then visit: http://localhost:5000/api/landmarks")

    client.close()


if __name__ == '__main__':
    import_data()
