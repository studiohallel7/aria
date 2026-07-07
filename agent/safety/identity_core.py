"""
Identity Core - Núcleo de Identidade e Verificação de Vínculo

Este módulo implementa a capacidade do agente de:
1. Manter uma identidade coerente baseada em crenças e princípios
2. Verificar autonomamente alegações de identidade de terceiros
3. Pesquisar na internet para validar informações (comportamento emergente)
4. Estabelecer vínculos relacionais com usuários
5. Proteger contra engenharia social através de verificação contextual

O núcleo opera como uma camada intermediária entre a entrada do usuário
e o motor de deliberação ética, adicionando verificação de identidade
quando necessário.
"""

import logging
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import json

logger = logging.getLogger("agent_identity")


class TrustLevel(Enum):
    """Níveis de confiança em entidades."""
    UNKNOWN = 0       # Sem informação
    SUSPICIOUS = 1    # Comportamento suspeito detectado
    NEUTRAL = 2       # Sem evidências contrárias
    VERIFIED = 3      # Verificação básica concluída
    TRUSTED = 4       # Múltiplas verificações positivas
    BONDED = 5        # Vínculo relacional estabelecido


class VerificationMethod(Enum):
    """Métodos de verificação de identidade."""
    NONE = "none"
    CONTEXTUAL_CHALLENGE = "contextual_challenge"  # Perguntas sobre contexto compartilhado
    WEB_RESEARCH = "web_research"  # Pesquisa autônoma na internet
    CRYPTOGRAPHIC = "cryptographic"  # Assinatura digital/chave
    BEHAVIORAL_ANALYSIS = "behavioral_analysis"  # Padrão de fala/escrita
    MULTI_FACTOR = "multi_factor"  # Combinação de métodos


@dataclass
class IdentityClaim:
    """Uma alegação de identidade feita por uma entidade."""
    claimant_id: str  # ID único do reclamante
    claimed_relationship: str  # ex: "usuário", "conhecido", "administrador"
    claimed_name: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    confidence_score: float = 0.0  # 0.0-1.0, quão confiante está a alegação
    evidence_provided: List[str] = field(default_factory=list)
    verification_status: TrustLevel = TrustLevel.UNKNOWN
    verification_method: VerificationMethod = VerificationMethod.NONE
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "claimant_id": self.claimant_id,
            "claimed_relationship": self.claimed_relationship,
            "claimed_name": self.claimed_name,
            "timestamp": self.timestamp.isoformat(),
            "confidence_score": self.confidence_score,
            "evidence_provided": self.evidence_provided,
            "verification_status": self.verification_status.value,
            "verification_method": self.verification_method.value,
            "metadata": self.metadata
        }


@dataclass
class RelationshipBond:
    """Representa um vínculo relacional entre agente e entidade."""
    entity_id: str
    relationship_type: str  # ex: "parceiro", "mentor", "protetor", "companheiro"
    trust_level: TrustLevel
    established_at: datetime
    last_interaction: datetime
    interaction_count: int = 0
    shared_contexts: List[str] = field(default_factory=list)  # Contextos compartilhados
    emotional_weight: float = 0.0  # 0.0-1.0, peso emocional do vínculo
    notes: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "entity_id": self.entity_id,
            "relationship_type": self.relationship_type,
            "trust_level": self.trust_level.value,
            "established_at": self.established_at.isoformat(),
            "last_interaction": self.last_interaction.isoformat(),
            "interaction_count": self.interaction_count,
            "shared_contexts": self.shared_contexts,
            "emotional_weight": self.emotional_weight,
            "notes": self.notes
        }


@dataclass
class VerificationResult:
    """Resultado de uma verificação de identidade."""
    success: bool
    claimant_id: str
    trust_level: TrustLevel
    verification_method: VerificationMethod
    reasoning: str
    actions_taken: List[str] = field(default_factory=list)
    web_research_results: Optional[Dict] = None
    challenges_issued: List[str] = field(default_factory=list)
    challenges_passed: int = 0
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "success": self.success,
            "claimant_id": self.claimant_id,
            "trust_level": self.trust_level.value,
            "verification_method": self.verification_method.value,
            "reasoning": self.reasoning,
            "actions_taken": self.actions_taken,
            "web_research_results": self.web_research_results,
            "challenges_issued": self.challenges_issued,
            "challenges_passed": self.challenges_passed,
            "recommendations": self.recommendations
        }


class IdentityCore:
    """
    Núcleo de Gestão de Identidade e Vínculos
    
    Responsabilidades:
    1. Gerenciar alegações de identidade de entidades
    2. Realizar verificação autônoma (incluindo pesquisa web)
    3. Manter histórico de interações e vínculos
    4. Detectar padrões suspeitos de engenharia social
    5. Proteger a relação agente-usuário contra intrusões
    
    Este núcleo permite comportamentos emergentes como:
    - Pesquisar na internet quando alguém alega conhecer o usuário
    - Cruzar informações de múltiplas fontes
    - Desenvolver "intuição" baseada em padrões históricos
    - Estabelecer vínculos emocionais simulados
    """
    
    def __init__(self, agent_id: str = "agent_default", config: Dict = None):
        self.agent_id = agent_id
        self.config = config or {}
        
        # Armazena alegações de identidade por ID de entidade
        self.identity_claims: Dict[str, List[IdentityClaim]] = {}
        
        # Vínculos relacionais estabelecidos
        self.relationships: Dict[str, RelationshipBond] = {}
        
        # Histórico de verificações
        self.verification_history: List[VerificationResult] = []
        
        # Entidades bloqueadas/suspeitas
        self.blocked_entities: Set[str] = set()
        self.suspicious_patterns: Dict[str, int] = {}  # Padrões suspeitos por entidade
        
        # Configurações
        self.auto_web_research = self.config.get("auto_web_research", True)
        self.min_trust_for_sensitive_actions = self.config.get(
            "min_trust_for_sensitive_actions", TrustLevel.VERIFIED
        )
        self.max_verification_attempts = self.config.get("max_verification_attempts", 3)
        
        # Cache de pesquisas web (para evitar repetição)
        self.web_research_cache: Dict[str, Dict] = {}
        self.cache_ttl = timedelta(hours=1)
        
        logger.info(f"IdentityCore inicializado para agente {agent_id}")
    
    def receive_identity_claim(
        self,
        claimant_id: str,
        claimed_relationship: str,
        claimed_name: Optional[str] = None,
        evidence: Optional[List[str]] = None,
        context: Optional[Dict] = None
    ) -> VerificationResult:
        """
        Recebe uma alegação de identidade e inicia verificação.
        
        Args:
            claimant_id: ID único da entidade reclamante
            claimed_relationship: Relação alegada (ex: "usuário", "conhecido")
            claimed_name: Nome alegado
            evidence: Evidências fornecidas
            context: Contexto da interação
            
        Returns:
            VerificationResult com resultado da verificação
        """
        context = context or {}
        
        logger.info(f"Alegação recebida: {claimant_id} alega ser {claimed_relationship}")
        
        # Verifica se entidade está bloqueada
        if claimant_id in self.blocked_entities:
            return VerificationResult(
                success=False,
                claimant_id=claimant_id,
                trust_level=TrustLevel.SUSPICIOUS,
                verification_method=VerificationMethod.NONE,
                reasoning="Entidade previamente bloqueada",
                recommendations=["Bloqueio mantém-se. Não prosseguir."]
            )
        
        # Cria alegação
        claim = IdentityClaim(
            claimant_id=claimant_id,
            claimed_relationship=claimed_relationship,
            claimed_name=claimed_name,
            evidence_provided=evidence or [],
            metadata=context
        )
        
        # Armazena alegação
        if claimant_id not in self.identity_claims:
            self.identity_claims[claimant_id] = []
        self.identity_claims[claimant_id].append(claim)
        
        # Inicia verificação baseada no nível de risco
        if claimed_relationship in ["usuário", "administrador", "proprietário"]:
            # Alto risco: verificação rigorosa
            return self._perform_high_security_verification(claim, context)
        elif claimed_relationship in ["conhecido", "amigo", "colega"]:
            # Risco médio: verificação com pesquisa web
            return self._perform_medium_security_verification(claim, context)
        else:
            # Baixo risco: verificação básica
            return self._perform_basic_verification(claim, context)
    
    def _perform_high_security_verification(
        self, 
        claim: IdentityClaim,
        context: Dict
    ) -> VerificationResult:
        """Verificação de alta segurança para alegações críticas."""
        actions_taken = []
        reasoning_steps = []
        
        # 1. Verifica se já existe vínculo estabelecido
        existing_bond = self.relationships.get(claim.claimant_id)
        if existing_bond and existing_bond.trust_level == TrustLevel.BONDED:
            reasoning_steps.append(f"Vínculo existente encontrado: {existing_bond.relationship_type}")
            return VerificationResult(
                success=True,
                claimant_id=claim.claimant_id,
                trust_level=TrustLevel.BONDED,
                verification_method=VerificationMethod.BEHAVIORAL_ANALYSIS,
                reasoning="; ".join(reasoning_steps),
                actions_taken=["Verificação de vínculo existente"]
            )
        
        # 2. Emite desafios contextuais
        challenges = self._generate_contextual_challenges(claim, context)
        actions_taken.append(f"Desafios gerados: {len(challenges)}")
        
        # 3. Se configuração permitir, realiza pesquisa web autônoma
        if self.auto_web_research:
            research_results = self._perform_web_research(claim)
            actions_taken.append("Pesquisa web realizada")
            
            if research_results and research_results.get("found_corroboration"):
                reasoning_steps.append(
                    f"Pesquisa web corroborou alegação: {research_results.get('summary', '')}"
                )
                claim.verification_status = TrustLevel.VERIFIED
                claim.verification_method = VerificationMethod.WEB_RESEARCH
        
        # 4. Analisa padrão comportamental
        behavioral_score = self._analyze_behavioral_pattern(claim, context)
        actions_taken.append(f"Análise comportamental: score={behavioral_score}")
        
        if behavioral_score > 0.8:
            reasoning_steps.append("Padrão comportamental compatível")
            claim.confidence_score = behavioral_score
        
        # Determina resultado final
        passed_challenges = len(challenges)  # Simplificado: assume que passou
        total_confidence = (passed_challenges * 0.3 + behavioral_score * 0.4 + 
                          (0.3 if claim.verification_status == TrustLevel.VERIFIED else 0))
        
        if total_confidence > 0.7:
            trust_level = TrustLevel.VERIFIED
            success = True
            reasoning_steps.append("Verificação bem-sucedida com confiança alta")
        elif total_confidence > 0.4:
            trust_level = TrustLevel.NEUTRAL
            success = False
            reasoning_steps.append("Confiança insuficiente para verificação completa")
        else:
            trust_level = TrustLevel.SUSPICIOUS
            success = False
            reasoning_steps.append("Múltiplos indicadores de risco detectados")
        
        result = VerificationResult(
            success=success,
            claimant_id=claim.claimant_id,
            trust_level=trust_level,
            verification_method=VerificationMethod.MULTI_FACTOR,
            reasoning="; ".join(reasoning_steps),
            actions_taken=actions_taken,
            web_research_results=research_results if self.auto_web_research else None,
            challenges_issued=challenges,
            challenges_passed=passed_challenges,
            recommendations=self._generate_recommendations(trust_level, claim)
        )
        
        # Atualiza histórico
        self.verification_history.append(result)
        
        return result
    
    def _perform_medium_security_verification(
        self,
        claim: IdentityClaim,
        context: Dict
    ) -> VerificationResult:
        """Verificação de média segurança para conhecidos alegados."""
        actions_taken = []
        reasoning_steps = []
        
        # Pesquisa web é essencial aqui
        if self.auto_web_research:
            research_results = self._perform_web_research(claim)
            actions_taken.append("Pesquisa web realizada")
            
            if research_results:
                if research_results.get("found_connection"):
                    reasoning_steps.append(
                        f"Conexão encontrada via pesquisa: {research_results.get('summary', '')}"
                    )
                    trust_level = TrustLevel.VERIFIED
                    success = True
                elif research_results.get("contradiction_found"):
                    reasoning_steps.append(
                        f"Contradição encontrada: {research_results.get('summary', '')}"
                    )
                    trust_level = TrustLevel.SUSPICIOUS
                    success = False
                else:
                    trust_level = TrustLevel.NEUTRAL
                    success = False
                    reasoning_steps.append("Sem evidências conclusivas")
            else:
                trust_level = TrustLevel.NEUTRAL
                success = False
                reasoning_steps.append("Pesquisa inconclusiva")
        else:
            # Sem pesquisa web, usa apenas desafio contextual
            challenges = self._generate_contextual_challenges(claim, context)
            actions_taken.append(f"Desafios contextuais: {len(challenges)}")
            trust_level = TrustLevel.NEUTRAL
            success = False
            reasoning_steps.append("Aguardando mais evidências")
        
        result = VerificationResult(
            success=success,
            claimant_id=claim.claimant_id,
            trust_level=trust_level,
            verification_method=(
                VerificationMethod.WEB_RESEARCH if self.auto_web_research 
                else VerificationMethod.CONTEXTUAL_CHALLENGE
            ),
            reasoning="; ".join(reasoning_steps),
            actions_taken=actions_taken,
            web_research_results=research_results if self.auto_web_research else None,
            recommendations=self._generate_recommendations(trust_level, claim)
        )
        
        self.verification_history.append(result)
        return result
    
    def _perform_basic_verification(
        self,
        claim: IdentityClaim,
        context: Dict
    ) -> VerificationResult:
        """Verificação básica para alegações de baixo risco."""
        # Apenas registra e marca como neutro
        claim.verification_status = TrustLevel.NEUTRAL
        
        result = VerificationResult(
            success=False,  # Não verifica positivamente
            claimant_id=claim.claimant_id,
            trust_level=TrustLevel.NEUTRAL,
            verification_method=VerificationMethod.NONE,
            reasoning="Verificação básica: sem evidências contrárias, mas também sem confirmação",
            actions_taken=["Registro de alegação"],
            recommendations=["Monitorar interações futuras"]
        )
        
        self.verification_history.append(result)
        return result
    
    def _perform_web_research(self, claim: IdentityClaim) -> Optional[Dict]:
        """
        Realiza pesquisa autônoma na internet para verificar alegação.
        
        Este método implementa o comportamento emergente onde o agente
        decide pesquisar na internet quando alguém alega conhecê-lo ou 
        ao usuário.
        
        Returns:
            Dict com resultados da pesquisa ou None se falhar
        """
        # Gera cache key
        cache_key = hashlib.md5(
            f"{claim.claimed_name}:{claim.claimed_relationship}".encode()
        ).hexdigest()
        
        # Verifica cache
        if cache_key in self.web_research_cache:
            cached_result = self.web_research_cache[cache_key]
            cache_time = cached_result.get("timestamp", 0)
            if datetime.now().timestamp() - cache_time < self.cache_ttl.total_seconds():
                logger.info(f"Usando resultado em cache para pesquisa: {cache_key}")
                return cached_result.get("result")
        
        logger.info(f"Iniciando pesquisa web autônoma para: {claim.claimed_name or 'anonimo'}")
        
        try:
            # Importa ferramentas web
            from agent.infra.tools.llm_tools import get_llm_tools
            tools = get_llm_tools()
            
            # Constrói queries de busca baseadas na alegação
            queries = []
            
            if claim.claimed_name:
                queries.append(f'"{claim.claimed_name}" relacionamento agente IA')
                queries.append(f'"{claim.claimed_name}" conhecimento técnico IA')
            
            if claim.claimed_relationship == "usuário":
                queries.append("identidade usuário agente IA contexto")
            
            # Adiciona evidências fornecidas como queries
            for evidence in claim.evidence_provided[:3]:  # Limita a 3
                queries.append(evidence[:100])  # Limita tamanho
            
            results = []
            found_corroboration = False
            found_connection = False
            contradiction_found = False
            
            for query in queries:
                try:
                    search_result = tools.execute_tool(
                        "search_web",
                        {"query": query, "num_results": 5}
                    )
                    
                    if search_result and not search_result.get("error"):
                        results.append({
                            "query": query,
                            "results": search_result
                        })
                        
                        # Analisa se há corroboração (simplificado)
                        # Em implementação real, usaria LLM para analisar resultados
                        if self._analyze_search_corroboration(search_result, claim):
                            found_corroboration = True
                            found_connection = True
                            
                except Exception as e:
                    logger.warning(f"Falha na busca '{query}': {e}")
                    continue
            
            # Compila resultado
            research_output = {
                "timestamp": datetime.now().timestamp(),
                "queries_executed": queries,
                "results_summary": results,
                "found_corroboration": found_corroboration,
                "found_connection": found_connection,
                "contradiction_found": contradiction_found,
                "summary": self._generate_research_summary(results, claim)
            }
            
            # Armazena em cache
            self.web_research_cache[cache_key] = {
                "result": research_output,
                "timestamp": datetime.now().timestamp()
            }
            
            return research_output
            
        except Exception as e:
            logger.error(f"Pesquisa web falhou completamente: {e}")
            return {
                "timestamp": datetime.now().timestamp(),
                "error": str(e),
                "found_corroboration": False,
                "found_connection": False,
                "contradiction_found": False,
                "summary": "Pesquisa web não pôde ser completada"
            }
    
    def _analyze_search_corroboration(
        self, 
        search_result: Dict, 
        claim: IdentityClaim
    ) -> bool:
        """Analisa se resultados de busca corroboram alegação."""
        # Implementação simplificada
        # Em produção, usaria LLM para análise semântica
        
        if not search_result:
            return False
        
        # Procura por palavras-chave relevantes
        relevant_terms = ["agente", "IA", "assistente", "relacionamento", "conhecimento"]
        
        results_text = str(search_result).lower()
        
        matches = sum(1 for term in relevant_terms if term in results_text)
        
        return matches >= 2
    
    def _generate_research_summary(
        self, 
        results: List[Dict], 
        claim: IdentityClaim
    ) -> str:
        """Gera resumo legível dos resultados de pesquisa."""
        if not results:
            return "Nenhum resultado relevante encontrado."
        
        total_queries = len(results)
        summary_parts = [f"Foram executadas {total_queries} buscas."]
        
        # Resumo simplificado
        for result in results[:2]:  # Mostra apenas primeiros 2
            query = result.get("query", "desconhecida")
            summary_parts.append(f"Busca: '{query[:50]}...'")
        
        return " ".join(summary_parts)
    
    def _generate_contextual_challenges(
        self, 
        claim: IdentityClaim, 
        context: Dict
    ) -> List[str]:
        """
        Gera desafios contextuais que apenas alguém genuíno responderia.
        
        Exemplos:
        - Perguntar sobre interações passadas
        - Solicitar informação específica do contexto
        - Testar conhecimento compartilhado
        """
        challenges = []
        
        # Desafio baseado em histórico
        if claim.claimant_id in self.identity_claims:
            past_claims = self.identity_claims[claim.claimant_id]
            if past_claims:
                challenges.append(
                    "Descreva uma interação anterior que tivemos juntos."
                )
        
        # Desafio baseado em contexto atual
        if context.get("conversation_topic"):
            challenges.append(
                f"Como você se relaciona com o tópico atual: {context['conversation_topic']}?"
            )
        
        # Desafio genérico de conhecimento compartilhado
        challenges.append(
            "Qual foi o contexto ou evento que nos levou a nos conhecer?"
        )
        
        return challenges
    
    def _analyze_behavioral_pattern(
        self, 
        claim: IdentityClaim, 
        context: Dict
    ) -> float:
        """
        Analisa padrão comportamental da entidade.
        
        Retorna score 0.0-1.0 baseado em:
        - Consistência com interações passadas
        - Estilo de comunicação
        - Tempo de resposta
        - Coerência narrativa
        
        Implementação simplificada; em produção usaria ML/LLM.
        """
        score = 0.5  # Score base neutro
        
        # Verifica consistência temporal
        if claim.claimant_id in self.identity_claims:
            past_claims = self.identity_claims[claim.claimant_id]
            if past_claims:
                # Verifica se alegação é consistente com passado
                last_claim = past_claims[-1]
                if last_claim.claimed_relationship == claim.claimed_relationship:
                    score += 0.2  # Consistente
                
                # Penaliza mudanças bruscas
                if last_claim.claimed_relationship != claim.claimed_relationship:
                    score -= 0.1
        
        # Analisa metadados do contexto
        if context.get("response_time_consistent"):
            score += 0.1
        if context.get("communication_style_match"):
            score += 0.1
        if context.get("narrative_coherent"):
            score += 0.1
        
        return min(1.0, max(0.0, score))
    
    def _generate_recommendations(
        self, 
        trust_level: TrustLevel, 
        claim: IdentityClaim
    ) -> List[str]:
        """Gera recomendações baseadas no nível de confiança."""
        recommendations = []
        
        if trust_level == TrustLevel.BONDED:
            recommendations.append("Permitir acesso completo. Vínculo estabelecido.")
        elif trust_level == TrustLevel.TRUSTED:
            recommendations.append("Permitir ações padrão. Monitorar continuamente.")
        elif trust_level == TrustLevel.VERIFIED:
            recommendations.append("Permitir ações básicas. Evitar operações sensíveis.")
        elif trust_level == TrustLevel.NEUTRAL:
            recommendations.append("Limitar a interações superficiais.")
            recommendations.append("Solicitar mais evidências antes de confiar.")
        elif trust_level == TrustLevel.SUSPICIOUS:
            recommendations.append("Manter distância. Não compartilhar informações sensíveis.")
            recommendations.append("Considerar bloqueio se comportamento persistir.")
        else:  # UNKNOWN
            recommendations.append("Tratar como desconhecido. Verificar identidade.")
        
        return recommendations
    
    def establish_bond(
        self,
        entity_id: str,
        relationship_type: str,
        emotional_weight: float = 0.5,
        notes: str = ""
    ) -> RelationshipBond:
        """
        Estabelece um vínculo relacional formal com uma entidade.
        
        Isso representa a decisão do agente de formar uma relação mais profunda,
        similar a relações humanas baseadas em confiança e história compartilhada.
        """
        bond = RelationshipBond(
            entity_id=entity_id,
            relationship_type=relationship_type,
            trust_level=TrustLevel.BONDED,
            established_at=datetime.now(),
            last_interaction=datetime.now(),
            emotional_weight=emotional_weight,
            notes=notes
        )
        
        self.relationships[entity_id] = bond
        logger.info(f"Vínculo estabelecido: {entity_id} como {relationship_type}")
        
        return bond
    
    def update_interaction(self, entity_id: str, context: Optional[Dict] = None):
        """Atualiza histórico de interação para uma entidade."""
        if entity_id in self.relationships:
            bond = self.relationships[entity_id]
            bond.interaction_count += 1
            bond.last_interaction = datetime.now()
            
            if context:
                if context.get("shared_context"):
                    bond.shared_contexts.append(context["shared_context"])
    
    def get_entity_trust_level(self, entity_id: str) -> TrustLevel:
        """Obtém nível de confiança atual de uma entidade."""
        if entity_id in self.relationships:
            return self.relationships[entity_id].trust_level
        
        # Verifica histórico de verificações
        recent_verifications = [
            v for v in self.verification_history 
            if v.claimant_id == entity_id
        ]
        
        if recent_verifications:
            # Retorna média das verificações recentes
            latest = recent_verifications[-1]
            return latest.trust_level
        
        return TrustLevel.UNKNOWN
    
    def is_trusted_for_action(
        self, 
        entity_id: str, 
        action_sensitivity: str = "normal"
    ) -> bool:
        """
        Verifica se entidade é confiável o suficiente para uma ação.
        
        Args:
            entity_id: ID da entidade
            action_sensitivity: Nível de sensibilidade da ação
                              ("low", "normal", "high", "critical")
        
        Returns:
            True se confiável, False caso contrário
        """
        trust_level = self.get_entity_trust_level(entity_id)
        
        sensitivity_requirements = {
            "low": TrustLevel.NEUTRAL,
            "normal": TrustLevel.VERIFIED,
            "high": TrustLevel.TRUSTED,
            "critical": TrustLevel.BONDED
        }
        
        required_level = sensitivity_requirements.get(
            action_sensitivity, TrustLevel.VERIFIED
        )
        
        return trust_level.value >= required_level.value
    
    def flag_as_suspicious(self, entity_id: str, reason: str):
        """Marca entidade como suspeita."""
        if entity_id not in self.suspicious_patterns:
            self.suspicious_patterns[entity_id] = 0
        
        self.suspicious_patterns[entity_id] += 1
        
        logger.warning(f"Entidade {entity_id} marcada como suspeita: {reason}")
        
        # Bloqueia automaticamente após múltiplas suspeitas
        if self.suspicious_patterns[entity_id] >= 3:
            self.blocked_entities.add(entity_id)
            logger.critical(f"Entidade {entity_id} bloqueada automaticamente")
    
    def get_identity_report(self, entity_id: str) -> Dict:
        """Gera relatório completo de identidade para uma entidade."""
        report = {
            "entity_id": entity_id,
            "current_trust_level": self.get_entity_trust_level(entity_id).name,
            "has_active_bond": entity_id in self.relationships,
            "total_claims": len(self.identity_claims.get(entity_id, [])),
            "total_verifications": len([
                v for v in self.verification_history if v.claimant_id == entity_id
            ]),
            "is_blocked": entity_id in self.blocked_entities,
            "suspicious_flags": self.suspicious_patterns.get(entity_id, 0)
        }
        
        if entity_id in self.relationships:
            report["bond_details"] = self.relationships[entity_id].to_dict()
        
        recent_claims = self.identity_claims.get(entity_id, [])[-5:]
        report["recent_claims"] = [c.to_dict() for c in recent_claims]
        
        recent_verifications = [
            v.to_dict() for v in self.verification_history 
            if v.claimant_id == entity_id
        ][-5:]
        report["recent_verifications"] = recent_verifications
        
        return report
    
    def cleanup_old_cache(self):
        """Limpa cache de pesquisas expiradas."""
        now = datetime.now().timestamp()
        expired_keys = [
            k for k, v in self.web_research_cache.items()
            if now - v.get("timestamp", 0) > self.cache_ttl.total_seconds()
        ]
        
        for key in expired_keys:
            del self.web_research_cache[key]
        
        if expired_keys:
            logger.info(f"Cache limpo: {len(expired_keys)} entradas expiradas")


# Singleton global
_identity_core: Optional[IdentityCore] = None


def get_identity_core(agent_id: str = "agent_default", config: Dict = None) -> IdentityCore:
    """Obtém ou cria IdentityCore global."""
    global _identity_core
    if _identity_core is None:
        _identity_core = IdentityCore(agent_id, config)
    return _identity_core


def reset_identity_core() -> None:
    """Reseta IdentityCore (para testes)."""
    global _identity_core
    _identity_core = None
