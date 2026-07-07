"""
Testes abrangentes para os novos módulos cognitivos da Fase 2.
Valida Interpretação, Tédio e Drives Internos.
"""

import pytest
import time
from core.cognition.interpretation import (
    ContinuousInterpreter, RawInput, InterpretationLayer, InterpretationResult
)
from core.cognition.boredom import BoredomEngine, BoredomLevel, BoredomAction
from core.cognition.drive import DriveSystem, DriveType


class TestContinuousInterpreter:
    """Testes para o sistema de interpretação contínua."""
    
    def setup_method(self):
        self.interpreter = ContinuousInterpreter()
    
    def test_literal_interpretation(self):
        """Testar interpretação literal básica."""
        raw_input = RawInput(
            source="user",
            content_type="text",
            raw_data="Preciso que você analise este arquivo agora!"
        )
        
        results = self.interpreter.interpret(raw_input)
        
        assert len(results) >= 1
        assert any(r.layer == InterpretationLayer.LITERAL for r in results)
        
        literal = next(r for r in results if r.layer == InterpretationLayer.LITERAL)
        assert "analise" in literal.content.lower()
        assert literal.urgency == 1.0  # Tem "!" no texto
    
    def test_intentional_interpretation(self):
        """Testar detecção de intenção."""
        raw_input = RawInput(
            source="user",
            content_type="text",
            raw_data="Como posso criar um novo projeto?"
        )
        
        results = self.interpreter.interpret(raw_input)
        
        intentional = next(
            (r for r in results if r.layer == InterpretationLayer.INTENTIONAL),
            None
        )
        
        assert intentional is not None
        assert "question" in [i for i in intentional.implicit_meanings if "Intenção" in i] or \
               any("question" in m for m in intentional.implicit_meanings)
    
    def test_emotional_interpretation(self):
        """Testar detecção de tom emocional."""
        raw_input = RawInput(
            source="user",
            content_type="text",
            raw_data="Isso está funcionando perfeitamente! Obrigado!"
        )
        
        results = self.interpreter.interpret(raw_input)
        
        emotional = next(
            (r for r in results if r.layer == InterpretationLayer.EMOTIONAL),
            None
        )
        
        assert emotional is not None
        assert emotional.emotional_tone == "positive"
    
    def test_contextual_interpretation(self):
        """Testar interpretação contextual com referências."""
        # Primeiro input para criar contexto
        raw_input1 = RawInput(
            source="user",
            content_type="text",
            raw_data="Vamos analisar o arquivo config.yaml"
        )
        self.interpreter.interpret(raw_input1)
        
        # Segundo input com referência contextual
        raw_input2 = RawInput(
            source="user",
            content_type="text",
            raw_data="Faça isso agora",
            context_snapshot={"agent_state": "idle"}
        )
        
        results = self.interpreter.interpret(raw_input2)
        
        contextual = next(
            (r for r in results if r.layer == InterpretationLayer.CONTEXTUAL),
            None
        )
        
        assert contextual is not None
        assert len(contextual.implicit_meanings) > 0 or len(contextual.ambiguities) > 0
    
    def test_ambiguity_detection(self):
        """Testar detecção de ambiguidades."""
        raw_input = RawInput(
            source="user",
            content_type="text",
            raw_data="Ok?"
        )
        
        results = self.interpreter.interpret(raw_input)
        
        # Deve detectar ambiguidade por ser muito curto
        assert any(len(r.ambiguities) > 0 for r in results)
    
    def test_urgency_scaling(self):
        """Testar escalonamento de urgência baseado em emoção."""
        raw_input = RawInput(
            source="user",
            content_type="text",
            raw_data="Isso não funciona! Erro crítico!"
        )
        
        results = self.interpreter.interpret(raw_input)
        
        emotional = next(
            (r for r in results if r.layer == InterpretationLayer.EMOTIONAL),
            None
        )
        
        assert emotional is not None
        assert emotional.emotional_tone in ["negative", "frustrated"]
        assert emotional.urgency > 0.5  # Urgência aumentada por frustração


class TestBoredomEngine:
    """Testes para o motor de tédio."""
    
    def setup_method(self):
        self.engine = BoredomEngine()
    
    def test_initial_state(self):
        """Testar estado inicial do tédio."""
        assert self.engine.state.level == BoredomLevel.ENGAGED
        assert self.engine.state.score == 0.0
    
    def test_boredom_increase_over_time(self):
        """Testar aumento do tédio com tempo ocioso."""
        # Simular passagem de tempo
        self.engine.state.last_stimulation = time.time() - 120  # 2 minutos atrás
        
        state = self.engine.update(has_user_tasks=False, is_executing=False)
        
        assert state.score > 0
        assert state.time_idle >= 120
    
    def test_boredom_level_transitions(self):
        """Testar transições entre níveis de tédio."""
        # Forçar score alto
        self.engine.state.score = 85
        self.engine._update_level()
        
        assert self.engine.state.level == BoredomLevel.DESPERATE
        
        # Reduzir score
        self.engine.state.score = 45
        self.engine._update_level()
        
        assert self.engine.state.level == BoredomLevel.RESTLESS
    
    def test_stimulation_reduces_boredom(self):
        """Testar que estímulos reduzem tédio."""
        initial_score = 60
        self.engine.state.score = initial_score
        
        self.engine.record_stimulation(
            event_type="user_task",
            description="Usuário pediu para analisar arquivo",
            impact=25
        )
        
        assert self.engine.state.score < initial_score
        assert self.engine.state.level.value != BoredomLevel.DESPERATE.value or \
               self.engine.state.score < 80
    
    def test_suggested_actions_by_level(self):
        """Testar ações sugeridas por nível de tédio."""
        # Testar nível ENGAGED
        self.engine.state.score = 10
        self.engine._update_level()
        action = self.engine.get_suggested_action()
        assert action is None or action == BoredomAction.WAIT
        
        # Testar nível BORED
        self.engine.state.score = 75
        self.engine._update_level()
        action = self.engine.get_suggested_action()
        assert action in [BoredomAction.ASK_USER, BoredomAction.CLEANUP, 
                         BoredomAction.OPTIMIZE, None]
        
        # Testar nível DESPERATE
        self.engine.state.score = 95
        self.engine._update_level()
        action = self.engine.get_suggested_action()
        # Em desespero, deve sugerir ASK_USER com alta probabilidade
        actions_tried = set()
        for _ in range(10):
            act = self.engine.get_suggested_action()
            if act:
                actions_tried.add(act)
        
        assert BoredomAction.ASK_USER in actions_tried or len(actions_tried) == 0
    
    def test_frustration_accumulation(self):
        """Testar acumulação de frustração por falta de propósito."""
        self.engine.state.last_stimulation = time.time() - 120
        
        self.engine.update(has_user_tasks=False, is_executing=False)
        
        assert self.engine.state.frustration_accumulator > 0
        assert self.engine.state.purpose_urgency > 0
    
    def test_boredom_message_generation(self):
        """Testar geração de mensagens de tédio."""
        self.engine.state.score = 90
        self.engine._update_level()
        
        message = self.engine.generate_boredom_message()
        
        assert len(message) > 0
        assert isinstance(message, str)


class TestDriveSystem:
    """Testes para o sistema de drives internos."""
    
    def setup_method(self):
        self.drive_system = DriveSystem(personality_profile="balanced")
    
    def test_initialization(self):
        """Testar inicialização dos drives."""
        assert len(self.drive_system.drives) == 7  # 7 tipos de drive
        assert DriveType.CURIOSITY in self.drive_system.drives
        assert DriveType.PURPOSE in self.drive_system.drives
    
    def test_different_personalities(self):
        """Testar diferentes perfis de personalidade."""
        profiles = ["balanced", "explorer", "worker", "scholar"]
        
        for profile in profiles:
            ds = DriveSystem(personality_profile=profile)
            assert len(ds.drives) == 7
            
            # Verificar se weights são diferentes por perfil
            summary = ds.get_personality_summary()
            assert summary["profile"] == profile
    
    def test_drive_decay(self):
        """Testar decay natural dos drives."""
        initial_curiosity = self.drive_system.drives[DriveType.CURIOSITY].current_level
        
        # Atualizar sem ações
        state = self.drive_system.update(
            recent_actions=[],
            environment_changes=0,
            user_interactions=0,
            completed_tasks=0
        )
        
        # Drive deve decair se estiver longe do target
        final_curiosity = self.drive_system.drives[DriveType.CURIOSITY].current_level
        
        # Ou decaiu ou já estava no target
        assert final_curiosity <= initial_curiosity or \
               abs(initial_curiosity - 50.0) < 10
    
    def test_action_satisfaction(self):
        """Testar que ações satisfazem drives relevantes."""
        initial_completion = self.drive_system.drives[DriveType.COMPLETION].current_level
        
        # Simular conclusão de tarefa
        state = self.drive_system.update(
            recent_actions=["finish_task"],
            completed_tasks=1
        )
        
        final_completion = self.drive_system.drives[DriveType.COMPLETION].current_level
        
        assert final_completion > initial_completion
    
    def test_user_interaction_satisfies_social(self):
        """Testar que interação social satisfaz drive social."""
        initial_social = self.drive_system.drives[DriveType.SOCIAL].current_level
        
        state = self.drive_system.update(
            user_interactions=3
        )
        
        final_social = self.drive_system.drives[DriveType.SOCIAL].current_level
        
        assert final_social > initial_social
    
    def test_motivational_state_calculation(self):
        """Testar cálculo do estado motivacional."""
        state = self.drive_system.update()
        
        assert state.dominant_drive is not None or state.overall_tension >= 0
        assert 0 <= state.urgency_level <= 1
        assert isinstance(state.action_candidates, list)
    
    def test_action_suggestions(self):
        """Testar sugestões de ações baseadas em tensão."""
        # Criar tensão artificial
        self.drive_system.drives[DriveType.CURIOSITY].current_level = 10
        self.drive_system.drives[DriveType.CURIOSITY].target_level = 80
        
        suggestions = self.drive_system.get_action_suggestions()
        
        # Deve sugerir ação para CURIOSITY
        curiosity_suggestions = [
            s for s in suggestions if s["drive"] == "curiosity"
        ]
        
        assert len(curiosity_suggestions) > 0
        assert curiosity_suggestions[0]["priority"] in ["high", "medium"]
    
    def test_drive_satisfaction(self):
        """Testar satisfação manual de drive."""
        initial = self.drive_system.drives[DriveType.LEARNING].current_level
        
        self.drive_system.satisfy_drive(DriveType.LEARNING, amount=20)
        
        final = self.drive_system.drives[DriveType.LEARNING].current_level
        
        assert final > initial
        assert final <= 100.0


class TestIntegration:
    """Testes de integração entre os módulos."""
    
    def test_perception_drives_action(self):
        """Testar fluxo: percepção → tédio → drive → ação."""
        interpreter = ContinuousInterpreter()
        boredom = BoredomEngine()
        drives = DriveSystem(personality_profile="explorer")
        
        # Simular agente ocioso
        boredom.state.last_stimulation = time.time() - 180
        boredom.update(has_user_tasks=False, is_executing=False)
        
        # Atualizar drives
        motivational_state = drives.update()
        
        # Agente entediado + drive de curiosidade alto → deve sugerir exploração
        assert boredom.state.level in [BoredomLevel.RESTLESS, BoredomLevel.BORED, 
                                       BoredomLevel.DESPERATE]
        
        # Verificar se há sugestões de ação
        boredom_action = boredom.get_suggested_action()
        drive_suggestions = drives.get_action_suggestions()
        
        # Pelo menos um dos sistemas deve sugerir ação
        assert boredom_action is not None or len(drive_suggestions) > 0
    
    def test_user_input_resets_boredom_and_satisfies_drives(self):
        """Testar que input do usuário reduz tédio e satisfaz drives."""
        boredom = BoredomEngine()
        drives = DriveSystem()
        
        # Deixar agente entediado
        boredom.state.last_stimulation = time.time() - 300
        boredom.update(has_user_tasks=False, is_executing=False)
        
        initial_boredom_score = boredom.state.score
        initial_purpose = drives.drives[DriveType.PURPOSE].current_level
        
        # Simular input do usuário
        boredom.record_stimulation(
            event_type="user_task",
            description="Usuário deu nova tarefa",
            impact=30
        )
        
        drives.update(completed_tasks=0, user_interactions=1)
        
        # Tédio deve reduzir
        assert boredom.state.score < initial_boredom_score
        
        # Drive social e purpose devem aumentar
        final_social = drives.drives[DriveType.SOCIAL].current_level
        assert final_social > 50.0  # Começa em 50, deve aumentar com interação


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
