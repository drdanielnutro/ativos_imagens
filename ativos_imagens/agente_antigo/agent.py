# ativos_imagens/agente_antigo/agent.py
"""
Agente de Produção de Ativos Digitais - Versão Simplificada
Implementa a mesma lógica do gerador_manual.py mas com interface ADK
"""

# Carregamento automático de variáveis de ambiente
from dotenv import load_dotenv
load_dotenv()

# Importações do ADK
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
import os
import sys
from pathlib import Path
from typing import Optional, Dict

# Adicionar o diretório raiz ao path (igual ao gerador manual)
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Importar AssetManager
from ativos_imagens.tools.asset_manager import AssetManager

# Importar ferramentas de geração
from ativos_imagens.tools.image_generator import ImageGenerator
from ativos_imagens.tools.lottie_programmatic import LottieProgrammaticGenerator
from ativos_imagens.tools.mascot_animator import MascotAnimator
from ativos_imagens.tools.svg_generator import SVGGenerator
from ativos_imagens.tools.audio_generator import AudioEffectGenerator

# Mapeamento de ferramentas (idêntico ao gerador_manual.py)
GENERATOR_MAP = {
    "image_generator": ImageGenerator,
    "lottie_programmatic": LottieProgrammaticGenerator,
    "mascot_animator": MascotAnimator,
    "svg_generator": SVGGenerator,
    "audio_generator": AudioEffectGenerator,
}

METHOD_MAP = {
    "image_generator": "generate_png",
    "lottie_programmatic": "generate_animation",
    "mascot_animator": "create_mascot_animation",
    "svg_generator": "generate_svg",
    "audio_generator": "generate_sound_effect",
}


def create_asset(asset_id: str) -> str:
    """
    Cria um ativo baseado em seu ID usando a mesma lógica do gerador_manual.py
    
    Args:
        asset_id: ID do ativo (ex: 'SFX-01', 'LOAD-01', 'UI-01')
        
    Returns:
        str: Mensagem de status da criação
    """
    try:
        # Inicializar AssetManager
        asset_manager = AssetManager(project_root=str(project_root))
        asset_manager.load_specifications()
        asset_manager.load_checklist_status()
        
        # Obter especificação do ativo
        spec = asset_manager.get_specification(asset_id)
        if not spec:
            return f"❌ Erro: Especificação para o ativo '{asset_id}' não encontrada."
        
        # Extrair ferramenta e parâmetros
        tool_name = spec.get("tool")
        params = spec.get("params", {})
        
        # Obter caminho de saída
        output_path_obj = asset_manager.get_asset_path(asset_id)
        if not output_path_obj:
            return f"❌ Erro: Não foi possível determinar o caminho de saída para '{asset_id}'."
        
        # Criar diretórios se necessário
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)
        output_path = str(output_path_obj)
        
        # Ajuste especial para mascot_animator (força extensão .webp)
        if tool_name == "mascot_animator":
            output_path = str(Path(output_path).with_suffix(".webp"))
        
        # Obter classe geradora
        generator_class = GENERATOR_MAP.get(tool_name)
        if not generator_class:
            return f"❌ Erro: Ferramenta '{tool_name}' não reconhecida."
        
        # Instanciar gerador
        if tool_name in ["svg_generator", "lottie_programmatic"]:
            generator = generator_class(output_dir=str(output_path_obj.parent))
        else:
            generator = generator_class()
        
        # Obter método de geração
        generation_method_name = METHOD_MAP.get(tool_name)
        generation_method = getattr(generator, generation_method_name)
        
        # Adicionar parâmetros derivados (igual ao gerador manual)
        if tool_name == "audio_generator":
            params['output_dir'] = str(output_path_obj.parent)
        elif tool_name == "image_generator":
            params['output_path'] = output_path
        elif tool_name == "mascot_animator":
            params['output_path'] = output_path
        
        # Executar geração
        generation_method(**params)
        
        # Atualizar checklist
        asset_manager.update_checklist_status(asset_id, 'completed')
        
        # Obter informações do arquivo gerado
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path) / 1024
            return f"""✅ Ativo criado com sucesso!

🆔 **ID:** {asset_id}
📁 **Arquivo:** {output_path_obj.name}
📂 **Local:** {output_path}
📊 **Tamanho:** {file_size:.1f} KB
🛠️ **Ferramenta:** {tool_name}

✨ **Status:** Checklist atualizado para concluído"""
        else:
            return f"""✅ Ativo '{asset_id}' processado com sucesso!

🆔 **ID:** {asset_id}
🛠️ **Ferramenta:** {tool_name}

✨ **Status:** Checklist atualizado para concluído"""
        
    except Exception as e:
        # Tentar atualizar status de erro
        try:
            asset_manager.update_checklist_status(asset_id, 'error')
        except:
            pass
        
        import traceback
        error_details = traceback.format_exc()
        return f"""❌ Erro ao gerar '{asset_id}'

**Erro:** {str(e)}

**Detalhes:**
```
{error_details}
```"""


def check_inventory() -> str:
    """
    Verifica o inventário de ativos e retorna um resumo do status
    
    Returns:
        str: Relatório do inventário com estatísticas
    """
    try:
        asset_manager = AssetManager(project_root=str(project_root))
        asset_manager.load_specifications()
        asset_manager.load_checklist_status()
        
        # Contar ativos por status
        total = len(asset_manager.asset_specs)
        completed = sum(1 for status in asset_manager.checklist_status.values() 
                       if status.get('completed'))
        pending = total - completed
        
        # Agrupar por ferramenta
        by_tool = {}
        for asset_id, spec in asset_manager.asset_specs.items():
            tool = spec.get('tool', 'unknown')
            if tool not in by_tool:
                by_tool[tool] = {'total': 0, 'completed': 0, 'pending': []}
            
            by_tool[tool]['total'] += 1
            if asset_manager.checklist_status.get(asset_id, {}).get('completed'):
                by_tool[tool]['completed'] += 1
            else:
                by_tool[tool]['pending'].append(asset_id)
        
        # Construir relatório
        report = f"""📊 **Inventário de Ativos - Status Geral**

📈 **Resumo:**
- Total de ativos: {total}
- Ativos criados: {completed} ({completed/total*100:.1f}%)
- Ativos pendentes: {pending} ({pending/total*100:.1f}%)

🛠️ **Status por Ferramenta:**
"""
        
        # Mapear nomes amigáveis
        tool_names = {
            'audio_generator': '🎵 Áudio (MP3)',
            'image_generator': '🖼️ Imagens (PNG)',
            'lottie_programmatic': '🎬 Animações Lottie',
            'mascot_animator': '🦸 Animações do Mascote',
            'svg_generator': '🎨 Vetores (SVG)'
        }
        
        for tool, stats in sorted(by_tool.items()):
            friendly_name = tool_names.get(tool, tool)
            report += f"\n**{friendly_name}:**\n"
            report += f"  - Total: {stats['total']}\n"
            report += f"  - Criados: {stats['completed']}\n"
            
            if stats['pending']:
                report += f"  - Pendentes: {', '.join(stats['pending'][:5])}"
                if len(stats['pending']) > 5:
                    report += f" e mais {len(stats['pending']) - 5}"
                report += "\n"
        
        report += "\n💡 **Como usar:**\n"
        report += "- Para criar um ativo: `create_asset('SFX-01')`\n"
        report += "- Para ver detalhes: `get_asset_details('UI-03')`\n"
        report += "- Para criar vários: liste os IDs separadamente"
        
        return report
        
    except Exception as e:
        return f"❌ Erro ao verificar inventário: {str(e)}"


def get_asset_details(asset_id: str) -> str:
    """
    Retorna detalhes sobre um ativo específico
    
    Args:
        asset_id: ID do ativo para consultar
        
    Returns:
        str: Detalhes do ativo ou mensagem de erro
    """
    try:
        asset_manager = AssetManager(project_root=str(project_root))
        asset_manager.load_specifications()
        asset_manager.load_checklist_status()
        
        spec = asset_manager.get_specification(asset_id)
        if not spec:
            return f"❌ Ativo '{asset_id}' não encontrado no inventário."
        
        # Obter status
        status_info = asset_manager.checklist_status.get(asset_id, {})
        is_completed = status_info.get('completed', False)
        
        # Obter caminho
        asset_path = asset_manager.get_asset_path(asset_id)
        
        # Construir resposta
        details = f"""📋 **Detalhes do Ativo: {asset_id}**

🛠️ **Ferramenta:** {spec.get('tool')}
📊 **Status:** {'✅ Criado' if is_completed else '⏳ Pendente'}
"""
        
        if asset_path:
            details += f"📁 **Arquivo:** {asset_path.name}\n"
            details += f"📂 **Caminho:** {asset_path}\n"
            
            if is_completed and asset_path.exists():
                file_size = asset_path.stat().st_size / 1024
                details += f"💾 **Tamanho:** {file_size:.1f} KB\n"
        
        # Mostrar parâmetros de forma legível
        params = spec.get('params', {})
        if params:
            details += "\n**📝 Parâmetros de Geração:**\n"
            for key, value in params.items():
                if isinstance(value, dict):
                    details += f"  - **{key}:**\n"
                    for sub_key, sub_value in value.items():
                        details += f"    - {sub_key}: {sub_value}\n"
                else:
                    details += f"  - **{key}:** {value}\n"
        
        return details
        
    except Exception as e:
        return f"❌ Erro ao obter detalhes: {str(e)}"


def get_project_status() -> str:
    """
    Retorna o status geral do projeto de geração de ativos
    
    Returns:
        str: Status formatado do projeto
    """
    return """🚀 **Sistema de Produção de Ativos - Professor Virtual**

**Versão:** Agente Único Simplificado (v2.0)
**Arquitetura:** Agente único com ferramentas diretas

**🛠️ Ferramentas Disponíveis:**
- 🎵 **audio_generator** - Gera efeitos sonoros MP3
- 🖼️ **image_generator** - Gera imagens PNG (mascote e genéricas)
- 🎬 **lottie_programmatic** - Gera animações Lottie programáticas
- 🦸 **mascot_animator** - Anima o mascote (PNG → WebP/Lottie)
- 🎨 **svg_generator** - Gera vetores SVG

**📊 Fonte de Dados:**
- Especificações: `docs/definicoes/geracao_de_ativos.md`
- Checklist: `docs/definicoes/checklist_ativos_criados.md`

**💡 Comandos Principais:**
- `check_inventory()` - Ver status de todos os ativos
- `create_asset('ID')` - Criar um ativo específico
- `get_asset_details('ID')` - Ver detalhes de um ativo

**🎯 Objetivo:**
Gerar todos os 68 ativos digitais para o app educacional
destinado a crianças brasileiras de 7-11 anos."""


# Criar o agente principal
try:
    root_agent = LlmAgent(
        name="root_agent",
        model="gemini-2.5-pro",
        instruction="""Você é o Assistente de Produção de Ativos Digitais do Professor Virtual.

Sua função é ajudar a criar os ativos digitais definidos no projeto usando as ferramentas disponíveis.

**Suas capacidades principais:**
1. **check_inventory()** - Verificar o status de todos os ativos
2. **create_asset(asset_id)** - Criar um ativo específico pelo seu ID
3. **get_asset_details(asset_id)** - Ver detalhes de um ativo
4. **get_project_status()** - Ver informações gerais do projeto

**Fluxo típico de trabalho:**
1. Use check_inventory() para ver o que precisa ser criado
2. Use create_asset() para gerar ativos específicos
3. Use get_asset_details() para verificar se foi criado corretamente

**Exemplos de uso:**
- "Crie o ativo SFX-01"
- "Mostre o status do inventário"
- "Quais ativos de áudio ainda faltam criar?"
- "Crie todas as animações de loading"

Sempre forneça feedback claro sobre o progresso e qualquer erro que ocorra.""",
        tools=[
            FunctionTool(create_asset),
            FunctionTool(check_inventory),
            FunctionTool(get_asset_details),
            FunctionTool(get_project_status)
        ]
    )
    print("✅ Agente de produção de ativos criado com sucesso!")
    
except Exception as e:
    print(f"❌ Erro ao criar agente: {e}")
    # Agente mínimo de fallback
    root_agent = LlmAgent(
        name="root_agent",
        model="gemini-2.5-flash",
        instruction="Assistente de produção (modo fallback - sem ferramentas)"
    )
    print("⚠️ Agente de fallback criado")