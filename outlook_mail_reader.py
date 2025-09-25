#!/usr/bin/env python3
"""
Outlook Mail Reader for Microsoft Graph API

A clean, error-free implementation for retrieving and filtering emails 
from Microsoft 365/Outlook using Microsoft Graph API. 
Suitable for importing into notebooks and production environments.

Dependencies:
    - msal>=1.20.0
    - requests>=2.28.0
    - python-dotenv>=0.20.0 (optional for .env support)
"""

import os
import json
import time
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

# Optional dotenv support
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

import requests
import msal


class OutlookMailReader:
    """
    Microsoft Outlook Mail Reader using Graph API
    
    Features:
    - Authenticates via device code flow or direct access token
    - Searches emails from specific senders
    - Filters emails containing specific keywords
    - Provides direct Outlook web links to messages
    """
    
    def __init__(self, tenant_id: Optional[str] = None, 
                 client_id: Optional[str] = None,
                 access_token: Optional[str] = None,
                 load_env: bool = True,
                 env_file: Optional[str] = None,
                 verbose: bool = True):
        """
        Initialize the Outlook Mail Reader
        
        Args:
            tenant_id (str, optional): Microsoft Entra ID tenant ID
            client_id (str, optional): Microsoft Entra ID client/app ID 
            access_token (str, optional): Microsoft Graph API access token (if already authenticated)
            load_env (bool): Whether to load credentials from .env file
            env_file (str, optional): Path to .env file if not in current directory
            verbose (bool): Whether to print status messages
        """
        self.verbose = verbose
        
        # Load environment variables if requested
        if load_env and DOTENV_AVAILABLE:
            self._log("Loading environment variables...")
            if env_file:
                load_dotenv(env_file)
            else:
                load_dotenv()
        
        # Set credentials (prioritize constructor arguments over environment variables)
        self.tenant_id = tenant_id or os.getenv("TENANT_ID")
        self.client_id = client_id or os.getenv("CLIENT_ID")
        self.access_token = access_token or os.getenv("ACCESS_TOKEN")
        
        # API settings
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.scopes = ["Mail.Read", "User.Read"]
        
        # Validate required credentials
        if not self.access_token and (not self.tenant_id or not self.client_id):
            raise ValueError(
                "Missing credentials. You must provide either:"
                "\n1. tenant_id AND client_id for authentication"
                "\n2. access_token for direct API access"
            )
    
    def _log(self, message: str) -> None:
        """Print log message if verbose mode is enabled"""
        if self.verbose:
            print(f"[OutlookMailReader] {message}")
    
    def authenticate(self, force_new_token: bool = False) -> bool:
        """
        Authenticate with Microsoft Graph API using device code flow
        
        Args:
            force_new_token (bool): Force new authentication even if token exists
            
        Returns:
            bool: True if authentication was successful
        
        Raises:
            ValueError: If authentication credentials are missing
            RuntimeError: If authentication fails after retries
        """
        # Skip if we already have a token and not forcing re-auth
        if self.access_token and not force_new_token:
            self._log("Using existing access token")
            return True
        
        # Validate credentials
        if not self.tenant_id or not self.client_id:
            raise ValueError("Missing tenant_id or client_id required for authentication")
        
        self._log("Starting authentication via device code flow...")
        
        try:
            # Create MSAL app
            app = msal.PublicClientApplication(
                client_id=self.client_id,
                authority=f"https://login.microsoftonline.com/{self.tenant_id}"
            )
            
            # Start device code flow
            flow = app.initiate_device_flow(scopes=self.scopes)
            
            if "user_code" not in flow:
                error_msg = f"Failed to start device flow: {flow.get('error_description', 'Unknown error')}"
                self._log(error_msg)
                raise RuntimeError(error_msg)
            
            # Display authentication instructions
            print("\n" + "=" * 60)
            print(f"🌐 To sign in, visit: {flow.get('verification_uri')}")
            print(f"📝 Enter code: {flow.get('user_code')}")
            print("=" * 60)
            print("⏳ Waiting for authentication...\n")
            
            # Wait for user to complete authentication
            result = app.acquire_token_by_device_flow(flow)
            
            if "access_token" not in result:
                error_msg = f"Authentication failed: {result.get('error_description', 'Unknown error')}"
                self._log(error_msg)
                raise RuntimeError(error_msg)
            
            # Save token
            self.access_token = result["access_token"]
            self._log("Authentication successful!")
            return True
            
        except Exception as e:
            error_msg = f"Authentication error: {str(e)}"
            self._log(error_msg)
            raise RuntimeError(error_msg) from e
    
    def _make_api_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None,
                         max_retries: int = 3, retry_delay: int = 1) -> Dict[str, Any]:
        """
        Make a request to Microsoft Graph API with retry logic
        
        Args:
            endpoint (str): API endpoint to call (without base URL)
            params (Dict, optional): Query parameters
            max_retries (int): Maximum number of retry attempts
            retry_delay (int): Delay between retries in seconds
            
        Returns:
            Dict: JSON response from API
            
        Raises:
            RuntimeError: If the request fails after all retries
        """
        if not self.access_token:
            raise ValueError("No access token available. Call authenticate() first.")
        
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        retries = 0
        while retries <= max_retries:
            try:
                self._log(f"Making request to: {url}")
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                retries += 1
                
                # Check if we've reached max retries
                if retries > max_retries:
                    error_msg = f"API request failed after {max_retries} attempts: {str(e)}"
                    
                    # Include error details if available
                    if hasattr(e, 'response') and e.response is not None:
                        try:
                            error_data = e.response.json()
                            error_msg += f"\nResponse error: {error_data}"
                        except ValueError:
                            error_msg += f"\nResponse text: {e.response.text}"
                    
                    self._log(error_msg)
                    raise RuntimeError(error_msg) from e
                
                # Wait before retrying
                self._log(f"Request failed, retrying in {retry_delay}s (attempt {retries}/{max_retries})")
                time.sleep(retry_delay)
    
    def get_messages(self, max_items: int = 25, filter_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get messages from Outlook mailbox with filtering options
        
        Args:
            max_items (int): Maximum number of messages to retrieve
            filter_query (str, optional): OData filter query (e.g., "from/emailAddress/address eq 'example@domain.com'")
            
        Returns:
            List[Dict]: List of message objects
        """
        self._log(f"Retrieving messages (max: {max_items})")
        
        # Ensure we have a token
        if not self.access_token:
            self.authenticate()
        
        # Set up request parameters
        params = {
            "$select": "id,subject,bodyPreview,receivedDateTime,from,body",
            "$orderby": "receivedDateTime DESC",
            "$top": min(max_items, 999)  # API limit is 999 per request
        }
        
        # Add filter if provided
        if filter_query:
            params["$filter"] = filter_query
        
        # Make the request
        response = self._make_api_request("me/messages", params)
        
        # Extract messages
        messages = response.get("value", [])
        self._log(f"Retrieved {len(messages)} messages")
        
        return messages
    
    def get_messages_from_sender(self, sender_email: str, max_items: int = 25) -> List[Dict[str, Any]]:
        """
        Get messages from a specific sender email address
        
        Args:
            sender_email (str): Sender email address to filter by
            max_items (int): Maximum number of messages to retrieve
            
        Returns:
            List[Dict]: List of message objects
        """
        self._log(f"Retrieving messages from sender: {sender_email}")
        
        # Create filter for specific sender
        filter_query = f"from/emailAddress/address eq '{sender_email}'"
        
        # Get messages with filter
        return self.get_messages(max_items=max_items, filter_query=filter_query)
    
    def filter_messages_by_keyword(self, messages: List[Dict[str, Any]], 
                                  keyword: str,
                                  search_in_subject: bool = True,
                                  search_in_body: bool = True,
                                  case_sensitive: bool = False) -> List[Dict[str, Any]]:
        """
        Filter messages containing a specific keyword in subject or body
        
        Args:
            messages (List[Dict]): List of message objects
            keyword (str): Keyword to search for
            search_in_subject (bool): Whether to search in subject
            search_in_body (bool): Whether to search in body
            case_sensitive (bool): Whether to perform case-sensitive search
            
        Returns:
            List[Dict]: Filtered list of message objects
        """
        self._log(f"Filtering messages containing keyword: '{keyword}'")
        
        if not (search_in_subject or search_in_body):
            raise ValueError("At least one of search_in_subject or search_in_body must be True")
        
        filtered_messages = []
        
        # Process keyword based on case sensitivity
        if not case_sensitive:
            keyword = keyword.lower()
        
        for message in messages:
            match_found = False
            
            # Check subject if enabled
            if search_in_subject:
                subject = message.get('subject', '')
                if not case_sensitive:
                    subject = subject.lower()
                if keyword in subject:
                    match_found = True
            
            # Check body if enabled and no match found yet
            if search_in_body and not match_found:
                body_preview = message.get('bodyPreview', '')
                if not case_sensitive:
                    body_preview = body_preview.lower()
                if keyword in body_preview:
                    match_found = True
                
                # Check full body content if available and no match found
                if not match_found:
                    body = message.get('body', {}).get('content', '')
                    if not case_sensitive:
                        body = body.lower()
                    if keyword in body:
                        match_found = True
            
            # Add message to filtered list if match found
            if match_found:
                filtered_messages.append(message)
        
        self._log(f"Found {len(filtered_messages)} messages containing '{keyword}'")
        return filtered_messages
    
    def get_outlook_link(self, message: Dict[str, Any]) -> str:
        """
        Generate Outlook web link for a message
        
        Args:
            message (Dict): Message object
            
        Returns:
            str: Outlook web link to the message
        """
        message_id = message.get('id', '')
        if not message_id:
            return ""
        
        return f"https://outlook.office.com/mail/deeplink/read/{message_id}"
    
    def format_message_info(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format message into a clean, easy-to-use structure
        
        Args:
            message (Dict): Original message object from Graph API
            
        Returns:
            Dict: Formatted message information
        """
        # Extract timestamp and format it
        received_time = message.get('receivedDateTime', '')
        if received_time:
            try:
                # Parse ISO format timestamp
                dt = datetime.fromisoformat(received_time.replace('Z', '+00:00'))
                formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                formatted_time = received_time
        else:
            formatted_time = 'Unknown'
        
        # Format sender information
        sender_info = message.get('from', {}).get('emailAddress', {})
        sender_email = sender_info.get('address', 'Unknown')
        sender_name = sender_info.get('name', sender_email)
        
        # Create formatted message
        return {
            'id': message.get('id', ''),
            'timestamp': formatted_time,
            'sender_name': sender_name,
            'sender_email': sender_email,
            'subject': message.get('subject', ''),
            'preview': message.get('bodyPreview', ''),
            'outlook_link': self.get_outlook_link(message)
        }
    
    def search_emails(self, sender_email: str, keyword: Optional[str] = None, 
                     max_items: int = 25, search_in_subject: bool = True, 
                     search_in_body: bool = True, case_sensitive: bool = False,
                     format_results: bool = True) -> List[Dict[str, Any]]:
        """
        Search for emails from a specific sender containing a keyword
        
        Args:
            sender_email (str): Sender email address to filter by
            keyword (str, optional): Keyword to search for (if None, returns all emails from sender)
            max_items (int): Maximum number of messages to retrieve
            search_in_subject (bool): Whether to search for keyword in subject
            search_in_body (bool): Whether to search for keyword in body
            case_sensitive (bool): Whether to perform case-sensitive search
            format_results (bool): Whether to format results into a cleaner structure
            
        Returns:
            List[Dict]: List of message objects matching the criteria
        """
        # Get messages from sender
        messages = self.get_messages_from_sender(sender_email, max_items)
        
        if not messages:
            self._log(f"No messages found from sender: {sender_email}")
            return []
        
        # Apply keyword filter if specified
        if keyword:
            messages = self.filter_messages_by_keyword(
                messages,
                keyword=keyword,
                search_in_subject=search_in_subject,
                search_in_body=search_in_body,
                case_sensitive=case_sensitive
            )
        
        # Format results if requested
        if format_results:
            return [self.format_message_info(message) for message in messages]
        
        return messages
    
    def print_message_details(self, message: Dict[str, Any], index: Optional[int] = None) -> None:
        """
        Print detailed information about a message
        
        Args:
            message (Dict): Message object (can be original or formatted)
            index (int, optional): Index to display (for numbering)
        """
        # Handle both original and formatted message format
        if 'timestamp' in message:
            # Already formatted
            formatted = message
        else:
            # Original format, needs formatting
            formatted = self.format_message_info(message)
        
        # Print header
        print(f"\n{'='*80}")
        if index is not None:
            print(f"📧 EMAIL #{index + 1}")
        else:
            print(f"📧 EMAIL DETAILS")
        print(f"{'='*80}")
        
        # Print message details
        print(f"📅 Date: {formatted['timestamp']}")
        print(f"👤 From: {formatted['sender_name']} <{formatted['sender_email']}>")
        print(f"📝 Subject: {formatted['subject']}")
        
        # Print preview
        preview = formatted['preview']
        if preview:
            print(f"\n📄 Preview:")
            # Truncate if too long
            if len(preview) > 500:
                preview = preview[:500] + "..."
            print(f"   {preview}")
        
        # Print Outlook link
        if formatted['outlook_link']:
            print(f"\n🔗 Outlook Link: {formatted['outlook_link']}")
        
        print(f"{'='*80}")


# Example usage (as standalone script)
if __name__ == "__main__":
    # Simple demonstration of the library
    import argparse
    
    parser = argparse.ArgumentParser(description="Outlook Mail Reader")
    parser.add_argument("--sender", help="Sender email to filter (default: FASTRAPP@paypal.com)", 
                        default="FASTRAPP@paypal.com")
    parser.add_argument("--keyword", help="Keyword to search for (default: failed)", 
                        default="failed")
    parser.add_argument("--max", type=int, help="Maximum emails to retrieve (default: 25)", 
                        default=25)
    args = parser.parse_args()
    
    try:
        # Initialize reader and authenticate
        reader = OutlookMailReader()
        reader.authenticate()
        
        # Search for emails
        emails = reader.search_emails(
            sender_email=args.sender,
            keyword=args.keyword,
            max_items=args.max
        )
        
        # Print results
        if emails:
            print(f"\n🎯 Found {len(emails)} emails from {args.sender} containing '{args.keyword}'")
            for i, email in enumerate(emails):
                reader.print_message_details(email, i)
        else:
            print(f"\n❌ No emails found from {args.sender} containing '{args.keyword}'")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")