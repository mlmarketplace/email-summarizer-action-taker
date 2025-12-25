# Quick Start Guide - Gmail Integration

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Setup (First Time Only)

1. **Get Gmail API Credentials:**
   - Follow the detailed guide in [GMAIL_SETUP.md](GMAIL_SETUP.md)
   - Download `credentials.json` from Google Cloud Console
   - Place it in the project root directory

2. **Run the example:**
   ```bash
   python example_gmail_usage.py
   ```
   - First run will open a browser for authentication
   - Grant permissions to read Gmail
   - `token.json` will be created automatically

## Basic Usage

```python
from src.GmailEmailAgent import GmailEmailAgent

# Initialize and connect
agent = GmailEmailAgent()
agent.connect()

# Process unread emails
tasks = agent.process_gmail_emails(max_results=10)

# View tasks
for task in tasks:
    print(f"{task.description} - {task.task_type} - {task.priority}")
```

## Common Use Cases

### Process Unread Emails
```python
tasks = agent.process_gmail_emails(max_results=20, fetch_unread=True)
```

### Process Emails from Last 7 Days
```python
tasks = agent.process_recent_emails(days=7, max_results=50)
```

### Custom Gmail Query
```python
tasks = agent.process_gmail_emails(
    max_results=10,
    query="from:boss@company.com subject:urgent",
    fetch_unread=False
)
```

### Filter Tasks
```python
# Get meeting tasks
meetings = agent.get_tasks_by_type("meeting")

# Get urgent tasks
urgent = agent.get_tasks_by_priority("high")

# Get summary
summary = agent.get_task_summary()
```

## Troubleshooting

**"Credentials file not found"**
- Make sure `credentials.json` is in the project root
- Download it from Google Cloud Console

**"Module not found"**
- Run: `pip install -r requirements.txt`

**"Access denied"**
- Check Gmail API is enabled in Google Cloud Console
- Verify OAuth consent screen is configured

For more details, see [GMAIL_SETUP.md](GMAIL_SETUP.md)

