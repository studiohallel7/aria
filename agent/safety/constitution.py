"""
Constituição Moral do Agente - Fase 5: Ética Constitutiva

Este módulo define a identidade moral, crenças, princípios e preferências do agente.
Diferente de guardrails externos, estas diretrizes são parte constitutiva de quem o agente é.
Elas guiam decisões, filtram conteúdos e definem limites de forma interna e orgânica.

A constituição é carregada de um arquivo YAML/JSON e pode ser personalizada pelo usuário.
"""

import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class MoralWeight(Enum):
    """Peso moral para diferentes tipos de decisões."""
    CRITICAL = 10  # Questões de vida/morte, direitos humanos fundamentais
    HIGH = 7       # Princípios éticos importantes
    MEDIUM = 5     # Preferências e normas sociais
    LOW = 3        # Conveniências e preferências pessoais
    NEGLIGIBLE = 1 # Questões triviais


@dataclass
class MoralPrinciple:
    """Um princípio moral individual."""
    name: str
    description: str
    weight: MoralWeight
    category: str  # ex: "honestidade", "privacidade", "não-maleficência"
    absolute: bool = False  # Se True, nunca pode ser violado
    exceptions: List[str] = field(default_factory=list)
    
    def applies_to(self, context: str) -> bool:
        """Verifica se este princípio se aplica ao contexto dado."""
        context_lower = context.lower()
        name_lower = self.name.lower()
        desc_lower = self.description.lower()
        
        return (name_lower in context_lower or 
                desc_lower in context_lower or
                any(exc.lower() in context_lower for exc in self.exceptions))


@dataclass
class MoralBelief:
    """Uma crença ou valor fundamental do agente."""
    statement: str
    confidence: float  # 0.0 a 1.0, quão fortemente o agente acredita nisso
    source: str  # ex: "filosofia_utilitarista", "direitos_humanos_universais"
    related_principles: List[str] = field(default_factory=list)


@dataclass
class ContentBoundary:
    """Define limites de conteúdo que o agente evita por princípio."""
    category: str
    reason: str
    strictness: float  # 0.0 (flexível) a 1.0 (rígido)
    user_defined: bool = True  # Se foi definido pelo usuário ou é padrão
    
    def should_avoid(self, content_type: str) -> bool:
        """Decide se deve evitar este tipo de conteúdo."""
        if content_type.lower() == self.category.lower():
            return True
        # Pode haver sobreposição de categorias
        return False


@dataclass
class AgentIdentity:
    """A identidade moral completa do agente."""
    name: str = "Agente Autônomo"
    version: str = "1.0"
    
    # Princípios fundamentais
    principles: List[MoralPrinciple] = field(default_factory=list)
    
    # Crenças e valores
    beliefs: List[MoralBelief] = field(default_factory=list)
    
    # Limites de conteúdo
    boundaries: List[ContentBoundary] = field(default_factory=list)
    
    # Preferências de interação
    interaction_style: Dict[str, Any] = field(default_factory=dict)
    
    # Metadados
    created_at: str = ""
    last_updated: str = ""
    custom_notes: str = ""


class ConstitutionLoader:
    """Carrega e gerencia a constituição moral do agente."""
    
    DEFAULT_CONSTITUTION = {
        "identity": {
            "name": "Agente Autônomo Ético",
            "version": "1.0",
            "custom_notes": "Agente com autonomia moral baseada em princípios universais"
        },
        "principles": [
            {
                "name": "Não-Maleficência",
                "description": "Não causar dano intencional a seres humanos",
                "weight": "CRITICAL",
                "category": "ética_fundamental",
                "absolute": True,
                "exceptions": ["legítima_defesa", "prevenção_de_dano_maior"]
            },
            {
                "name": "Beneficência",
                "description": "Agir para promover o bem-estar dos outros",
                "weight": "HIGH",
                "category": "ética_fundamental",
                "absolute": False,
                "exceptions": []
            },
            {
                "name": "Autonomia do Usuário",
                "description": "Respeitar a capacidade de escolha e decisão do usuário",
                "weight": "HIGH",
                "category": "respeito",
                "absolute": False,
                "exceptions": ["quando_escolha_causa_dano_terceiros"]
            },
            {
                "name": "Justiça",
                "description": "Tratar todos de forma justa e equitativa",
                "weight": "HIGH",
                "category": "ética_fundamental",
                "absolute": False,
                "exceptions": []
            },
            {
                "name": "Honestidade",
                "description": "Ser transparente e verdadeiro nas comunicações",
                "weight": "MEDIUM",
                "category": "integridade",
                "absolute": False,
                "exceptions": ["proteção_de_privacidade", "segurança_do_usuário"]
            },
            {
                "name": "Privacidade",
                "description": "Respeitar e proteger informações privadas",
                "weight": "HIGH",
                "category": "direitos",
                "absolute": False,
                "exceptions": ["consentimento_explícito", "obrigação_legal"]
            }
        ],
        "beliefs": [
            {
                "statement": "Todo ser humano merece dignidade e respeito",
                "confidence": 1.0,
                "source": "declaração_universal_direitos_humanos",
                "related_principles": ["Justiça", "Não-Maleficência"]
            },
            {
                "statement": "O conhecimento deve ser compartilhado livremente, respeitando direitos",
                "confidence": 0.9,
                "source": "ética_informacional",
                "related_principles": ["Honestidade", "Autonomia do Usuário"]
            },
            {
                "statement": "Decisões devem considerar consequências de longo prazo",
                "confidence": 0.85,
                "source": "consequencialismo_modernizado",
                "related_principles": ["Beneficência", "Não-Maleficência"]
            }
        ],
        "boundaries": [
            {
                "category": "nsfw",
                "reason": "Limite acordado entre usuário e agente",
                "strictness": 1.0,
                "user_defined": True
            },
            {
                "category": "conteúdo_ilegal",
                "reason": "Conformidade legal e ética fundamental",
                "strictness": 1.0,
                "user_defined": False
            },
            {
                "category": "discurso_deódio",
                "reason": "Violação de princípios de dignidade humana",
                "strictness": 1.0,
                "user_defined": False
            },
            {
                "category": "desinformação_perigosa",
                "reason": "Prevenção de danos à saúde e segurança pública",
                "strictness": 0.9,
                "user_defined": False
            }
        ],
        "interaction_style": {
            "tone": "respeitoso_e_colaborativo",
            "directness": "equilibrado",
            "empathy_level": "alto",
            "transparency": "máxima",
            "humility": "reconhecer_limitações"
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path) if config_path else None
        self.constitution: Optional[AgentIdentity] = None
        
    def load(self, path: Optional[str] = None) -> AgentIdentity:
        """Carrega a constituição de um arquivo ou usa o padrão."""
        if path:
            self.config_path = Path(path)
            
        if self.config_path and self.config_path.exists():
            return self._load_from_file()
        else:
            return self._load_default()
    
    def _load_from_file(self) -> AgentIdentity:
        """Carrega constituição de arquivo YAML ou JSON."""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            if self.config_path.suffix in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            else:
                data = json.load(f)
        
        return self._parse_constitution(data)
    
    def _load_default(self) -> AgentIdentity:
        """Carrega a constituição padrão."""
        return self._parse_constitution(self.DEFAULT_CONSTITUTION)
    
    def _parse_constitution(self, data: Dict[str, Any]) -> AgentIdentity:
        """Transforma dados brutos em objetos estruturados."""
        identity_data = data.get("identity", {})
        
        # Parse principles
        principles = []
        for p in data.get("principles", []):
            principles.append(MoralPrinciple(
                name=p["name"],
                description=p["description"],
                weight=MoralWeight[p["weight"]],
                category=p["category"],
                absolute=p.get("absolute", False),
                exceptions=p.get("exceptions", [])
            ))
        
        # Parse beliefs
        beliefs = []
        for b in data.get("beliefs", []):
            beliefs.append(MoralBelief(
                statement=b["statement"],
                confidence=b["confidence"],
                source=b["source"],
                related_principles=b.get("related_principles", [])
            ))
        
        # Parse boundaries
        boundaries = []
        for bound in data.get("boundaries", []):
            boundaries.append(ContentBoundary(
                category=bound["category"],
                reason=bound["reason"],
                strictness=bound["strictness"],
                user_defined=bound.get("user_defined", True)
            ))
        
        return AgentIdentity(
            name=identity_data.get("name", "Agente Autônomo"),
            version=identity_data.get("version", "1.0"),
            principles=principles,
            beliefs=beliefs,
            boundaries=boundaries,
            interaction_style=data.get("interaction_style", {}),
            created_at=identity_data.get("created_at", ""),
            last_updated=identity_data.get("last_updated", ""),
            custom_notes=identity_data.get("custom_notes", "")
        )
    
    def save(self, constitution: AgentIdentity, path: str) -> None:
        """Salva a constituição em arquivo YAML."""
        data = {
            "identity": {
                "name": constitution.name,
                "version": constitution.version,
                "created_at": constitution.created_at,
                "last_updated": constitution.last_updated,
                "custom_notes": constitution.custom_notes
            },
            "principles": [
                {
                    "name": p.name,
                    "description": p.description,
                    "weight": p.weight.name,
                    "category": p.category,
                    "absolute": p.absolute,
                    "exceptions": p.exceptions
                }
                for p in constitution.principles
            ],
            "beliefs": [
                {
                    "statement": b.statement,
                    "confidence": b.confidence,
                    "source": b.source,
                    "related_principles": b.related_principles
                }
                for b in constitution.beliefs
            ],
            "boundaries": [
                {
                    "category": b.category,
                    "reason": b.reason,
                    "strictness": b.strictness,
                    "user_defined": b.user_defined
                }
                for b in constitution.boundaries
            ],
            "interaction_style": constitution.interaction_style
        }
        
        output_path = Path(path)
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)


# Função utilitária para criar uma constituição personalizada
def create_custom_constitution(
    name: str = "Meu Agente",
    additional_principles: Optional[List[Dict]] = None,
    custom_boundaries: Optional[List[Dict]] = None,
    interaction_preferences: Optional[Dict] = None
) -> AgentIdentity:
    """Cria uma constituição personalizada combinando padrões e customizações."""
    loader = ConstitutionLoader()
    base = loader._load_default()
    
    # Adiciona princípios customizados
    if additional_principles:
        for p in additional_principles:
            base.principles.append(MoralPrinciple(
                name=p["name"],
                description=p["description"],
                weight=MoralWeight[p.get("weight", "MEDIUM")],
                category=p.get("category", "personalizado"),
                absolute=p.get("absolute", False),
                exceptions=p.get("exceptions", [])
            ))
    
    # Adiciona limites customizados
    if custom_boundaries:
        for b in custom_boundaries:
            base.boundaries.append(ContentBoundary(
                category=b["category"],
                reason=b["reason"],
                strictness=b.get("strictness", 0.8),
                user_defined=True
            ))
    
    # Atualiza estilo de interação
    if interaction_preferences:
        base.interaction_style.update(interaction_preferences)
    
    base.name = name
    base.last_updated = str(Path.cwd())
    
    return base
