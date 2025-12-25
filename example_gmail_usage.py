"""
Example usage of GmailEmailAgent.

This script demonstrates how to use the Gmail-integrated EmailAgent.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from GmailEmailAgent import GmailEmailAgent
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Main function to demonstrate GmailEmailAgent usage."""
    
    print("=" * 60)
    print("Gmail Email Agent - Example Usage")
    print("=" * 60)
    
    # Initialize the agent
    print("\n1. Initializing GmailEmailAgent...")
    agent = GmailEmailAgent(
        credentials_path="credentials.json",
        token_path="token.json"
    )
    
    # Connect to Gmail
    print("\n2. Connecting to Gmail...")
    print("   (This will open a browser for first-time authentication)")
    if not agent.connect():
        print("   ❌ Failed to authenticate with Gmail")
        print("   Please check your credentials.json file and try again.")
        return
    
    print("   ✅ Successfully authenticated!")
    
    # Process unread emails
    print("\n3. Processing unread emails...")
    tasks = agent.process_gmail_emails(
        max_results=10,
        fetch_unread=True
    )
    
    if not tasks:
        print("   No tasks created from unread emails.")
    else:
        print(f"   ✅ Created {len(tasks)} tasks from emails")
    
    # Display all tasks
    print("\n" + "=" * 60)
    print("ALL TASKS")
    print("=" * 60)
    for i, task in enumerate(agent.tasks, 1):
        print(f"\n{i}. {task.description}")
        print(f"   Type: {task.task_type}")
        print(f"   Priority: {task.priority}")
        print(f"   Created: {task.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        if task.source_email and 'from' in task.source_email:
            print(f"   From: {task.source_email['from']}")
    
    # Display task summary
    print("\n" + "=" * 60)
    print("TASK SUMMARY")
    print("=" * 60)
    summary = agent.get_task_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    # Display tasks by type
    print("\n" + "=" * 60)
    print("TASKS BY TYPE")
    print("=" * 60)
    
    meeting_tasks = agent.get_tasks_by_type("meeting")
    deadline_tasks = agent.get_tasks_by_type("deadline")
    misc_tasks = agent.get_tasks_by_type("misc")
    
    print(f"\nMeetings: {len(meeting_tasks)}")
    for task in meeting_tasks:
        print(f"  - {task.description}")
    
    print(f"\nDeadlines: {len(deadline_tasks)}")
    for task in deadline_tasks:
        print(f"  - {task.description}")
    
    print(f"\nMisc: {len(misc_tasks)}")
    for task in misc_tasks:
        print(f"  - {task.description}")
    
    # Display high priority tasks
    print("\n" + "=" * 60)
    print("HIGH PRIORITY TASKS")
    print("=" * 60)
    high_priority = agent.get_tasks_by_priority("high")
    if high_priority:
        for task in high_priority:
            print(f"  ⚠️  {task.description} [{task.task_type}]")
    else:
        print("  No high priority tasks found.")
    
    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()

