#!/usr/bin/env bash
set -e

echo "[startup.sh] Instalando utilitários de linha de comando necessários…"

# Atualiza índices do apt
sudo apt-get update -y

# Instala ImageMagick (convert), mkbitmap e Potrace
sudo apt-get install -y imagemagick mkbitmap potrace

# (Opcional) Instalar SVGO para otimização extra de SVG
# sudo npm install -g svgo

echo "[startup.sh] Instalação concluída."
