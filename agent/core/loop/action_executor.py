"""
Action Executor - Executor real de ações do agente
Substitui o mock por implementação real com ferramentas
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime

from agent.infra.tools.llm_tools import get_llm_tools, LLMTools
from agent.infra.llm.client import LLMMessage
from agent.infra.llm.router import LLMRouter
from agent.safety.identity_core import get_identity_core, TrustLevel

logger = logging.getLogger("agent_executor")


@dataclass
class ActionResult:
    """Resultado de uma ação executada"""
    success: bool
    action_type: str
    description: str
    result: Any = None
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    tool_used: Optional[str] = None
    tokens_used: int = 0
    
    def to_dict(self) -> Dict:
        return {
            "success": self.success,
            "action_type": self.action_type,
            "description": self.description,
            "result": self.result,
            "error": self.error,
            "timestamp": self.timestamp.isoformat(),
            "tool_used": self.tool_used,
            "tokens_used": self.tokens_used
        }


class ActionExecutor:
    """
    Executor real de ações do agente autônomo
    
    Responsabilidades:
    1. Interpretar plano e executar ações
    2. Usar ferramentas reais (filesystem, shell, web)
    3. Chamar LLM para decisões complexas
    4. Retornar resultados estruturados
    5. Verificar identidade antes de ações sensíveis
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.tools = get_llm_tools()
        self.llm_router = LLMRouter()
        
        # Inicializa IdentityCore para verificação de vínculos
        self.identity_core = get_identity_core(
            agent_id=self.config.get("agent_id", "agent_default"),
            config={
                "auto_web_research": self.config.get("auto_web_research", True),
                "min_trust_for_sensitive_actions": TrustLevel.VERIFIED
            }
        )
        
        # Mapeamento de tipos de ação para métodos
        self.action_handlers = {
            "file_operation": self._handle_file_operation,
            "shell_command": self._handle_shell_command,
            "web_search": self._handle_web_search,
            "code_analysis": self._handle_code_analysis,
            "respond_to_user": self._handle_user_response,
            "log_insight": self._handle_log_insight,
            "fix_issue": self._handle_fix_issue,
            "optimize_system": self._handle_optimization,
        }
        
        # Histórico de execuções
        self.execution_history: List[ActionResult] = []
        
        logger.info("ActionExecutor inicializado com ferramentas reais e IdentityCore")
    
    def execute_action(self, action_type: str, description: str, 
                      context: Dict = None, plan_step: Dict = None) -> ActionResult:
        """
        Executa uma ação baseada no tipo
        
        Args:
            action_type: Tipo da ação (file_operation, shell_command, etc)
            description: Descrição detalhada da ação
            context: Contexto adicional para execução
            plan_step: Passo do plano sendo executado
        
        Returns:
            ActionResult com resultado da execução
        """
        context = context or {}
        
        logger.info(f"Executando ação: {action_type} - {description}")
        
        # Seleciona handler baseado no tipo de ação
        handler = self.action_handlers.get(action_type, self._handle_generic_action)
        
        try:
            result = handler(description, context, plan_step)
            self.execution_history.append(result)
            return result
            
        except Exception as e:
            logger.error(f"Erro ao executar ação {action_type}: {e}")
            return ActionResult(
                success=False,
                action_type=action_type,
                description=description,
                error=str(e)
            )
    
    def _handle_file_operation(self, description: str, context: Dict, 
                               plan_step: Dict = None) -> ActionResult:
        """Opera arquivos (ler, escrever, listar)"""
        
        # Usa LLM para interpretar a descrição e extrair parâmetros
        params = self._extract_file_params(description, context)
        
        if not params:
            return ActionResult(
                success=False,
                action_type="file_operation",
                description=description,
                error="Não foi possível extrair parâmetros da operação de arquivo"
            )
        
        operation = params.get("operation", "read")
        path = params.get("path", ".")
        
        try:
            if operation == "read":
                result = self.tools.execute_tool("read_file", {"path": path})
            elif operation == "write":
                content = params.get("content", "")
                result = self.tools.execute_tool("write_file", {"path": path, "content": content})
            elif operation == "list":
                result = self.tools.execute_tool("list_directory", {"path": path})
            elif operation == "search":
                pattern = params.get("pattern", "*")
                recursive = params.get("recursive", False)
                result = self.tools.execute_tool("search_files", {"pattern": pattern, "recursive": recursive})
            else:
                result = {"error": f"Operação desconhecida: {operation}"}
            
            # Verifica se houve erro
            if isinstance(result, dict) and "error" in result:
                return ActionResult(
                    success=False,
                    action_type="file_operation",
                    description=description,
                    error=result["error"],
                    tool_used=f"fs_{operation}"
                )
            
            return ActionResult(
                success=True,
                action_type="file_operation",
                description=description,
                result=result,
                tool_used=f"fs_{operation}"
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                action_type="file_operation",
                description=description,
                error=str(e),
                tool_used=f"fs_{operation}"
            )
    
    def _extract_file_params(self, description: str, context: Dict) -> Optional[Dict]:
        """Usa LLM para extrair parâmetros de operação de arquivo ou usa contexto direto."""
        
        # Se o contexto já tem os parâmetros necessários, usa diretamente
        if context and ('operation' in context or 'path' in context):
            params = {
                'operation': context.get('operation', 'read'),
                'path': context.get('path', '.'),
                'content': context.get('content', ''),
                'pattern': context.get('pattern', '*')
            }
            logger.info(f"Usando parâmetros do contexto: {params}")
            return params
        
        # Tenta extrair com LLM se não houver contexto suficiente
        system_prompt = """Você é um extrator de parâmetros para operações de arquivo.
Analise a descrição e extraia:
- operation: read, write, list, ou search
- path: caminho do arquivo/diretório
- content: conteúdo (se for write)
- pattern: padrão (se for search)

Responda APENAS com JSON válido."""
        
        user_prompt = f"""Descrição da operação: {description}
Contexto: {str(context)[:500]}"""
        
        try:
            messages = [
                LLMMessage(role="system", content=system_prompt),
                LLMMessage(role="user", content=user_prompt)
            ]
            
            response = self.llm_router.chat_completion(
                messages=messages,
                purpose="tarefas_rapidas",
                max_tokens=200
            )
            
            if response.error or not response.content:
                logger.warning(f"LLM falhou: {response.error}")
                # Fallback para extrator simples
                return self._simple_file_param_extract(description, context)
            
            import json
            # Tenta parsear JSON da resposta
            content = response.content.strip()
            # Remove markdown code blocks se presentes
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            content = content.strip()
            
            params = json.loads(content)
            return params
            
        except Exception as e:
            logger.warning(f"Falha ao extrair parâmetros com LLM: {e}")
            # Fallback: tenta extrair manualmente
            return self._simple_file_param_extract(description, context)
    
    def _simple_file_param_extract(self, description: str, context: Dict = None) -> Optional[Dict]:
        """Extrator simples de parâmetros sem LLM"""
        context = context or {}
        desc_lower = description.lower()
        
        if any(word in desc_lower for word in ["ler", "read", "abrir"]):
            operation = "read"
        elif any(word in desc_lower for word in ["escrever", "write", "criar", "salvar"]):
            operation = "write"
        elif any(word in desc_lower for word in ["listar", "list", "ver diretório"]):
            operation = "list"
        elif any(word in desc_lower for word in ["buscar", "search", "procurar"]):
            operation = "search"
        else:
            operation = "read"  # default
        
        # Extrai caminho (simplificado)
        import re
        path_match = re.search(r'["\']([^"\']*\.?\w+)["\']', description)
        path = path_match.group(1) if path_match else context.get('path', '.')
        
        return {"operation": operation, "path": path}
    
    def _handle_shell_command(self, description: str, context: Dict,
                              plan_step: Dict = None) -> ActionResult:
        """Executa comando shell"""
        
        # Usa LLM para extrair comando
        command = self._extract_shell_command(description, context)
        
        if not command:
            return ActionResult(
                success=False,
                action_type="shell_command",
                description=description,
                error="Não foi possível extrair comando shell"
            )
        
        # Validação de segurança (bloqueia comandos perigosos)
        dangerous_commands = ["rm -rf", "sudo", "chmod 777", "dd if=", ":(){:|:&};:"]
        if any(dc in command for dc in dangerous_commands):
            return ActionResult(
                success=False,
                action_type="shell_command",
                description=description,
                error=f"Comando bloqueado por segurança: {command}"
            )
        
        try:
            result = self.tools.execute_tool("execute_command", {"command": command})
            
            if isinstance(result, dict) and "error" in result:
                return ActionResult(
                    success=False,
                    action_type="shell_command",
                    description=description,
                    error=result["error"],
                    tool_used="shell"
                )
            
            return ActionResult(
                success=True,
                action_type="shell_command",
                description=description,
                result=result,
                tool_used="shell"
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                action_type="shell_command",
                description=description,
                error=str(e),
                tool_used="shell"
            )
    
    def _extract_shell_command(self, description: str, context: Dict) -> Optional[str]:
        """Extrai comando shell da descrição"""
        
        system_prompt = """Você é um extrator de comandos shell.
Analise a descrição e extraia o comando shell exato a ser executado.
Responda APENAS com o comando, sem explicações."""
        
        user_prompt = f"""Descrição: {description}
Contexto: {str(context)[:500]}"""
        
        try:
            messages = [
                LLMMessage(role="system", content=system_prompt),
                LLMMessage(role="user", content=user_prompt)
            ]
            
            response = self.llm_router.chat_completion(
                messages=messages,
                purpose="tarefas_rapidas",
                max_tokens=100
            )
            
            if response.error or not response.content:
                return None
            
            return response.content.strip()
            
        except Exception as e:
            logger.warning(f"Falha ao extrair comando: {e}")
            return None
    
    def _handle_web_search(self, description: str, context: Dict,
                          plan_step: Dict = None) -> ActionResult:
        """Busca na web"""
        
        # Extrai query de busca
        query = self._extract_search_query(description, context)
        
        if not query:
            query = description  # fallback
        
        try:
            # NOTA: Atualmente usa placeholder, será implementado com DuckDuckGo
            results = self.tools.execute_tool("search_web", {"query": query, "num_results": 5})
            
            return ActionResult(
                success=True,
                action_type="web_search",
                description=description,
                result=results,
                tool_used="web_search",
                tokens_used=0  # Placeholder não usa tokens
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                action_type="web_search",
                description=description,
                error=str(e),
                tool_used="web_search"
            )
    
    def _extract_search_query(self, description: str, context: Dict) -> Optional[str]:
        """Extrai query de busca da descrição"""
        
        system_prompt = """Extraia a query de busca principal da descrição.
Responda APENAS com a query, sem explicações."""
        
        try:
            messages = [
                LLMMessage(role="system", content=system_prompt),
                LLMMessage(role="user", content=description)
            ]
            
            response = self.llm_router.chat_completion(
                messages=messages,
                purpose="tarefas_rapidas",
                max_tokens=50
            )
            
            if response.error or not response.content:
                return None
            
            return response.content.strip()
            
        except Exception as e:
            logger.warning(f"Falha ao extrair query: {e}")
            return None
    
    def _handle_code_analysis(self, description: str, context: Dict,
                             plan_step: Dict = None) -> ActionResult:
        """Analisa código usando LLM"""
        
        # Obtém código do contexto ou descrição
        code = context.get("code", "")
        file_path = context.get("file_path", "")
        
        if not code and file_path:
            # Lê arquivo
            try:
                code = self.tools.execute_tool("read_file", {"path": file_path})
            except:
                pass
        
        if not code:
            return ActionResult(
                success=False,
                action_type="code_analysis",
                description=description,
                error="Código não disponível para análise"
            )
        
        system_prompt = """Você é um analista de código experiente.
Analise o código fornecido e retorne:
1. Resumo do que o código faz
2. Possíveis problemas ou melhorias
3. Sugestões de otimização

Seja conciso mas completo."""
        
        try:
            messages = [
                LLMMessage(role="system", content=system_prompt),
                LLMMessage(role="user", content=f"Código para análise:\n\n{code[:5000]}")
            ]
            
            response = self.llm_router.chat_completion(
                messages=messages,
                purpose="analise_codigo",
                max_tokens=1000
            )
            
            if response.error:
                return ActionResult(
                    success=False,
                    action_type="code_analysis",
                    description=description,
                    error=response.error,
                    tool_used="llm_analysis"
                )
            
            return ActionResult(
                success=True,
                action_type="code_analysis",
                description=description,
                result=response.content,
                tool_used="llm_analysis",
                tokens_used=response.tokens_used
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                action_type="code_analysis",
                description=description,
                error=str(e),
                tool_used="llm_analysis"
            )
    
    def _handle_user_response(self, description: str, context: Dict,
                             plan_step: Dict = None) -> ActionResult:
        """Gera resposta para usuário com verificação de identidade"""
        
        # Verifica identidade do solicitante se houver entity_id no contexto
        entity_id = context.get("entity_id")
        if entity_id:
            trust_level = self.identity_core.get_entity_trust_level(entity_id)
            
            # Se não for confiável e a ação for sensível, alerta
            if not self.identity_core.is_trusted_for_action(entity_id, "normal"):
                logger.warning(f"Entidade {entity_id} com confiança baixa ({trust_level.name}) tentando interação")
                # Pode adicionar aviso na resposta ou bloquear
        
        # Usa LLM para formular resposta natural
        system_prompt = """Você é um assistente prestativo e claro.
Formule uma resposta natural e útil baseada na descrição da ação concluída.
Inclua:
- O que foi feito
- Resultado obtido
- Próximos passos (se aplicável)

Seja conciso mas informativo."""
        
        mode = context.get("mode", "WORK")
        state = context.get("state", "EXECUTING")
        
        try:
            messages = [
                LLMMessage(role="system", content=system_prompt),
                LLMMessage(role="user", content=f"Ação concluída: {description}\nModo: {mode}\nEstado: {state}")
            ]
            
            response = self.llm_router.chat_completion(
                messages=messages,
                purpose="tarefas_rapidas",
                max_tokens=300
            )
            
            if response.error:
                # Fallback para resposta simples
                response_content = f"Ação concluída: {description}"
            else:
                response_content = response.content
            
            # Atualiza interação se entity_id fornecido
            if entity_id:
                self.identity_core.update_interaction(entity_id, context)
            
            return ActionResult(
                success=True,
                action_type="respond_to_user",
                description=description,
                result={"response": response_content},
                tool_used="llm_response",
                tokens_used=response.tokens_used if not response.error else 0
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                action_type="respond_to_user",
                description=description,
                error=str(e),
                tool_used="llm_response"
            )
    
    def _handle_log_insight(self, description: str, context: Dict,
                           plan_step: Dict = None) -> ActionResult:
        """Registra insight/log"""
        
        logger.info(f"[INSIGHT] {description}")
        
        return ActionResult(
            success=True,
            action_type="log_insight",
            description=description,
            result={"logged": True},
            tool_used="logger"
        )
    
    def _handle_fix_issue(self, description: str, context: Dict,
                         plan_step: Dict = None) -> ActionResult:
        """Tenta corrigir problema identificado"""
        
        issue = context.get("issue", description)
        
        system_prompt = """Você é um resolvedor de problemas.
Analise o problema e sugira uma solução prática.
Retorne:
1. Diagnóstico do problema
2. Solução recomendada
3. Passos para implementar

Seja específico e acionável."""
        
        try:
            messages = [
                LLMMessage(role="system", content=system_prompt),
                LLMMessage(role="user", content=f"Problema: {issue}")
            ]
            
            response = self.llm_router.chat_completion(
                messages=messages,
                purpose="raciocinio_complexo",
                max_tokens=800
            )
            
            if response.error:
                return ActionResult(
                    success=False,
                    action_type="fix_issue",
                    description=description,
                    error=response.error,
                    tool_used="llm_diagnosis"
                )
            
            return ActionResult(
                success=True,
                action_type="fix_issue",
                description=description,
                result={"diagnosis": response.content},
                tool_used="llm_diagnosis",
                tokens_used=response.tokens_used
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                action_type="fix_issue",
                description=description,
                error=str(e),
                tool_used="llm_diagnosis"
            )
    
    def _handle_optimization(self, description: str, context: Dict,
                            plan_step: Dict = None) -> ActionResult:
        """Otimiza sistema/processo"""
        
        system_prompt = """Você é um especialista em otimização de sistemas.
Analise a oportunidade de otimização e retorne:
1. Estado atual
2. Gargalos identificados
3. Recomendações de otimização
4. Impacto esperado

Priorize mudanças de alto impacto e baixo risco."""
        
        try:
            messages = [
                LLMMessage(role="system", content=system_prompt),
                LLMMessage(role="user", content=f"Oportunidade: {description}")
            ]
            
            response = self.llm_router.chat_completion(
                messages=messages,
                purpose="raciocinio_complexo",
                max_tokens=800
            )
            
            if response.error:
                return ActionResult(
                    success=False,
                    action_type="optimize_system",
                    description=description,
                    error=response.error,
                    tool_used="llm_optimization"
                )
            
            return ActionResult(
                success=True,
                action_type="optimize_system",
                description=description,
                result={"recommendations": response.content},
                tool_used="llm_optimization",
                tokens_used=response.tokens_used
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                action_type="optimize_system",
                description=description,
                error=str(e),
                tool_used="llm_optimization"
            )
    
    def _handle_generic_action(self, description: str, context: Dict,
                              plan_step: Dict = None) -> ActionResult:
        """Handler genérico para ações não mapeadas"""
        
        logger.warning(f"Ação genérica não mapeada: {description}")
        
        # Tenta usar LLM para interpretar e executar
        system_prompt = """Uma ação genérica foi solicitada.
Analise e tente executar ou explique por que não pode ser executada.
Retorne um resultado claro."""
        
        try:
            messages = [
                LLMMessage(role="system", content=system_prompt),
                LLMMessage(role="user", content=f"Ação: {description}\nContexto: {str(context)[:500]}")
            ]
            
            response = self.llm_router.chat_completion(
                messages=messages,
                purpose="tarefas_rapidas",
                max_tokens=400
            )
            
            if response.error:
                return ActionResult(
                    success=False,
                    action_type="generic",
                    description=description,
                    error=response.error
                )
            
            return ActionResult(
                success=True,
                action_type="generic",
                description=description,
                result=response.content,
                tool_used="llm_generic"
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                action_type="generic",
                description=description,
                error=str(e)
            )
    
    def get_execution_summary(self) -> Dict:
        """Retorna resumo das execuções"""
        
        total = len(self.execution_history)
        successful = sum(1 for r in self.execution_history if r.success)
        failed = total - successful
        total_tokens = sum(r.tokens_used for r in self.execution_history)
        
        # Agrupa por tipo
        by_type = {}
        for result in self.execution_history:
            action_type = result.action_type
            if action_type not in by_type:
                by_type[action_type] = {"total": 0, "success": 0}
            by_type[action_type]["total"] += 1
            if result.success:
                by_type[action_type]["success"] += 1
        
        return {
            "total_executions": total,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total if total > 0 else 0,
            "total_tokens_used": total_tokens,
            "by_type": by_type,
            "last_execution": self.execution_history[-1].to_dict() if self.execution_history else None
        }


# Singleton global
_executor: Optional[ActionExecutor] = None


def get_executor(config: Dict = None) -> ActionExecutor:
    """Obtém ou cria executor global"""
    global _executor
    if _executor is None:
        _executor = ActionExecutor(config)
    return _executor


def reset_executor() -> None:
    """Reseta executor (para testes)"""
    global _executor
    _executor = None
