"""
timeout.py - Timeout and retry utilities for the assignment.
Provides decorators and context managers for handling timeouts and retries.
"""

import time
import functools
from typing import Callable, Any, Optional, TypeVar
import signal
import sys

T = TypeVar('T')


class TimeoutError(Exception):
    """Custom timeout exception."""
    pass


def timeout_handler(signum, frame):
    """Signal handler for timeout."""
    raise TimeoutError("Operation timed out")


def set_timeout(seconds: int) -> None:
    """
    Set a timeout for the current operation.
    
    Args:
        seconds: Timeout in seconds
    """
    if sys.platform != "win32":  # signal.alarm not available on Windows
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(seconds)


def clear_timeout() -> None:
    """Clear any pending timeout."""
    if sys.platform != "win32":
        signal.alarm(0)


def retry_with_timeout(
    max_retries: int = 3,
    timeout_seconds: int = 30,
    backoff_factor: float = 1.5,
    allowed_exceptions: tuple = (Exception,),
) -> Callable:
    """
    Decorator for retrying a function with timeout.
    
    Args:
        max_retries: Maximum number of retry attempts
        timeout_seconds: Timeout for each attempt in seconds
        backoff_factor: Multiplicative factor for exponential backoff
        allowed_exceptions: Tuple of exceptions to catch and retry
    
    Returns:
        Decorated function
    
    Example:
        @retry_with_timeout(max_retries=3, timeout_seconds=10)
        def my_function():
            pass
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            wait_time = 1
            
            for attempt in range(1, max_retries + 1):
                try:
                    print(f"[Attempt {attempt}/{max_retries}] Calling {func.__name__}...")
                    
                    # Set timeout
                    set_timeout(timeout_seconds)
                    
                    try:
                        result = func(*args, **kwargs)
                        clear_timeout()
                        print(f"✅ {func.__name__} succeeded on attempt {attempt}")
                        return result
                    finally:
                        clear_timeout()
                        
                except allowed_exceptions as e:
                    last_exception = e
                    print(f"❌ Attempt {attempt} failed: {str(e)[:100]}")
                    
                    if attempt < max_retries:
                        print(f"   Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        wait_time *= backoff_factor
                    else:
                        print(f"   No more retries. Total attempts: {max_retries}")
            
            # All retries exhausted
            if last_exception:
                raise last_exception
            else:
                raise RuntimeError(f"Function {func.__name__} failed after {max_retries} retries")
        
        return wrapper
    return decorator


class TimeoutContext:
    """Context manager for timeout operations."""
    
    def __init__(self, seconds: int, message: str = "Operation timed out"):
        self.seconds = seconds
        self.message = message
    
    def __enter__(self):
        set_timeout(self.seconds)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        clear_timeout()
        if exc_type is TimeoutError:
            print(f"⏱️  {self.message}")
            return False
        return False


def measure_time(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to measure execution time of a function."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> T:
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        print(f"⏱️  {func.__name__} took {elapsed:.2f}s")
        return result
    return wrapper
