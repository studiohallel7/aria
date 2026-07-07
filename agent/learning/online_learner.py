"""
Online Learning System - Aprendizado contínuo baseado em experiência

Implementa:
- Buffer de experiências (estado, ação, recompensa, próximo_estado)
- Estratégias de aprendizado (supervisionado, reforço, por demonstração)
- Atualização incremental de modelos e prompts
- Transfer learning entre tarefas relacionadas
"""

import json
import hashlib
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import deque
import random


class LearningStrategy(Enum):
    """Estratégias de aprendizado suportadas"""
    SUPERVISED = "supervised"  # Aprendizado com exemplos rotulados
    REINFORCEMENT = "reinforcement"  # Aprendizado por recompensa/punição
    DEMONSTRATION = "demonstration"  # Learning from demonstration (LfD)
    SELF_SUPERVISED = "self_supervised"  # Auto-geração de labels
    TRANSFER = "transfer"  # Transferência entre domínios
    META = "meta"  # Meta-learning (aprender a aprender)


@dataclass
class Experience:
    """Uma experiência de aprendizado única"""
    state: Dict[str, Any]  # Estado/contexto inicial
    action: str  # Ação tomada (prompt, decisão, etc.)
    reward: float  # Recompensa recebida (-1.0 a 1.0)
    next_state: Dict[str, Any]  # Estado após ação
    timestamp: datetime = field(default_factory=datetime.now)
    strategy: LearningStrategy = LearningStrategy.REINFORCEMENT
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'state': self.state,
            'action': self.action,
            'reward': self.reward,
            'next_state': self.next_state,
            'timestamp': self.timestamp.isoformat(),
            'strategy': self.strategy.value,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Experience':
        return cls(
            state=data['state'],
            action=data['action'],
            reward=data['reward'],
            next_state=data['next_state'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            strategy=LearningStrategy(data['strategy']),
            metadata=data.get('metadata', {})
        )
    
    def hash(self) -> str:
        """Hash único para deduplicação"""
        content = json.dumps({
            'state': self.state,
            'action': self.action,
            'reward': self.reward
        }, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]


class ExperienceBuffer:
    """
    Buffer de experiências com amostragem prioritária
    
    Armazena experiências e permite:
    - Amostragem baseada em importância (TD-error)
    - Decay temporal (experiências antigas perdem peso)
    - Deduplicação automática
    - Persistência em disco
    """
    
    def __init__(
        self, 
        capacity: int = 10000,
        priority_alpha: float = 0.6,  # Quanto prioridade importa
        beta_start: float = 0.4,  # Importância sampling initial
        beta_frames: int = 100000  # Frames para beta chegar a 1
    ):
        self.capacity = capacity
        self.priority_alpha = priority_alpha
        self.beta_start = beta_start
        self.beta_frames = beta_frames
        self.frame = 0
        
        self.buffer: deque = deque(maxlen=capacity)
        self.priorities: deque = deque(maxlen=capacity)
        self.hash_set: set = set()  # Para deduplicação
        
        # Estatísticas
        self.total_experiences = 0
        self.positive_rewards = 0
        self.negative_rewards = 0
    
    def add(self, experience: Experience, priority: float = 1.0):
        """Adiciona experiência ao buffer"""
        exp_hash = experience.hash()
        
        # Evitar duplicatas
        if exp_hash in self.hash_set:
            return False
        
        # Remover hash antigo se buffer cheio
        if len(self.buffer) >= self.capacity:
            old_exp = self.buffer[0]
            old_hash = old_exp.hash()
            self.hash_set.discard(old_hash)
        
        # Adicionar nova experiência
        self.buffer.append(experience)
        self.priorities.append(priority ** self.priority_alpha)
        self.hash_set.add(exp_hash)
        self.total_experiences += 1
        
        # Atualizar estatísticas
        if experience.reward > 0:
            self.positive_rewards += 1
        elif experience.reward < 0:
            self.negative_rewards += 1
        
        return True
    
    def sample(self, batch_size: int) -> Tuple[List[Experience], List[float], List[int]]:
        """
        Amostra batch com prioridade
        
        Returns:
            - Lista de experiências
            - Pesos de importância (para corrigir bias)
            - Índices (para atualizar prioridades)
        """
        if len(self.buffer) == 0:
            return [], [], []
        
        self.frame = min(self.frame + batch_size, self.beta_frames)
        beta = self.beta_start * (self.frame / self.beta_frames)
        
        # Calcular probabilidades
        priorities = np.array(self.priorities)
        probabilities = priorities / priorities.sum()
        
        # Amostrar
        indices = np.random.choice(
            len(self.buffer), 
            size=min(batch_size, len(self.buffer)), 
            replace=False,
            p=probabilities
        )
        
        experiences = [self.buffer[i] for i in indices]
        
        # Calcular pesos de importância
        weights = (len(self.buffer) * probabilities[indices]) ** (-beta)
        weights /= weights.max()  # Normalizar
        
        return experiences, weights.tolist(), indices.tolist()
    
    def update_priorities(self, indices: List[int], priorities: List[float]):
        """Atualiza prioridades após aprendizado"""
        for idx, prio in zip(indices, priorities):
            if 0 <= idx < len(self.priorities):
                self.priorities[idx] = prio ** self.priority_alpha
    
    def get_recent(self, n: int = 10) -> List[Experience]:
        """Retorna experiências mais recentes"""
        return list(self.buffer)[-n:]
    
    def get_by_reward_range(
        self, 
        min_reward: float, 
        max_reward: float
    ) -> List[Experience]:
        """Filtra experiências por faixa de recompensa"""
        return [
            exp for exp in self.buffer 
            if min_reward <= exp.reward <= max_reward
        ]
    
    def save(self, filepath: str):
        """Persiste buffer em disco"""
        data = {
            'experiences': [exp.to_dict() for exp in self.buffer],
            'priorities': list(self.priorities),
            'stats': {
                'total': self.total_experiences,
                'positive': self.positive_rewards,
                'negative': self.negative_rewards
            }
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load(self, filepath: str):
        """Carrega buffer do disco"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.buffer.clear()
        self.priorities.clear()
        self.hash_set.clear()
        
        for exp_dict in data['experiences']:
            exp = Experience.from_dict(exp_dict)
            self.buffer.append(exp)
            self.hash_set.add(exp.hash())
        
        self.priorities = deque(data['priorities'], maxlen=self.capacity)
        
        if 'stats' in data:
            self.total_experiences = data['stats'].get('total', 0)
            self.positive_rewards = data['stats'].get('positive', 0)
            self.negative_rewards = data['stats'].get('negative', 0)
    
    def statistics(self) -> Dict:
        """Estatísticas do buffer"""
        if not self.buffer:
            return {'empty': True}
        
        rewards = [exp.reward for exp in self.buffer]
        return {
            'size': len(self.buffer),
            'capacity': self.capacity,
            'total_experiences': self.total_experiences,
            'unique_hashes': len(self.hash_set),
            'avg_reward': np.mean(rewards),
            'std_reward': np.std(rewards),
            'min_reward': min(rewards),
            'max_reward': max(rewards),
            'positive_ratio': self.positive_rewards / max(1, self.total_experiences),
            'negative_ratio': self.negative_rewards / max(1, self.total_experiences),
            'strategies': self._count_strategies()
        }
    
    def _count_strategies(self) -> Dict[str, int]:
        counts = {}
        for exp in self.buffer:
            key = exp.strategy.value
            counts[key] = counts.get(key, 0) + 1
        return counts


class OnlineLearner:
    """
    Sistema de aprendizado online contínuo
    
    Integra:
    - Múltiplas estratégias de aprendizado
    - Buffer de experiências prioritário
    - Atualização incremental de políticas/prompts
    - Avaliação de desempenho em tempo real
    """
    
    def __init__(
        self,
        buffer_capacity: int = 5000,
        learning_rate: float = 0.01,
        discount_factor: float = 0.99,
        exploration_rate: float = 0.1,
        target_update_interval: int = 100
    ):
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.target_update_interval = target_update_interval
        
        self.buffer = ExperienceBuffer(capacity=buffer_capacity)
        
        # Políticas por estratégia
        self.policies: Dict[LearningStrategy, Callable] = {}
        
        # Histórico de aprendizado
        self.learning_history: List[Dict] = []
        self.performance_window: deque = deque(maxlen=100)
        
        # Callbacks
        self.on_learn_callback: Optional[Callable] = None
        self.on_evaluate_callback: Optional[Callable] = None
    
    def register_policy(
        self, 
        strategy: LearningStrategy, 
        policy_fn: Callable
    ):
        """Registra função de política para uma estratégia"""
        self.policies[strategy] = policy_fn
    
    def observe(
        self,
        state: Dict,
        action: str,
        reward: float,
        next_state: Dict,
        strategy: LearningStrategy = LearningStrategy.REINFORCEMENT,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Observa nova experiência e adiciona ao buffer
        
        Returns True se experiência foi adicionada (não duplicada)
        """
        experience = Experience(
            state=state,
            action=action,
            reward=reward,
            next_state=next_state,
            strategy=strategy,
            metadata=metadata or {}
        )
        
        # Calcular prioridade inicial baseada na magnitude da recompensa
        priority = abs(reward) + 0.1  # Evitar prioridade zero
        
        added = self.buffer.add(experience, priority)
        
        if added and self.on_learn_callback:
            self.on_learn_callback(experience)
        
        return added
    
    def learn(self, batch_size: int = 32) -> Dict[str, float]:
        """
        Executa um passo de aprendizado
        
        Returns:
            Métricas de aprendizado (loss, accuracy, etc.)
        """
        if len(self.buffer) < batch_size:
            return {'status': 'insufficient_data'}
        
        # Amostrar batch prioritário
        experiences, weights, indices = self.buffer.sample(batch_size)
        
        if not experiences:
            return {'status': 'sampling_failed'}
        
        # Agrupar por estratégia
        by_strategy: Dict[LearningStrategy, List[Experience]] = {}
        for exp in experiences:
            if exp.strategy not in by_strategy:
                by_strategy[exp.strategy] = []
            by_strategy[exp.strategy].append(exp)
        
        metrics = {}
        
        # Aprender por estratégia
        for strategy, exps in by_strategy.items():
            if strategy in self.policies:
                policy_metrics = self._learn_strategy(
                    strategy, 
                    exps, 
                    weights[:len(exps)]
                )
                metrics[strategy.value] = policy_metrics
        
        # Atualizar prioridades (se tiver TD-errors)
        if 'td_errors' in metrics:
            new_priorities = [abs(e) + 0.1 for e in metrics['td_errors']]
            self.buffer.update_priorities(indices, new_priorities)
        
        # Registrar histórico
        self.learning_history.append({
            'timestamp': datetime.now().isoformat(),
            'batch_size': batch_size,
            'metrics': metrics,
            'buffer_stats': self.buffer.statistics()
        })
        
        # Atualizar janela de performance
        avg_reward = np.mean([exp.reward for exp in experiences])
        self.performance_window.append(avg_reward)
        
        return metrics
    
    def _learn_strategy(
        self,
        strategy: LearningStrategy,
        experiences: List[Experience],
        weights: List[float]
    ) -> Dict[str, float]:
        """Executa aprendizado para estratégia específica"""
        policy_fn = self.policies.get(strategy)
        
        if not policy_fn:
            return {'error': 'policy_not_registered'}
        
        # Chamar política com experiências
        try:
            result = policy_fn(experiences, weights, {
                'learning_rate': self.learning_rate,
                'discount_factor': self.discount_factor
            })
            
            # Extrair TD errors se disponível
            if isinstance(result, dict) and 'td_errors' in result:
                return result
            
            return {'success': True}
            
        except Exception as e:
            return {'error': str(e)}
    
    def evaluate(self) -> Dict:
        """Avalia desempenho atual do agente"""
        if self.on_evaluate_callback:
            return self.on_evaluate_callback()
        
        # Avaliação padrão baseada no buffer
        stats = self.buffer.statistics()
        
        if self.performance_window:
            recent_performance = np.mean(self.performance_window)
            performance_trend = np.polyfit(
                range(len(self.performance_window)),
                list(self.performance_window),
                1
            )[0] if len(self.performance_window) > 1 else 0
        else:
            recent_performance = 0
            performance_trend = 0
        
        return {
            'buffer_stats': stats,
            'recent_performance': recent_performance,
            'performance_trend': performance_trend,
            'learning_progress': self._calculate_learning_progress(),
            'recommendations': self._generate_recommendations()
        }
    
    def _calculate_learning_progress(self) -> float:
        """Calcula progresso geral de aprendizado"""
        if len(self.learning_history) < 2:
            return 0.0
        
        # Comparar recompensas médias do início vs fim
        early_rewards = [
            h['metrics'].get('avg_reward', 0) 
            for h in self.learning_history[:10]
        ]
        recent_rewards = [
            h['metrics'].get('avg_reward', 0) 
            for h in self.learning_history[-10:]
        ]
        
        if not early_rewards or not recent_rewards:
            return 0.0
        
        early_avg = np.mean(early_rewards)
        recent_avg = np.mean(recent_rewards)
        
        # Normalizar para 0-1
        progress = (recent_avg - early_avg + 1) / 2
        return max(0, min(1, progress))
    
    def _generate_recommendations(self) -> List[str]:
        """Gera recomendações para melhorar aprendizado"""
        recommendations = []
        
        stats = self.buffer.statistics()
        
        if stats.get('avg_reward', 0) < 0:
            recommendations.append(
                "Recompensas negativas predominam. Revise função de recompensa."
            )
        
        if stats.get('positive_ratio', 0) < 0.3:
            recommendations.append(
                "Poucas experiências positivas. Considere explorar mais."
            )
        
        if len(self.buffer) < self.buffer.capacity * 0.1:
            recommendations.append(
                "Buffer pouco preenchido. Continue coletando experiências."
            )
        
        strategies = stats.get('strategies', {})
        if len(strategies) == 1:
            recommendations.append(
                "Use apenas uma estratégia. Diversifique abordagens."
            )
        
        return recommendations
    
    def export_knowledge(self, filepath: str):
        """Exporta conhecimento aprendido para arquivo"""
        knowledge = {
            'buffer': {
                'experiences': [exp.to_dict() for exp in self.buffer.buffer],
                'stats': self.buffer.statistics()
            },
            'history': self.learning_history,
            'performance': {
                'window': list(self.performance_window),
                'trend': self._calculate_learning_progress()
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(knowledge, f, indent=2)
    
    def import_knowledge(self, filepath: str):
        """Importa conhecimento de arquivo"""
        with open(filepath, 'r') as f:
            knowledge = json.load(f)
        
        # Carregar experiências
        for exp_dict in knowledge['buffer']['experiences']:
            exp = Experience.from_dict(exp_dict)
            self.buffer.add(exp)
        
        # Restaurar histórico
        self.learning_history = knowledge.get('history', [])
        
        # Restaurar performance window
        self.performance_window = deque(
            knowledge.get('performance', {}).get('window', []),
            maxlen=100
        )
    
    def reset(self, keep_buffer: bool = False):
        """Reseta estado de aprendizado"""
        if not keep_buffer:
            self.buffer = ExperienceBuffer(capacity=self.buffer.capacity)
        
        self.learning_history.clear()
        self.performance_window.clear()
