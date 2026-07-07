"""
Fase 4: Sistema de Memória Persistente Avançada

Arquitetura cognitiva com quatro pilares:
1. Memória Holográfica & Associativa - Grafo dinâmico de conhecimento
2. Processo de Consolidação Noturna - Deduplicação e esquecimento ativo
3. O "Subconsciente" - Ideias incompletas e associações fracas
4. Linha do Tempo Episódica vs. Semântica - Separação de eventos e conhecimento

Author: Autonomous Agent System
Version: 4.0.0
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Set, Tuple
from enum import Enum
import uuid
import json
import asyncio
from collections import defaultdict
import numpy as np
from pathlib import Path
import pickle
import threading
import time


class MemoryType(Enum):
    """Tipos de memória para separação episódica vs semântica."""
    EPISODIC = "episodic"      # Eventos específicos ("o que eu fiz")
    SEMANTIC = "semantic"      # Conhecimento geral ("o que eu sei")
    SUBCONSCIOUS = "subconscious"  # Ideias incompletas, associações fracas


class MemoryConsolidation(Enum):
    """Estados de consolidação da memória."""
    RAW = "raw"              # Memória crua, recém-criada
    CONSOLIDATED = "consolidated"  # Memória processada e estabilizada
    COMPRESSED = "compressed"  # Memória antiga, compactada
    MARKED_FOR_FORGETTING = "marked_for_forgetting"  # Aguardando remoção


@dataclass
class MemoryNode:
    """
    Nodo individual de memória no grafo holográfico.
    
    Atributos:
        id: Identificador único
        content: Conteúdo da memória
        memory_type: Tipo (episódica, semântica, subconsciente)
        consolidation_state: Estado de consolidação
        created_at: Timestamp de criação
        last_accessed: Último acesso (para forgetting curve)
        access_count: Quantas vezes foi acessada
        importance_score: Score de importância (0-1)
        embedding: Vetor de embedding para busca semântica
        associations: IDs de memórias associadas
        metadata: Dados adicionais estruturados
        tags: Tags para associação rápida
        source: Origem da memória (observação, reflexão, ação, etc.)
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    memory_type: MemoryType = MemoryType.EPISODIC
    consolidation_state: MemoryConsolidation = MemoryConsolidation.RAW
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    importance_score: float = 0.5
    embedding: Optional[List[float]] = None
    associations: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)
    source: str = "observation"
    
    def to_dict(self) -> Dict[str, Any]:
        """Serializa para dicionário."""
        return {
            "id": self.id,
            "content": self.content,
            "memory_type": self.memory_type.value,
            "consolidation_state": self.consolidation_state.value,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "access_count": self.access_count,
            "importance_score": self.importance_score,
            "embedding": self.embedding,
            "associations": list(self.associations),
            "metadata": self.metadata,
            "tags": list(self.tags),
            "source": self.source
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryNode":
        """Deserializa de dicionário."""
        node = cls()
        node.id = data.get("id", str(uuid.uuid4()))
        node.content = data.get("content", "")
        node.memory_type = MemoryType(data.get("memory_type", "episodic"))
        node.consolidation_state = MemoryConsolidation(
            data.get("consolidation_state", "raw")
        )
        node.created_at = datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now()
        node.last_accessed = datetime.fromisoformat(data["last_accessed"]) if "last_accessed" in data else datetime.now()
        node.access_count = data.get("access_count", 0)
        node.importance_score = data.get("importance_score", 0.5)
        node.embedding = data.get("embedding")
        node.associations = set(data.get("associations", []))
        node.metadata = data.get("metadata", {})
        node.tags = set(data.get("tags", []))
        node.source = data.get("source", "observation")
        return node
    
    def update_access(self):
        """Atualiza timestamp de acesso e incrementa contador."""
        self.last_accessed = datetime.now()
        self.access_count += 1
    
    def calculate_decay(self, current_time: datetime = None) -> float:
        """
        Calcula fator de decaimento baseado na curva de esquecimento de Ebbinghaus.
        
        Retorna valor entre 0 e 1, onde 1 = memória fresca, 0 = completamente esquecida.
        """
        if current_time is None:
            current_time = datetime.now()
        
        time_diff = current_time - self.last_accessed
        hours_since_access = time_diff.total_seconds() / 3600
        
        # Curva de esquecimento exponencial modificada
        # Memórias importantes decaem mais lentamente
        decay_rate = 0.5 / (1 + self.importance_score)
        decay_factor = np.exp(-decay_rate * np.log1p(hours_since_access))
        
        return max(0.1, decay_factor)  # Mínimo de 0.1 para permitir recuperação


@dataclass
class MemoryAssociation:
    """
    Associação entre duas memórias no grafo holográfico.
    
    A força da associação determina quão facilmente uma memória 
    ativa outra durante a recuperação associativa.
    """
    source_id: str
    target_id: str
    strength: float = 0.5  # 0-1, força da associação
    association_type: str = "related"  # related, causal, temporal, conceptual
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "strength": self.strength,
            "association_type": self.association_type,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class ConsolidationReport:
    """Relatório do processo de consolidação noturna."""
    started_at: datetime
    completed_at: Optional[datetime] = None
    memories_processed: int = 0
    memories_deduplicated: int = 0
    memories_compressed: int = 0
    memories_forgotten: int = 0
    new_associations_created: int = 0
    subconscious_insights: List[str] = field(default_factory=list)
    status: str = "pending"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "memories_processed": self.memories_processed,
            "memories_deduplicated": self.memories_deduplicated,
            "memories_compressed": self.memories_compressed,
            "memories_forgotten": self.memories_forgotten,
            "new_associations_created": self.new_associations_created,
            "subconscious_insights": self.subconscious_insights,
            "status": self.status
        }


class HolographicMemoryGraph:
    """
    Grafo dinâmico de conhecimento para memória holográfica e associativa.
    
    Implementa recuperação baseada em contexto e associações complexas,
    indo além da busca vetorial simples.
    """
    
    def __init__(self):
        self.nodes: Dict[str, MemoryNode] = {}
        self.associations: Dict[Tuple[str, str], MemoryAssociation] = {}
        self.index_by_type: Dict[MemoryType, Set[str]] = defaultdict(set)
        self.index_by_tags: Dict[str, Set[str]] = defaultdict(set)
        self.embedding_matrix: Optional[np.ndarray] = None
        self.id_to_index: Dict[str, int] = {}
        self._lock = threading.RLock()
    
    def add_memory(self, node: MemoryNode) -> str:
        """Adiciona um nodo de memória ao grafo."""
        with self._lock:
            self.nodes[node.id] = node
            self.index_by_type[node.memory_type].add(node.id)
            
            for tag in node.tags:
                self.index_by_tags[tag].add(node.id)
            
            # Atualiza matriz de embeddings se houver embedding
            if node.embedding is not None:
                self._rebuild_embedding_matrix()
            
            return node.id
    
    def remove_memory(self, memory_id: str) -> bool:
        """Remove um nodo de memória do grafo."""
        with self._lock:
            if memory_id not in self.nodes:
                return False
            
            node = self.nodes[memory_id]
            
            # Remove das indexes
            self.index_by_type[node.memory_type].discard(memory_id)
            for tag in node.tags:
                self.index_by_tags[tag].discard(memory_id)
            
            # Remove associações relacionadas
            associations_to_remove = [
                key for key in self.associations.keys()
                if memory_id in key
            ]
            for key in associations_to_remove:
                del self.associations[key]
            
            # Remove das associações de outros nodes
            for other_node in self.nodes.values():
                other_node.associations.discard(memory_id)
            
            del self.nodes[memory_id]
            self._rebuild_embedding_matrix()
            
            return True
    
    def create_association(
        self,
        source_id: str,
        target_id: str,
        strength: float = 0.5,
        association_type: str = "related"
    ) -> bool:
        """Cria uma associação entre duas memórias."""
        with self._lock:
            if source_id not in self.nodes or target_id not in self.nodes:
                return False
            
            # Adiciona às associações bidirecionais
            assoc = MemoryAssociation(
                source_id=source_id,
                target_id=target_id,
                strength=strength,
                association_type=association_type
            )
            self.associations[(source_id, target_id)] = assoc
            
            # Atualiza as listas de associação nos nodes
            self.nodes[source_id].associations.add(target_id)
            self.nodes[target_id].associations.add(source_id)
            
            return True
    
    def get_memory(self, memory_id: str) -> Optional[MemoryNode]:
        """Recupera uma memória pelo ID."""
        with self._lock:
            node = self.nodes.get(memory_id)
            if node:
                node.update_access()
            return node
    
    def search_by_context(
        self,
        query_embedding: List[float],
        memory_type: Optional[MemoryType] = None,
        tags: Optional[Set[str]] = None,
        top_k: int = 10,
        min_importance: float = 0.0
    ) -> List[Tuple[MemoryNode, float]]:
        """
        Busca memórias por similaridade de contexto (embedding).
        
        Combina busca vetorial com filtros semânticos.
        """
        with self._lock:
            if self.embedding_matrix is None or len(self.nodes) == 0:
                return []
            
            query_vector = np.array(query_embedding).reshape(1, -1)
            
            # Calcula similaridade de cosseno
            norms = np.linalg.norm(self.embedding_matrix, axis=1, keepdims=True)
            norms[norms == 0] = 1  # Evita divisão por zero
            normalized_matrix = self.embedding_matrix / norms
            normalized_query = query_vector / np.linalg.norm(query_vector)
            
            similarities = np.dot(normalized_matrix, normalized_query.T).flatten()
            
            # Filtra por tipo e tags se especificado
            candidates = []
            for idx, (memory_id, similarity) in enumerate(zip(
                list(self.id_to_index.keys()), similarities
            )):
                if memory_id not in self.nodes:
                    continue
                
                node = self.nodes[memory_id]
                
                # Filtros
                if memory_type and node.memory_type != memory_type:
                    continue
                
                if tags and not tags.intersection(node.tags):
                    continue
                
                if node.importance_score < min_importance:
                    continue
                
                candidates.append((node, float(similarity)))
            
            # Ordena por similaridade
            candidates.sort(key=lambda x: x[1], reverse=True)
            
            return candidates[:top_k]
    
    def search_associative(
        self,
        seed_memory_id: str,
        max_depth: int = 2,
        min_strength: float = 0.3
    ) -> List[Tuple[MemoryNode, float, List[str]]]:
        """
        Busca associativa a partir de uma memória semente.
        
        Explora o grafo seguindo associações, retornando memórias
        relacionadas com seus caminhos e forças de associação.
        
        Retorna lista de (nodo, força_total, caminho).
        """
        with self._lock:
            if seed_memory_id not in self.nodes:
                return []
            
            results = []
            visited = {seed_memory_id}
            queue = [(seed_memory_id, 1.0, [seed_memory_id])]
            
            while queue:
                current_id, current_strength, path = queue.pop(0)
                
                if len(path) > max_depth + 1:
                    continue
                
                # Adiciona aos resultados (exceto a semente)
                if current_id != seed_memory_id:
                    node = self.nodes[current_id]
                    results.append((node, current_strength, path.copy()))
                
                # Explora associações
                if current_id in self.nodes:
                    for target_id in self.nodes[current_id].associations:
                        if target_id in visited:
                            continue
                        
                        assoc_key = (current_id, target_id)
                        if assoc_key not in self.associations:
                            assoc_key = (target_id, current_id)
                        
                        if assoc_key in self.associations:
                            assoc = self.associations[assoc_key]
                            if assoc.strength >= min_strength:
                                visited.add(target_id)
                                new_strength = current_strength * assoc.strength
                                new_path = path + [target_id]
                                queue.append((target_id, new_strength, new_path))
            
            # Ordena por força total
            results.sort(key=lambda x: x[1], reverse=True)
            return results
    
    def _rebuild_embedding_matrix(self):
        """Reconstrói a matriz de embeddings após mudanças."""
        if not self.nodes:
            self.embedding_matrix = None
            self.id_to_index = {}
            return
        
        embeddings = []
        ids = []
        
        for memory_id, node in self.nodes.items():
            if node.embedding is not None:
                embeddings.append(node.embedding)
                ids.append(memory_id)
        
        if embeddings:
            self.embedding_matrix = np.array(embeddings)
            self.id_to_index = {id_: idx for idx, id_ in enumerate(ids)}
        else:
            self.embedding_matrix = None
            self.id_to_index = {}
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do grafo."""
        with self._lock:
            type_counts = {
                mt.value: len(ids) for mt, ids in self.index_by_type.items()
            }
            
            association_types = defaultdict(int)
            for assoc in self.associations.values():
                association_types[assoc.association_type] += 1
            
            return {
                "total_memories": len(self.nodes),
                "total_associations": len(self.associations),
                "by_type": type_counts,
                "association_types": dict(association_types),
                "has_embeddings": self.embedding_matrix is not None,
                "avg_associations_per_memory": (
                    len(self.associations) * 2 / len(self.nodes)
                    if self.nodes else 0
                )
            }


class SubconsciousProcessor:
    """
    Processador do "Subconsciente" - área para ideias incompletas
    e associações fracas que permitem conexões inusitadas.
    """
    
    def __init__(self, graph: HolographicMemoryGraph):
        self.graph = graph
        self.pending_associations: List[Tuple[str, str, float]] = []
        self.weak_connections: Dict[Tuple[str, str], float] = {}
        self.insight_history: List[Dict[str, Any]] = []
    
    def add_weak_connection(self, memory_id1: str, memory_id2: str, strength: float = 0.2):
        """
        Adiciona uma conexão fraca entre memórias.
        
        Conexões fracas podem se fortalecer com o tempo ou uso,
        simulando o processo criativo de insight.
        """
        key = tuple(sorted([memory_id1, memory_id2]))
        self.weak_connections[key] = strength
    
    def strengthen_connection(self, memory_id1: str, memory_id2: str, delta: float = 0.1):
        """Fortalece uma conexão existente."""
        key = tuple(sorted([memory_id1, memory_id2]))
        if key in self.weak_connections:
            self.weak_connections[key] = min(1.0, self.weak_connections[key] + delta)
            
            # Se fortaleceu o suficiente, promove para associação formal
            if self.weak_connections[key] >= 0.5:
                self.graph.create_association(
                    memory_id1, memory_id2,
                    strength=self.weak_connections[key],
                    association_type="emergent"
                )
                del self.weak_connections[key]
                return True
        return False
    
    def generate_insights(self, max_insights: int = 5) -> List[Dict[str, Any]]:
        """
        Gera insights combinando memórias aparentemente não relacionadas.
        
        Simula intuição ao encontrar padrões ocultos no subconsciente.
        """
        insights = []
        
        # Tenta conectar memórias semanticas com episódicas
        semantic_ids = list(self.graph.index_by_type.get(MemoryType.SEMANTIC, set()))
        episodic_ids = list(self.graph.index_by_type.get(MemoryType.EPISODIC, set()))
        
        # Amostra aleatória para eficiência
        import random
        if len(semantic_ids) > 10:
            semantic_ids = random.sample(semantic_ids, min(10, len(semantic_ids)))
        if len(episodic_ids) > 10:
            episodic_ids = random.sample(episodic_ids, min(10, len(episodic_ids)))
        
        for sem_id in semantic_ids:
            for ep_id in episodic_ids:
                if sem_id == ep_id:
                    continue
                
                sem_node = self.graph.get_memory(sem_id)
                ep_node = self.graph.get_memory(ep_id)
                
                if not sem_node or not ep_node:
                    continue
                
                # Verifica se já têm associação forte
                if ep_id in sem_node.associations:
                    continue
                
                # Calcula potencial de insight baseado em tags compartilhadas
                shared_tags = sem_node.tags.intersection(ep_node.tags)
                if shared_tags:
                    insight_strength = len(shared_tags) * 0.15
                    
                    insights.append({
                        "type": "semantic_episodic_link",
                        "memory_1": sem_id,
                        "memory_2": ep_id,
                        "shared_tags": list(shared_tags),
                        "insight_strength": insight_strength,
                        "description": f"Conexão entre conhecimento '{sem_node.content[:50]}...' e evento '{ep_node.content[:50]}...'"
                    })
        
        # Ordena por força do insight
        insights.sort(key=lambda x: x["insight_strength"], reverse=True)
        
        # Armazena histórico
        self.insight_history.extend(insights[:max_insights])
        
        return insights[:max_insights]
    
    def process_subconscious_dream(self) -> List[str]:
        """
        Processa o subconsciente durante consolidação noturna.
        
        Retorna lista de novos insights descobertos.
        """
        new_insights = []
        
        # Fortalece conexões fracas usadas recentemente
        for key, strength in list(self.weak_connections.items()):
            id1, id2 = key
            node1 = self.graph.get_memory(id1)
            node2 = self.graph.get_memory(id2)
            
            if node1 and node2:
                # Se ambas foram acessadas recentemente, fortalece
                hours_ago_1 = (datetime.now() - node1.last_accessed).total_seconds() / 3600
                hours_ago_2 = (datetime.now() - node2.last_accessed).total_seconds() / 3600
                
                if hours_ago_1 < 24 and hours_ago_2 < 24:
                    self.strengthen_connection(id1, id2, 0.15)
        
        # Gera novos insights
        insights = self.generate_insights(max_insights=3)
        for insight in insights:
            new_insights.append(insight["description"])
            
            # Cria associação fraca para insights promissores
            if insight["insight_strength"] >= 0.3:
                self.add_weak_connection(
                    insight["memory_1"],
                    insight["memory_2"],
                    strength=insight["insight_strength"]
                )
        
        return new_insights


class NightlyConsolidation:
    """
    Processo de Consolidação Noturna.
    
    Mecanismo em segundo plano que, quando o agente está ocioso,
    deduplica, abstrai e faz esquecimento ativo das memórias irrelevantes.
    """
    
    def __init__(
        self,
        graph: HolographicMemoryGraph,
        subconscious: SubconsciousProcessor,
        storage_path: Optional[Path] = None
    ):
        self.graph = graph
        self.subconscious = subconscious
        self.storage_path = storage_path or Path("./data/memory")
        self.consolidation_thread: Optional[threading.Thread] = None
        self.running = False
        self.last_consolidation: Optional[datetime] = None
        self.consolidation_reports: List[ConsolidationReport] = []
    
    def start_background_consolidation(self, idle_threshold_hours: float = 2.0):
        """
        Inicia processo de consolidação em segundo plano.
        
        Executa quando o agente está ocioso por threshold horas.
        """
        def consolidation_loop():
            while self.running:
                time.sleep(300)  # Verifica a cada 5 minutos
                
                # Verifica se está ocioso há tempo suficiente
                # (implementação específica do agente seria necessária aqui)
                if self._should_consolidate(idle_threshold_hours):
                    self.run_consolidation()
        
        self.running = True
        self.consolidation_thread = threading.Thread(target=consolidation_loop, daemon=True)
        self.consolidation_thread.start()
    
    def stop_background_consolidation(self):
        """Para o processo de consolidação em segundo plano."""
        self.running = False
        if self.consolidation_thread:
            self.consolidation_thread.join(timeout=5)
    
    def _should_consolidate(self, idle_threshold_hours: float) -> bool:
        """Verifica se deve executar consolidação."""
        if self.last_consolidation is None:
            return True
        
        hours_since_last = (datetime.now() - self.last_consolidation).total_seconds() / 3600
        return hours_since_last >= idle_threshold_hours
    
    def run_consolidation(self) -> ConsolidationReport:
        """
        Executa o processo completo de consolidação.
        
        Passos:
        1. Deduplicação de memórias similares
        2. Compressão de memórias antigas
        3. Esquecimento ativo de memórias irrelevantes
        4. Fortalecimento de associações importantes
        5. Processamento do subconsciente
        """
        report = ConsolidationReport(started_at=datetime.now())
        
        try:
            # 1. Deduplicação
            report.memories_deduplicated = self._deduplicate_memories()
            
            # 2. Compressão
            report.memories_compressed = self._compress_old_memories()
            
            # 3. Esquecimento ativo
            report.memories_forgotten = self._active_forgetting()
            
            # 4. Fortalecimento de associações
            report.new_associations_created = self._strengthen_important_associations()
            
            # 5. Processamento do subconsciente
            report.subconscious_insights = self.subconscious.process_subconscious_dream()
            
            report.memories_processed = len(self.graph.nodes)
            report.status = "completed"
            
        except Exception as e:
            report.status = f"failed: {str(e)}"
        
        finally:
            report.completed_at = datetime.now()
            self.last_consolidation = report.completed_at
            self.consolidation_reports.append(report)
        
        return report
    
    def _deduplicate_memories(self) -> int:
        """
        Identifica e merge de memórias duplicadas ou muito similares.
        
        Retorna número de memórias removidas por duplicação.
        """
        removed_count = 0
        to_merge: Dict[str, List[str]] = defaultdict(list)
        
        # Agrupa memórias por conteúdo similar (usando hashing simples)
        for memory_id, node in list(self.graph.nodes.items()):
            if node.consolidation_state == MemoryConsolidation.COMPRESSED:
                continue
            
            # Hash do conteúdo normalizado
            content_hash = hash(node.content.lower().strip())
            to_merge[content_hash].append(memory_id)
        
        # Merge de duplicatas
        for content_hash, memory_ids in to_merge.items():
            if len(memory_ids) <= 1:
                continue
            
            # Mantém a mais recente/importante, remove as outras
            sorted_ids = sorted(
                memory_ids,
                key=lambda x: (
                    self.graph.nodes[x].importance_score,
                    self.graph.nodes[x].created_at
                ),
                reverse=True
            )
            
            keeper_id = sorted_ids[0]
            keeper_node = self.graph.nodes[keeper_id]
            
            for duplicate_id in sorted_ids[1:]:
                dup_node = self.graph.nodes[duplicate_id]
                
                # Transfere associações
                for assoc_id in dup_node.associations:
                    if assoc_id != keeper_id:
                        keeper_node.associations.add(assoc_id)
                        self.graph.create_association(
                            keeper_id, assoc_id,
                            strength=0.5,
                            association_type="merged"
                        )
                
                # Transfere tags
                keeper_node.tags.update(dup_node.tags)
                
                # Remove duplicata
                self.graph.remove_memory(duplicate_id)
                removed_count += 1
        
        return removed_count
    
    def _compress_old_memories(self) -> int:
        """
        Comprime memórias antigas não acessadas.
        
        Retorna número de memórias comprimidas.
        """
        compressed_count = 0
        now = datetime.now()
        
        for memory_id, node in list(self.graph.nodes.items()):
            if node.consolidation_state in [
                MemoryConsolidation.COMPRESSED,
                MemoryConsolidation.MARKED_FOR_FORGETTING
            ]:
                continue
            
            days_old = (now - node.created_at).days
            days_since_access = (now - node.last_accessed).days
            
            # Critérios para compressão
            should_compress = (
                (days_old > 30 and days_since_access > 14) or
                (days_old > 90 and node.access_count < 3)
            )
            
            if should_compress:
                # Compressão: resume conteúdo, mantém metadata essencial
                original_content = node.content
                if len(node.content) > 200:
                    node.content = f"[Comprimido] {node.content[:200]}..."
                    node.metadata["original_length"] = len(original_content)
                
                node.consolidation_state = MemoryConsolidation.COMPRESSED
                node.importance_score *= 0.9  # Reduz importância
                compressed_count += 1
        
        return compressed_count
    
    def _active_forgetting(self) -> int:
        """
        Remove ativamente memórias irrelevantes.
        
        Baseia-se na curva de esquecimento e importância.
        Retorna número de memórias esquecidas.
        """
        forgotten_count = 0
        now = datetime.now()
        
        for memory_id, node in list(self.graph.nodes.items()):
            if node.consolidation_state == MemoryConsolidation.MARKED_FOR_FORGETTING:
                # Já marcado, remove
                self.graph.remove_memory(memory_id)
                forgotten_count += 1
                continue
            
            # Calcula decaimento
            decay = node.calculate_decay(now)
            
            # Critérios para esquecimento
            should_forget = (
                (decay < 0.2 and node.importance_score < 0.3) or
                (node.access_count == 0 and (now - node.created_at).days > 60) or
                (node.memory_type == MemoryType.SUBCONSCIOUS and 
                 (now - node.created_at).days > 7 and
                 node.access_count == 0)
            )
            
            if should_forget:
                # Marca para remoção ou remove diretamente se muito irrelevante
                if node.importance_score < 0.1:
                    self.graph.remove_memory(memory_id)
                    forgotten_count += 1
                else:
                    node.consolidation_state = MemoryConsolidation.MARKED_FOR_FORGETTING
        
        return forgotten_count
    
    def _strengthen_important_associations(self) -> int:
        """
        Fortalece associações entre memórias frequentemente acessadas juntas.
        
        Retorna número de novas associações criadas.
        """
        new_associations = 0
        
        # Analisa padrões de acesso conjunto
        # (implementação simplificada - idealmente usaria histórico de acesso)
        for memory_id, node in self.graph.nodes.items():
            if node.access_count < 3:
                continue
            
            # Encontra memórias co-acessadas (mesmas tags, tipo similar)
            candidates = []
            for other_id, other_node in self.graph.nodes.items():
                if other_id == memory_id:
                    continue
                
                if other_id in node.associations:
                    continue
                
                # Similaridade baseada em tags e tipo
                shared_tags = len(node.tags.intersection(other_node.tags))
                same_type = node.memory_type == other_node.memory_type
                
                score = shared_tags * 0.2 + (0.3 if same_type else 0)
                
                if score >= 0.3:
                    candidates.append((other_id, score))
            
            # Cria associações para candidatos fortes
            for other_id, score in candidates[:3]:  # Máximo 3 por memória
                self.graph.create_association(
                    memory_id, other_id,
                    strength=min(0.8, score),
                    association_type="discovered"
                )
                new_associations += 1
        
        return new_associations
    
    def save_state(self, filepath: Optional[Path] = None):
        """Salva o estado completo da memória."""
        filepath = filepath or (self.storage_path / "memory_graph.pkl")
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        state = {
            "graph_nodes": {k: v.to_dict() for k, v in self.graph.nodes.items()},
            "graph_associations": {
                str(k): v.to_dict() for k, v in self.graph.associations.items()
            },
            "weak_connections": {
                str(k): v for k, v in self.subconscious.weak_connections.items()
            },
            "last_consolidation": self.last_consolidation.isoformat() if self.last_consolidation else None,
            "reports": [r.to_dict() for r in self.consolidation_reports[-10:]]
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(state, f)
    
    def load_state(self, filepath: Optional[Path] = None):
        """Carrega o estado completo da memória."""
        filepath = filepath or (self.storage_path / "memory_graph.pkl")
        
        if not filepath.exists():
            return False
        
        with open(filepath, 'rb') as f:
            state = pickle.load(f)
        
        # Restaura nodes
        for memory_id, node_data in state.get("graph_nodes", {}).items():
            node = MemoryNode.from_dict(node_data)
            self.graph.nodes[memory_id] = node
            self.graph.index_by_type[node.memory_type].add(memory_id)
            for tag in node.tags:
                self.graph.index_by_tags[tag].add(memory_id)
        
        # Restaura associações
        for assoc_key, assoc_data in state.get("graph_associations", {}).items():
            # Parse da tupla string de volta
            parts = assoc_key.strip("()").split(", ")
            if len(parts) == 2:
                source, target = parts[0].strip("'"), parts[1].strip("'")
                assoc = MemoryAssociation(
                    source_id=source,
                    target_id=target,
                    strength=assoc_data["strength"],
                    association_type=assoc_data["association_type"]
                )
                self.graph.associations[(source, target)] = assoc
        
        # Restaura conexões fracas
        for conn_key, strength in state.get("weak_connections", {}).items():
            parts = conn_key.strip("()").split(", ")
            if len(parts) == 2:
                id1, id2 = parts[0].strip("'"), parts[1].strip("'")
                self.subconscious.weak_connections[(id1, id2)] = strength
        
        # Restaura metadata
        if state.get("last_consolidation"):
            self.last_consolidation = datetime.fromisoformat(state["last_consolidation"])
        
        return True
