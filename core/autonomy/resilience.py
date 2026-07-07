"""
Sistema de Resiliência e Tratamento de Erros
Gerencia falhas, recupera estado e evita tracebacks expostos.
"""

import time
import random
import logging
from enum import Enum
from typing import Optional, Callable, Any, Dict
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Níveis de severidade de erro."""
    LOW = "low"              # Falha cosmética, ignora
    MEDIUM = "medium"        # Falha operacional, tenta retry
    HIGH = "high"            # Falha crítica, fallback necessário
    FATAL = "fatal"          # Falha sistêmica, requer intervenção


class RecoveryStrategy(Enum):
    """Estratégias de recuperação."""
    IGNORE = "ignore"
    RETRY_IMMEDIATE = "retry_immediate"
    RETRY_EXPONENTIAL = "retry_exponential"
    FALLBACK_MODEL = "fallback_model"
    FALLBACK_MODE = "fallback_mode"  # Muda para modo seguro
    RESTART_MODULE = "restart_module"
    ABORT_GRACEFULLY = "abort_gracefully"


@dataclass
class ErrorContext:
    """Contexto rico sobre o erro ocorrido."""
    error_type: str
    message: str
    module: str
    function: str
    severity: ErrorSeverity
    timestamp: float = field(default_factory=time.time)
    retry_count: int = 0
    original_exception: Optional[Exception] = None
    context_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "type": self.error_type,
            "message": self.message,
            "module": self.module,
            "severity": self.severity.value,
            "retries": self.retry_count,
            "timestamp": self.timestamp
        }


class ResilienceManager:
    """
    Gerente de resiliência do agente.
    Atua como sistema imunológico: detecta, isola e trata falhas.
    """

    def __init__(self):
        self.consecutive_failures = 0
        self.last_error_time: Optional[float] = None
        self.is_degraded_mode = False
        self.max_retries = 3
        self.base_delay = 1.0  # segundos
        self.max_delay = 30.0
        
        # Estatísticas de saúde
        self.total_errors = 0
        self.recovered_errors = 0
        self.critical_errors = 0
        
        # Mapa de estratégias por tipo de erro
        self.strategies: Dict[str, RecoveryStrategy] = {
            "RateLimitError": RecoveryStrategy.RETRY_EXPONENTIAL,
            "ConnectionError": RecoveryStrategy.RETRY_EXPONENTIAL,
            "TimeoutError": RecoveryStrategy.RETRY_IMMEDIATE,
            "AuthenticationError": RecoveryStrategy.FALLBACK_MODEL,
            "OutOfTokensError": RecoveryStrategy.FALLBACK_MODE,
            "MemoryError": RecoveryStrategy.RESTART_MODULE,
            "PermissionError": RecoveryStrategy.ABORT_GRACEFULLY,
        }

    def classify_error(self, exception: Exception) -> ErrorSeverity:
        """Classifica a severidade baseada no tipo de exceção."""
        exc_name = type(exception).__name__
        
        if exc_name in ["KeyboardInterrupt", "SystemExit"]:
            return ErrorSeverity.FATAL
            
        if exc_name in ["MemoryError", "OSError"]:
            return ErrorSeverity.FATAL
            
        if exc_name in ["AuthenticationError", "PermissionError"]:
            return ErrorSeverity.HIGH
            
        if exc_name in ["RateLimitError", "TimeoutError", "ConnectionError"]:
            return ErrorSeverity.MEDIUM
            
        return ErrorSeverity.LOW

    def get_strategy(self, exception: Exception) -> RecoveryStrategy:
        """Determina a estratégia de recuperação ideal."""
        exc_name = type(exception).__name__
        return self.strategies.get(exc_name, RecoveryStrategy.RETRY_IMMEDIATE)

    def calculate_backoff(self, retry_count: int) -> float:
        """Calcula delay exponencial com jitter."""
        delay = min(self.base_delay * (2 ** retry_count), self.max_delay)
        jitter = random.uniform(0, delay * 0.1)  # 10% de variação
        return delay + jitter

    def handle_error(self, error_ctx: ErrorContext) -> bool:
        """
        Processa o erro e decide se o sistema pode continuar.
        Retorna True se recuperado, False se falha crítica.
        """
        self.total_errors += 1
        self.last_error_time = time.time()
        
        # Atualiza contagem de falhas consecutivas
        if self.last_error_time and (time.time() - self.last_error_time) < 60:
            self.consecutive_failures += 1
        else:
            self.consecutive_failures = 1

        logger.warning(f"Erro detectado [{error_ctx.severity.value}]: {error_ctx.message}")

        # Lógica baseada na severidade
        if error_ctx.severity == ErrorSeverity.FATAL:
            self.critical_errors += 1
            logger.critical("Erro fatal detectado. Iniciando shutdown seguro.")
            return False

        if error_ctx.severity == ErrorSeverity.HIGH:
            if self.consecutive_failures >= 3:
                logger.warning("Múltiplas falhas críticas. Ativando modo degradado.")
                self.is_degraded_mode = True
            return False  # Requer intervenção ou fallback externo

        # Erros médios/baixos: tenta recuperação automática
        strategy = self.get_strategy(error_ctx.original_exception or Exception())
        
        if strategy == RecoveryStrategy.RETRY_EXPONENTIAL:
            delay = self.calculate_backoff(error_ctx.retry_count)
            logger.info(f"Tentativa {error_ctx.retry_count + 1}. Aguardando {delay:.2f}s...")
            time.sleep(delay)
            self.recovered_errors += 1
            return True

        if strategy == RecoveryStrategy.IGNORE:
            logger.debug("Erro ignorado conforme estratégia.")
            self.recovered_errors += 1
            return True

        # Estratégias complexas delegadas ao caller
        return False

    def reset_health(self):
        """Reseta contadores de saúde após sucesso prolongado."""
        self.consecutive_failures = 0
        self.is_degraded_mode = False
        logger.info("Saúde do sistema restaurada.")

    def get_health_status(self) -> dict:
        """Retorna status atual de saúde do agente."""
        health_score = 100 - (self.consecutive_failures * 10) - (self.critical_errors * 20)
        health_score = max(0, min(100, health_score))
        
        return {
            "status": "degraded" if self.is_degraded_mode else "healthy",
            "health_score": health_score,
            "consecutive_failures": self.consecutive_failures,
            "total_errors": self.total_errors,
            "recovery_rate": (self.recovered_errors / max(1, self.total_errors)) * 100
        }


def safe_execute(
    func: Callable, 
    *args, 
    default_return: Any = None, 
    friendly_message: str = "Ocorreu um erro inesperado.",
    **kwargs
) -> Any:
    """
    Decorador/Wrapper para executar funções com segurança.
    Nunca deixa um traceback escapar para o usuário final.
    """
    resilience = ResilienceManager()  # Em produção, seria singleton
    
    try:
        return func(*args, **kwargs)
    
    except Exception as e:
        error_type = type(e).__name__
        severity = resilience.classify_error(e)
        
        ctx = ErrorContext(
            error_type=error_type,
            message=str(e),
            module=func.__module__,
            function=func.__name__,
            severity=severity,
            original_exception=e
        )
        
        # Log técnico detalhado (apenas logs)
        logger.exception(f"Erro interno em {func.__name__}: {e}")
        
        # Comportamento baseado na severidade
        if severity == ErrorSeverity.FATAL:
            raise SystemExit(f"Erro crítico: {friendly_message}")
        
        if severity == ErrorSeverity.HIGH:
            # Retorna mensagem amigável em vez de explodir
            print(f"⚠️  {friendly_message}")
            print(f"   Detalhes: {str(e)}")
            return default_return
            
        # Tenta recuperar para erros menores
        if resilience.handle_error(ctx):
            # Retry simples (em produção, lógica mais complexa)
            try:
                return func(*args, **kwargs)
            except Exception:
                pass
                
        print(f"⚠️  {friendly_message}")
        return default_return
