# ativos_imagens/__init__.py
# Importa o agente principal apenas se o Google ADK estiver disponível.
# Isso evita erros em ambientes onde as dependências de execução do ADK
# não estão instaladas (por exemplo, durante testes unitários de partes
# que não precisam do ADK).

try:
    import importlib
    import pkg_resources
    # Tenta localizar o módulo google.adk sem importá-lo totalmente
    if importlib.util.find_spec("google.adk") is not None:
        # Tenta importar o novo orquestrador multi-agente da pasta agentes_ativos
        try:
            from .agentes_ativos import orchestrator  # noqa: F401
            from .agentes_ativos.orchestrator import root_agent  # noqa: F401
        except ImportError:
            # Se falhar, tenta o agente único anterior da pasta agente_antigo
            try:
                from .agente_antigo import agent  # noqa: F401
                from .agente_antigo.agent import root_agent  # noqa: F401
            except ImportError:
                # Não conseguiu importar nenhum agente
                pass
    else:
        # ADK não disponível – expõe apenas submódulos tools.
        pass
except ImportError:
    # Qualquer erro durante a checagem: ignora importação do agente.
    pass