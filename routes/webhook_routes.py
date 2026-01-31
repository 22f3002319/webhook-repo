"""
Webhook Routes
Handles GitHub webhook endpoint
"""

from flask import Blueprint, request, jsonify, current_app
import logging
from datetime import datetime
from services.github_webhook_service import GitHubWebhookService
from services.event_service import EventService

logger = logging.getLogger(__name__)

webhook_bp = Blueprint('webhook', __name__)

@webhook_bp.route('/webhook', methods=['POST'])
def webhook():
    """
    GitHub webhook endpoint
    Receives and processes GitHub webhook events
    """
    try:
        # Get event type from headers
        event_type = request.headers.get('X-GitHub-Event')
        
        if not event_type:
            logger.warning("Missing X-GitHub-Event header")
            return jsonify({'error': 'Missing event type'}), 400
        
        # Get signature for verification
        signature = request.headers.get('X-Hub-Signature-256', '')
        secret = current_app.config.get('GITHUB_WEBHOOK_SECRET', '')
        
        # Verify webhook signature
        if not GitHubWebhookService.verify_signature(
            request.data,
            signature,
            secret
        ):
            logger.warning("Invalid webhook signature")
            return jsonify({'error': 'Invalid signature'}), 401
        
        # Parse JSON payload
        try:
            payload = request.get_json()
        except Exception as e:
            logger.error(f"Error parsing JSON payload: {e}")
            return jsonify({'error': 'Invalid JSON payload'}), 400
        
        if not payload:
            return jsonify({'error': 'Empty payload'}), 400
        
        # Parse event based on type
        event_data = GitHubWebhookService.parse_webhook_event(payload, event_type)
        
        if not event_data:
            # Unsupported event type - return success but don't process
            logger.info(f"Unsupported event type: {event_type}")
            return jsonify({'message': 'Event type not processed'}), 200
        
        # Save event to MongoDB
        success = EventService.save_event(event_data)
        
        if success:
            logger.info(f"Successfully processed {event_type} event: {event_data.get('request_id')}")
            return jsonify({
                'message': 'Event processed successfully',
                'event_id': event_data.get('request_id')
            }), 200
        else:
            # Event might be duplicate, but return success
            return jsonify({
                'message': 'Event received (may be duplicate)',
                'event_id': event_data.get('request_id')
            }), 200
            
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@webhook_bp.route('/webhook', methods=['GET'])
def webhook_info():
    """Provide webhook endpoint information"""
    return jsonify({
        'message': 'GitHub Webhook Endpoint',
        'method': 'POST',
        'events': ['push', 'pull_request'],
        'status': 'active'
    }), 200

@webhook_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for testing"""
    from flask import current_app
    from db.mongodb import client, db
    
    # Check MongoDB connection
    mongo_status = 'unknown'
    try:
        if client is None or db is None:
            mongo_status = 'not_initialized'
        else:
            # Try to ping MongoDB
            client.admin.command('ping')
            mongo_status = 'connected'
    except Exception as e:
        mongo_status = f'disconnected: {str(e)}'
    
    # Check if MongoDB URI is configured
    mongodb_uri = current_app.config.get('MONGODB_URI', '')
    if not mongodb_uri:
        mongo_status = 'not_configured'
    
    return jsonify({
        'status': 'ok',
        'service': 'GitHub Webhook Receiver',
        'mongodb': mongo_status,
        'mongodb_configured': bool(mongodb_uri),
        'timestamp': datetime.utcnow().isoformat()
    }), 200
