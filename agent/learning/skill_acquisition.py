"""
Skill Acquisition - Aquisição e evolução de habilidades

Implementa:
- Árvore de habilidades interconectadas
- Níveis de competência (novato -> mestre)
- Transferência entre habilidades relacionadas
- Detecção automática de novas habilidades necessárias
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum


class CompetencyLevel(Enum):
    """Níveis de competência em uma habilidade"""
    NOVICE = 1  # 0-25%
    BEGINNER = 2  # 25-50%
    INTERMEDIATE = 3  # 50-70%
    ADVANCED = 4  # 70-85%
    EXPERT = 5  # 85-95%
    MASTER = 6  # 95-100%
    
    @property
    def min_progress(self) -> float:
        return {
            CompetencyLevel.NOVICE: 0.0,
            CompetencyLevel.BEGINNER: 0.25,
            CompetencyLevel.INTERMEDIATE: 0.50,
            CompetencyLevel.ADVANCED: 0.70,
            CompetencyLevel.EXPERT: 0.85,
            CompetencyLevel.MASTER: 0.95
        }[self]
    
    @property
    def max_progress(self) -> float:
        return {
            CompetencyLevel.NOVICE: 0.25,
            CompetencyLevel.BEGINNER: 0.50,
            CompetencyLevel.INTERMEDIATE: 0.70,
            CompetencyLevel.ADVANCED: 0.85,
            CompetencyLevel.EXPERT: 0.95,
            CompetencyLevel.MASTER: 1.0
        }[self]


@dataclass
class Skill:
    """Representa uma habilidade única"""
    id: str
    name: str
    description: str
    category: str
    prerequisites: List[str] = field(default_factory=list)
    competency_level: CompetencyLevel = CompetencyLevel.NOVICE
    progress: float = 0.0  # 0.0 a 1.0 dentro do nível atual
    times_used: int = 0
    last_used: Optional[datetime] = None
    related_skills: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'prerequisites': self.prerequisites,
            'competency_level': self.competency_level.name,
            'progress': self.progress,
            'times_used': self.times_used,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'related_skills': self.related_skills,
            'metadata': self.metadata
        }
    
    def gain_experience(self, amount: float) -> bool:
        """
        Ganha experiência na habilidade
        
        Returns True se houve level up
        """
        old_level = self.competency_level
        self.progress += amount
        self.times_used += 1
        self.last_used = datetime.now()
        
        # Verificar level up
        leveled_up = False
        while self.progress >= self.competency_level.max_progress:
            if self.competency_level == CompetencyLevel.MASTER:
                self.progress = 1.0
                break
            
            # Subir nível
            self.progress -= self.competency_level.max_progress
            level_list = list(CompetencyLevel)
            current_idx = level_list.index(self.competency_level)
            self.competency_level = level_list[current_idx + 1]
            leveled_up = True
        
        return leveled_up


class SkillTree:
    """
    Árvore de habilidades do agente
    
    Gerencia:
    - Dependências entre habilidades
    - Progressão de competência
    - Transferência de conhecimento
    - Descoberta de novas habilidades
    """
    
    def __init__(self):
        self.skills: Dict[str, Skill] = {}
        self.skill_graph: Dict[str, Set[str]] = {}  # Adjacency list
        self.acquisition_history: List[Dict] = []
    
    def add_skill(self, skill: Skill):
        """Adiciona habilidade à árvore"""
        self.skills[skill.id] = skill
        self.skill_graph[skill.id] = set(skill.related_skills)
        
        self.acquisition_history.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'add_skill',
            'skill_id': skill.id,
            'skill_name': skill.name
        })
    
    def remove_skill(self, skill_id: str):
        """Remove habilidade da árvore"""
        if skill_id in self.skills:
            del self.skills[skill_id]
        if skill_id in self.skill_graph:
            del self.skill_graph[skill_id]
        
        # Remover referências
        for related in self.skill_graph.values():
            related.discard(skill_id)
    
    def get_skill(self, skill_id: str) -> Optional[Skill]:
        """Obtém habilidade por ID"""
        return self.skills.get(skill_id)
    
    def can_learn(self, skill_id: str) -> tuple[bool, List[str]]:
        """
        Verifica se pode aprender habilidade (pré-requisitos satisfeitos)
        
        Returns:
            - Pode aprender?
            - Lista de pré-requisitos faltantes
        """
        skill = self.skills.get(skill_id)
        if not skill:
            return False, ['skill_not_found']
        
        missing = []
        for prereq_id in skill.prerequisites:
            prereq = self.skills.get(prereq_id)
            if not prereq or prereq.competency_level == CompetencyLevel.NOVICE:
                missing.append(prereq_id)
        
        return len(missing) == 0, missing
    
    def practice_skill(
        self, 
        skill_id: str, 
        experience_gain: float = 0.1
    ) -> Dict:
        """
        Pratica habilidade e ganha experiência
        
        Returns:
            Resultado da prática
        """
        skill = self.skills.get(skill_id)
        if not skill:
            return {'success': False, 'error': 'skill_not_found'}
        
        # Verificar pré-requisitos
        can_learn, missing = self.can_learn(skill_id)
        if not can_learn:
            return {
                'success': False, 
                'error': 'prerequisites_missing',
                'missing': missing
            }
        
        # Ganhar experiência
        leveled_up = skill.gain_experience(experience_gain)
        
        result = {
            'success': True,
            'skill_id': skill_id,
            'old_level': skill.competency_level.name,
            'new_level': skill.competency_level.name,
            'progress': skill.progress,
            'leveled_up': leveled_up
        }
        
        if leveled_up:
            self.acquisition_history.append({
                'timestamp': datetime.now().isoformat(),
                'action': 'level_up',
                'skill_id': skill_id,
                'new_level': skill.competency_level.name
            })
        
        return result
    
    def get_related_skills(self, skill_id: str, depth: int = 1) -> List[Skill]:
        """Obtém habilidades relacionadas"""
        if skill_id not in self.skill_graph:
            return []
        
        related_ids = self.skill_graph[skill_id]
        related = [
            self.skills[sid] 
            for sid in related_ids 
            if sid in self.skills
        ]
        
        if depth > 1:
            for related_id in list(related_ids):
                deeper = self.get_related_skills(related_id, depth - 1)
                related.extend(deeper)
        
        return related
    
    def get_skills_by_category(self, category: str) -> List[Skill]:
        """Filtra habilidades por categoria"""
        return [
            skill for skill in self.skills.values()
            if skill.category == category
        ]
    
    def get_competency_summary(self) -> Dict:
        """Resumo de competências"""
        if not self.skills:
            return {'total': 0}
        
        level_counts = {level.name: 0 for level in CompetencyLevel}
        for skill in self.skills.values():
            level_counts[skill.competency_level.name] += 1
        
        avg_progress = sum(s.progress for s in self.skills.values()) / len(self.skills)
        
        return {
            'total_skills': len(self.skills),
            'by_level': level_counts,
            'average_progress': avg_progress,
            'most_practiced': max(self.skills.values(), key=lambda s: s.times_used).name if self.skills else None,
            'categories': self._count_categories()
        }
    
    def _count_categories(self) -> Dict[str, int]:
        counts = {}
        for skill in self.skills.values():
            counts[skill.category] = counts.get(skill.category, 0) + 1
        return counts
    
    def suggest_next_skill(self) -> Optional[str]:
        """Sugere próxima habilidade para aprender"""
        # Habilidades desbloqueadas mas não praticadas
        candidates = []
        
        for skill_id, skill in self.skills.items():
            if skill.competency_level == CompetencyLevel.NOVICE and skill.times_used == 0:
                can_learn, _ = self.can_learn(skill_id)
                if can_learn:
                    # Priorizar baseado em habilidades relacionadas já aprendidas
                    related_learned = sum(
                        1 for rel_id in skill.related_skills
                        if rel_id in self.skills and 
                        self.skills[rel_id].competency_level != CompetencyLevel.NOVICE
                    )
                    candidates.append((skill_id, related_learned))
        
        if not candidates:
            return None
        
        # Retornar candidata com mais relacionados aprendidos
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]
    
    def export_tree(self, filepath: str):
        """Exporta árvore de habilidades"""
        data = {
            'skills': [s.to_dict() for s in self.skills.values()],
            'graph': {k: list(v) for k, v in self.skill_graph.items()},
            'history': self.acquisition_history
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def import_tree(self, filepath: str):
        """Importa árvore de habilidades"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.skills.clear()
        self.skill_graph.clear()
        
        for skill_dict in data['skills']:
            skill = Skill(
                id=skill_dict['id'],
                name=skill_dict['name'],
                description=skill_dict['description'],
                category=skill_dict['category'],
                prerequisites=skill_dict['prerequisites'],
                competency_level=CompetencyLevel[skill_dict['competency_level']],
                progress=skill_dict['progress'],
                times_used=skill_dict['times_used'],
                related_skills=skill_dict['related_skills'],
                metadata=skill_dict.get('metadata', {})
            )
            if skill_dict.get('last_used'):
                skill.last_used = datetime.fromisoformat(skill_dict['last_used'])
            
            self.skills[skill.id] = skill
            self.skill_graph[skill.id] = set(skill.related_skills)
        
        self.acquisition_history = data.get('history', [])


class SkillAcquisition:
    """
    Sistema principal de aquisição de habilidades
    
    Integra:
    - Detecção de oportunidades de aprendizado
    - Prática deliberada
    - Transferência entre habilidades
    - Feedback e ajuste
    """
    
    def __init__(self, skill_tree: Optional[SkillTree] = None):
        self.skill_tree = skill_tree or SkillTree()
        self.learning_sessions: List[Dict] = []
    
    def detect_new_skill_opportunity(
        self,
        task_description: str,
        available_skills: List[str]
    ) -> Optional[Dict]:
        """Detecta oportunidade para nova habilidade"""
        # Análise simplificada
        return None
    
    def start_learning_session(
        self,
        skill_id: str,
        learning_material: str,
        duration_minutes: int
    ) -> Dict:
        """Inicia sessão de aprendizado"""
        session = {
            'id': len(self.learning_sessions) + 1,
            'skill_id': skill_id,
            'material': learning_material,
            'duration': duration_minutes,
            'start_time': datetime.now().isoformat(),
            'completed': False
        }
        
        self.learning_sessions.append(session)
        
        return {
            'success': True,
            'session_id': session['id'],
            'message': f"Sessão de aprendizado iniciada para {skill_id}"
        }
    
    def complete_learning_session(
        self,
        session_id: int,
        comprehension_score: float
    ) -> Dict:
        """Completa sessão de aprendizado"""
        session = next(
            (s for s in self.learning_sessions if s['id'] == session_id),
            None
        )
        
        if not session:
            return {'success': False, 'error': 'session_not_found'}
        
        session['completed'] = True
        session['end_time'] = datetime.now().isoformat()
        session['comprehension'] = comprehension_score
        
        # Aplicar aprendizado
        experience_gain = comprehension_score * (session['duration'] / 60.0)
        result = self.skill_tree.practice_skill(
            session['skill_id'],
            experience_gain
        )
        
        return {
            'success': True,
            'session': session,
            'skill_result': result
        }
    
    def get_learning_recommendations(self) -> List[Dict]:
        """Recomendações de aprendizado"""
        recommendations = []
        
        # Sugerir próxima habilidade
        next_skill = self.skill_tree.suggest_next_skill()
        if next_skill:
            skill = self.skill_tree.get_skill(next_skill)
            recommendations.append({
                'type': 'learn_new',
                'skill_id': next_skill,
                'skill_name': skill.name if skill else 'Unknown',
                'reason': 'Pré-requisitos satisfeitos, pronto para aprender'
            })
        
        # Sugerir prática de habilidades subutilizadas
        for skill in self.skill_tree.skills.values():
            if skill.competency_level != CompetencyLevel.MASTER and skill.times_used < 5:
                recommendations.append({
                    'type': 'practice',
                    'skill_id': skill.id,
                    'skill_name': skill.name,
                    'current_level': skill.competency_level.name,
                    'reason': 'Habilidade pouco praticada'
                })
        
        return recommendations[:5]  # Top 5 recomendações
    
    def statistics(self) -> Dict:
        """Estatísticas gerais"""
        return {
            'skill_tree': self.skill_tree.get_competency_summary(),
            'total_sessions': len(self.learning_sessions),
            'completed_sessions': sum(1 for s in self.learning_sessions if s.get('completed')),
            'recent_sessions': self.learning_sessions[-5:]
        }
