"""
Context Manager - Gerencia contexto ativo e memória de curto prazo
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class ContextItem:
    """Item individual no contexto"""
    content: str
    role: str  # 'system', 'user', 'assistant', 'tool', 'thought'
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "content": self.content,
            "role": self.role,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ContextItem':
        return cls(
            content=data["content"],
            role=data["role"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {})
        )


class ContextManager:
    """
    Gerencia o contexto ativo (memória de curto prazo)
    
    - Mantém histórico de interações recentes
    - Controla tamanho do contexto para não exceder limites
    - Separa pensamento interno de comunicação externa
    """
    
    def __init__(self, max_size: int = 50):
        self.max_size = max_size
        self.items: List[ContextItem] = []
        self.thoughts: List[str] = []  # Pensamentos internos (não expostos)
        self.current_intention: Optional[str] = None
        self.current_plan: List[str] = []
    
    def add_item(self, content: str, role: str, metadata: Dict = None):
        """Adiciona item ao contexto"""
        item = ContextItem(
            content=content,
            role=role,
            metadata=metadata or {}
        )
        self.items.append(item)
        
        # Limita tamanho do contexto
        if len(self.items) > self.max_size:
            self.items = self.items[-self.max_size:]
    
    def add_thought(self, thought: str):
        """Adiciona pensamento interno (não exposto ao usuário)"""
        self.thoughts.append(thought)
        
        # Limita pensamentos recentes
        if len(self.thoughts) > 20:
            self.thoughts = self.thoughts[-20:]
    
    def add_system_message(self, content: str, metadata: Dict = None):
        """Adiciona mensagem do sistema"""
        self.add_item(content, "system", metadata)
    
    def add_user_message(self, content: str, metadata: Dict = None):
        """Adiciona mensagem do usuário"""
        self.add_item(content, "user", metadata)
    
    def add_assistant_message(self, content: str, metadata: Dict = None):
        """Adiciona resposta do assistente"""
        self.add_item(content, "assistant", metadata)
    
    def add_tool_result(self, content: str, tool_name: str, metadata: Dict = None):
        """Adiciona resultado de ferramenta"""
        meta = metadata or {}
        meta["tool_name"] = tool_name
        self.add_item(content, "tool", meta)
    
    def get_context_for_llm(self, include_thoughts: bool = False) -> List[Dict]:
        """
        Retorna contexto formatado para LLM
        
        Por padrão, NÃO inclui pensamentos internos
        """
        context = []
        
        for item in self.items:
            # Filtra pensamentos se não forem explicitamente solicitados
            if item.role == "thought" and not include_thoughts:
                continue
            
            context.append({
                "role": item.role,
                "content": item.content,
                **item.metadata
            })
        
        return context
    
    def get_recent_messages(self, n: int = 10) -> List[ContextItem]:
        """Retorna últimas n mensagens"""
        return self.items[-n:]
    
    def clear_context(self):
        """Limpa o contexto"""
        self.items = []
        self.thoughts = []
        self.current_intention = None
        self.current_plan = []
    
    def set_intention(self, intention: str):
        """Define intenção atual"""
        self.current_intention = intention
    
    def get_intention(self) -> Optional[str]:
        """Retorna intenção atual"""
        return self.current_intention
    
    def set_plan(self, plan: List[str]):
        """Define plano atual"""
        self.current_plan = plan
    
    def get_plan(self) -> List[str]:
        """Retorna plano atual"""
        return self.current_plan
    
    def get_summary(self) -> Dict:
        """Retorna resumo do contexto"""
        return {
            "total_items": len(self.items),
            "total_thoughts": len(self.thoughts),
            "current_intention": self.current_intention,
            "plan_steps": len(self.current_plan),
            "last_update": self.items[-1].timestamp.isoformat() if self.items else None
        }
    
    def export_to_file(self, filepath: str):
        """Exporta contexto para arquivo JSON"""
        data = {
            "items": [item.to_dict() for item in self.items],
            "thoughts": self.thoughts,
            "intention": self.current_intention,
            "plan": self.current_plan
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def import_from_file(self, filepath: str):
        """Importa contexto de arquivo JSON"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.items = [ContextItem.from_dict(item) for item in data.get("items", [])]
        self.thoughts = data.get("thoughts", [])
        self.current_intention = data.get("intention")
        self.current_plan = data.get("plan", [])
