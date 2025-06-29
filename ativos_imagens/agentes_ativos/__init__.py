"""
Agentes ativos do sistema multi-agente
"""

# Expor o root_agent para que o ADK possa encontrá-lo
from .orchestrator import root_agent

__all__ = ['root_agent']