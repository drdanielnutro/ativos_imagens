
# Gerador Manual de Ativos

Este diretório contém um script para gerar manualmente os ativos do projeto "Professor Virtual" com base nas especificações definidas em `docs/definicoes/ativos_a_serem_criados.md`.

## Pré-requisitos

- Python 3.9+ instalado.
- As dependências do projeto instaladas (ver `requirements.txt` na raiz).
- As variáveis de ambiente necessárias (como `REPLICATE_API_TOKEN`) devem estar configuradas.

## Como Usar

Execute o script `gerador_manual.py` a partir do diretório **raiz do projeto** (`ativos_imagens`), passando os IDs dos ativos que você deseja criar como argumentos.

O script irá automaticamente:
1. Ler as especificações do ativo.
2. Chamar a ferramenta de geração correta (PNG, SVG, Lottie, etc.).
3. Passar os prompts e parâmetros necessários.
4. Salvar o arquivo no diretório de destino correto dentro de `professor_virtual/assets/`.
5. Atualizar o `docs/definicoes/checklist_ativos_criados.md` para marcar o ativo como concluído.

### Sintaxe

```bash
python -m ativos_imagens.geracao_manual.gerador_manual <ASSET_ID_1> <ASSET_ID_2> ...
```

### Exemplos

**Gerar um único efeito sonoro:**
```bash
python -m ativos_imagens.geracao_manual.gerador_manual SFX-01
```

**Gerar uma imagem estática do mascote:**
```bash
python -m ativos_imagens.geracao_manual.gerador_manual MAS-08
```

**Gerar uma animação WebP do mascote:**
```bash
python -m ativos_imagens.geracao_manual.gerador_manual MAS-ANI-02
```

**Gerar múltiplos ativos de diferentes tipos de uma só vez:**
```bash
python -m ativos_imagens.geracao_manual.gerador_manual UI-01 LOAD-01 ACH-04 FBK-02
```

## Em Caso de Erros

Se a geração de um ativo falhar, o script exibirá uma mensagem de erro detalhada no console, marcará o item correspondente com um status de erro no checklist e continuará para o próximo ativo solicitado.
