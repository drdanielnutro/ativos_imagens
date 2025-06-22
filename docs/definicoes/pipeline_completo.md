# Plano de Produção Unificado de Assets para Aplicação Infantil
# Blueprint Técnico para Agente Autônomo de Geração de Ativos

## Seção 1: Arquitetura do Agente e Princípios de Design de Ferramentas

### 1.1. Visão Executiva e Objetivo Principal
O objetivo deste documento é detalhar o **blueprint técnico para a construção de um Agente de Software Autônomo** especializado na geração de um conjunto completo de assets digitais (imagens PNG, vetores SVG, áudio MP3 e animações Lottie) para uma aplicação infantil. Este plano descreve a arquitetura das **ferramentas (`FunctionTool`)** que o agente utilizará, combinando modelos de Inteligência Artificial com pós-processamento programático para garantir consistência, alta qualidade e performance. Cada seção subsequente deve ser interpretada como a especificação para a implementação de uma ferramenta que o agente irá invocar.

### 1.2. O Princípio Central de Operação: Seleção de Ferramentas Híbrida (`Tool-Use`)
A arquitetura do agente se baseia em uma estratégia de **seleção de ferramentas (`Tool-Use`) híbrida**. O agente selecionará a `FunctionTool` mais adequada para cada tipo de ativo, em vez de uma abordagem única.
*   **Ferramentas IA-Assistidas:** Para ativos complexos e orgânicos (ex: animações de personagens, ilustrações temáticas), o agente usará ferramentas que invocam modelos de IA para criar a base criativa, que é subsequentemente refinada e convertida para o formato técnico final.
*   **Ferramentas de Geração Programática:** Para ativos geometricamente definíveis (ex: animações de UI, spinners, ícones simples), o agente usará ferramentas que criam o conteúdo diretamente por código. Esta abordagem garante perfeição matemática, tamanho de arquivo mínimo e performance máxima.

### 1.3. Estratégia de Implementação de Ferramentas: Plataforma Unificada
As ferramentas do agente serão construídas sobre uma plataforma unificada para centralizar e simplificar o acesso aos modelos generativos.
*   **Modelos de IA:** As ferramentas que dependem de IA encapsularão chamadas à API da plataforma **Replicate** para todas as tarefas de geração de imagem, vídeo e áudio. Isso garante um faturamento consolidado e uma interface de API consistente.
*   **Processamento Local:** Para o pós-processamento e geração programática, as ferramentas serão implementadas utilizando bibliotecas Python open-source (ex: `python-lottie`, `pydub`, `opencv-python`), que formarão o núcleo da caixa de ferramentas do agente.

### 1.4. Estratégia de Consistência (Lógica Interna do Agente)
A **lógica interna do agente** e o design de suas ferramentas garantirão a coesão entre os assets. A consistência será alcançada através de três pilares de implementação:
*   **Consistência de Personagem (Ferramenta LoRA):** O agente terá acesso a uma ferramenta para treinar um modelo LoRA (Low-Rank Adaptation) para o mascote principal, garantindo que sua aparência seja idêntica em todas as suas diferentes poses e expressões.
*   **Consistência de Estilo (Modificadores de Prompt):** Para todos os ativos visuais (PNG e SVG), serão utilizados modificadores de estilo padronizados nos prompts para garantir uma linguagem visual uniforme (ex: "cartoon style", "flat colors").
*   **Consistência de Paleta e Padrões Técnicos:** As ferramentas de geração aplicarão uma paleta de cores pré-definida a todos os ativos SVG. Padrões técnicos de áudio (bitrate, normalização) e animação (duração, easing) serão codificados dentro das ferramentas para uma experiência de usuário coesa.

### 1.5. Estratégia de Otimização Final (Output das Ferramentas)
As ferramentas de geração de animação do agente serão projetadas para produzir o formato **`.lottie`** (dotLottie) como saída final. Este formato, que é um arquivo ZIP contendo o JSON da animação, oferece compressão superior, reduzindo drasticamente o tamanho do arquivo e melhorando os tempos de carregamento na aplicação cliente.

---

## Seção 2: Especificação das Ferramentas de Geração de Imagem (PNG)

Esta seção detalha as especificações para as ferramentas Python que o agente usará para criar arquivos PNG.

### 2.1. Ferramentas para Geração do Mascote com Consistência (PROF)

#### Ferramenta 1: `train_lora_model(dataset_zip_path: str, trigger_word: str) -> str`
Esta função será responsável por treinar o modelo LoRA para garantir a consistência do personagem.
*   **Lógica Interna:** Invocará a API do Replicate (`ostris/flux-dev-lora-trainer`).
*   **Parâmetros:**
    *   `dataset_zip_path`: Caminho para um arquivo ZIP contendo 12-20 imagens de referência do mascote.
    *   `trigger_word`: Palavra-chave para ativar o modelo (ex: `PROF`).
*   **Retorno:** O ID ou URL do modelo LoRA treinado, a ser usado pela próxima ferramenta.

#### Ferramenta 2: `generate_mascot_png(lora_model_id: str, state: str) -> str`
Esta função irá gerar os diferentes estados visuais do mascote.

**Tabela 1: Especificação da Ferramenta `generate_mascot_png`**
| Valor do Parâmetro `state` | Descrição do Estado                 | Lógica Interna (Prompt para o modelo LoRA)                                                     |
| :------------------------- | :---------------------------------- | :--------------------------------------------------------------------------------------------- |
| `thinking`                 | Mascote em pose pensativa.          | `PROF, thinking pose, hand on chin, contemplative expression, cartoon style, clean background` |
| `welcoming`                | Mascote acenando de forma amigável. | `PROF, waving hello, friendly smile, welcoming gesture, cartoon style, clean background`       |
| `celebrating`              | Mascote em pose de celebração.      | `PROF, party hat, confetti, celebration pose, happy expression, cartoon style`                 |
| `sleeping`                 | Mascote dormindo pacificamente.     | `PROF, sleeping, closed eyes, Zzz symbols, peaceful expression, cartoon style`                 |
| `surprised`                | Mascote com expressão de surpresa.  | `PROF, surprised expression, wide open mouth, shocked, cartoon style`                          |

### 2.2. Ferramenta para Sprites, Efeitos e Backgrounds

#### Ferramenta 3: `generate_generic_png(asset_name: str) -> str`
Esta função irá gerar os demais ativos PNG que não dependem do modelo LoRA.

**Tabela 2: Especificação da Ferramenta `generate_generic_png`**
| Valor do Parâmetro `asset_name` | Descrição do Ativo              | Lógica Interna (Prompt para o modelo de imagem)                                                                       |
| :------------------------------ | :------------------------------ | :-------------------------------------------------------------------------------------------------------------------- |
| `sparkle_particle`              | Partícula de brilho individual. | `single sparkle particle, bright glow, magical effect, high contrast, on a clean white background`                    |
| `badge_glow`                    | Efeito de brilho para emblemas. | `soft circular glow effect, radial gradient, aura for a badge, on a clean white background`                           |
| `confetti_pieces`               | Sprite sheet 4x4 de confetes.   | `sprite sheet of falling confetti pieces, 16 frames, 4x4 grid, animation sequence, colorful particles, cartoon style` |
| `gradient_mesh_1`               | Fundo com gradiente suave.      | `abstract background, soft gradient mesh, pastel colors, blue and purple, clean and simple`                           |
| `gradient_mesh_2`               | Fundo com gradiente suave.      | `abstract background, soft gradient mesh, warm colors, orange and yellow, clean and simple`                           |

### 2.3. Toolchain de Pós-Processamento de PNGs
As ferramentas `generate_mascot_png` e `generate_generic_png` irão orquestrar uma sequência de funções utilitárias internas para garantir a qualidade final do ativo:
1.  **Remoção de Fundo:** Utilização da biblioteca `rembg` para mascote e sprites.
2.  **Otimização de Tamanho:** Invocação da API do **TinyPNG**.
3.  **Geração Multi-Resolução:** Criação de versões `@1x`, `@2x`, e `@3x` com a biblioteca `Pillow`.
4.  **Validação Final:** Verificação de transparência e conformidade com o tamanho de arquivo.

---

## Seção 3: Especificação das Ferramentas de Geração Vetorial (SVG)

### 3.1. Lógica Interna da Ferramenta `generate_svg`
A ferramenta `generate_svg` seguirá um pipeline interno de três etapas:

**Etapa 1: Geração da Imagem Raster Base**
*   **Lógica:** A ferramenta invocará um modelo de imagem no Replicate (ex: `stability-ai/sdxl`).
*   **Modificador de Estilo Padrão (Hardcoded no Prompt):** `vector art style, clean line art, flat solid colors, high contrast, white background`.

**Etapa 2: Vetorização Automática**
*   **Lógica:** A ferramenta enviará a imagem raster para a **API do Vectorizer.AI** devido à sua alta fidelidade.
*   **Alternativa (Implementação Local):** Pode-se usar bibliotecas como `pyautotrace` ou `VTracer`.

**Etapa 3: Pós-Processamento e Otimização do SVG**
*   **Lógica:** A ferramenta utilizará a biblioteca **Scour** (Python) para limpar e otimizar o SVG.
*   **Padronização de Paleta:** A ferramenta irá mapear as cores do SVG resultante para uma paleta de projeto pré-definida.

### 3.2. Ferramenta para Geração de Ativos SVG

#### Ferramenta 4: `generate_svg(asset_name: str, category: str) -> str`
Esta função irá gerar todos os ativos no formato SVG.

**Tabela 3: Especificação da Ferramenta `generate_svg`**
| Valor do Parâmetro `asset_name` | Valor do Parâmetro `category` | Lógica Interna (Prompt para geração da imagem base)                          |
| :------------------------------ | :---------------------------- | :--------------------------------------------------------------------------- |
| `icon_book`                     | `Ícone`                       | `A simple icon of an open book`                                              |
| `icon_pencil`                   | `Ícone`                       | `A simple icon of a pencil`                                                  |
| `pattern_stars`                 | `Padrão`                      | `A seamless pattern of cute, smiling stars and crescent moons`               |
| `frame_corner_floral`           | `Moldura`                     | `An ornate decorative corner piece for a frame, with floral and vine motifs` |

---

## Seção 4: Especificação das Ferramentas de Geração de Áudio (MP3)

### 4.1. Lógica Interna da Ferramenta `generate_audio_mp3`
A ferramenta `generate_audio_mp3` seguirá um pipeline interno de duas etapas:

**Etapa 1: Geração do Áudio Bruto (WAV)**
*   **Lógica:** A ferramenta invocará o modelo **`stackadoc/stable-audio-open-1.0`** no Replicate.

**Etapa 2: Pós-Processamento e Conversão para MP3**
A ferramenta utilizará a biblioteca **PyDub** para aplicar as seguintes operações no áudio bruto:
1.  Garantir áudio estéreo a 44.1kHz.
2.  Ajustar para a duração alvo.
3.  Normalizar o pico para **-3.0 dBFS**.
4.  Aplicar **fade-in/out de 10ms**.
5.  Criar loop contínuo com crossfade (se aplicável, como para `processing_loop`).
6.  Exportar para MP3 **128 kbps CBR**.

### 4.2. Ferramenta para Geração de Efeitos Sonoros (MP3)

#### Ferramenta 5: `generate_audio_mp3(asset_name: str, duration_seconds: float) -> str`
Esta função irá gerar todos os efeitos sonoros.

**Tabela 4: Especificação da Ferramenta `generate_audio_mp3`**
| Valor do Parâmetro `asset_name` | Parâmetro `duration_seconds` | Lógica Interna (Prompt para o modelo de áudio)                          |
| :------------------------------ | :--------------------------- | :---------------------------------------------------------------------- |
| `button_tap`                    | 0.5                          | `soft gentle button click UI sound, pleasant interface feedback, short` |
| `success`                       | 1.5                          | `cheerful success bell chime, pleasant notification, achievement sound` |
| `error_gentle`                  | 1.0                          | `gentle error sound, soft musical warning, kind notification`           |
| `notification`                  | 1.0                          | `gentle notification bell, soft chime, pleasant alert sound`            |
| `achievement`                   | 2.5                          | `celebratory fanfare, achievement fanfare, success celebration music`   |
| `processing_loop`               | 3.0                          | `ambient processing sound, soft background loop, gentle electronic hum` |

---

## Seção 5: Especificação das Ferramentas de Geração de Animação (Lottie)

Esta seção detalha as duas principais metodologias de ferramentas para a criação de 18 animações Lottie, utilizando a estratégia híbrida.

### 5.1. Toolchain A: Ferramenta de Geração IA-Vetorizada (Para Animações de Personagem)
Esta metodologia será encapsulada em uma ferramenta como `generate_ai_driven_lottie(image_path: str, prompt: str)`. Ela é usada para animações orgânicas e complexas, como as do mascote.

*   **Etapa 1: Geração de Vídeo Fonte:**
    *   **Lógica:** A ferramenta invocará um modelo Imagem-para-Vídeo no Replicate (ex: `minimax/video-01-live`), usando a imagem estática do mascote e um prompt de animação.
    *   **Pós-processamento de Vídeo:** A ferramenta usará um modelo secundário no Replicate (ex: `tahercoolguy/video_background_remover_appender`) para aplicar um fundo verde sólido (`#00FF00`), simplificando a vetorização.

*   **Etapa 2: Extração de Frames:**
    *   **Lógica:** A ferramenta utilizará a biblioteca `opencv-python` para decompor o vídeo MP4 em uma sequência de frames PNG.

*   **Etapa 3: Vetorização Frame a Frame:**
    *   **Lógica:** A ferramenta invocará o motor de vetorização **Potrace** (via `python-lottie`) para converter cada frame PNG em um SVG correspondente.

*   **Etapa 4: Compilação em Animação Lottie:**
    *   **Lógica:** A ferramenta utilizará o modelo de objetos da biblioteca `python-lottie` para criar uma animação Lottie programaticamente, onde cada frame da animação é uma camada vetorial (`ShapeLayer`) visível por apenas um único frame.

### 5.2. Toolchain B: Ferramenta de Geração Programática Direta (Para Animações de UI e Geométricas)
Esta metodologia será usada para ferramentas como `generate_geometric_lottie(animation_type: str, ...params)`. Ela é ideal para animações com formas e movimentos matematicamente definíveis.

*   **Lógica:** A ferramenta utilizará o modelo de objetos da biblioteca `python-lottie` para construir a animação diretamente em código Python. Formas (`Path`, `Ellipse`), transformações (`position`, `scale`) e modificadores (`TrimPath`) serão definidos e animados com `Keyframes`.
    *   **Exemplo (`success_checkmark`):** A ferramenta animará a propriedade `end` de um `TrimPath` de 0 a 100 para "desenhar" o caminho.
    *   **Exemplo (`error_shake`):** A ferramenta animará a propriedade `position` de uma camada com múltiplos keyframes para criar um efeito de vibração.
    *   **Exemplo (`loading_spinner`):** A ferramenta animará a propriedade `rotation` de uma forma para criar um giro contínuo.

### 5.3. Pós-Produção e Otimização (Lógica Interna das Ferramentas Lottie)
1.  **Otimização Programática:** Todas as ferramentas Lottie usarão as funções de otimização da biblioteca `python-lottie` (`--optimize level 2`) para truncar a precisão de ponto flutuante e remover metadados.
2.  **Empacotamento para `.lottie`:** Como etapa final, a ferramenta empacotará o `.json` otimizado em um arquivo `.lottie` usando o módulo `zipfile` do Python para máxima compressão.

### 5.4. Especificação das Ferramentas de Geração Lottie

**Tabela 5: Matriz de Especificação de Ferramentas e Metodologia para Animações Lottie**
| Nome da Animação (Parâmetro `asset_name`) | Categoria    | Metodologia da Ferramenta | Feature Lottie Primária (Lógica Interna) | Parâmetros Adicionais da Ferramenta                        |
| :---------------------------------------- | :----------- | :------------------------ | :--------------------------------------- | :--------------------------------------------------------- |
| `mascot_idle`                             | Mascote      | IA-Vetorizado             | Sequência de Imagens Vetoriais           | `image_path`, `prompt: "breathing gently"`                 |
| `mascot_bounce`                           | Mascote      | IA-Vetorizado             | Sequência de Imagens Vetoriais           | `image_path`, `prompt: "bouncing with squash and stretch"` |
| `mascot_wave`                             | Mascote      | IA-Vetorizado             | Sequência de Imagens Vetoriais           | `image_path`, `prompt: "waving hello"`                     |
| `mascot_thinking`                         | Mascote      | IA-Vetorizado             | Sequência de Imagens Vetoriais           | `image_path`, `prompt: "thinking pose, tapping chin"`      |
| `mascot_celebration`                      | Mascote      | IA-Vetorizado             | Sequência de Imagens Vetoriais           | `image_path`, `prompt: "celebrating happily, jumping"`     |
| `loading_spinner`                         | Carregamento | Programático              | `Transform.rotation`, `GradientStroke`   | `duration`, `loop`, `colors`                               |
| `loading_bounce`                          | Carregamento | Programático              | `Transform.position`, `Keyframe`         | `duration`, `loop`, `color`                                |
| `loading_wave`                            | Carregamento | Programático              | `Path` (animação de vértices)            | `duration`, `loop`, `color`                                |
| `loading_thinking`                        | Carregamento | Programático              | `ShapeLayer`, `Transform.opacity`        | `duration`, `loop`                                         |
| `loading_camera`                          | Carregamento | Programático              | `Path` (morphing), `Mask`                | `duration`                                                 |
| `loading_ai`                              | Carregamento | Programático              | `Path`, `TrimPath`, `Repeater`           | `duration`, `loop`                                         |
| `touch_ripple`                            | Feedback     | Programático              | `Transform.scale`, `Transform.opacity`   | `duration`, `color`                                        |
| `success_checkmark`                       | Feedback     | Programático              | `TrimPath`                               | `duration`, `color`                                        |
| `error_shake`                             | Feedback     | Programático              | `Transform.position`                     | `duration`                                                 |
| `hint_pulse`                              | Feedback     | Programático              | `Transform.scale`, `Transform.opacity`   | `duration`, `loop`                                         |
| `achievement_unlock`                      | Achievement  | Programático              | `Mask`, `Transform.scale`                | `duration`                                                 |
| `level_up`                                | Achievement  | Programático              | `Transform` (escala, posição), `Opacity` | `duration`                                                 |
| `star_burst`                              | Achievement  | Programático              | `Star`, `Transform` (rotação, escala)    | `duration`                                                 |