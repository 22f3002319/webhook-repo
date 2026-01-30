"""
GitHub Webhook Service
Handles GitHub webhook payload parsing and data normalization
"""

import hmac
import hashlib
import json
import logging
from datetime import datetime
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

class GitHubWebhookService:
    """Service class for processing GitHub webhook events"""
    
    @staticmethod
    def verify_signature(payload_body: bytes, signature_header: str, secret: str) -> bool:
        """
        Verify GitHub webhook signature to ensure request authenticity
        
        Args:
            payload_body: Raw request body as bytes
            signature_header: X-Hub-Signature-256 header value
            secret: GitHub webhook secret
            
        Returns:
            True if signature is valid, False otherwise
        """
        if not secret:
            logger.warning("GitHub webhook secret not configured. Skipping signature verification.")
            return True  # Allow in development, but should be False in production
        
        if not signature_header:
            logger.warning("Missing signature header")
            return False
        
        try:
            # GitHub sends signature as "sha256=<hash>"
            hash_object = hmac.new(
                secret.encode('utf-8'),
                msg=payload_body,
                digestmod=hashlib.sha256
            )
            expected_signature = "sha256=" + hash_object.hexdigest()
            
            # Use constant-time comparison to prevent timing attacks
            return hmac.compare_digest(expected_signature, signature_header)
        except Exception as e:
            logger.error(f"Error verifying signature: {e}")
            return False
    
    @staticmethod
    def parse_push_event(payload: Dict) -> Optional[Dict]:
        """
        Parse GitHub push event payload
        
        Args:
            payload: GitHub webhook payload dictionary
            
        Returns:
            Normalized event data dictionary or None if parsing fails
        """
        try:
            # Extract commit information
            commits = payload.get('commits', [])
            if not commits:
                logger.warning("Push event with no commits")
                return None
            
            # Use the first commit (most recent)
            commit = commits[0]
            
            # Extract branch information
            ref = payload.get('ref', '')
            branch = ref.replace('refs/heads/', '') if ref.startswith('refs/heads/') else ref
            
            # Extract author information
            author = payload.get('pusher', {}).get('name', '')
            if not author:
                author = commit.get('author', {}).get('name', '')
            
            # Extract commit hash (request_id)
            commit_hash = commit.get('id', '')[:7]  # Short hash
            
            # Extract timestamp
            timestamp_str = commit.get('timestamp', '')
            if timestamp_str:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                timestamp = datetime.utcnow()
            
            return {
                'request_id': commit_hash,
                'author': author,
                'action': 'PUSH',
                'from_branch': None,  # Push doesn't have from_branch
                'to_branch': branch,
                'timestamp': timestamp
            }
        except Exception as e:
            logger.error(f"Error parsing push event: {e}")
            return None
    
    @staticmethod
    def parse_pull_request_event(payload: Dict) -> Optional[Dict]:
        """
        Parse GitHub pull request event payload
        
        Args:
            payload: GitHub webhook payload dictionary
            
        Returns:
            Normalized event data dictionary or None if parsing fails
        """
        try:
            pr_data = payload.get('pull_request', {})
            action = payload.get('action', '')
            
            # Only process opened, closed, or synchronize actions
            if action not in ['opened', 'closed', 'synchronize']:
                logger.info(f"Ignoring pull request action: {action}")
                return None
            
            # Extract branch information
            from_branch = pr_data.get('head', {}).get('ref', '')
            to_branch = pr_data.get('base', {}).get('ref', '')
            
            # Extract author information
            author = pr_data.get('user', {}).get('login', '')
            
            # Extract PR ID (request_id)
            pr_id = str(pr_data.get('number', ''))
            
            # Determine if this is a merge event
            is_merged = pr_data.get('merged', False)
            merged_at = pr_data.get('merged_at')
            
            # Extract timestamp
            if is_merged and merged_at:
                # This is a merge event
                timestamp_str = merged_at
                event_action = 'MERGE'
            else:
                # This is a pull request event
                timestamp_str = pr_data.get('created_at', '')
                event_action = 'PULL_REQUEST'
            
            if timestamp_str:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                timestamp = datetime.utcnow()
            
            return {
                'request_id': pr_id,
                'author': author,
                'action': event_action,
                'from_branch': from_branch,
                'to_branch': to_branch,
                'timestamp': timestamp
            }
        except Exception as e:
            logger.error(f"Error parsing pull request event: {e}")
            return None
    
    @staticmethod
    def parse_webhook_event(payload: Dict, event_type: str) -> Optional[Dict]:
        """
        Parse GitHub webhook event based on event type
        
        Args:
            payload: GitHub webhook payload dictionary
            event_type: GitHub event type (push, pull_request, etc.)
            
        Returns:
            Normalized event data dictionary or None if event type is unsupported
        """
        if event_type == 'push':
            return GitHubWebhookService.parse_push_event(payload)
        elif event_type == 'pull_request':
            return GitHubWebhookService.parse_pull_request_event(payload)
        else:
            logger.info(f"Unsupported event type: {event_type}")
            return None
