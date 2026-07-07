"""
Reflection Engine - Sistema de reflexão pós-ação

Avalia resultados e aprende com experiências
"""

from typing import List, Dict, Optional
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
            "confidence_after": self.confidence_after
        }


class ReflectionEngine:
    """
    Motor de reflexão
    
    - Analisa resultados de ações
    - Extrai lições aprendidas
    - Sugere melhorias para futuras execuções
    """
    
    def __init__(self, max_history: int = 100):
        self.max_history = max_history
        self.reflections: List[Reflection] = []
    
    def create_reflection(
        self,
        action: str,
        expected: str,
        actual: str,
        confidence_before: float = 0.5
    ) -> Reflection:
        """Cria nova reflexão"""
        reflection_id = f"refl_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Determina sucesso baseado em similaridade entre esperado e atual
        # Em produção, usaria LLM para avaliar
        success = self._evaluate_success(expected, actual)
        
        reflection = Reflection(
            id=reflection_id,
            action_description=action,
            expected_outcome=expected,
            actual_outcome=actual,
            success=success,
            confidence_before=confidence_before,
            confidence_after=confidence_before if success else confidence_before * 0.8
        )
        
        # Gera lições aprendidas
        reflection.lessons_learned = self._generate_lessons(reflection)
        reflection.improvements = self._generate_improvements(reflection)
        
        self.reflections.append(reflection)
        
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
        error_indicators = ["error", "fail", "exception", "não conseguiu", "falha"]
        actual_lower = actual.lower()
        
        has_error = any(indicator in actual_lower for indicator in error_indicators)
        return not has_error
    
    def _generate_lessons(self, reflection: Reflection) -> List[str]:
        """Gera lições aprendidas da reflexão"""
        lessons = []
        
        if reflection.success:
            lessons.append(f"Ação '{reflection.action_description}' foi eficaz")
            if reflection.confidence_before < 0.7:
                lessons.append("Subestimei a eficácia desta abordagem")
        else:
            lessons.append(f"Ação '{reflection.action_description}' não produziu resultado esperado")
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
        
        return improvements
    
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
            "overall_success_rate": self.get_success_rate()
        }
    
    def export_reflections(self, filepath: str):
        """Exporta reflexões para arquivo JSON"""
        with open(filepath, 'w') as f:
            json.dump([r.to_dict() for r in self.reflections], f, indent=2)
    
    def get_summary(self) -> Dict:
        """Retorna resumo das reflexões"""
        return {
            "total_reflections": len(self.reflections),
            "success_rate": self.get_success_rate(),
            "recent_successes": sum(1 for r in self.reflections[-10:] if r.success),
            "recent_failures": sum(1 for r in self.reflections[-10:] if not r.success)
        }
