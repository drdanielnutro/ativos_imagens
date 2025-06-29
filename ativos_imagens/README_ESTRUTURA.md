# 📁 Estrutura do Diretório - Sistema de Produção de Ativos

## 🗂️ Organização Atual

```
ativos_imagens/
├── agente_antigo/          # 📦 Sistema anterior (arquivado)
│   ├── agent.py            # Agente único original (AUF)
│   └── agent_minimal.py    # Versão mínima do agente
│
├── agentes_ativos/         # 🚀 Sistema atual (em uso)
│   ├── orchestrator.py     # Orquestrador principal (SMA)
│   ├── asset_creator.py    # Agente especializado em criação
│   └── asset_validator.py  # Agente especializado em validação
│
├── tools/                  # 🛠️ Ferramentas compartilhadas
│   ├── asset_manager.py    # Gerenciador de inventário
│   ├── audio_generator.py  # Gerador de áudio MP3
│   ├── lottie_programmatic.py # Gerador de animações
│   ├── svg_generator.py    # Gerador de SVG
│   └── ...                 # Outras ferramentas
│
├── resources/              # 📂 Recursos internos
│   └── ativos_a_serem_criados.md # Inventário de ativos
│
├── output/                 # 📤 Arquivos gerados
└── __init__.py            # 🔧 Importações do sistema

```

## 🎯 Como Funciona

1. **Sistema Atual**: O arquivo `__init__.py` importa o orquestrador de `agentes_ativos/`
2. **Orquestrador**: Coordena os dois agentes especializados usando `AgentTool`
3. **Validador**: Escaneia, valida e gera relatórios
4. **Criador**: Gera áudio, Lottie, SVG e animações

## 💡 Benefícios da Organização

- ✅ **Clareza**: Fácil identificar código ativo vs. arquivado
- ✅ **Modularidade**: Cada agente em seu próprio arquivo
- ✅ **Manutenibilidade**: Mudanças isoladas por componente
- ✅ **Histórico**: Código antigo preservado para referência

## 🚀 Para Executar

```bash
cd /Users/institutorecriare/VSCodeProjects/criador_agentes/ativos_imagens
source venv/bin/activate
adk web
```

Selecione `ativos_imagens` no menu e use comandos como:
- "Escaneie o projeto"
- "Crie o ativo SFX-01"
- "Gere um relatório de progresso"