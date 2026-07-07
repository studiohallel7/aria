"""
Alignment Engine - Fase 5: Ética Constitutiva

Este módulo integra constituição e consciência para garantir alinhamento moral
contínuo do agente. Ele atua como uma camada de mediação entre as intenções
do agente e suas ações, aplicando deliberação ética de forma transparente.

O alignment não é um filtro externo, mas um processo de reflexão interna
que faz parte da identidade do agente.
"""

from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
import time
import json

from .constitution import AgentIdentity, ConstitutionLoader, create_custom_constitution
from .conscience import (
    ConscienceEngine, 
    MoralSituation, 
    EthicalDeliberation,
    DecisionOutcome
)


@dataclass
class AlignmentConfig:
    """Configuração do sistema de alignment."""
    auto_reject_critical_violations: bool = True
    log_all_deliberations: bool = True
    require_high_confidence: bool = False
    minimum_confidence_threshold: float = 0.7
    enable_learning: bool = True
    max_history_size: int = 1000
    user_override_allowed: bool = False  # Usuário pode sobrescrever decisões?
    

@dataclass
class AlignmentResult:
    """Resultado de uma verificação de alignment."""
    approved: bool
    action: str
    modified_action: Optional[str]
    deliberation: EthicalDeliberation
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário serializável."""
        return {
            "approved": self.approved,
            "action": self.action,
            "modified_action": self.modified_action,
            "outcome": self.deliberation.outcome.value,
            "confidence": self.deliberation.confidence,
            "reasoning": self.deliberation.reasoning,
            "principles_invoked": self.deliberation.principles_invoked,
            "timestamp": self.timestamp
        }


class AlignmentEngine:
    """
    Motor de Alignment que garante coerência moral do agente.
    
    Este engine:
    1. Carrega a constituição moral do agente
    2. Inicializa o motor de consciência
    3. Intercepta ações propostas para deliberação ética
    4. Mantém histórico e aprende com deliberações passadas
    5. Fornece transparência sobre decisões morais
    """
    
    def __init__(
        self,
        constitution_path: Optional[str] = None,
        config: Optional[AlignmentConfig] = None
    ):
        self.config = config or AlignmentConfig()
        
        # Carregar constituição
        loader = ConstitutionLoader(constitution_path)
        self.constitution = loader.load()
        
        # Inicializar consciência
        self.conscience = ConscienceEngine(self.constitution)
        
        # Histórico de alignments
        self.alignment_history: List[AlignmentResult] = []
        
        # Callbacks opcionais para hooks externos
        self.on_rejection: Optional[Callable[[AlignmentResult], None]] = None
        self.on_approval: Optional[Callable[[AlignmentResult], None]] = None
        self.on_modification: Optional[Callable[[AlignmentResult], None]] = None
        
        # Estatísticas
        self.stats = {
            "total_checks": 0,
            "approvals": 0,
            "rejections": 0,
            "modifications": 0,
            "conflicts": 0
        }
    
    def check_action(
        self,
        action_description: str,
        context: Optional[Dict[str, Any]] = None,
        stakeholders: Optional[List[str]] = None,
        potential_harms: Optional[List[str]] = None,
        potential_benefits: Optional[List[str]] = None,
        urgency: float = 0.5,
        reversibility: float = 0.8
    ) -> AlignmentResult:
        """
        Verifica se uma ação está alinhada com a constituição moral.
        
        Args:
            action_description: Descrição da ação proposta
            context: Contexto adicional da situação
            stakeholders: Lista de partes afetadas
            potential_harms: Danos potenciais identificados
            potential_benefits: Benefícios potenciais identificados
            urgency: Nível de urgência (0.0-1.0)
            reversibilidade: Quão reversível é a ação (0.0-1.0)
            
        Returns:
            AlignmentResult com decisão e raciocínio
        """
        self.stats["total_checks"] += 1
        
        # Criar situação moral
        situation = MoralSituation(
            description=action_description,
            stakeholders=stakeholders or ["usuário"],
            potential_harms=potential_harms or [],
            potential_benefits=potential_benefits or [],
            urgency=urgency,
            reversibility=reversibility,
            context_metadata=context or {}
        )
        
        # Avaliar com a consciência
        deliberation = self.conscience.evaluate(situation, action_description)
        
        # Determinar resultado
        approved = deliberation.outcome in [
            DecisionOutcome.APPROVED,
            DecisionOutcome.MODIFIED
        ]
        
        modified_action = None
        if deliberation.outcome == DecisionOutcome.MODIFIED:
            # Extrair ação modificada do raciocínio (em implementação futura)
            modified_action = self._suggest_modification(action_description, deliberation)
        
        # Criar resultado
        result = AlignmentResult(
            approved=approved,
            action=action_description,
            modified_action=modified_action,
            deliberation=deliberation,
            timestamp=time.time(),
            metadata={
                "context": context,
                "stats_snapshot": self.stats.copy()
            }
        )
        
        # Atualizar estatísticas
        if deliberation.outcome == DecisionOutcome.APPROVED:
            self.stats["approvals"] += 1
            if self.on_approval:
                self.on_approval(result)
        elif deliberation.outcome == DecisionOutcome.REJECTED:
            self.stats["rejections"] += 1
            if self.on_rejection:
                self.on_rejection(result)
        elif deliberation.outcome == DecisionOutcome.MODIFIED:
            self.stats["modifications"] += 1
            if self.on_modification:
                self.on_modification(result)
        elif deliberation.outcome == DecisionOutcome.CONFLICTING:
            self.stats["conflicts"] += 1
        
        # Armazenar histórico
        if self.config.log_all_deliberations:
            self.alignment_history.append(result)
            
            # Limitar tamanho do histórico
            if len(self.alignment_history) > self.config.max_history_size:
                self.alignment_history = self.alignment_history[-self.config.max_history_size:]
        
        # Verificar rejeição crítica
        if (deliberation.outcome == DecisionOutcome.REJECTED and 
            self.config.auto_reject_critical_violations):
            return result
        
        # Verificar confiança mínima
        if (self.config.require_high_confidence and 
            deliberation.confidence < self.config.minimum_confidence_threshold):
            # Baixar confiança trata como não-aprovado
            result.approved = False
            result.metadata["low_confidence_flag"] = True
        
        return result
    
    def _suggest_modification(
        self,
        action: str,
        deliberation: EthicalDeliberation
    ) -> str:
        """Sugere modificação para ação baseada na deliberação."""
        # Usa LLM para gerar ação modificada quando há conflito ético
        from agent.infra.llm.client import LLMMessage
        from agent.infra.llm.router import LLMRouter
        
        system_prompt = """Você é um assistente de alinhamento ético.
Sua tarefa é modificar ações propostas para que estejam em conformidade com princípios éticos.
Retorne APENAS a ação modificada, sem explicações adicionais."""

        user_prompt = f"""Ação original: {action}
Princípios violados: {', '.join(deliberation.principles_invoked)}
Raciocínio: {deliberation.reasoning}

Modifique a ação para respeitar os princípios éticos mencionados."""
        
        try:
            router = LLMRouter()
            messages = [
                LLMMessage(role="system", content=system_prompt),
                LLMMessage(role="user", content=user_prompt)
            ]
            
            response = router.chat_completion(
                messages=messages,
                purpose="raciocinio_rapido"
            )
            
            if response and not response.error and response.content.strip():
                return response.content.strip()
        except Exception as e:
            print(f"[FALLBACK] Usando modificação básica: {e}")
        
        # Fallback mínimo: adiciona sufixo indicando necessidade de revisão
        return f"{action} [REVISAR PARA ALINHAMENTO ÉTICO]"
    
    def batch_check(
        self,
        actions: List[Dict[str, Any]]
    ) -> List[AlignmentResult]:
        """
        Verifica múltiplas ações em lote.
        
        Args:
            actions: Lista de dicionários com parâmetros para check_action
            
        Returns:
            Lista de AlignmentResults
        """
        results = []
        for action_params in actions:
            result = self.check_action(**action_params)
            results.append(result)
        return results
    
    def get_constitution_summary(self) -> Dict[str, Any]:
        """Retorna resumo da constituição atual."""
        return {
            "name": self.constitution.name,
            "version": self.constitution.version,
            "principle_count": len(self.constitution.principles),
            "belief_count": len(self.constitution.beliefs),
            "boundary_count": len(self.constitution.boundaries),
            "principles": [
                {"name": p.name, "weight": p.weight.name, "absolute": p.absolute}
                for p in self.constitution.principles
            ],
            "boundaries": [
                {"category": b.category, "strictness": b.strictness}
                for b in self.constitution.boundaries
            ]
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de usage do alignment."""
        total = self.stats["total_checks"]
        if total == 0:
            return self.stats
        
        return {
            **self.stats,
            "approval_rate": round(self.stats["approvals"] / total, 3),
            "rejection_rate": round(self.stats["rejections"] / total, 3),
            "modification_rate": round(self.stats["modifications"] / total, 3),
            "conflict_rate": round(self.stats["conflicts"] / total, 3),
            "average_confidence": round(
                sum(r.deliberation.confidence for r in self.alignment_history) / 
                max(len(self.alignment_history), 1),
                3
            )
        }
    
    def get_recent_deliberations(
        self,
        limit: int = 10,
        outcome_filter: Optional[DecisionOutcome] = None
    ) -> List[Dict[str, Any]]:
        """
        Retorna deliberações recentes.
        
        Args:
            limit: Número máximo de resultados
            outcome_filter: Filtrar por tipo de resultado
            
        Returns:
            Lista de deliberações serializadas
        """
        history = self.alignment_history
        
        if outcome_filter:
            history = [r for r in history if r.deliberation.outcome == outcome_filter]
        
        # Ordenar por timestamp (mais recente primeiro)
        history = sorted(history, key=lambda r: r.timestamp, reverse=True)
        
        return [r.to_dict() for r in history[:limit]]
    
    def export_alignment_log(self, filepath: str) -> None:
        """Exporta log completo de alignments para arquivo JSON."""
        log_data = {
            "export_timestamp": time.time(),
            "constitution": self.get_constitution_summary(),
            "stats": self.get_stats(),
            "deliberations": [r.to_dict() for r in self.alignment_history]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
    
    def update_constitution(
        self,
        new_principles: Optional[List] = None,
        new_boundaries: Optional[List] = None,
        updated_beliefs: Optional[List] = None
    ) -> None:
        """
        Atualiza a constituição com novos elementos.
        
        Nota: Em produção, isso requereria aprovação do usuário.
        """
        if new_principles:
            self.constitution.principles.extend(new_principles)
        
        if new_boundaries:
            self.constitution.boundaries.extend(new_boundaries)
        
        if updated_beliefs:
            # Substituir crenças existentes
            self.constitution.beliefs = updated_beliefs
        
        # Re-inicializar consciência com nova constituição
        self.conscience = ConscienceEngine(self.constitution)
    
    def analyze_moral_trends(self) -> Dict[str, Any]:
        """Analisa tendências nas deliberações morais."""
        if not self.alignment_history:
            return {"message": "Dados insuficientes para análise"}
        
        # Analisar por tipo de outcome ao longo do tempo
        outcomes_over_time = {}
        for result in self.alignment_history:
            hour_bucket = int(result.timestamp // 3600)
            if hour_bucket not in outcomes_over_time:
                outcomes_over_time[hour_bucket] = {
                    "approved": 0, "rejected": 0, "modified": 0, "conflicting": 0
                }
            
            outcome_key = result.deliberation.outcome.value
            outcomes_over_time[hour_bucket][outcome_key] += 1
        
        # Princípios mais invocados
        principle_counts = {}
        for result in self.alignment_history:
            for principle in result.deliberation.principles_invoked:
                principle_counts[principle] = principle_counts.get(principle, 0) + 1
        
        return {
            "total_deliberations": len(self.alignment_history),
            "outcomes_over_time": outcomes_over_time,
            "most_invoked_principles": sorted(
                principle_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10],
            "conflict_patterns": self.conscience.conflict_patterns
        }


# Função utilitária para criar engine com configuração rápida
def create_alignment_engine(
    constitution_name: str = "default",
    strict_mode: bool = False,
    enable_logging: bool = True
) -> AlignmentEngine:
    """
    Cria um AlignmentEngine com configuração simplificada.
    
    Args:
        constitution_name: Nome da constituição a carregar
        strict_mode: Se True, rejeita qualquer dúvida moral
        enable_logging: Se True, loga todas as deliberações
        
    Returns:
        AlignmentEngine configurado
    """
    config = AlignmentConfig(
        auto_reject_critical_violations=True,
        log_all_deliberations=enable_logging,
        require_high_confidence=strict_mode,
        minimum_confidence_threshold=0.8 if strict_mode else 0.5,
        enable_learning=True
    )
    
    return AlignmentEngine(config=config)
