# COMO EXECUTAR O AGENTE ADK

Este guia fornece instruções passo a passo para executar o agente de geração de assets digitais.

## 🚀 Passos Rápidos

### 1. Navegue até o diretório do projeto:
```bash
cd /Users/institutorecriare/VSCodeProjects/criador_agentes/ativos_imagens
```

### 2. Ative o ambiente virtual Python:

**macOS/Linux:**
```bash
source .venv312/bin/activate
```

**Windows (CMD):**
```bash
.venv312\Scripts\activate.bat
```

**Windows (PowerShell):**
```bash
.venv312\Scripts\Activate.ps1
```

### 3. (Opcional) Sincronizar inventário interno
Se você alterou `docs/definicoes/ativos_a_serem_criados.md`, copie a atualização para dentro do pacote para que o agente continue autossuficiente:
```bash
python -m ativos_imagens.sync_inventory
```

### 4. Verifique se o google-adk está instalado:
```bash
pip list | grep google-adk
```

Se não estiver instalado:
```bash
pip install google-adk
```

### 5. Execute o servidor ADK:
```bash
adk web
```

### 6. Acesse o agente:
- Abra seu navegador
- Acesse: `http://127.0.0.1:8000`
- No menu dropdown (canto superior esquerdo), selecione: `ativos_imagens`
- Teste com prompts como:
  - "Qual é o status do projeto?"
  - "Olá! Me fale sobre o sistema"

## 🛑 Para parar o servidor:
Pressione `Ctrl+C` no terminal

## ✅ Verificação rápida da estrutura:
```bash
ls -la
```

Deve mostrar:
- `.env` (com sua API key)
- `.venv312/` (ambiente virtual)
- `ativos_imagens/` (pasta do agente)
- `README.md`
- `COMO_EXECUTAR.md` (este arquivo)

## 🔧 Troubleshooting

### Erro "name Field required" no LlmAgent:
- **Solução**: A partir da versão 1.4.2 do ADK, o parâmetro `name` é obrigatório
- Adicione `name="root_agent"` ao criar qualquer LlmAgent
- Exemplo: `LlmAgent(name="root_agent", model="gemini-1.5-flash-latest", ...)`

### Se o ambiente virtual não ativar:
- Certifique-se de que está no diretório correto
- Verifique se o ambiente virtual existe: `ls .venv312/`
- Se não existir, crie um novo: `python3 -m venv .venv312`

### Se o ADK não estiver instalado:
```bash
pip install --upgrade pip
pip install google-adk
```

### Se o servidor não iniciar:
- Verifique se a porta 8000 está livre: `lsof -i :8000`
- Tente outra porta: `adk web --port 8080`

### Se o agente não aparecer no menu:
- Certifique-se de executar `adk web` no diretório raiz (onde está a pasta `ativos_imagens/`)
- Verifique se o arquivo `ativos_imagens/__init__.py` existe

## 📝 Notas Importantes

- **Sempre ative o ambiente virtual** antes de executar comandos pip ou adk
- **Execute adk web do diretório raiz**, não de dentro da pasta ativos_imagens/
- **A API key** deve estar configurada no arquivo `.env`
- **O nome do agente** no menu será `ativos_imagens` (nome da pasta)

## 🔄 Comando Completo (copiar e colar):
```bash
cd /Users/institutorecriare/VSCodeProjects/criador_agentes/ativos_imagens && source .venv312/bin/activate && adk web
```