#!/usr/bin/env python3
"""
Script de migração para converter checklist_ativos_criados.md para formato JSON
"""
import re
import json
from pathlib import Path
from datetime import datetime

def parse_checklist_md(md_file_path):
    """Parseia o arquivo MD e extrai informações dos ativos"""
    with open(md_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extrair resumo do status
    status_match = re.search(r'- \*\*Total de Assets:\*\* (\d+)\n- \*\*Concluídos:\*\* (\d+)', content)
    if status_match:
        total_assets = int(status_match.group(1))
        completed = int(status_match.group(2))
    else:
        total_assets = 62
        completed = 0
    
    # Estrutura JSON
    checklist_data = {
        "version": "1.0",
        "last_updated": datetime.now().isoformat(),
        "total_assets": total_assets,
        "completed": completed,
        "in_progress": 0,
        "pending": total_assets - completed,
        "assets": {}
    }
    
    # Regex para encontrar cada ativo
    # Formato: - [x] **SFX-01: `button_tap.mp3`**
    asset_pattern = re.compile(
        r'- \[([ x])\] \*\*([A-Z]+-(?:ANI-)?[\d]+): `([^`]+)`\*\*\n'
        r'(?:  > \*\*Status:\*\*(.+)\n)?'
        r'  > \*\*Descrição:\*\* (.+)\n'
    )
    
    # Mapear categorias baseado no prefixo do ID
    category_map = {
        'SFX': 'audio',
        'MAS': 'mascot_static',
        'MAS-ANI': 'mascot_animations',
        'UI': 'ui_elements',
        'LOAD': 'loading_animations',
        'ACH': 'achievements',
        'THM': 'themed_elements',
        'FBK': 'feedback_animations',
        'ICO': 'navigation_icons'
    }
    
    # Mapear ferramentas baseado na categoria
    tool_map = {
        'audio': 'audio_generator',
        'mascot_static': 'image_generator',
        'mascot_animations': 'mascot_animator',
        'ui_elements': 'mixed',  # SVG ou image_generator
        'loading_animations': 'lottie_programmatic',
        'achievements': 'mixed',  # Lottie ou SVG
        'themed_elements': 'svg_generator',
        'feedback_animations': 'lottie_programmatic',
        'navigation_icons': 'svg_generator'
    }
    
    # Processar cada ativo encontrado
    for match in asset_pattern.finditer(content):
        checkbox = match.group(1)
        asset_id = match.group(2)
        filename = match.group(3)
        status_text = match.group(4) or ""
        description = match.group(5)
        
        # Determinar status
        if checkbox == 'x':
            status = 'completed'
            completed_date = datetime.now().isoformat()  # Aproximado
        else:
            status = 'pending'
            completed_date = None
        
        # Determinar categoria
        prefix = asset_id.split('-')[0]
        if asset_id.startswith('MAS-ANI'):
            category = 'mascot_animations'
        else:
            category = category_map.get(prefix, 'unknown')
        
        # Determinar ferramenta
        tool = tool_map.get(category, 'unknown')
        
        # Ajustar ferramenta para casos específicos
        if category == 'ui_elements':
            if filename.endswith('.svg'):
                tool = 'svg_generator'
            else:
                tool = 'image_generator'
        elif category == 'achievements':
            if filename.endswith('.json'):
                tool = 'lottie_programmatic'
            elif filename.endswith('.svg'):
                tool = 'svg_generator'
            else:
                tool = 'image_generator'
        
        # Adicionar ao dicionário
        checklist_data['assets'][asset_id] = {
            'status': status,
            'completed_date': completed_date,
            'tool': tool,
            'file': filename,
            'category': category,
            'description': description
        }
    
    return checklist_data

def main():
    """Script principal de migração"""
    project_root = Path(__file__).parent
    md_path = project_root / "docs" / "definicoes" / "checklist_ativos_criados.md"
    json_path = project_root / "docs" / "definicoes" / "checklist_ativos_criados.json"
    
    print(f"🔄 Iniciando migração de checklist MD → JSON")
    print(f"📄 Origem: {md_path}")
    print(f"📄 Destino: {json_path}")
    
    try:
        # Parsear o arquivo MD
        checklist_data = parse_checklist_md(md_path)
        
        # Atualizar contadores
        completed_count = sum(1 for asset in checklist_data['assets'].values() 
                            if asset['status'] == 'completed')
        checklist_data['completed'] = completed_count
        checklist_data['pending'] = checklist_data['total_assets'] - completed_count
        
        # Salvar como JSON
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(checklist_data, f, indent=2, ensure_ascii=False)
        
        # Relatório
        print(f"\n✅ Migração concluída com sucesso!")
        print(f"📊 Total de ativos: {checklist_data['total_assets']}")
        print(f"✅ Concluídos: {checklist_data['completed']}")
        print(f"⏳ Pendentes: {checklist_data['pending']}")
        print(f"📁 Arquivo JSON criado: {json_path}")
        
        # Verificar integridade
        assert len(checklist_data['assets']) == checklist_data['total_assets'], \
            f"Erro: Esperado {checklist_data['total_assets']} ativos, encontrado {len(checklist_data['assets'])}"
        
        print(f"\n✨ Verificação de integridade: OK")
        
    except Exception as e:
        print(f"\n❌ Erro durante migração: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())