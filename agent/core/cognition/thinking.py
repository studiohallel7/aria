"""
Thinking Engine - Internal thought processing.
Handles reasoning, planning, and curiosity generation.
"""

import random
from typing import Dict, Any, List, Optional
from datetime import datetime

from core.state.agent_state import AgentStatus, ContextManager


class ThinkingEngine:
    """Engine for internal thought processing."""
    
    def __init__(self, max_depth: int = 5):
        self.max_depth = max_depth
        self.current_depth = 0
    
    def think(self, task: str, state: AgentStatus, ctx: ContextManager) -> Dict[str, Any]:
        """Think about a task and generate a plan."""
        if self.current_depth >= self.max_depth:
            return {
                "status": "max_depth_reached",
                "message": "Profundidade máxima de pensamento atingida",
            }
        
        self.current_depth += 1
        
        # Get context for thinking
        context = ctx.get_context(limit=10)
        
        # Generate thought process (simplified - would use LLM in production)
        thought = {
            "task": task,
            "context_used": len(context),
            "depth": self.current_depth,
            "timestamp": datetime.now().isoformat(),
            "considerations": self._generate_considerations(task, context),
        }
        
        self.current_depth -= 1
        return thought
    
    def _generate_considerations(self, task: str, context: List[str]) -> List[str]:
        """Generate considerations for the task."""
        considerations = []
        
        # Check if task relates to recent context
        for ctx_item in context[-3:]:
            if any(word in task.lower() for word in ctx_item.lower().split()[:5]):
                considerations.append(f"Relacionado ao contexto recente: {ctx_item[:50]}...")
        
        # Add general considerations
        considerations.append("Verificar recursos disponíveis")
        considerations.append("Avaliar riscos e segurança")
        considerations.append("Considerar estado atual do sistema")
        
        return considerations
    
    def generate_curiosity_topic(self, ctx: ContextManager) -> str:
        """Generate a curiosity-based exploration topic."""
        topics = [
            "Explorar novos padrões no código",
            "Analisar eficiência das operações recentes",
            "Investigar melhorias possíveis na arquitetura",
            "Revisar decisões anteriores",
            "Buscar correlações entre tarefas",
        ]
        
        # Weight by context
        if len(ctx.items) > 20:
            topics.append("Sintetizar conhecimento acumulado")
        
        return random.choice(topics)
    
    def reset_depth(self) -> None:
        """Reset thought depth counter."""
        self.current_depth = 0