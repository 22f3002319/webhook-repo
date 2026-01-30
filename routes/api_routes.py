"""
API Routes
Handles frontend API requests for fetching events
"""

from flask import Blueprint, request, jsonify, send_from_directory
import logging
from datetime import datetime
from services.event_service import EventService

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/events', methods=['GET'])
def get_events():
    """
    API endpoint to fetch latest events
    Supports optional 'since' parameter for polling
    """
    try:
        # Get optional 'since' parameter (ISO format timestamp)
        since_param = request.args.get('since')
        since = None
        
        if since_param:
            try:
                since = datetime.fromisoformat(since_param.replace('Z', '+00:00'))
            except ValueError:
                logger.warning(f"Invalid 'since' parameter: {since_param}")
                # Continue without since filter
        
        # Get limit parameter (default 50)
        limit = int(request.args.get('limit', 50))
        
        # Fetch events
        events = EventService.get_latest_events(limit=limit, since=since)
        
        return jsonify({
            'success': True,
            'events': events,
            'count': len(events)
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching events: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch events'
        }), 500

@api_bp.route('/', methods=['GET'])
def index():
    """Serve the main HTML page"""
    from flask import current_app
    import os
    try:
        return current_app.send_static_file('index.html')
    except Exception as e:
        # Fallback if static file not found
        return f"""
        <html>
        <head><title>GitHub Webhook Monitor</title></head>
        <body>
            <h1>GitHub Webhook Events Monitor</h1>
            <p>Application is running but static files may not be configured correctly.</p>
            <p>Error: {str(e)}</p>
            <p>API endpoint: <a href="/api/events">/api/events</a></p>
            <p>Webhook endpoint: <a href="/webhook">/webhook</a></p>
        </body>
        </html>
        """, 200
