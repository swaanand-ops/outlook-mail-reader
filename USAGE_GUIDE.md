# Outlook Mail Reader - Usage Guide

This guide explains how to import and use the `OutlookMailReader` module in your production notebooks.

## Prerequisites

Before using the module, ensure you have the required dependencies installed:

```bash
pip install msal requests python-dotenv
```

## Importing the Module

Copy the `outlook_mail_reader.py` file to your project directory or a location in your Python path. Then import it in your notebook:

```python
from outlook_mail_reader import OutlookMailReader
```

## Basic Usage

### 1. Initialize the Reader

You can initialize the reader in several ways:

```python
# Option 1: Using environment variables from a .env file
reader = OutlookMailReader(load_env=True)

# Option 2: Providing credentials directly
reader = OutlookMailReader(
    tenant_id="your-tenant-id",
    client_id="your-client-id"
)

# Option 3: Using an existing access token
reader = OutlookMailReader(
    access_token="your-access-token"
)
```

### 2. Authenticate

If you're not using an access token, you need to authenticate:

```python
reader.authenticate()
```

This will display a URL and code to enter in your browser to authenticate.

### 3. Search for Emails

Search for emails from a specific sender containing a keyword:

```python
emails = reader.search_emails(
    sender_email="FASTRAPP@paypal.com",  # Sender email address
    keyword="failed",                    # Keyword to search for
    max_items=25                         # Maximum emails to retrieve
)
```

### 4. Process the Results

The search results are returned as a list of dictionaries, each containing formatted email information:

```python
for email in emails:
    print(f"Date: {email['timestamp']}")
    print(f"Subject: {email['subject']}")
    print(f"Outlook Link: {email['outlook_link']}")
    print("---")
```

## Advanced Usage

### Custom Filtering

For more complex filtering needs:

```python
# Get raw messages
messages = reader.get_messages_from_sender("FASTRAPP@paypal.com", max_items=50)

# Apply custom filtering logic
custom_filtered = []
for msg in messages:
    subject = msg.get('subject', '').lower()
    body = msg.get('bodyPreview', '').lower()
    
    # Your custom filtering logic here
    if ('error' in subject and 'authentication' in body):
        custom_filtered.append(msg)

# Format the results
formatted_results = [reader.format_message_info(msg) for msg in custom_filtered]
```

### Integration with Pandas

You can easily convert the results to a pandas DataFrame for analysis:

```python
import pandas as pd

df = pd.DataFrame([
    {
        'Date': email['timestamp'],
        'Sender': email['sender_email'],
        'Subject': email['subject'],
        'Preview': email['preview']
    }
    for email in emails
])

# Now you can use pandas functions
df.sort_values('Date', ascending=False)
```

## Complete Example

Here's a complete example that you can paste into your notebook:

```python
# Import the module
from outlook_mail_reader import OutlookMailReader

# Initialize and authenticate
reader = OutlookMailReader(load_env=True)
reader.authenticate()

# Search for emails
emails = reader.search_emails(
    sender_email="FASTRAPP@paypal.com",
    keyword="failed",
    max_items=25
)

# Print the results
print(f"Found {len(emails)} matching emails\n")

for i, email in enumerate(emails, 1):
    print(f"Email {i}:")
    print(f"  Date: {email['timestamp']}")
    print(f"  Subject: {email['subject']}")
    print(f"  Link: {email['outlook_link']}")
    print()

# Convert to pandas DataFrame (if needed)
import pandas as pd
df = pd.DataFrame(emails)
```

## Troubleshooting

- **Authentication Failed**: Ensure your tenant_id and client_id are correct. Make sure your app registration in Microsoft Entra ID has the required permissions.
- **No Emails Found**: Verify the sender email and keyword. Try removing the keyword filter to see if there are any emails from the sender.
- **Rate Limiting**: If you're making many requests, you might hit rate limits. Add delays between requests.

## API Reference

For more details about the available methods and parameters, refer to the docstrings in the `outlook_mail_reader.py` file.