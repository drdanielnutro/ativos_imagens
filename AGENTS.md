<!--
Este arquivo serve como documentação para o Codex Cloud (ADK) sobre o agente
"ativos_imagens" e sua estrutura interna. Ele será automaticamente incluído como
contexto em sessões do Codex CLI para orientar o comportamento do agente.
-->
# AGENTS

Este documento descreve o agente *Gerador Automatizado de Assets Digitais*,
suas ferramentas e a estrutura do projeto, para uso com o Google Agent
Development Kit (ADK).

## Visão Geral do Projeto

O projeto implementa um **Agente Único com Ferramentas** para geração
automatizada de ativos digitais (PNG, SVG, Lottie e em breve MP3) voltados
para aplicações infantis. O agente atua como um "Diretor de Produção",
orquestrando módulos especializados que utilizam IA e lógicas programáticas.

## Estrutura de Diretórios

```
.
├── AGENTS.md                # Este arquivo de instruções para o Codex Cloud
├── README.md                # Descrição geral e instruções de setup/execução
└── ativos_imagens/          # Pacote principal do agente e tools
    ├── agent.py             # Agente de produção com orquestração de tools
    ├── agent_minimal.py     # Versão mínima do agente para testes/debug
    ├── sync_inventory.py    # Sincroniza inventário de ativos (docs → resources)
    ├── resources/definicoes/ # Definições de ativos carregadas pelo AssetManager
    ├── tools/               # Ferramentas especializadas de geração de assets
    │   ├── asset_manager.py
    │   ├── image_generator.py
    │   ├── svg_generator.py
    │   ├── lottie_programmatic.py
    │   └── mascot_animator.py
    └── output/              # Exemplos de saída (PNG, SVG e Lottie gerados)
```

## Ferramentas Disponíveis

| Ferramenta                  | Localização                  | Função                                              |
| --------------------------- | ---------------------------- | --------------------------------------------------- |
| AssetManager                | tools/asset_manager.py       | Gerencia inventário, checklist e paths dos ativos   |
| ImageGenerator              | tools/image_generator.py     | Gera imagens PNG via IA e opcional remoção de fundo |
| SVGGenerator                | tools/svg_generator.py       | Gera vetores SVG programáticos ou assistidos por IA |
| LottieProgrammaticGenerator | tools/lottie_programmatic.py | Cria animações Lottie programaticamente             |
| MascotAnimator              | tools/mascot_animator.py     | Cria animações Lottie para mascote via IA           |

## Comportamento do Agente

- **get_project_status()**: retorna status do projeto e lista de tools ativas.
- **create_asset(asset_id: str)**: orquestra a chamada ao AssetManager para
  buscar especificações e invocar a tool correta conforme o tipo do ativo.
- Carrega variáveis de ambiente do arquivo `.env`:
  - `GOOGLE_API_KEY` para chamadas ao ADK/Google Gemini
  - `REPLICATE_API_TOKEN` para chamadas à API do Replicate
- Controla limites de API via `API_CALL_TRACKER` e previne loops de erro com
  `ErrorTracker`.
- Caso ferramentas não estejam disponíveis, exibe alertas e instruções de
  instalação.

## Fluxo de Uso no Codex Cloud

1. Selecione o agente **ativos_imagens** no painel de agentes do ADK.
2. Faça perguntas ou comandos ao agente:
   - Ex: "Qual é o status do projeto?"
   - Ex: "Crie o ativo 'LOAD-01' do inventário."
3. O agente retornará informações formatadas e criará os arquivos em
   `ativos_imagens/output/`, organizados por tipo.
4. Para atualizar o inventário de ativos após editar as definições em
   `docs/definicoes/ativos_a_serem_criados.md`, execute:
   ```bash
   python -m ativos_imagens.sync_inventory
   ```

## Observações

- Mantenha `docs/definicoes/ativos_a_serem_criados.md` sempre sincronizado
  executando `sync_inventory.py`.
- Antes de rodar o agente em um ambiente novo, instale as dependências
  Python listadas em `requirements.txt` **e** execute `./startup.sh` (ou
  configure o *script de configuração* do Codex Cloud) para instalar
  utilitários de linha de comando essenciais como *ImageMagick*, *Potrace*,
  *mkbitmap* etc.
- Novas ferramentas de geração de áudio MP3 (SFX) serão adicionadas em breve.
- O agente está em fase de desenvolvimento e feedback é bem-vindo.