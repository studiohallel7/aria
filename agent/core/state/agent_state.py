"""
Agente State - Gerenciamento de estado do agente

Estados possíveis:
- IDLE: Ocioso, aguardando gatilhos
- THINKING: Processando informações, planejando
- EXECUTING: Executando ações
- EXPLORING: Explorando ativamente (modo livre)
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
import json
import os


class AgentState(Enum):
    IDLE = "idle"
    THINKING = "thinking"
    EXECUTING = "executing"
    EXPLORING = "exploring"


class AgentMode(Enum):
    WORK = "work"      # Modo trabalho: segue usuário estritamente
    FREE = "free"      # Modo livre: exploração e auto-iniciativa


@dataclass
class Task:
    """Tarefa a ser executada pelo agente"""
    id: str
    description: str
    priority: int  # 1-10, sendo 10 mais prioritário
    source: str    # 'user', 'internal', 'auto'
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "pending"  # pending, running, completed, failed
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "description": self.description,
            "priority": self.priority,
            "source": self.source,
            "created_at": self.created_at.isoformat(),
            "status": self.status,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Task':
        return cls(
            id=data["id"],
            description=data["description"],
            priority=data["priority"],
            source=data["source"],
            created_at=datetime.fromisoformat(data["created_at"]),
            status=data["status"],
            metadata=data.get("metadata", {})
        )


@dataclass
class AgentStatus:
    """Status atual do agente"""
    state: AgentState = AgentState.IDLE
    mode: AgentMode = AgentMode.WORK
    current_task: Optional[Task] = None
    last_action_time: Optional[datetime] = None
    idle_since: datetime = field(default_factory=datetime.now)
    cycle_count: int = 0
    errors_in_cycle: int = 0
    llm_calls_in_cycle: int = 0
    
    def to_dict(self) -> Dict:
        return {
            "state": self.state.value,
            "mode": self.mode.value,
            "current_task": self.current_task.to_dict() if self.current_task else None,
            "last_action_time": self.last_action_time.isoformat() if self.last_action_time else None,
            "idle_since": self.idle_since.isoformat(),
            "cycle_count": self.cycle_count,
            "errors_in_cycle": self.errors_in_cycle,
            "llm_calls_in_cycle": self.llm_calls_in_cycle
        }


class StateManager:
    """Gerencia o estado persistente do agente"""
    
    def __init__(self, base_dir: str = "~/.agent"):
        self.base_dir = os.path.expanduser(base_dir)
        self.state_file = os.path.join(self.base_dir, "state.json")
        self.tasks_file = os.path.join(self.base_dir, "tasks.json")
        self._ensure_dirs()
        self.status = AgentStatus()
        self.tasks: List[Task] = []
        self._load_state()
    
    def _ensure_dirs(self):
        """Garante que diretórios existem"""
        os.makedirs(self.base_dir, exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, "identity"), exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, "memory"), exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, "logs"), exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, "scratchpad"), exist_ok=True)
    
    def _load_state(self):
        """Carrega estado persistente"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    self.status = AgentStatus(
                        state=AgentState(data.get("state", "idle")),
                        mode=AgentMode(data.get("mode", "work")),
                        cycle_count=data.get("cycle_count", 0),
                        idle_since=datetime.fromisoformat(data.get("idle_since", datetime.now().isoformat()))
                    )
            except Exception as e:
                print(f"Warning: Could not load state: {e}")
        
        if os.path.exists(self.tasks_file):
            try:
                with open(self.tasks_file, 'r') as f:
                    data = json.load(f)
                    self.tasks = [Task.from_dict(t) for t in data.get("tasks", [])]
            except Exception as e:
                print(f"Warning: Could not load tasks: {e}")
    
    def _save_state(self):
        """Salva estado persistente"""
        with open(self.state_file, 'w') as f:
            json.dump(self.status.to_dict(), f, indent=2)
        
        with open(self.tasks_file, 'w') as f:
            json.dump({"tasks": [t.to_dict() for t in self.tasks]}, f, indent=2)
    
    def set_state(self, state: AgentState):
        """Muda o estado do agente"""
        old_state = self.status.state
        self.status.state = state
        
        if state == AgentState.IDLE:
            self.status.idle_since = datetime.now()
        elif old_state == AgentState.IDLE:
            self.status.idle_since = datetime.now()
        
        self._save_state()
    
    def set_mode(self, mode: AgentMode):
        """Muda o modo do agente"""
        self.status.mode = mode
        self._save_state()
    
    def add_task(self, task: Task):
        """Adiciona uma tarefa à fila"""
        self.tasks.append(task)
        self._save_state()
    
    def get_next_task(self) -> Optional[Task]:
        """Retorna a próxima tarefa por prioridade"""
        pending = [t for t in self.tasks if t.status == "pending"]
        if not pending:
            return None
        
        # Ordena por prioridade (maior primeiro) e depois por tempo de criação
        pending.sort(key=lambda t: (-t.priority, t.created_at))
        return pending[0]
    
    def get_user_tasks(self) -> List[Task]:
        """Retorna tarefas do usuário pendentes"""
        return [t for t in self.tasks if t.source == "user" and t.status == "pending"]
    
    def mark_task_status(self, task_id: str, status: str):
        """Marca o status de uma tarefa"""
        for task in self.tasks:
            if task.id == task_id:
                task.status = status
                break
        self._save_state()
    
    def increment_cycle(self):
        """Incrementa contador de ciclos"""
        self.status.cycle_count += 1
        self.status.errors_in_cycle = 0
        self.status.llm_calls_in_cycle = 0
        self._save_state()
    
    def increment_error(self):
        """Registra erro no ciclo atual"""
        self.status.errors_in_cycle += 1
        self._save_state()
    
    def increment_llm_call(self):
        """Registra chamada LLM no ciclo atual"""
        self.status.llm_calls_in_cycle += 1
        self._save_state()
    
    def update_last_action(self):
        """Atualiza timestamp da última ação"""
        self.status.last_action_time = datetime.now()
        self._save_state()
    
    def get_idle_time(self) -> float:
        """Retorna tempo em segundos desde que está ocioso"""
        if self.status.state != AgentState.IDLE:
            return 0.0
        return (datetime.now() - self.status.idle_since).total_seconds()
    
    def get_status(self) -> AgentStatus:
        """Retorna status atual"""
        return self.status
