# Outlook Mail Reader for Microsoft Graph API

A Python library for connecting to Microsoft 365 mailboxes and filtering emails using Microsoft Graph API.

## Features

- 🔐 Authenticates via **device-code flow** using **Microsoft Entra ID**
- 📥 Connects to **Outlook mailboxes** using `Mail.Read` delegated permission
- 🔍 Filters **emails by sender and keywords** in subject or body
- 📄 Provides detailed email information including direct Outlook web links
- 📊 Easy integration with data analysis tools like Pandas

## Installation

Clone this repository or download the `outlook_mail_reader.py` file:

```bash
git clone https://github.com/yourusername/outlook-mail-reader.git
```

Install the required dependencies:

```bash
pip install msal requests python-dotenv
```

## Quick Start

```python
from outlook_mail_reader import OutlookMailReader

# Initialize with credentials from .env file or provide directly
reader = OutlookMailReader(load_env=True)
# Or: reader = OutlookMailReader(tenant_id="your-tenant-id", client_id="your-client-id")

# Authenticate (will display a URL and code to enter in your browser)
reader.authenticate()

# Search for emails
emails = reader.search_emails(
    sender_email="FASTRAPP@paypal.com",  # Sender email address
    keyword="failed",                    # Keyword to search for
    max_items=25                         # Maximum number of emails to retrieve
)

# Process the results
for email in emails:
    print(f"Date: {email['timestamp']}")
    print(f"Subject: {email['subject']}")
    print(f"Link: {email['outlook_link']}")
    print("---")
```

## Jupyter Notebook Integration

Check out `outlook_reader_example.ipynb` for a complete example of how to use this library in Jupyter notebooks.

## Prerequisites

1. **App registration** in Microsoft Entra ID (Azure AD)
   - ✅ `Allow public client flows: ON`
   - ✅ Delegated permissions:
     - `Mail.Read`
     - `User.Read`
   - ✅ Consent granted (user or admin based on policy)

2. **Environment file (`.env`)**

```ini
TENANT_ID=<your-tenant-id>
CLIENT_ID=<your-app-client-id>
```

## Documentation

- [Usage Guide](USAGE_GUIDE.md) - Detailed usage instructions
- [Application Flow](APPLICATION_FLOW.md) - Understanding how the library works

## License

MIT License