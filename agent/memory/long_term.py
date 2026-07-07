"""
Memória de Longo Prazo (Long-Term Memory - LTM)

Armazena informações permanentes com consolidação e recuperação associativa.
Inclui processos de:
- Consolidação: estabilização de memórias
- Esquecimento ativo: remoção seletiva de informações irrelevantes
- Recuperação contextual: busca baseada em contexto e associações
"""

from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
import pickle
import threading


class LongTermMemory:
    """
    Memória de longo prazo com armazenamento persistente e consolidação.
    """
    
    def __init__(self, storage_path: str = "/workspace/agent/memory/ltm_store",
                 consolidation_interval: int = 3600):
        self.storage_path = Path(storage_path)
        self.consolidation_interval = consolidation_interval
        
        # Cria diretório se não existir
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Cache em memória
        self.cache: Dict[str, Any] = {}
        self.access_log: List[Dict[str, Any]] = []
        self._lock = threading.RLock()
        
        # Carrega memórias existentes
        self._load_from_disk()
    
    def store(self, content: Any, memory_type: str = "semantic",
              tags: List[str] = None, importance: float = 0.5,
              source: str = "experience") -> str:
        """Armazena uma memória de longo prazo."""
        with self._lock:
            memory_id = f"{memory_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.cache)}"
            
            memory = {
                "id": memory_id,
                "content": content,
                "memory_type": memory_type,
                "tags": tags or [],
                "importance": importance,
                "source": source,
                "created_at": datetime.now().isoformat(),
                "last_accessed": datetime.now().isoformat(),
                "access_count": 0
            }
            
            self.cache[memory_id] = memory
            
            # Salva em disco periodicamente
            if len(self.cache) % 10 == 0:
                self._save_to_disk()
            
            return memory_id
    
    def retrieve(self, memory_id: str) -> Optional[Any]:
        """Recupera uma memória pelo ID."""
        with self._lock:
            if memory_id not in self.cache:
                return None
            
            memory = self.cache[memory_id]
            memory["access_count"] += 1
            memory["last_accessed"] = datetime.now().isoformat()
            
            # Log de acesso para análise
            self.access_log.append({
                "memory_id": memory_id,
                "timestamp": datetime.now().isoformat()
            })
            
            return memory["content"]
    
    def search_by_tags(self, tags: List[str]) -> List[Dict[str, Any]]:
        """Busca memórias por tags."""
        with self._lock:
            results = []
            for memory in self.cache.values():
                if any(tag in memory.get("tags", []) for tag in tags):
                    results.append(memory)
            return results
    
    def search_by_type(self, memory_type: str) -> List[Dict[str, Any]]:
        """Busca memórias por tipo."""
        with self._lock:
            return [
                m for m in self.cache.values()
                if m.get("memory_type") == memory_type
            ]
    
    def consolidate(self):
        """Processo de consolidação de memórias."""
        with self._lock:
            # Aumenta importância de memórias frequentemente acessadas
            for memory in self.cache.values():
                if memory["access_count"] > 5:
                    memory["importance"] = min(1.0, memory["importance"] + 0.1)
            
            self._save_to_disk()
    
    def forget_low_importance(self, threshold: float = 0.3):
        """Esquece memórias de baixa importância (esquecimento ativo)."""
        with self._lock:
            to_forget = [
                mid for mid, m in self.cache.items()
                if m.get("importance", 0.5) < threshold
            ]
            
            for mid in to_forget:
                del self.cache[mid]
            
            if to_forget:
                self._save_to_disk()
            
            return len(to_forget)
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas da memória de longo prazo."""
        with self._lock:
            by_type = {}
            by_source = {}
            
            for memory in self.cache.values():
                mtype = memory.get("memory_type", "unknown")
                source = memory.get("source", "unknown")
                
                by_type[mtype] = by_type.get(mtype, 0) + 1
                by_source[source] = by_source.get(source, 0) + 1
            
            avg_importance = (
                sum(m.get("importance", 0.5) for m in self.cache.values()) /
                len(self.cache) if self.cache else 0.0
            )
            
            return {
                "total_memories": len(self.cache),
                "by_type": by_type,
                "by_source": by_source,
                "average_importance": avg_importance,
                "total_accesses": sum(m.get("access_count", 0) for m in self.cache.values()),
                "storage_path": str(self.storage_path)
            }
    
    def _save_to_disk(self):
        """Salva cache em disco."""
        try:
            index_file = self.storage_path / "index.json"
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump({
                    mid: m for mid, m in self.cache.items()
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar LTM: {e}")
    
    def _load_from_disk(self):
        """Carrega memórias do disco."""
        try:
            index_file = self.storage_path / "index.json"
            if index_file.exists():
                with open(index_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
        except Exception as e:
            print(f"Erro ao carregar LTM: {e}")
            self.cache = {}
    
    def clear(self):
        """Limpa toda a memória de longo prazo."""
        with self._lock:
            self.cache.clear()
            self.access_log.clear()
            self._save_to_disk()