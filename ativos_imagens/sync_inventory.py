#!/usr/bin/env python3
"""Sincroniza o arquivo de inventário de assets para dentro do pacote.

Uso:
    python -m ativos_imagens.sync_inventory

Ele copia docs/definicoes/ativos_a_serem_criados.md para
ativos_imagens/resources/definicoes/, criando diretórios se necessário.
"""
import shutil
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent  # raiz do repo
SRC_FILE = PROJECT_ROOT / "docs" / "definicoes" / "ativos_a_serem_criados.md"
DST_DIR = PROJECT_ROOT / "ativos_imagens" / "resources" / "definicoes"
DST_FILE = DST_DIR / "ativos_a_serem_criados.md"


def main():
    if not SRC_FILE.exists():
        print(f"Arquivo fonte não encontrado: {SRC_FILE}")
        sys.exit(1)

    DST_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SRC_FILE, DST_FILE)
    print(f"✅ Inventário sincronizado para {DST_FILE.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main() 