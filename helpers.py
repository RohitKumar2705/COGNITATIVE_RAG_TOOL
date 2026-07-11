"""
helpers.py - General helper functions for the assignment.
Includes environment setup, logging, validation, and common utilities.
"""

import os
import sys
import logging
import json
from typing import Any, Dict, List, Optional
from pathlib import Path
from dotenv import load_dotenv


# ── Logging Setup ─────────────────────────────────────────────────────────────

def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
) -> logging.Logger:
    """
    Setup logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file to write logs to
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("grid07")
    logger.setLevel(getattr(logging, log_level))
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level))
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    
    # Add console handler
    if not logger.handlers:
        logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, log_level))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# ── Environment Setup ─────────────────────────────────────────────────────────

def load_environment_variables(env_file: str = ".env") -> Dict[str, str]:
    """
    Load environment variables from .env file.
    
    Args:
        env_file: Path to .env file
    
    Returns:
        Dictionary of environment variables
    """
    env_path = Path(env_file)
    
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Loaded environment from {env_file}")
    else:
        print(f"⚠️  {env_file} not found. Using system environment variables.")
    
    return dict(os.environ)


def validate_api_key(key_name: str, required: bool = True) -> Optional[str]:
    """
    Validate that an API key is set.
    
    Args:
        key_name: Name of the environment variable
        required: Whether the key is required
    
    Returns:
        The API key value or None
    
    Raises:
        ValueError: If required key is missing
    """
    value = os.environ.get(key_name)
    
    if not value:
        message = f"Missing API key: {key_name}"
        if required:
            raise ValueError(message)
        else:
            print(f"⚠️  {message}")
    
    return value


# ── File and Path Utilities ───────────────────────────────────────────────────

def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent


def ensure_directory(path: str) -> Path:
    """Ensure a directory exists, create if needed."""
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def read_json_file(filepath: str) -> Dict[str, Any]:
    """
    Read and parse a JSON file.
    
    Args:
        filepath: Path to JSON file
    
    Returns:
        Parsed JSON data
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
        return {}
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {filepath}: {e}")
        return {}


def write_json_file(filepath: str, data: Dict[str, Any], indent: int = 2) -> bool:
    """
    Write data to a JSON file.
    
    Args:
        filepath: Path to write to
        data: Data to write
        indent: JSON indentation level
    
    Returns:
        Success status
    """
    try:
        ensure_directory(os.path.dirname(filepath))
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent)
        return True
    except Exception as e:
        print(f"❌ Error writing JSON to {filepath}: {e}")
        return False


# ── Text and String Utilities ─────────────────────────────────────────────────

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to max length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def clean_text(text: str) -> str:
    """
    Clean and normalize text.
    
    Args:
        text: Text to clean
    
    Returns:
        Cleaned text
    """
    # Remove extra whitespace
    text = ' '.join(text.split())
    # Remove control characters
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
    return text


def extract_json_from_string(text: str) -> Optional[Dict[str, Any]]:
    """
    Extract JSON object from a string (handles markdown formatting).
    
    Args:
        text: Text potentially containing JSON
    
    Returns:
        Parsed JSON or None
    """
    # Remove markdown code fences
    text = text.strip()
    text = text.replace('```json', '').replace('```', '')
    
    # Try to parse JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


# ── Formatting Utilities ──────────────────────────────────────────────────────

def format_section_header(title: str, width: int = 60) -> str:
    """Create a formatted section header."""
    return f"\n{'█' * width}\n   {title}\n{'█' * width}\n"


def format_key_value(key: str, value: Any, indent: int = 2) -> str:
    """Format key-value pair."""
    return f"{' ' * indent}{key}: {value}"


def format_list_item(item: str, indent: int = 3, marker: str = "→") -> str:
    """Format a list item."""
    return f"{' ' * indent}{marker} {item}"


# ── Validation Utilities ──────────────────────────────────────────────────────

def validate_threshold(value: float, min_val: float = 0.0, max_val: float = 1.0) -> bool:
    """Validate similarity threshold."""
    return min_val <= value <= max_val


def validate_bot_id(bot_id: str, valid_ids: List[str] = None) -> bool:
    """Validate bot ID."""
    if valid_ids is None:
        valid_ids = ["bot_a", "bot_b", "bot_c"]
    return bot_id in valid_ids


def validate_text_length(text: str, min_len: int = 1, max_len: int = 10000) -> bool:
    """Validate text length."""
    return min_len <= len(text) <= max_len
