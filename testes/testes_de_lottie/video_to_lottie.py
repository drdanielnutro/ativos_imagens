#!/usr/bin/env python3
"""
Converte um vídeo em animação Lottie usando lottie_convert.py e Python-Lottie.

Suporta diferentes modos de vetorização de imagens via lottie_convert:

  * polygon: vetoriza cada cor como polígonos (Potrace) – qualidade alta
  * trace:   vetorização Potrace clássica – bom para contornos definidos
  * pixel:   vetorização em retângulos (estilo pixel art) – mais rápido
  * none:    mantém bitmaps internos (sem vetorizar) – arquivos maiores

Também controla número de cores, FPS de extração e nível de otimização do JSON.

Exemplo de uso:
    python video_to_lottie.py \
      --input-video meu_video.mp4 \
      --output saida.lottie \
      --mode pixel \
      --colors 6 \
      --fps 12 \
      --optimize 2
"""
import argparse
import os
import sys
import tempfile
import shutil
import json
import zipfile
import subprocess

import cv2
from PIL import Image

def extract_frames(video_path: str, frames_dir: str, target_fps: int) -> int:
    cap = cv2.VideoCapture(video_path)
    video_fps = cap.get(cv2.CAP_PROP_FPS) or 24
    interval = video_fps / target_fps
    saved = 0
    count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if count >= saved * interval:
            path = os.path.join(frames_dir, f"frame_{saved:04d}.png")
            cv2.imwrite(path, frame)
            saved += 1
        count += 1
    cap.release()
    return saved

def subsample_frames(frames_dir: str, frame_count: int) -> int:
    kept = 0
    for i in range(frame_count):
        src = os.path.join(frames_dir, f"frame_{i:04d}.png")
        if not os.path.exists(src):
            continue
        if i % 2 == 0:
            os.remove(src)
        else:
            dst = os.path.join(frames_dir, f"frame_{kept:04d}.png")
            os.rename(src, dst)
            kept += 1
    return kept

def make_gif(frames_dir: str, frame_count: int, gif_path: str, duration_ms: int) -> None:
    images = []
    for i in range(frame_count):
        images.append(Image.open(os.path.join(frames_dir, f"frame_{i:04d}.png")))
    images[0].save(
        gif_path,
        save_all=True,
        append_images=images[1:],
        duration=duration_ms,
        loop=0,
        optimize=False
    )

def run_lottie_convert(
    gif_path: str,
    json_path: str,
    colors: int,
    optimize_level: int,
    mode: str
) -> None:
    executable = os.path.join(os.path.dirname(sys.executable), "lottie_convert.py")
    cmd = [
        executable,
        gif_path,
        json_path,
        "--input-format", "bmp",
        "--output-format", "lottie",
    ]
    if mode in ("polygon", "trace", "pixel"):
        cmd += ["--bmp-mode", mode]
    cmd += ["--bmp-n-colors", str(colors), "--optimize", str(optimize_level)]
    subprocess.run(cmd, check=True)

def create_dotlottie(json_path: str, lottie_path: str) -> None:
    with open(json_path, "r") as f:
        data = json.load(f)
    minified = json.dumps(data, separators=(",", ":"))
    manifest = {"animations": [{"id": "a", "path": "a.json"}], "version": "1.0"}
    with zipfile.ZipFile(
        lottie_path,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9
    ) as zf:
        zf.writestr("manifest.json", json.dumps(manifest, separators=(",", ":")))
        zf.writestr("a.json", minified)

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gera animação Lottie a partir de vídeo (configurável: mode, colors, optimize)"
    )
    parser.add_argument(
        "-i", "--input-video", required=True,
        help="Caminho para o arquivo de vídeo"
    )
    parser.add_argument(
        "-o", "--output", required=True,
        help="Caminho de saída (.json ou .lottie)"
    )
    parser.add_argument(
        "--colors", type=int, default=8,
        help="Número de cores para vetorizar (default: 8)"
    )
    parser.add_argument(
        "--fps", type=int, default=12,
        help="FPS para extração de frames (default: 12)"
    )
    parser.add_argument(
        "--optimize", type=int, default=2,
        help="Nível de otimização do JSON (0,1,2 – default: 2)"
    )
    parser.add_argument(
        "--mode", choices=("polygon", "trace", "pixel", "none"), default="polygon",
        help="Modo de vetorização BMP: polygon, trace, pixel ou none (default: polygon)"
    )
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as tmpdir:
        frames_dir = os.path.join(tmpdir, "frames")
        os.makedirs(frames_dir)
        count = extract_frames(args.input_video, frames_dir, args.fps)
        count = subsample_frames(frames_dir, count)
        if count == 0:
            print("Erro: nenhum frame extraído.", file=sys.stderr)
            sys.exit(1)

        temp_gif = os.path.join(tmpdir, "all_frames.gif")
        make_gif(frames_dir, count, temp_gif, duration_ms=int(1000/args.fps))
        temp_json = os.path.join(tmpdir, "animation.json")
        run_lottie_convert(temp_gif, temp_json, args.colors, args.optimize, args.mode)

        output = args.output
        if output.lower().endswith(".lottie"):
            create_dotlottie(temp_json, output)
            print(f"Arquivo .lottie gerado: {output}")
        else:
            shutil.copy2(temp_json, output)
            print(f"Arquivo JSON gerado: {output}")

if __name__ == "__main__":
    main()