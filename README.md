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
    ```

3.  **Configure sua chave de API:**
    *   Abra o arquivo `.env` e substitua `SUA_CHAVE_API_AQUI` pela sua chave de API do Google Gemini.
    *   Para obter uma chave, acesse: https://makersuite.google.com/app/apikey

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

## Exemplo de Interação (Agente Mínimo)

*   "Qual é o status do projeto?"
*   "Olá! Você pode me informar sobre o sistema?"

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

Este é um **agente mínimo de teste** com apenas uma ferramenta de demonstração (`get_project_status`). As ferramentas completas do pipeline serão adicionadas após a validação desta estrutura base:

- [ ] Ferramenta de Geração de Imagens PNG (mascote PROF e sprites)
- [ ] Ferramenta de Geração Vetorial SVG (ícones e padrões)
- [ ] Ferramenta de Geração de Áudio MP3 (efeitos sonoros)
- [ ] Ferramenta de Geração de Animações Lottie (IA-vetorizada e programática)

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