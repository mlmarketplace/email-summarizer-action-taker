
from datetime import datetime, timedelta

class EmailAgent:
    def __init__(self):
        self.tasks = []

    def perceive(self, emails):
        """Collect raw emails."""
        return emails

    def reason(self, email):
        """Extract key info using simple pattern matching."""
        subject = email.get("subject", "").lower()
        body = email.get("body", "").lower()

        if "meeting" in subject or "meeting" in body:
            return {"type": "meeting", "content": email}
        if "deadline" in subject or "deadline" in body:
            return {"type": "deadline", "content": email}
        return {"type": "misc", "content": email}

    def act(self, info):
        """Create tasks depending on type."""
        if info["type"] == "meeting":
            self.tasks.append("Follow up on meeting request.")
        elif info["type"] == "deadline":
            self.tasks.append("Check upcoming deadline.")
        else:
            self.tasks.append("Review misc email.")
        return self.tasks

# --- Example usage ---
emails = [
    {"subject": "Team Meeting Tomorrow", "body": "Please confirm attendance."},
    {"subject": "Deadline Reminder", "body": "Submit report by Friday."}
]

agent = EmailAgent()

for email in agent.perceive(emails):
    info = agent.reason(email)
    agent.act(info)

print(agent.tasks)
