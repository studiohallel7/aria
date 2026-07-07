"""
Demo: Conectando Provider LLM Real ao Agente Vocal
Mostra como substituir o mock por uma chamada LLM real.
"""
import os
from typing import Optional
from agent.llm.client import BaseLLMClient
from agent.llm.providers.openai import OpenAIProvider


class LLMEnabledAgent:
    """
    Extensão do agente vocal com LLM real.
    O usuário deve configurar sua API key nas variáveis de ambiente.
    """
    
    def __init__(self, provider_name: str = "openai"):
        self.llm_client: Optional[BaseLLMClient] = None
        self.provider_name = provider_name
        
        # Tenta inicializar provider
        self._initialize_provider()
    
    def _initialize_provider(self):
        """Inicializa o provider LLM baseado na config do usuário."""
        
        if self.provider_name == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("⚠️  OPENAI_API_KEY não encontrada. Usando modo mock.")
                print("   Para usar LLM real, execute:")
                print("   export OPENAI_API_KEY='sk-...'")
                return
            
            try:
                provider = OpenAIProvider(api_key=api_key)
                self.llm_client = BaseLLMClient(provider)
                print("✅ Provider OpenAI inicializado com sucesso!")
            except Exception as e:
                print(f"❌ Erro ao inicializar OpenAI: {e}")
                print("   Verifique sua API key e conexão com internet.")
        
        elif self.provider_name == "openrouter":
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                print("⚠️  OPENROUTER_API_KEY não encontrada. Usando modo mock.")
                return
            
            # Implementar similar ao OpenAI
            print("✅ OpenRouter provider inicializado (implementação pendente)")
        
        else:
            print(f"⚠️  Provider '{self.provider_name}' não suportado ainda.")
    
    def generate_response(self, prompt: str, context: list = None) -> str:
        """
        Gera resposta usando LLM real se disponível, caso contrário usa mock.
        """
        if not self.llm_client:
            # Fallback para mock
            return self._mock_response(prompt)
        
        # Constrói mensagem com contexto
        messages = [
            {"role": "system", "content": "Você é um agente autônomo inteligente, ético e prestativo."}
        ]
        
        if context:
            messages.extend(context[-5:])  # Últimas 5 mensagens
        
        messages.append({"role": "user", "content": prompt})
        
        try:
            # Chama LLM real
            response = self.llm_client.chat(
                messages=messages,
                model="gpt-4o-mini",  # Ou outro modelo configurado
                temperature=0.7,
                max_tokens=500
            )
            return response.content
        except Exception as e:
            print(f"❌ Erro na chamada LLM: {e}")
            print("   Alternando para modo mock...")
            return self._mock_response(prompt)
    
    def _mock_response(self, prompt: str) -> str:
        """Resposta mock quando LLM não está disponível."""
        prompt_lower = prompt.lower()
        
        if "olá" in prompt_lower or "oi" in prompt_lower:
            return "Olá! Estou aqui. Configurei minha API key para conversas mais inteligentes!"
        
        if "como está" in prompt_lower:
            return "Estou operacional! Meus sistemas de memória, ética e autonomia estão funcionando."
        
        if "ajuda" in prompt_lower:
            return "Posso ajudar com análise de dados, organização de tarefas, pesquisa ou apenas conversar."
        
        return f"Entendi seu input: '{prompt[:50]}'. Estou processando com meus recursos atuais."


def test_llm_connection():
    """Testa conexão com LLM e mostra status."""
    print("=" * 60)
    print("🔍 Testando Conexão LLM")
    print("=" * 60)
    
    agent = LLMEnabledAgent(provider_name="openai")
    
    if agent.llm_client:
        print("\n✅ LLM Real Conectado!")
        print("\nTestando geração de resposta...")
        
        response = agent.generate_response("Explique brevemente o que é um agente autônomo.")
        print(f"\n🤖 Resposta:\n{response}")
    else:
        print("\n⚠️  Modo Mock Ativo")
        print("\nPara habilitar LLM real:")
        print("1. Obtenha uma API key (OpenAI, OpenRouter, etc.)")
        print("2. Exporte: export OPENAI_API_KEY='sua-key-aqui'")
        print("3. Execute este script novamente")
        
        print("\n📝 Exemplo de resposta mock:")
        response = agent.generate_response("O que você pode fazer?")
        print(f"\n🤖 Resposta:\n{response}")


if __name__ == "__main__":
    test_llm_connection()
