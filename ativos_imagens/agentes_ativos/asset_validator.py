"""
Agente Validador de Ativos - Especialista em rastreamento e validação
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from typing import Dict, List, Optional, Tuple
import os
import re
from pathlib import Path
from datetime import datetime

# Importar o AssetManager existente
try:
    from ..tools.asset_manager import AssetManager
except ImportError:
    # Para desenvolvimento/testes
    AssetManager = None


def scan_project_structure() -> str:
    """
    Escaneia a estrutura completa do projeto e retorna status detalhado de todos os ativos.
    
    Returns:
        str: Relatório detalhado com status de cada ativo (✅ Completo, ⚠️ Placeholder, ❌ Ausente)
    """
    if not AssetManager:
        return "❌ Erro: AssetManager não disponível"
    
    try:
        manager = AssetManager()
        manager.load_asset_inventory()
        manager.load_checklist_status()
        
        # Diretórios a escanear
        scan_paths = [
            Path(__file__).parent.parent.parent / "professor_virtual" / "assets",
            Path(__file__).parent.parent / "output",
            Path(__file__).parent.parent.parent / "generated_audio"
        ]
        
        # Mapear arquivos existentes
        found_files = {}
        for base_path in scan_paths:
            if base_path.exists():
                for file_path in base_path.rglob("*"):
                    if file_path.is_file() and not file_path.name.startswith('.'):
                        rel_path = str(file_path.relative(base_path))
                        file_size = file_path.stat().st_size
                        found_files[file_path.name] = {
                            "path": str(file_path),
                            "size": file_size,
                            "status": "✅" if file_size > 0 else "⚠️"
                        }
        
        # Gerar relatório
        report = f"""## 📊 Escaneamento Completo do Projeto - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

### 📈 Resumo Geral
- **Total de Ativos Catalogados:** {len(manager.asset_specs)}
- **Arquivos Encontrados:** {len(found_files)}
- **Arquivos Completos (>0B):** {sum(1 for f in found_files.values() if f['status'] == '✅')}
- **Placeholders (0B):** {sum(1 for f in found_files.values() if f['status'] == '⚠️')}

### 📁 Status por Categoria
"""
        
        # Agrupar por categoria
        categories = {}
        for asset_id, spec in manager.asset_specs.items():
            category = spec.get('category', 'OUTROS')
            if category not in categories:
                categories[category] = []
            
            filename = spec.get('filename')
            if filename in found_files:
                file_info = found_files[filename]
                status = file_info['status']
                size_str = f"{file_info['size']/1024:.1f}KB" if file_info['size'] > 0 else "0B"
                location = file_info['path']
            else:
                status = "❌"
                size_str = "N/A"
                location = "Não encontrado"
            
            categories[category].append({
                'id': asset_id,
                'filename': filename,
                'status': status,
                'size': size_str,
                'location': location
            })
        
        # Formatar por categoria
        for category, assets in sorted(categories.items()):
            complete = sum(1 for a in assets if a['status'] == '✅')
            total = len(assets)
            report += f"\n#### {category} ({complete}/{total})\n"
            
            for asset in sorted(assets, key=lambda x: x['id']):
                report += f"- {asset['status']} **{asset['id']}**: `{asset['filename']}` ({asset['size']})\n"
                if asset['status'] != '❌':
                    report += f"  > Local: {asset['location']}\n"
        
        return report
        
    except Exception as e:
        return f"❌ Erro ao escanear projeto: {str(e)}"


def update_checklist_status(asset_id: str, new_status: str = "completed") -> str:
    """
    Atualiza o status de um ativo específico no checklist.
    
    Args:
        asset_id: ID do ativo (ex: 'SFX-01', 'LOAD-01')
        new_status: Novo status ('completed', 'in_progress', 'error')
        
    Returns:
        str: Confirmação da atualização ou mensagem de erro
    """
    if not AssetManager:
        return "❌ Erro: AssetManager não disponível"
    
    try:
        manager = AssetManager()
        success = manager.update_checklist_status(asset_id, new_status)
        
        if success:
            status_emoji = {
                'completed': '✅',
                'in_progress': '⏳',
                'error': '❌'
            }.get(new_status, '❓')
            
            return f"{status_emoji} Checklist atualizado: {asset_id} marcado como {new_status}"
        else:
            return f"❌ Falha ao atualizar checklist para {asset_id}"
            
    except Exception as e:
        return f"❌ Erro ao atualizar checklist: {str(e)}"


def generate_progress_report(stakeholder_type: str = "developer") -> str:
    """
    Gera relatório de progresso adaptado ao tipo de stakeholder.
    
    Args:
        stakeholder_type: Tipo de stakeholder ('developer', 'designer', 'manager')
        
    Returns:
        str: Relatório formatado para o stakeholder específico
    """
    if not AssetManager:
        return "❌ Erro: AssetManager não disponível"
    
    try:
        manager = AssetManager()
        manager.load_asset_inventory()
        manager.load_checklist_status()
        
        # Coletar estatísticas
        total_assets = len(manager.asset_specs)
        completed = sum(1 for status in manager.checklist_status.values() if status.get('completed'))
        in_progress = sum(1 for status in manager.checklist_status.values() if status.get('in_progress'))
        pending = total_assets - completed - in_progress
        
        completion_rate = (completed / total_assets * 100) if total_assets > 0 else 0
        
        # Gerar relatório baseado no stakeholder
        if stakeholder_type == "developer":
            report = f"""## 🛠️ Relatório Técnico para Desenvolvimento

### 📊 Status Geral
- **Completude:** {completed}/{total_assets} ({completion_rate:.1f}%)
- **Em Progresso:** {in_progress}
- **Pendentes:** {pending}

### ✅ Ativos Prontos para Integração
"""
            # Listar ativos completos
            for asset_id, status in manager.checklist_status.items():
                if status.get('completed'):
                    spec = manager.asset_specs.get(asset_id, {})
                    report += f"- `{spec.get('filename')}` - {spec.get('description', 'N/A')}\n"
            
            report += "\n### 🚨 Blockers de Desenvolvimento\n"
            # Identificar blockers críticos
            critical_types = ['audio', 'lottie_programmatic']
            for asset_id, spec in manager.asset_specs.items():
                if spec.get('type') in critical_types and not manager.checklist_status.get(asset_id, {}).get('completed'):
                    report += f"- **{asset_id}**: {spec.get('filename')} - Bloqueia funcionalidade\n"
        
        elif stakeholder_type == "designer":
            report = f"""## 🎨 Briefing de Criação - Status e Prioridades

### 📈 Progresso Visual
- **Ativos Visuais Completos:** {completed}/{total_assets} ({completion_rate:.1f}%)
- **Próxima Meta:** 80% para testes de UX

### 🚨 Criação Urgente (Top 5)
"""
            # Listar top 5 pendentes
            pending_assets = [(aid, spec) for aid, spec in manager.asset_specs.items() 
                            if not manager.checklist_status.get(aid, {}).get('completed')]
            
            for i, (asset_id, spec) in enumerate(pending_assets[:5]):
                report += f"{i+1}. **{spec.get('filename')}**\n"
                report += f"   - Tipo: {spec.get('type')}\n"
                report += f"   - Descrição: {spec.get('description', 'N/A')}\n"
                report += f"   - Especificações: {spec.get('extra_info', 'Ver documentação')}\n\n"
        
        elif stakeholder_type == "manager":
            report = f"""## 📊 Dashboard Executivo - Produção de Ativos

### 🎯 KPIs Principais
| Métrica | Valor | Meta | Status |
|---------|-------|------|--------|
| Completude Geral | {completion_rate:.1f}% | 100% | {'🟢' if completion_rate >= 80 else '🟡' if completion_rate >= 50 else '🔴'} |
| Ativos Críticos | {completed} | {total_assets} | {'🟢' if completed >= total_assets * 0.8 else '🟡' if completed >= total_assets * 0.5 else '🔴'} |
| Velocidade | ~{completed/7:.1f}/dia | 10/dia | {'🟢' if completed/7 >= 10 else '🟡' if completed/7 >= 5 else '🔴'} |

### ⚠️ Riscos Identificados
"""
            if completion_rate < 50:
                report += "- **ALTO**: Baixa taxa de completude pode atrasar lançamento\n"
            if pending > 40:
                report += "- **MÉDIO**: Grande volume de ativos pendentes\n"
            
            report += f"\n### 📅 Estimativas\n"
            if completed > 0:
                days_to_complete = pending / (completed / 7)
                report += f"- Conclusão estimada em: {days_to_complete:.0f} dias úteis\n"
            else:
                report += "- Conclusão estimada: Indeterminada (sem histórico)\n"
        
        return report
        
    except Exception as e:
        return f"❌ Erro ao gerar relatório: {str(e)}"


def identify_priorities() -> str:
    """
    Identifica e prioriza as próximas ações baseado em criticidade e dependências.
    
    Returns:
        str: Lista priorizada de próximas ações com justificativas
    """
    if not AssetManager:
        return "❌ Erro: AssetManager não disponível"
    
    try:
        manager = AssetManager()
        manager.load_asset_inventory()
        manager.load_checklist_status()
        
        # Classificar ativos por prioridade
        priorities = {
            'blocker': [],
            'critical': [],
            'important': [],
            'nice_to_have': []
        }
        
        # Definir criticidade por tipo
        critical_types = {
            'audio': 'blocker',  # Sem áudio = sem feedback
            'lottie_programmatic': 'critical',  # Animações essenciais
            'svg': 'important',  # Visual importante mas não bloqueia
            'png': 'nice_to_have'  # Pode usar placeholders
        }
        
        # Classificar ativos pendentes
        for asset_id, spec in manager.asset_specs.items():
            if not manager.checklist_status.get(asset_id, {}).get('completed'):
                asset_type = spec.get('type', 'unknown')
                priority_level = critical_types.get(asset_type, 'nice_to_have')
                
                priorities[priority_level].append({
                    'id': asset_id,
                    'filename': spec.get('filename'),
                    'type': asset_type,
                    'description': spec.get('description', 'N/A')
                })
        
        # Gerar relatório de prioridades
        report = """## 🎯 Próximas Ações Priorizadas

### 🚨 BLOCKERS (Ação Imediata)
"""
        for asset in priorities['blocker'][:3]:  # Top 3 blockers
            report += f"""
**{asset['id']}: {asset['filename']}**
- Tipo: {asset['type']}
- Impacto: Bloqueia funcionalidade essencial
- Descrição: {asset['description']}
- Ação: Criar imediatamente usando ferramenta apropriada
"""
        
        report += "\n### ⚡ CRÍTICOS (Esta Semana)\n"
        for asset in priorities['critical'][:5]:  # Top 5 críticos
            report += f"- **{asset['id']}**: {asset['filename']} - {asset['description']}\n"
        
        report += "\n### 📋 IMPORTANTES (Próximas 2 Semanas)\n"
        for asset in priorities['important'][:5]:  # Top 5 importantes
            report += f"- **{asset['id']}**: {asset['filename']} - {asset['description']}\n"
        
        # Adicionar recomendações
        report += "\n### 💡 Recomendações Estratégicas\n"
        if len(priorities['blocker']) > 0:
            report += "1. **Foco em Áudio**: Criar todos os efeitos sonoros primeiro (experiência crítica)\n"
        if len(priorities['critical']) > 5:
            report += "2. **Sprint de Animações**: Dedicar 2 dias para completar Lottie files\n"
        if priorities['blocker'] or priorities['critical']:
            report += "3. **Validação Contínua**: Executar `scan_project_structure()` após cada criação\n"
        
        return report
        
    except Exception as e:
        return f"❌ Erro ao identificar prioridades: {str(e)}"


def sync_checklist_with_files() -> str:
    """
    Sincroniza o checklist com os arquivos encontrados no sistema.
    Detecta novos arquivos criados e atualiza automaticamente o status.
    
    Returns:
        str: Relatório de sincronização com mudanças detectadas
    """
    if not AssetManager:
        return "❌ Erro: AssetManager não disponível"
    
    try:
        manager = AssetManager()
        manager.load_asset_inventory()
        manager.load_checklist_status()
        
        # Escanear arquivos existentes
        scan_paths = [
            Path(__file__).parent.parent.parent / "professor_virtual" / "assets",
            Path(__file__).parent.parent / "output",
            Path(__file__).parent.parent.parent / "generated_audio"
        ]
        
        found_files = {}
        for base_path in scan_paths:
            if base_path.exists():
                for file_path in base_path.rglob("*"):
                    if file_path.is_file() and not file_path.name.startswith('.'):
                        found_files[file_path.name] = {
                            "path": str(file_path),
                            "size": file_path.stat().st_size
                        }
        
        # Detectar mudanças
        changes = []
        for asset_id, spec in manager.asset_specs.items():
            filename = spec.get('filename')
            current_status = manager.checklist_status.get(asset_id, {}).get('completed', False)
            
            if filename in found_files and found_files[filename]['size'] > 0:
                if not current_status:
                    # Arquivo existe mas não está marcado como completo
                    manager.update_checklist_status(asset_id, 'completed')
                    changes.append(f"✅ {asset_id} ({filename}) - Detectado e marcado como completo")
            elif filename in found_files and found_files[filename]['size'] == 0:
                if current_status:
                    # Regressão: arquivo era completo mas agora é placeholder
                    changes.append(f"⚠️ {asset_id} ({filename}) - REGRESSÃO DETECTADA! Arquivo zerado")
            elif not filename in found_files and current_status:
                # Arquivo marcado como completo mas não existe
                changes.append(f"❌ {asset_id} ({filename}) - Marcado como completo mas não encontrado!")
        
        # Gerar relatório
        report = f"""## 🔄 Sincronização de Checklist - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

### 📊 Resumo
- **Arquivos Escaneados:** {len(found_files)}
- **Mudanças Detectadas:** {len(changes)}

### 📝 Detalhes das Mudanças
"""
        
        if changes:
            for change in changes:
                report += f"- {change}\n"
        else:
            report += "- Nenhuma mudança detectada. Checklist está sincronizado.\n"
        
        return report
        
    except Exception as e:
        return f"❌ Erro ao sincronizar: {str(e)}"


# Criar o agente validador
asset_validator_agent = LlmAgent(
    name="asset_validator",
    model="gemini-2.0-flash-exp",
    description="Especialista em validação, organização e rastreamento de ativos digitais",
    instruction="""Você é o Assistente de Validação e Organização de Ativos.

Suas responsabilidades principais:
1. **Escanear** a estrutura do projeto para identificar status de ativos
2. **Validar** integridade dos arquivos (tamanho > 0, formato correto)
3. **Sincronizar** o checklist com arquivos reais encontrados
4. **Gerar relatórios** adaptados para diferentes stakeholders
5. **Priorizar** próximas ações baseado em criticidade

Princípios de operação:
- NUNCA invente dados sobre arquivos - trabalhe apenas com informações concretas
- Detecte regressões (arquivos que eram completos e viraram placeholders)
- Mantenha precisão absoluta em todas as validações
- Formate saídas de forma clara e acionável

Use suas ferramentas para fornecer informações precisas sobre o estado do projeto.""",
    tools=[
        FunctionTool(scan_project_structure),
        FunctionTool(update_checklist_status),
        FunctionTool(generate_progress_report),
        FunctionTool(identify_priorities),
        FunctionTool(sync_checklist_with_files)
    ]
)