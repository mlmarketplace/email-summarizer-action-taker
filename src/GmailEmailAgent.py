"""
Gmail-enabled EmailAgent that integrates with Gmail API.
"""

import logging
from typing import List, Dict, Any, Optional

try:
    # Try relative imports first (when used as a package)
    from .EmailAgent_optimized import EmailAgent, Task
    from .GmailIntegration import GmailIntegration
except ImportError:
    # Fall back to absolute imports (when run directly)
    from EmailAgent_optimized import EmailAgent, Task
    from GmailIntegration import GmailIntegration

logger = logging.getLogger(__name__)


class GmailEmailAgent(EmailAgent):
    """
    EmailAgent with Gmail integration.
    
    Extends EmailAgent to work directly with Gmail API.
    """
    
    def __init__(self, credentials_path: str = "credentials.json", 
                 token_path: str = "token.json"):
        """
        Initialize Gmail-enabled EmailAgent.
        
        Args:
            credentials_path: Path to Gmail OAuth2 credentials JSON file
            token_path: Path to store/load OAuth2 token
        """
        super().__init__()
        self.gmail = GmailIntegration(credentials_path, token_path)
        self.authenticated = False
    
    def connect(self) -> bool:
        """
        Authenticate with Gmail API.
        
        Returns:
            True if authentication successful, False otherwise
        """
        self.authenticated = self.gmail.authenticate()
        return self.authenticated
    
    def process_gmail_emails(self,
                             max_results: int = 10,
                             query: Optional[str] = None,
                             label_ids: Optional[List[str]] = None,
                             fetch_unread: bool = True) -> List[Task]:
        """
        Fetch emails from Gmail and process them into tasks.
        
        Args:
            max_results: Maximum number of emails to fetch
            query: Gmail search query (e.g., "is:unread", "from:example@gmail.com")
            label_ids: List of label IDs to filter by
            fetch_unread: If True, fetch only unread emails (overrides query)
            
        Returns:
            List of created tasks
        """
        if not self.authenticated:
            logger.warning("Not authenticated. Attempting to connect...")
            if not self.connect():
                logger.error("Failed to authenticate with Gmail")
                return []
        
        # Fetch emails from Gmail
        if fetch_unread:
            emails = self.gmail.fetch_unread_emails(max_results=max_results)
        else:
            emails = self.gmail.fetch_emails(
                max_results=max_results,
                query=query,
                label_ids=label_ids
            )
        
        if not emails:
            logger.info("No emails found to process")
            return []
        
        # Convert Gmail format to EmailAgent format and process
        processed_emails = self._convert_gmail_to_agent_format(emails)
        
        # Process through perceive -> reason -> act pipeline
        valid_emails = self.perceive(processed_emails)
        
        for email in valid_emails:
            info = self.reason(email)
            self.act(info)
        
        logger.info(f"Processed {len(valid_emails)} emails, created {len(self.tasks)} tasks")
        return self.tasks
    
    def _convert_gmail_to_agent_format(self, gmail_emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert Gmail email format to EmailAgent expected format.
        
        Args:
            gmail_emails: List of Gmail email dictionaries
            
        Returns:
            List of emails in EmailAgent format
        """
        converted = []
        for email in gmail_emails:
            # EmailAgent expects: {'subject': str, 'body': str}
            # Gmail provides: {'subject': str, 'body': str, 'from': str, 'date': str, ...}
            agent_email = {
                'subject': email.get('subject', ''),
                'body': email.get('body', ''),
                # Preserve additional Gmail metadata for potential future use
                'gmail_id': email.get('id'),
                'from': email.get('from', ''),
                'date': email.get('date', ''),
                'snippet': email.get('snippet', ''),
                'labels': email.get('labels', [])
            }
            converted.append(agent_email)
        
        return converted
    
    def process_recent_emails(self, days: int = 1, max_results: int = 50) -> List[Task]:
        """
        Process emails from the last N days.
        
        Args:
            days: Number of days to look back
            max_results: Maximum number of emails to fetch
            
        Returns:
            List of created tasks
        """
        if not self.authenticated:
            if not self.connect():
                return []
        
        emails = self.gmail.fetch_recent_emails(days=days, max_results=max_results)
        
        if not emails:
            return []
        
        processed_emails = self._convert_gmail_to_agent_format(emails)
        valid_emails = self.perceive(processed_emails)
        
        for email in valid_emails:
            info = self.reason(email)
            self.act(info)
        
        return self.tasks
    
    def mark_emails_processed(self, task: Task) -> bool:
        """
        Mark the source email as read/processed (if task has source email).
        
        Note: This requires 'gmail.modify' scope, which is not included by default
        for security. You would need to update SCOPES in GmailIntegration.
        
        Args:
            task: Task with source_email containing Gmail ID
            
        Returns:
            True if successful, False otherwise
        """
        if not task.source_email or 'gmail_id' not in task.source_email:
            logger.warning("Task does not have Gmail ID")
            return False
        
        # This would require additional scope: 'https://www.googleapis.com/auth/gmail.modify'
        # For now, just log the action
        logger.info(f"Would mark email {task.source_email['gmail_id']} as processed")
        return False  # Not implemented for read-only access

