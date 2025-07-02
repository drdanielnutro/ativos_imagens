

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
        # Tentar primeiro o arquivo JSON (novo formato)
        json_path = self.data_path / "checklist_ativos_criados.json"
        md_path = self.data_path / "checklist_ativos_criados.md"
        
        if json_path.exists():
            # Usar o novo formato JSON
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Construir status no formato esperado
            status = {}
            for asset_id, asset_info in data.get("assets", {}).items():
                status[asset_id] = {
                    "completed": asset_info["status"] == "completed",
                    "in_progress": asset_info["status"] == "in_progress",
                }
            
            self.checklist_status = status
            print(f"INFO (AssetManager): Status de {len(status)} ativos carregados de '{json_path.name}' (formato JSON).")
            return status
            
        elif md_path.exists():
            # Fallback para o formato antigo MD
            print("AVISO (AssetManager): Usando formato antigo MD para checklist. Considere migrar para JSON.")
            with open(md_path, 'r', encoding='utf-8') as f:
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
        else:
            return {}

    def update_checklist_status(self, asset_id: str, status: str) -> bool:
        """Atualiza o status de um ativo no checklist."""
        # Tentar primeiro o arquivo JSON (novo formato)
        json_path = self.data_path / "checklist_ativos_criados.json"
        md_path = self.data_path / "checklist_ativos_criados.md"
        
        if json_path.exists():
            # Usar o novo formato JSON
            from datetime import datetime
            
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Verificar se o ativo existe
            if asset_id not in data.get("assets", {}):
                print(f"AVISO (AssetManager): Ativo '{asset_id}' não encontrado no checklist JSON.")
                return False
            
            # Atualizar status do ativo
            data["assets"][asset_id]["status"] = status
            
            # Atualizar timestamp se completado
            if status == "completed":
                data["assets"][asset_id]["completed_date"] = datetime.now().isoformat()
            elif status == "pending":
                data["assets"][asset_id]["completed_date"] = None
            
            # Recalcular totais
            completed_count = sum(1 for asset in data["assets"].values() if asset["status"] == "completed")
            in_progress_count = sum(1 for asset in data["assets"].values() if asset["status"] == "in_progress")
            
            data["completed"] = completed_count
            data["in_progress"] = in_progress_count
            data["pending"] = data["total_assets"] - completed_count - in_progress_count
            data["last_updated"] = datetime.now().isoformat()
            
            # Salvar de volta
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Também atualizar o MD se existir (para manter sincronizado temporariamente)
            if md_path.exists():
                self._update_md_checklist(md_path, asset_id, status)
            
            return True
            
        elif md_path.exists():
            # Fallback para o formato antigo MD
            return self._update_md_checklist(md_path, asset_id, status)
        else:
            return False
    
    def _update_md_checklist(self, md_path: Path, asset_id: str, status: str) -> bool:
        """Método auxiliar para atualizar o checklist MD (legado)."""
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        marker_map = {'completed': 'x', 'in_progress': '~', 'error': ' ', 'pending': ' '}
        marker = marker_map.get(status, ' ')
        
        # Regex para encontrar o checkbox do asset_id
        pattern = re.compile(rf"(- \[)[ x~](\] \*\*{re.escape(asset_id)}:)")
        if not pattern.search(content):
            print(f"AVISO (AssetManager): Não foi possível encontrar '{asset_id}' no checklist MD.")
            return False

        content = pattern.sub(rf"\1{marker}\2", content)
        
        # Atualiza o texto de status
        status_text_map = {
            'completed': "✅ Gerado via script",
            'in_progress': "🔄 Em produção",
            'error': "❌ Erro na geração",
            'pending': ""
        }
        status_text = status_text_map.get(status, " indefinido")

        # Encontra a linha do asset e substitui o status na linha seguinte
        if status_text:
            asset_line_pattern = re.compile(rf"(.*?{re.escape(asset_id)}:.*\n)")
            content = asset_line_pattern.sub(rf"\1  > **Status:**{status_text}\n", content)

        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return True

    def get_pending_assets(self, category: Optional[str] = None, limit: Optional[int] = None) -> List[Dict]:
        """
        Retorna lista de ativos pendentes, opcionalmente filtrados por categoria.
        
        Args:
            category: Categoria para filtrar (ex: 'audio', 'mascot_static', etc)
            limit: Número máximo de ativos a retornar
            
        Returns:
            Lista de dicionários com informações dos ativos pendentes
        """
        # Carregar dados se necessário
        if not self.checklist_status:
            self.load_checklist_status()
        
        # Tentar carregar do JSON para ter informações completas
        json_path = self.data_path / "checklist_ativos_criados.json"
        if json_path.exists():
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            pending_assets = []
            for asset_id, asset_info in data.get("assets", {}).items():
                if asset_info["status"] == "pending":
                    # Filtrar por categoria se especificado
                    if category and asset_info.get("category") != category:
                        continue
                    
                    pending_assets.append({
                        "id": asset_id,
                        "file": asset_info["file"],
                        "tool": asset_info["tool"],
                        "category": asset_info["category"],
                        "description": asset_info.get("description", "")
                    })
            
            # Ordenar por ID para manter consistência
            pending_assets.sort(key=lambda x: x["id"])
            
            # Aplicar limite se especificado
            if limit:
                pending_assets = pending_assets[:limit]
            
            return pending_assets
        else:
            # Fallback para formato antigo (informações limitadas)
            pending_assets = []
            for asset_id, status_info in self.checklist_status.items():
                if not status_info["completed"] and not status_info["in_progress"]:
                    spec = self.get_specification(asset_id)
                    if spec:
                        if category and spec.get("category") != category:
                            continue
                        pending_assets.append({
                            "id": asset_id,
                            "tool": spec.get("tool", "unknown")
                        })
            
            if limit:
                pending_assets = pending_assets[:limit]
            
            return pending_assets
    
    def get_next_pending_asset(self) -> Optional[str]:
        """
        Retorna o ID do próximo ativo pendente a ser criado.
        
        Returns:
            ID do ativo ou None se todos estiverem completos
        """
        pending = self.get_pending_assets(limit=1)
        return pending[0]["id"] if pending else None
    
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
