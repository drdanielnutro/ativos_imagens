# Tutorial Passo a Passo – Geração Automática de SVG

> Baseado no relatório **"Geração Automática de SVG.txt"** (deep_research)
> Diretório de trabalho: `testes/testes_de_svg/`
>
> Este guia mostra como gerar todos os SVGs listados em `lista_svg_para_geracao.md` usando Python e ferramentas gratuitas/opcionais.

---

## 0. Pré-requisitos

1. **Python 3.10 ou 3.11** (evite 3.13 por causa do módulo `audioop` de outras rotinas).
2. **Git** e **Node ≥ 18** (para SVGO opcional).
3. Conta na **Replicate** com créditos e token de API.
4. (Opcional) Conta na **Vectorizer.AI** se preferir vetorização via API cloud.
5. Binários **Potrace** e/ou **Autotrace** instalados (Homebrew: `brew install potrace autotrace`).

---

## 1. Criar ambiente Python

```bash
cd /Users/institutorecriare/VSCodeProjects/criador_agentes/ativos_imagens
python3 -m venv .venv_svg
source .venv_svg/bin/activate
pip install --upgrade pip
# Dependências principais
pip install replicate requests pillow pyautotrace pypotrace scour
# (Opcional) ferramentas extras
brew install svgo # se quiser usar SVGO para otimização
```

---

## 2. Configurar tokens e variáveis

```bash
# Token da Replicate
export REPLICATE_API_TOKEN="SEU_TOKEN_AQUI"
# (Opcional) Token da Vectorizer.AI, se usar API
export VECTORIZER_AI_TOKEN="SEU_TOKEN_AI_AQUI"
```

---

## 3. Gerar a imagem raster base

Exemplo para **`pattern_dots.svg`**:

```python
import replicate, requests, io, PIL.Image as Image
prompt = "seamless pattern of colorful polka dots, vector art style, flat solid colors, high contrast, white background"
model = "stability-ai/sdxl"
img_url = replicate.run(model, input={"prompt": prompt, "width":1024, "height":1024})
img = Image.open(io.BytesIO(requests.get(img_url).content))
img.save("pattern_dots_base.png")
```
> Dica: use sempre *vector art*, *flat colors*, *white background* no prompt.

---

## 4. Vetorizar a imagem

### 4.1 Modo **offline** (Autotrace / Potrace)

```bash
# Exemplo com Autotrace (cores)
autotrace pattern_dots_base.png \
  --output-file pattern_dots.svg \
  --output-format svg \
  --color-count 16 \
  --background-color FFFFFF
```
* Para arte em **apenas contorno**, use Potrace:
```bash
mkbitmap -s 2 -f 2 -o tmp.pbm pattern_dots_base.png
potrace tmp.pbm -s -o pattern_dots.svg --flat --turnpolicy minority
rm tmp.pbm
```

### 4.2 Modo **cloud** (Vectorizer.AI)

```python
import requests
headers = {"Authorization": f"Bearer {os.environ['VECTORIZER_AI_TOKEN']}"}
files = {"image": open("pattern_dots_base.png", "rb")}
resp = requests.post("https://vectorizer.ai/api/v1/trace", headers=headers, files=files)
with open("pattern_dots.svg", "wb") as f:
    f.write(resp.content)
```

---

## 5. Otimizar o SVG

### 5.1 Scour (Python)
```bash
scour -i pattern_dots.svg -o pattern_dots_optimized.svg --enable-id-stripping --enable-comment-stripping --shorten-ids --indent=none
mv pattern_dots_optimized.svg pattern_dots.svg
```

### 5.2 SVGO (Node) – opcional
```bash
svgo -i pattern_dots.svg -o pattern_dots.svg --multipass
```

---

## 6. Padronizar paleta de cores (opcional)

```python
from lxml import etree
palette = ["#4A90F2", "#FF8A3D", "#7ED321", "#9B59B6", "#FFC107", "#00D4AA"]
svg = etree.parse("pattern_dots.svg")
for elt in svg.xpath('//*[@fill]'):
    old = elt.attrib['fill']
    if old.startswith('#') and len(old)==7:
        # calcula cor mais próxima da paleta (simples diff RGB)
        r,g,b = int(old[1:3],16),int(old[3:5],16),int(old[5:],16)
        best=min(palette, key=lambda c: sum(abs(int(c[i:i+2],16)-v) for i,v in zip((1,3,5),(r,g,b))))
        elt.attrib['fill']=best
svg.write("pattern_dots.svg")
```

---

## 7. Validar visualmente

Abra o arquivo no navegador ou use `cairosvg` para gerar um PNG rápido:
```bash
pip install cairosvg
cairosvg pattern_dots.svg -o preview.png
open preview.png  # macOS
```

---

## 8. Repetir para todos os itens

1. Consulte `lista_svg_para_geracao.md`.  
2. Substitua `prompt`, `file_name` e repita passos 3-7.

Para automatizar, crie um script Python que leia o Markdown, gere as imagens e siga o pipeline – mas este tutorial cobre o processo manual/controlado.

---

## 9. Organização de arquivos

Após gerar e otimizar:

```bash
mkdir -p professor_virtual/assets/images/ui/patterns
mkdir -p professor_virtual/assets/icons/navigation
# … crie pastas conforme necessidade
mv pattern_*.svg professor_virtual/assets/images/ui/patterns/
mv icon_* professor_virtual/assets/icons/navigation/
```

---

## 10. Versionamento Git

```bash
git add professor_virtual/assets
git commit -m "Add first batch of SVG assets (patterns + icons)"
```

---

## Dicas Finais

* **Consistência** – Use sempre os mesmos termos de estilo nos prompts.
* **Tileabilidade** – Para padrões, verifique se os lados se encaixam; se não, edite o SVG duplicando formas na borda.
* **Nomes exatos** – Salve o arquivo exatamente com o nome esperado (`file_name`).
* **SVG < 50 KB** – Use otimização até que cada arquivo esteja abaixo dessa marca.
* **Backup** – Mantenha a versão raster `.png` num diretório `backup_raster/` caso precise re-vetorizar.

Pronto!  Siga estes passos para produzir todos os SVGs necessários com qualidade consistente e tamanho otimizado. 