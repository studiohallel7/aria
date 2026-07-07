"""
Triggers System - Sistema de gatilhos do loop do agente

Gatilhos que iniciam/executam ciclos:
- Tempo (intervalo)
- Evento externo
- Mudança de estado interno
- Atualização de memória
- Threshold de consumo
- Conclusão de tarefa
- Falhas/erros
- Alterações em arquivos monitorados
- Curiosidade (contexto + aleatoriedade)
"""

from enum import Enum
from typing import List, Dict, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import os
import hashlib


class TriggerType(Enum):
    TIMER = "timer"
    EVENT = "event"
    STATE_CHANGE = "state_change"
    MEMORY_UPDATE = "memory_update"
    THRESHOLD = "threshold"
    TASK_COMPLETE = "task_complete"
    ERROR = "error"
    FILE_CHANGE = "file_change"
    CURIOSITY = "curiosity"


@dataclass
class Trigger:
    """Definição de um gatilho"""
    id: str
    trigger_type: TriggerType
    description: str
    enabled: bool = True
    priority: int = 5  # 1-10
    metadata: Dict = field(default_factory=dict)
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "trigger_type": self.trigger_type.value,
            "description": self.description,
            "enabled": self.enabled,
            "priority": self.priority,
            "metadata": self.metadata,
            "last_triggered": self.last_triggered.isoformat() if self.last_triggered else None,
            "trigger_count": self.trigger_count
        }


@dataclass
class TimerTrigger(Trigger):
    """Gatilho baseado em tempo"""
    interval_seconds: int = 60
    next_fire: Optional[datetime] = None
    
    def __post_init__(self):
        if self.next_fire is None:
            self.next_fire = datetime.now() + timedelta(seconds=self.interval_seconds)
    
    def should_fire(self) -> bool:
        return self.enabled and datetime.now() >= self.next_fire
    
    def fire(self):
        self.last_triggered = datetime.now()
        self.trigger_count += 1
        self.next_fire = datetime.now() + timedelta(seconds=self.interval_seconds)


@dataclass
class FileChangeTrigger(Trigger):
    """Gatilho baseado em mudança em arquivo"""
    filepath: str = ""
    last_hash: Optional[str] = None
    
    def _get_file_hash(self) -> Optional[str]:
        if not os.path.exists(self.filepath):
            return None
        
        with open(self.filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def should_fire(self) -> bool:
        if not self.enabled:
            return False
        
        current_hash = self._get_file_hash()
        
        if current_hash is None:
            return False
        
        if self.last_hash is None:
            self.last_hash = current_hash
            return False
        
        if current_hash != self.last_hash:
            self.last_hash = current_hash
            return True
        
        return False
    
    def fire(self):
        self.last_triggered = datetime.now()
        self.trigger_count += 1


@dataclass
class ThresholdTrigger(Trigger):
    """Gatilho baseado em threshold (ex: consumo de API)"""
    metric_name: str = ""
    threshold_value: float = 0.0
    comparison: str = "gte"  # gte, lte, eq
    
    def check(self, current_value: float) -> bool:
        if not self.enabled:
            return False
        
        if self.comparison == "gte":
            return current_value >= self.threshold_value
        elif self.comparison == "lte":
            return current_value <= self.threshold_value
        elif self.comparison == "eq":
            return abs(current_value - self.threshold_value) < 0.01
        
        return False
    
    def fire(self):
        self.last_triggered = datetime.now()
        self.trigger_count += 1


@dataclass
class EventTrigger(Trigger):
    """Gatilho baseado em evento externo"""
    event_name: str = ""
    callback: Optional[Callable] = None
    pending: bool = False
    
    def signal(self):
        """Sinaliza que o evento ocorreu"""
        self.pending = True
    
    def should_fire(self) -> bool:
        return self.enabled and self.pending
    
    def fire(self):
        self.last_triggered = datetime.now()
        self.trigger_count += 1
        self.pending = False
        
        if self.callback:
            try:
                self.callback()
            except Exception:
                pass


class TriggerManager:
    """
    Gerenciador de gatilhos do loop
    
    - Registra diferentes tipos de gatilhos
    - Avalia quais gatilhos estão ativos
    - Dispara ciclos baseados em gatilhos
    """
    
    def __init__(self):
        self.triggers: Dict[str, Trigger] = {}
        self._setup_default_triggers()
    
    def _setup_default_triggers(self):
        """Configura gatilhos padrão"""
        # Timer base (30 segundos)
        self.add_trigger(TimerTrigger(
            id="timer_base",
            trigger_type=TriggerType.TIMER,
            description="Timer base do loop",
            interval_seconds=30,
            priority=5
        ))
        
        # Erros críticos
        self.add_trigger(ThresholdTrigger(
            id="error_critical",
            trigger_type=TriggerType.ERROR,
            description="Múltiplos erros consecutivos",
            metric_name="consecutive_errors",
            threshold_value=3.0,
            comparison="gte",
            priority=9
        ))
        
        # curiosity trigger (será avaliado periodicamente)
        self.add_trigger(TimerTrigger(
            id="curiosity_check",
            trigger_type=TriggerType.CURIOSITY,
            description="Check de curiosidade",
            interval_seconds=120,
            priority=3
        ))
    
    def add_trigger(self, trigger: Trigger):
        """Adiciona gatilho"""
        self.triggers[trigger.id] = trigger
    
    def remove_trigger(self, trigger_id: str):
        """Remove gatilho"""
        if trigger_id in self.triggers:
            del self.triggers[trigger_id]
    
    def enable_trigger(self, trigger_id: str):
        """Habilita gatilho"""
        if trigger_id in self.triggers:
            self.triggers[trigger_id].enabled = True
    
    def disable_trigger(self, trigger_id: str):
        """Desabilita gatilho"""
        if trigger_id in self.triggers:
            self.triggers[trigger_id].enabled = False
    
    def get_active_triggers(self) -> List[Trigger]:
        """Retorna gatilhos que devem disparar agora"""
        active = []
        
        for trigger in self.triggers.values():
            if not trigger.enabled:
                continue
            
            should_fire = False
            
            if isinstance(trigger, TimerTrigger):
                should_fire = trigger.should_fire()
            elif isinstance(trigger, FileChangeTrigger):
                should_fire = trigger.should_fire()
            elif isinstance(trigger, EventTrigger):
                should_fire = trigger.should_fire()
            else:
                # Gatilhos genéricos são avaliados externamente
                continue
            
            if should_fire:
                active.append(trigger)
        
        # Ordena por prioridade
        active.sort(key=lambda t: -t.priority)
        return active
    
    def fire_trigger(self, trigger_id: str):
        """Dispara gatilho específico"""
        if trigger_id in self.triggers:
            self.triggers[trigger_id].fire()
    
    def signal_event(self, event_name: str):
        """Sinaliza ocorrência de evento"""
        for trigger in self.triggers.values():
            if isinstance(trigger, EventTrigger) and trigger.event_name == event_name:
                trigger.signal()
    
    def check_threshold(self, metric_name: str, value: float) -> List[str]:
        """Verifica thresholds e retorna gatilhos disparados"""
        fired = []
        
        for trigger in self.triggers.values():
            if isinstance(trigger, ThresholdTrigger) and trigger.metric_name == metric_name:
                if trigger.check(value):
                    trigger.fire()
                    fired.append(trigger.id)
        
        return fired
    
    def get_statistics(self) -> Dict:
        """Estatísticas dos gatilhos"""
        total = len(self.triggers)
        enabled = sum(1 for t in self.triggers.values() if t.enabled)
        total_fires = sum(t.trigger_count for t in self.triggers.values())
        
        by_type = {}
        for t in self.triggers.values():
            ttype = t.trigger_type.value
            by_type[ttype] = by_type.get(ttype, 0) + 1
        
        return {
            "total_triggers": total,
            "enabled_triggers": enabled,
            "disabled_triggers": total - enabled,
            "total_fires": total_fires,
            "by_type": by_type
        }
    
    def export_triggers(self, filepath: str):
        """Exporta configuração de gatilhos"""
        import json
        with open(filepath, 'w') as f:
            json.dump([t.to_dict() for t in self.triggers.values()], f, indent=2)
