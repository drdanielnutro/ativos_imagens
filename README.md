# Projeto: Criador de Agentes de IA (Fábrica de Agentes)

Este repositório é um sistema para a geração automática de agentes de IA utilizando o Google Agent Development Kit (ADK). Ele funciona como uma "fábrica" que traduz documentos de especificação em projetos de agentes Python completos e funcionais.

## Objetivo Principal

O objetivo é acelerar e padronizar o desenvolvimento de agentes de IA, permitindo que o foco seja na **especificação do problema** (o *o quê*), enquanto o sistema automatiza a **implementação do código** (o *como*).

## Como Funciona

O fluxo de trabalho é centrado em um agente mestre, o **"Engenheiro de Agentes de IA"**, cujas instruções estão detalhadas no arquivo `CLAUDE.md`. Este engenheiro executa o seguinte processo:

1.  **Análise da Arquitetura:** Ele lê o arquivo `docs/definicoes/documento_identificador_arquitetura.md` para determinar a estrutura de alto nível do agente a ser criado (por exemplo, um Agente Único com Ferramentas ou um Sistema Multiagente).

2.  **Análise da Implementação:** Em seguida, ele lê o `docs/definicoes/pipeline_completo.md` para extrair todos os detalhes técnicos necessários: as ferramentas a serem implementadas, os prompts específicos, a lógica do fluxo de trabalho e outras configurações.

3.  **Geração do Código:** Com base nas duas análises, o Engenheiro de IA gera um projeto de agente completo, incluindo a estrutura de pastas, o código Python, um arquivo `.env` de modelo e um `README.md` específico para o agente recém-criado.

## Como Utilizar este Repositório

Para criar um novo agente:

1.  **Defina seu Projeto:** Navegue até o diretório `docs/definicoes/`.
2.  **Escreva as Especificações:** Edite os dois arquivos-chave:
    *   `documento_identificador_arquitetura.md`: Descreva a arquitetura desejada.
    *   `pipeline_completo.md`: Detalhe o plano de implementação completo.
3.  **Execute o Engenheiro:** Utilize o "Engenheiro de Agentes de IA" (conforme definido em `CLAUDE.md`) para processar os arquivos de definição.
4.  **Receba o Agente:** O sistema irá gerar um novo projeto de agente pronto para ser configurado e executado com o comando `adk web`.

## Estrutura de Arquivos Essenciais

-   `CLAUDE.md`: O "cérebro" do sistema. Contém a instrução de sistema que define o comportamento do Engenheiro de Agentes de IA.
-   `docs/definicoes/`: O "coração" de cada novo projeto. É aqui que as especificações do agente a ser construído são colocadas.
    -   `documento_identificador_arquitetura.md`
    -   `pipeline_completo.md`

## Estrutura do Projeto

```
ativos_imagens/
├── docs/
│   ├── definicoes/
│   │   └── documento_identificador_arquitetura.md
│   └── deep_research/
│       └── deep_research_ideia/
│           └── gerando_ativos_rapidamente.md
└── CLAUDE.md
```

## Documentação Principal

### CLAUDE.md
Contém as instruções do sistema para o Engenheiro de Agentes de IA, incluindo:
- Protocolos de construção para Agente Único com Ferramentas (AUF)
- Protocolos de construção para Sistema Multiagente (SMA)
- Diretrizes de desenvolvimento usando Google Agent Development Kit (ADK)

### Documento de Estratégia de Geração de Ativos
Em `docs/deep_research/deep_research_ideia/gerando_ativos_rapidamente.md`:
- Pipeline de produção "Vector-First" para criação rápida de ativos
- Estratégias de animação com movimento impulsionado por predefinições
- Matrizes de prompts para geração via IA
- Fluxos de trabalho de pós-produção automatizados

## Objetivo do Projeto

Criar um sistema completo de geração de ativos digitais priorizando:
- **Velocidade** acima da perfeição
- **Automação** via ferramentas de IA
- **Consistência** visual e técnica
- **Escalabilidade** para produção em massa

## Tecnologias e Ferramentas

- **Geração de Vetores**: Recraft, SVG.io, MagicShot.ai
- **Geração de Imagens**: Leonardo.ai, getimg.ai
- **Animações**: LottieFiles, conversores SVG-para-Lottie
- **Áudio**: ElevenLabs, MyEdit
- **Otimização**: FFmpeg, pngquant, SVGO

## Licença

Este projeto está sob desenvolvimento. Direitos reservados.