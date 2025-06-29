"""
Sistema antigo de agente único (arquivado)
"""

# Expor o root_agent do sistema antigo caso seja necessário
try:
    from .agent import root_agent
except ImportError:
    root_agent = None

__all__ = ['root_agent']