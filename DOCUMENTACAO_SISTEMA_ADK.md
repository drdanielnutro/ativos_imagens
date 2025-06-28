# Documentação do Sistema: Gerador de Ativos de IA

**Versão:** 1.0
**Data:** 26 de Junho de 2025

## 1. Visão Geral do Sistema

Este projeto implementa um **Gerador Automatizado de Ativos Digitais**, um sistema de software avançado construído sobre o **Google Agent Development Kit (ADK)**. O sistema funciona como um "Diretor de Produção de IA", capaz de interpretar solicitações em linguagem natural para orquestrar a criação de uma variedade de ativos digitais, incluindo:

*   Imagens rasterizadas (PNG)
*   Gráficos vetoriais (SVG)
*   Animações complexas (JSON/Lottie)

A arquitetura foi projetada para ser robusta e extensível, utilizando um agente de IA central que delega tarefas a um conjunto de ferramentas especializadas. Essas ferramentas, por sua vez, interagem com APIs de IA generativa de ponta para executar as tarefas de criação.

## 2. Arquitetura do Agente

O sistema adota o padrão de arquitetura **AUF (Agente Único com Ferramentas)**, um dos modelos preconizados para o desenvolvimento com ADK.

*   **Agente Orquestrador (`root_agent`):** No coração do sistema (`agent.py`) está um `LlmAgent` do ADK. Este agente utiliza o modelo `gemini-1.5-flash-latest` para compreender as intenções do usuário, analisar os pedidos e decidir qual ferramenta utilizar para cumprir a tarefa. Ele é o cérebro do sistema.

*   **Caixa de Ferramentas (`tools`):** O agente tem acesso a um conjunto de `FunctionTool`. Cada ferramenta é uma função Python que encapsula uma capacidade de negócio específica (ex: criar um SVG, gerar uma animação). Essa abordagem desacopla a lógica de orquestração da lógica de execução, tornando o sistema mais modular e fácil de manter.

## 3. Componentes Principais (Análise de Arquivos)

A funcionalidade do sistema é distribuída entre vários arquivos e diretórios chave:

| Arquivo/Diretório                          | Propósito                                                                                                                                                                                                                                                                                                 |
| :----------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`agent.py`**                             | **Orquestrador Central.** Define o `root_agent`, sua instrução de sistema e as ferramentas que ele pode usar (`check_asset_inventory`, `create_asset`). É o ponto de entrada para todas as solicitações do usuário.                                                                                       |
| **`tools/asset_manager.py`**               | **Gerenciador de Inventário.** Contém a classe `AssetManager`, responsável por carregar e fornecer as especificações detalhadas de cada ativo que pode ser gerado (descrições, prompts, nomes de arquivos).                                                                                               |
| **`tools/image_generator.py`**             | **Gerador de Imagens PNG.** Contém a lógica para interagir com APIs de imagem (provavelmente Recraft ou Replicate) para gerar imagens PNG. Inclui funcionalidades críticas como a remoção de fundo, que é executada em um subprocesso isolado para garantir estabilidade (`test_isolated_bg_removal.py`). |
| **`tools/svg_generator.py`**               | **Gerador de Vetores SVG.** Implementa a lógica para criar arquivos SVG. Possui um sistema de fallback: primeiro tenta gerar um SVG diretamente via API (ex: Recraft); se falhar, executa um pipeline secundário que gera um PNG e o vetoriza.                                                            |
| **`tools/mascot_animator.py`**             | **Gerador de Animações Lottie.** Orquestra o pipeline mais complexo do sistema para criar animações de mascote. Este processo envolve múltiplas chamadas de API e etapas de processamento.                                                                                                                |
| **`test_*.py`**                            | **Suíte de Testes.** Um conjunto de scripts de teste que validam a funcionalidade de cada componente de forma isolada (`test_isolated_bg_removal.py`) e de ponta a ponta (`test_pipeline_mascote.py`). Eles são cruciais para garantir a integridade do sistema.                                          |
| **`CLAUDE.md`**                            | **Documento de Meta-Arquitetura.** Descreve, para um "Engenheiro de Agentes de IA", como construir sistemas ADK. É a "constituição" que define os padrões de design (AUF vs. SMA) seguidos neste projeto.                                                                                                 |
| **`prompts_*.md`**                         | **Banco de Prompts.** Arquivos Markdown que contêm os prompts de texto detalhados e estruturados usados pelas ferramentas para gerar ativos específicos, como os emblemas de conquistas (`prompts_achievement_badges.md`).                                                                                |
| **`README.md` / `COMO_EXECUTAR.md`**       | **Documentação do Usuário.** Fornecem instruções claras sobre como configurar o ambiente, instalar dependências e executar o agente usando o servidor web do ADK.                                                                                                                                         |
| **`ativos_imagens/resources/definicoes/`** | **Cópia interna do inventário.** Mantém o agente autossuficiente em distribuições `pip install`. É atualizada pelo script `sync_inventory.py`.                                                                                                                                                            |
| **`ativos_imagens/sync_inventory.py`**     | **Script utilitário.** Copia `docs/definicoes/ativos_a_serem_criados.md` para a pasta `resources/` interna. Execute-o sempre que editar o inventário.                                                                                                                                                     |

## 4. Fluxos de Trabalho Detalhados

### 4.1. Fluxo Principal de Criação de Ativo

1.  **Entrada do Usuário:** O usuário interage com a interface web do ADK (iniciada com `adk web`) e envia um comando, como: `"Crie o ícone da câmera"`.
2.  **Interpretação do Agente:** O `root_agent` recebe o texto. Seu LLM, guiado pela instrução de sistema, entende que a intenção é criar um ativo e que a ferramenta apropriada é `create_asset`.
3.  **Chamada da Ferramenta:** O agente invoca a função `create_asset`, passando o identificador do ativo que ele extraiu do prompt (ex: `ICO-01`).
4.  **Consulta ao Inventário:** A função `create_asset` utiliza o `AssetManager` para obter as especificações completas do `ICO-01` (prompt, tipo, nome do arquivo).
5.  **Delegação para o Módulo Correto:** Com base no tipo de ativo (SVG), a função chama o orquestrador específico, `_create_svg_asset`.
6.  **Execução da Geração:** O `_create_svg_asset` executa sua lógica, chamando as APIs externas necessárias.
7.  **Retorno do Resultado:** O caminho do arquivo gerado ou uma mensagem de status (sucesso/erro) é retornado em cascata até a interface do usuário.

### 4.2. Pipeline de Animação de Mascote (Lottie)

Este é o fluxo mais sofisticado, orquestrado pelo `MascotAnimator`:

1.  **Geração do PNG Base:** Uma imagem de alta qualidade do mascote é gerada via API (ex: Recraft) com base em um prompt detalhado.
2.  **Geração de Vídeo:** A imagem PNG é enviada para outra API (ex: Replicate) com um prompt de animação (ex: "respiração sutil, movimento de cabeça suave") para gerar um pequeno clipe de vídeo (MP4).
3.  **Extração de Frames:** O vídeo é processado localmente (usando OpenCV) para extrair seus frames individuais como imagens.
4.  **Vetorização dos Frames:** Cada frame é convertido de um formato raster (PNG) para um formato vetorial (SVG) usando um tracer como o `potrace`.
5.  **Montagem do Lottie:** Os frames SVG são montados em uma única animação JSON no formato Lottie, que é leve e escalável.
6.  **Otimização:** O arquivo Lottie final é otimizado para reduzir seu tamanho.

## 5. APIs e Serviços Externos

O sistema depende das seguintes APIs para sua funcionalidade:

*   **Google Gemini API:** Utilizada pelo `LlmAgent` do ADK para processamento de linguagem natural, raciocínio e tomada de decisões.
*   **Recraft AI API:** Utilizada para a geração de imagens estilizadas e vetores (SVG). É a primeira escolha para a geração de SVG devido à sua capacidade de produzir vetores nativamente.
*   **Replicate AI API:** Utilizada para tarefas de IA mais pesadas e especializadas que não estão disponíveis em outras APIs, como:
    *   Geração de vídeo a partir de uma imagem estática.
    *   Remoção de fundo de imagens.

## 6. Robustez e Tratamento de Erros

O sistema foi projetado com mecanismos de proteção para garantir uma operação confiável, conforme evidenciado em `test_svg_system.py`:

*   **Limite de Chamadas de API:** O sistema rastreia o número de chamadas de API por sessão para evitar custos inesperados e atingir os limites de taxa (`rate limits`).
*   **Detecção de Erros Persistentes:** O código está preparado para identificar e lidar com erros de API recorrentes (ex: `402 Payment Required`, `429 Rate Limit`), parando as tentativas para evitar desperdício de recursos.
*   **Mecanismo de Fallback:** Se a tentativa primária de gerar um ativo falhar (ex: a API Recraft não consegue criar um SVG), o sistema automaticamente aciona um pipeline secundário (ex: gerar um PNG e vetorizá-lo) para garantir que o usuário sempre receba um resultado.

## 7. Configuração e Execução

Para executar o sistema, siga os passos definidos em `COMO_EXECUTAR.md`:

1.  **Navegar** para o diretório raiz do projeto.
2.  **Ativar** o ambiente virtual Python (`source .venv312/bin/activate`).
3.  **Configurar** a chave da API do Google no arquivo `.env`.
4.  **Iniciar** o servidor web do ADK com o comando `adk web`.
5.  **Acessar** a interface em `http://127.0.0.1:8000` e selecionar o agente `ativos_imagens`.

**Sincronizar inventário interno**
```bash
python -m ativos_imagens.sync_inventory  # executa na raiz sempre que atualizar o Markdown de inventário
```
