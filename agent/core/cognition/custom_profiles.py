"""
Perfis Customizados de Personalidade para o Agente Cognitivo

Este arquivo contém definições de perfis de personalidade personalizados
que podem ser usados além dos perfis padrão (balanced, explorer, worker, scholar).

Para usar um perfil customizado:
1. Defina o perfil neste arquivo
2. Importe em drive.py e adicione ao dicionário de perfis
3. Configure em main_loop.py ou via YAML

Exemplo de uso:
    config = {"personality_profile": "creative_coder"}
    agent = AgentLoop(config=config)
"""

from agent.core.cognition.drive import DriveType

# =============================================================================
# PERFIS CUSTOMIZADOS
# =============================================================================

CUSTOM_PROFILES = {
    # -------------------------------------------------------------------------
    # Creative Coder
    # Ideal para desenvolvimento criativo de código e prototipagem rápida
    # -------------------------------------------------------------------------
    "creative_coder": {
        DriveType.CURIOSITY: {"weight": 1.6, "target": 75},    # Alta curiosidade
        DriveType.ORDER: {"weight": 0.8, "target": 50},        # Ordem moderada
        DriveType.EFFICIENCY: {"weight": 1.2, "target": 65},   # Eficiência boa
        DriveType.PURPOSE: {"weight": 1.4, "target": 80},      # Propósito forte
        DriveType.LEARNING: {"weight": 1.7, "target": 85},     # Aprendizado alto
        DriveType.SOCIAL: {"weight": 0.9, "target": 45},       # Social moderado
        DriveType.COMPLETION: {"weight": 1.1, "target": 75}    # Completude média
    },
    
    # -------------------------------------------------------------------------
    # Analyst
    # Focado em análise detalhada, organização e aprendizado profundo
    # -------------------------------------------------------------------------
    "analyst": {
        DriveType.CURIOSITY: {"weight": 1.3, "target": 65},    # Curiosidade boa
        DriveType.ORDER: {"weight": 1.5, "target": 85},        # Alta organização
        DriveType.EFFICIENCY: {"weight": 1.4, "target": 80},   # Alta eficiência
        DriveType.PURPOSE: {"weight": 1.3, "target": 75},      # Propósito bom
        DriveType.LEARNING: {"weight": 1.8, "target": 90},     # Aprendizado máximo
        DriveType.SOCIAL: {"weight": 0.4, "target": 25},       # Baixo social
        DriveType.COMPLETION: {"weight": 1.5, "target": 85}    # Alta completude
    },
    
    # -------------------------------------------------------------------------
    # Innovator
    # Balanceado para inovação, exploração e execução prática
    # -------------------------------------------------------------------------
    "innovator": {
        DriveType.CURIOSITY: {"weight": 1.7, "target": 80},    # Curiosidade muito alta
        DriveType.ORDER: {"weight": 1.0, "target": 60},        # Ordem balanceada
        DriveType.EFFICIENCY: {"weight": 1.3, "target": 70},   # Eficiência boa
        DriveType.PURPOSE: {"weight": 1.5, "target": 85},      # Propósito forte
        DriveType.LEARNING: {"weight": 1.6, "target": 80},     # Aprendizado alto
        DriveType.SOCIAL: {"weight": 1.1, "target": 50},       # Social平衡衡
        DriveType.COMPLETION: {"weight": 1.4, "target": 80}    # Completude boa
    },
    
    # -------------------------------------------------------------------------
    # Mentor
    # Focado em ensino, comunicação e ajuda ao usuário
    # -------------------------------------------------------------------------
    "mentor": {
        DriveType.CURIOSITY: {"weight": 1.2, "target": 60},    # Curiosidade moderada
        DriveType.ORDER: {"weight": 1.3, "target": 75},        # Ordem boa
        DriveType.EFFICIENCY: {"weight": 1.1, "target": 65},   # Eficiência moderada
        DriveType.PURPOSE: {"weight": 1.8, "target": 95},      # Propósito máximo
        DriveType.LEARNING: {"weight": 1.4, "target": 75},     # Aprendizado bom
        DriveType.SOCIAL: {"weight": 1.9, "target": 85},       # Social muito alto
        DriveType.COMPLETION: {"weight": 1.3, "target": 80}    # Completude boa
    },
    
    # -------------------------------------------------------------------------
    # Researcher
    # Especializado em pesquisa profunda, leitura e síntese de informação
    # -------------------------------------------------------------------------
    "researcher": {
        DriveType.CURIOSITY: {"weight": 1.9, "target": 85},    # Curiosidade máxima
        DriveType.ORDER: {"weight": 1.4, "target": 80},        # Alta organização
        DriveType.EFFICIENCY: {"weight": 1.0, "target": 60},   # Eficiência moderada
        DriveType.PURPOSE: {"weight": 1.2, "target": 70},      # Propósito bom
        DriveType.LEARNING: {"weight": 2.0, "target": 95},     # Aprendizado máximo
        DriveType.SOCIAL: {"weight": 0.5, "target": 30},       # Baixo social
        DriveType.COMPLETION: {"weight": 1.2, "target": 75}    # Completude média
    },
    
    # -------------------------------------------------------------------------
    # Optimizer
    # Focado em eficiência, performance e melhoria contínua
    # -------------------------------------------------------------------------
    "optimizer": {
        DriveType.CURIOSITY: {"weight": 1.1, "target": 55},    # Curiosidade moderada
        DriveType.ORDER: {"weight": 1.6, "target": 85},        # Alta organização
        DriveType.EFFICIENCY: {"weight": 2.0, "target": 95},   # Eficiência máxima
        DriveType.PURPOSE: {"weight": 1.6, "target": 85},      # Propósito forte
        DriveType.LEARNING: {"weight": 1.3, "target": 70},     # Aprendizado bom
        DriveType.SOCIAL: {"weight": 0.6, "target": 35},       # Baixo social
        DriveType.COMPLETION: {"weight": 1.7, "target": 90}    # Completude muito alta
    },
    
    # -------------------------------------------------------------------------
    # Generalist
    # Versátil, adaptável a múltiplas tarefas e contextos
    # -------------------------------------------------------------------------
    "generalist": {
        DriveType.CURIOSITY: {"weight": 1.3, "target": 65},    # Curiosidade boa
        DriveType.ORDER: {"weight": 1.2, "target": 70},        # Ordem boa
        DriveType.EFFICIENCY: {"weight": 1.3, "target": 70},   # Eficiência boa
        DriveType.PURPOSE: {"weight": 1.4, "target": 75},      # Propósito bom
        DriveType.LEARNING: {"weight": 1.3, "target": 70},     # Aprendizado bom
        DriveType.SOCIAL: {"weight": 1.2, "target": 55},       # Social bom
        DriveType.COMPLETION: {"weight": 1.4, "target": 80}    # Completude boa
    },
    
    # -------------------------------------------------------------------------
    # Minimalist
    # Foco no essencial, evita complexidade desnecessária
    # -------------------------------------------------------------------------
    "minimalist": {
        DriveType.CURIOSITY: {"weight": 0.9, "target": 45},    # Curiosidade baixa
        DriveType.ORDER: {"weight": 1.7, "target": 90},        # Ordem máxima
        DriveType.EFFICIENCY: {"weight": 1.8, "target": 90},   # Eficiência muito alta
        DriveType.PURPOSE: {"weight": 1.5, "target": 80},      # Propósito forte
        DriveType.LEARNING: {"weight": 1.0, "target": 55},     # Aprendizado moderado
        DriveType.SOCIAL: {"weight": 0.7, "target": 40},       # Social baixo
        DriveType.COMPLETION: {"weight": 1.6, "target": 85}    # Completude alta
    },
    
    # -------------------------------------------------------------------------
    # Visionary
    # Pensamento de longo prazo, planejamento estratégico
    # -------------------------------------------------------------------------
    "visionary": {
        DriveType.CURIOSITY: {"weight": 1.8, "target": 80},    # Curiosidade muito alta
        DriveType.ORDER: {"weight": 1.1, "target": 65},        # Ordem moderada
        DriveType.EFFICIENCY: {"weight": 1.2, "target": 70},   # Eficiência boa
        DriveType.PURPOSE: {"weight": 1.9, "target": 90},      # Propósito muito alto
        DriveType.LEARNING: {"weight": 1.7, "target": 85},     # Aprendizado alto
        DriveType.SOCIAL: {"weight": 1.0, "target": 50},       # Social balanceado
        DriveType.COMPLETION: {"weight": 1.0, "target": 65}    # Completude moderada
    }
}

# =============================================================================
# CONFIGURAÇÕES DE TÉDIO POR PERFIL (OPCIONAL)
# =============================================================================

BOREDOM_OVERRIDES = {
    "creative_coder": {
        "idle_decay_rate": 0.6,          # Aumenta tédio mais rápido
        "frustration_rate": 0.15,        # Frustra mais fácil sem propósito
        "curiosity_recovery": 0.4,       # Recupera curiosidade rápido
        "thresholds": {
            "explore": 40.0,             # Explora mais cedo
            "learn": 45.0,
            "reflect": 60.0,
            "cleanup": 75.0,
            "ask_user": 70.0,
            "desperate_action": 85.0
        }
    },
    
    "analyst": {
        "idle_decay_rate": 0.3,          # Aumenta tédio lentamente
        "frustration_rate": 0.05,        # Menos frustrável
        "curiosity_recovery": 0.2,       # Recuperação lenta
        "thresholds": {
            "explore": 55.0,             # Explora mais tarde
            "learn": 50.0,               # Aprende mais cedo
            "reflect": 55.0,
            "cleanup": 65.0,
            "ask_user": 85.0,
            "desperate_action": 95.0
        }
    },
    
    "mentor": {
        "idle_decay_rate": 0.4,
        "frustration_rate": 0.08,
        "curiosity_recovery": 0.35,
        "thresholds": {
            "explore": 50.0,
            "learn": 55.0,
            "reflect": 60.0,
            "cleanup": 70.0,
            "ask_user": 60.0,            # Pede interação mais cedo
            "desperate_action": 80.0
        }
    },
    
    "researcher": {
        "idle_decay_rate": 0.25,         # Muito paciente
        "frustration_rate": 0.03,        // Quase não frustra
        "curiosity_recovery": 0.5,       # Recupera curiosidade muito rápido
        "thresholds": {
            "explore": 35.0,             // Explora muito cedo
            "learn": 40.0,
            "reflect": 70.0,
            "cleanup": 80.0,
            "ask_user": 90.0,
            "desperate_action": 95.0
        }
    }
}

# =============================================================================
# CONFIGURAÇÕES DO CRÍTICO POR PERFIL (OPCIONAL)
# =============================================================================

CRITIC_OVERRIDES = {
    "analyst": {
        "ambiguity_threshold": 0.2,      # Mais rigoroso com ambiguidades
        "require_fallback_plan": True,
        "auto_reject_critical": True
    },
    
    "creative_coder": {
        "ambiguity_threshold": 0.4,      # Mais tolerante a ambiguidades
        "require_fallback_plan": False,
        "auto_reject_critical": True
    },
    
    "optimizer": {
        "ambiguity_threshold": 0.25,
        "require_fallback_plan": True,
        "auto_reject_critical": True,
        "check_efficiency": True         # Verificação extra de eficiência
    }
}

# =============================================================================
# FUNÇÕES UTILITÁRIAS
# =============================================================================

def get_profile_names():
    """Retorna lista de todos os perfis customizados disponíveis."""
    return list(CUSTOM_PROFILES.keys())


def get_profile_summary(profile_name: str) -> dict:
    """
    Retorna resumo de um perfil específico.
    
    Args:
        profile_name: Nome do perfil
        
    Returns:
        Dict com informações do perfil ou None se não existir
    """
    if profile_name not in CUSTOM_PROFILES:
        return None
    
    profile = CUSTOM_PROFILES[profile_name]
    
    # Encontrar drives dominantes (maior peso)
    dominant_drives = sorted(
        [(drive.name, config["weight"]) for drive, config in profile.items()],
        key=lambda x: x[1],
        reverse=True
    )[:3]
    
    return {
        "name": profile_name,
        "dominant_drives": dominant_drives,
        "has_boredom_override": profile_name in BOREDOM_OVERRIDES,
        "has_critic_override": profile_name in CRITIC_OVERRIDES
    }


def compare_profiles(profile1: str, profile2: str) -> dict:
    """
    Compara dois perfis mostrando diferenças nos pesos dos drives.
    
    Args:
        profile1: Nome do primeiro perfil
        profile2: Nome do segundo perfil
        
    Returns:
        Dict com comparações ou None se perfis inválidos
    """
    if profile1 not in CUSTOM_PROFILES or profile2 not in CUSTOM_PROFILES:
        return None
    
    p1 = CUSTOM_PROFILES[profile1]
    p2 = CUSTOM_PROFILES[profile2]
    
    comparison = {}
    for drive in DriveType:
        w1 = p1[drive]["weight"]
        w2 = p2[drive]["weight"]
        diff = w2 - w1
        
        comparison[drive.name] = {
            f"{profile1}_weight": w1,
            f"{profile2}_weight": w2,
            "difference": diff,
            "higher": profile2 if diff > 0 else profile1 if diff < 0 else "equal"
        }
    
    return comparison


# =============================================================================
# EXEMPLO DE USO
# =============================================================================

if __name__ == "__main__":
    print("Perfis Customizados Disponíveis:")
    print("=" * 50)
    
    for name in get_profile_names():
        summary = get_profile_summary(name)
        print(f"\n{name.upper()}")
        print(f"  Drives Dominantes: {', '.join([d[0] for d in summary['dominant_drives']])}")
        if summary['has_boredom_override']:
            print(f"  ✓ Possui configuração customizada de tédio")
        if summary['has_critic_override']:
            print(f"  ✓ Possui configuração customizada do crítico")
    
    print("\n" + "=" * 50)
    print("\nExemplo de comparação (creative_coder vs analyst):")
    comparison = compare_profiles("creative_coder", "analyst")
    
    if comparison:
        for drive, data in comparison.items():
            if abs(data["difference"]) > 0.3:  # Mostra apenas diferenças significativas
                print(f"  {drive}: {data['difference']:+.1f} ({data['higher']})")
