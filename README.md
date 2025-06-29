# README.md

# Projeto: Gerador Automatizado de Assets Digitais

Este projeto implementa um **Agente Único com Ferramentas** usando o Google Agent Development Kit (ADK).

## Descrição

Sistema de geração automatizada de assets digitais (imagens PNG, vetores SVG, áudio MP3 e animações Lottie) para aplicações infantis. O agente atua como um "Diretor de Produção" orquestrando ferramentas especializadas de IA e processamento programático para criar recursos visuais e sonoros de alta qualidade com consistência garantida.

## Configuração

1.  **Crie e ative um ambiente virtual Python:**
    ```bash
    python -m venv .venv
    # No macOS/Linux
    source .venv/bin/activate
    # No Windows (CMD)
    # .venv\Scripts\activate.bat
    ```

2.  **Instale as dependências:**
    ```bash
    pip install google-adk
    
    # Para funcionalidade de áudio:
    pip install pydub replicate
    
    # Para outras funcionalidades opcionais:
    pip install pillow rembg[gpu,cli] lottie potrace-wheel
    ```
    
    **Nota**: Para geração de áudio, você também precisa ter o FFmpeg instalado no sistema:
    - macOS: `brew install ffmpeg`
    - Ubuntu/Debian: `sudo apt install ffmpeg`
    - Windows: Baixe de https://ffmpeg.org/download.html

3.  **Configure suas chaves de API:**
    *   Abra o arquivo `.env` e configure:
        - `GOOGLE_API_KEY`: Sua chave de API do Google Gemini (obtenha em https://makersuite.google.com/app/apikey)
        - `REPLICATE_API_TOKEN`: Sua chave da Replicate (obtenha em https://replicate.com/account/api-tokens)
        - `RECRAFT_API_TOKEN`: (Opcional) Para geração avançada de imagens

## Execução

1.  **Inicie o servidor de desenvolvimento do ADK:**
    *   A partir do diretório raiz do projeto (que contém a pasta `ativos_imagens/`), execute:
    ```bash
    adk web
    ```

2.  **Interaja com o Agente:**
    *   Abra a URL fornecida no terminal (geralmente `http://127.0.0.1:8000`) em seu navegador
    *   No menu suspenso no canto superior esquerdo, selecione `ativos_imagens`
    *   Comece a conversar com seu agente no chat

## Exemplos de Interação

### Comandos Básicos
*   "Qual é o status do projeto?"
*   "Mostre o inventário de ativos"
*   "Verifique o inventário"

### Geração de Ativos

#### 🎵 Áudio (Efeitos Sonoros)
*   "Crie o ativo SFX-01" (som de clique de botão)
*   "Gere o efeito sonoro de sucesso"
*   "Crie todos os efeitos sonoros"
*   "Crie o processing_loop.mp3"

#### 🎬 Animações Lottie
*   "Crie o ativo LOAD-01" (spinner de carregamento)
*   "Gere a animação de feedback FBK-02"
*   "Crie todas as animações de loading"

#### 🎨 Vetores SVG
*   "Crie o ícone da câmera"
*   "Gere o ativo UI-03" (padrão de nuvens)
*   "Crie todos os ícones SVG"

## Estrutura do Projeto

```
ativos_imagens/
├── .env                    # Configuração da API (não commitado)
├── README.md              # Este arquivo
└── ativos_imagens/        # Pacote do agente
    ├── __init__.py        # Inicializador do pacote
    └── agent.py           # Agente principal e ferramentas
```

## Status Atual

O agente está **totalmente funcional** com todas as ferramentas do pipeline implementadas:

- [x] Ferramenta de Geração de Imagens PNG (mascote PROF e sprites)
- [x] Ferramenta de Geração Vetorial SVG (ícones e padrões)
- [x] Ferramenta de Geração de Áudio MP3 (efeitos sonoros)
- [x] Ferramenta de Geração de Animações Lottie (IA-vetorizada e programática)

## Próximos Passos

1. Testar o agente mínimo para validar a estrutura
2. Implementar as ferramentas específicas do pipeline
3. Adicionar lógica de orquestração para executar o pipeline completo
4. Implementar tratamento de erros e logging
5. Otimizar para produção

## Troubleshooting

Se encontrar problemas:
- Verifique se a chave API está corretamente configurada no `.env`
- Certifique-se de que o ambiente virtual está ativado
- Confirme que está executando `adk web` no diretório correto
- Verifique os logs do terminal para mensagens de erro detalhadas