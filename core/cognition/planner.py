"""
Planner - Sistema de planejamento em etapas do agente

Quebra intenções em planos executáveis
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
import uuid


@dataclass
class PlanStep:
    """Etapa individual de um plano"""
    id: str
    description: str
    action_type: str  # 'llm', 'shell', 'file', 'web', 'memory'
    status: str = "pending"  # pending, running, completed, failed, skipped
    result: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "description": self.description,
            "action_type": self.action_type,
            "status": self.status,
            "result": self.result,
            "error": self.error,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PlanStep':
        return cls(
            id=data["id"],
            description=data["description"],
            action_type=data["action_type"],
            status=data.get("status", "pending"),
            result=data.get("result"),
            error=data.get("error"),
            metadata=data.get("metadata", {})
        )


@dataclass
class Plan:
    """Plano completo com múltiplas etapas"""
    id: str
    intention: str
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    steps: List[PlanStep] = field(default_factory=list)
    current_step_index: int = 0
    status: str = "active"  # active, completed, failed, aborted
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "intention": self.intention,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "steps": [s.to_dict() for s in self.steps],
            "current_step_index": self.current_step_index,
            "status": self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Plan':
        plan = cls(
            id=data["id"],
            intention=data["intention"],
            created_at=datetime.fromisoformat(data["created_at"]),
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            current_step_index=data.get("current_step_index", 0),
            status=data.get("status", "active")
        )
        plan.steps = [PlanStep.from_dict(s) for s in data.get("steps", [])]
        return plan
    
    def get_next_step(self) -> Optional[PlanStep]:
        """Retorna próxima etapa pendente"""
        if self.current_step_index >= len(self.steps):
            return None
        
        for i in range(self.current_step_index, len(self.steps)):
            if self.steps[i].status == "pending":
                self.current_step_index = i
                return self.steps[i]
        
        return None
    
    def mark_step_completed(self, step_id: str, result: str = None):
        """Marca etapa como completada"""
        for step in self.steps:
            if step.id == step_id:
                step.status = "completed"
                step.result = result
                break
    
    def mark_step_failed(self, step_id: str, error: str):
        """Marca etapa como falhada"""
        for step in self.steps:
            if step.id == step_id:
                step.status = "failed"
                step.error = error
                break
    
    def is_complete(self) -> bool:
        """Verifica se todas as etapas estão completas"""
        return all(s.status in ["completed", "skipped"] for s in self.steps)
    
    def has_failed(self) -> bool:
        """Verifica se alguma etapa falhou"""
        return any(s.status == "failed" for s in self.steps)


class Planner:
    """
    Sistema de planejamento
    
    - Cria planos a partir de intenções
    - Quebra tarefas complexas em etapas
    - Acompanha execução do plano
    """
    
    def __init__(self):
        self.current_plan: Optional[Plan] = None
        self.plan_history: List[Plan] = []
    
    def create_plan(
        self, 
        intention: str, 
        steps: List[Dict] = None
    ) -> Plan:
        """
        Cria novo plano
        
        Args:
            intention: Descrição da intenção
            steps: Lista de etapas (opcional, pode ser gerado automaticamente)
        """
        plan_id = f"plan_{uuid.uuid4().hex[:8]}"
        
        plan = Plan(id=plan_id, intention=intention)
        
        # Se etapas não fornecidas, cria plano básico
        if not steps:
            steps = self._generate_default_steps(intention)
        
        for i, step_data in enumerate(steps):
            step = PlanStep(
                id=f"{plan_id}_step_{i}",
                description=step_data.get("description", f"Etapa {i}"),
                action_type=step_data.get("action_type", "llm"),
                metadata=step_data.get("metadata", {})
            )
            plan.steps.append(step)
        
        self.current_plan = plan
        return plan
    
    def _generate_default_steps(self, intention: str) -> List[Dict]:
        """
        Gera etapas padrão para uma intenção
        
        Em produção, isso usaria LLM para gerar plano inteligente
        """
        return [
            {
                "description": f"Analisar: {intention}",
                "action_type": "llm",
                "metadata": {"purpose": "analysis"}
            },
            {
                "description": "Executar ação necessária",
                "action_type": "llm",
                "metadata": {"purpose": "execution"}
            },
            {
                "description": "Validar resultado",
                "action_type": "llm",
                "metadata": {"purpose": "validation"}
            }
        ]
    
    def get_current_plan(self) -> Optional[Plan]:
        """Retorna plano atual"""
        return self.current_plan
    
    def get_next_step(self) -> Optional[PlanStep]:
        """Retorna próxima etapa do plano atual"""
        if not self.current_plan:
            return None
        return self.current_plan.get_next_step()
    
    def complete_step(self, step_id: str, result: str = None):
        """Completa etapa atual"""
        if self.current_plan:
            self.current_plan.mark_step_completed(step_id, result)
            
            if self.current_plan.is_complete():
                self.current_plan.completed_at = datetime.now()
                self.current_plan.status = "completed"
                self.plan_history.append(self.current_plan)
                self.current_plan = None
    
    def fail_step(self, step_id: str, error: str):
        """Falha etapa atual"""
        if self.current_plan:
            self.current_plan.mark_step_failed(step_id, error)
            
            if self.current_plan.has_failed():
                self.current_plan.status = "failed"
                self.plan_history.append(self.current_plan)
                self.current_plan = None
    
    def abort_plan(self):
        """Aborta plano atual"""
        if self.current_plan:
            self.current_plan.status = "aborted"
            self.plan_history.append(self.current_plan)
            self.current_plan = None
    
    def get_recent_plans(self, n: int = 5) -> List[Plan]:
        """Retorna últimos n planos"""
        return self.plan_history[-n:]
    
    def export_plan(self, plan_id: str, filepath: str) -> bool:
        """Exporta plano para arquivo"""
        for plan in self.plan_history:
            if plan.id == plan_id:
                with open(filepath, 'w') as f:
                    json.dump(plan.to_dict(), f, indent=2)
                return True
        
        if self.current_plan and self.current_plan.id == plan_id:
            with open(filepath, 'w') as f:
                json.dump(self.current_plan.to_dict(), f, indent=2)
            return True
        
        return False
    
    def get_summary(self) -> Dict:
        """Retorna resumo de planejamento"""
        total_plans = len(self.plan_history) + (1 if self.current_plan else 0)
        completed = sum(1 for p in self.plan_history if p.status == "completed")
        failed = sum(1 for p in self.plan_history if p.status == "failed")
        
        return {
            "total_plans": total_plans,
            "active_plans": 1 if self.current_plan else 0,
            "completed_plans": completed,
            "failed_plans": failed,
            "success_rate": completed / len(self.plan_history) if self.plan_history else 0.0
        }
