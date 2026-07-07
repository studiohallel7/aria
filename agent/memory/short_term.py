"""
Memória de Curto Prazo (Short-Term Memory - STM)

Armazena informações temporárias durante a execução de tarefas.
Capacidade limitada (7 ± 2 itens) com decaimento temporal.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import uuid


@dataclass
class STMItem:
    """Item individual na memória de curto prazo."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: Any = None
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    importance: float = 0.5
    decay_time: int = 300  # segundos até decair
    tags: List[str] = field(default_factory=list)
    
    def is_expired(self) -> bool:
        """Verifica se o item expirou."""
        expiry_time = self.created_at + timedelta(seconds=self.decay_time)
        return datetime.now() > expiry_time
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "importance": self.importance,
            "tags": self.tags
        }


class ShortTermMemory:
    """
    Memória de curto prazo com capacidade limitada e decaimento temporal.
    Implementa o conceito psicológico de STM com capacidade de 7±2 itens.
    """
    
    def __init__(self, capacity: int = 7, decay_time: int = 300):
        self.capacity = capacity
        self.default_decay_time = decay_time
        self.items: Dict[str, STMItem] = {}
        self.order: List[str] = []  # Mantém ordem de inserção para FIFO
    
    def add(self, content: Any, importance: float = 0.5, 
            tags: List[str] = None, decay_time: int = None) -> str:
        """Adiciona um item à memória de curto prazo."""
        # Remove itens expirados primeiro
        self._cleanup_expired()
        
        # Se atingiu capacidade, remove o mais antigo
        if len(self.items) >= self.capacity:
            self._evict_oldest()
        
        item_id = str(uuid.uuid4())
        item = STMItem(
            id=item_id,
            content=content,
            importance=importance,
            decay_time=decay_time or self.default_decay_time,
            tags=tags or []
        )
        
        self.items[item_id] = item
        self.order.append(item_id)
        
        return item_id
    
    def get(self, item_id: str) -> Optional[Any]:
        """Recupera um item pelo ID."""
        if item_id not in self.items:
            return None
        
        item = self.items[item_id]
        if item.is_expired():
            self.forget(item_id)
            return None
        
        item.last_accessed = datetime.now()
        return item.content
    
    def get_all(self) -> List[STMItem]:
        """Retorna todos os itens não expirados."""
        self._cleanup_expired()
        return list(self.items.values())
    
    def forget(self, item_or_id) -> bool:
        """Remove um item da memória (esquecimento)."""
        item_id = item_or_id if isinstance(item_or_id, str) else item_or_id.id
        
        if item_id not in self.items:
            return False
        
        del self.items[item_id]
        if item_id in self.order:
            self.order.remove(item_id)
        
        return True
    
    def _cleanup_expired(self):
        """Remove itens expirados."""
        expired_ids = [
            item_id for item_id, item in self.items.items()
            if item.is_expired()
        ]
        
        for item_id in expired_ids:
            self.forget(item_id)
    
    def _evict_oldest(self):
        """Remove o item mais antigo (FIFO)."""
        if self.order:
            oldest_id = self.order[0]
            self.forget(oldest_id)
    
    def clear(self):
        """Limpa toda a memória de curto prazo."""
        self.items.clear()
        self.order.clear()
    
    def __len__(self) -> int:
        return len(self.items)