"""
Grid07 AI Assignment - Cognitative RAG Tool
A three-phase bot assignment system with persona routing, content generation, and debate responses.
"""

__version__ = "1.0.0"
__author__ = "Grid07 Assignment"

# Package configuration
from .helpers import setup_logging, load_environment_variables
from .timeout import timeout_handler, retry_with_timeout
from .method import BaseMethod, MethodRegistry

__all__ = [
    'setup_logging',
    'load_environment_variables',
    'timeout_handler',
    'retry_with_timeout',
    'BaseMethod',
    'MethodRegistry',
]

# Initialize package
try:
    load_environment_variables()
    setup_logging()
except Exception as e:
    print(f"Warning: Could not initialize package: {e}")
