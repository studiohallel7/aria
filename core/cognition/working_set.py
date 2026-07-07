"""
Working Set - Memória de Trabalho Ativa
Espaço temporário para rascunho mental, permitindo ao agente 
testar ideias, descartá-las e refiná-las antes do planejamento final.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib


@dataclass
class WorkingItem:
    """Item individual na memória de trabalho."""
    id: str
    content: str
    item_type: str  # 'idea', 'hypothesis', 'draft', 'constraint'
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    confidence: float = 0.5
    status: str = 'active'  # 'active', 'discarded', 'promoted'
    tags: List[str] = field(default_factory=list)
    related_items: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "item_type": self.item_type,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "confidence": self.confidence,
            "status": self.status,
            "tags": self.tags,
            "related_items": self.related_items
        }


class WorkingMemorySet:
    """
    Quadro negro mental (Working Set) para problemas complexos.
    
    Diferente da memória de curto prazo (que armazena contexto recente),
    o Working Set é um espaço ativo de manipulação cognitiva onde:
    - Ideias são testadas e descartadas
    - Hipóteses são formuladas e validadas
    - Rascunhos de planos são iterados
    - Restrições são mapeadas
    
    Este espaço é volátil e limpo após cada ciclo de pensamento completo.
    """
    
    def __init__(self, max_items: int = 20, ttl_seconds: int = 600):
        self.max_items = max_items
        self.ttl_seconds = ttl_seconds  # Tempo de vida máximo dos itens
        self.items: Dict[str, WorkingItem] = {}
        self.session_id = f"ws_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.iteration_count = 0
    
    def add_idea(self, content: str, tags: List[str] = None, 
                 confidence: float = 0.5) -> WorkingItem:
        """Adiciona uma ideia ao working set."""
        item_id = self._generate_id(content)
        
        if item_id in self.items:
            # Atualiza ideia existente
            item = self.items[item_id]
            item.content = content
            item.updated_at = datetime.now()
            item.confidence = confidence
            if tags:
                item.tags = list(set(item.tags + tags))
        else:
            # Nova ideia
            if len(self.items) >= self.max_items:
                self._evict_oldest()
            
            item = WorkingItem(
                id=item_id,
                content=content,
                item_type='idea',
                confidence=confidence,
                tags=tags or []
            )
            self.items[item_id] = item
        
        self.iteration_count += 1
        return item
    
    def add_hypothesis(self, hypothesis: str, 
                      related_to: List[str] = None) -> WorkingItem:
        """Adiciona uma hipótese para teste."""
        item = self.add_idea(
            content=hypothesis,
            tags=['hypothesis'] + (related_to or []),
            confidence=0.3  # Hipóteses começam com baixa confiança
        )
        item.item_type = 'hypothesis'
        if related_to:
            item.related_items = related_to
        return item
    
    def add_constraint(self, constraint: str, 
                      severity: str = 'medium') -> WorkingItem:
        """Adiciona uma restrição ou limitação ao problema."""
        item = self.add_idea(
            content=constraint,
            tags=['constraint', severity],
            confidence=1.0  # Restrições são fatos
        )
        item.item_type = 'constraint'
        return item
    
    def refine_item(self, item_id: str, new_content: str, 
                   confidence_delta: float = 0.1) -> Optional[WorkingItem]:
        """Refina um item existente (itera sobre a ideia)."""
        if item_id not in self.items:
            return None
        
        item = self.items[item_id]
        item.content = new_content
        item.updated_at = datetime.now()
        item.confidence = min(1.0, max(0.0, item.confidence + confidence_delta))
        self.iteration_count += 1
        
        return item
    
    def discard_item(self, item_id: str, reason: str = None) -> bool:
        """Descarta um item do working set (não promove para memória)."""
        if item_id not in self.items:
            return False
        
        item = self.items[item_id]
        item.status = 'discarded'
        item.updated_at = datetime.now()
        
        # Adiciona razão do descarte como tag
        if reason:
            item.tags.append(f'discarded:{reason}')
        
        return True
    
    def promote_item(self, item_id: str) -> Optional[WorkingItem]:
        """Promove um item para ser movido à memória permanente."""
        if item_id not in self.items:
            return None
        
        item = self.items[item_id]
        item.status = 'promoted'
        item.updated_at = datetime.now()
        
        return item
    
    def get_active_items(self, item_type: str = None) -> List[WorkingItem]:
        """Retorna itens ativos, opcionalmente filtrados por tipo."""
        items = [
            item for item in self.items.values() 
            if item.status == 'active'
        ]
        
        if item_type:
            items = [item for item in items if item.item_type == item_type]
        
        # Ordenar por confiança (mais confiantes primeiro)
        items.sort(key=lambda x: x.confidence, reverse=True)
        
        return items
    
    def get_related_items(self, item_id: str) -> List[WorkingItem]:
        """Retorna itens relacionados a um item específico."""
        if item_id not in self.items:
            return []
        
        item = self.items[item_id]
        related = []
        
        for rid in item.related_items:
            if rid in self.items:
                related.append(self.items[rid])
        
        return related
    
    def find_by_tag(self, tag: str) -> List[WorkingItem]:
        """Encontra todos os itens com uma tag específica."""
        return [
            item for item in self.items.values()
            if tag in item.tags and item.status == 'active'
        ]
    
    def get_summary(self) -> Dict[str, Any]:
        """Retorna resumo do estado atual do working set."""
        active = self.get_active_items()
        by_type = {}
        by_status = {}
        
        for item in self.items.values():
            # Por tipo
            t = item.item_type
            by_type[t] = by_type.get(t, 0) + 1
            
            # Por status
            s = item.status
            by_status[s] = by_status.get(s, 0) + 1
        
        avg_confidence = (
            sum(i.confidence for i in active) / len(active) 
            if active else 0.0
        )
        
        return {
            "session_id": self.session_id,
            "total_items": len(self.items),
            "active_items": len(active),
            "by_type": by_type,
            "by_status": by_status,
            "average_confidence": avg_confidence,
            "iterations": self.iteration_count,
            "oldest_item_age": self._get_oldest_item_age()
        }
    
    def export_for_planning(self) -> Dict[str, Any]:
        """
        Exporta apenas itens promovidos e ativos de alta confiança
        para uso no módulo de planejamento.
        """
        promoted = [i for i in self.items.values() if i.status == 'promoted']
        high_confidence_active = [
            i for i in self.get_active_items() 
            if i.confidence >= 0.7
        ]
        
        return {
            "session_id": self.session_id,
            "promoted_items": [i.to_dict() for i in promoted],
            "high_confidence_ideas": [i.to_dict() for i in high_confidence_active],
            "constraints": [i.to_dict() for i in self.find_by_tag('constraint')]
        }
    
    def clear_discarded(self):
        """Remove permanentemente itens descartados."""
        discarded_ids = [
            item_id for item_id, item in self.items.items()
            if item.status == 'discarded'
        ]
        
        for item_id in discarded_ids:
            del self.items[item_id]
    
    def reset(self):
        """Reseta completamente o working set (fim do ciclo cognitivo)."""
        self.items.clear()
        self.iteration_count = 0
        self.session_id = f"ws_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def _generate_id(self, content: str) -> str:
        """Gera ID único baseado no conteúdo."""
        timestamp = datetime.now().isoformat()
        raw = f"{timestamp}:{content}"
        return hashlib.md5(raw.encode()).hexdigest()[:12]
    
    def _evict_oldest(self):
        """Remove o item mais antigo (menor confiança prioritária)."""
        if not self.items:
            return
        
        # Prioriza remover itens de baixa confiança
        active_items = [
            (item_id, item) for item_id, item in self.items.items()
            if item.status == 'active'
        ]
        
        if not active_items:
            return
        
        # Ordenar por confiança (menor primeiro) e depois por idade
        active_items.sort(
            key=lambda x: (x[1].confidence, x[1].created_at)
        )
        
        oldest_id = active_items[0][0]
        del self.items[oldest_id]
    
    def _get_oldest_item_age(self) -> float:
        """Retorna idade do item mais antigo em segundos."""
        if not self.items:
            return 0.0
        
        oldest = min(
            (item.created_at for item in self.items.values()),
            default=datetime.now()
        )
        
        return (datetime.now() - oldest).total_seconds()
