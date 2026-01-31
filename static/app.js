/**
 * GitHub Webhook Events Monitor - Frontend Application
 * Handles polling, data fetching, and UI updates
 */

class WebhookMonitor {
    constructor() {
        this.pollInterval = 15000; // 15 seconds
        this.lastFetchTime = null;
        this.displayedEventIds = new Set(); // Track displayed events to prevent duplicates
        this.pollTimer = null;
        this.isPolling = false;
        
        this.init();
    }

    /**
     * Initialize the application
     */
    init() {
        this.updateStatus('Connecting...', false);
        this.loadEvents();
        this.startPolling();
        this.updateLastUpdateTime();
    }

    /**
     * Start polling for new events
     */
    startPolling() {
        if (this.isPolling) return;
        
        this.isPolling = true;
        this.pollTimer = setInterval(() => {
            this.loadEvents();
        }, this.pollInterval);
    }

    /**
     * Stop polling
     */
    stopPolling() {
        if (this.pollTimer) {
            clearInterval(this.pollTimer);
            this.pollTimer = null;
            this.isPolling = false;
        }
    }

    /**
     * Load events from the API
     */
    async loadEvents() {
        try {
            // Build API URL with optional 'since' parameter
            let apiUrl = '/api/events?limit=50';
            if (this.lastFetchTime) {
                // Only fetch events after the last fetch time
                apiUrl += `&since=${this.lastFetchTime.toISOString()}`;
            }

            const response = await fetch(apiUrl);
            const data = await response.json();

            if (data.success && data.events) {
                this.processEvents(data.events);
                this.updateStatus('Connected', true);
                this.lastFetchTime = new Date(); // Update last fetch time
                this.updateLastUpdateTime();
            } else {
                throw new Error('Failed to fetch events');
            }
        } catch (error) {
            console.error('Error loading events:', error);
            this.updateStatus('Connection Error', false);
        }
    }

    /**
     * Process and display new events
     * Only displays events that haven't been shown before
     */
    processEvents(events) {
        if (!events || events.length === 0) {
            return;
        }

        // Filter out already displayed events
        const newEvents = events.filter(event => {
            const eventId = this.getEventId(event);
            if (this.displayedEventIds.has(eventId)) {
                return false; // Skip already displayed events
            }
            this.displayedEventIds.add(eventId);
            return true;
        });

        // Sort by timestamp (newest first) and display
        newEvents.sort((a, b) => {
            const timeA = new Date(a.timestamp);
            const timeB = new Date(b.timestamp);
            return timeB - timeA;
        });

        newEvents.forEach(event => {
            this.displayEvent(event);
        });

        // Remove empty state if events exist
        const emptyState = document.querySelector('.empty-state');
        if (emptyState && this.displayedEventIds.size > 0) {
            emptyState.remove();
        }
    }

    /**
     * Generate unique event ID for tracking
     */
    getEventId(event) {
        // Use request_id + timestamp to create unique ID
        return `${event.request_id}-${event.timestamp}`;
    }

    /**
     * Display a single event in the UI
     */
    displayEvent(event) {
        const eventsList = document.getElementById('events-list');
        
        // Create event card
        const eventCard = document.createElement('div');
        eventCard.className = `event-card ${event.action.toLowerCase()}`;
        
        // Format message based on action type
        const message = this.formatEventMessage(event);
        
        // Format timestamp
        const formattedTime = this.formatTimestamp(event.timestamp);
        
        eventCard.innerHTML = `
            <div class="event-message">${message}</div>
            <div class="event-timestamp">${formattedTime}</div>
        `;
        
        // Insert at the beginning of the list (newest first)
        // Find first element child (skip text nodes)
        let firstElementChild = eventsList.firstElementChild;
        if (firstElementChild && firstElementChild.classList && !firstElementChild.classList.contains('empty-state')) {
            eventsList.insertBefore(eventCard, firstElementChild);
        } else {
            eventsList.appendChild(eventCard);
        }
    }

    /**
     * Format event message based on action type
     * Formats match exact requirements:
     * - PUSH: "{author} pushed to {to_branch} on {timestamp}"
     * - PULL_REQUEST: "{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}"
     * - MERGE: "{author} merged branch {from_branch} to {to_branch} on {timestamp}"
     */
    formatEventMessage(event) {
        const author = `<span class="event-author">${this.escapeHtml(event.author)}</span>`;
        const fromBranch = event.from_branch 
            ? `<span class="event-branch">${this.escapeHtml(event.from_branch)}</span>` 
            : '';
        const toBranch = event.to_branch 
            ? `<span class="event-branch">${this.escapeHtml(event.to_branch)}</span>` 
            : '';
        
        switch (event.action) {
            case 'PUSH':
                return `${author} pushed to ${toBranch}`;
            
            case 'PULL_REQUEST':
                return `${author} submitted a pull request from ${fromBranch} to ${toBranch}`;
            
            case 'MERGE':
                return `${author} merged branch ${fromBranch} to ${toBranch}`;
            
            default:
                return `${author} performed ${event.action}`;
        }
    }

    /**
     * Format timestamp for display
     * Displays in UTC format as required
     */
    formatTimestamp(timestamp) {
        try {
            const date = new Date(timestamp);
            
            // Format as UTC string (e.g., "Mon, 15 Jan 2024 10:30:00 GMT")
            const utcString = date.toUTCString();
            
            // Also show relative time for better UX
            const now = new Date();
            const diffMs = now - date;
            const diffSecs = Math.floor(diffMs / 1000);
            const diffMins = Math.floor(diffSecs / 60);
            const diffHours = Math.floor(diffMins / 60);
            const diffDays = Math.floor(diffHours / 24);
            
            let relativeTime = '';
            if (diffSecs < 60) {
                relativeTime = 'Just now';
            } else if (diffMins < 60) {
                relativeTime = `${diffMins} minute${diffMins !== 1 ? 's' : ''} ago`;
            } else if (diffHours < 24) {
                relativeTime = `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
            } else if (diffDays < 7) {
                relativeTime = `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
            } else {
                relativeTime = utcString;
            }
            
            return `${relativeTime} (${utcString})`;
        } catch (error) {
            return timestamp; // Return original if parsing fails
        }
    }

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Update connection status indicator
     */
    updateStatus(text, connected) {
        const statusText = document.getElementById('status-text');
        const statusDot = document.getElementById('status-dot');
        
        statusText.textContent = text;
        if (connected) {
            statusDot.classList.add('connected');
        } else {
            statusDot.classList.remove('connected');
        }
    }

    /**
     * Update last update time display
     */
    updateLastUpdateTime() {
        const lastUpdate = document.getElementById('last-update');
        if (lastUpdate) {
            const now = new Date();
            lastUpdate.textContent = now.toLocaleTimeString();
        }
    }
}

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new WebhookMonitor();
});
