#!/usr/bin/env python3
"""Teste unitário: vetorização de um único frame usando o mesmo pipeline do MascotAnimator.

Executa a função _vectorize_frames diretamente para garantir que as
ferramentas externas (convert/imagemagick, mkbitmap, potrace) estejam
instaladas e funcionando.
"""
import os
import shutil
import tempfile
from pathlib import Path

import pytest

from ativos_imagens.tools.mascot_animator import MascotAnimator

# Caminho da imagem de teste (ajuste se necessário)
TEST_PNG = Path("prof.png")

@pytest.mark.skipif(not TEST_PNG.exists(), reason="Arquivo prof.png não encontrado")
def test_single_frame_vectorization():
    animator = MascotAnimator()

    with tempfile.TemporaryDirectory() as tmpdir:
        frames_dir = Path(tmpdir) / "frames"
        svg_dir = Path(tmpdir) / "svgs"
        frames_dir.mkdir()
        svg_dir.mkdir()

        # Copiar imagem para o frame_0000.png
        shutil.copy(TEST_PNG, frames_dir / "frame_0000.png")

        # Chamar função de vetorização com frame_count=1
        animator._vectorize_frames(str(frames_dir), str(svg_dir), frame_count=1)

        out_svg = svg_dir / "frame_0000.svg"
        assert out_svg.exists(), "SVG não foi gerado"

        size_kb = out_svg.stat().st_size / 1024
        print(f"SVG gerado: {out_svg} ({size_kb:.1f} KB)") 