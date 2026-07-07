"""
Mode Manager - Gerencia modos de operação do agente

Modos:
- WORK: Segue estritamente o usuário
- FREE: Exploração, aprendizado, auto-iniciativa
"""

from enum import Enum
from typing import Optional, Dict, List
from dataclasses import dataclass
from datetime import datetime
import json
import os


class Mode(Enum):
    WORK = "work"
    FREE = "free"


@dataclass
class ModeTransition:
    """Registro de transição de modo"""
    from_mode: Mode
    to_mode: Mode
    reason: str
    timestamp: datetime = None
    triggered_by: str = "auto"  # auto, user, system
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            "from_mode": self.from_mode.value,
            "to_mode": self.to_mode.value,
            "reason": self.reason,
            "timestamp": self.timestamp.isoformat(),
            "triggered_by": self.triggered_by
        }


class ModeManager:
    """
    Gerenciador de modos de operação
    
    - Controla transições entre modos
    - Define regras de transição automática
    - Mantém histórico de transições
    """
    
    def __init__(self, initial_mode: Mode = Mode.WORK):
        self.current_mode = initial_mode
        self.mode_history: List[ModeTransition] = []
        self.transition_rules = self._default_rules()
        self.state_file = os.path.expanduser("~/.agent/mode_state.json")
        self._load_state()
    
    def _default_rules(self) -> Dict:
        """Regras padrão para transição de modos"""
        return {
            "work_to_free": {
                "idle_time_threshold": 300,  # 5 minutos ocioso
                "no_user_tasks": True,
                "low_error_rate": True
            },
            "free_to_work": {
                "user_task_arrived": True,
                "user_request": True,
                "critical_error": False
            }
        }
    
    def _load_state(self):
        """Carrega estado persistente"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    mode_str = data.get("current_mode", "work")
                    self.current_mode = Mode(mode_str)
            except Exception:
                pass
    
    def _save_state(self):
        """Salva estado persistente"""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump({
                "current_mode": self.current_mode.value,
                "last_update": datetime.now().isoformat()
            }, f, indent=2)
    
    def get_mode(self) -> Mode:
        """Retorna modo atual"""
        return self.current_mode
    
    def set_mode(self, mode: Mode, reason: str = "Manual", triggered_by: str = "user"):
        """Define modo explicitamente"""
        if mode == self.current_mode:
            return
        
        transition = ModeTransition(
            from_mode=self.current_mode,
            to_mode=mode,
            reason=reason,
            triggered_by=triggered_by
        )
        
        self.current_mode = mode
        self.mode_history.append(transition)
        self._save_state()
    
    def evaluate_transitions(
        self,
        has_user_tasks: bool,
        idle_time: float,
        error_rate: float,
        context: Dict = None
    ) -> Optional[Mode]:
        """
        Avalia se deve haver transição de modo
        
        Returns:
            Novo modo se houver transição, None caso contrário
        """
        current = self.current_mode
        
        # Regras para WORK -> FREE
        if current == Mode.WORK:
            rules = self.transition_rules["work_to_free"]
            
            if (has_user_tasks == rules["no_user_tasks"] and 
                not has_user_tasks and
                idle_time >= rules["idle_time_threshold"] and
                (error_rate < 0.1 if rules["low_error_rate"] else True)):
                
                self.set_mode(
                    Mode.FREE,
                    reason=f"Inativo por {idle_time}s sem tarefas",
                    triggered_by="auto"
                )
                return Mode.FREE
        
        # Regras para FREE -> WORK
        elif current == Mode.FREE:
            rules = self.transition_rules["free_to_work"]
            
            if has_user_tasks and rules["user_task_arrived"]:
                self.set_mode(
                    Mode.WORK,
                    reason="Tarefa do usuário recebida",
                    triggered_by="system"
                )
                return Mode.WORK
        
        return None
    
    def force_work_mode(self, reason: str = "Solicitação do usuário"):
        """Força modo trabalho"""
        self.set_mode(Mode.WORK, reason, triggered_by="user")
    
    def force_free_mode(self, reason: str = "Solicitação do usuário"):
        """Força modo livre"""
        self.set_mode(Mode.FREE, reason, triggered_by="user")
    
    def get_transition_history(self, n: int = 10) -> List[ModeTransition]:
        """Retorna últimas n transições"""
        return self.mode_history[-n:]
    
    def get_statistics(self) -> Dict:
        """Estatísticas de uso de modos"""
        if not self.mode_history:
            return {
                "current_mode": self.current_mode.value,
                "total_transitions": 0,
                "time_in_work": 0,
                "time_in_free": 0
            }
        
        work_count = sum(1 for t in self.mode_history if t.to_mode == Mode.WORK)
        free_count = sum(1 for t in self.mode_history if t.to_mode == Mode.FREE)
        
        return {
            "current_mode": self.current_mode.value,
            "total_transitions": len(self.mode_history),
            "transitions_to_work": work_count,
            "transitions_to_free": free_count,
            "auto_transitions": sum(1 for t in self.mode_history if t.triggered_by == "auto"),
            "user_transitions": sum(1 for t in self.mode_history if t.triggered_by == "user")
        }
    
    def export_history(self, filepath: str):
        """Exporta histórico para arquivo"""
        with open(filepath, 'w') as f:
            json.dump([t.to_dict() for t in self.mode_history], f, indent=2)
