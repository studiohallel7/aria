"""
Fase 8: Aprendizado Contínuo & Auto-Evolução

Módulos para aprendizado online, auto-otimização de prompts, 
evolução de constituição ética e melhoria contínua baseada em feedback.
"""

from .online_learner import OnlineLearner, ExperienceBuffer, LearningStrategy
from .prompt_evolver import PromptEvolver, PromptGene, FitnessEvaluator
from .constitution_evolver import ConstitutionEvolver, EthicalMutation
from .skill_acquisition import SkillAcquisition, SkillTree, CompetencyLevel
from .meta_learning import MetaLearner, PerformanceAnalyzer, AdaptationPlan

__all__ = [
    'OnlineLearner',
    'ExperienceBuffer', 
    'LearningStrategy',
    'PromptEvolver',
    'PromptGene',
    'FitnessEvaluator',
    'ConstitutionEvolver',
    'EthicalMutation',
    'SkillAcquisition',
    'SkillTree',
    'CompetencyLevel',
    'MetaLearner',
    'PerformanceAnalyzer',
    'AdaptationPlan'
]
