# GT Landmarks Backend

Flask backend for a Georgia Tech landmarks image classification workshop.

## What's Included

- Flask REST API with pandas/numpy
- 29 training images from Wikimedia Commons
- MongoDB for landmarks, users, and visits
- Analytics endpoints

## Setup

### 1. Install
```bash
pip install -r requirements.txt
```

### 2. Configure MongoDB
```bash
cp .env.example .env
# Edit .env with your MongoDB URI
```

### 3. Seed Database
```bash
python seed_data.py
```

### 4. Run
```bash
python app.py
```

Server runs at `http://localhost:5000`

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
- `GET /api/analytics` - Summary stats

**Health**
- `GET /api/health` - Status check

## Quick Test

```bash
curl http://localhost:5000/api/health
curl http://localhost:5000/api/landmarks
curl http://localhost:5000/api/analytics
```

## Dataset

- Tech Tower: 15 images
- CULC: 14 images
- All from Wikimedia Commons (CC0, CC BY-SA)

## Tech Stack

- Flask 3.0.0
- MongoDB
- Pandas 2.2.0
- Numpy 1.26.3

Go Jackets! 🐝💛
