"""
method.py - Base methods and method registry for the assignment.
Provides abstract base classes and patterns for phases.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import json


# ── Data Classes ──────────────────────────────────────────────────────────────

@dataclass
class BotPersona:
    """Represents a bot persona."""
    bot_id: str
    name: str
    description: str
    
    def to_dict(self) -> Dict[str, str]:
        return {
            'bot_id': self.bot_id,
            'name': self.name,
            'description': self.description,
        }


@dataclass
class SearchResult:
    """Represents a search result."""
    bot_id: str
    name: str
    similarity: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'bot_id': self.bot_id,
            'name': self.name,
            'similarity': self.similarity,
        }


@dataclass
class ContentPost:
    """Represents a generated content post."""
    bot_id: str
    topic: str
    post_content: str
    
    def to_dict(self) -> Dict[str, str]:
        return {
            'bot_id': self.bot_id,
            'topic': self.topic,
            'post_content': self.post_content,
        }


@dataclass
class ThreadMessage:
    """Represents a message in a thread."""
    author: str
    content: str
    
    def to_dict(self) -> Dict[str, str]:
        return {
            'author': self.author,
            'content': self.content,
        }


# ── Base Classes ──────────────────────────────────────────────────────────────

class BaseMethod(ABC):
    """Abstract base class for phase methods."""
    
    def __init__(self, name: str):
        self.name = name
        self.results: Dict[str, Any] = {}
        self.errors: List[str] = []
    
    @abstractmethod
    def execute(self, **kwargs) -> bool:
        """Execute the method."""
        pass
    
    @abstractmethod
    def validate_input(self, **kwargs) -> bool:
        """Validate input parameters."""
        pass
    
    def get_result(self) -> Dict[str, Any]:
        """Get execution result."""
        return self.results.copy()
    
    def get_errors(self) -> List[str]:
        """Get any errors from execution."""
        return self.errors.copy()
    
    def add_error(self, error: str) -> None:
        """Add an error message."""
        self.errors.append(f"[{self.name}] {error}")
    
    def clear_errors(self) -> None:
        """Clear error list."""
        self.errors.clear()
    
    def to_json(self) -> str:
        """Convert results to JSON."""
        return json.dumps(self.results, indent=2)


class MethodRegistry:
    """Registry for managing methods."""
    
    def __init__(self):
        self._methods: Dict[str, BaseMethod] = {}
    
    def register(self, method: BaseMethod) -> None:
        """Register a method."""
        self._methods[method.name] = method
    
    def get(self, name: str) -> Optional[BaseMethod]:
        """Get a registered method."""
        return self._methods.get(name)
    
    def execute(self, name: str, **kwargs) -> bool:
        """Execute a registered method."""
        method = self.get(name)
        if not method:
            raise ValueError(f"Method '{name}' not registered")
        
        # Validate input
        if not method.validate_input(**kwargs):
            raise ValueError(f"Invalid input for method '{name}'")
        
        # Execute
        return method.execute(**kwargs)
    
    def get_result(self, name: str) -> Dict[str, Any]:
        """Get result from a method."""
        method = self.get(name)
        if not method:
            raise ValueError(f"Method '{name}' not registered")
        return method.get_result()
    
    def get_errors(self, name: str) -> List[str]:
        """Get errors from a method."""
        method = self.get(name)
        if not method:
            return []
        return method.get_errors()
    
    def list_methods(self) -> List[str]:
        """List all registered methods."""
        return list(self._methods.keys())


# ── Helper Methods ───────────────────────────────────────────────────────────

def validate_bot_personas(personas: Dict[str, Dict[str, str]]) -> bool:
    """
    Validate bot personas dictionary.
    
    Args:
        personas: Dictionary of personas
    
    Returns:
        True if valid
    """
    if not isinstance(personas, dict):
        return False
    
    required_fields = {'name', 'description'}
    
    for bot_id, persona in personas.items():
        if not isinstance(persona, dict):
            return False
        if not required_fields.issubset(persona.keys()):
            return False
    
    return True


def validate_search_results(results: List[Dict[str, Any]]) -> bool:
    """
    Validate search results format.
    
    Args:
        results: List of search results
    
    Returns:
        True if valid
    """
    if not isinstance(results, list):
        return False
    
    required_fields = {'bot_id', 'name', 'similarity'}
    
    for result in results:
        if not isinstance(result, dict):
            return False
        if not required_fields.issubset(result.keys()):
            return False
        if not isinstance(result['similarity'], (int, float)):
            return False
        if not (0 <= result['similarity'] <= 1):
            return False
    
    return True


def validate_content_post(post: Dict[str, Any]) -> bool:
    """
    Validate content post format.
    
    Args:
        post: Content post dictionary
    
    Returns:
        True if valid
    """
    required_fields = {'bot_id', 'topic', 'post_content'}
    
    if not isinstance(post, dict):
        return False
    
    if not required_fields.issubset(post.keys()):
        return False
    
    if not isinstance(post['post_content'], str):
        return False
    
    if len(post['post_content']) > 280:
        return False
    
    return True


# ── Error Handling ───────────────────────────────────────────────────────────

class MethodError(Exception):
    """Custom exception for method errors."""
    pass


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class ExecutionError(Exception):
    """Custom exception for execution errors."""
    pass
