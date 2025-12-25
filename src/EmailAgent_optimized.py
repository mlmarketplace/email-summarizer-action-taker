"""
Optimized EmailAgent with improved performance, error handling, and functionality.
"""

import re
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Task:
    """Represents a task created from an email."""
    description: str
    task_type: str
    created_at: datetime = field(default_factory=datetime.now)
    priority: str = "normal"
    source_email: Optional[Dict[str, Any]] = None

    def __hash__(self):
        """Make Task hashable for deduplication."""
        return hash((self.description, self.task_type))

    def __eq__(self, other):
        """Compare tasks for equality."""
        if not isinstance(other, Task):
            return False
        return self.description == other.description and self.task_type == other.task_type


class EmailAgent:
    """Optimized email agent that processes emails and creates tasks."""
    
    # Class constants for patterns and keywords
    MEETING_KEYWORDS = r'\b(meeting|meetings|schedule|appointment|call|conference)\b'
    DEADLINE_KEYWORDS = r'\b(deadline|deadlines|due|submit|deliver|urgent)\b'
    HIGH_PRIORITY_KEYWORDS = r'\b(urgent|asap|immediately|critical|important)\b'
    
    def __init__(self):
        """Initialize the EmailAgent."""
        self.tasks: List[Task] = []
        self.processed_emails: set = set()  # Track processed emails to avoid duplicates
        
        # Compile regex patterns for better performance
        self.meeting_pattern = re.compile(self.MEETING_KEYWORDS, re.IGNORECASE)
        self.deadline_pattern = re.compile(self.DEADLINE_KEYWORDS, re.IGNORECASE)
        self.priority_pattern = re.compile(self.HIGH_PRIORITY_KEYWORDS, re.IGNORECASE)

    def perceive(self, emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Collect and validate raw emails.
        
        Args:
            emails: List of email dictionaries with 'subject' and 'body' keys
            
        Returns:
            Filtered list of valid emails
        """
        if not emails:
            logger.warning("No emails provided to perceive")
            return []
        
        valid_emails = []
        for email in emails:
            try:
                # Validate email structure
                if not isinstance(email, dict):
                    logger.warning(f"Invalid email format: {type(email)}")
                    continue
                
                if "subject" not in email and "body" not in email:
                    logger.warning("Email missing both subject and body")
                    continue
                
                # Create email hash for deduplication
                email_hash = hash((email.get("subject", ""), email.get("body", "")))
                if email_hash in self.processed_emails:
                    logger.debug(f"Skipping duplicate email: {email.get('subject', 'No subject')}")
                    continue
                
                self.processed_emails.add(email_hash)
                valid_emails.append(email)
                
            except Exception as e:
                logger.error(f"Error processing email: {e}")
                continue
        
        logger.info(f"Processed {len(valid_emails)} valid emails out of {len(emails)}")
        return valid_emails

    def reason(self, email: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract key info using optimized pattern matching.
        
        Args:
            email: Email dictionary with 'subject' and 'body' keys
            
        Returns:
            Dictionary with 'type', 'priority', and 'content'
        """
        try:
            subject = email.get("subject", "")
            body = email.get("body", "")
            
            # Combine subject and body for analysis (more efficient than separate checks)
            combined_text = f"{subject} {body}"
            
            # Determine priority first (can be used for any type)
            priority = "high" if self.priority_pattern.search(combined_text) else "normal"
            
            # Determine email type using compiled regex patterns
            if self.meeting_pattern.search(combined_text):
                email_type = "meeting"
            elif self.deadline_pattern.search(combined_text):
                email_type = "deadline"
            else:
                email_type = "misc"
            
            return {
                "type": email_type,
                "priority": priority,
                "content": email
            }
            
        except Exception as e:
            logger.error(f"Error in reason() for email: {e}")
            return {
                "type": "misc",
                "priority": "normal",
                "content": email
            }

    def act(self, info: Dict[str, Any]) -> List[Task]:
        """
        Create tasks depending on type, with deduplication.
        
        Args:
            info: Dictionary with 'type', 'priority', and 'content' keys
            
        Returns:
            List of all tasks
        """
        try:
            task_type = info.get("type", "misc")
            priority = info.get("priority", "normal")
            email = info.get("content", {})
            
            # Create task description based on type
            task_descriptions = {
                "meeting": "Follow up on meeting request.",
                "deadline": "Check upcoming deadline.",
                "misc": "Review misc email."
            }
            
            description = task_descriptions.get(task_type, "Review email.")
            
            # Create new task
            new_task = Task(
                description=description,
                task_type=task_type,
                priority=priority,
                source_email=email
            )
            
            # Deduplication: only add if task doesn't already exist
            if new_task not in self.tasks:
                self.tasks.append(new_task)
                logger.info(f"Created new task: {description} (type: {task_type}, priority: {priority})")
            else:
                logger.debug(f"Skipping duplicate task: {description}")
            
            return self.tasks
            
        except Exception as e:
            logger.error(f"Error in act(): {e}")
            return self.tasks

    def get_tasks_by_type(self, task_type: str) -> List[Task]:
        """Get all tasks of a specific type."""
        return [task for task in self.tasks if task.task_type == task_type]

    def get_tasks_by_priority(self, priority: str) -> List[Task]:
        """Get all tasks of a specific priority."""
        return [task for task in self.tasks if task.priority == priority]

    def remove_task(self, task: Task) -> bool:
        """Remove a specific task if it exists."""
        if task in self.tasks:
            self.tasks.remove(task)
            logger.info(f"Removed task: {task.description}")
            return True
        return False

    def get_task_summary(self) -> Dict[str, int]:
        """Get summary statistics of tasks."""
        summary = defaultdict(int)
        for task in self.tasks:
            summary[task.task_type] += 1
            summary[f"{task.task_type}_{task.priority}"] += 1
        return dict(summary)


# --- Example usage ---
if __name__ == "__main__":
    emails = [
        {"subject": "Team Meeting Tomorrow", "body": "Please confirm attendance."},
        {"subject": "Deadline Reminder", "body": "Submit report by Friday. Urgent!"},
        {"subject": "Team Meeting Tomorrow", "body": "Please confirm attendance."},  # Duplicate
        {"subject": "Weekly Update", "body": "Here's what happened this week."}
    ]

    agent = EmailAgent()

    # Process emails
    valid_emails = agent.perceive(emails)
    
    for email in valid_emails:
        info = agent.reason(email)
        agent.act(info)

    # Display results
    print("\n=== Tasks Created ===")
    for i, task in enumerate(agent.tasks, 1):
        print(f"{i}. {task.description} [{task.task_type}] (Priority: {task.priority})")
    
    print("\n=== Task Summary ===")
    print(agent.get_task_summary())
    
    print(f"\n=== High Priority Tasks ===")
    high_priority = agent.get_tasks_by_priority("high")
    for task in high_priority:
        print(f"- {task.description}")

