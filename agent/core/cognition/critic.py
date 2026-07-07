"""
Módulo Crítico Interno (Self-Correction Loop)
Valida planos antes da execução, identifica falhas lógicas e sugere correções.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
import time


class CriticSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Critique:
    issue: str
    severity: CriticSeverity
    suggestion: str
    confidence: float  # 0.0 a 1.0
    timestamp: float = field(default_factory=time.time)


@dataclass
class CritiqueReport:
    plan_id: str
    is_approved: bool
    critiques: List[Critique] = field(default_factory=list)
    overall_confidence: float = 0.0
    summary: str = ""
    
    def add_critique(self, issue: str, severity: CriticSeverity, 
                     suggestion: str, confidence: float):
        critique = Critique(issue, severity, suggestion, confidence)
        self.critiques.append(critique)
        
        # Se houver crítica crítica ou de alta severidade, reprova o plano
        if severity in [CriticSeverity.CRITICAL, CriticSeverity.HIGH]:
            self.is_approved = False
            self.overall_confidence = min(self.overall_confidence, 1.0 - confidence)
        else:
            self.overall_confidence = max(0.0, self.overall_confidence - (confidence * 0.1))
    
    def get_critical_issues(self) -> List[Critique]:
        return [c for c in self.critiques if c.severity in [CriticSeverity.CRITICAL, CriticSeverity.HIGH]]


class InternalCritic:
    """
    Crítico interno que valida planos antes da execução.
    Atua como um "advogado do diabo" para identificar falhas.
    """
    
    def __init__(self):
        self.critique_count = 0
        self.approval_count = 0
        self.rejection_count = 0
    
    def evaluate_plan(self, plan: Dict[str, Any], context: Dict[str, Any]) -> CritiqueReport:
        """
        Avalia um plano em busca de falhas lógicas, riscos e inconsistências.
        """
        report = CritiqueReport(
            plan_id=plan.get("id", "unknown"),
            is_approved=True,
            overall_confidence=0.95  # Confiança inicial alta
        )
        
        # 1. Verificar se o plano tem ações válidas
        actions = plan.get("actions", [])
        if not actions:
            report.add_critique(
                issue="Plano não contém ações",
                severity=CriticSeverity.CRITICAL,
                suggestion="Adicione pelo menos uma ação ao plano",
                confidence=1.0
            )
            return report
        
        # 2. Verificar dependências circulares
        if self._has_circular_dependencies(actions):
            report.add_critique(
                issue="Dependências circulares detectadas nas ações",
                severity=CriticSeverity.HIGH,
                suggestion="Reorganize as ações para evitar loops",
                confidence=0.9
            )
        
        # 3. Verificar recursos necessários
        required_resources = plan.get("required_resources", [])
        available_resources = context.get("available_resources", [])
        missing_resources = set(required_resources) - set(available_resources)
        
        if missing_resources:
            report.add_critique(
                issue=f"Recursos faltando: {', '.join(missing_resources)}",
                severity=CriticSeverity.HIGH,
                suggestion=f"Obtenha os recursos: {', '.join(missing_resources)} antes de executar",
                confidence=0.95
            )
        
        # 4. Verificar segurança das ações
        for action in actions:
            risk_level = action.get("risk_level", "unknown")
            if risk_level == "critical":
                report.add_critique(
                    issue=f"Ação crítica sem confirmação: {action.get('name', 'unknown')}",
                    severity=CriticSeverity.CRITICAL,
                    suggestion="Solicite confirmação do usuário antes de executar ações críticas",
                    confidence=1.0
                )
        
        # 5. Verificar timeout estimado vs limite
        estimated_time = plan.get("estimated_time_seconds", 0)
        max_time = context.get("max_execution_time_seconds", 300)
        
        if estimated_time > max_time:
            report.add_critique(
                issue=f"Tempo estimado ({estimated_time}s) excede o limite ({max_time}s)",
                severity=CriticSeverity.MEDIUM,
                suggestion="Divida o plano em sub-planos menores",
                confidence=0.85
            )
        
        # 6. Verificar se há plano B (fallback)
        if not plan.get("fallback_plan") and len(actions) > 3:
            report.add_critique(
                issue="Plano complexo sem fallback definido",
                severity=CriticSeverity.MEDIUM,
                suggestion="Defina um plano alternativo caso as ações falhem",
                confidence=0.7
            )
        
        # 7. Análise de consistência de objetivo
        goal = plan.get("goal", "")
        if goal and not self._actions_align_with_goal(actions, goal):
            report.add_critique(
                issue="Ações não parecem alinhadas com o objetivo declarado",
                severity=CriticSeverity.HIGH,
                suggestion="Revise as ações para garantir que contribuam para o objetivo",
                confidence=0.8
            )
        
        # Atualizar estatísticas
        self.critique_count += 1
        if report.is_approved:
            self.approval_count += 1
        else:
            self.rejection_count += 1
        
        # Gerar resumo
        if report.is_approved:
            report.summary = f"Plano aprovado com {len(report.critiques)} observações menores"
        else:
            critical_count = len(report.get_critical_issues())
            report.summary = f"Plano reprovado: {critical_count} issues críticos/altos encontrados"
        
        return report
    
    def _has_circular_dependencies(self, actions: List[Dict]) -> bool:
        """Verifica se há dependências circulares entre ações."""
        # Implementação simplificada - em produção usaria graph traversal
        action_ids = {a.get("id") for a in actions}
        for action in actions:
            depends_on = action.get("depends_on", [])
            for dep in depends_on:
                if dep not in action_ids:
                    continue
                # Verificação básica de auto-dependência
                if dep == action.get("id"):
                    return True
        return False
    
    def _actions_align_with_goal(self, actions: List[Dict], goal: str) -> bool:
        """Verifica se as ações parecem alinhadas com o objetivo."""
        # Heurística simples: verificar se há pelo menos uma ação
        # Em produção, usaria LLM para análise semântica
        if not actions:
            return False
        
        goal_keywords = goal.lower().split()
        alignment_score = 0
        
        for action in actions:
            action_desc = action.get("description", "").lower()
            for keyword in goal_keywords:
                if len(keyword) > 3 and keyword in action_desc:
                    alignment_score += 1
        
        # Se nenhuma palavra-chave foi encontrada, pode haver desalinhamento
        return alignment_score > 0 or len(goal_keywords) == 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de avaliações do crítico."""
        total = max(1, self.critique_count)
        return {
            "total_evaluations": self.critique_count,
            "approvals": self.approval_count,
            "rejections": self.rejection_count,
            "approval_rate": self.approval_count / total,
            "rejection_rate": self.rejection_count / total
        }
