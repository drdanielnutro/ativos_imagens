#!/usr/bin/env python3
"""
Script de Validação do arquivo geracao_de_ativos.json
Verifica integridade, consistência e conformidade do arquivo de definições.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Cores para output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.BLUE}{Colors.BOLD}=== {text} ==={Colors.RESET}")

def print_success(text: str):
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text: str):
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def validate_json_structure(data: Dict) -> Tuple[bool, List[str]]:
    """Valida a estrutura básica do JSON."""
    errors = []
    
    # Campos obrigatórios no root
    required_root = ["version", "description", "total_assets", "categories"]
    for field in required_root:
        if field not in data:
            errors.append(f"Campo obrigatório ausente no root: '{field}'")
    
    # Validar categorias
    if "categories" in data:
        if not isinstance(data["categories"], dict):
            errors.append("'categories' deve ser um dicionário")
        else:
            for cat_name, cat_data in data["categories"].items():
                # Campos obrigatórios em cada categoria
                required_cat = ["description", "tool", "assets"]
                for field in required_cat:
                    if field not in cat_data:
                        errors.append(f"Campo '{field}' ausente na categoria '{cat_name}'")
                
                # Validar array de assets
                if "assets" in cat_data:
                    if not isinstance(cat_data["assets"], list):
                        errors.append(f"'assets' em '{cat_name}' deve ser um array")
    
    return len(errors) == 0, errors

def validate_assets(data: Dict) -> Tuple[bool, List[str]]:
    """Valida cada ativo individualmente."""
    errors = []
    warnings = []
    asset_ids = set()
    total_count = 0
    
    for cat_name, cat_data in data.get("categories", {}).items():
        for i, asset in enumerate(cat_data.get("assets", [])):
            total_count += 1
            
            # Validar campos obrigatórios
            required_asset = ["id", "tool", "params"]
            for field in required_asset:
                if field not in asset:
                    errors.append(f"Campo '{field}' ausente no ativo {i} da categoria '{cat_name}'")
            
            # Validar ID único
            if "id" in asset:
                asset_id = asset["id"]
                if asset_id in asset_ids:
                    errors.append(f"ID duplicado: '{asset_id}'")
                asset_ids.add(asset_id)
                
                # Validar formato do ID
                if not asset_id or not isinstance(asset_id, str):
                    errors.append(f"ID inválido no ativo {i} da categoria '{cat_name}'")
            
            # Validar params
            if "params" in asset:
                if not isinstance(asset["params"], dict):
                    errors.append(f"'params' deve ser um dicionário no ativo '{asset.get('id', f'índice {i}')}'")
            
            # Avisos para campos opcionais úteis
            if "description" not in asset:
                warnings.append(f"Ativo '{asset.get('id', f'índice {i}')}' sem descrição")
    
    # Validar total declarado vs real
    if "total_assets" in data and data["total_assets"] != total_count:
        errors.append(f"Total declarado ({data['total_assets']}) diferente do real ({total_count})")
    
    return len(errors) == 0, errors, warnings

def validate_tools_consistency(data: Dict) -> Tuple[bool, List[str]]:
    """Valida consistência das ferramentas."""
    errors = []
    known_tools = {
        "audio_generator", "image_generator", "mascot_animator",
        "svg_generator", "lottie_programmatic"
    }
    
    for cat_name, cat_data in data.get("categories", {}).items():
        cat_tool = cat_data.get("tool")
        
        for asset in cat_data.get("assets", []):
            asset_tool = asset.get("tool")
            
            # Verificar se a ferramenta é conhecida
            if asset_tool and asset_tool not in known_tools and asset_tool != "mixed":
                errors.append(f"Ferramenta desconhecida '{asset_tool}' no ativo '{asset.get('id')}'")
            
            # Verificar consistência com a categoria (se não for "mixed")
            if cat_tool != "mixed" and asset_tool and asset_tool != cat_tool:
                errors.append(f"Ferramenta '{asset_tool}' inconsistente com categoria '{cat_name}' (esperado: '{cat_tool}')")
    
    return len(errors) == 0, errors

def validate_params_by_tool(data: Dict) -> Tuple[bool, List[str]]:
    """Valida parâmetros específicos por ferramenta."""
    errors = []
    
    # Parâmetros obrigatórios por ferramenta
    required_params = {
        "audio_generator": ["filename", "duration", "prompt"],
        "image_generator": ["asset_type"],
        "mascot_animator": ["animation_prompt"],
        "svg_generator": ["svg_type"],
        "lottie_programmatic": ["animation_type", "duration"]
    }
    
    for cat_name, cat_data in data.get("categories", {}).items():
        for asset in cat_data.get("assets", []):
            tool = asset.get("tool")
            params = asset.get("params", {})
            asset_id = asset.get("id", "unknown")
            
            if tool in required_params:
                for param in required_params[tool]:
                    if param not in params:
                        errors.append(f"Parâmetro obrigatório '{param}' ausente em '{asset_id}' (tool: {tool})")
    
    return len(errors) == 0, errors

def main():
    # Encontrar o arquivo JSON
    project_root = Path(__file__).parent.parent.parent
    json_path = project_root / "docs" / "definicoes" / "geracao_de_ativos.json"
    
    print(f"{Colors.BOLD}Validador de geracao_de_ativos.json{Colors.RESET}")
    print(f"Arquivo: {json_path}")
    
    if not json_path.exists():
        print_error(f"Arquivo não encontrado: {json_path}")
        sys.exit(1)
    
    # Carregar JSON
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print_success("JSON carregado com sucesso")
    except json.JSONDecodeError as e:
        print_error(f"Erro ao decodificar JSON: {e}")
        sys.exit(1)
    
    # Executar validações
    all_valid = True
    
    # 1. Estrutura básica
    print_header("Validação de Estrutura")
    valid, errors = validate_json_structure(data)
    if valid:
        print_success("Estrutura do JSON está correta")
    else:
        all_valid = False
        for error in errors:
            print_error(error)
    
    # 2. Validação de ativos
    print_header("Validação de Ativos")
    valid, errors, warnings = validate_assets(data)
    if valid:
        print_success(f"Todos os {data.get('total_assets', 0)} ativos validados")
    else:
        all_valid = False
        for error in errors:
            print_error(error)
    
    if warnings:
        for warning in warnings:
            print_warning(warning)
    
    # 3. Consistência de ferramentas
    print_header("Validação de Ferramentas")
    valid, errors = validate_tools_consistency(data)
    if valid:
        print_success("Ferramentas consistentes")
    else:
        all_valid = False
        for error in errors:
            print_error(error)
    
    # 4. Parâmetros por ferramenta
    print_header("Validação de Parâmetros")
    valid, errors = validate_params_by_tool(data)
    if valid:
        print_success("Parâmetros corretos para cada ferramenta")
    else:
        all_valid = False
        for error in errors:
            print_error(error)
    
    # Resumo final
    print_header("Resumo")
    if all_valid:
        print_success("✨ JSON completamente válido!")
        
        # Estatísticas
        total = sum(len(cat["assets"]) for cat in data["categories"].values())
        print(f"\n📊 Estatísticas:")
        print(f"  - Total de ativos: {total}")
        print(f"  - Categorias: {len(data['categories'])}")
        for cat_name, cat_data in data["categories"].items():
            print(f"    • {cat_name}: {len(cat_data['assets'])} ativos")
    else:
        print_error("❌ Foram encontrados erros no JSON")
        sys.exit(1)

if __name__ == "__main__":
    main()