"""
Unit tests for config module.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import logging

from config import load_config, validate_config, ConfigError


class TestConfig(unittest.TestCase):
    """Test cases for config module."""
    
    @patch('config.load_dotenv')
    @patch('config.os.getenv')
    def test_load_config_required_vars(self, mock_getenv, mock_load_dotenv):
        """Test load_config loads required variables."""
        # Set up mock return values for required variables
        mock_getenv.side_effect = lambda key, default=None: {
            'TENANT_ID': 'test-tenant-id',
            'CLIENT_ID': 'test-client-id',
            'SENDER_FILTER': 'test@example.com',
            'MAX_ITEMS': '50',
            'STATE_FILE': 'test-state.json',
            'LOG_LEVEL': 'INFO',
            'KEYWORD': 'test-keyword',
            'SEARCH_IN_SUBJECT': 'true',
            'SEARCH_IN_BODY': 'true',
            'CONNECTION_RETRIES': '3',
            'CONNECTION_RETRY_DELAY': '5',
        }.get(key, default)
        
        # Call the function
        config = load_config()
        
        # Verify load_dotenv was called
        mock_load_dotenv.assert_called_once()
        
        # Verify required variables were loaded
        self.assertEqual(config['TENANT_ID'], 'test-tenant-id')
        self.assertEqual(config['CLIENT_ID'], 'test-client-id')
        self.assertEqual(config['SENDER_FILTER'], 'test@example.com')
        
        # Verify optional variables were loaded with correct types
        self.assertEqual(config['MAX_ITEMS'], 50)  # Converted to int
        self.assertEqual(config['STATE_FILE'], 'test-state.json')
        self.assertEqual(config['LOG_LEVEL'], logging.INFO)  # Converted to logging level
        self.assertEqual(config['KEYWORD'], 'test-keyword')
        self.assertTrue(config['SEARCH_IN_SUBJECT'])  # Converted to bool
        self.assertTrue(config['SEARCH_IN_BODY'])  # Converted to bool
        self.assertEqual(config['CONNECTION_RETRIES'], 3)  # Converted to int
        self.assertEqual(config['CONNECTION_RETRY_DELAY'], 5)  # Converted to int
    
    @patch('config.load_dotenv')
    @patch('config.os.getenv')
    def test_load_config_missing_required(self, mock_getenv, mock_load_dotenv):
        """Test load_config raises error on missing required variables."""
        # Set up mock to return None for required variables
        mock_getenv.return_value = None
        
        # Verify exception is raised
        with self.assertRaises(ConfigError):
            load_config()
    
    @patch('config.load_dotenv')
    @patch('config.os.getenv')
    def test_load_config_defaults(self, mock_getenv, mock_load_dotenv):
        """Test load_config sets defaults for optional variables."""
        # Set up mock to return values for required variables only
        mock_getenv.side_effect = lambda key, default=None: {
            'TENANT_ID': 'test-tenant-id',
            'CLIENT_ID': 'test-client-id',
            'SENDER_FILTER': 'test@example.com',
        }.get(key, default)
        
        # Call the function
        config = load_config()
        
        # Verify defaults were set
        self.assertEqual(config['MAX_ITEMS'], 25)
        self.assertEqual(config['STATE_FILE'], '.state.json')
        self.assertEqual(config['LOG_LEVEL'], logging.INFO)
        self.assertEqual(config['KEYWORD'], 'failed')
        self.assertTrue(config['SEARCH_IN_SUBJECT'])
        self.assertTrue(config['SEARCH_IN_BODY'])
        self.assertEqual(config['CONNECTION_RETRIES'], 3)
        self.assertEqual(config['CONNECTION_RETRY_DELAY'], 5)
    
    @patch('config.load_dotenv')
    @patch('config.os.getenv')
    def test_load_config_invalid_int(self, mock_getenv, mock_load_dotenv):
        """Test load_config raises error on invalid integer values."""
        # Set up mock to return invalid MAX_ITEMS
        mock_getenv.side_effect = lambda key, default=None: {
            'TENANT_ID': 'test-tenant-id',
            'CLIENT_ID': 'test-client-id',
            'SENDER_FILTER': 'test@example.com',
            'MAX_ITEMS': 'not-an-integer',
        }.get(key, default)
        
        # Verify exception is raised
        with self.assertRaises(ConfigError):
            load_config()
    
    def test_validate_config_valid(self):
        """Test validate_config with valid configuration."""
        config = {
            'TENANT_ID': 'test-tenant-id-12345',
            'CLIENT_ID': 'test-client-id-12345',
            'SENDER_FILTER': 'test@example.com',
            'MAX_ITEMS': 50,
            'CONNECTION_RETRIES': 3,
            'CONNECTION_RETRY_DELAY': 5,
            'SEARCH_IN_SUBJECT': True,
            'SEARCH_IN_BODY': True,
        }
        
        # Should not raise exception
        validate_config(config)
    
    def test_validate_config_invalid_tenant_id(self):
        """Test validate_config with invalid tenant ID."""
        config = {
            'TENANT_ID': '',  # Empty tenant ID
            'CLIENT_ID': 'test-client-id-12345',
            'SENDER_FILTER': 'test@example.com',
            'MAX_ITEMS': 50,
            'CONNECTION_RETRIES': 3,
            'CONNECTION_RETRY_DELAY': 5,
            'SEARCH_IN_SUBJECT': True,
            'SEARCH_IN_BODY': True,
        }
        
        # Should raise exception
        with self.assertRaises(ConfigError):
            validate_config(config)
    
    def test_validate_config_invalid_client_id(self):
        """Test validate_config with invalid client ID."""
        config = {
            'TENANT_ID': 'test-tenant-id-12345',
            'CLIENT_ID': 'short',  # Too short client ID
            'SENDER_FILTER': 'test@example.com',
            'MAX_ITEMS': 50,
            'CONNECTION_RETRIES': 3,
            'CONNECTION_RETRY_DELAY': 5,
            'SEARCH_IN_SUBJECT': True,
            'SEARCH_IN_BODY': True,
        }
        
        # Should raise exception
        with self.assertRaises(ConfigError):
            validate_config(config)
    
    def test_validate_config_invalid_max_items(self):
        """Test validate_config with invalid max items."""
        config = {
            'TENANT_ID': 'test-tenant-id-12345',
            'CLIENT_ID': 'test-client-id-12345',
            'SENDER_FILTER': 'test@example.com',
            'MAX_ITEMS': 0,  # Too small
            'CONNECTION_RETRIES': 3,
            'CONNECTION_RETRY_DELAY': 5,
            'SEARCH_IN_SUBJECT': True,
            'SEARCH_IN_BODY': True,
        }
        
        # Should raise exception
        with self.assertRaises(ConfigError):
            validate_config(config)
        
        # Test with too large value
        config['MAX_ITEMS'] = 1001
        with self.assertRaises(ConfigError):
            validate_config(config)
    
    def test_validate_config_invalid_search_options(self):
        """Test validate_config with invalid search options."""
        config = {
            'TENANT_ID': 'test-tenant-id-12345',
            'CLIENT_ID': 'test-client-id-12345',
            'SENDER_FILTER': 'test@example.com',
            'MAX_ITEMS': 50,
            'CONNECTION_RETRIES': 3,
            'CONNECTION_RETRY_DELAY': 5,
            'SEARCH_IN_SUBJECT': False,
            'SEARCH_IN_BODY': False,  # Both search options disabled
        }
        
        # Should raise exception
        with self.assertRaises(ConfigError):
            validate_config(config)


if __name__ == '__main__':
    unittest.main()