# GEMINI.md - Guia Rápido do Projeto

Este arquivo fornece um resumo rápido de como configurar e executar o projeto de geração de assets.

## Visão Geral

Este é um **Sistema Multi-Agente** que usa o Google Agent Development Kit (ADK) para gerar automaticamente assets digitais (PNG, SVG, MP3, WebP) para aplicações infantis.

Existem duas maneiras de operar o sistema:
1.  **Modo Agente (via `adk web`)**: Interação por chat com o sistema de agentes (em desenvolvimento).
2.  **Modo Manual (via script Python)**: Execução direta das ferramentas de geração (método atual e estável).

---

## 1. Configuração do Ambiente

Execute estes comandos na raiz do projeto.

```bash
# 1. Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Configure as chaves de API no arquivo .env
# Crie um arquivo .env e adicione:
# GOOGLE_API_KEY="sua_chave"
# REPLICATE_API_TOKEN="sua_chave"
```

---

## 2. Como Executar

### Modo 1: Sistema Multi-Agente (Em Desenvolvimento)

Use este modo para interagir com o agente via interface web.

```bash
# Execute o servidor a partir da raiz do projeto
adk web
```
- **URL:** `http://127.0.0.1:8000`
- **Agente:** Selecione `ativos_imagens` no menu.
- **Exemplo de prompt:** `Crie o ativo SFX-01`

### Modo 2: Geração Manual de Ativos (Estável)

Use este script para gerar ativos específicos diretamente. **Este é o fluxo de trabalho principal no momento.**

```bash
# Execute o script a partir da raiz do projeto
python -m ativos_imagens.geracao_manual.gerador_manual <ASSET_ID_1> <ASSET_ID_2>
```
- **Exemplo:**
  ```bash
  python -m ativos_imagens.geracao_manual.gerador_manual MAS-08 UI-01 SFX-02
  ```

---

## Arquivos Importantes

- **Definição de Ativos:** `docs/definicoes/geracao_de_ativos.json` (fonte da verdade principal)
- **Checklist de Status:** `docs/definicoes/checklist_ativos_criados.md` (atualizado automaticamente pelo gerador manual)
- **Script de Geração Manual:** `ativos_imagens/geracao_manual/gerador_manual.py`
- **Pacote do Agente ADK:** `ativos_imagens/`
