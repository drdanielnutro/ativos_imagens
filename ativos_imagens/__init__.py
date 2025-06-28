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
        from . import agent  # noqa: F401
    else:
        # ADK não disponível – expõe apenas submódulos tools.
        pass
except ImportError:
    # Qualquer erro durante a checagem: ignora importação do agente.
    pass