"""
Prompt Evolver - Otimização evolutiva de prompts

Implementa algoritmos genéticos para evoluir prompts automaticamente:
- Representação de prompts como genes
- Função de fitness baseada em desempenho
- Crossover e mutação
- Seleção natural das melhores versões
"""

import json
import hashlib
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import numpy as np


class MutationType(Enum):
    """Tipos de mutação suportados"""
    WORD_SWAP = "word_swap"  # Trocar palavra por sinônimo
    PHRASE_INSERT = "phrase_insert"  # Inserir frase nova
    PHRASE_DELETE = "phrase_delete"  # Remover frase
    REORDER = "reorder"  # Reordenar seções
    TONE_CHANGE = "tone_change"  # Mudar tom (formal, casual, etc.)
    EXAMPLE_MODIFY = "example_modify"  # Modificar exemplos


@dataclass
class PromptGene:
    """
    Representação de um prompt como gene evolutivo
    
    Attributes:
        sequence: Texto do prompt
        fitness: Score de desempenho (0-1)
        generation: Geração em que foi criado
        parent_ids: IDs dos pais (para crossover)
        mutations: Histórico de mutações aplicadas
    """
    sequence: str
    fitness: float = 0.0
    generation: int = 0
    parent_ids: List[str] = field(default_factory=list)
    mutations: List[Dict] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        self.id = hashlib.sha256(
            self.sequence.encode()
        ).hexdigest()[:12]
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'sequence': self.sequence,
            'fitness': self.fitness,
            'generation': self.generation,
            'parent_ids': self.parent_ids,
            'mutations': self.mutations,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PromptGene':
        gene = cls(
            sequence=data['sequence'],
            fitness=data.get('fitness', 0.0),
            generation=data.get('generation', 0),
            parent_ids=data.get('parent_ids', []),
            mutations=data.get('mutations', []),
            metadata=data.get('metadata', {})
        )
        gene.id = data.get('id', gene.id)
        return gene


class FitnessEvaluator:
    """
    Avalia qualidade de prompts baseado em múltiplas métricas
    
    Métricas suportadas:
    - Accuracy (quando há ground truth)
    - User satisfaction (feedback explícito)
    - Task completion rate
    - Response quality (via LLM judge)
    - Efficiency (tokens/custo)
    """
    
    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        llm_judge_fn: Optional[Callable] = None
    ):
        # Pesos das métricas (devem somar 1.0)
        self.weights = weights or {
            'accuracy': 0.3,
            'satisfaction': 0.25,
            'completion': 0.2,
            'quality': 0.15,
            'efficiency': 0.1
        }
        
        # Normalizar pesos
        total = sum(self.weights.values())
        self.weights = {k: v/total for k, v in self.weights.items()}
        
        # Função externa para LLM judge
        self.llm_judge_fn = llm_judge_fn
        
        # Histórico de avaliações
        self.evaluation_history: List[Dict] = []
    
    def evaluate(
        self,
        prompt: str,
        response: str,
        context: Optional[Dict] = None,
        feedback: Optional[Dict] = None
    ) -> float:
        """
        Avalia qualidade de um prompt baseado na resposta
        
        Args:
            prompt: Prompt testado
            response: Resposta gerada
            context: Contexto da tarefa (opcional)
            feedback: Feedback do usuário (opcional)
        
        Returns:
            Fitness score (0.0 a 1.0)
        """
        context = context or {}
        feedback = feedback or {}
        
        scores = {}
        
        # 1. Accuracy (se houver ground truth)
        if 'ground_truth' in context:
            scores['accuracy'] = self._calculate_accuracy(
                response, 
                context['ground_truth']
            )
        else:
            scores['accuracy'] = 0.5  # Neutro se não há como medir
        
        # 2. User satisfaction
        if 'rating' in feedback:
            scores['satisfaction'] = feedback['rating'] / 5.0
        elif 'thumbs_up' in feedback:
            scores['satisfaction'] = 1.0 if feedback['thumbs_up'] else 0.0
        else:
            scores['satisfaction'] = 0.5
        
        # 3. Task completion
        if 'task_completed' in feedback:
            scores['completion'] = 1.0 if feedback['task_completed'] else 0.0
        else:
            # Inferir baseado na resposta
            scores['completion'] = self._infer_completion(response)
        
        # 4. Response quality (LLM judge)
        if self.llm_judge_fn:
            scores['quality'] = self.llm_judge_fn(prompt, response)
        else:
            # Heurísticas simples
            scores['quality'] = self._heuristic_quality(response)
        
        # 5. Efficiency (tokens)
        token_count = len(response.split())
        max_expected = context.get('max_tokens', 500)
        scores['efficiency'] = max(0, 1 - (token_count / max_expected))
        
        # Calcular fitness ponderado
        fitness = sum(
            scores[metric] * weight 
            for metric, weight in self.weights.items()
        )
        
        # Registrar avaliação
        self.evaluation_history.append({
            'timestamp': datetime.now().isoformat(),
            'prompt_id': hashlib.sha256(prompt.encode()).hexdigest()[:12],
            'scores': scores,
            'fitness': fitness
        })
        
        return fitness
    
    def _calculate_accuracy(self, response: str, ground_truth: str) -> float:
        """Calcula similaridade com ground truth"""
        # Simplificado: overlap de palavras
        resp_words = set(response.lower().split())
        truth_words = set(ground_truth.lower().split())
        
        if not truth_words:
            return 0.0
        
        overlap = len(resp_words & truth_words)
        return overlap / len(truth_words)
    
    def _infer_completion(self, response: str) -> float:
        """Infere se tarefa foi completada baseado na resposta"""
        completion_indicators = [
            'concluí', 'completei', 'fiz', 'realizei',
            'aqui está', 'segue', 'pronto', 'finalizado'
        ]
        
        response_lower = response.lower()
        matches = sum(
            1 for indicator in completion_indicators
            if indicator in response_lower
        )
        
        return min(1.0, matches / 3.0)  # Normalizar
    
    def _heuristic_quality(self, response: str) -> float:
        """Heurísticas simples para qualidade"""
        score = 0.5  # Base
        
        # Penalizar respostas muito curtas
        word_count = len(response.split())
        if word_count < 10:
            score -= 0.2
        elif word_count > 500:
            score -= 0.1
        
        # Bonificar estrutura (parágrafos, listas)
        if '\n\n' in response:
            score += 0.1
        if '- ' in response or '* ' in response:
            score += 0.1
        if response.count('.') > 2:
            score += 0.1
        
        return max(0.0, min(1.0, score))
    
    def get_best_prompts(self, n: int = 5) -> List[Dict]:
        """Retorna top N prompts avaliados"""
        sorted_history = sorted(
            self.evaluation_history,
            key=lambda x: x['fitness'],
            reverse=True
        )
        return sorted_history[:n]
    
    def statistics(self) -> Dict:
        """Estatísticas das avaliações"""
        if not self.evaluation_history:
            return {'count': 0}
        
        fitnesses = [e['fitness'] for e in self.evaluation_history]
        
        return {
            'count': len(self.evaluation_history),
            'avg_fitness': np.mean(fitnesses),
            'std_fitness': np.std(fitnesses),
            'min_fitness': min(fitnesses),
            'max_fitness': max(fitnesses),
            'best_prompt': self.evaluation_history[np.argmax(fitnesses)]['prompt_id']
        }


class PromptEvolver:
    """
    Sistema de evolução de prompts usando algoritmos genéticos
    
    Fluxo:
    1. População inicial de prompts
    2. Avaliação de fitness
    3. Seleção dos melhores
    4. Crossover e mutação
    5. Nova geração
    6. Repetir até convergência
    """
    
    def __init__(
        self,
        initial_prompts: List[str],
        evaluator: FitnessEvaluator,
        population_size: int = 20,
        elite_count: int = 4,
        mutation_rate: float = 0.3,
        crossover_rate: float = 0.7,
        synonym_api: Optional[Callable] = None
    ):
        self.population_size = population_size
        self.elite_count = elite_count
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        
        self.evaluator = evaluator
        self.synonym_api = synonym_api or self._default_synonyms
        
        # Inicializar população
        self.population: List[PromptGene] = [
            PromptGene(sequence=prompt, generation=0)
            for prompt in initial_prompts[:population_size]
        ]
        
        # Preencher se população inicial pequena
        while len(self.population) < population_size:
            mutated = self._mutate(self.population[-1])
            mutated.generation = 0
            self.population.append(mutated)
        
        # Histórico de gerações
        self.generation_history: List[Dict] = []
        self.current_generation = 0
        self.best_ever: Optional[PromptGene] = None
    
    def evolve(self, generations: int = 10) -> PromptGene:
        """
        Executa evolução por N gerações
        
        Returns:
            Melhor prompt encontrado
        """
        for gen in range(generations):
            self.current_generation = gen + 1
            
            # 1. Avaliar toda população
            self._evaluate_population()
            
            # 2. Atualizar melhor histórico
            current_best = max(self.population, key=lambda p: p.fitness)
            if not self.best_ever or current_best.fitness > self.best_ever.fitness:
                self.best_ever = current_best
            
            # 3. Registrar geração
            self.generation_history.append(self._generation_stats())
            
            # 4. Criar nova população
            self.population = self._create_next_generation()
        
        return self.best_ever
    
    def _evaluate_population(self):
        """Avalia fitness de todos os indivíduos"""
        for gene in self.population:
            # Simular resposta (na prática, chamaria LLM)
            # Aqui usamos uma heurística simples
            simulated_response = f"Resposta para: {gene.sequence[:100]}"
            gene.fitness = self.evaluator.evaluate(
                gene.sequence,
                simulated_response
            )
    
    def _create_next_generation(self) -> List[PromptGene]:
        """Cria próxima geração via seleção, crossover e mutação"""
        new_population = []
        
        # Elitismo: manter melhores
        sorted_pop = sorted(self.population, key=lambda p: p.fitness, reverse=True)
        elites = sorted_pop[:self.elite_count]
        new_population.extend(elites)
        
        # Preencher resto com crossover e mutação
        while len(new_population) < self.population_size:
            # Selecionar pais (tournament selection)
            parent1 = self._tournament_select()
            parent2 = self._tournament_select()
            
            # Crossover
            if random.random() < self.crossover_rate:
                child1, child2 = self._crossover(parent1, parent2)
            else:
                child1, child2 = parent1, parent2
            
            # Mutação
            if random.random() < self.mutation_rate:
                child1 = self._mutate(child1)
            if random.random() < self.mutation_rate and len(new_population) + 1 < self.population_size:
                child2 = self._mutate(child2)
            
            # Adicionar filhos
            child1.generation = self.current_generation
            child1.parent_ids = [parent1.id, parent2.id]
            new_population.append(child1)
            
            if len(new_population) < self.population_size:
                child2.generation = self.current_generation
                child2.parent_ids = [parent1.id, parent2.id]
                new_population.append(child2)
        
        return new_population[:self.population_size]
    
    def _tournament_select(self, k: int = 3) -> PromptGene:
        """Seleção por torneio"""
        contestants = random.sample(self.population, min(k, len(self.population)))
        return max(contestants, key=lambda p: p.fitness)
    
    def _crossover(
        self, 
        parent1: PromptGene, 
        parent2: PromptGene
    ) -> Tuple[PromptGene, PromptGene]:
        """Crossover de um ponto"""
        seq1 = parent1.sequence
        seq2 = parent2.sequence
        
        # Dividir em frases
        sentences1 = seq1.split('. ')
        sentences2 = seq2.split('. ')
        
        if len(sentences1) < 2 or len(sentences2) < 2:
            # Muito curtos, copiar pais
            return parent1, parent2
        
        # Ponto de crossover
        point1 = random.randint(1, len(sentences1) - 1)
        point2 = random.randint(1, len(sentences2) - 1)
        
        # Criar filhos
        child1_seq = '. '.join(sentences1[:point1] + sentences2[point2:])
        child2_seq = '. '.join(sentences2[:point2] + sentences1[point1:])
        
        child1 = PromptGene(
            sequence=child1_seq,
            parent_ids=[parent1.id, parent2.id]
        )
        child2 = PromptGene(
            sequence=child2_seq,
            parent_ids=[parent1.id, parent2.id]
        )
        
        # Registrar crossover nas mutações
        child1.mutations.append({
            'type': 'crossover',
            'parents': [parent1.id, parent2.id],
            'generation': self.current_generation
        })
        child2.mutations.append({
            'type': 'crossover',
            'parents': [parent1.id, parent2.id],
            'generation': self.current_generation
        })
        
        return child1, child2
    
    def _mutate(self, gene: PromptGene) -> PromptGene:
        """Aplica mutação ao gene"""
        mutation_type = random.choice(list(MutationType))
        original_seq = gene.sequence
        
        if mutation_type == MutationType.WORD_SWAP:
            mutated_seq = self._mutate_word_swap(gene.sequence)
        elif mutation_type == MutationType.PHRASE_INSERT:
            mutated_seq = self._mutate_phrase_insert(gene.sequence)
        elif mutation_type == MutationType.PHRASE_DELETE:
            mutated_seq = self._mutate_phrase_delete(gene.sequence)
        elif mutation_type == MutationType.REORDER:
            mutated_seq = self._mutate_reorder(gene.sequence)
        elif mutation_type == MutationType.TONE_CHANGE:
            mutated_seq = self._mutate_tone_change(gene.sequence)
        else:  # EXAMPLE_MODIFY
            mutated_seq = self._mutate_example_modify(gene.sequence)
        
        # Criar novo gene se mudou
        if mutated_seq != original_seq:
            new_gene = PromptGene(
                sequence=mutated_seq,
                parent_ids=[gene.id]
            )
            new_gene.mutations.append({
                'type': mutation_type.value,
                'original': original_seq[:50],
                'generation': self.current_generation
            })
            return new_gene
        
        return gene
    
    def _mutate_word_swap(self, text: str) -> str:
        """Troca palavra por sinônimo"""
        words = text.split()
        if len(words) < 3:
            return text
        
        idx = random.randint(0, len(words) - 1)
        word = words[idx]
        
        synonyms = self.synonym_api(word)
        if synonyms:
            words[idx] = random.choice(synonyms)
        
        return ' '.join(words)
    
    def _mutate_phrase_insert(self, text: str) -> str:
        """Insere frase nova"""
        phrases = [
            "Por favor, seja detalhado.",
            "Explique passo a passo.",
            "Considere todos os aspectos.",
            "Forneça exemplos práticos.",
            "Seja claro e conciso."
        ]
        
        insertions = [
            "Além disso,",
            "É importante notar que",
            "Vale ressaltar que",
            "Em particular,"
        ]
        
        insertion = random.choice(insertions)
        phrase = random.choice(phrases)
        
        sentences = text.split('. ')
        if len(sentences) > 1:
            idx = random.randint(1, len(sentences) - 1)
            sentences.insert(idx, f"{insertion} {phrase}")
            return '. '.join(sentences)
        
        return text + f" {insertion} {phrase}"
    
    def _mutate_phrase_delete(self, text: str) -> str:
        """Remove frase"""
        sentences = text.split('. ')
        if len(sentences) > 2:
            idx = random.randint(0, len(sentences) - 1)
            del sentences[idx]
            return '. '.join(sentences)
        return text
    
    def _mutate_reorder(self, text: str) -> str:
        """Reordena seções"""
        paragraphs = text.split('\n\n')
        if len(paragraphs) > 2:
            random.shuffle(paragraphs)
            return '\n\n'.join(paragraphs)
        return text
    
    def _mutate_tone_change(self, text: str) -> str:
        """Muda tom (simplificado)"""
        tone_modifiers = {
            'formal': ['Por favor', 'Gentilmente', 'Solicito'],
            'casual': ['Oi', 'E aí', 'Vamos lá'],
            'direct': ['Faça isso', 'Execute', 'Implemente'],
            'polite': ['Poderia', 'Seria possível', 'Agradeço se']
        }
        
        tone = random.choice(list(tone_modifiers.keys()))
        modifier = random.choice(tone_modifiers[tone])
        
        return f"{modifier}. {text}"
    
    def _mutate_example_modify(self, text: str) -> str:
        """Modifica exemplos"""
        example_phrases = [
            "Por exemplo,",
            "Como ilustração,",
            "Um caso prático é",
            "Veja o seguinte exemplo:"
        ]
        
        if 'exemplo' in text.lower():
            # Substituir marcador de exemplo
            return text.replace('exemplo', 'caso prático')
        else:
            # Adicionar exemplo
            return text + f" {random.choice(example_phrases)} considere X."
    
    def _default_synonyms(self, word: str) -> List[str]:
        """Sinônimos básicos (substituível por API externa)"""
        synonyms = {
            'bom': ['excelente', 'ótimo', 'qualificado'],
            'rápido': ['veloz', 'ágil', 'eficiente'],
            'importante': ['relevante', 'significativo', 'crucial'],
            'claro': ['óbvio', 'evidente', 'transparente'],
            'ajudar': ['auxiliar', 'assistir', 'suportar'],
            'fazer': ['realizar', 'executar', 'completar']
        }
        return synonyms.get(word.lower(), [])
    
    def _generation_stats(self) -> Dict:
        """Estatísticas da geração atual"""
        fitnesses = [p.fitness for p in self.population]
        
        return {
            'generation': self.current_generation,
            'avg_fitness': np.mean(fitnesses),
            'min_fitness': min(fitnesses),
            'max_fitness': max(fitnesses),
            'std_fitness': np.std(fitnesses),
            'best_individual': self.population[np.argmax(fitnesses)].to_dict()
        }
    
    def get_evolution_history(self) -> List[Dict]:
        """Retorna histórico completo de evolução"""
        return self.generation_history
    
    def export_population(self, filepath: str):
        """Exporta população atual"""
        data = {
            'generation': self.current_generation,
            'population': [p.to_dict() for p in self.population],
            'best_ever': self.best_ever.to_dict() if self.best_ever else None,
            'history': self.generation_history
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def import_population(self, filepath: str):
        """Importa população salva"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.population = [
            PromptGene.from_dict(p) for p in data['population']
        ]
        self.current_generation = data.get('generation', 0)
        
        if data.get('best_ever'):
            self.best_ever = PromptGene.from_dict(data['best_ever'])
        
        self.generation_history = data.get('history', [])
