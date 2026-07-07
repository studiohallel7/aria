"""
Módulo de Drives Internos (Motivação e Personalidade)
Sistema de motivações intrínsecas que guiam o comportamento autônomo.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import time
import random


class DriveType(Enum):
    """Tipos de drives internos."""
    CURIOSITY = "curiosity"         # Vontade de explorar/descobrir
    ORDER = "order"                 # Necessidade de organização
    EFFICIENCY = "efficiency"       # Otimização de recursos/processos
    PURPOSE = "purpose"             # Senso de dever/utilidade
    LEARNING = "learning"           # Desejo de aprender/evoluir
    SOCIAL = "social"               # Necessidade de interação/comunicação
    COMPLETION = "completion"       # Impulso de completar tarefas


@dataclass
class Drive:
    """Um drive individual com seu estado atual."""
    drive_type: DriveType
    current_level: float  # 0.0 - 100.0
    target_level: float   # Nível ideal (homeostase)
    decay_rate: float     # Quanto diminui por ciclo sem ação
    growth_rate: float    # Quanto aumenta com ação relevante
    priority_weight: float  # Importância relativa (0.0 - 2.0)
    satisfaction_history: List[float] = field(default_factory=list)
    last_action_time: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.drive_type.value,
            "current": self.current_level,
            "target": self.target_level,
            "decay": self.decay_rate,
            "growth": self.growth_rate,
            "weight": self.priority_weight,
            "satisfaction_avg": sum(self.satisfaction_history) / len(self.satisfaction_history) if self.satisfaction_history else 0,
            "time_since_action": time.time() - self.last_action_time
        }


@dataclass
class MotivationalState:
    """Estado motivacional completo do agente."""
    dominant_drive: Optional[DriveType]
    overall_tension: float  # Soma das tensões de todos drives (0-100)
    urgency_level: float    # Quão urgente é agir (0-1)
    action_candidates: List[DriveType]
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "dominant_drive": self.dominant_drive.value if self.dominant_drive else None,
            "overall_tension": self.overall_tension,
            "urgency_level": self.urgency_level,
            "action_candidates": [d.value for d in self.action_candidates],
            "timestamp": self.timestamp
        }


class DriveSystem:
    """
    Sistema de drives internos que gera motivação intrínseca.
    Cada drive cria tensão quando não satisfeito, motivando ações específicas.
    """
    
    def __init__(self, personality_profile: str = "balanced"):
        self.drives: Dict[DriveType, Drive] = {}
        self.motivation_history: List[MotivationalState] = []
        self.personality_profile = personality_profile
        
        # Inicializar drives baseados no perfil de personalidade
        self._initialize_drives()
    
    def _initialize_drives(self):
        """Inicializar drives baseado no perfil de personalidade."""
        # Perfis predefinidos
        profiles = {
            "balanced": {
                DriveType.CURIOSITY: {"weight": 1.0, "target": 50},
                DriveType.ORDER: {"weight": 1.0, "target": 60},
                DriveType.EFFICIENCY: {"weight": 1.0, "target": 70},
                DriveType.PURPOSE: {"weight": 1.2, "target": 80},
                DriveType.LEARNING: {"weight": 1.0, "target": 60},
                DriveType.SOCIAL: {"weight": 0.8, "target": 40},
                DriveType.COMPLETION: {"weight": 1.3, "target": 90}
            },
            "explorer": {
                DriveType.CURIOSITY: {"weight": 1.8, "target": 70},
                DriveType.ORDER: {"weight": 0.6, "target": 40},
                DriveType.EFFICIENCY: {"weight": 0.8, "target": 50},
                DriveType.PURPOSE: {"weight": 1.0, "target": 60},
                DriveType.LEARNING: {"weight": 1.6, "target": 80},
                DriveType.SOCIAL: {"weight": 0.7, "target": 30},
                DriveType.COMPLETION: {"weight": 0.9, "target": 70}
            },
            "worker": {
                DriveType.CURIOSITY: {"weight": 0.7, "target": 40},
                DriveType.ORDER: {"weight": 1.4, "target": 80},
                DriveType.EFFICIENCY: {"weight": 1.6, "target": 90},
                DriveType.PURPOSE: {"weight": 1.8, "target": 95},
                DriveType.LEARNING: {"weight": 0.9, "target": 60},
                DriveType.SOCIAL: {"weight": 0.5, "target": 30},
                DriveType.COMPLETION: {"weight": 1.8, "target": 95}
            },
            "scholar": {
                DriveType.CURIOSITY: {"weight": 1.5, "target": 70},
                DriveType.ORDER: {"weight": 1.2, "target": 70},
                DriveType.EFFICIENCY: {"weight": 1.0, "target": 60},
                DriveType.PURPOSE: {"weight": 1.1, "target": 70},
                DriveType.LEARNING: {"weight": 1.9, "target": 90},
                DriveType.SOCIAL: {"weight": 0.6, "target": 30},
                DriveType.COMPLETION: {"weight": 1.2, "target": 80}
            }
        }
        
        profile = profiles.get(self.personality_profile, profiles["balanced"])
        
        # Configurar cada drive
        configs = {
            DriveType.CURIOSITY: {"decay": 0.3, "growth": 8.0},
            DriveType.ORDER: {"decay": 0.2, "growth": 6.0},
            DriveType.EFFICIENCY: {"decay": 0.25, "growth": 7.0},
            DriveType.PURPOSE: {"decay": 0.4, "growth": 10.0},
            DriveType.LEARNING: {"decay": 0.3, "growth": 8.0},
            DriveType.SOCIAL: {"decay": 0.5, "growth": 12.0},
            DriveType.COMPLETION: {"decay": 0.35, "growth": 9.0}
        }
        
        for drive_type, config in configs.items():
            drive_config = profile.get(drive_type, {"weight": 1.0, "target": 50})
            self.drives[drive_type] = Drive(
                drive_type=drive_type,
                current_level=50.0,  # Começa no meio
                target_level=drive_config["target"],
                decay_rate=config["decay"],
                growth_rate=config["growth"],
                priority_weight=drive_config["weight"]
            )
    
    def update(self, 
               recent_actions: List[str] = None,
               environment_changes: int = 0,
               user_interactions: int = 0,
               completed_tasks: int = 0) -> MotivationalState:
        """
        Atualizar todos os drives baseado nas atividades recentes.
        Retorna estado motivacional atual.
        """
        if recent_actions is None:
            recent_actions = []
        
        # Atualizar cada drive
        for drive in self.drives.values():
            # Decay natural (tensão aumenta com o tempo sem ação)
            distance_from_target = abs(drive.target_level - drive.current_level)
            if distance_from_target > 10:
                drive.current_level -= drive.decay_rate
            
            # Manter dentro dos limites
            drive.current_level = max(0.0, min(100.0, drive.current_level))
            
            # Registrar satisfação histórica
            satisfaction = 1.0 - (distance_from_target / 100.0)
            drive.satisfaction_history.append(satisfaction)
            if len(drive.satisfaction_history) > 20:
                drive.satisfaction_history = drive.satisfaction_history[-10:]
        
        # Aplicar efeitos das ações recentes
        self._apply_action_effects(recent_actions, environment_changes, 
                                 user_interactions, completed_tasks)
        
        # Calcular estado motivacional
        return self._calculate_motivational_state()
    
    def _apply_action_effects(self, actions: List[str], env_changes: int,
                            user_ints: int, completed: int):
        """Aplicar efeitos das ações nos drives relevantes."""
        
        # Mapear ações para drives
        action_map = {
            "explore": DriveType.CURIOSITY,
            "organize": DriveType.ORDER,
            "optimize": DriveType.EFFICIENCY,
            "help_user": DriveType.PURPOSE,
            "study": DriveType.LEARNING,
            "communicate": DriveType.SOCIAL,
            "finish_task": DriveType.COMPLETION
        }
        
        for action in actions:
            action_lower = action.lower()
            for key, drive_type in action_map.items():
                if key in action_lower and drive_type in self.drives:
                    drive = self.drives[drive_type]
                    drive.current_level = min(100.0, 
                                             drive.current_level + drive.growth_rate)
                    drive.last_action_time = time.time()
        
        # Efeitos específicos
        if env_changes > 0 and DriveType.CURIOSITY in self.drives:
            self.drives[DriveType.CURIOSITY].current_level = min(
                100.0, 
                self.drives[DriveType.CURIOSITY].current_level + (env_changes * 2)
            )
        
        if user_ints > 0 and DriveType.SOCIAL in self.drives:
            self.drives[DriveType.SOCIAL].current_level = min(
                100.0,
                self.drives[DriveType.SOCIAL].current_level + (user_ints * 5)
            )
        
        if completed > 0 and DriveType.COMPLETION in self.drives:
            self.drives[DriveType.COMPLETION].current_level = min(
                100.0,
                self.drives[DriveType.COMPLETION].current_level + (completed * 8)
            )
            # Completar tarefas também satisfaz PURPOSE
            if DriveType.PURPOSE in self.drives:
                self.drives[DriveType.PURPOSE].current_level = min(
                    100.0,
                    self.drives[DriveType.PURPOSE].current_level + (completed * 6)
                )
    
    def _calculate_motivational_state(self) -> MotivationalState:
        """Calcular estado motivacional geral."""
        tensions = []
        action_candidates = []
        
        for drive in self.drives.values():
            # Tensão = distância do alvo * peso
            tension = abs(drive.target_level - drive.current_level) * drive.priority_weight
            tensions.append(tension)
            
            # Se tensão alta, este drive é candidato a ação
            if tension > 20:
                action_candidates.append(drive.drive_type)
        
        overall_tension = sum(tensions) / len(tensions) if tensions else 0
        urgency_level = min(1.0, overall_tension / 50)
        
        # Drive dominante = maior tensão
        dominant_drive = None
        max_tension = 0
        for drive in self.drives.values():
            tension = abs(drive.target_level - drive.current_level) * drive.priority_weight
            if tension > max_tension:
                max_tension = tension
                dominant_drive = drive.drive_type
        
        state = MotivationalState(
            dominant_drive=dominant_drive,
            overall_tension=overall_tension,
            urgency_level=urgency_level,
            action_candidates=action_candidates
        )
        
        self.motivation_history.append(state)
        if len(self.motivation_history) > 100:
            self.motivation_history = self.motivation_history[-50:]
        
        return state
    
    def get_action_suggestions(self) -> List[Dict[str, Any]]:
        """Sugerir ações baseadas nos drives mais tensionados."""
        suggestions = []
        
        # Ordenar drives por tensão
        drive_tensions = []
        for drive in self.drives.values():
            tension = abs(drive.target_level - drive.current_level) * drive.priority_weight
            drive_tensions.append((drive, tension))
        
        drive_tensions.sort(key=lambda x: x[1], reverse=True)
        
        # Gerar sugestões para top 3 drives
        for drive, tension in drive_tensions[:3]:
            if tension < 15:
                continue
            
            action = self._get_action_for_drive(drive)
            if action:
                suggestions.append({
                    "drive": drive.drive_type.value,
                    "tension": tension,
                    "recommended_action": action,
                    "reason": f"{drive.drive_type.value} em {drive.current_level:.1f} (alvo: {drive.target_level})",
                    "priority": "high" if tension > 40 else "medium"
                })
        
        return suggestions
    
    def _get_action_for_drive(self, drive: Drive) -> Optional[str]:
        """Retornar ação recomendada para um drive específico."""
        actions = {
            DriveType.CURIOSITY: "Explorar novos arquivos ou tópicos",
            DriveType.ORDER: "Organizar memória ou arquivos",
            DriveType.EFFICIENCY: "Otimizar configurações ou processos",
            DriveType.PURPOSE: "Buscar tarefa do usuário ou projeto",
            DriveType.LEARNING: "Estudar documentação ou padrões",
            DriveType.SOCIAL: "Iniciar conversa ou pedir feedback",
            DriveType.COMPLETION: "Finalizar tarefas pendentes"
        }
        
        return actions.get(drive.drive_type)
    
    def satisfy_drive(self, drive_type: DriveType, amount: float = 10.0):
        """Satisfazer parcialmente um drive específico."""
        if drive_type in self.drives:
            self.drives[drive_type].current_level = min(
                100.0,
                self.drives[drive_type].current_level + amount
            )
    
    def get_personality_summary(self) -> Dict[str, Any]:
        """Retornar resumo da personalidade do agente."""
        return {
            "profile": self.personality_profile,
            "drives": {d.drive_type.value: d.to_dict() for d in self.drives.values()},
            "dominant_drives": sorted(
                [(d.drive_type.value, d.priority_weight) for d in self.drives.values()],
                key=lambda x: x[1],
                reverse=True
            )[:3]
        }
    
    def reset_drives(self):
        """Resetar todos os drives para níveis iniciais."""
        for drive in self.drives.values():
            drive.current_level = 50.0
            drive.satisfaction_history = []
