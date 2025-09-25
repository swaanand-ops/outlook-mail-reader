"""
Unit tests for outlook_mail_reader module.
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import json
import os
import datetime
import requests
from io import StringIO
import sys

from outlook_mail_reader import OutlookMailReader


class TestOutlookMailReader(unittest.TestCase):
    """Test cases for OutlookMailReader class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Patch environment variables
        self.env_patcher = patch.dict('os.environ', {
            'TENANT_ID': 'test-tenant-id',
            'CLIENT_ID': 'test-client-id',
        })
        self.env_patcher.start()
        
        # Create instance with mocked values
        self.reader = OutlookMailReader(verbose=False)
        
        # Sample messages for testing
        self.sample_message = {
            'id': 'test-message-id',
            'subject': 'Test Subject with Failed Notification',
            'bodyPreview': 'This is a test message that contains the word failed',
            'body': {
                'content': 'This is the full body content of the test message that contains the word failed.'
            },
            'from': {
                'emailAddress': {
                    'address': 'FASTRAPP@paypal.com',
                    'name': 'PayPal FASTRAPP'
                }
            },
            'receivedDateTime': '2023-09-18T10:30:00Z'
        }
        
        # Capture stdout for logging tests
        self.stdout_capture = StringIO()
        self.old_stdout = sys.stdout
        sys.stdout = self.stdout_capture
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.env_patcher.stop()
        sys.stdout = self.old_stdout
    
    def test_initialization_with_env_vars(self):
        """Test initialization with environment variables."""
        reader = OutlookMailReader(verbose=False)
        self.assertEqual(reader.tenant_id, 'test-tenant-id')
        self.assertEqual(reader.client_id, 'test-client-id')
        self.assertIsNone(reader.access_token)
        
    def test_initialization_with_params(self):
        """Test initialization with constructor parameters."""
        reader = OutlookMailReader(
            tenant_id='custom-tenant-id',
            client_id='custom-client-id',
            access_token='custom-token',
            verbose=False
        )
        self.assertEqual(reader.tenant_id, 'custom-tenant-id')
        self.assertEqual(reader.client_id, 'custom-client-id')
        self.assertEqual(reader.access_token, 'custom-token')
    
    def test_initialization_missing_credentials(self):
        """Test initialization with missing credentials raises ValueError."""
        with patch.dict('os.environ', {}, clear=True):  # Clear environment variables
            with self.assertRaises(ValueError):
                OutlookMailReader(verbose=False)
    
    @patch('msal.PublicClientApplication')
    def test_initialize_app(self, mock_msal_app):
        """Test the MSAL app initialization."""
        # Setup the mock
        mock_app_instance = MagicMock()
        mock_msal_app.return_value = mock_app_instance
        
        # Initialize app
        self.reader._initialize_app()
        
        # Check if msal.PublicClientApplication was called with correct args
        mock_msal_app.assert_called_once_with(
            client_id='test-client-id',
            authority='https://login.microsoftonline.com/test-tenant-id'
        )
        self.assertEqual(self.reader.app, mock_app_instance)
    
    @patch('builtins.open', new_callable=mock_open, read_data=json.dumps({"token_data": "test"}))
    @patch('os.path.exists', return_value=True)
    @patch('msal.PublicClientApplication')
    def test_token_cache_loading(self, mock_msal_app, mock_exists, mock_file):
        """Test loading token cache from file."""
        # Setup mocks
        mock_app_instance = MagicMock()
        mock_msal_app.return_value = mock_app_instance
        
        # Create reader with token cache path
        reader = OutlookMailReader(token_cache_path='test_cache.json', verbose=False)
        
        # Check if cache was loaded
        mock_exists.assert_called_once_with('test_cache.json')
        mock_file.assert_called_once_with('test_cache.json', 'r')
        mock_app_instance.token_cache.deserialize.assert_called_once()
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('msal.PublicClientApplication')
    def test_save_token_cache(self, mock_msal_app, mock_file):
        """Test saving token cache to file."""
        # Setup mocks
        mock_app_instance = MagicMock()
        mock_app_instance.token_cache.serialize.return_value = json.dumps({"token_data": "test"})
        mock_msal_app.return_value = mock_app_instance
        
        # Create reader with token cache path
        reader = OutlookMailReader(token_cache_path='test_cache.json', verbose=False)
        reader.app = mock_app_instance
        
        # Save token cache
        reader._save_token_cache()
        
        # Check if cache was saved
        mock_file.assert_called_once_with('test_cache.json', 'w')
        mock_app_instance.token_cache.serialize.assert_called_once()
    
    def test_check_token_expiry(self):
        """Test token expiry checking."""
        # Test with no expiry time
        self.reader.token_expiry = None
        self.assertTrue(self.reader._check_token_expiry())
        
        # Test with future expiry time (not expired)
        self.reader.token_expiry = datetime.datetime.now() + datetime.timedelta(hours=1)
        self.assertFalse(self.reader._check_token_expiry())
        
        # Test with past expiry time (expired)
        self.reader.token_expiry = datetime.datetime.now() - datetime.timedelta(minutes=10)
        self.assertTrue(self.reader._check_token_expiry())
        
        # Test with expiry time less than 5 minutes away (considered expired)
        self.reader.token_expiry = datetime.datetime.now() + datetime.timedelta(minutes=4)
        self.assertTrue(self.reader._check_token_expiry())
    
    @patch('msal.PublicClientApplication')
    def test_acquire_token_silent_success(self, mock_msal_app):
        """Test silent token acquisition success."""
        # Setup mocks
        mock_app_instance = MagicMock()
        mock_app_instance.get_accounts.return_value = [MagicMock()]
        mock_app_instance.acquire_token_silent.return_value = {
            'access_token': 'new-token',
            'expires_in': 3600,
            'refresh_token': 'refresh-token'
        }
        mock_msal_app.return_value = mock_app_instance
        
        # Initialize reader with app
        self.reader.app = mock_app_instance
        
        # Test token acquisition
        result = self.reader._acquire_token_silent()
        
        # Verify result
        self.assertTrue(result)
        self.assertEqual(self.reader.access_token, 'new-token')
        self.assertIsNotNone(self.reader.token_expiry)
        self.assertEqual(self.reader.refresh_token, 'refresh-token')
    
    @patch('msal.PublicClientApplication')
    def test_acquire_token_silent_no_accounts(self, mock_msal_app):
        """Test silent token acquisition with no accounts."""
        # Setup mocks
        mock_app_instance = MagicMock()
        mock_app_instance.get_accounts.return_value = []  # No accounts
        mock_msal_app.return_value = mock_app_instance
        
        # Initialize reader with app
        self.reader.app = mock_app_instance
        
        # Test token acquisition
        result = self.reader._acquire_token_silent()
        
        # Verify result
        self.assertFalse(result)
    
    @patch('msal.PublicClientApplication')
    def test_acquire_token_silent_failure(self, mock_msal_app):
        """Test silent token acquisition failure."""
        # Setup mocks
        mock_app_instance = MagicMock()
        mock_app_instance.get_accounts.return_value = [MagicMock()]
        mock_app_instance.acquire_token_silent.return_value = None  # Acquisition failed
        mock_msal_app.return_value = mock_app_instance
        
        # Initialize reader with app
        self.reader.app = mock_app_instance
        
        # Test token acquisition
        result = self.reader._acquire_token_silent()
        
        # Verify result
        self.assertFalse(result)
    
    @patch('msal.PublicClientApplication')
    def test_get_auth_url(self, mock_msal_app):
        """Test getting auth URL for device code flow."""
        # Setup mocks
        mock_app_instance = MagicMock()
        mock_app_instance.initiate_device_flow.return_value = {
            'verification_uri': 'https://login.microsoftonline.com/verify',
            'user_code': 'ABC123'
        }
        mock_msal_app.return_value = mock_app_instance
        
        # Initialize reader with app
        self.reader.app = mock_app_instance
        
        # Get auth URL
        uri, code = self.reader.get_auth_url()
        
        # Verify result
        self.assertEqual(uri, 'https://login.microsoftonline.com/verify')
        self.assertEqual(code, 'ABC123')
        self.assertEqual(self.reader._device_flow, {
            'verification_uri': 'https://login.microsoftonline.com/verify',
            'user_code': 'ABC123'
        })
    
    @patch('msal.PublicClientApplication')
    def test_get_auth_url_failure(self, mock_msal_app):
        """Test getting auth URL failure."""
        # Setup mocks
        mock_app_instance = MagicMock()
        mock_app_instance.initiate_device_flow.return_value = {
            'error': 'error_code',
            'error_description': 'Error message'
        }
        mock_msal_app.return_value = mock_app_instance
        
        # Initialize reader with app
        self.reader.app = mock_app_instance
        
        # Get auth URL should raise RuntimeError
        with self.assertRaises(RuntimeError):
            self.reader.get_auth_url()
    
    @patch('msal.PublicClientApplication')
    def test_complete_auth_success(self, mock_msal_app):
        """Test completing authentication successfully."""
        # Setup mocks
        mock_app_instance = MagicMock()
        mock_app_instance.acquire_token_by_device_flow.return_value = {
            'access_token': 'device-flow-token',
            'expires_in': 3600,
            'refresh_token': 'device-flow-refresh'
        }
        mock_msal_app.return_value = mock_app_instance
        
        # Initialize reader with app and device flow
        self.reader.app = mock_app_instance
        self.reader._device_flow = {'device_code': 'test-device-code'}
        
        # Complete authentication
        result = self.reader.complete_auth()
        
        # Verify result
        self.assertTrue(result)
        self.assertEqual(self.reader.access_token, 'device-flow-token')
        self.assertIsNotNone(self.reader.token_expiry)
        self.assertEqual(self.reader.refresh_token, 'device-flow-refresh')
    
    @patch('msal.PublicClientApplication')
    def test_complete_auth_failure(self, mock_msal_app):
        """Test completing authentication failure."""
        # Setup mocks
        mock_app_instance = MagicMock()
        mock_app_instance.acquire_token_by_device_flow.return_value = {
            'error': 'error_code',
            'error_description': 'Error message'
        }
        mock_msal_app.return_value = mock_app_instance
        
        # Initialize reader with app and device flow
        self.reader.app = mock_app_instance
        self.reader._device_flow = {'device_code': 'test-device-code'}
        
        # Complete authentication should raise RuntimeError
        with self.assertRaises(RuntimeError):
            self.reader.complete_auth()
    
    @patch('outlook_mail_reader.OutlookMailReader._acquire_token_silent')
    @patch('outlook_mail_reader.OutlookMailReader.get_auth_url')
    @patch('outlook_mail_reader.OutlookMailReader.complete_auth')
    def test_authenticate_existing_valid_token(self, mock_complete_auth, mock_get_auth_url, mock_acquire_token_silent):
        """Test authentication with existing valid token."""
        # Setup
        self.reader.access_token = 'existing-token'
        self.reader.token_expiry = datetime.datetime.now() + datetime.timedelta(hours=1)
        
        # Authenticate
        result = self.reader.authenticate()
        
        # Verify result
        self.assertTrue(result)
        
        # Verify no calls to token acquisition methods
        mock_acquire_token_silent.assert_not_called()
        mock_get_auth_url.assert_not_called()
        mock_complete_auth.assert_not_called()
    
    @patch('outlook_mail_reader.OutlookMailReader._acquire_token_silent', return_value=True)
    def test_authenticate_silent_acquisition(self, mock_acquire_token_silent):
        """Test authentication with silent token acquisition."""
        # Setup
        self.reader.access_token = None
        
        # Authenticate
        result = self.reader.authenticate()
        
        # Verify result
        self.assertTrue(result)
        
        # Verify call to silent token acquisition
        mock_acquire_token_silent.assert_called_once()
    
    @patch('outlook_mail_reader.OutlookMailReader._acquire_token_silent', return_value=False)
    @patch('outlook_mail_reader.OutlookMailReader.get_auth_url')
    @patch('outlook_mail_reader.OutlookMailReader.complete_auth', return_value=True)
    def test_authenticate_interactive(self, mock_complete_auth, mock_get_auth_url, mock_acquire_token_silent):
        """Test authentication with interactive flow."""
        # Setup
        self.reader.access_token = None
        mock_get_auth_url.return_value = ('https://login.example.com', 'CODE123')
        
        # Authenticate
        result = self.reader.authenticate()
        
        # Verify result
        self.assertTrue(result)
        
        # Verify calls to authentication methods
        mock_acquire_token_silent.assert_called_once()
        mock_get_auth_url.assert_called_once()
        mock_complete_auth.assert_called_once()
    
    @patch('msal.ConfidentialClientApplication')
    def test_authenticate_with_client_secret(self, mock_confidential_app):
        """Test authentication with client secret."""
        # Setup mocks
        mock_app_instance = MagicMock()
        mock_app_instance.acquire_token_for_client.return_value = {
            'access_token': 'client-secret-token',
            'expires_in': 3600
        }
        mock_confidential_app.return_value = mock_app_instance
        
        # Authenticate with client secret
        result = self.reader.authenticate_with_client_secret('test-client-secret')
        
        # Verify result
        self.assertTrue(result)
        self.assertEqual(self.reader.access_token, 'client-secret-token')
        
        # Verify confidential client app was created correctly
        mock_confidential_app.assert_called_once_with(
            client_id='test-client-id',
            authority='https://login.microsoftonline.com/test-tenant-id',
            client_credential='test-client-secret'
        )
    
    def test_set_access_token(self):
        """Test manually setting access token."""
        self.reader.set_access_token('manual-token', 3600)
        
        self.assertEqual(self.reader.access_token, 'manual-token')
        self.assertIsNotNone(self.reader.token_expiry)
    
    @patch('requests.get')
    def test_make_api_request_success(self, mock_get):
        """Test making successful API request."""
        # Setup mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'value': 'test-data'}
        mock_get.return_value = mock_response
        
        # Set access token
        self.reader.access_token = 'test-token'
        
        # Make API request
        result = self.reader._make_api_request('me', {'param': 'value'})
        
        # Verify result
        self.assertEqual(result, {'value': 'test-data'})
        
        # Verify request was made correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args[1]
        self.assertEqual(call_args['params'], {'param': 'value'})
        self.assertEqual(call_args['headers']['Authorization'], 'Bearer test-token')
    
    @patch('requests.get')
    @patch('outlook_mail_reader.OutlookMailReader._acquire_token_silent', return_value=True)
    def test_make_api_request_refresh_token(self, mock_acquire_token_silent, mock_get):
        """Test API request with token refresh on 401."""
        # Setup mocks for first call (401) and second call (200)
        mock_response_401 = MagicMock()
        mock_response_401.status_code = 401
        mock_response_401.raise_for_status.side_effect = requests.exceptions.HTTPError()
        
        mock_response_200 = MagicMock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = {'value': 'test-data'}
        
        mock_get.side_effect = [mock_response_401, mock_response_200]
        
        # Set access token
        self.reader.access_token = 'old-token'
        
        # Make API request
        result = self.reader._make_api_request('me')
        
        # Verify token refresh was attempted
        mock_acquire_token_silent.assert_called_once()
        
        # Verify request was made twice
        self.assertEqual(mock_get.call_count, 2)
    
    @patch('requests.get')
    def test_make_api_request_retry_on_error(self, mock_get):
        """Test API request retries on error."""
        # Setup mocks for first two calls (error) and third call (success)
        error_response = MagicMock()
        error_response.raise_for_status.side_effect = requests.exceptions.RequestException()
        
        success_response = MagicMock()
        success_response.status_code = 200
        success_response.json.return_value = {'value': 'test-data'}
        
        mock_get.side_effect = [error_response, error_response, success_response]
        
        # Set access token
        self.reader.access_token = 'test-token'
        
        # Make API request with retry
        with patch('time.sleep'):  # Skip actual sleep
            result = self.reader._make_api_request('me', max_retries=2, retry_delay=0)
        
        # Verify result
        self.assertEqual(result, {'value': 'test-data'})
        
        # Verify request was made three times
        self.assertEqual(mock_get.call_count, 3)
    
    @patch('requests.get')
    def test_get_messages(self, mock_get):
        """Test getting messages."""
        # Setup mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'value': [self.sample_message]
        }
        mock_get.return_value = mock_response
        
        # Set access token
        self.reader.access_token = 'test-token'
        
        # Get messages
        messages = self.reader.get_messages(max_items=10, filter_query="filter=value")
        
        # Verify result
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]['id'], 'test-message-id')
        
        # Verify request was made correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args[1]
        self.assertEqual(call_args['params']['$top'], 10)
        self.assertEqual(call_args['params']['$filter'], "filter=value")
    
    @patch('outlook_mail_reader.OutlookMailReader.get_messages')
    def test_get_messages_from_sender(self, mock_get_messages):
        """Test getting messages from specific sender."""
        # Setup mock
        mock_get_messages.return_value = [self.sample_message]
        
        # Get messages from sender
        messages = self.reader.get_messages_from_sender('FASTRAPP@paypal.com', max_items=10)
        
        # Verify result
        self.assertEqual(len(messages), 1)
        
        # Verify get_messages was called with correct filter
        mock_get_messages.assert_called_once_with(
            max_items=10, 
            filter_query="from/emailAddress/address eq 'FASTRAPP@paypal.com'"
        )
    
    def test_filter_messages_by_keyword(self):
        """Test filtering messages by keyword."""
        # Test with matching keyword in subject
        messages = [self.sample_message]
        result = self.reader.filter_messages_by_keyword(
            messages=messages,
            keyword='Failed',
            search_in_subject=True,
            search_in_body=True,
            case_sensitive=False
        )
        self.assertEqual(len(result), 1)
        
        # Test with non-matching keyword
        result = self.reader.filter_messages_by_keyword(
            messages=messages,
            keyword='nonexistent',
            search_in_subject=True,
            search_in_body=True
        )
        self.assertEqual(len(result), 0)
        
        # Test with case-sensitive matching
        result = self.reader.filter_messages_by_keyword(
            messages=messages,
            keyword='Failed',
            search_in_subject=True,
            search_in_body=True,
            case_sensitive=True
        )
        self.assertEqual(len(result), 0)  # Should not match (case mismatch)
        
        # Test with different search scopes
        # Only search in subject
        result = self.reader.filter_messages_by_keyword(
            messages=messages,
            keyword='failed',
            search_in_subject=True,
            search_in_body=False
        )
        self.assertEqual(len(result), 1)
        
        # Only search in body
        result = self.reader.filter_messages_by_keyword(
            messages=messages,
            keyword='failed',
            search_in_subject=False,
            search_in_body=True
        )
        self.assertEqual(len(result), 1)
    
    def test_get_outlook_link(self):
        """Test generating Outlook web link."""
        link = self.reader.get_outlook_link(self.sample_message)
        self.assertEqual(link, "https://outlook.office.com/mail/deeplink/read/test-message-id")
        
        # Test with missing ID
        message_without_id = {}
        link = self.reader.get_outlook_link(message_without_id)
        self.assertEqual(link, "")
    
    def test_format_message_info(self):
        """Test formatting message info."""
        formatted = self.reader.format_message_info(self.sample_message)
        
        self.assertEqual(formatted['id'], 'test-message-id')
        self.assertEqual(formatted['timestamp'], '2023-09-18 10:30:00')
        self.assertEqual(formatted['sender_name'], 'PayPal FASTRAPP')
        self.assertEqual(formatted['sender_email'], 'FASTRAPP@paypal.com')
        self.assertEqual(formatted['subject'], 'Test Subject with Failed Notification')
        self.assertEqual(formatted['preview'], 'This is a test message that contains the word failed')
        self.assertEqual(formatted['outlook_link'], 'https://outlook.office.com/mail/deeplink/read/test-message-id')
    
    @patch('outlook_mail_reader.OutlookMailReader.get_messages_from_sender')
    @patch('outlook_mail_reader.OutlookMailReader.filter_messages_by_keyword')
    @patch('outlook_mail_reader.OutlookMailReader.format_message_info')
    def test_search_emails(self, mock_format_message, mock_filter_messages, mock_get_messages):
        """Test searching emails."""
        # Setup mocks
        mock_get_messages.return_value = [self.sample_message]
        mock_filter_messages.return_value = [self.sample_message]
        mock_format_message.return_value = {'id': 'formatted-id'}
        
        # Search emails
        result = self.reader.search_emails(
            sender_email='FASTRAPP@paypal.com',
            keyword='failed',
            max_items=10,
            search_in_subject=True,
            search_in_body=True,
            format_results=True
        )
        
        # Verify result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['id'], 'formatted-id')
        
        # Verify method calls
        mock_get_messages.assert_called_once_with('FASTRAPP@paypal.com', 10)
        mock_filter_messages.assert_called_once()
        mock_format_message.assert_called_once_with(self.sample_message)
        
        # Test without formatting
        mock_format_message.reset_mock()
        result = self.reader.search_emails(
            sender_email='FASTRAPP@paypal.com',
            keyword='failed',
            format_results=False
        )
        mock_format_message.assert_not_called()
    
    @patch('outlook_mail_reader.OutlookMailReader.authenticate')
    @patch('outlook_mail_reader.OutlookMailReader._make_api_request')
    def test_test_connection(self, mock_make_api_request, mock_authenticate):
        """Test connection testing."""
        # Setup mock
        mock_make_api_request.return_value = {
            'userPrincipalName': 'test@example.com'
        }
        
        # Test connection
        result = self.reader.test_connection()
        
        # Verify result
        self.assertTrue(result)
        
        # Verify API request was made
        mock_make_api_request.assert_called_once_with("me")
    
    @patch('outlook_mail_reader.OutlookMailReader.authenticate')
    @patch('outlook_mail_reader.OutlookMailReader._make_api_request')
    def test_check_permissions(self, mock_make_api_request, mock_authenticate):
        """Test permission checking."""
        # Setup mock responses for different endpoints
        def side_effect(endpoint, *args, **kwargs):
            if endpoint == "me":
                return {'userPrincipalName': 'test@example.com'}
            elif endpoint == "me/messages":
                return {'value': []}
            return None
        
        mock_make_api_request.side_effect = side_effect
        
        # Check permissions
        result = self.reader.check_permissions()
        
        # Verify result
        self.assertTrue(result['User.Read'])
        self.assertTrue(result['Mail.Read'])
        
        # Verify API requests were made
        self.assertEqual(mock_make_api_request.call_count, 2)


if __name__ == '__main__':
    unittest.main()