# Microsoft Graph API Outlook Mail Reader: Application Flow

## Overview

The Outlook Mail Reader application connects to Microsoft 365 mailboxes via the Microsoft Graph API to retrieve and filter emails from specific senders containing specific keywords. This document explains the key components and flow of the application.

## Authentication Flow

1. **Initialize Authentication**
   - Load credentials (tenant_id, client_id) from environment variables or direct input
   - Create an MSAL PublicClientApplication with the tenant authority

2. **Device Code Flow**
   - The application initiates the device code flow
   - User is presented with a URL and code to enter in their browser
   - User authenticates in their browser using their Microsoft credentials
   - Application polls for authentication completion
   - Upon successful authentication, access tokens are received

3. **Token Management**
   - Access token is stored for API requests
   - Refresh token can be used for silent token renewal
   - Token cache can be serialized and saved for future sessions

## API Request Flow

1. **Initialize API Client**
   - Create headers with Bearer token for authorization
   - Set up retry logic for handling transient errors

2. **Email Retrieval**
   - Make request to `/me/messages` endpoint
   - Apply filters like sender email via OData filters
   - Request specific fields (id, subject, body, etc.)
   - Handle pagination for large result sets

3. **Error Handling**
   - Implement retry mechanism for transient errors
   - Parse error responses for troubleshooting
   - Proper exception handling with descriptive messages

## Email Filtering Flow

1. **Sender Filtering**
   - Filter messages from specific sender (e.g., FASTRAPP@paypal.com)
   - Compare sender email address case-insensitively

2. **Keyword Filtering**
   - Search for keyword in subject, body preview, or full body content
   - Support for case-sensitive or case-insensitive search
   - Option to search only in subject or only in body

3. **Result Formatting**
   - Format timestamps into readable format
   - Extract sender information
   - Generate direct Outlook web links to messages
   - Create consistent data structure for easy consumption

## Complete End-to-End Flow

1. **Configuration**
   - Load environment variables or user-provided credentials
   - Validate required configuration parameters

2. **Authentication**
   - Authenticate using device code flow
   - Obtain and store access token

3. **Email Retrieval**
   - Connect to Microsoft Graph API
   - Retrieve emails from the mailbox (filtered by sender if specified)

4. **Email Filtering**
   - Filter messages by keyword
   - Apply additional filtering if needed

5. **Result Processing**
   - Format and display matching emails
   - Provide links to view emails in Outlook web
   - Optionally export data to different formats

## Integration Flow for Notebooks

1. **Import Module**
   - Import the OutlookMailReader class into your notebook

2. **Initialize and Authenticate**
   - Create reader instance with credentials
   - Authenticate to obtain access token

3. **Search and Filter**
   - Use search_emails method to find emails matching criteria

4. **Process Results**
   - Work with returned email objects
   - Display, analyze, or export the data

5. **Custom Processing**
   - Apply additional custom filtering if needed
   - Convert to pandas DataFrame for analysis
   - Generate reports or visualizations

## Technical Implementation Details

- **Authentication**: Uses MSAL (Microsoft Authentication Library) for secure OAuth 2.0 flows
- **API Requests**: Uses the requests library with proper retry and error handling
- **Pagination**: Handles Microsoft Graph API pagination for complete result sets
- **Error Handling**: Comprehensive exception handling and informative error messages
- **Data Processing**: Clean formatting of API responses for easy consumption