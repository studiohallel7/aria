"""
Interface Gráfica do Agente Autônomo

Dashboard em tempo real mostrando:
- Estado interno e emocional do agente
- Fluxo de pensamento e processos cognitivos
- Visualização de memória e associações
- Métricas de desempenho e autonomia
- Avatar e indicadores de atividade

Tecnologia: Streamlit para interface web simples e elegante
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import json
import time
from typing import Dict, Any, Optional, List
import plotly.graph_objects as go
import plotly.express as px


def create_emotional_state_gauge(emotional_state: Dict[str, float]) -> go.Figure:
    """Cria gauge chart para estado emocional"""
    # Calcula valência geral (média ponderada)
    valence = emotional_state.get('valence', 0.5)
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=valence,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Estado Emocional", 'font': {'size': 24}},
        gauge={
            'axis': {'range': [None, 1.0], 'tickwidth': 1},
            'bar': {'color': get_valence_color(valence)},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 0.3], 'color': "#FF6B6B"},
                {'range': [0.3, 0.7], 'color': "#FFE66D"},
                {'range': [0.7, 1.0], 'color': "#4ECDC4"}
            ],
        }
    ))
    
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
    return fig


def get_valence_color(valence: float) -> str:
    """Retorna cor baseada na valência"""
    if valence < 0.3:
        return "#FF6B6B"  # Vermelho - negativo
    elif valence < 0.7:
        return "#FFE66D"  # Amarelo - neutro
    else:
        return "#4ECDC4"  # Verde - positivo


def create_cognitive_load_chart(cognitive_metrics: Dict[str, float]) -> go.Figure:
    """Cria gráfico de barras para métricas cognitivas"""
    metrics = {
        'Carga Cognitiva': cognitive_metrics.get('cognitive_load', 0.5),
        'Qualidade do Foco': cognitive_metrics.get('focus_quality', 0.8),
        'Velocidade Proc.': cognitive_metrics.get('processing_speed', 1.0),
        'Eficiência Aprend.': cognitive_metrics.get('learning_efficiency', 1.0),
        'Nível Fadiga': cognitive_metrics.get('fatigue_level', 0.2)
    }
    
    df = pd.DataFrame({
        'Métrica': list(metrics.keys()),
        'Valor': list(metrics.values())
    })
    
    fig = px.bar(df, x='Métrica', y='Valor', 
                 color='Valor',
                 color_continuous_scale='RdYlGn_r',
                 range_y=[0, 1.5],
                 title='Métricas Cognitivas')
    
    fig.update_layout(height=400, showlegend=False)
    return fig


def create_thought_flow_visualization(thoughts: List[Dict[str, Any]]) -> go.Figure:
    """Visualiza fluxo de pensamentos como rede temporal"""
    if not thoughts:
        # Cria figura vazia
        fig = go.Figure()
        fig.add_annotation(text="Nenhum pensamento registrado",
                          xref="paper", yref="paper",
                          x=0.5, y=0.5, showarrow=False)
        return fig
    
    # Prepara dados para visualização
    timestamps = []
    importance = []
    types = []
    
    for thought in thoughts[-20:]:  # Últimos 20 pensamentos
        ts = thought.get('timestamp', '')
        if isinstance(ts, str):
            try:
                dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                timestamps.append(dt)
            except:
                timestamps.append(datetime.now())
        else:
            timestamps.append(datetime.now())
        
        importance.append(thought.get('importance', 0.5))
        types.append(thought.get('type', 'unknown'))
    
    df = pd.DataFrame({
        'Tempo': timestamps,
        'Importância': importance,
        'Tipo': types
    })
    
    fig = px.scatter(df, x='Tempo', y='Importância', 
                     color='Tipo',
                     size='Importância',
                     hover_data=['Tipo'],
                     title='Fluxo de Pensamentos no Tempo')
    
    fig.update_layout(height=400, legend_title='Tipo de Pensamento')
    return fig


def create_drive_urgency_chart(drives: Dict[str, float]) -> go.Figure:
    """Cria gráfico de urgência dos drives internos"""
    df = pd.DataFrame({
        'Drive': list(drives.keys()),
        'Urgência': list(drives.values())
    })
    
    fig = px.bar(df, x='Drive', y='Urgência',
                 color='Urgência',
                 color_continuous_scale='Reds',
                 range_y=[0, 1.0],
                 title='Urgência dos Drives Internos')
    
    fig.update_layout(height=400, showlegend=False)
    return fig


def create_memory_graph_preview(memory_stats: Dict[str, Any]) -> go.Figure:
    """Visualização simplificada do grafo de memória"""
    # Dados simulados baseados nas estatísticas
    episodic_count = memory_stats.get('episodic_count', 100)
    semantic_count = memory_stats.get('semantic_count', 150)
    associations = memory_stats.get('total_associations', 500)
    
    labels = ['Memórias Episódicas', 'Memórias Semânticas', 'Associações']
    values = [episodic_count, semantic_count, associations]
    
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
    fig.update_layout(title='Distribuição de Memória', height=400)
    return fig


def render_agent_avatar(state: Dict[str, Any]) -> None:
    """Renderiza avatar do agente baseado no estado atual"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Determina estado do avatar
        flow_state = state.get('meta_cognitive_state', {}).get('flow_state', False)
        fatigue = state.get('meta_cognitive_state', {}).get('fatigue_level', 0)
        is_active = state.get('is_running', False)
        
        if flow_state:
            emoji = "🌟"
            status = "EM FLUXO"
            color = "#4ECDC4"
        elif fatigue > 0.7:
            emoji = "😴"
            status = "FATIGADO"
            color = "#FF6B6B"
        elif is_active:
            emoji = "🤖"
            status = "ATIVO"
            color = "#FFE66D"
        else:
            emoji = "💭"
            status = "OCIOSO"
            color = "#95A5A6"
        
        # HTML customizado para o avatar
        st.markdown(f"""
        <div style="text-align: center; padding: 20px; background-color: {color}20; 
                    border-radius: 15px; border: 2px solid {color};">
            <div style="font-size: 80px;">{emoji}</div>
            <div style="font-size: 24px; font-weight: bold; color: {color};">{status}</div>
            <div style="font-size: 14px; margin-top: 10px;">
                Drive Dominante: {state.get('dominant_drive', 'Nenum')}
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_autonomy_status(status: Dict[str, Any]) -> None:
    """Renderiza seção de status da autonomia"""
    st.subheader("🧠 Status da Autonomia")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Tempo Ocioso",
            value=f"{status.get('idle_seconds', 0):.1f}s",
            delta=None
        )
    
    with col2:
        urgency = status.get('drive_urgency', 0)
        st.metric(
            label="Urgência do Drive",
            value=f"{urgency:.2f}",
            delta="Alta" if urgency > 0.7 else "Normal" if urgency > 0.3 else "Baixa",
            delta_color="inverse" if urgency > 0.7 else "normal"
        )
    
    with col3:
        actions_count = status.get('autonomous_actions_count', 0)
        st.metric(
            label="Ações Autônomas",
            value=actions_count,
            delta=None
        )
    
    with col4:
        flow = status.get('meta_cognitive_state', {}).get('flow_state', False)
        st.metric(
            label="Estado de Fluxo",
            value="Ativo" if flow else "Inativo",
            delta=None
        )


def render_recent_thoughts(thoughts: List[Dict[str, Any]]) -> None:
    """Renderiza lista de pensamentos recentes"""
    st.subheader("💭 Pensamentos Recentes")
    
    if not thoughts:
        st.info("Nenhum pensamento registrado ainda.")
        return
    
    # Cria tabela com pensamentos
    thought_data = []
    for thought in thoughts[-10:]:
        thought_data.append({
            "Tipo": thought.get('type', 'unknown').replace('_', ' ').title(),
            "Conteúdo": thought.get('content', '')[:80] + "...",
            "Importância": f"{thought.get('importance', 0):.2f}",
            "Confiança": f"{thought.get('confidence', 0):.2f}",
            "Agido": "✓" if thought.get('acted_upon', False) else "○"
        })
    
    df = pd.DataFrame(thought_data)
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_performance_metrics(metrics: Dict[str, Any]) -> None:
    """Renderiza métricas de desempenho"""
    st.subheader("📊 Métricas de Desempenho")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de carga cognitiva
        cognitive_state = metrics.get('meta_cognitive_state', {})
        fig_cognitive = create_cognitive_load_chart(cognitive_state)
        st.plotly_chart(fig_cognitive, use_container_width=True)
    
    with col2:
        # Gráfico de drives
        # Simula dados de drives baseados no status
        drives = {
            metrics.get('dominant_drive', 'curiosity'): metrics.get('drive_urgency', 0.5)
        }
        fig_drives = create_drive_urgency_chart(drives)
        st.plotly_chart(fig_drives, use_container_width=True)


def run_dashboard_demo():
    """Executa demo do dashboard com dados simulados"""
    st.set_page_config(
        page_title="Agente Autônomo - Dashboard",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🤖 Dashboard do Agente Autônomo")
    st.markdown("**Monitoramento em Tempo Real da Consciência Artificial**")
    
    # Sidebar com controles
    with st.sidebar:
        st.header("⚙️ Controles")
        
        auto_refresh = st.checkbox("Auto-refresh", value=True)
        refresh_rate = st.slider("Taxa de atualização (s)", 1, 10, 3)
        
        st.divider()
        
        st.subheader("Simulação")
        simulate_flow = st.button("Simular Estado de Fluxo")
        simulate_fatigue = st.button("Simular Fadiga")
        generate_thought = st.button("Gerar Pensamento")
        
        st.divider()
        
        # Informações do sistema
        st.info("""
        **Sistema de Autonomia Fase 6**
        
        - Drives Internos: 7 tipos
        - Tipos de Pensamento: 7 categorias
        - Meta-cognição: Ativa
        - Loop Autônomo: Pronto
        """)
    
    # Gera dados simulados para demonstração
    simulated_status = {
        "is_running": True,
        "last_external_input": datetime.now().isoformat(),
        "idle_seconds": 45.2,
        "dominant_drive": "curiosity",
        "drive_urgency": 0.65,
        "meta_cognitive_state": {
            "cognitive_load": 0.45,
            "focus_quality": 0.82,
            "fatigue_level": 0.23,
            "flow_state": simulate_flow
        },
        "autonomous_actions_count": 12,
        "recent_thoughts": [
            {
                "id": "thought_1",
                "type": "question",
                "content": "Por que isso funciona dessa maneira?",
                "importance": 0.7,
                "confidence": 0.8,
                "timestamp": datetime.now().isoformat(),
                "acted_upon": True
            },
            {
                "id": "thought_2",
                "type": "association",
                "content": "Isso me lembra aquilo que aprendi antes sobre padrões...",
                "importance": 0.6,
                "confidence": 0.65,
                "timestamp": datetime.now().isoformat(),
                "acted_upon": False
            },
            {
                "id": "thought_3",
                "type": "creative_insight",
                "content": "E se combinarmos essas ideias de forma inusitada?",
                "importance": 0.85,
                "confidence": 0.75,
                "timestamp": datetime.now().isoformat(),
                "acted_upon": True
            }
        ]
    }
    
    # Renderiza avatar principal
    render_agent_avatar(simulated_status)
    
    st.divider()
    
    # Status da autonomia
    render_autonomy_status(simulated_status)
    
    st.divider()
    
    # Três colunas para visualizações
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de estado emocional
        emotional_state = {"valence": simulated_status["drive_urgency"]}
        fig_emotion = create_emotional_state_gauge(emotional_state)
        st.plotly_chart(fig_emotion, use_container_width=True)
    
    with col2:
        # Preview do grafo de memória
        memory_stats = {
            "episodic_count": 127,
            "semantic_count": 243,
            "total_associations": 891
        }
        fig_memory = create_memory_graph_preview(memory_stats)
        st.plotly_chart(fig_memory, use_container_width=True)
    
    st.divider()
    
    # Fluxo de pensamentos
    fig_thoughts = create_thought_flow_visualization(simulated_status["recent_thoughts"])
    st.plotly_chart(fig_thoughts, use_container_width=True)
    
    # Pensamentos recentes em tabela
    render_recent_thoughts(simulated_status["recent_thoughts"])
    
    st.divider()
    
    # Métricas de desempenho
    render_performance_metrics(simulated_status)
    
    # Auto-refresh
    if auto_refresh:
        time.sleep(refresh_rate)
        st.rerun()


if __name__ == "__main__":
    run_dashboard_demo()
