"""
Gmail API Integration for EmailAgent.

This module provides functionality to authenticate with Gmail and fetch emails.
"""

import os
import base64
import logging
from typing import List, Dict, Any, Optional
from email.utils import parsedate_to_datetime
from datetime import datetime, timedelta

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    raise ImportError(
        "Gmail API libraries not installed. Install with: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client"
    )

logger = logging.getLogger(__name__)

# Gmail API scopes - read-only access to emails
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class GmailIntegration:
    """Handles Gmail API authentication and email fetching."""
    
    def __init__(self, credentials_path: str = "credentials.json", 
                 token_path: str = "token.json"):
        """
        Initialize Gmail integration.
        
        Args:
            credentials_path: Path to OAuth2 credentials JSON file
            token_path: Path to store/load OAuth2 token
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self.creds = None
        
    def authenticate(self) -> bool:
        """
        Authenticate with Gmail API using OAuth2.
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            # Load existing token if available
            if os.path.exists(self.token_path):
                self.creds = Credentials.from_authorized_user_file(
                    self.token_path, SCOPES
                )
                logger.info("Loaded existing credentials from token.json")
            
            # If there are no (valid) credentials available, let the user log in
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    logger.info("Refreshing expired credentials")
                    self.creds.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_path):
                        logger.error(
                            f"Credentials file not found: {self.credentials_path}\n"
                            "Please download credentials.json from Google Cloud Console"
                        )
                        return False
                    
                    logger.info("Starting OAuth2 flow")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, SCOPES
                    )
                    self.creds = flow.run_local_server(port=0)
                
                # Save credentials for next run
                with open(self.token_path, 'w') as token:
                    token.write(self.creds.to_json())
                logger.info(f"Saved credentials to {self.token_path}")
            
            # Build Gmail service
            self.service = build('gmail', 'v1', credentials=self.creds)
            logger.info("Successfully authenticated with Gmail API")
            return True
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    def fetch_emails(self, 
                     max_results: int = 10,
                     query: Optional[str] = None,
                     label_ids: Optional[List[str]] = None,
                     include_spam_trash: bool = False) -> List[Dict[str, Any]]:
        """
        Fetch emails from Gmail.
        
        Args:
            max_results: Maximum number of emails to fetch (default: 10)
            query: Gmail search query (e.g., "is:unread", "from:example@gmail.com")
            label_ids: List of label IDs to filter by (e.g., ["INBOX"])
            include_spam_trash: Whether to include spam and trash
            
        Returns:
            List of email dictionaries with 'subject', 'body', 'from', 'date', etc.
        """
        if not self.service:
            logger.error("Not authenticated. Call authenticate() first.")
            return []
        
        try:
            # Build query parameters
            params = {
                'maxResults': max_results,
                'includeSpamTrash': include_spam_trash
            }
            
            if query:
                params['q'] = query
            
            if label_ids:
                params['labelIds'] = label_ids
            
            # Fetch message list
            logger.info(f"Fetching up to {max_results} emails...")
            results = self.service.users().messages().list(
                userId='me', **params
            ).execute()
            
            messages = results.get('messages', [])
            logger.info(f"Found {len(messages)} messages")
            
            if not messages:
                logger.info("No messages found")
                return []
            
            # Fetch full message details
            email_list = []
            for msg in messages:
                try:
                    email_dict = self._get_message_details(msg['id'])
                    if email_dict:
                        email_list.append(email_dict)
                except Exception as e:
                    logger.warning(f"Error fetching message {msg['id']}: {e}")
                    continue
            
            logger.info(f"Successfully fetched {len(email_list)} emails")
            return email_list
            
        except HttpError as error:
            logger.error(f"Gmail API error: {error}")
            return []
        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            return []
    
    def _get_message_details(self, msg_id: str) -> Optional[Dict[str, Any]]:
        """
        Get full details of a message by ID.
        
        Args:
            msg_id: Gmail message ID
            
        Returns:
            Dictionary with email details or None if error
        """
        try:
            message = self.service.users().messages().get(
                userId='me', id=msg_id, format='full'
            ).execute()
            
            # Extract headers
            headers = message['payload'].get('headers', [])
            header_dict = {h['name'].lower(): h['value'] for h in headers}
            
            # Extract body
            body_text = self._extract_body(message['payload'])
            
            # Extract date
            date_str = header_dict.get('date', '')
            try:
                email_date = parsedate_to_datetime(date_str) if date_str else datetime.now()
            except:
                email_date = datetime.now()
            
            # Build email dictionary
            email_dict = {
                'id': msg_id,
                'subject': header_dict.get('subject', '(No Subject)'),
                'body': body_text,
                'from': header_dict.get('from', ''),
                'to': header_dict.get('to', ''),
                'date': email_date.isoformat(),
                'snippet': message.get('snippet', ''),
                'thread_id': message.get('threadId', ''),
                'labels': message.get('labelIds', [])
            }
            
            return email_dict
            
        except Exception as e:
            logger.error(f"Error getting message details for {msg_id}: {e}")
            return None
    
    def _extract_body(self, payload: Dict[str, Any]) -> str:
        """
        Extract text body from email payload.
        
        Args:
            payload: Gmail message payload
            
        Returns:
            Extracted text body
        """
        body = ""
        
        try:
            # Check if body is directly available
            if 'body' in payload and 'data' in payload['body']:
                data = payload['body']['data']
                body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                return body
            
            # Check parts (multipart messages)
            if 'parts' in payload:
                for part in payload['parts']:
                    mime_type = part.get('mimeType', '')
                    
                    # Prefer text/plain over text/html
                    if mime_type == 'text/plain':
                        if 'body' in part and 'data' in part['body']:
                            data = part['body']['data']
                            body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                            return body
                    
                    # Fallback to text/html
                    elif mime_type == 'text/html' and not body:
                        if 'body' in part and 'data' in part['body']:
                            data = part['body']['data']
                            body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    
                    # Recursively check nested parts
                    if 'parts' in part:
                        nested_body = self._extract_body(part)
                        if nested_body:
                            body = nested_body
                            break
            
            return body if body else "(No body content)"
            
        except Exception as e:
            logger.warning(f"Error extracting body: {e}")
            return "(Error extracting body)"
    
    def fetch_unread_emails(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Convenience method to fetch unread emails.
        
        Args:
            max_results: Maximum number of emails to fetch
            
        Returns:
            List of unread email dictionaries
        """
        return self.fetch_emails(
            max_results=max_results,
            query="is:unread",
            label_ids=["INBOX"]
        )
    
    def fetch_recent_emails(self, days: int = 1, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch emails from the last N days.
        
        Args:
            days: Number of days to look back
            max_results: Maximum number of emails to fetch
            
        Returns:
            List of recent email dictionaries
        """
        date_query = datetime.now() - timedelta(days=days)
        date_str = date_query.strftime("%Y/%m/%d")
        query = f"after:{date_str}"
        
        return self.fetch_emails(
            max_results=max_results,
            query=query,
            label_ids=["INBOX"]
        )

