# Email-Summarizer-Action-Taker

An intelligent email agent that processes emails and creates actionable tasks.

## Features

- **Email Processing**: Reads and analyzes incoming emails
- **Intelligent Reasoning**: Identifies email types (meetings, deadlines, etc.) using pattern matching
- **Task Creation**: Automatically creates tasks based on email content
- **Priority Detection**: Identifies high-priority emails (urgent, asap, critical)
- **Gmail Integration**: Direct integration with Gmail API for real-time email processing
- **Task Management**: Query, filter, and manage tasks by type and priority

## Quick Start

### Basic Usage (Mock Data)

```python
from src.EmailAgent_optimized import EmailAgent

emails = [
    {"subject": "Team Meeting Tomorrow", "body": "Please confirm attendance."},
    {"subject": "Deadline Reminder", "body": "Submit report by Friday. Urgent!"}
]

agent = EmailAgent()
valid_emails = agent.perceive(emails)

for email in valid_emails:
    info = agent.reason(email)
    agent.act(info)

print(agent.tasks)
```

### Gmail Integration

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Gmail API credentials** (see [GMAIL_SETUP.md](GMAIL_SETUP.md) for detailed instructions)

3. **Use GmailEmailAgent:**
   ```python
   from src.GmailEmailAgent import GmailEmailAgent
   
   agent = GmailEmailAgent()
   if agent.connect():
       tasks = agent.process_gmail_emails(max_results=10)
       for task in tasks:
           print(f"- {task.description} [{task.task_type}]")
   ```

See `example_gmail_usage.py` for a complete example.

## Project Structure

```
email-summarizer-action-taker/
├── src/
│   ├── EmailAgent.py              # Original basic agent
│   ├── EmailAgent_optimized.py    # Optimized agent with enhanced features
│   ├── GmailIntegration.py        # Gmail API integration module
│   └── GmailEmailAgent.py          # Gmail-enabled agent
├── requirements.txt                # Python dependencies
├── GMAIL_SETUP.md                  # Gmail API setup guide
├── example_gmail_usage.py          # Example usage script
└── README.md
```

## Documentation

- **[GMAIL_SETUP.md](GMAIL_SETUP.md)**: Complete guide for setting up Gmail API integration
- **[OPTIMIZATION_SUGGESTIONS.md](OPTIMIZATION_SUGGESTIONS.md)**: Code review and optimization suggestions
- **[IMPROVEMENTS_SUMMARY.md](IMPROVEMENTS_SUMMARY.md)**: Summary of improvements made

## Features in Detail

### Email Types Detected
- **Meetings**: Identifies meeting requests, appointments, calls
- **Deadlines**: Detects deadline reminders, submission dates
- **Misc**: General emails that don't match specific patterns

### Priority Levels
- **High**: Emails containing urgent, asap, immediately, critical, important
- **Normal**: All other emails

### Task Management
- Get tasks by type: `get_tasks_by_type("meeting")`
- Get tasks by priority: `get_tasks_by_priority("high")`
- Get summary statistics: `get_task_summary()`
- Remove tasks: `remove_task(task)`

## Requirements

- Python 3.7+
- Google API credentials (for Gmail integration)
- See `requirements.txt` for Python packages

## Security Note

⚠️ **Never commit `credentials.json` or `token.json` to version control!**

These files contain sensitive authentication information. They are automatically excluded via `.gitignore`.

## License

This project is open source and available for use.
