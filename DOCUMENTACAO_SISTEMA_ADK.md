# Documentação do Sistema: Gerador de Ativos de IA

**Versão:** 2.0
**Data:** 01 de Julho de 2025

## 1. Visão Geral do Sistema

Este projeto implementa um **Gerador Automatizado de Ativos Digitais**, um sistema de software avançado construído sobre o **Google Agent Development Kit (ADK)**. O sistema funciona como um "Diretor de Produção de IA", capaz de interpretar solicitações em linguagem natural para orquestrar a criação de uma variedade de ativos digitais, incluindo:

*   Imagens rasterizadas (PNG)
*   Gráficos vetoriais (SVG)
*   Animações complexas (JSON/Lottie)

A arquitetura foi projetada para ser robusta e extensível, adotando um **Sistema Multi-Agente**: um orquestrador central delega tarefas a agentes especializados, que por sua vez interagem com APIs de IA generativa de ponta para executar as tarefas de criação.

## 2. Arquitetura do Sistema Multi-Agente (SMA)

Este sistema evoluiu para uma arquitetura **SMA (Sistema Multi-Agente)**, separando responsabilidades em um orquestrador central e agentes especializados:

- **Orquestrador (`root_agent`)**: definido em `ativos_imagens/agentes_ativos/orchestrator.py`, coordena delegação de tarefas e integra agentes especializados e funções utilitárias.
- **Agentes Especializados**: módulos independentes que executam funcionalidades de negócio específicas:
  - `asset_validator_agent` (valida inventário, gera relatórios e identifica prioridades)
  - `asset_creator_agent` (cria áudio, animações Lottie, SVG e mascote)

A integração entre orquestrador e agentes é feita via `AgentTool`, e há funções utilitárias expostas como `FunctionTool` para visão geral do sistema (`get_system_overview`) e status rápido (`get_quick_status`).

## 3. Componentes Principais (Análise de Arquivos)

A funcionalidade do sistema está organizada nos principais arquivos e diretórios abaixo:

| Arquivo/Diretório                          | Propósito                                                                                                                                                                                                                                                                                                 |
| :----------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`ativos_imagens/README_ESTRUTURA.md`**           | Descreve a organização atual do código (agente_antigo vs. agentes_ativos)                                                        |
| **`ativos_imagens/agentes_ativos/orchestrator.py`** | Orquestrador principal (`root_agent`), coordena agentes especializados e funções utilitárias                                      |
| **`ativos_imagens/agentes_ativos/asset_validator.py`** | Agente especializado em validar inventário e gerar relatórios e prioridades                                                    |
| **`ativos_imagens/agentes_ativos/asset_creator.py`**   | Agente especializado em criar ativos (áudio, SVG, mascote em WebP, e outras animações Lottie programáticas)                                                           |
| **`ativos_imagens/tools/asset_manager.py`**          | Gerenciador de inventário interno e checklist                                                                                |
| **`ativos_imagens/tools/mascot_animator.py`**          | Orquestra a criação de animações de mascote (imagem -> vídeo -> WebP) com remoção de fundo opcional |
| **`ativos_imagens/tools/image_generator.py`**         | Gera imagens PNG, incluindo remoção de fundo                                                                                 |
| **`ativos_imagens/tools/svg_generator.py`**           | Cria vetores SVG programáticos com fallback de vetorização                                                                  |
| **`ativos_imagens/tools/lottie_programmatic.py`**     | Gera animações Lottie programaticamente                                                                                     |
| **`test_multi_agent.py`**                             | Teste de importação e validação do sistema multi-agente                                                                      |
| **`agente_antigo/`**                                  | Código legado do agente único original (AUF), mantido para referência                                                        |

## 4. Fluxos de Trabalho Detalhados

### 4.1. Fluxo de Trabalho Multi-Agente

1.  **Entrada do Usuário:** Usuário envia um comando na interface web do ADK, por exemplo:
    - `Escaneie o projeto e mostre o status` → delega ao `asset_validator_agent`.
    - `Crie o ativo SFX-01` → delega ao `asset_creator_agent`.
2.  **Interpretação do Orquestrador:** O `root_agent` recebe o comando e, baseado em sua instrução de sistema, escolhe o agente especializado adequado.
3.  **Chamada ao Agente Especializado:** O orquestrador invoca o agente correspondente via `AgentTool`.
4.  **Processamento do Agente:** O agente especializado executa seu pipeline interno (validação, criação ou geração de relatórios).
5.  **Retorno ao Orquestrador:** O resultado (caminho de arquivo, relatório ou status) é enviado de volta ao `root_agent`.
6.  **Resposta ao Usuário:** O `root_agent` formata e apresenta a resposta final na interface do ADK.

### 4.2. Pipeline de Animação de Mascote (WebP)

Este é o fluxo para animações de mascote, orquestrado pelo `MascotAnimator`:

1.  **Geração do PNG Base (Opcional):** Se um vídeo de entrada não for fornecido, uma imagem de alta qualidade do mascote é gerada via API (ex: Replicate) com base em um prompt detalhado. Esta imagem é gerada com seu fundo original.
2.  **Geração de Vídeo (Opcional):** Se a imagem base foi gerada, ela é enviada para outra API (ex: Replicate) com um prompt de animação para gerar um pequeno clipe de vídeo (MP4). Este vídeo também terá o fundo original.
3.  **Remoção de Fundo do Vídeo (Opcional):** Se solicitado (`remove_background=True`), o vídeo (seja ele gerado ou fornecido como entrada) tem seu fundo removido usando uma API especializada (ex: Replicate `lucataco/rembg-video`).
4.  **Conversão para WebP:** O vídeo resultante (com ou sem fundo) é convertido para o formato WebP otimizado usando FFmpeg. Este formato é ideal para web e mobile devido ao seu tamanho reduzido e suporte à transparência.

## 5. APIs e Serviços Externos

O sistema depende das seguintes APIs para sua funcionalidade:

*   **Google Gemini API:** Utilizada pelo `LlmAgent` do ADK para processamento de linguagem natural, raciocínio e tomada de decisões.
*   **Recraft AI API:** Utilizada para a geração de imagens estilizadas e vetores (SVG). É a primeira escolha para a geração de SVG devido à sua capacidade de produzir vetores nativamente.
*   **Replicate AI API:** Utilizada para tarefas de IA mais pesadas e especializadas que não estão disponíveis em outras APIs, como:
    *   Geração de vídeo a partir de uma imagem estática.
    *   Remoção de fundo de imagens.

## 6. Robustez e Tratamento de Erros

O sistema foi projetado com mecanismos de proteção para garantir uma operação confiável, conforme evidenciado em `test_multi_agent.py`:

*   **Limite de Chamadas de API:** O sistema rastreia o número de chamadas de API por sessão para evitar custos inesperados e atingir os limites de taxa (`rate limits`).
*   **Detecção de Erros Persistentes:** O código está preparado para identificar e lidar com erros de API recorrentes (ex: `402 Payment Required`, `429 Rate Limit`), parando as tentativas para evitar desperdício de recursos.
*   **Mecanismo de Fallback:** Se a tentativa primária de gerar um ativo falhar (ex: a API Recraft não consegue criar um SVG), o sistema automaticamente aciona um pipeline secundário (ex: gerar um PNG e vetorizá-lo) para garantir que o usuário sempre receba um resultado.

## 7. Configuração e Execução

Para executar o sistema multi-agente, siga os passos em `COMO_EXECUTAR.md`:

1. Navegue até o diretório raiz do projeto.
2. Ative o ambiente virtual Python:
   ```bash
   source venv/bin/activate
   ```
3. Instale as dependências do projeto:
   ```bash
   pip install -r requirements.txt
   ```
4. (Opcional) Sincronize o inventário interno:
   ```bash
   python -m ativos_imagens.sync_inventory
   ```
5. Inicie o servidor web do ADK:
   ```bash
   adk web
   ```
6. Acesse `http://127.0.0.1:8000` e selecione o agente `ativos_imagens`.

Para validar a instalação e configuração, execute:
```bash
pytest test_multi_agent.py -q --disable-warnings
```
