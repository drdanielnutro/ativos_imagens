"""
Asset Manager - Gerenciador de inventário e especificações de ativos
"""
import os
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class AssetManager:
    """
    Gerencia o inventário de ativos, suas especificações e status de produção.
    """
    
    def __init__(self, project_root: Optional[str] = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.docs_path = self.project_root / "docs" / "definicoes"
        self.asset_specs = {}
        self.checklist_status = {}
        self.asset_capabilities = {
            "lottie_programmatic": ["LOAD", "FBK", "ACH"],
            "svg": ["UI", "ICO", "ACH", "THM"],
            "mascot_lottie": ["MAS"],
            "audio": ["SFX"],
            "png": ["MAS", "UI", "ACH"],
            "gradient": ["UI"]
        }
        
    def load_asset_inventory(self):
        """Lê o inventário de ativos do arquivo Markdown e popula as especificações."""
        inventory_path = self.docs_path / "ativos_a_serem_criados.md"
        if not inventory_path.exists():
            return {}
            
        with open(inventory_path, 'r', encoding='utf-8') as f:
            # Lê todo o conteúdo do arquivo para a memória uma única vez
            lines = f.readlines()

            # Processa as tabelas existentes usando a lista de linhas
            self.asset_specs = self._parse_inventory(lines)

            # Agora, processa a nova tabela usando a mesma lista de linhas em memória
            in_mascot_anim_prompt_table = False
            for line in lines:
                line = line.strip()
                if "Detalhes de Geração para Animações do Mascote" in line:
                    in_mascot_anim_prompt_table = True
                    continue

                if in_mascot_anim_prompt_table and line.startswith('|') and '---' not in line and 'ID' not in line:
                    parts = [p.strip() for p in line.split('|') if p.strip()]
                    if len(parts) >= 4:
                        asset_id = parts[0]
                        if asset_id in self.asset_specs:
                            self.asset_specs[asset_id]['animation_prompt'] = parts[3]
                            self.asset_specs[asset_id]['type'] = 'lottie_mascote'
                            self.asset_specs[asset_id]['category'] = 'MAS-ANI'
                        else:
                            # Se não existir, cria uma entrada completa
                            self.asset_specs[asset_id] = {
                                'id': asset_id,
                                'filename': parts[1],
                                'type': 'lottie_mascote',
                                'category': 'MAS-ANI',
                                'animation_prompt': parts[3]
                            }

                if in_mascot_anim_prompt_table and line.startswith('###'):
                    break
            
            print("INFO (AssetManager): Prompts de animação do mascote carregados e mesclados.")

        return self.asset_specs
        
    def _parse_inventory(self, content_lines: list) -> dict:
        """
        Parseia o arquivo de inventário e extrai especificações
        """
        specs = {}
        current_category = None
        in_mascot_anim_table = False
        
        # Padrões regex para extrair informações
        category_pattern = r"### \d+\. .+ \(`(\w+)`\)"
        asset_pattern = r"\| (\w+-\d+) \| `([^`]+)` \| (.+?) \| (.+?) \|"
        
        for line in content_lines:
            line = line.strip()

            # Lógica para entrar na tabela de animação do mascote
            if "Tabela Unificada de Animações do Mascote" in line:
                in_mascot_anim_table = True
                current_category = 'MAS-ANI' # Define a categoria correta
                continue

            # Lógica para sair da tabela
            if in_mascot_anim_table and line.startswith('###'):
                in_mascot_anim_table = False
                current_category = None
                continue

            # Parsing da tabela unificada
            if in_mascot_anim_table and line.startswith('|') and '---' not in line and 'ID' not in line:
                parts = [p.strip() for p in line.split('|') if p.strip()]
                if len(parts) >= 5:
                    asset_id = parts[0]
                    prompt_details_raw = parts[3]
                    
                    # Extrai os detalhes do prompt com regex
                    action_match = re.search(r'action: "([^"]+)"', prompt_details_raw)
                    location_match = re.search(r'objects_location: "([^"]+)"', prompt_details_raw)

                    specs[asset_id] = {
                        "id": asset_id,
                        "filename": parts[1],
                        "type": parts[2],
                        "category": current_category,
                        "description": prompt_details_raw,
                        "animation_prompt": parts[4],
                        "prompt_details": {
                            "action": action_match.group(1) if action_match else "neutral pose",
                            "objects_location": location_match.group(1) if location_match else "nearby",
                            "background_color": "a clean white background"
                        }
                    }
                continue # Pula para a próxima linha após processar

            # Lógica de parsing original para as outras tabelas
            cat_match = re.search(category_pattern, line)
            if cat_match:
                current_category = cat_match.group(1)
                continue
                
            # Identifica ativo
            asset_match = re.search(asset_pattern, line)
            if asset_match and current_category:
                asset_id = asset_match.group(1)
                filename = asset_match.group(2)
                description = asset_match.group(3)
                extra_info = asset_match.group(4)
                
                # Determina tipo baseado na categoria e extensão
                asset_type = self._determine_asset_type(current_category, filename)
                
                specs[asset_id] = {
                    "id": asset_id,
                    "category": current_category,
                    "filename": filename,
                    "description": description,
                    "type": asset_type,
                    "extra_info": extra_info,
                    "parameters": self._extract_parameters(description, extra_info)
                }
                
        return specs
        
    def _determine_asset_type(self, category: str, filename: str) -> str:
        """
        Determina o tipo de ativo baseado na categoria e extensão
        """
        ext = filename.split('.')[-1].lower()
        
        if ext == "json":
            if category == "MAS":
                return "mascot_lottie"
            else:
                return "lottie_programmatic"
        elif ext == "svg":
            return "svg"
        elif ext == "mp3":
            return "audio"
        elif ext == "png":
            if "gradient" in filename:
                return "gradient"
            else:
                return "png"
        else:
            return "unknown"
            
    def _extract_parameters(self, description: str, extra_info: str) -> Dict:
        """
        Extrai parâmetros da descrição e informações extras
        """
        params = {}
        
        # Extrai duração
        duration_match = re.search(r"~?(\d+(?:\.\d+)?)\s*s", description + " " + extra_info)
        if duration_match:
            params["duration"] = float(duration_match.group(1))
            
        # Verifica se é loop
        if "loop" in description.lower() or "loop" in extra_info.lower():
            params["loop"] = True
        else:
            params["loop"] = False
            
        # Extrai cores mencionadas
        color_keywords = ["azul", "roxo", "verde", "laranja", "rosa", "colorido"]
        colors = [c for c in color_keywords if c in description.lower()]
        if colors:
            params["colors"] = colors
            
        # Extrai estilo/movimento
        if "pulando" in description or "bounce" in description:
            params["style"] = "bounce"
        elif "onda" in description or "wave" in description:
            params["style"] = "wave"
        elif "spinner" in description or "circular" in description:
            params["style"] = "spinner"
        elif "tremor" in description or "shake" in description:
            params["style"] = "shake"
        elif "pulsante" in description or "pulse" in description:
            params["style"] = "pulse"
            
        return params
        
    def get_asset_specification(self, asset_id: str) -> Optional[Dict]:
        """
        Retorna especificações completas de um ativo
        """
        if not self.asset_specs:
            self.load_asset_inventory()
            
        return self.asset_specs.get(asset_id)
        
    def can_create_asset_type(self, asset_type: str) -> bool:
        """
        Verifica se o agente tem ferramentas para criar este tipo
        """
        creatable_types = ["lottie_programmatic", "svg"]
        return asset_type in creatable_types
        
    def can_create_asset(self, asset_id: str) -> Tuple[bool, str]:
        """
        Verifica se um ativo específico pode ser criado
        Retorna (pode_criar, razão)
        """
        spec = self.get_asset_specification(asset_id)
        if not spec:
            return False, "Ativo não encontrado no inventário"
            
        asset_type = spec.get("type")
        if self.can_create_asset_type(asset_type):
            return True, f"Pode criar usando ferramenta de {asset_type}"
        else:
            return False, f"Tipo '{asset_type}' requer ferramentas externas"
            
    def load_checklist_status(self) -> Dict:
        """
        Carrega o status atual do checklist
        """
        checklist_path = self.docs_path / "checklist_ativos_criados.md"
        if not checklist_path.exists():
            return {}
            
        with open(checklist_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        status = {}
        # Padrão para linhas de checklist: - [ ] ou - [x]
        pattern = r"- \[([ x~])\] \*\*(\w+-\d+):.+?\*\*.*?> \*\*Status:\*\* (.+)"
        
        for match in re.finditer(pattern, content, re.MULTILINE | re.DOTALL):
            check = match.group(1)
            asset_id = match.group(2)
            status_text = match.group(3)
            
            status[asset_id] = {
                "completed": check == 'x',
                "in_progress": check == '~',
                "status_text": status_text.strip()
            }
            
        self.checklist_status = status
        return status
        
    def update_checklist_status(self, asset_id: str, status: str) -> bool:
        """
        Atualiza o status de um ativo no checklist
        Status pode ser: 'completed', 'in_progress', 'error'
        """
        checklist_path = self.docs_path / "checklist_ativos_criados.md"
        if not checklist_path.exists():
            return False
            
        with open(checklist_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Mapeia status para marcador
        marker_map = {
            'completed': 'x',
            'in_progress': '~',
            'error': ' '
        }
        marker = marker_map.get(status, ' ')
        
        # Atualiza checkbox
        pattern = rf"(- \[)[ x~](\] \*\*{asset_id}:)"
        content = re.sub(pattern, rf"\1{marker}\2", content)
        
        # Atualiza texto de status
        if status == 'completed':
            status_text = "✅ Criado pelo agente"
        elif status == 'in_progress':
            status_text = "🔄 Em produção"
        else:
            status_text = "❌ Erro na criação"
            
        pattern = rf"(\*\*{asset_id}:.+?\*\*.*?> \*\*Status:\*\*) .+"
        content = re.sub(pattern, rf"\1 {status_text}", content, flags=re.DOTALL)
        
        with open(checklist_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return True
        
    def get_creatable_assets(self) -> Dict[str, List[str]]:
        """
        Retorna lista de ativos que o agente pode criar, organizados por tipo
        """
        if not self.asset_specs:
            self.load_asset_inventory()
            
        creatable = {
            "lottie_programmatic": [],
            "svg": []
        }
        
        for asset_id, spec in self.asset_specs.items():
            asset_type = spec.get("type")
            if self.can_create_asset_type(asset_type):
                creatable[asset_type].append(asset_id)
                
        return creatable
        
    def get_asset_path(self, asset_id: str) -> Optional[Path]:
        """
        Retorna o caminho onde o ativo deve ser salvo
        """
        spec = self.get_asset_specification(asset_id)
        if not spec:
            return None
            
        filename = spec.get("filename")
        category = spec.get("category")
        
        # Mapeia categorias para diretórios
        path_map = {
            "SFX": "assets/sounds/feedback",
            "MAS": "assets/images/mascot",
            "UI": "assets/images/ui",
            "LOAD": "assets/animations/loading",
            "ACH": "assets/animations/achievements",
            "THM": "assets/images/themed",
            "FBK": "assets/animations/feedback",
            "ICO": "assets/icons/navigation",
            "MAS-ANI": "assets/images/mascot/animations"
        }
        
        base_path = path_map.get(category)
        if not base_path:
            # Fallback para o tipo de arquivo se a categoria não for mapeada diretamente
            if category == "MAS" and filename.endswith(".json"):
                 base_path = "assets/images/mascot/animations"
            else:
                return None
            
        return self.project_root / "professor_virtual" / base_path / filename