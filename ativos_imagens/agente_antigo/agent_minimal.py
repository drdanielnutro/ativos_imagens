# ativos_imagens/agent_minimal.py
"""Agente mínimo para teste e debug"""

from google.adk.agents import LlmAgent

# Agente principal - versão mínima sem ferramentas
root_agent = LlmAgent(
    name="root_agent",
    model="gemini-1.5-flash-latest",
    instruction="Você é um assistente de teste. Responda com 'Olá! O agente está funcionando corretamente.'"
)