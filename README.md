# GitHub Webhook Receiver - Flask Backend

A production-ready Flask application that receives GitHub webhook events, normalizes the data, stores it in MongoDB Atlas, and serves a real-time polling-based UI.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [GitHub Webhook Setup](#github-webhook-setup)
- [Testing](#testing)
- [Application Flow](#application-flow)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

This application implements a complete GitHub webhook receiver system that:

1. **Receives** GitHub webhook events via POST endpoint
2. **Verifies** webhook signatures for security
3. **Parses** and normalizes event data (PUSH, PULL_REQUEST, MERGE)
4. **Stores** structured data in MongoDB Atlas
5. **Serves** a polling-based UI that displays real-time updates

## 🏗️ Architecture

```
GitHub Repository (action-repo)
    ↓ (Webhook POST)
Flask Backend (/webhook endpoint)
    ↓ (Parse & Normalize)
MongoDB Atlas (Store Events)
    ↓ (Poll every 15s)
Frontend UI (/api/events endpoint)
    ↓ (Display)
Real-time Event Monitor
```

### Data Flow

1. **GitHub Event Trigger**: User performs action (push, PR, merge) in `action-repo`
2. **Webhook Delivery**: GitHub sends POST request to `/webhook` endpoint
3. **Signature Verification**: Backend verifies request authenticity using HMAC
4. **Event Parsing**: Service layer extracts and normalizes required fields
5. **Data Storage**: Event saved to MongoDB with unique `request_id` to prevent duplicates
6. **UI Polling**: Frontend polls `/api/events` every 15 seconds
7. **Display**: New events rendered with formatted messages

## ✨ Features

- ✅ Secure webhook signature verification
- ✅ Support for PUSH, PULL_REQUEST, and MERGE events
- ✅ MongoDB Atlas integration with indexing
- ✅ Duplicate event prevention
- ✅ Real-time polling UI (15-second intervals)
- ✅ Clean, modular code structure
- ✅ Comprehensive error handling
- ✅ Production-ready logging
- ✅ UTC timestamp handling
- ✅ No duplicate UI rendering

## 📦 Prerequisites

- Python 3.8+
- MongoDB Atlas account (free tier available)
- GitHub account with repository access
- ngrok or similar tool for local webhook testing (optional)

## 🚀 Setup Instructions

### Step 1: Clone and Navigate

```bash
git clone <your-webhook-repo-url>
cd webhook-repo
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: MongoDB Atlas Setup

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free cluster
3. Create a database user (Database Access)
4. Whitelist your IP address (Network Access)
5. Get your connection string:
   - Click "Connect" → "Connect your application"
   - Copy the connection string
   - Format: `mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority`

### Step 5: Environment Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your values:
   ```env
   SECRET_KEY=your-random-secret-key-here
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
   MONGODB_DB_NAME=github_webhooks
   GITHUB_WEBHOOK_SECRET=your-github-webhook-secret
   ```

### Step 6: Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

### Step 7: Expose for Webhooks (Local Development)

For local testing, use ngrok to expose your local server:

```bash
ngrok http 5000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`) - you'll need this for GitHub webhook configuration.

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Flask secret key for sessions | Yes |
| `MONGODB_URI` | MongoDB Atlas connection string | Yes |
| `MONGODB_DB_NAME` | Database name | Yes (default: github_webhooks) |
| `GITHUB_WEBHOOK_SECRET` | GitHub webhook secret for verification | Recommended |

### MongoDB Indexes

The application automatically creates the following indexes:

- **timestamp** (descending): For efficient sorting
- **request_id** (unique): Prevents duplicate events
- **author + timestamp**: Compound index for author queries

## 📁 Project Structure

```
webhook-repo/
├── app.py                      # Flask application entry point
├── config.py                   # Configuration management
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
│
├── db/
│   ├── __init__.py
│   └── mongodb.py              # MongoDB connection and utilities
│
├── routes/
│   ├── __init__.py
│   ├── webhook_routes.py       # Webhook endpoint handler
│   └── api_routes.py           # API endpoints for frontend
│
├── services/
│   ├── __init__.py
│   ├── github_webhook_service.py  # Webhook parsing and verification
│   └── event_service.py          # Event storage and retrieval
│
├── static/
│   ├── index.html              # Frontend HTML
│   ├── styles.css              # Frontend CSS
│   └── app.js                  # Frontend JavaScript (polling logic)
│
└── utils/
    └── __init__.py
```

## 🔌 API Endpoints

### POST `/webhook`

Receives GitHub webhook events.

**Headers:**
- `X-GitHub-Event`: Event type (push, pull_request, etc.)
- `X-Hub-Signature-256`: HMAC signature for verification

**Response:**
```json
{
  "message": "Event processed successfully",
  "event_id": "abc1234"
}
```

### GET `/api/events`

Fetches events for the frontend.

**Query Parameters:**
- `since` (optional): ISO timestamp to fetch events after this time
- `limit` (optional): Maximum number of events (default: 50)

**Response:**
```json
{
  "success": true,
  "events": [
    {
      "_id": "...",
      "request_id": "abc1234",
      "author": "username",
      "action": "PUSH",
      "from_branch": null,
      "to_branch": "main",
      "timestamp": "2024-01-15T10:30:00+00:00"
    }
  ],
  "count": 1
}
```

### GET `/`

Serves the main HTML page with the event monitor UI.

## 🔗 GitHub Webhook Setup

### Step 1: Navigate to Repository Settings

1. Go to your `action-repo` repository on GitHub
2. Click **Settings** → **Webhooks**
3. Click **Add webhook**

### Step 2: Configure Webhook

- **Payload URL**: `https://your-domain.com/webhook` (or ngrok URL for local testing)
- **Content type**: `application/json`
- **Secret**: Generate a random secret (save this for `.env` file)
- **Events**: Select "Let me select individual events"
  - ✅ Pushes
  - ✅ Pull requests
- **Active**: ✅ Checked

### Step 3: Save and Test

Click **Add webhook**. GitHub will send a test ping - check your Flask logs to verify receipt.

## 🧪 Testing

### Test PUSH Event

```bash
# In action-repo
echo "Test push" >> sample-file.txt
git add .
git commit -m "Test push event"
git push origin main
```

**Expected Result:**
- Webhook received in Flask logs
- Event stored in MongoDB
- UI displays: `{author} pushed to {branch} on {timestamp}`

### Test PULL_REQUEST Event

```bash
# In action-repo
git checkout -b feature/test-pr
echo "PR changes" >> sample-file.txt
git add .
git commit -m "Test PR"
git push origin feature/test-pr
```

Then create a PR on GitHub from `feature/test-pr` to `main`.

**Expected Result:**
- UI displays: `{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}`

### Test MERGE Event

Merge the pull request created above through GitHub's web interface.

**Expected Result:**
- UI displays: `{author} merged branch {from_branch} to {to_branch} on {timestamp}`

### Verify MongoDB

Connect to MongoDB Atlas and check the `events` collection:

```javascript
use github_webhooks
db.events.find().sort({timestamp: -1}).limit(5)
```

## 🔄 Application Flow

### Complete Event Lifecycle

1. **Developer Action**: Developer pushes/creates PR/merges in `action-repo`
2. **GitHub Webhook**: GitHub sends POST to `/webhook` with event payload
3. **Signature Verification**: Backend verifies HMAC signature
4. **Event Parsing**: 
   - Extract: `request_id`, `author`, `action`, `from_branch`, `to_branch`, `timestamp`
   - Normalize data structure
5. **Database Storage**: 
   - Check for duplicate `request_id`
   - Insert if new
   - Create indexes automatically
6. **Frontend Polling**: 
   - Every 15 seconds, fetch `/api/events?since={lastFetchTime}`
   - Filter out already-displayed events
   - Render new events with formatted messages
7. **UI Update**: New events appear at top of list

### Data Normalization

**PUSH Event:**
```json
{
  "request_id": "abc1234",      // Commit hash (short)
  "author": "username",          // Pusher name
  "action": "PUSH",
  "from_branch": null,           // Not applicable
  "to_branch": "main",
  "timestamp": "2024-01-15T10:30:00+00:00"
}
```

**PULL_REQUEST Event:**
```json
{
  "request_id": "42",            // PR number
  "author": "username",
  "action": "PULL_REQUEST",
  "from_branch": "feature-branch",
  "to_branch": "main",
  "timestamp": "2024-01-15T10:30:00+00:00"
}
```

**MERGE Event:**
```json
{
  "request_id": "42",            // PR number
  "author": "username",
  "action": "MERGE",
  "from_branch": "feature-branch",
  "to_branch": "main",
  "timestamp": "2024-01-15T10:35:00+00:00"  // merged_at time
}
```

## 🎯 Best Practices

### Security
- ✅ Webhook signature verification prevents unauthorized requests
- ✅ Environment variables for sensitive data
- ✅ Input validation and error handling
- ✅ CORS enabled for frontend requests

### Code Quality
- ✅ Modular structure (routes, services, db separation)
- ✅ Comprehensive docstrings and comments
- ✅ Clean variable naming
- ✅ Proper error handling and logging

### Data Integrity
- ✅ Unique `request_id` index prevents duplicates
- ✅ UTC timestamp storage
- ✅ Proper datetime handling
- ✅ Graceful handling of unsupported events

### Frontend
- ✅ No duplicate rendering (tracks displayed events)
- ✅ Efficient polling (only fetches new events)
- ✅ Clean, minimal UI design
- ✅ Proper date formatting

## 🐛 Troubleshooting

### Webhook Not Receiving Events

1. **Check GitHub Webhook Status**: Go to repository settings → Webhooks → Check delivery status
2. **Verify URL**: Ensure webhook URL is accessible (use ngrok for local testing)
3. **Check Flask Logs**: Look for incoming requests
4. **Verify Secret**: Ensure `GITHUB_WEBHOOK_SECRET` matches GitHub webhook secret

### MongoDB Connection Issues

1. **Check Connection String**: Verify `MONGODB_URI` format
2. **IP Whitelist**: Ensure your IP is whitelisted in MongoDB Atlas
3. **Credentials**: Verify username/password in connection string
4. **Network**: Check firewall/network restrictions

### Events Not Appearing in UI

1. **Check Browser Console**: Look for JavaScript errors
2. **Verify API Endpoint**: Test `/api/events` directly
3. **Check Polling**: Verify 15-second interval is working
4. **MongoDB Data**: Verify events are being stored

### Duplicate Events

- The `request_id` unique index should prevent this
- If duplicates appear, check MongoDB indexes: `db.events.getIndexes()`

## 📝 Sample GitHub Webhook Payloads

### PUSH Event Payload (Excerpt)

```json
{
  "ref": "refs/heads/main",
  "pusher": {
    "name": "username"
  },
  "commits": [
    {
      "id": "abc1234567890",
      "message": "Test commit",
      "timestamp": "2024-01-15T10:30:00Z",
      "author": {
        "name": "username"
      }
    }
  ]
}
```

### PULL_REQUEST Event Payload (Excerpt)

```json
{
  "action": "opened",
  "pull_request": {
    "number": 42,
    "user": {
      "login": "username"
    },
    "head": {
      "ref": "feature-branch"
    },
    "base": {
      "ref": "main"
    },
    "created_at": "2024-01-15T10:30:00Z",
    "merged": false,
    "merged_at": null
  }
}
```

## 📋 Submission Checklist

- [x] Two separate repositories created (`action-repo` and `webhook-repo`)
- [x] Flask backend with `/webhook` endpoint
- [x] GitHub webhook signature verification
- [x] PUSH, PULL_REQUEST, and MERGE event handling
- [x] MongoDB Atlas integration with proper schema
- [x] Frontend with 15-second polling
- [x] Proper data formatting and display
- [x] No duplicate event rendering
- [x] Comprehensive documentation
- [x] Clean, modular code structure
- [x] Environment variable configuration
- [x] Error handling and logging

## 📚 Additional Resources

- [GitHub Webhooks Documentation](https://docs.github.com/en/developers/webhooks-and-events/webhooks)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [MongoDB Atlas Documentation](https://docs.atlas.mongodb.com/)
- [PyMongo Documentation](https://pymongo.readthedocs.io/)

## 📄 License

This project is created for educational and assessment purposes.

---

**Built with ❤️ for production-ready webhook handling**
