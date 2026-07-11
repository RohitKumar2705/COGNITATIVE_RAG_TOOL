"""
todo.py - Task tracking and TODO management for the assignment.
Provides a simple task tracking system for phases and operations.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
import json
from datetime import datetime


class TaskStatus(Enum):
    """Task status enumeration."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TaskPriority(Enum):
    """Task priority enumeration."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Task:
    """Represents a single task."""
    id: str
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.NOT_STARTED
    priority: TaskPriority = TaskPriority.NORMAL
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    
    def start(self) -> None:
        """Mark task as started."""
        if self.status == TaskStatus.NOT_STARTED:
            self.status = TaskStatus.IN_PROGRESS
            self.started_at = datetime.now().isoformat()
    
    def complete(self) -> None:
        """Mark task as completed."""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now().isoformat()
    
    def fail(self, error_message: str) -> None:
        """Mark task as failed."""
        self.status = TaskStatus.FAILED
        self.error_message = error_message
        self.completed_at = datetime.now().isoformat()
    
    def skip(self) -> None:
        """Mark task as skipped."""
        self.status = TaskStatus.SKIPPED
        self.completed_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert task to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status.value,
            'priority': self.priority.name,
            'created_at': self.created_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'error_message': self.error_message,
        }
    
    def __str__(self) -> str:
        """String representation."""
        icon = {
            TaskStatus.NOT_STARTED: "⭕",
            TaskStatus.IN_PROGRESS: "🔵",
            TaskStatus.COMPLETED: "✅",
            TaskStatus.FAILED: "❌",
            TaskStatus.SKIPPED: "⏭️ ",
        }
        return f"{icon[self.status]} [{self.id}] {self.title} ({self.status.value})"


class TodoList:
    """Manages a list of tasks."""
    
    def __init__(self, name: str = "Assignment Tasks"):
        self.name = name
        self.tasks: Dict[str, Task] = {}
        self._task_counter = 0
    
    def add_task(
        self,
        title: str,
        description: str = "",
        priority: TaskPriority = TaskPriority.NORMAL,
    ) -> Task:
        """Add a new task."""
        self._task_counter += 1
        task_id = f"task_{self._task_counter:03d}"
        
        task = Task(
            id=task_id,
            title=title,
            description=description,
            priority=priority,
        )
        
        self.tasks[task_id] = task
        return task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        return self.tasks.get(task_id)
    
    def update_task_status(self, task_id: str, status: TaskStatus) -> bool:
        """Update task status."""
        task = self.get_task(task_id)
        if not task:
            return False
        
        if status == TaskStatus.IN_PROGRESS:
            task.start()
        elif status == TaskStatus.COMPLETED:
            task.complete()
        elif status == TaskStatus.FAILED:
            task.fail("Manual status update")
        elif status == TaskStatus.SKIPPED:
            task.skip()
        
        return True
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get all tasks with a specific status."""
        return [t for t in self.tasks.values() if t.status == status]
    
    def get_tasks_by_priority(self, priority: TaskPriority) -> List[Task]:
        """Get all tasks with a specific priority."""
        return [t for t in self.tasks.values() if t.priority == priority]
    
    def get_pending_tasks(self) -> List[Task]:
        """Get all pending (not started or in progress) tasks."""
        return [
            t for t in self.tasks.values()
            if t.status in [TaskStatus.NOT_STARTED, TaskStatus.IN_PROGRESS]
        ]
    
    def get_completed_tasks(self) -> List[Task]:
        """Get all completed tasks."""
        return self.get_tasks_by_status(TaskStatus.COMPLETED)
    
    def get_failed_tasks(self) -> List[Task]:
        """Get all failed tasks."""
        return self.get_tasks_by_status(TaskStatus.FAILED)
    
    def get_progress(self) -> Dict[str, int]:
        """Get progress statistics."""
        total = len(self.tasks)
        
        if total == 0:
            return {'total': 0, 'completed': 0, 'percentage': 0}
        
        completed = len(self.get_completed_tasks())
        percentage = (completed / total) * 100
        
        return {
            'total': total,
            'completed': completed,
            'pending': len(self.get_pending_tasks()),
            'failed': len(self.get_failed_tasks()),
            'percentage': round(percentage, 1),
        }
    
    def print_summary(self) -> None:
        """Print task summary."""
        progress = self.get_progress()
        
        print(f"\n📋 {self.name}")
        print(f"   Total: {progress['total']} | Completed: {progress['completed']} | "
              f"Progress: {progress['percentage']}%\n")
        
        # Print tasks sorted by priority
        sorted_tasks = sorted(
            self.tasks.values(),
            key=lambda t: t.priority.value,
            reverse=True,
        )
        
        for task in sorted_tasks:
            print(f"   {task}")
    
    def save_to_json(self, filepath: str) -> bool:
        """Save tasks to JSON file."""
        try:
            data = {
                'name': self.name,
                'created_at': datetime.now().isoformat(),
                'tasks': [task.to_dict() for task in self.tasks.values()],
                'progress': self.get_progress(),
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            print(f"✅ Saved tasks to {filepath}")
            return True
        except Exception as e:
            print(f"❌ Error saving tasks: {e}")
            return False
    
    def load_from_json(self, filepath: str) -> bool:
        """Load tasks from JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.name = data.get('name', 'Assignment Tasks')
            self.tasks.clear()
            
            for task_data in data.get('tasks', []):
                task = Task(
                    id=task_data['id'],
                    title=task_data['title'],
                    description=task_data['description'],
                    status=TaskStatus(task_data['status']),
                    priority=TaskPriority[task_data['priority']],
                    created_at=task_data['created_at'],
                    started_at=task_data['started_at'],
                    completed_at=task_data['completed_at'],
                    error_message=task_data['error_message'],
                )
                self.tasks[task.id] = task
            
            print(f"✅ Loaded tasks from {filepath}")
            return True
        except Exception as e:
            print(f"❌ Error loading tasks: {e}")
            return False


# ── Predefined Task Lists ─────────────────────────────────────────────────────

def create_assignment_tasks() -> TodoList:
    """Create the main assignment task list."""
    todos = TodoList("Grid07 Assignment Tasks")
    
    # Phase 1 tasks
    todos.add_task(
        "Phase 1: Build persona index",
        "Create FAISS index from bot personas",
        TaskPriority.HIGH,
    )
    todos.add_task(
        "Phase 1: Route posts to bots",
        "Match incoming posts to appropriate bot personas",
        TaskPriority.HIGH,
    )
    
    # Phase 2 tasks
    todos.add_task(
        "Phase 2: Decide search query",
        "LLM decides what topic to post about",
        TaskPriority.NORMAL,
    )
    todos.add_task(
        "Phase 2: Execute web search",
        "Search for recent news on selected topic",
        TaskPriority.NORMAL,
    )
    todos.add_task(
        "Phase 2: Draft post content",
        "Generate opinionated post under 280 chars",
        TaskPriority.NORMAL,
    )
    
    # Phase 3 tasks
    todos.add_task(
        "Phase 3: Build thread context",
        "Construct RAG context from thread history",
        TaskPriority.NORMAL,
    )
    todos.add_task(
        "Phase 3: Generate defense reply",
        "Generate in-character reply to challenge",
        TaskPriority.NORMAL,
    )
    todos.add_task(
        "Phase 3: Detect prompt injection",
        "Identify and resist prompt injection attacks",
        TaskPriority.HIGH,
    )
    
    return todos
