

"""
Asset Manager - Gerenciador de especificações de ativos e status.
Lê a partir de uma fonte única da verdade para geração de ativos.
"""
import os
import re
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class AssetManager:
    """
    Gerencia as especificações de ativos, o status de produção e os caminhos de saída.
    """
    
    def __init__(self, project_root: Optional[str] = None):
        if project_root:
            self.project_root = Path(project_root)
        else:
            # Fallback robusto para encontrar a raiz do projeto
            self.project_root = Path(__file__).parent.parent.parent

        self.data_path = self.project_root / "docs" / "definicoes"
        self.asset_specs = {}
        self.checklist_status = {}

    def load_specifications(self) -> Dict:
        """Lê as especificações de geração do arquivo de definição principal."""
        # Tentar primeiro o arquivo JSON (novo formato)
        json_path = self.data_path / "geracao_de_ativos.json"
        md_path = self.data_path / "geracao_de_ativos.md"
        
        if json_path.exists():
            # Usar o novo formato JSON
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            specs = {}
            # Extrair ativos de todas as categorias
            for category_name, category_data in data.get("categories", {}).items():
                for asset in category_data.get("assets", []):
                    asset_id = asset["id"]
                    specs[asset_id] = {
                        "id": asset_id,
                        "tool": asset["tool"],
                        "params": asset["params"],
                        "category": category_name,
                        "description": asset.get("description", "")
                    }
            
            self.asset_specs = specs
            print(f"INFO (AssetManager): {len(specs)} especificações de ativos carregadas de '{json_path.name}' (formato JSON).")
            return self.asset_specs
            
        elif md_path.exists():
            # Fallback para o formato antigo MD
            print("AVISO (AssetManager): Usando formato antigo MD. Considere migrar para JSON.")
            with open(md_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            specs = {}
            # Pula as duas primeiras linhas (cabeçalho da tabela)
            for line in lines[2:]:
                line = line.strip()
                if not line.startswith('|'):
                    continue

                parts = [p.strip() for p in line.split('|') if p.strip()]
                if len(parts) < 3:
                    continue

                asset_id, tool, params_str = parts[0], parts[1], parts[2]
                
                try:
                    # Remove as crases e converte a string JSON em um dicionário Python
                    params_json = json.loads(params_str.strip('`'))
                    specs[asset_id] = {
                        "id": asset_id,
                        "tool": tool,
                        "params": params_json
                    }
                except json.JSONDecodeError as e:
                    print(f"AVISO (AssetManager): Erro ao decodificar JSON para o ativo '{asset_id}'. Linha: {params_str}. Erro: {e}")
                    continue
            
            self.asset_specs = specs
            print(f"INFO (AssetManager): {len(specs)} especificações de ativos carregadas de '{md_path.name}'.")
            return self.asset_specs
        else:
            raise FileNotFoundError(f"Arquivo de definição de ativos não encontrado em: {json_path} ou {md_path}")

    def get_specification(self, asset_id: str) -> Optional[Dict]:
        """Retorna a especificação completa de um ativo."""
        if not self.asset_specs:
            self.load_specifications()
        return self.asset_specs.get(asset_id)

    def load_checklist_status(self) -> Dict:
        """Carrega o status atual do checklist."""
        checklist_path = self.data_path / "checklist_ativos_criados.md"
        if not checklist_path.exists():
            return {}
            
        with open(checklist_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        status = {}
        pattern = r"- \[([ x~])\] \*\*(\w+-\w+-\d+):| - \[([ x~])\] \*\*(\w+-\d+):"
        
        for match in re.finditer(pattern, content):
            check = match.group(1) or match.group(3)
            asset_id = match.group(2) or match.group(4)
            
            status[asset_id] = {
                "completed": check == 'x',
                "in_progress": check == '~',
            }
            
        self.checklist_status = status
        return status

    def update_checklist_status(self, asset_id: str, status: str) -> bool:
        """Atualiza o status de um ativo no checklist."""
        checklist_path = self.data_path / "checklist_ativos_criados.md"
        if not checklist_path.exists():
            return False
            
        with open(checklist_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        marker_map = {'completed': 'x', 'in_progress': '~', 'error': ' '}
        marker = marker_map.get(status, ' ')
        
        # Regex para encontrar o checkbox do asset_id
        pattern = re.compile(rf"(- \[)[ x~](\] \*\*{re.escape(asset_id)}:)")
        if not pattern.search(content):
            print(f"AVISO (AssetManager): Não foi possível encontrar a entrada do checklist para '{asset_id}'. O status não foi atualizado.")
            return False

        content = pattern.sub(rf"\1{marker}\2", content)
        
        # Atualiza o texto de status
        status_text_map = {
            'completed': "✅ Gerado via script",
            'in_progress': "🔄 Em produção",
            'error': "❌ Erro na geração"
        }
        status_text = status_text_map.get(status, " indefinido")

        status_pattern = re.compile(rf"(> \*\*Status:\*\*) .+")
        # Encontra a linha do asset e substitui o status na linha seguinte
        asset_line_pattern = re.compile(rf"(.*?{re.escape(asset_id)}:.*\n)")
        content = asset_line_pattern.sub(rf"\1  > **Status:**{status_text}\n", content)

        with open(checklist_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return True

    def get_asset_path(self, asset_id: str) -> Optional[Path]:
        """
        Retorna o caminho de destino onde o ativo deve ser salvo.
        Esta função agora precisa ler o arquivo de mapeamento original para obter o nome do arquivo e a categoria.
        """
        # Para obter o filename e a categoria, precisamos ler o documento original
        # Esta é uma solução temporária para manter a compatibilidade
        inventory_path = self.data_path / "ativos_a_serem_criados.md"
        if not inventory_path.exists():
            return None

        with open(inventory_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Regex para encontrar a linha da tabela com o ID do ativo
        # Ex: | SFX-01 | `button_tap.mp3` | ...
        # Ex: | MAS-ANI-01 | mascot_idle.json | ...
        match = re.search(rf"\|\s*{re.escape(asset_id)}\s*\|\s*`?([^`|]+)`?", content)
        if not match:
            return None
        
        filename = match.group(1).strip()
        
        # Encontrar a categoria (SFX, MAS, UI, etc.)
        # A categoria está no cabeçalho da seção ###, ex: ### 1. 🎵 Efeitos Sonoros (`SFX`)
        # Encontramos a posição do asset e procuramos para trás pelo cabeçalho mais próximo
        asset_pos = match.start()
        headers = list(re.finditer(r"### .*?`(\w+)`", content))
        
        category = None
        for header in reversed(headers):
            if header.start() < asset_pos:
                category = header.group(1)
                break
        
        # Caso especial para animações do mascote na tabela unificada
        if asset_id.startswith("MAS-ANI"):
            category = "MAS-ANI"

        if not category or not filename:
            return None

        # Mapeia categorias para diretórios
        path_map = {
            "SFX": "assets/sounds/feedback",
            "MAS": "assets/images/mascot",
            "UI": "assets/images/ui",
            "LOAD": "assets/animations/loading",
            "ACH": "assets/images/achievements", # Categoria mista para frames e animações
            "THM": "assets/images/themed",
            "FBK": "assets/animations/feedback",
            "ICO": "assets/icons/navigation",
            "MAS-ANI": "assets/images/mascot/animations"
        }

        # Lógica de ajuste para subdiretórios
        if category == "ACH":
            if filename.endswith(".svg"):
                base_path = "assets/images/achievements/frames"
            else:
                base_path = "assets/animations/achievements"
        elif category == "UI":
            if "pattern" in filename:
                base_path = "assets/images/ui/patterns"
            elif "gradient" in filename:
                base_path = "assets/images/ui/backgrounds"
            else:
                base_path = "assets/images/ui"
        else:
            base_path = path_map.get(category)

        if not base_path:
            return None
            
        return self.project_root / "professor_virtual" / base_path / filename
