"""
Este arquivo __init__.py expõe o root_agent principal para que o Google ADK
possa descobri-lo e carregá-lo.

Ele tenta importar o `root_agent` do sistema multi-agente (preferencial)
e, se falhar, tenta carregar o agente legado como um fallback.
"""

try:
    # Abordagem primária: carregar o orquestrador do sistema multi-agente
    from .agentes_ativos.orchestrator import root_agent
except ImportError:
    try:
        # Fallback: carregar o agente do sistema antigo se o novo falhar
        from .agente_antigo.agent import root_agent
    except ImportError:
        # Se ambos falharem, o ADK não encontrará um agente para carregar,
        # o que é o comportamento esperado se nenhum agente estiver configurado.
        root_agent = None
