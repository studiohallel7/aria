"""
Constitution Evolver - Evolução da ética do agente

Permite que a constituição moral do agente evolua baseada em:
- Novas situações éticas encontradas
- Feedback sobre decisões passadas
- Conflitos entre princípios
- Mudanças contextuais aceitáveis
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import random


class EthicalMutationType(Enum):
    """Tipos de mutação ética"""
    PRINCIPLE_WEIGHT_ADJUST = "principle_weight_adjust"
    BELIEF_CONFIDENCE_UPDATE = "belief_confidence_update"
    BOUNDARY_REFINE = "boundary_refine"
    NEW_PRINCIPLE_ADD = "new_principle_add"
    PRINCIPLE_MERGE = "principle_merge"
    CONTEXT_EXPAND = "context_expand"


@dataclass
class EthicalMutation:
    """Representa uma mudança na constituição"""
    mutation_type: EthicalMutationType
    target_id: str  # ID do princípio/crença afetado
    old_value: Any
    new_value: Any
    justification: str
    timestamp: datetime = field(default_factory=datetime.now)
    accepted: bool = False
    
    def to_dict(self) -> Dict:
        return {
            'type': self.mutation_type.value,
            'target_id': self.target_id,
            'old_value': str(self.old_value),
            'new_value': str(self.new_value),
            'justification': self.justification,
            'timestamp': self.timestamp.isoformat(),
            'accepted': self.accepted
        }


class ConstitutionEvolver:
    """
    Sistema de evolução da constituição ética
    
    Mecanismos:
    - Propõe mudanças baseadas em experiências
    - Avalia impacto de mudanças
    - Requer validação para mudanças críticas
    - Mantém histórico de evolução ética
    """
    
    def __init__(
        self,
        constitution: Any,  # Constituição atual
        min_confidence_threshold: float = 0.7,
        critical_change_requires_approval: bool = True
    ):
        self.constitution = constitution
        self.min_confidence_threshold = min_confidence_threshold
        self.critical_change_requires_approval = critical_change_requires_approval
        
        self.mutation_history: List[EthicalMutation] = []
        self.pending_mutations: List[EthicalMutation] = []
        self.evolution_log: List[Dict] = []
    
    def propose_mutation(
        self,
        mutation_type: EthicalMutationType,
        target_id: str,
        new_value: Any,
        justification: str,
        confidence: float
    ) -> Optional[EthicalMutation]:
        """Propõe mudança na constituição"""
        if confidence < self.min_confidence_threshold:
            return None
        
        # Obter valor atual
        old_value = self._get_current_value(target_id)
        
        mutation = EthicalMutation(
            mutation_type=mutation_type,
            target_id=target_id,
            old_value=old_value,
            new_value=new_value,
            justification=justification
        )
        
        # Se mudança crítica, requer aprovação
        if self._is_critical_change(mutation) and self.critical_change_requires_approval:
            self.pending_mutations.append(mutation)
            return mutation
        
        # Aplicar automaticamente se não crítica
        self._apply_mutation(mutation)
        return mutation
    
    def approve_mutation(self, mutation_id: int) -> bool:
        """Aprova mudança pendente"""
        if 0 <= mutation_id < len(self.pending_mutations):
            mutation = self.pending_mutations[mutation_id]
            mutation.accepted = True
            self._apply_mutation(mutation)
            self.pending_mutations.pop(mutation_id)
            return True
        return False
    
    def reject_mutation(self, mutation_id: int) -> bool:
        """Rejeita mudança pendente"""
        if 0 <= mutation_id < len(self.pending_mutations):
            self.pending_mutations.pop(mutation_id)
            return True
        return False
    
    def analyze_ethical_dilemma(
        self,
        situation: Dict,
        decision_made: str,
        outcome_satisfactory: bool
    ) -> List[EthicalMutation]:
        """Analisa dilema ético e propõe ajustes"""
        proposed = []
        
        if not outcome_satisfactory:
            # Identificar princípios conflitantes
            conflicts = self._identify_conflicts(situation)
            
            for conflict in conflicts:
                mutation = self.propose_mutation(
                    mutation_type=EthicalMutationType.PRINCIPLE_WEIGHT_ADJUST,
                    target_id=conflict['principle_id'],
                    new_value=conflict['suggested_weight'],
                    justification=f"Conflito em situação: {situation.get('description', 'N/A')}",
                    confidence=conflict['confidence']
                )
                if mutation:
                    proposed.append(mutation)
        
        return proposed
    
    def _get_current_value(self, target_id: str) -> Any:
        """Obtém valor atual de princípio/crença"""
        # Implementação depende da estrutura da constituição
        return None
    
    def _is_critical_change(self, mutation: EthicalMutation) -> bool:
        """Verifica se mudança é crítica"""
        critical_types = [
            EthicalMutationType.NEW_PRINCIPLE_ADD,
            EthicalMutationType.PRINCIPLE_MERGE
        ]
        
        if mutation.mutation_type in critical_types:
            return True
        
        # Verificar magnitude da mudança
        if isinstance(mutation.old_value, (int, float)) and isinstance(mutation.new_value, (int, float)):
            change_ratio = abs(mutation.new_value - mutation.old_value) / max(abs(mutation.old_value), 0.001)
            return change_ratio > 0.5  # Mudança > 50% é crítica
        
        return False
    
    def _apply_mutation(self, mutation: EthicalMutation):
        """Aplica mudança à constituição"""
        mutation.accepted = True
        self.mutation_history.append(mutation)
        
        # Atualizar constituição (implementação específica)
        # self.constitution.update(...)
        
        self.evolution_log.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'applied_mutation',
            'mutation': mutation.to_dict()
        })
    
    def _identify_conflicts(self, situation: Dict) -> List[Dict]:
        """Identifica conflitos entre princípios"""
        # Análise simplificada
        return []
    
    def get_evolution_summary(self) -> Dict:
        """Retorna resumo da evolução ética"""
        return {
            'total_mutations': len(self.mutation_history),
            'pending_mutations': len(self.pending_mutations),
            'accepted_count': sum(1 for m in self.mutation_history if m.accepted),
            'by_type': self._count_by_type(),
            'recent_changes': [m.to_dict() for m in self.mutation_history[-10:]]
        }
    
    def _count_by_type(self) -> Dict[str, int]:
        counts = {}
        for mutation in self.mutation_history:
            key = mutation.mutation_type.value
            counts[key] = counts.get(key, 0) + 1
        return counts
    
    def export_evolution(self, filepath: str):
        """Exporta histórico de evolução"""
        data = {
            'mutations': [m.to_dict() for m in self.mutation_history],
            'pending': [m.to_dict() for m in self.pending_mutations],
            'log': self.evolution_log
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
