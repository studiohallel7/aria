"""
Core state management for the autonomous agent.
Handles agent state, context, and persistence.
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
import json
import os


class AgentState(Enum):
    """Possible states of the agent."""
    IDLE = "idle"
    THINKING = "thinking"
    EXECUTING = "executing"
    EXPLORING = "exploring"


class OperationMode(Enum):
    """Operation modes of the agent."""
    TRABALHO = "trabalho"  # Work mode - follows user strictly
    LIVRE = "livre"        # Free mode - exploration and learning


@dataclass
class AgentStatus:
    """Current status of the agent."""
    state: AgentState = AgentState.IDLE
    mode: OperationMode = OperationMode.TRABALHO
    current_task: Optional[str] = None
    cycle_count: int = 0
    last_cycle_time: Optional[datetime] = None
    thought_depth: int = 0
    tool_calls_this_cycle: int = 0
    active_account: Optional[str] = None
    error_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "state": self.state.value,
            "mode": self.mode.value,
            "current_task": self.current_task,
            "cycle_count": self.cycle_count,
            "last_cycle_time": self.last_cycle_time.isoformat() if self.last_cycle_time else None,
            "thought_depth": self.thought_depth,
            "tool_calls_this_cycle": self.tool_calls_this_cycle,
            "active_account": self.active_account,
            "error_count": self.error_count,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentStatus":
        return cls(
            state=AgentState(data.get("state", "idle")),
            mode=OperationMode(data.get("mode", "trabalho")),
            current_task=data.get("current_task"),
            cycle_count=data.get("cycle_count", 0),
            last_cycle_time=datetime.fromisoformat(data["last_cycle_time"]) if data.get("last_cycle_time") else None,
            thought_depth=data.get("thought_depth", 0),
            tool_calls_this_cycle=data.get("tool_calls_this_cycle", 0),
            active_account=data.get("active_account"),
            error_count=data.get("error_count", 0),
        )


@dataclass
class ContextItem:
    """An item in the short-term memory context."""
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    priority: int = 0  # Higher = more important
    source: str = "internal"  # internal, user, external, tool
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority,
            "source": self.source,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContextItem":
        return cls(
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            priority=data.get("priority", 0),
            source=data.get("source", "internal"),
        )


class ContextManager:
    """Manages short-term context and working memory."""
    
    def __init__(self, max_items: int = 50):
        self.max_items = max_items
        self.items: List[ContextItem] = []
        self.user_tasks: List[Dict[str, Any]] = []
        self.internal_goals: List[Dict[str, Any]] = []
        
    def add_item(self, content: str, priority: int = 0, source: str = "internal") -> None:
        """Add an item to context."""
        item = ContextItem(content=content, priority=priority, source=source)
        self.items.append(item)
        
        # Sort by priority and trim
        self.items.sort(key=lambda x: (-x.priority, x.timestamp))
        if len(self.items) > self.max_items:
            self.items = self.items[:self.max_items]
    
    def get_context(self, limit: int = 10) -> List[str]:
        """Get recent context items as strings."""
        return [item.content for item in self.items[-limit:]]
    
    def clear_cycle_data(self) -> None:
        """Clear cycle-specific data."""
        self.items = [item for item in self.items if item.priority > 0]
    
    def add_user_task(self, task: str, priority: int = 10) -> None:
        """Add a user task (high priority by default)."""
        self.user_tasks.append({
            "task": task,
            "priority": priority,
            "created_at": datetime.now().isoformat(),
            "status": "pending",
        })
    
    def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """Get all pending tasks sorted by priority."""
        pending = [t for t in self.user_tasks if t["status"] == "pending"]
        pending.sort(key=lambda x: -x["priority"])
        return pending
    
    def complete_task(self, task_idx: int) -> None:
        """Mark a task as completed."""
        if 0 <= task_idx < len(self.user_tasks):
            self.user_tasks[task_idx]["status"] = "completed"
            self.user_tasks[task_idx]["completed_at"] = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": [item.to_dict() for item in self.items],
            "user_tasks": self.user_tasks,
            "internal_goals": self.internal_goals,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], max_items: int = 50) -> "ContextManager":
        ctx = cls(max_items=max_items)
        ctx.items = [ContextItem.from_dict(item) for item in data.get("items", [])]
        ctx.user_tasks = data.get("user_tasks", [])
        ctx.internal_goals = data.get("internal_goals", [])
        return ctx


class StatePersistence:
    """Handles persistence of agent state to disk."""
    
    def __init__(self, base_path: str = "./data/agent"):
        self.base_path = base_path
        self.state_path = os.path.join(base_path, "state.json")
        self.context_path = os.path.join(base_path, "context.json")
        
    def save_state(self, status: AgentStatus) -> None:
        """Save agent status to disk."""
        os.makedirs(os.path.dirname(self.state_path), exist_ok=True)
        with open(self.state_path, 'w') as f:
            json.dump(status.to_dict(), f, indent=2)
    
    def load_state(self) -> Optional[AgentStatus]:
        """Load agent status from disk."""
        if os.path.exists(self.state_path):
            with open(self.state_path, 'r') as f:
                data = json.load(f)
                return AgentStatus.from_dict(data)
        return None
    
    def save_context(self, context_manager: ContextManager) -> None:
        """Save context to disk."""
        os.makedirs(os.path.dirname(self.context_path), exist_ok=True)
        with open(self.context_path, 'w') as f:
            json.dump(context_manager.to_dict(), f, indent=2)
    
    def load_context(self, max_items: int = 50) -> ContextManager:
        """Load context from disk."""
        if os.path.exists(self.context_path):
            with open(self.context_path, 'r') as f:
                data = json.load(f)
                return ContextManager.from_dict(data, max_items=max_items)
        return ContextManager(max_items=max_items)


# Singleton instances
_default_persistence = StatePersistence()


def get_current_state() -> AgentStatus:
    """Get current agent state from disk or create new."""
    state = _default_persistence.load_state()
    if state is None:
        state = AgentStatus()
    return state


def save_current_state(state: AgentStatus) -> None:
    """Save current agent state to disk."""
    _default_persistence.save_state(state)


def get_context_manager(max_items: int = 50) -> ContextManager:
    """Get context manager from disk or create new."""
    return _default_persistence.load_context(max_items=max_items)


def save_context_manager(ctx: ContextManager) -> None:
    """Save context manager to disk."""
    _default_persistence.save_context(ctx)