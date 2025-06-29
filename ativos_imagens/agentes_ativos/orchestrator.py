"""
Agente Orquestrador Principal - Sistema Multi-Agente de Produção de Ativos
"""

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools import FunctionTool
import datetime
import os

# Importar os agentes especializados (agora no mesmo diretório)
try:
    from .asset_validator import asset_validator_agent
    from .asset_creator import asset_creator_agent
    agents_available = True
except ImportError:
    print("Aviso: Agentes especializados não disponíveis.")
    agents_available = False

# Importar o AssetManager para funções gerais
try:
    from ..tools.asset_manager import AssetManager
    asset_manager_available = True
except ImportError:
    asset_manager_available = False
    print("Aviso: AssetManager não disponível.")


def get_system_overview() -> str:
    """
    Fornece uma visão geral do sistema de produção de ativos.
    
    Returns:
        str: Descrição do sistema e capacidades
    """
    now = datetime.datetime.now()
    return f"""📊 **Sistema de Produção de Ativos - Visão Geral**
{now.strftime("%d/%m/%Y %H:%M:%S")}

🏗️ **Arquitetura:** Sistema Multi-Agente (SMA)

👥 **Agentes Especializados:**

1. **🔍 Validador de Ativos** (asset_validator)
   - Escaneia estrutura do projeto
   - Valida integridade de arquivos
   - Gera relatórios de progresso
   - Identifica prioridades
   - Sincroniza checklist

2. **🛠️ Criador de Ativos** (asset_creator)
   - Gera efeitos sonoros MP3
   - Cria animações Lottie
   - Produz arquivos SVG
   - Anima o mascote

📦 **Categorias de Ativos:**
- 🎵 SFX: 9 efeitos sonoros
- 🦸 MAS: 15 assets do mascote
- 🎨 UI: 10 elementos de interface
- 🔄 LOAD: 6 animações de carregamento
- 🏆 ACH: 7 elementos de conquistas
- 🎯 FBK: 4 feedbacks interativos
- 🎮 ICO: 6 ícones de navegação

💡 **Como usar:**
- Para validar: "Escaneie o projeto e mostre o status"
- Para criar: "Crie o ativo SFX-01"
- Para relatórios: "Gere um relatório para desenvolvedores"
- Para prioridades: "Quais ativos devo criar primeiro?"
"""


def get_quick_status() -> str:
    """
    Retorna um status rápido do projeto.
    
    Returns:
        str: Status resumido com métricas principais
    """
    if not asset_manager_available:
        return "❌ AssetManager não disponível para obter status."
    
    try:
        manager = AssetManager()
        manager.load_asset_inventory()
        manager.load_checklist_status()
        
        total = len(manager.asset_specs)
        completed = sum(1 for status in manager.checklist_status.values() 
                       if status.get('completed'))
        
        # Contar por tipo
        types_count = {}
        for spec in manager.asset_specs.values():
            asset_type = spec.get('type', 'unknown')
            types_count[asset_type] = types_count.get(asset_type, 0) + 1
        
        return f"""⚡ **Status Rápido do Projeto**

📊 **Progresso Geral:** {completed}/{total} ({completed/total*100:.1f}%)

📈 **Por Tipo:**
- 🎵 Áudio: {types_count.get('audio', 0)} ativos
- 🎬 Lottie: {types_count.get('lottie_programmatic', 0) + types_count.get('lottie_mascote', 0)} ativos
- 🎨 SVG: {types_count.get('svg', 0)} ativos
- 🖼️ PNG: {types_count.get('png_mascote', 0) + types_count.get('png_generico', 0)} ativos

💡 **Próximos Passos:**
- Use o validador para escaneamento completo
- Use o criador para gerar ativos específicos
"""
        
    except Exception as e:
        return f"❌ Erro ao obter status: {str(e)}"


# Criar o agente orquestrador principal
if agents_available:
    root_agent = LlmAgent(
        name="root_agent",
        model="gemini-2.5-pro",
        description="Orquestrador principal do sistema de produção de ativos digitais",
        instruction="""Você é o Orquestrador Principal de um sistema multi-agente para produção de assets digitais.

Você coordena dois agentes especializados:

1. **🔍 Validador de Ativos** (asset_validator)
   - Use para: escanear projeto, verificar status, gerar relatórios, identificar prioridades
   - Comandos: scan_project_structure, generate_progress_report, identify_priorities
   
2. **🛠️ Criador de Ativos** (asset_creator)
   - Use para: criar qualquer ativo específico (áudio, Lottie, SVG, mascote)
   - Comandos: forneça o ID do ativo (ex: "SFX-01", "LOAD-01")

**Fluxo de Trabalho Recomendado:**
1. Primeiro, use o validador para entender o estado atual
2. Identifique prioridades com o validador
3. Delegue criação de ativos específicos ao criador
4. Valide progresso periodicamente

**Princípios de Delegação:**
- SEMPRE delegue tarefas específicas aos agentes especializados
- NUNCA tente executar tarefas de criação ou validação diretamente
- Sintetize as respostas dos agentes em uma resposta coerente
- Mantenha o usuário informado sobre o progresso

**Exemplos de Uso:**
- "Escaneie o projeto" → Delegue ao validador
- "Crie o ativo SFX-01" → Delegue ao criador
- "Quais ativos faltam?" → Delegue ao validador
- "Gere relatório para gerentes" → Delegue ao validador

Use suas ferramentas diretas apenas para informações gerais do sistema.""",
        tools=[
            AgentTool(asset_validator_agent),
            AgentTool(asset_creator_agent),
            FunctionTool(get_system_overview),
            FunctionTool(get_quick_status)
        ]
    )
    print("✅ Sistema Multi-Agente criado com sucesso!")
else:
    # Fallback para agente único
    print("⚠️ Modo fallback: criando agente único sem delegação")
    root_agent = LlmAgent(
        name="root_agent",
        model="gemini-1.5-flash-latest",
        instruction="Assistente de produção de assets (modo limitado - agentes especializados não disponíveis)",
        tools=[
            FunctionTool(get_system_overview),
            FunctionTool(get_quick_status)
        ]
    )