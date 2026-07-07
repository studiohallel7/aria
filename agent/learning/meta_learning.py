"""
Meta-Learning - Aprender a aprender
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import numpy as np


class LearningPattern(Enum):
    SPACED_REPETITION = "spaced_repetition"
    MASS_PRACTICE = "mass_practice"
    INTERLEAVED = "interleaved"
    DEEP_DIVE = "deep_dive"
    BROAD_EXPLORATION = "broad_exploration"


@dataclass
class PerformanceRecord:
    task_id: str
    task_type: str
    start_time: datetime
    end_time: datetime
    success: bool
    score: float
    difficulty: float
    strategy_used: str
    context: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration_minutes(self) -> float:
        return (self.end_time - self.start_time).total_seconds() / 60.0
    
    def to_dict(self) -> Dict:
        return {
            'task_id': self.task_id,
            'task_type': self.task_type,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'duration_minutes': self.duration_minutes,
            'success': self.success,
            'score': self.score,
            'difficulty': self.difficulty,
            'strategy_used': self.strategy_used,
            'context': self.context
        }


@dataclass
class AdaptationPlan:
    current_strategy: str
    recommended_strategy: str
    confidence: float
    reasoning: str
    expected_improvement: float
    actions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'current_strategy': self.current_strategy,
            'recommended_strategy': self.recommended_strategy,
            'confidence': self.confidence,
            'reasoning': self.reasoning,
            'expected_improvement': self.expected_improvement,
            'actions': self.actions
        }


class PerformanceAnalyzer:
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.records: List[PerformanceRecord] = []
        self.strategy_stats: Dict[str, Dict] = {}
    
    def add_record(self, record: PerformanceRecord):
        self.records.append(record)
        if len(self.records) > self.window_size:
            self.records.pop(0)
        
        strategy = record.strategy_used
        if strategy not in self.strategy_stats:
            self.strategy_stats[strategy] = {
                'count': 0, 'successes': 0,
                'total_score': 0.0, 'avg_duration': 0.0
            }
        
        stats = self.strategy_stats[strategy]
        old_avg = stats['avg_duration']
        stats['count'] += 1
        stats['successes'] += 1 if record.success else 0
        stats['total_score'] += record.score
        stats['avg_duration'] = ((old_avg * (stats['count'] - 1) + record.duration_minutes) / stats['count'])
    
    def get_strategy_effectiveness(self) -> Dict[str, float]:
        effectiveness = {}
        for strategy, stats in self.strategy_stats.items():
            if stats['count'] > 0:
                success_rate = stats['successes'] / stats['count']
                avg_score = stats['total_score'] / stats['count']
                effectiveness[strategy] = (success_rate + avg_score) / 2
        return effectiveness
    
    def identify_best_strategy(self, task_type: Optional[str] = None) -> Optional[str]:
        if task_type:
            filtered = [r for r in self.records if r.task_type == task_type]
            if not filtered:
                return None
            by_strategy: Dict[str, List[PerformanceRecord]] = {}
            for record in filtered:
                if record.strategy_used not in by_strategy:
                    by_strategy[record.strategy_used] = []
                by_strategy[record.strategy_used].append(record)
            
            best_strategy, best_score = None, -1
            for strategy, records in by_strategy.items():
                avg_score = sum(r.score for r in records) / len(records)
                if avg_score > best_score:
                    best_score = avg_score
                    best_strategy = strategy
            return best_strategy
        
        effectiveness = self.get_strategy_effectiveness()
        if not effectiveness:
            return None
        return max(effectiveness.items(), key=lambda x: x[1])[0]
    
    def statistics(self) -> Dict:
        if not self.records:
            return {'count': 0}
        return {
            'total_records': len(self.records),
            'overall_success_rate': sum(1 for r in self.records if r.success) / len(self.records),
            'average_score': float(np.mean([r.score for r in self.records])),
            'best_strategy': self.identify_best_strategy()
        }


class MetaLearner:
    def __init__(self):
        self.analyzer = PerformanceAnalyzer()
        self.context_strategies: Dict[str, Dict[str, float]] = {}
        self.adaptation_history: List[AdaptationPlan] = []
        self.meta_knowledge: Dict[str, Any] = {}
    
    def record_performance(self, task_id: str, task_type: str, success: bool, 
                          score: float, difficulty: float, strategy: str, 
                          duration_minutes: float, context: Optional[Dict] = None):
        record = PerformanceRecord(
            task_id=task_id, task_type=task_type,
            start_time=datetime.now() - timedelta(minutes=duration_minutes),
            end_time=datetime.now(), success=success, score=score,
            difficulty=difficulty, strategy_used=strategy, context=context or {}
        )
        self.analyzer.add_record(record)
        self._update_context_knowledge(task_type, strategy, score)
    
    def _update_context_knowledge(self, task_type: str, strategy: str, score: float):
        if task_type not in self.context_strategies:
            self.context_strategies[task_type] = {}
        if strategy not in self.context_strategies[task_type]:
            self.context_strategies[task_type][strategy] = 0.0
        old = self.context_strategies[task_type][strategy]
        self.context_strategies[task_type][strategy] = old * 0.9 + score * 0.1
    
    def create_adaptation_plan(self, current_strategy: str, 
                               task_type: Optional[str] = None) -> Optional[AdaptationPlan]:
        effectiveness = self.analyzer.get_strategy_effectiveness()
        current_score = effectiveness.get(current_strategy, 0.5)
        best_strategy = self.analyzer.identify_best_strategy(task_type)
        
        if not best_strategy or best_strategy == current_strategy:
            return None
        
        best_score = effectiveness.get(best_strategy, 0.5)
        improvement = best_score - current_score
        if improvement < 0.1:
            return None
        
        plan = AdaptationPlan(
            current_strategy=current_strategy,
            recommended_strategy=best_strategy,
            confidence=min(1.0, improvement + 0.5),
            reasoning=f"Estratégia '{best_strategy}' tem {(improvement*100):.1f}% mais efetividade",
            expected_improvement=improvement,
            actions=[f"Migrar para {best_strategy}", "Monitorar resultados"]
        )
        self.adaptation_history.append(plan)
        return plan
    
    def get_meta_insights(self) -> List[str]:
        insights = []
        trend = self.analyzer.performance_trend() if hasattr(self.analyzer, 'performance_trend') else 0
        if trend > 0.05:
            insights.append("Desempenho em melhoria")
        elif trend < -0.05:
            insights.append("Desempenho em declínio")
        
        best = self.analyzer.identify_best_strategy()
        if best:
            insights.append(f"Melhor estratégia: {best}")
        return insights
    
    def export_meta_knowledge(self, filepath: str):
        data = {
            'context_strategies': self.context_strategies,
            'adaptation_history': [p.to_dict() for p in self.adaptation_history],
            'meta_knowledge': self.meta_knowledge,
            'analyzer_stats': self.analyzer.statistics()
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def import_meta_knowledge(self, filepath: str):
        with open(filepath, 'r') as f:
            data = json.load(f)
        self.context_strategies = data.get('context_strategies', {})
        self.meta_knowledge = data.get('meta_knowledge', {})
        self.adaptation_history = [
            AdaptationPlan(**p) for p in data.get('adaptation_history', [])
        ]
