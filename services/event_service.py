"""
Event Service
Handles event storage and retrieval from MongoDB
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from db.mongodb import get_db
from pymongo.errors import DuplicateKeyError

logger = logging.getLogger(__name__)

class EventService:
    """Service class for managing events in MongoDB"""
    
    @staticmethod
    def save_event(event_data: Dict) -> bool:
        """
        Save normalized event data to MongoDB
        
        Args:
            event_data: Normalized event data dictionary
            
        Returns:
            True if event was saved successfully, False otherwise
        """
        try:
            db = get_db()
            collection = db.events
            
            # Ensure timestamp is datetime object
            if isinstance(event_data.get('timestamp'), str):
                event_data['timestamp'] = datetime.fromisoformat(
                    event_data['timestamp'].replace('Z', '+00:00')
                )
            
            # Insert document
            result = collection.insert_one(event_data)
            
            logger.info(f"Event saved successfully: {result.inserted_id}")
            return True
            
        except DuplicateKeyError:
            logger.warning(f"Duplicate event detected (request_id: {event_data.get('request_id')}). Skipping.")
            return False
        except Exception as e:
            logger.error(f"Error saving event: {e}")
            return False
    
    @staticmethod
    def get_latest_events(limit: int = 50, since: Optional[datetime] = None) -> List[Dict]:
        """
        Retrieve latest events from MongoDB
        
        Args:
            limit: Maximum number of events to retrieve
            since: Optional datetime to filter events after this time
            
        Returns:
            List of event dictionaries sorted by timestamp (newest first)
        """
        try:
            db = get_db()
            collection = db.events
            
            # Build query
            query = {}
            if since:
                query['timestamp'] = {'$gt': since}
            
            # Query and sort by timestamp descending
            cursor = collection.find(query).sort('timestamp', -1).limit(limit)
            
            # Convert to list and handle datetime serialization
            events = []
            for event in cursor:
                # Convert ObjectId to string for JSON serialization
                event['_id'] = str(event['_id'])
                # Ensure timestamp is properly formatted
                if isinstance(event.get('timestamp'), datetime):
                    event['timestamp'] = event['timestamp'].isoformat()
                events.append(event)
            
            return events
            
        except Exception as e:
            logger.error(f"Error retrieving events: {e}")
            return []
    
    @staticmethod
    def get_events_since_timestamp(timestamp: datetime) -> List[Dict]:
        """
        Get events that occurred after a specific timestamp
        Used by frontend polling to get only new events
        
        Args:
            timestamp: Datetime to filter events after
            
        Returns:
            List of event dictionaries
        """
        return EventService.get_latest_events(since=timestamp)
