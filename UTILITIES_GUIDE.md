# Grid07 AI Assignment - Utility Files Guide

## Overview
This project includes several utility modules to make the code run smoothly and easily. These utility files are organized for better structure, error handling, and maintainability.

---

## Utility Files

### 1. **__init__.py**
Package initialization file that imports and configures all utility modules.
- Initializes logging and environment variables on import
- Exports commonly used functions
- Handles initialization errors gracefully

**Usage:**
```python
from helpers import setup_logging
from timeout import retry_with_timeout
```

---

### 2. **helpers.py** - General Utilities
Provides general helper functions for environment setup, logging, validation, and file operations.

**Key Functions:**
- `setup_logging()` - Configure application logging
- `load_environment_variables()` - Load .env file
- `validate_api_key()` - Verify API keys are set
- `read_json_file()` / `write_json_file()` - JSON file operations
- `truncate_text()` - Truncate text safely
- `extract_json_from_string()` - Parse JSON from text with markdown handling
- `validate_threshold()` - Validate similarity thresholds
- `validate_bot_id()` - Verify bot IDs
- `format_section_header()` - Create formatted headers

**Example:**
```python
from helpers import setup_logging, load_environment_variables

logger = setup_logging(log_level="INFO")
load_environment_variables()
logger.info("Application started")
```

---

### 3. **timeout.py** - Timeout & Retry Management
Provides timeout handling and retry logic with exponential backoff.

**Key Functions:**
- `@retry_with_timeout()` - Decorator for retrying with timeout
- `TimeoutContext` - Context manager for operations with timeout
- `@measure_time()` - Decorator to measure execution time

**Features:**
- Automatic retry with exponential backoff
- Timeout per attempt
- Exception filtering
- Detailed logging of retry attempts

**Example:**
```python
from timeout import retry_with_timeout, measure_time

@retry_with_timeout(max_retries=3, timeout_seconds=30)
@measure_time
def api_call():
    # Function will retry up to 3 times if it fails
    # Each attempt has 30 second timeout
    pass

api_call()
```

---

### 4. **utility.py** - Array & Embedding Operations
Utilities for numpy arrays, embeddings, and FAISS operations.

**Key Functions:**
- `normalize_embedding()` - Normalize embedding vectors
- `compute_cosine_similarity()` - Calculate similarity between vectors
- `batch_normalize_embeddings()` - Normalize multiple embeddings
- `create_faiss_index()` - Build FAISS index
- `search_faiss_index()` - Query FAISS index
- `stack_embeddings()` - Combine embeddings into matrix
- `compute_embedding_statistics()` - Get embedding stats
- `batch_compute_similarities()` - Pairwise similarity matrix

**Example:**
```python
from utility import normalize_embedding, compute_cosine_similarity

emb1 = normalize_embedding(np.array([1, 2, 3]))
emb2 = normalize_embedding(np.array([3, 2, 1]))
similarity = compute_cosine_similarity(emb1, emb2)
```

---

### 5. **method.py** - Base Classes & Registry
Provides abstract base classes and patterns for structuring phases.

**Key Classes:**
- `BaseMethod` - Abstract base class for phase implementations
- `MethodRegistry` - Registry for managing methods
- `BotPersona` - Bot persona dataclass
- `SearchResult` - Search result dataclass
- `ContentPost` - Generated post dataclass
- `ThreadMessage` - Thread message dataclass

**Validation Functions:**
- `validate_bot_personas()` - Validate persona format
- `validate_search_results()` - Validate search results
- `validate_content_post()` - Validate post format

**Example:**
```python
from method import BaseMethod, MethodRegistry

class MyPhase(BaseMethod):
    def execute(self, **kwargs):
        # Implementation
        pass
    
    def validate_input(self, **kwargs):
        return True

registry = MethodRegistry()
registry.register(MyPhase("phase1"))
registry.execute("phase1")
```

---

### 6. **todo.py** - Task Tracking
Task management system for tracking progress through phases.

**Key Classes:**
- `Task` - Individual task with status tracking
- `TodoList` - Collection of tasks
- `TaskStatus` - Enum for task states (not_started, in_progress, completed, failed, skipped)
- `TaskPriority` - Enum for priority levels

**Key Methods:**
- `add_task()` - Add a new task
- `update_task_status()` - Update task status
- `get_progress()` - Get progress statistics
- `save_to_json()` / `load_from_json()` - Persist tasks
- `print_summary()` - Print task summary

**Example:**
```python
from todo import create_assignment_tasks, TaskStatus

todos = create_assignment_tasks()
task = todos.get_task("task_001")
task.start()
# ... do work ...
task.complete()

todos.print_summary()
todos.save_to_json("tasks.json")
```

---

## Running the Assignment

### Option 1: Enhanced Main (Recommended)
```bash
python main_enhanced.py
```
This uses all utility modules for robust error handling and logging.

### Option 2: Basic Main
```bash
python main.py
```
This is the simpler version with basic functionality.

---

## File Structure
```
COGNITATIVE_RAG_TOOL/
├── __init__.py                 # Package initialization
├── helpers.py                  # General utilities
├── timeout.py                  # Timeout & retry handling
├── utility.py                  # Array/embedding utilities
├── method.py                   # Base classes & registry
├── todo.py                     # Task tracking
├── main_enhanced.py            # Enhanced main runner (recommended)
├── main.py                     # Basic main runner
├── PHASE1_ROUTER.PY            # Phase 1: Persona routing
├── phase2_content_engine.py    # Phase 2: Content generation
├── phase3_combat_engine.py     # Phase 3: Defense replies
├── .env                        # Environment variables
├── tasks.json                  # Saved task progress
└── r.txt                       # Requirements file
```

---

## Features

### ✅ Error Handling
- Automatic retry with exponential backoff
- Timeout protection for API calls
- Graceful error reporting and logging

### ✅ Logging
- Structured logging with timestamps
- Configurable log levels
- Optional file logging

### ✅ Task Tracking
- Real-time task progress monitoring
- Save/load task state to JSON
- Priority-based task organization

### ✅ Data Validation
- Input validation for all major operations
- Type checking for embeddings and results
- Format validation for posts and searches

### ✅ Performance Monitoring
- Execution time tracking
- Embedding statistics
- Progress percentage

---

## Best Practices

### 1. Use Retry Decorators
```python
@retry_with_timeout(max_retries=3, timeout_seconds=30)
def critical_api_call():
    # Your code here
    pass
```

### 2. Validate Input Data
```python
from method import validate_search_results

if validate_search_results(results):
    # Process results
    pass
```

### 3. Track Tasks
```python
from todo import create_assignment_tasks

todos = create_assignment_tasks()
task = todos.get_task("task_001")
task.start()
# ... work ...
task.complete()
```

### 4. Use Helper Functions
```python
from helpers import setup_logging, validate_api_key

logger = setup_logging()
api_key = validate_api_key("GOOGLE_API_KEY")
```

---

## Environment Variables Required

Create a `.env` file with:
```
GOOGLE_API_KEY=your_api_key_here
```

---

## Troubleshooting

### Timeout Errors
- Increase `timeout_seconds` in decorator
- Check API rate limits
- Monitor network connectivity

### Import Errors
- Ensure all utility files are in the project directory
- Check Python path includes project root
- Verify file names match (case-sensitive on Linux)

### API Errors
- Validate API key is set correctly
- Check rate limits
- Verify embeddings model name

### Task Tracking Issues
- Ensure write permissions for `tasks.json`
- Check JSON file format
- Clear corrupted `tasks.json` and start fresh

---

## Contributing

To extend the utilities:
1. Add new helper functions to appropriate modules
2. Follow existing naming conventions
3. Add docstrings for all functions
4. Test before committing

---

## Version
Grid07 AI Assignment v1.0.0
