# **Professor Virtual - Especificação de Requisitos de Assets**

**Versão do Documento:** 1.1  
**Última Atualização:** 2025-01-21  
**Status:** Completo  
**Projeto:** Professor Virtual - Assistente de Aprendizagem com IA

## **Sumário Executivo**

Este documento detalha o inventário completo de assets digitais necessários para o desenvolvimento do aplicativo móvel "Professor Virtual". O objetivo é fornecer uma especificação clara e acionável para as equipes de design e desenvolvimento, garantindo consistência e qualidade. Todos os assets devem ser amigáveis para crianças de 7 a 11 anos, promovendo uma experiência de aprendizado imersiva e engajadora.

### **Métricas do Projeto**
- **Total de Assets a Criar/Finalizar:** 62
- **Assets Críticos Pendentes:** 20
- **Formatos Primários:** PNG, SVG, MP3, Lottie (JSON)

---

## **Status Atual dos Assets**

### ✅ Assets Prontos para Uso

#### **Fontes (`assets/fonts/`)**
- ✓ `Nunito-Bold.ttf`
- ✓ `Nunito-Regular.ttf`
- ✓ `Poppins-Medium.ttf`
- ✓ `Poppins-Regular.ttf`

#### **Badges de Conquista (`assets/images/achievements/`)**
- ✓ 15 arquivos PNG (512x512px) finalizados.

#### **Ícones do Aplicativo**
- ✓ Ícones para Android (todas as resoluções).
- ✓ Ícones para iOS (todas as resoluções).

### ⚠️ Placeholders a Substituir

#### **Estados do Mascote (`assets/images/mascot/`)**
- ✓ 5 arquivos PNG (512x512px) com qualidade de placeholder, que precisam ser substituídos pelas versões finais.
  - `prof_curious.png`
  - `prof_encouraging.png`
  - `prof_excited.png`
  - `prof_explaining.png`
  - `prof_happy.png`

---

## **Especificação de Assets por Categoria**

### 1. 🎵 Efeitos Sonoros (`SFX`)
**Local:** `assets/sounds/feedback/`  
**Formato:** MP3, 44.1kHz, Stereo, Normalizado para -3dB

| ID     | Nome do Arquivo       | Descrição                               | Duração    | Prioridade |
| :----- | :-------------------- | :-------------------------------------- | :--------- | :--------- |
| SFX-01 | `button_tap.mp3`      | Clique suave e agradável.               | ~0.5s      | Crítica    |
| SFX-02 | `success.mp3`         | Som alegre de conclusão.                | 1-2s       | Crítica    |
| SFX-03 | `error_gentle.mp3`    | Indicação de erro suave, não alarmante. | ~1s        | Crítica    |
| SFX-04 | `notification.mp3`    | Notificação de sino gentil.             | ~1s        | Crítica    |
| SFX-05 | `achievement.mp3`     | Fanfarra celebratória de conquista.     | 2-3s       | Crítica    |
| SFX-06 | `camera_shutter.mp3`  | Som de captura de câmera de celular.    | ~0.5s      | Crítica    |
| SFX-07 | `page_transition.mp3` | Transição "swoosh" de página.           | ~0.5s      | Importante |
| SFX-08 | `pop_up.mp3`          | Efeito de estouro de bolha.             | ~0.5s      | Importante |
| SFX-09 | `processing_loop.mp3` | Zumbido eletrônico suave para loop.     | ~3s (loop) | Importante |

### 2. 🦸 Mascote "Prof" (`MAS`)

#### **Imagens Estáticas**
**Local:** `assets/images/mascot/`  
**Formato:** PNG, 512x512px, Fundo Transparente

| ID     | Nome do Arquivo        | Emoção/Estado | Status          | Prioridade |
| :----- | :--------------------- | :------------ | :-------------- | :--------- |
| MAS-01 | `prof_happy.png`       | Feliz         | **Placeholder** | Crítica    |
| MAS-02 | `prof_curious.png`     | Curioso       | **Placeholder** | Crítica    |
| MAS-03 | `prof_encouraging.png` | Encorajador   | **Placeholder** | Crítica    |
| MAS-04 | `prof_excited.png`     | Empolgado     | **Placeholder** | Crítica    |
| MAS-05 | `prof_explaining.png`  | Explicando    | **Placeholder** | Crítica    |
| MAS-06 | `prof_thinking.png`    | Pensativo     | A ser criado    | Importante |
| MAS-07 | `prof_welcoming.png`   | Acolhedor     | A ser criado    | Importante |
| MAS-08 | `prof_celebrating.png` | Celebrando    | A ser criado    | Importante |
| MAS-09 | `prof_sleeping.png`    | Dormindo      | A ser criado    | Opcional   |
| MAS-10 | `prof_surprised.png`   | Surpreso      | A ser criado    | Opcional   |

#### **Animações do Mascote**
**Local:** `assets/images/mascot/animations/`  
**Formato:** Lottie JSON, Viewport 512x512px

| ID     | Nome do Arquivo           | Descrição da Animação                    | Duração | Loop | Prioridade |
| :----- | :------------------------ | :--------------------------------------- | :------ | :--- | :--------- |
| MAS-11 | `mascot_idle.json`        | Respiração suave e piscadas.             | ~3s     | Sim  | Crítica    |
| MAS-12 | `mascot_bounce.json`      | Pulo de empolgação com squash/stretch.   | ~1s     | Não  | Importante |
| MAS-13 | `mascot_wave.json`        | Aceno amigável de boas-vindas.           | ~2s     | Não  | Importante |
| MAS-14 | `mascot_thinking.json`    | Lâmpada aparece e brilha sobre a cabeça. | ~3s     | Sim  | Importante |
| MAS-15 | `mascot_celebration.json` | Explosão de confetes e pulo de alegria.  | ~3s     | Não  | Importante |

### 2.1 🦸 Tabela Unificada de Animações do Mascote (Lottie)

| ID         | File Name               | Type           | Description & Base Pose (Prompt Details)                                                  | Animation Prompt (for Video Gen)                                      |
| ---------- | ----------------------- | -------------- | ----------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| MAS-ANI-01 | mascot_idle.json        | lottie_mascote | **Pose:** `action: "standing still, friendly pose"`, `objects_location: "book under arm"` | "subtle breathing motion, seamless loop, character is mostly still"   |
| MAS-ANI-02 | mascot_bounce.json      | lottie_mascote | **Pose:** `action: "in a ready-to-jump pose"`                                             | "a happy jump with a little squash and stretch"                       |
| MAS-ANI-03 | mascot_wave.json        | lottie_mascote | **Pose:** `action: "with one arm raised"`                                                 | "a friendly wave to the user"                                         |
| MAS-ANI-04 | mascot_thinking.json    | lottie_mascote | **Pose:** `action: "hand on chin, looking curious"`                                       | "tapping chin thoughtfully, a lightbulb appears and glows above head" |
| MAS-ANI-05 | mascot_celebration.json | lottie_mascote | **Pose:** `action: "with arms open wide"`                                                 | "jumping for joy, with confetti exploding around"                     |

### 3. 🎨 Interface de Usuário e Fundos (`UI`)

#### **Padrões de Fundo (Tileable)**
**Local:** `assets/images/ui/patterns/`

| ID    | Nome do Arquivo      | Formato | Descrição                      | Prioridade |
| :---- | :------------------- | :------ | :----------------------------- | :--------- |
| UI-01 | `pattern_dots.svg`   | SVG     | Padrão de bolinhas coloridas.  | Importante |
| UI-02 | `pattern_stars.svg`  | SVG     | Padrão de estrelas espalhadas. | Importante |
| UI-03 | `pattern_clouds.svg` | SVG     | Padrão de nuvens suaves.       | Importante |
| UI-04 | `pattern_school.svg` | SVG     | Padrão com ícones escolares.   | Importante |

#### **Imagens de Fundo (Full-screen)**
**Local:** `assets/images/ui/backgrounds/`

| ID    | Nome do Arquivo       | Formato | Descrição                                 | Prioridade |
| :---- | :-------------------- | :------ | :---------------------------------------- | :--------- |
| UI-05 | `gradient_mesh_1.png` | PNG     | Gradiente suave azul-roxo (1920x1080).    | Importante |
| UI-06 | `gradient_mesh_2.png` | PNG     | Gradiente suave laranja-rosa (1920x1080). | Importante |

#### **Elementos Decorativos**
**Local:** `assets/images/ui/`

| ID    | Nome do Arquivo         | Formato | Descrição                                    | Prioridade |
| :---- | :---------------------- | :------ | :------------------------------------------- | :--------- |
| UI-07 | `sparkle_particle.png`  | PNG     | Sprite de partícula de brilho (64x64).       | Importante |
| UI-08 | `confetti_pieces.png`   | PNG     | Sprite sheet com peças de confete (512x512). | Importante |
| UI-09 | `bubble_decoration.svg` | SVG     | Formas de balões de fala decorativos.        | Importante |
| UI-10 | `rainbow_arc.svg`       | SVG     | Arco-íris decorativo.                        | Opcional   |

### 4. 🔄 Animações de Carregamento (`LOAD`)
**Local:** `assets/animations/loading/`  
**Formato:** Lottie JSON, Viewport 200x200px

| ID      | Nome do Arquivo         | Descrição                          | Duração      | Prioridade |
| :------ | :---------------------- | :--------------------------------- | :----------- | :--------- |
| LOAD-01 | `loading_spinner.json`  | Spinner circular colorido.         | ~2s (loop)   | Crítica    |
| LOAD-02 | `loading_bounce.json`   | Três pontos pulando.               | ~1.5s (loop) | Importante |
| LOAD-03 | `loading_wave.json`     | Animação de padrão de onda.        | ~2s (loop)   | Importante |
| LOAD-04 | `loading_thinking.json` | Cérebro com lâmpadas acendendo.    | ~3s (loop)   | Importante |
| LOAD-05 | `loading_camera.json`   | Íris de câmera abrindo e fechando. | ~1.5s (loop) | Importante |
| LOAD-06 | `loading_ai.json`       | Animação de rede neural.           | ~2.5s (loop) | Importante |

### 5. 🏆 Sistema de Conquistas (`ACH`)
*(Nota: Os 15 badges PNG já existem e não estão listados para criação)*

#### **Animações e Molduras**

| ID     | Nome do Arquivo           | Localização                          | Tipo     | Formato | Prioridade |
| :----- | :------------------------ | :----------------------------------- | :------- | :------ | :--------- |
| ACH-01 | `achievement_unlock.json` | `assets/animations/achievements/`    | Animação | Lottie  | Importante |
| ACH-02 | `level_up.json`           | `assets/animations/achievements/`    | Animação | Lottie  | Importante |
| ACH-03 | `star_burst.json`         | `assets/animations/achievements/`    | Animação | Lottie  | Importante |
| ACH-04 | `badge_frame_bronze.svg`  | `assets/images/achievements/frames/` | Moldura  | SVG     | Importante |
| ACH-05 | `badge_frame_silver.svg`  | `assets/images/achievements/frames/` | Moldura  | SVG     | Importante |
| ACH-06 | `badge_frame_gold.svg`    | `assets/images/achievements/frames/` | Moldura  | SVG     | Importante |
| ACH-07 | `badge_glow.png`          | `assets/images/achievements/frames/` | Efeito   | PNG     | Opcional   |

### 6. 🎨 Elementos Temáticos e Sazonais (`THM`)
**Local:** `assets/images/themed/`  
**Formato:** SVG preferencial

| ID     | Nome do Arquivo               | Descrição                                          | Prioridade |
| :----- | :---------------------------- | :------------------------------------------------- | :--------- |
| THM-01 | `holiday_decorations.svg`     | Itens genéricos de feriados (gorro, presente).     | Importante |
| THM-02 | `seasonal_pattern_spring.svg` | Padrão temático de primavera (flores, borboletas). | Opcional   |
| THM-03 | `seasonal_pattern_autumn.svg` | Padrão temático de outono (folhas, cores quentes). | Opcional   |
| THM-04 | `birthday_elements.svg`       | Bolo de aniversário, balões, confetes.             | Opcional   |
| THM-05 | `space_theme.svg`             | Planetas, estrelas, foguetes.                      | Opcional   |

### 7. 🎯 Feedback Interativo (`FBK`)
**Local:** `assets/animations/feedback/`  
**Formato:** Lottie JSON

| ID     | Nome do Arquivo          | Descrição                              | Duração    | Prioridade |
| :----- | :----------------------- | :------------------------------------- | :--------- | :--------- |
| FBK-01 | `touch_ripple.json`      | Efeito de ondulação no ponto de toque. | ~0.5s      | Crítica    |
| FBK-02 | `success_checkmark.json` | Checkmark verde animado.               | ~1s        | Importante |
| FBK-03 | `error_shake.json`       | Animação de tremor suave para erro.    | ~0.5s      | Importante |
| FBK-04 | `hint_pulse.json`        | Efeito de brilho pulsante para dicas.  | ~2s (loop) | Opcional   |

### 8. 🎮 Ícones de Navegação (`ICO`)
**Local:** `assets/icons/navigation/`  
**Formato:** SVG, Base 24x24dp, Estilo arredondado

| ID     | Nome do Arquivo             | Descrição                            | Prioridade |
| :----- | :-------------------------- | :----------------------------------- | :--------- |
| ICO-01 | `icon_camera_fun.svg`       | Câmera divertida e amigável.         | Importante |
| ICO-02 | `icon_microphone_fun.svg`   | Microfone amigável.                  | Importante |
| ICO-03 | `icon_history_fun.svg`      | Relógio com um sorriso.              | Importante |
| ICO-04 | `icon_achievements_fun.svg` | Troféu com estrelas.                 | Importante |
| ICO-05 | `icon_settings_fun.svg`     | Engrenagem com um rosto.             | Opcional   |
| ICO-06 | `icon_help_fun.svg`         | Personagem de ponto de interrogação. | Opcional   |

---

## **Especificações Técnicas Gerais**

*(Esta seção permanece a mesma, pois já é altamente profissional e detalhada)*

---

## **Diretrizes de Design**

*(Esta seção permanece a mesma, pois já é altamente profissional e detalhada)*

---

## **Roadmap de Produção**

### **Fase 1: Crítica**
- Todos os Efeitos Sonoros (9 arquivos)
- Finalização das imagens estáticas do Mascote (5 arquivos)
- Animação `loading_spinner.json`
- Animação `touch_ripple.json`

### **Fase 2: Importante**
- Imagens estáticas e animações restantes do Mascote
- Animações de Carregamento restantes
- Todos os Padrões de Fundo e Imagens de Fundo
- Todos os Ícones de Navegação
- Todas as Animações e Molduras de Conquista

### **Fase 3: Melhorias (Opcional)**
- Todos os Elementos Temáticos e Sazonais
- Elementos Decorativos e de Feedback restantes
- Variações e otimizações adicionais

---

## **Estrutura de Arquivos do Projeto**

```
professor_virtual/
└── assets/
├── animations/
    │   ├── achievements/
    │   │   ├── achievement_unlock.json
    │   │   └── ...
│   ├── feedback/
│   │   ├── touch_ripple.json
    │   │   └── ...
│   └── loading/
│       ├── loading_spinner.json
│       └── ...
├── fonts/
    │   └── (arquivos existentes)
├── icons/
│   └── navigation/
│       ├── icon_camera_fun.svg
│       └── ...
├── images/
│   ├── achievements/
    │   │   ├── (15 badges existentes)
│   │   └── frames/
│   │       ├── badge_frame_bronze.svg
│   │       └── ...
│   ├── mascot/
    │   │   ├── prof_happy.png
    │   │   ├── ...
│   │   └── animations/
│   │       ├── mascot_idle.json
    │   │   └── ...
    │   ├── themed/
    │   │   ├── holiday_decorations.svg
    │   │   └── ...
│   └── ui/
│       ├── backgrounds/
│       │   ├── gradient_mesh_1.png
    │   │   └── ...
    │       ├── patterns/
    │       │   ├── pattern_dots.svg
    │       │   └── ...
    │       ├── sparkle_particle.png
    │       └── ...
└── sounds/
    └── feedback/
        ├── button_tap.mp3
        └── ...
```

---
**Fim do Documento**