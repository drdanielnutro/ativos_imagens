#!/usr/bin/env python3
"""Teste que vetoriza prof.png usando o *mesmo* método do pipeline completo
(MascotAnimator._vectorize_frames) e mantém o SVG gerado em disco para
inspeção manual.

O arquivo resultante ficará em:
    tests/artifacts/vectorization/frame_0000.svg
"""

import shutil
from pathlib import Path
import os

import pytest

from ativos_imagens.tools.mascot_animator import MascotAnimator

TEST_PNG = Path("prof.png")
OUTPUT_DIR = Path("tests/artifacts/vectorization")

@pytest.mark.skipif(not TEST_PNG.exists(), reason="Arquivo prof.png não encontrado")
def test_vectorization_keep_file():
    # Preparar diretórios
    frames_dir = OUTPUT_DIR / "frames"
    svg_dir = OUTPUT_DIR / "svgs"
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
    svg_dir.mkdir(parents=True, exist_ok=True)
    frames_dir.mkdir(parents=True, exist_ok=True)

    # Copiar imagem
    shutil.copy(TEST_PNG, frames_dir / "frame_0000.png")

    # Vetorizar usando o MESMO método do pipeline mascote
    MascotAnimator()._vectorize_frames(str(frames_dir), str(svg_dir), frame_count=1)

    out_svg = svg_dir / "frame_0000.svg"
    assert out_svg.exists(), "SVG não foi gerado"

    size_kb = out_svg.stat().st_size / 1024
    print(f"SVG salvo em: {out_svg} ({size_kb:.1f} KB)") 