# 🧠 FASE 8: Aprendizado Contínuo & Auto-Evolução

## Visão Geral

A Fase 8 implementa sistemas de aprendizado contínuo que permitem ao agente:
- **Aprender com experiências** passadas (online learning)
- **Evoluir prompts** automaticamente via algoritmos genéticos
- **Adaptar sua constituição ética** baseada em dilemas
- **Desenvolver habilidades** progressivamente (skill tree)
- **Aprender a aprender** (meta-learning)

## Arquitetura

```
agent/learning/
├── __init__.py              # exports do módulo
├── online_learner.py        # Aprendizado baseado em experiência
├── prompt_evolver.py        # Otimização evolutiva de prompts
├── constitution_evolver.py  # Evolução da ética
├── skill_acquisition.py     # Árvore de habilidades
└── meta_learning.py         # Meta-aprendizado
```

## Componentes Principais

### 1. Online Learner (`online_learner.py`)

**Classes:**
- `Experience`: Uma experiência única (estado, ação, recompensa)
- `ExperienceBuffer`: Buffer com amostragem prioritária
- `OnlineLearner`: Sistema principal de aprendizado
- `LearningStrategy`: Estratégias (supervisionado, reforço, etc.)

**Exemplo de Uso:**
```python
from agent.learning import OnlineLearner, LearningStrategy

learner = OnlineLearner(buffer_capacity=5000)

# Registrar experiência
learner.observe(
    state={'context': 'user_asked_question'},
    action='provided_detailed_answer',
    reward=0.8,
    next_state={'user_satisfied': True},
    strategy=LearningStrategy.REINFORCEMENT
)

# Aprender
metrics = learner.learn(batch_size=32)

# Avaliar
evaluation = learner.evaluate()
print(evaluation['recent_performance'])
```

### 2. Prompt Evolver (`prompt_evolver.py`)

**Classes:**
- `PromptGene`: Prompt representado como gene evolutivo
- `FitnessEvaluator`: Avalia qualidade de prompts
- `PromptEvolver`: Algoritmo genético completo

**Exemplo de Uso:**
```python
from agent.learning import PromptEvolver, FitnessEvaluator

evaluator = FitnessEvaluator(weights={
    'accuracy': 0.3,
    'satisfaction': 0.25,
    'completion': 0.2
})

initial_prompts = [
    "Explique de forma clara e detalhada",
    "Forneça uma explicação completa passo a passo",
    "Descreva minuciosamente o conceito"
]

evolver = PromptEvolver(
    initial_prompts=initial_prompts,
    evaluator=evaluator,
    population_size=20
)

best_prompt = evolver.evolve(generations=10)
print(f"Melhor prompt: {best_prompt.sequence}")
print(f"Fitness: {best_prompt.fitness}")
```

### 3. Constitution Evolver (`constitution_evolver.py`)

**Classes:**
- `EthicalMutation`: Mudança na constituição
- `ConstitutionEvolver`: Evolução ética

**Exemplo de Uso:**
```python
from agent.learning import ConstitutionEvolver, EthicalMutationType

evolver = ConstitutionEvolver(constitution=my_constitution)

# Analisar dilema ético
mutations = evolver.analyze_ethical_dilemma(
    situation={'description': 'privacy_vs_safety'},
    decision_made='prioritized_safety',
    outcome_satisfactory=False
)

# Aprovar/rejeitar mudanças
for i, mutation in enumerate(mutations):
    if mutation.mutation_type == EthicalMutationType.PRINCIPLE_WEIGHT_ADJUST:
        evolver.approve_mutation(i)
```

### 4. Skill Acquisition (`skill_acquisition.py`)

**Classes:**
- `CompetencyLevel`: Níveis (Novice → Master)
- `Skill`: Habilidade individual
- `SkillTree`: Árvore de habilidades
- `SkillAcquisition`: Sistema principal

**Exemplo de Uso:**
```python
from agent.learning import SkillAcquisition, Skill, CompetencyLevel

acquisition = SkillAcquisition()

# Adicionar habilidades
acquisition.skill_tree.add_skill(Skill(
    id='python_programming',
    name='Programação Python',
    description='Escrever código Python',
    category='technical',
    prerequisites=[]
))

# Praticar
result = acquisition.skill_tree.practice_skill(
    'python_programming',
    experience_gain=0.15
)

# Verificar nível
skill = acquisition.skill_tree.get_skill('python_programming')
print(f"Nível: {skill.competency_level.name}")
print(f"Progresso: {skill.progress:.2%}")

# Recomendações
recommendations = acquisition.get_learning_recommendations()
```

### 5. Meta Learning (`meta_learning.py`)

**Classes:**
- `PerformanceAnalyzer`: Análise de desempenho
- `MetaLearner`: Meta-aprendizado
- `AdaptationPlan`: Plano de adaptação

**Exemplo de Uso:**
```python
from agent.learning import MetaLearner

meta = MetaLearner()

# Registrar desempenho
meta.record_performance(
    task_id='task_001',
    task_type='coding',
    success=True,
    score=0.85,
    difficulty=0.6,
    strategy='deep_dive',
    duration_minutes=45
)

# Criar plano de adaptação
plan = meta.create_adaptation_plan(
    current_strategy='mass_practice'
)

if plan:
    print(f"Recomendação: {plan.recommended_strategy}")
    print(f"Razão: {plan.reasoning}")

# Insights
insights = meta.get_meta_insights()
for insight in insights:
    print(insight)
```

## Integração com Outras Fases

### Com Fase 4 (Memória)
```python
# Experiências são armazenadas na memória semântica
memory.store_experience(experience.to_dict())
```

### Com Fase 5 (Ética)
```python
# Constituição evolui baseada em dilemas
constitution_evolver.analyze_ethical_dilemma(...)
```

### Com Fase 6 (Autonomia)
```python
# Drives de auto-melhoria acionam aprendizado
if drive_system.get_intensity(Drive.SELF_IMPROVEMENT) > 0.7:
    learner.learn()
```

## Persistência

Todos os componentes suportam export/import:

```python
# Salvar conhecimento
learner.export_knowledge('knowledge.json')
evolver.export_population('prompts.json')
acquisition.skill_tree.export_tree('skills.json')
meta.export_meta_knowledge('meta.json')

# Carregar conhecimento
learner.import_knowledge('knowledge.json')
evolver.import_population('prompts.json')
acquisition.skill_tree.import_tree('skills.json')
meta.import_meta_knowledge('meta.json')
```

## Configuração Recomendada

```yaml
learning:
  buffer_capacity: 5000
  batch_size: 32
  learning_rate: 0.01
  
  prompt_evolution:
    population_size: 20
    generations: 10
    mutation_rate: 0.3
    
  skills:
    initial_skills:
      - id: communication
        name: Comunicação
        category: soft_skills
      - id: reasoning
        name: Raciocínio Lógico
        category: cognitive
    
  meta_learning:
    enabled: true
    adaptation_threshold: 0.1
```

## Métricas de Desempenho

Monitore:
- **Taxa de aprendizado**: Melhoria no score médio
- **Eficiência de prompts**: Fitness evolution over generations
- **Progresso de habilidades**: Distribuição por nível
- **Adaptações bem-sucedidas**: % de planos que melhoraram performance

## Próximos Passos

1. **Integração com LLM real** para avaliação de prompts
2. **Transfer learning** entre domínios relacionados
3. **Curriculum learning** automático
4. **Social learning** (aprender com outros agentes)

## Referências

- Sutton & Barto - Reinforcement Learning
- Holland - Genetic Algorithms
- Dweck - Growth Mindset
- Flavell - Metacognition
