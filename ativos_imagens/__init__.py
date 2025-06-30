"""
Este arquivo __init__.py expõe o root_agent principal para que o Google ADK
possa descobri-lo e carregá-lo.

Agora usa o agente simplificado único que segue a mesma lógica do gerador manual.
"""

try:
    # Carregar o agente simplificado
    from .agente_antigo.agent import root_agent
    print("INFO (__init__.py): root_agent carregado com sucesso de agente_antigo/agent.py")
except ImportError as e:
    # Se falhar, o ADK não encontrará um agente para carregar
    print(f"ERRO (__init__.py): Não foi possível carregar o agente: {e}")
    root_agent = None
