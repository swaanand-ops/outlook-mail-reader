"""
Unit tests for mail_filter module.
"""

import unittest
from unittest.mock import patch, MagicMock

from mail_filter import EmailFilter, FilterError


class TestEmailFilter(unittest.TestCase):
    """Test cases for EmailFilter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.filter = EmailFilter()
        
        # Sample message with all required fields
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
    
    def test_is_from_sender_match(self):
        """Test is_from_sender with matching sender."""
        result = self.filter.is_from_sender(self.sample_message, 'FASTRAPP@paypal.com')
        self.assertTrue(result)
    
    def test_is_from_sender_no_match(self):
        """Test is_from_sender with non-matching sender."""
        result = self.filter.is_from_sender(self.sample_message, 'different@example.com')
        self.assertFalse(result)
    
    def test_is_from_sender_case_insensitive(self):
        """Test is_from_sender with case-insensitive matching."""
        result = self.filter.is_from_sender(self.sample_message, 'fastrapp@paypal.com')
        self.assertTrue(result)
    
    def test_is_from_sender_missing_field(self):
        """Test is_from_sender with missing from field."""
        message_without_from = {
            'id': 'test-message-id',
            'subject': 'Test Subject'
        }
        result = self.filter.is_from_sender(message_without_from, 'FASTRAPP@paypal.com')
        self.assertFalse(result)
    
    def test_contains_keyword_in_subject(self):
        """Test contains_keyword with keyword in subject."""
        result = self.filter.contains_keyword(self.sample_message, 'Failed')
        self.assertTrue(result)
    
    def test_contains_keyword_in_body_preview(self):
        """Test contains_keyword with keyword in body preview."""
        message = self.sample_message.copy()
        message['subject'] = 'Test Subject'  # Remove keyword from subject
        result = self.filter.contains_keyword(message, 'failed')
        self.assertTrue(result)
    
    def test_contains_keyword_in_body_content(self):
        """Test contains_keyword with keyword in body content."""
        message = self.sample_message.copy()
        message['subject'] = 'Test Subject'  # Remove keyword from subject
        message['bodyPreview'] = 'This is a test message'  # Remove keyword from preview
        result = self.filter.contains_keyword(message, 'failed')
        self.assertTrue(result)
    
    def test_contains_keyword_no_match(self):
        """Test contains_keyword with no keyword match."""
        message = self.sample_message.copy()
        message['subject'] = 'Test Subject'
        message['bodyPreview'] = 'This is a test message'
        message['body']['content'] = 'This is the full body content.'
        result = self.filter.contains_keyword(message, 'failed')
        self.assertFalse(result)
    
    def test_contains_keyword_case_sensitive(self):
        """Test contains_keyword with case-sensitive matching."""
        # Default is case-insensitive
        result = self.filter.contains_keyword(self.sample_message, 'FAILED')
        self.assertTrue(result)
        
        # With case-sensitive matching
        result = self.filter.contains_keyword(self.sample_message, 'FAILED', case_sensitive=True)
        self.assertFalse(result)
    
    def test_contains_keyword_search_scope(self):
        """Test contains_keyword with different search scopes."""
        # Keyword is in subject and body
        result = self.filter.contains_keyword(
            self.sample_message, 'failed', 
            search_in_subject=True, search_in_body=True
        )
        self.assertTrue(result)
        
        # Search only in subject
        result = self.filter.contains_keyword(
            self.sample_message, 'failed', 
            search_in_subject=True, search_in_body=False
        )
        self.assertTrue(result)
        
        # Search only in body
        result = self.filter.contains_keyword(
            self.sample_message, 'failed', 
            search_in_subject=False, search_in_body=True
        )
        self.assertTrue(result)
    
    def test_contains_keyword_regex(self):
        """Test contains_keyword with regex pattern."""
        # Match with regex
        result = self.filter.contains_keyword(
            self.sample_message, r'fail\w+', 
            use_regex=True
        )
        self.assertTrue(result)
        
        # No match with regex
        result = self.filter.contains_keyword(
            self.sample_message, r'error\d+', 
            use_regex=True
        )
        self.assertFalse(result)
    
    def test_contains_keyword_invalid_regex(self):
        """Test contains_keyword with invalid regex pattern."""
        with self.assertRaises(FilterError):
            self.filter.contains_keyword(
                self.sample_message, r'[invalid', 
                use_regex=True
            )
    
    def test_filter_messages(self):
        """Test filter_messages with matching criteria."""
        messages = [self.sample_message]
        result = self.filter.filter_messages(
            messages=messages,
            sender='FASTRAPP@paypal.com',
            keyword='failed'
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['id'], 'test-message-id')
    
    def test_filter_messages_no_match(self):
        """Test filter_messages with non-matching criteria."""
        messages = [self.sample_message]
        result = self.filter.filter_messages(
            messages=messages,
            sender='FASTRAPP@paypal.com',
            keyword='nonexistent'
        )
        self.assertEqual(len(result), 0)
    
    def test_filter_messages_custom_filter(self):
        """Test filter_messages with custom filter function."""
        messages = [self.sample_message]
        
        # Custom filter function to check for a specific date
        def date_filter(message):
            return '2023-09-18' in message.get('receivedDateTime', '')
        
        result = self.filter.filter_messages(
            messages=messages,
            sender='FASTRAPP@paypal.com',
            keyword='failed',
            custom_filters=[date_filter]
        )
        self.assertEqual(len(result), 1)
        
        # Custom filter that won't match
        def negative_filter(message):
            return False
        
        result = self.filter.filter_messages(
            messages=messages,
            sender='FASTRAPP@paypal.com',
            keyword='failed',
            custom_filters=[negative_filter]
        )
        self.assertEqual(len(result), 0)


if __name__ == '__main__':
    unittest.main()