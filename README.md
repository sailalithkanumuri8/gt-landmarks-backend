# GT Landmarks Backend

Flask backend for a Georgia Tech landmarks image classification project.

## What's Included

- Flask REST API with pandas/numpy
- 223 training images across 5 GT landmarks
- MongoDB for landmarks, users, and visits
- Sample users with visit history
- Analytics endpoints with top landmarks and users

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd gt-landmarks-backend
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure MongoDB
Create a `.env` file in the project root:

### 3. Seed Database
```bash
# Import landmark images from data/ folder
python3 scripts/import_local_data.py

# Add sample users and visits
python3 scripts/seed_sample_data.py
```

### 6. Run the Server
```bash
python3 app.py
```

Server runs at `http://localhost:5001`

## API Endpoints

**Landmarks**
- `GET /api/landmarks` - All landmarks with stats
- `GET /api/landmarks/<id>` - Specific landmark

**Users**
- `POST /api/users` - Create user
- `GET /api/users` - All users
- `GET /api/users/<id>` - Specific user

**Visits**
- `POST /api/visits` - Record visit
- `GET /api/users/<id>/visits` - User's visits
- `GET /api/landmarks/<id>/visitors` - Landmark visitors

**Analytics**
- `GET /api/analytics` - Summary stats with top landmarks and users

**Images**
- `GET /api/images/<path>` - Serve images from GridFS

**Health**
- `GET /api/health` - Status check

## Quick Test

```bash
curl http://localhost:5001/api/health
curl http://localhost:5001/api/landmarks
curl http://localhost:5001/api/analytics
```

## Dataset

**Landmarks:**
- Bobby Dodd Stadium: 50 images
- Clough Undergraduate Learning Commons (CULC): 50 images
- Kendeda Building: 50 images
- McCamish Pavilion: 50 images
- Tech Tower: 23 images
- **Total: 223 images across 5 landmarks**

**Sample Users:**
- alice_johnson (4 visits)
- bob_smith (3 visits)
- carol_williams (5 visits - visited all landmarks!)
- david_brown (2 visits)
- emma_davis (3 visits)

## Tech Stack

- Flask 3.0.0
- MongoDB with GridFS
- Pandas 2.2.0
- Numpy 1.26.3
- Python 3.11+
