"""
Reflection Engine - Sistema de reflexão pós-ação com aprendizado baseado em erros

Avalia resultados, extrai lições e REESCREVE regras internas para evitar repetição de falhas.
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class Reflection:
    """Reflexão sobre uma ação executada"""
    id: str
    action_description: str
    expected_outcome: str
    actual_outcome: str
    success: bool
    lessons_learned: List[str] = field(default_factory=list)
    improvements: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    confidence_before: float = 0.0
    confidence_after: float = 0.0
    error_type: Optional[str] = None
    root_cause: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "action_description": self.action_description,
            "expected_outcome": self.expected_outcome,
            "actual_outcome": self.actual_outcome,
            "success": self.success,
            "lessons_learned": self.lessons_learned,
            "improvements": self.improvements,
            "timestamp": self.timestamp.isoformat(),
            "confidence_before": self.confidence_before,
            "confidence_after": self.confidence_after,
            "error_type": self.error_type,
            "root_cause": self.root_cause
        }


@dataclass
class LearningRule:
    """
    Regra interna aprendida a partir de erros.
    O agente usa essas regras para ajustar comportamento futuro.
    """
    id: str
    trigger_pattern: str  # Padrão que ativa a regra
    rule_description: str
    action_adjustment: str  # Como ajustar a ação
    confidence: float = 0.5  # Confiança na regra
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    applications_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "trigger_pattern": self.trigger_pattern,
            "rule_description": self.rule_description,
            "action_adjustment": self.action_adjustment,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "applications_count": self.applications_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "is_active": self.is_active
        }
    
    def record_application(self, success: bool):
        """Registra aplicação da regra e atualiza estatísticas."""
        self.applications_count += 1
        if success:
            self.success_count += 1
            self.confidence = min(1.0, self.confidence + 0.05)
        else:
            self.failure_count += 1
            self.confidence = max(0.0, self.confidence - 0.1)
        
        self.updated_at = datetime.now()
        
        # Desativa regra se confiança cair muito
        if self.confidence < 0.3:
            self.is_active = False


class ReflectionEngine:
    """
    Motor de reflexão com aprendizado baseado em erros.
    
    - Analisa resultados de ações
    - Extrai lições aprendidas
    - Identifica causa raiz de falhas
    - Cria/regula regras internas para evitar repetição
    - Ajusta confiança em estratégias baseado em histórico
    """
    
    def __init__(self, max_history: int = 100, max_rules: int = 50):
        self.max_history = max_history
        self.max_rules = max_rules
        self.reflections: List[Reflection] = []
        self.learning_rules: Dict[str, LearningRule] = {}
        self.error_patterns: Dict[str, int] = {}  # Contagem de padrões de erro
    
    def create_reflection(
        self,
        action: str,
        expected: str,
        actual: str,
        confidence_before: float = 0.5
    ) -> Reflection:
        """Cria nova reflexão com análise de causa raiz"""
        reflection_id = f"refl_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Determina sucesso baseado em similaridade entre esperado e atual
        success = self._evaluate_success(expected, actual)
        
        # Identifica tipo de erro e causa raiz se falhou
        error_type = None
        root_cause = None
        
        if not success:
            error_type = self._classify_error(actual)
            root_cause = self._infer_root_cause(action, expected, actual)
            
            # Atualiza contagem de padrões de erro
            if error_type:
                self.error_patterns[error_type] = self.error_patterns.get(error_type, 0) + 1
        
        reflection = Reflection(
            id=reflection_id,
            action_description=action,
            expected_outcome=expected,
            actual_outcome=actual,
            success=success,
            confidence_before=confidence_before,
            confidence_after=confidence_before if success else confidence_before * 0.8,
            error_type=error_type,
            root_cause=root_cause
        )
        
        # Gera lições aprendidas
        reflection.lessons_learned = self._generate_lessons(reflection)
        reflection.improvements = self._generate_improvements(reflection)
        
        self.reflections.append(reflection)
        
        # Se houve erro, cria ou atualiza regra de aprendizado
        if not success and (error_type or root_cause):
            self._create_or_update_learning_rule(reflection)
        
        # Limita histórico
        if len(self.reflections) > self.max_history:
            self.reflections = self.reflections[-self.max_history:]
        
        return reflection
    
    def _evaluate_success(self, expected: str, actual: str) -> bool:
        """
        Avalia se resultado foi bem-sucedido
        
        Em produção, usaria LLM para avaliação semântica
        Aqui usa heurística simples
        """
        # Heurística básica: verifica se há palavras de erro no resultado
        error_indicators = ["error", "fail", "exception", "não conseguiu", "falha", "timeout"]
        actual_lower = actual.lower()
        
        has_error = any(indicator in actual_lower for indicator in error_indicators)
        return not has_error
    
    def _classify_error(self, actual: str) -> Optional[str]:
        """Classifica o tipo de erro baseado na descrição do resultado."""
        actual_lower = actual.lower()
        
        if "timeout" in actual_lower or "time out" in actual_lower:
            return "timeout"
        elif "quota" in actual_lower or "limit" in actual_lower or "rate limit" in actual_lower:
            return "quota_exceeded"
        elif "connection" in actual_lower or "network" in actual_lower:
            return "network_error"
        elif "permission" in actual_lower or "access denied" in actual_lower:
            return "permission_error"
        elif "not found" in actual_lower or "404" in actual_lower:
            return "resource_not_found"
        elif "invalid" in actual_lower or "malformed" in actual_lower:
            return "invalid_input"
        elif "exception" in actual_lower or "traceback" in actual_lower:
            return "runtime_exception"
        else:
            return "unknown_error"
    
    def _infer_root_cause(self, action: str, expected: str, actual: str) -> str:
        """
        Infere causa raiz do erro baseado em padrões.
        Em produção, usaria LLM para análise mais sofisticada.
        """
        actual_lower = actual.lower()
        
        # Análise baseada em padrões comuns
        if "api" in actual_lower and ("rate" in actual_lower or "limit" in actual_lower):
            return "Excesso de chamadas API em curto período"
        elif "memory" in actual_lower:
            return "Recursos de memória insuficientes"
        elif "disk" in actual_lower:
            return "Espaço em disco insuficiente"
        elif "context" in actual_lower or "token" in actual_lower:
            return "Limite de contexto/tokens excedido"
        elif "dependency" in actual_lower or "missing" in actual_lower:
            return "Dependência externa não disponível"
        elif "assumption" in actual_lower or "premise" in actual_lower:
            return "Premissa incorreta sobre o estado do sistema"
        else:
            return "Causa raiz não identificada automaticamente"
    
    def _generate_lessons(self, reflection: Reflection) -> List[str]:
        """Gera lições aprendidas da reflexão"""
        lessons = []
        
        if reflection.success:
            lessons.append(f"Ação '{reflection.action_description}' foi eficaz")
            if reflection.confidence_before < 0.7:
                lessons.append("Subestimei a eficácia desta abordagem")
        else:
            lessons.append(f"Ação '{reflection.action_description}' não produziu resultado esperado")
            
            if reflection.error_type:
                lessons.append(f"Tipo de erro identificado: {reflection.error_type}")
            
            if reflection.root_cause:
                lessons.append(f"Causa raiz provável: {reflection.root_cause}")
            
            lessons.append("Necessário revisar estratégia")
        
        return lessons
    
    def _generate_improvements(self, reflection: Reflection) -> List[str]:
        """Gera sugestões de melhoria"""
        improvements = []
        
        if not reflection.success:
            improvements.append("Considerar abordagem alternativa")
            improvements.append("Validar premissas antes de executar")
            
            if reflection.confidence_before > 0.8:
                improvements.append("Reduzir confiança em situações similares")
            
            # Melhorias específicas baseadas no tipo de erro
            if reflection.error_type == "timeout":
                improvements.append("Implementar retry com backoff exponencial")
                improvements.append("Aumentar timeout ou dividir operação em partes menores")
            elif reflection.error_type == "quota_exceeded":
                improvements.append("Implementar rate limiting local")
                improvements.append("Alternar para conta/provider alternativo")
            elif reflection.error_type == "network_error":
                improvements.append("Adicionar retry com validação de conectividade")
            elif reflection.error_type == "permission_error":
                improvements.append("Validar permissões antes de executar ação crítica")
            elif reflection.error_type == "invalid_input":
                improvements.append("Adicionar validação de input antes de processamento")
        
        return improvements
    
    def _create_or_update_learning_rule(self, reflection: Reflection):
        """
        Cria ou atualiza regra de aprendizado baseada na reflexão de erro.
        Esta é a chave do aprendizado contínuo do agente.
        """
        # Gera padrão de trigger baseado no tipo de erro e ação
        trigger_pattern = f"{reflection.error_type}:{reflection.action_description[:30]}"
        
        if trigger_pattern in self.learning_rules:
            # Atualiza regra existente
            rule = self.learning_rules[trigger_pattern]
            rule.rule_description += f"\n[Atualizado] {reflection.root_cause}"
            rule.updated_at = datetime.now()
        else:
            # Cria nova regra
            if len(self.learning_rules) >= self.max_rules:
                self._evict_low_confidence_rules()
            
            rule_id = f"rule_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            rule = LearningRule(
                id=rule_id,
                trigger_pattern=trigger_pattern,
                rule_description=f"Erro em '{reflection.action_description}': {reflection.root_cause}",
                action_adjustment=self._generate_action_adjustment(reflection),
                confidence=0.5
            )
            self.learning_rules[trigger_pattern] = rule
    
    def _generate_action_adjustment(self, reflection: Reflection) -> str:
        """Gera ajuste específico de ação baseado no erro."""
        adjustments = {
            "timeout": "Reduzir complexidade da operação ou aumentar timeout",
            "quota_exceeded": "Verificar quota antes de executar; alternar conta se necessário",
            "network_error": "Validar conectividade; implementar retry",
            "permission_error": "Verificar permissões; solicitar autorização se crítico",
            "invalid_input": "Validar input contra schema antes de processar",
            "runtime_exception": "Adicionar try-catch; loggar detalhes para debugging"
        }
        
        return adjustments.get(
            reflection.error_type, 
            "Revisar abordagem e validar premissas"
        )
    
    def _evict_low_confidence_rules(self):
        """Remove regras com baixa confiança para liberar espaço."""
        inactive_rules = [
            (pattern, rule) for pattern, rule in self.learning_rules.items()
            if not rule.is_active or rule.confidence < 0.3
        ]
        
        # Remove as mais antigas primeiro
        inactive_rules.sort(key=lambda x: x[1].created_at)
        
        for pattern, _ in inactive_rules[:len(inactive_rules)//2 + 1]:
            del self.learning_rules[pattern]
    
    def get_applicable_rules(self, context: Dict[str, Any]) -> List[LearningRule]:
        """
        Retorna regras aplicáveis ao contexto atual.
        Usado pelo PlanningEngine para ajustar planos.
        """
        applicable = []
        
        for rule in self.learning_rules.values():
            if not rule.is_active:
                continue
            
            # Verifica se padrão de trigger match com contexto
            trigger_parts = rule.trigger_pattern.split(":")
            error_type = trigger_parts[0] if trigger_parts else ""
            
            # Match simples: verifica se contexto menciona o erro
            context_str = json.dumps(context).lower()
            if error_type.lower() in context_str:
                applicable.append(rule)
        
        # Ordena por confiança
        applicable.sort(key=lambda x: x.confidence, reverse=True)
        
        return applicable
    
    def get_reflections_for_action(self, action_pattern: str) -> List[Reflection]:
        """Busca reflexões relacionadas a padrão de ação"""
        return [
            r for r in self.reflections 
            if action_pattern.lower() in r.action_description.lower()
        ]
    
    def get_recent_reflections(self, n: int = 10) -> List[Reflection]:
        """Retorna últimas n reflexões"""
        return self.reflections[-n:]
    
    def get_success_rate(self) -> float:
        """Retorna taxa de sucesso histórica"""
        if not self.reflections:
            return 0.0
        
        successes = sum(1 for r in self.reflections if r.success)
        return successes / len(self.reflections)
    
    def get_error_distribution(self) -> Dict[str, int]:
        """Retorna distribuição de tipos de erro."""
        return dict(sorted(
            self.error_patterns.items(),
            key=lambda x: x[1],
            reverse=True
        ))
    
    def get_patterns(self) -> Dict:
        """Identifica padrões nas reflexões"""
        if not self.reflections:
            return {}
        
        # Ações mais comuns
        action_counts = {}
        for r in self.reflections:
            action = r.action_description[:50]  # Trunca para agrupar
            action_counts[action] = action_counts.get(action, 0) + 1
        
        # Taxa de sucesso por tipo de ação
        success_by_action = {}
        for r in self.reflections:
            action = r.action_description[:50]
            if action not in success_by_action:
                success_by_action[action] = {"success": 0, "total": 0}
            success_by_action[action]["total"] += 1
            if r.success:
                success_by_action[action]["success"] += 1
        
        return {
            "most_common_actions": sorted(
                action_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5],
            "success_by_action": {
                k: v["success"] / v["total"] 
                for k, v in success_by_action.items()
            },
            "overall_success_rate": self.get_success_rate(),
            "error_distribution": self.get_error_distribution(),
            "active_learning_rules": len([r for r in self.learning_rules.values() if r.is_active])
        }
    
    def export_reflections(self, filepath: str):
        """Exporta reflexões para arquivo JSON"""
        with open(filepath, 'w') as f:
            json.dump([r.to_dict() for r in self.reflections], f, indent=2)
    
    def export_learning_rules(self, filepath: str):
        """Exporta regras de aprendizado para arquivo JSON"""
        with open(filepath, 'w') as f:
            json.dump([r.to_dict() for r in self.learning_rules.values()], f, indent=2)
    
    def get_summary(self) -> Dict:
        """Retorna resumo das reflexões e aprendizado"""
        active_rules = [r for r in self.learning_rules.values() if r.is_active]
        
        return {
            "total_reflections": len(self.reflections),
            "success_rate": self.get_success_rate(),
            "recent_successes": sum(1 for r in self.reflections[-10:] if r.success),
            "recent_failures": sum(1 for r in self.reflections[-10:] if not r.success),
            "active_learning_rules": len(active_rules),
            "avg_rule_confidence": sum(r.confidence for r in active_rules) / len(active_rules) if active_rules else 0.0,
            "top_error_types": list(self.get_error_distribution().items())[:5]
        }
