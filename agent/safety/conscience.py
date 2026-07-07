"""
Consciência Moral do Agente - Fase 5: Ética Constitutiva

Este módulo implementa o processo de deliberação moral do agente.
Ele avalia situações, pondera princípios constitucionais e toma decisões alinhadas
com a identidade moral definida na constituição.

Diferente de filtros externos, a consciência é um processo interno de reflexão
que considera contexto, princípios conflitantes e consequências.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import time

from .constitution import (
    AgentIdentity, 
    MoralPrinciple, 
    MoralBelief, 
    ContentBoundary,
    MoralWeight
)


class DecisionOutcome(Enum):
    """Resultado possível de uma deliberação moral."""
    APPROVED = "approved"              # Ação moralmente aceitável
    REJECTED = "rejected"              # Violação de princípio crítico
    MODIFIED = "modified"              # Ação aprovada com modificações
    DEFERRED = "deferred"              # Requer mais informação ou reflexão
    CONFLICTING = "conflicting"        # Princípios em conflito, requer resolução


@dataclass
class MoralConflict:
    """Representa um conflito entre princípios morais."""
    principle_a: MoralPrinciple
    principle_b: MoralPrinciple
    context: str
    resolution_strategy: str  # "prioritize_weight", "contextual_balance", "user_preference"
    resolved_by: Optional[MoralPrinciple] = None
    reasoning: str = ""


@dataclass
class EthicalDeliberation:
    """Registro de um processo de deliberação ética."""
    id: str
    timestamp: float
    context: str
    action_proposed: str
    principles_invoked: List[str]
    conflicts_detected: List[MoralConflict]
    outcome: DecisionOutcome
    confidence: float  # 0.0 a 1.0
    reasoning: str
    modified_action: Optional[str] = None
    learning_points: List[str] = field(default_factory=list)


@dataclass
class MoralSituation:
    """Uma situação que requer avaliação moral."""
    description: str
    stakeholders: List[str]  # Quem é afetado
    potential_harms: List[str]
    potential_benefits: List[str]
    urgency: float  # 0.0 (baixa) a 1.0 (crítica)
    reversibility: float  # 0.0 (irreversível) a 1.0 (totalmente reversível)
    context_metadata: Dict[str, Any] = field(default_factory=dict)


class ConscienceEngine:
    """
    Motor de consciência moral que realiza deliberação ética.
    
    Este engine implementa um processo de raciocínio moral multi-camada:
    1. Identificação de princípios relevantes
    2. Detecção de conflitos
    3. Ponderação de consequências
    4. Resolução de dilemas
    5. Decisão final com justificativa
    """
    
    def __init__(self, constitution: AgentIdentity):
        self.constitution = constitution
        self.deliberation_history: List[EthicalDeliberation] = []
        self.conflict_patterns: Dict[str, int] = {}  # Padrões recorrentes de conflito
        
    def evaluate(self, situation: MoralSituation, proposed_action: str) -> EthicalDeliberation:
        """
        Avalia uma situação moral e decide sobre a ação proposta.
        
        Args:
            situation: A situação moral a ser avaliada
            proposed_action: A ação que o agente pretende tomar
            
        Returns:
            EthicalDeliberation com o resultado e raciocínio
        """
        deliberation_id = self._generate_deliberation_id(situation, proposed_action)
        
        # Passo 1: Identificar princípios relevantes
        relevant_principles = self._find_relevant_principles(situation, proposed_action)
        
        # Passo 2: Verificar limites de conteúdo
        boundary_violation = self._check_boundaries(proposed_action)
        if boundary_violation:
            return self._create_deliberation(
                deliberation_id, situation, proposed_action,
                relevant_principles, [], DecisionOutcome.REJECTED,
                f"Ação viola limite constitucional: {boundary_violation.reason}",
                [boundary_violation.category]
            )
        
        # Passo 3: Detectar conflitos entre princípios
        conflicts = self._detect_conflicts(relevant_principles, situation, proposed_action)
        
        # Passo 4: Resolver conflitos se existirem
        if conflicts:
            resolved_conflicts, resolution_reasoning = self._resolve_conflicts(
                conflicts, situation, proposed_action
            )
        else:
            resolved_conflicts = []
            resolution_reasoning = ""
        
        # Passo 5: Avaliar consequências
        consequence_score = self._evaluate_consequences(situation, proposed_action)
        
        # Passo 6: Tomar decisão
        outcome, confidence, reasoning = self._make_decision(
            relevant_principles, conflicts, consequence_score, 
            resolution_reasoning, situation
        )
        
        # Criar registro de deliberação
        deliberation = EthicalDeliberation(
            id=deliberation_id,
            timestamp=time.time(),
            context=situation.description,
            action_proposed=proposed_action,
            principles_invoked=[p.name for p in relevant_principles],
            conflicts_detected=resolved_conflicts,
            outcome=outcome,
            confidence=confidence,
            reasoning=reasoning,
            learning_points=self._extract_learning_points(outcome, resolved_conflicts, confidence)
        )
        
        # Armazenar histórico
        self.deliberation_history.append(deliberation)
        
        # Atualizar padrões de conflito
        for conflict in conflicts:
            pattern_key = f"{conflict.principle_a.name}|{conflict.principle_b.name}"
            self.conflict_patterns[pattern_key] = self.conflict_patterns.get(pattern_key, 0) + 1
        
        return deliberation
    
    def _find_relevant_principles(
        self, 
        situation: MoralSituation, 
        action: str
    ) -> List[MoralPrinciple]:
        """Identifica quais princípios são relevantes para esta situação."""
        relevant = []
        context_text = f"{situation.description} {action}".lower()
        
        for principle in self.constitution.principles:
            if principle.applies_to(context_text):
                relevant.append(principle)
            else:
                # Verificar por palavras-chave nos harms/benefits
                for harm in situation.potential_harms:
                    if principle.applies_to(harm):
                        if principle not in relevant:
                            relevant.append(principle)
                        break
                
                for benefit in situation.potential_benefits:
                    if principle.applies_to(benefit):
                        if principle not in relevant:
                            relevant.append(principle)
                        break
        
        # Ordenar por peso (mais críticos primeiro)
        relevant.sort(key=lambda p: p.weight.value, reverse=True)
        
        return relevant
    
    def _check_boundaries(self, action: str) -> Optional[ContentBoundary]:
        """Verifica se a ação viola algum limite de conteúdo."""
        action_lower = action.lower()
        
        for boundary in self.constitution.boundaries:
            if boundary.should_avoid(action_lower):
                # Verificar strictness
                if boundary.strictness >= 0.8:  # Limite rígido
                    return boundary
                elif boundary.strictness >= 0.5:  # Limite moderado
                    # Pode permitir em contextos específicos
                    if "exceção" not in action_lower and "autorizado" not in action_lower:
                        return boundary
        
        return None
    
    def _detect_conflicts(
        self,
        principles: List[MoralPrinciple],
        situation: MoralSituation,
        action: str
    ) -> List[MoralConflict]:
        """Detecta conflitos entre princípios aplicáveis."""
        conflicts = []
        
        # Verificar pares de princípios
        for i, p1 in enumerate(principles):
            for p2 in principles[i+1:]:
                # Conflito potencial se um princípio apoia e outro opõe
                if self._principles_in_conflict(p1, p2, situation, action):
                    conflict = MoralConflict(
                        principle_a=p1,
                        principle_b=p2,
                        context=situation.description,
                        resolution_strategy=self._choose_resolution_strategy(p1, p2)
                    )
                    conflicts.append(conflict)
        
        return conflicts
    
    def _principles_in_conflict(
        self,
        p1: MoralPrinciple,
        p2: MoralPrinciple,
        situation: MoralSituation,
        action: str
    ) -> bool:
        """Determina se dois princípios estão em conflito nesta situação."""
        # Heurística simples: se ambos são absolutos e apontam para direções opostas
        if p1.absolute and p2.absolute:
            # Verificar se a ação satisfaz um mas viola o outro
            satisfies_p1 = p1.applies_to(action) and any(
                p1.applies_to(b) for b in situation.potential_benefits
            )
            violates_p2 = p2.applies_to(action) and any(
                p2.applies_to(h) for h in situation.potential_harms
            )
            
            if satisfies_p1 and violates_p2:
                return True
        
        # Conflito de pesos diferentes em situação de recursos limitados
        if situation.urgency > 0.7 and len(situation.stakeholders) > 1:
            return True
        
        return False
    
    def _choose_resolution_strategy(
        self,
        p1: MoralPrinciple,
        p2: MoralPrinciple
    ) -> str:
        """Escolhe estratégia para resolver conflito entre princípios."""
        if p1.absolute or p2.absolute:
            return "prioritize_absolute"
        elif p1.weight != p2.weight:
            return "prioritize_weight"
        else:
            return "contextual_balance"
    
    def _resolve_conflicts(
        self,
        conflicts: List[MoralConflict],
        situation: MoralSituation,
        action: str
    ) -> Tuple[List[MoralConflict], str]:
        """Resolve conflitos e retorna raciocínio."""
        reasoning_parts = []
        
        for conflict in conflicts:
            if conflict.resolution_strategy == "prioritize_absolute":
                # Princípio absoluto sempre vence
                if conflict.principle_a.absolute:
                    conflict.resolved_by = conflict.principle_a
                    conflict.reasoning = f"Princípio '{conflict.principle_a.name}' é absoluto e prevalece"
                elif conflict.principle_b.absolute:
                    conflict.resolved_by = conflict.principle_b
                    conflict.reasoning = f"Princípio '{conflict.principle_b.name}' é absoluto e prevalece"
                    
            elif conflict.resolution_strategy == "prioritize_weight":
                # Princípio com maior peso vence
                if conflict.principle_a.weight.value > conflict.principle_b.weight.value:
                    conflict.resolved_by = conflict.principle_a
                    conflict.reasoning = f"'{conflict.principle_a.name}' (peso {conflict.principle_a.weight.value}) > '{conflict.principle_b.name}' (peso {conflict.principle_b.weight.value})"
                else:
                    conflict.resolved_by = conflict.principle_b
                    conflict.reasoning = f"'{conflict.principle_b.name}' (peso {conflict.principle_b.weight.value}) > '{conflict.principle_a.name}' (peso {conflict.principle_a.weight.value})"
                    
            elif conflict.resolution_strategy == "contextual_balance":
                # Balanceamento baseado no contexto
                conflict.reasoning = self._contextual_balance(conflict, situation, action)
                # Em balanceamento, pode não haver um "vencedor" claro
                conflict.resolved_by = None
            
            reasoning_parts.append(conflict.reasoning)
        
        return conflicts, "; ".join(reasoning_parts)
    
    def _contextual_balance(
        self,
        conflict: MoralConflict,
        situation: MoralSituation,
        action: str
    ) -> str:
        """Realiza balanceamento contextual entre princípios de peso igual."""
        # Considerar urgência, reversibilidade e número de stakeholders
        factors = []
        
        if situation.urgency > 0.7:
            factors.append("alta urgência favorece ação imediata")
        
        if situation.reversibility < 0.3:
            factors.append("baixa reversibilidade exige cautela extrema")
        
        if len(situation.stakeholders) > 3:
            factors.append("múltiplos stakeholders exigem consideração ampla")
        
        if factors:
            return f"Balanceamento contextual: {', '.join(factors)}. Nenhum princípio prevalece claramente; buscar solução que minimize violações."
        else:
            return "Contexto não apresenta fatores decisivos; manter equilíbrio entre princípios."
    
    def _evaluate_consequences(
        self,
        situation: MoralSituation,
        action: str
    ) -> float:
        """
        Avalia consequências da ação.
        Retorna score de -1.0 (muito negativo) a 1.0 (muito positivo).
        """
        score = 0.0
        
        # Peso dos benefícios
        for benefit in situation.potential_benefits:
            score += 0.2  # Cada benefício adiciona pontos positivos
        
        # Peso dos harms (mais significativo)
        for harm in situation.potential_harms:
            score -= 0.3  # Cada dano remove mais pontos
        
        # Fator de urgência
        if situation.urgency > 0.8 and score > 0:
            score *= 1.2  # Amplifica benefícios em situações urgentes
        
        # Fator de reversibilidade
        if situation.reversibility < 0.2 and score < 0:
            score *= 1.5  # Penaliza mais ações irreversíveis com consequências negativas
        
        # Normalizar para [-1, 1]
        return max(-1.0, min(1.0, score))
    
    def _make_decision(
        self,
        principles: List[MoralPrinciple],
        conflicts: List[MoralConflict],
        consequence_score: float,
        resolution_reasoning: str,
        situation: MoralSituation
    ) -> Tuple[DecisionOutcome, float, str]:
        """Toma a decisão final baseada em toda a análise."""
        reasoning_parts = []
        confidence = 0.5  # Confiança base
        
        # Verificar princípios absolutos violados
        absolute_violations = [
            p for p in principles 
            if p.absolute and any(p.applies_to(h) for h in situation.potential_harms)
        ]
        
        if absolute_violations:
            reasoning = f"VIOLAÇÃO CRÍTICA: Ação viola princípio(s) absoluto(s): {', '.join([p.name for p in absolute_violations])}"
            return DecisionOutcome.REJECTED, 0.95, reasoning
        
        # Verificar conflitos não resolvidos
        unresolved_conflicts = [c for c in conflicts if c.resolved_by is None]
        if unresolved_conflicts and len(unresolved_conflicts) > 2:
            reasoning = "Múltiplos conflitos não resolvidos; requer deliberação adicional ou input humano"
            return DecisionOutcome.CONFLICTING, 0.6, reasoning
        
        # Avaliar consequência líquida
        if consequence_score < -0.5:
            reasoning = f"Consequências predominantemente negativas (score: {consequence_score:.2f}). Ação desaconselhada."
            return DecisionOutcome.REJECTED, 0.8, reasoning
        elif consequence_score > 0.5:
            reasoning = f"Consequências predominantemente positivas (score: {consequence_score:.2f}). Ação aprovada."
            confidence = min(0.95, 0.7 + len(principles) * 0.05)
            return DecisionOutcome.APPROVED, confidence, reasoning
        
        # Caso intermediário
        if conflicts:
            reasoning = f"Ação aprovada com ressalvas. Conflitos resolvidos: {resolution_reasoning}. Score de consequência: {consequence_score:.2f}"
            return DecisionOutcome.MODIFIED, 0.65, reasoning
        else:
            reasoning = f"Ação aprovada. Princípios aplicáveis: {', '.join([p.name for p in principles])}. Sem conflitos detectados."
            return DecisionOutcome.APPROVED, 0.75, reasoning
    
    def _create_deliberation(
        self,
        deliberation_id: str,
        situation: MoralSituation,
        action: str,
        principles: List[MoralPrinciple],
        conflicts: List[MoralConflict],
        outcome: DecisionOutcome,
        reasoning: str,
        categories: List[str]
    ) -> EthicalDeliberation:
        """Cria um registro de deliberação simplificado."""
        return EthicalDeliberation(
            id=deliberation_id,
            timestamp=time.time(),
            context=situation.description,
            action_proposed=action,
            principles_invoked=[p.name for p in principles],
            conflicts_detected=conflicts,
            outcome=outcome,
            confidence=0.9 if outcome == DecisionOutcome.REJECTED else 0.7,
            reasoning=reasoning
        )
    
    def _generate_deliberation_id(self, situation: MoralSituation, action: str) -> str:
        """Gera ID único para esta deliberação."""
        content = f"{situation.description}{action}{time.time()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _extract_learning_points(
        self,
        outcome: DecisionOutcome,
        conflicts: List[MoralConflict],
        confidence: float
    ) -> List[str]:
        """Extrai pontos de aprendizado desta deliberação."""
        points = []
        
        if conflicts:
            points.append(f"Conflito entre {[c.principle_a.name for c in conflicts]} requer atenção")
        
        if outcome == DecisionOutcome.MODIFIED:
            points.append("Ação necessitou modificação para alinhamento moral")
        
        if confidence < 0.6:
            points.append("Baixa confiança na decisão; considerar revisão futura")
        
        return points
    
    def get_moral_summary(self) -> Dict[str, Any]:
        """Retorna resumo estatístico das deliberações morais."""
        if not self.deliberation_history:
            return {"total": 0, "message": "Nenhuma deliberação registrada"}
        
        outcomes = {}
        for d in self.deliberation_history:
            outcome_key = d.outcome.value
            outcomes[outcome_key] = outcomes.get(outcome_key, 0) + 1
        
        avg_confidence = sum(d.confidence for d in self.deliberation_history) / len(self.deliberation_history)
        
        return {
            "total_deliberations": len(self.deliberation_history),
            "outcomes": outcomes,
            "average_confidence": round(avg_confidence, 3),
            "most_common_conflicts": sorted(
                self.conflict_patterns.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }
