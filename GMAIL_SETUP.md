# Gmail Integration Setup Guide

This guide will help you set up Gmail API integration for the EmailAgent.

## Prerequisites

- Python 3.7 or higher
- A Google account
- Google Cloud Project with Gmail API enabled

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

## Step 2: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"

## Step 3: Create OAuth 2.0 Credentials

1. In Google Cloud Console, go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - Choose "External" (unless you have a Google Workspace account)
   - Fill in required fields (App name, User support email, Developer contact)
   - Add scopes: `https://www.googleapis.com/auth/gmail.readonly`
   - Add test users (your email) if in testing mode
   - Save and continue
4. Create OAuth client ID:
   - Application type: "Desktop app"
   - Name: "Email Agent" (or any name you prefer)
   - Click "Create"
5. Download the credentials:
   - Click the download icon next to your newly created OAuth client
   - Save the file as `credentials.json` in the project root directory

## Step 4: First-Time Authentication

When you run the agent for the first time:

1. The script will open a browser window
2. Sign in with your Google account
3. Grant permissions to read your Gmail
4. A `token.json` file will be created automatically (this stores your authentication)

**Note:** The `token.json` file allows the app to access your Gmail without re-authenticating. Keep it secure and don't share it.

## Step 5: Usage

### Basic Usage

```python
from src.GmailEmailAgent import GmailEmailAgent

# Initialize the agent
agent = GmailEmailAgent()

# Connect to Gmail (will open browser on first run)
if agent.connect():
    # Process unread emails
    tasks = agent.process_gmail_emails(max_results=10)
    
    # Display tasks
    for task in tasks:
        print(f"- {task.description} [{task.task_type}] (Priority: {task.priority})")
```

### Advanced Usage

```python
from src.GmailEmailAgent import GmailEmailAgent

agent = GmailEmailAgent()

if agent.connect():
    # Process emails with custom query
    tasks = agent.process_gmail_emails(
        max_results=20,
        query="from:important@example.com",
        fetch_unread=False
    )
    
    # Process emails from last 7 days
    recent_tasks = agent.process_recent_emails(days=7, max_results=50)
    
    # Get tasks by type
    meeting_tasks = agent.get_tasks_by_type("meeting")
    deadline_tasks = agent.get_tasks_by_type("deadline")
    
    # Get high priority tasks
    urgent_tasks = agent.get_tasks_by_priority("high")
    
    # Get summary
    summary = agent.get_task_summary()
    print(summary)
```

## File Structure

After setup, your project should have:

```
email-summarizer-action-taker/
├── credentials.json      # OAuth2 credentials (from Google Cloud Console)
├── token.json           # Auto-generated authentication token
├── requirements.txt
├── src/
│   ├── EmailAgent.py
│   ├── EmailAgent_optimized.py
│   ├── GmailIntegration.py
│   └── GmailEmailAgent.py
└── GMAIL_SETUP.md
```

## Gmail Search Query Examples

You can use Gmail search queries to filter emails:

- `is:unread` - Unread emails
- `from:example@gmail.com` - Emails from specific sender
- `subject:meeting` - Emails with "meeting" in subject
- `has:attachment` - Emails with attachments
- `after:2024/01/01` - Emails after a date
- `before:2024/12/31` - Emails before a date
- `label:important` - Emails with specific label

Combine queries: `is:unread from:boss@company.com subject:urgent`

## Security Notes

1. **Never commit credentials.json or token.json to version control**
   - Add them to `.gitignore`:
     ```
     credentials.json
     token.json
     ```

2. **Token.json contains access tokens**
   - Keep it secure
   - If compromised, revoke access in Google Account settings

3. **Read-only access**
   - The current implementation only reads emails
   - It cannot send, delete, or modify emails

## Troubleshooting

### "Credentials file not found"
- Make sure `credentials.json` is in the project root directory
- Verify the file name is exactly `credentials.json`

### "Access denied" or "Permission denied"
- Check that Gmail API is enabled in Google Cloud Console
- Verify OAuth consent screen is configured
- Make sure you're using the correct Google account

### "Token expired"
- Delete `token.json` and re-authenticate
- The token should auto-refresh, but if it fails, re-authenticate

### "Module not found" errors
- Install dependencies: `pip install -r requirements.txt`
- Make sure you're using Python 3.7+

## Next Steps

- Customize email processing patterns in `EmailAgent_optimized.py`
- Add date extraction from email content
- Set up scheduled runs (cron job, task scheduler)
- Add email filtering and labeling
- Integrate with task management systems

