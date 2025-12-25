"""
Email Agent Package

This package provides email processing and task creation functionality
with optional Gmail API integration.
"""

from .EmailAgent_optimized import EmailAgent, Task
from .GmailIntegration import GmailIntegration
from .GmailEmailAgent import GmailEmailAgent

__all__ = ['EmailAgent', 'Task', 'GmailIntegration', 'GmailEmailAgent']
__version__ = '1.0.0'

