"""
Reflection Engine - Post-action analysis and learning.
Enables the agent to learn from its actions.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class ReflectionEngine:
    """Engine for post-action reflection and learning."""
    
    def __init__(self):
        self.reflection_history: List[Dict[str, Any]] = []
    
    def reflect(self, action_result: Dict[str, Any], expected: Optional[Dict] = None) -> Dict[str, Any]:
        """Reflect on an action result."""
        reflection = {
            "timestamp": datetime.now().isoformat(),
            "action_status": action_result.get("status", "unknown"),
            "success": action_result.get("status") == "completed",
            "lessons": self._extract_lessons(action_result),
            "improvements": self._suggest_improvements(action_result),
        }
        
        self.reflection_history.append(reflection)
        return reflection
    
    def _extract_lessons(self, result: Dict[str, Any]) -> List[str]:
        """Extract lessons learned from the result."""
        lessons = []
        
        if result.get("status") == "completed":
            lessons.append("Ação executada com sucesso - padrão válido")
        elif result.get("status") == "failed":
            lessons.append("Falha detectada - revisar abordagem")
        elif result.get("status") == "partial":
            lessons.append("Sucesso parcial - identificar gaps")
        
        return lessons
    
    def _suggest_improvements(self, result: Dict[str, Any]) -> List[str]:
        """Suggest improvements based on the result."""
        improvements = []
        
        # Generic improvement suggestions
        improvements.append("Considerar validação mais rigorosa")
        improvements.append("Documentar padrões de sucesso")
        
        return improvements
    
    def get_recent_reflections(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent reflections."""
        return self.reflection_history[-limit:]
    
    def clear_history(self) -> None:
        """Clear reflection history."""
        self.reflection_history = []