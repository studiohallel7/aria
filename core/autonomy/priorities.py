"""
Priority System - Sistema de prioridades do agente

Prioridades:
- usuário > interno > auto
- crítico > alto > normal > baixo
"""

from enum import Enum
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import heapq


class PriorityLevel(Enum):
    CRITICAL = 10
    HIGH = 7
    NORMAL = 5
    LOW = 2


class SourcePriority(Enum):
    USER = 100      # Tarefas do usuário têm prioridade máxima
    INTERNAL = 50   # Tarefas internas
    AUTO = 25       # Auto-iniciativa
    SYSTEM = 75     # Sistema (fallback, segurança)


@dataclass
class PrioritizedItem:
    """Item com prioridade composta"""
    id: str
    description: str
    source: SourcePriority
    level: PriorityLevel
    created_at: datetime = field(default_factory=datetime.now)
    deadline: Optional[datetime] = None
    metadata: Dict = field(default_factory=dict)
    
    @property
    def composite_priority(self) -> float:
        """
        Calcula prioridade composta
        
        Quanto maior, mais prioritário
        """
        base = self.source.value + self.level.value
        
        # Bônus por deadline próxima
        if self.deadline:
            time_left = (self.deadline - datetime.now()).total_seconds()
            if time_left < 0:
                base += 50  # Atrasado
            elif time_left < 60:
                base += 30  # Menos de 1 minuto
            elif time_left < 300:
                base += 15  # Menos de 5 minutos
        
        return base
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "description": self.description,
            "source": self.source.name,
            "level": self.level.name,
            "created_at": self.created_at.isoformat(),
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "composite_priority": self.composite_priority,
            "metadata": self.metadata
        }


class PriorityQueue:
    """Fila de prioridades para tarefas"""
    
    def __init__(self):
        self._queue = []
        self._counter = 0
    
    def push(self, item: PrioritizedItem):
        """Adiciona item à fila"""
        # Usa prioridade negativa para max-heap
        priority = -item.composite_priority
        heapq.heappush(self._queue, (priority, self._counter, item))
        self._counter += 1
    
    def pop(self) -> Optional[PrioritizedItem]:
        """Remove e retorna item mais prioritário"""
        if not self._queue:
            return None
        
        _, _, item = heapq.heappop(self._queue)
        return item
    
    def peek(self) -> Optional[PrioritizedItem]:
        """Retorna item mais prioritário sem remover"""
        if not self._queue:
            return None
        
        return self._queue[0][2]
    
    def is_empty(self) -> bool:
        return len(self._queue) == 0
    
    def size(self) -> int:
        return len(self._queue)
    
    def get_all(self) -> List[PrioritizedItem]:
        """Retorna todos os itens ordenados por prioridade"""
        sorted_items = sorted(self._queue, key=lambda x: x[0])
        return [item for _, _, item in sorted_items]


class PriorityManager:
    """
    Gerenciador de prioridades
    
    - Classifica tarefas por prioridade
    - Decide ordem de execução
    - Balanceia fontes diferentes
    """
    
    def __init__(self):
        self.queue = PriorityQueue()
        self.completed: List[PrioritizedItem] = []
        self.cancelled: List[PrioritizedItem] = []
    
    def add_task(
        self,
        task_id: str,
        description: str,
        source: str,
        level: str = "NORMAL",
        deadline: Optional[datetime] = None,
        metadata: Dict = None
    ) -> PrioritizedItem:
        """Adiciona tarefa ao sistema de prioridades"""
        
        # Mapeia strings para enums
        source_enum = SourcePriority[source.upper()]
        level_enum = PriorityLevel[level.upper()]
        
        item = PrioritizedItem(
            id=task_id,
            description=description,
            source=source_enum,
            level=level_enum,
            deadline=deadline,
            metadata=metadata or {}
        )
        
        self.queue.push(item)
        return item
    
    def get_next_task(self) -> Optional[PrioritizedItem]:
        """Retorna próxima tarefa a executar"""
        return self.queue.pop()
    
    def peek_next_task(self) -> Optional[PrioritizedItem]:
        """Espia próxima tarefa sem remover"""
        return self.queue.peek()
    
    def complete_task(self, task_id: str) -> bool:
        """Marca tarefa como completada"""
        # Busca na fila
        for i, (_, _, item) in enumerate(self.queue._queue):
            if item.id == task_id:
                # Remove da fila
                self.queue._queue.pop(i)
                heapq.heapify(self.queue._queue)
                self.completed.append(item)
                return True
        
        return False
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancela tarefa"""
        for i, (_, _, item) in enumerate(self.queue._queue):
            if item.id == task_id:
                self.queue._queue.pop(i)
                heapq.heapify(self.queue._queue)
                self.cancelled.append(item)
                return True
        
        return False
    
    def get_user_tasks(self) -> List[PrioritizedItem]:
        """Retorna apenas tarefas do usuário"""
        return [
            item for item in self.queue.get_all()
            if item.source == SourcePriority.USER
        ]
    
    def has_user_tasks(self) -> bool:
        """Verifica se há tarefas do usuário pendentes"""
        return any(
            item.source == SourcePriority.USER
            for item in self.queue.get_all()
        )
    
    def get_statistics(self) -> Dict:
        """Estatísticas do sistema de prioridades"""
        all_items = self.queue.get_all()
        
        by_source = {}
        for item in all_items:
            src = item.source.name
            by_source[src] = by_source.get(src, 0) + 1
        
        by_level = {}
        for item in all_items:
            lvl = item.level.name
            by_level[lvl] = by_level.get(lvl, 0) + 1
        
        return {
            "pending": len(all_items),
            "completed": len(self.completed),
            "cancelled": len(self.cancelled),
            "by_source": by_source,
            "by_level": by_level,
            "has_user_tasks": self.has_user_tasks()
        }
    
    def clear_completed(self, older_than_days: int = 7):
        """Limpa tarefas completadas antigas"""
        cutoff = datetime.now()
        from datetime import timedelta
        cutoff = cutoff - timedelta(days=older_than_days)
        
        self.completed = [
            item for item in self.completed
            if item.created_at > cutoff
        ]
        self.cancelled = [
            item for item in self.cancelled
            if item.created_at > cutoff
        ]
