"""
Testes de Integração - Validação do Sistema Completo
"""

import pytest
from datetime import datetime

class TestCoreIntegration:
    def test_state_management(self):
        from agent.core.state.agent_state import StateManager
        state_manager = StateManager()
        state = state_manager.get_state()
        assert state is not None
        
    def test_intention_engine(self):
        from agent.core.cognition.intention import IntentionEngine
        engine = IntentionEngine()
        intention = engine.generate_intention(context="Teste", current_goal="Objetivo")
        assert intention is not None

class TestMemoryIntegration:
    def test_memory_manager_creation(self):
        from agent.memory.manager import HolographicMemoryGraph
        memory = HolographicMemoryGraph(agent_id="test")
        assert memory is not None

class TestSafetyIntegration:
    def test_constitution_load(self):
        from agent.safety.constitution import ConstitutionLoader
        loader = ConstitutionLoader()
        constitution = loader.load_default()
        assert constitution is not None

class TestEndToEnd:
    def test_agent_loop_creation(self):
        from agent.core.loop.main_loop import AgentLoop
        loop = AgentLoop(agent_name="TestAgent")
        assert loop is not None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
