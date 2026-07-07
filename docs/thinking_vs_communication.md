# Separação Pensamento vs Comunicação

## Arquitetura Cognitiva

O agente possui **separação estrita** entre:

### 1. Pensamento Interno (`thinking.py`)
- **NÃO visível ao usuário**
- Processo de raciocínio em múltiplos passos
- Avaliação de riscos interna
- Seleção de estratégias
- Auto-crítica e validação

**Exemplo de fluxo interno:**
```
[Passo 0] Questão: Liste os arquivos do diretório atual
[Passo 1] Analisando intenção do usuário...
[Passo 2] Verificando restrições de segurança...
[Passo 3] Ação é segura (leitura apenas)
[Passo 4] Decisão: executar comando 'ls'
```

### 2. Comunicação Externa (`communication.py`)
- **Visível ao usuário**
- Tradução do pensamento para linguagem natural
- Decisão de QUANDO falar (alguns pensamentos são silenciosos)
- Adaptação de tom (neutral, friendly, professional, urgent)
- Histórico de conversas

**Exemplo de saída:**
```
Tom: neutral
Conteúdo: Ação executada: execute_task
          Devo executar a tarefa solicitada com cautela.
```

## Por que separar?

1. **Privacidade cognitiva**: Nem todo pensamento deve ser verbalizado
2. **Eficiência**: Pensamentos internos podem ser mais técnicos/diretos
3. **Segurança**: Avaliação de risco ocorre antes da fala
4. **Flexibilidade**: Mesmo pensamento pode gerar comunicações diferentes dependendo do contexto
5. **Debug**: Desenvolvedores podem ver o pensamento completo, usuários apenas a resposta

## Fluxo Completo

```
┌─────────────────┐
│   Usuário fala  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  ThinkingEngine │ ← NÃO visível
│  (Pensamento)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Decisão:      │
│   Falar ou não? │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
   Sim       Não
    │         │
    ▼         ▼
┌─────────┐  ┌──────────┐
│Communication│ │Silêncio  │
│  Engine     │ │(log only)│
└─────────┘  └──────────┘
    │
    ▼
┌─────────────────┐
│   Resposta ao   │
│    Usuário      │ ← Visível
└─────────────────┘
```

## Implementação

Ver `core/cognition/communication.py` para detalhes da `CommunicationEngine` e `CognitiveLoop`.

Teste rápido:
```bash
python -m core.cognition.communication
```
