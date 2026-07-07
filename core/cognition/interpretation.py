"""
Módulo de Interpretação Contínua
Transforma dados brutos em significado contextual antes do pensamento.
Identifica intenções não ditas, ambiguidades e estados emocionais.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import hashlib
import time


class InterpretationLayer(Enum):
    """Camadas de interpretação da realidade."""
    LITERAL = "literal"           # O que foi dito/existe
    CONTEXTUAL = "contextual"     # O que significa no contexto
    INTENTIONAL = "intentional"   # Qual a intenção por trás
    EMOTIONAL = "emotional"       # Qual o estado emocional implícito
    IMPLICIT = "implicit"         # O que não foi dito mas está lá


@dataclass
class InterpretationResult:
    """Resultado de uma interpretação."""
    layer: InterpretationLayer
    content: str
    confidence: float  # 0.0 - 1.0
    ambiguities: List[str] = field(default_factory=list)
    implicit_meanings: List[str] = field(default_factory=list)
    emotional_tone: Optional[str] = None
    urgency: float = 0.0  # 0.0 - 1.0
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "layer": self.layer.value,
            "content": self.content,
            "confidence": self.confidence,
            "ambiguities": self.ambiguities,
            "implicit_meanings": self.implicit_meanings,
            "emotional_tone": self.emotional_tone,
            "urgency": self.urgency,
            "timestamp": self.timestamp
        }


@dataclass
class RawInput:
    """Entrada bruta para interpretação."""
    source: str  # 'user', 'environment', 'internal', 'system'
    content_type: str  # 'text', 'event', 'signal', 'file_change'
    raw_data: Any
    context_snapshot: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class ContinuousInterpreter:
    """
    Sistema de interpretação contínua que opera em paralelo ao pensamento.
    Transforma dados brutos em significado antes de chegar ao ThinkingEngine.
    """
    
    def __init__(self):
        self.interpretation_history: List[InterpretationResult] = []
        self.context_memory: Dict[str, Any] = {}
        self.ambiguity_threshold = 0.3  # Acima disso, pede clarificação
        self.emotional_sensitivity = 0.7  # Sensibilidade a tons emocionais
        
        # Padrões de interpretação
        self.intention_patterns = {
            "request": ["preciso", "quero", "faça", "crie", "analise"],
            "question": ["como", "por que", "quando", "onde", "qual"],
            "command": ["execute", "rode", "inicie", "pare", "mate"],
            "suggestion": ["talvez", "poderia", "que tal", "sugiro"],
            "frustration": ["não funciona", "erro", "falhou", "quebra"],
            "urgency": ["agora", "urgente", "rápido", "imediatamente"]
        }
        
        self.emotional_indicators = {
            "positive": ["bom", "ótimo", "excelente", "perfeito", "obrigado"],
            "negative": ["ruim", "péssimo", "errado", "ódio", "frustrante"],
            "neutral": ["ok", "certo", "entendi", "veja", "ok"]
        }
    
    def interpret(self, raw_input: RawInput) -> List[InterpretationResult]:
        """
        Interpreta uma entrada bruta em múltiplas camadas simultaneamente.
        Retorna lista de interpretações ordenadas por confiança.
        """
        interpretations = []
        
        # Camada 1: Literal
        literal = self._interpret_literal(raw_input)
        interpretations.append(literal)
        
        # Camada 2: Contextual
        contextual = self._interpret_contextual(raw_input, literal)
        interpretations.append(contextual)
        
        # Camada 3: Intencional
        intentional = self._interpret_intentional(raw_input, contextual)
        interpretations.append(intentional)
        
        # Camada 4: Emocional
        emotional = self._interpret_emotional(raw_input, intentional)
        interpretations.append(emotional)
        
        # Camada 5: Implícita
        implicit = self._interpret_implicit(raw_input, interpretations)
        if implicit:
            interpretations.append(implicit)
        
        # Ordenar por confiança
        interpretations.sort(key=lambda x: x.confidence, reverse=True)
        
        # Atualizar histórico
        self.interpretation_history.extend(interpretations)
        if len(self.interpretation_history) > 1000:
            self.interpretation_history = self.interpretation_history[-500:]
        
        # Atualizar memória de contexto
        self._update_context_memory(raw_input, interpretations)
        
        return interpretations
    
    def _interpret_literal(self, raw_input: RawInput) -> InterpretationResult:
        """Interpretação literal do conteúdo."""
        content = str(raw_input.raw_data)
        
        # Detectar ambiguidades literais
        ambiguities = []
        if len(content) < 5:
            ambiguities.append("Conteúdo muito curto para interpretação precisa")
        if "?" in content and "!" in content:
            ambiguities.append("Tom misto (pergunta + exclamação)")
        
        return InterpretationResult(
            layer=InterpretationLayer.LITERAL,
            content=content,
            confidence=0.95,
            ambiguities=ambiguities,
            urgency=1.0 if "!" in content else 0.5
        )
    
    def _interpret_contextual(self, raw_input: RawInput, 
                             literal: InterpretationResult) -> InterpretationResult:
        """Interpretação baseada no contexto atual."""
        context = raw_input.context_snapshot
        content = literal.content
        
        # Analisar contexto
        implicit_meanings = []
        confidence = 0.8
        
        # Verificar histórico recente
        recent_interpretations = self.interpretation_history[-5:] if self.interpretation_history else []
        
        # Detectar referências contextuais
        if any(word in content.lower() for word in ["isso", "aquilo", "aquele", "esta"]):
            if recent_interpretations:
                last_topic = recent_interpretations[-1].content
                implicit_meanings.append(f"Referência provável a: {last_topic[:50]}")
                confidence += 0.1
            else:
                implicit_meanings.append("Referência contextual sem histórico claro")
                confidence -= 0.2
        
        # Verificar estado do sistema no contexto
        if context.get("agent_state") == "executing" and "pare" in content.lower():
            implicit_meanings.append("Comando de parada durante execução")
            confidence += 0.15
        
        return InterpretationResult(
            layer=InterpretationLayer.CONTEXTUAL,
            content=content,
            confidence=max(0.0, min(1.0, confidence)),
            ambiguities=literal.ambiguities,
            implicit_meanings=implicit_meanings,
            urgency=literal.urgency
        )
    
    def _interpret_intentional(self, raw_input: RawInput,
                              contextual: InterpretationResult) -> InterpretationResult:
        """Detectar intenção por trás do conteúdo."""
        content = contextual.content.lower()
        intentions_detected = []
        confidence = 0.7
        
        for intention, patterns in self.intention_patterns.items():
            matches = sum(1 for pattern in patterns if pattern in content)
            if matches > 0:
                intentions_detected.append(intention)
                confidence += matches * 0.1
        
        # Múltiplas intenções reduzem confiança
        if len(intentions_detected) > 1:
            contextual.ambiguities.append(f"Múltiplas intenções detectadas: {intentions_detected}")
            confidence -= 0.15
        
        implicit_meanings = contextual.implicit_meanings.copy()
        if intentions_detected:
            implicit_meanings.append(f"Intenção primária: {intentions_detected[0]}")
        
        return InterpretationResult(
            layer=InterpretationLayer.INTENTIONAL,
            content=content,
            confidence=max(0.0, min(1.0, confidence)),
            ambiguities=contextual.ambiguities,
            implicit_meanings=implicit_meanings,
            urgency=contextual.urgency * (1.2 if "urgency" in intentions_detected else 1.0)
        )
    
    def _interpret_emotional(self, raw_input: RawInput,
                            intentional: InterpretationResult) -> InterpretationResult:
        """Detectar tom emocional."""
        content = intentional.content.lower()
        emotional_tone = "neutral"
        confidence = 0.6
        
        scores = {"positive": 0, "negative": 0, "neutral": 0}
        
        for emotion, indicators in self.emotional_indicators.items():
            matches = sum(1 for indicator in indicators if indicator in content)
            scores[emotion] = matches
        
        if scores["positive"] > scores["negative"] and scores["positive"] > scores["neutral"]:
            emotional_tone = "positive"
            confidence += 0.2
        elif scores["negative"] > scores["positive"] and scores["negative"] > scores["neutral"]:
            emotional_tone = "negative"
            confidence += 0.2
            intentional.urgency *= 1.3  # Frustração aumenta urgência
        else:
            emotional_tone = "neutral"
        
        # Detectar frustração específica
        if "frustration" in [i for i in intentional.implicit_meanings if "Intenção" in i]:
            emotional_tone = "frustrated"
            confidence += 0.25
        
        implicit_meanings = intentional.implicit_meanings.copy()
        implicit_meanings.append(f"Tom emocional: {emotional_tone}")
        
        return InterpretationResult(
            layer=InterpretationLayer.EMOTIONAL,
            content=intentional.content,
            confidence=max(0.0, min(1.0, confidence)),
            ambiguities=intentional.ambiguities,
            implicit_meanings=implicit_meanings,
            emotional_tone=emotional_tone,
            urgency=min(1.0, intentional.urgency)
        )
    
    def _interpret_implicit(self, raw_input: RawInput,
                           layers: List[InterpretationResult]) -> Optional[InterpretationResult]:
        """Inferir significados implícitos não ditos."""
        # Analisar contradições entre camadas
        contradictions = []
        for i, layer1 in enumerate(layers):
            for layer2 in layers[i+1:]:
                if abs(layer1.confidence - layer2.confidence) > 0.4:
                    contradictions.append(
                        f"Contraste entre {layer1.layer.value} e {layer2.layer.value}"
                    )
        
        if not contradictions and not any(l.implicit_meanings for l in layers):
            return None
        
        # Sintetizar significado implícito
        all_implicit = []
        for layer in layers:
            all_implicit.extend(layer.implicit_meanings)
        
        confidence = 0.5
        if contradictions:
            confidence -= 0.1
        
        return InterpretationResult(
            layer=InterpretationLayer.IMPLICIT,
            content=layers[-1].content,
            confidence=confidence,
            ambiguities=contradictions,
            implicit_meanings=all_implicit,
            emotional_tone=layers[-1].emotional_tone,
            urgency=layers[-1].urgency
        )
    
    def _update_context_memory(self, raw_input: RawInput, 
                              interpretations: List[InterpretationResult]):
        """Atualizar memória de contexto com novas interpretações."""
        # Manter últimas interpretações por tipo de fonte
        source_key = f"{raw_input.source}_last"
        self.context_memory[source_key] = interpretations[-1] if interpretations else None
        
        # Atualizar padrões emocionais recentes
        if interpretations:
            emotional_layer = next(
                (i for i in interpretations if i.layer == InterpretationLayer.EMOTIONAL), 
                None
            )
            if emotional_layer:
                self.context_memory["last_emotional_tone"] = emotional_layer.emotional_tone
                self.context_memory["last_urgency"] = emotional_layer.urgency
    
    def get_ambiguity_alerts(self) -> List[Dict[str, Any]]:
        """Retornar alertas sobre ambiguidades acima do threshold."""
        alerts = []
        recent = self.interpretation_history[-20:]
        
        for interp in recent:
            if len(interp.ambiguities) > 0 and interp.confidence < self.ambiguity_threshold:
                alerts.append({
                    "content": interp.content[:100],
                    "ambiguities": interp.ambiguities,
                    "confidence": interp.confidence,
                    "layer": interp.layer.value,
                    "recommendation": "Solicitar clarificação ao usuário"
                })
        
        return alerts
    
    def clear_history(self):
        """Limpar histórico de interpretações."""
        self.interpretation_history = []
        self.context_memory = {}
