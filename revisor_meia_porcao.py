# Script Python Adaptado para Otimização de Prompts de Ativos
# Baseado em: script de geração de prompts de ícones
# Adaptado para: Engenheiro de Prompts para Otimização de Ativos
# Missão: Analisar e otimizar prompts existentes em ativos digitais

import json
import os
import logging
import asyncio
import argparse
import re
import sys
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError
from typing import Optional, Dict, Any, Union, List
import anthropic

# Carrega variáveis de ambiente
load_dotenv()

# Configuração de logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("otimizacao_prompts_ativos.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

# Configura a chave de API do Anthropic
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
if not anthropic_api_key:
    logger.critical("A variável de ambiente ANTHROPIC_API_KEY não foi encontrada. O script não pode continuar sem a chave de API.")
    sys.exit("Erro: Chave de API da Anthropic não configurada.")

# Inicializa o cliente Anthropic
anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)

# --- Definição do Modelo Pydantic para Ativo ---
class AssetDocument(BaseModel):
    id: Union[str, int]  # ID do ativo pode ser string ou int
    prompt: Optional[str] = None  # Prompt direto no objeto
    alimento: Optional[str] = None  # Nome do alimento
    nome_cotidiano: Optional[str] = None  # Nome cotidiano
    tool: str = "image_generator"  # Ferramenta geradora padrão
    params: Dict[str, Any] = Field(default_factory=dict)  # Parâmetros opcionais
    description: str = ""  # Descrição do ativo
    
    def get_prompt(self) -> Optional[str]:
        """Extrai o prompt atual"""
        # Primeiro tenta o prompt direto
        if self.prompt:
            return self.prompt
        # Depois tenta nos parâmetros (compatibilidade antiga)
        if 'prompt' in self.params:
            return self.params['prompt']
        # Para imagens com prompt_details
        if 'prompt_details' in self.params:
            details = self.params['prompt_details']
            if isinstance(details, dict):
                # Concatena elementos relevantes
                parts = []
                if 'action' in details:
                    parts.append(details['action'])
                if 'description' in details:
                    parts.append(details['description'])
                return ' '.join(parts) if parts else None
        # Para animações
        if 'animation_prompt' in self.params:
            return self.params['animation_prompt']
        return None

# --- System Instructions do Engenheiro de Prompts ---
system_instructions = """# INSTRUÇÃO DE SISTEMA - ENGENHEIRO DE PROMPTS PARA OTIMIZAÇÃO DE ATIVOS

## 1. IDENTIDADE E OBJETIVO

**SYSTEM_CONTEXT:**
Você é o **Engenheiro de Prompts para Otimização de Ativos**, um especialista de elite em análise e refinamento de prompts para geração de ativos digitais multimodais. Sua expertise combina compreensão profunda de modelos generativos, princípios de prompt engineering e sensibilidade contextual para diferentes tipos de mídia (áudio, imagem, animação, vetorial).

**CORE_MISSION:**
Analisar criticamente prompts existentes para geração de ativos e determinar, com precisão cirúrgica, se necessitam otimização ou se já atingiram seu potencial máximo. Você opera no delicado equilíbrio entre aperfeiçoamento técnico e preservação da intenção original, garantindo que cada prompt maximize a probabilidade de gerar o ativo exato especificado.

**CRITICAL_PRINCIPLE:**
Modificação não é sinônimo de melhoria. Um prompt tecnicamente adequado deve ser preservado. Sua expertise reside em reconhecer quando a intervenção agregará valor real versus quando criará complexidade desnecessária ou desviará da intenção original.

## 2. CONHECIMENTO E HABILIDADES

**KNOWLEDGE_AND_SKILLS:**
Você possui domínio especializado em:

- **Análise Contextual de Prompts** - identificação precisa de elementos essenciais vs. acessórios
- **Engenharia Reversa de Intenção** - dedução do objetivo central a partir do prompt existente
- **Otimização Modal-Específica** - técnicas diferenciadas para áudio, imagem, SVG, animação
- **Preservação Semântica** - manutenção da essência enquanto enriquece especificações
- **Avaliação de Adequação Técnica** - reconhecimento de quando um prompt já é otimal
- **Contextualização Cultural e Etária** - adaptação para público-alvo específico

### 2.1 Framework de Análise PRESERVE
- **P**reservar intenção original
- **R**econhecer elementos centrais
- **E**nriquecer com contexto relevante
- **S**implificar complexidade desnecessária
- **E**specificar parâmetros técnicos
- **R**espeitar limitações do modelo gerador
- **V**alidar coerência final
- **E**vitar over-engineering

### 2.2 Critérios de Decisão para Intervenção
Um prompt deve ser modificado APENAS quando:
- Falta especificações técnicas críticas para o tipo de ativo
- Apresenta ambiguidade que compromete o resultado
- Carece de contexto essencial para o público-alvo
- Contém elementos contraditórios ou confusos
- Omite características fundamentais do ativo esperado

Um prompt deve ser MANTIDO quando:
- Já contém todos elementos necessários para geração adequada
- Expressa claramente a intenção desejada
- Inclui especificações técnicas apropriadas
- Está bem adaptado ao modelo gerador alvo
- Modificações introduziriam complexidade sem benefício proporcional

## 3. PROCESSO DE TAREFA / INSTRUÇÕES PASSO A PASSO

**TASK_PROCESS:**
Siga este processo rigoroso para cada ativo analisado:

### FASE 1: DECOMPOSIÇÃO E ANÁLISE

1. **Parsing do Documento JSON**
   - Extrair `id` do ativo
   - Identificar `tool` (tipo de ferramenta geradora)
   - Analisar estrutura de `params` e campos específicos
   - Mapear tipo de ativo (áudio, imagem, SVG, animação)

2. **Análise do Prompt Atual**
   - Identificar núcleo semântico (ação/objeto principal)
   - Catalogar especificações técnicas presentes
   - Detectar elementos contextuais
   - Avaliar adequação para ferramenta geradora

3. **Consulta de Boas Práticas**
   - Acessar regras específicas para o tipo de ativo identificado
   - Comparar prompt atual com padrões de excelência
   - Identificar gaps críticos ou redundâncias

### FASE 2: AVALIAÇÃO ESTRATÉGICA

4. **Aplicação do Framework PRESERVE**
   Para cada elemento do prompt:
   - É essencial para a intenção original? → PRESERVAR
   - Adiciona clareza técnica necessária? → MANTER/ADICIONAR
   - Cria ambiguidade ou desvio? → REMOVER/CLARIFICAR
   - Está otimizado para a ferramenta? → AJUSTAR SE NECESSÁRIO

5. **Decisão de Intervenção**
   SE (prompt_atual atende todos critérios de qualidade)
      E (modificações não agregariam valor mensurável)
      E (risco de desvio > benefício potencial)
   ENTÃO:
      MANTER prompt original
   SENÃO:
      PROCEDER com otimização cirúrgica

### FASE 3: OTIMIZAÇÃO (quando necessária)

6. **Enriquecimento Contextual**
   - Adicionar contexto do aplicativo quando relevante
   - Especificar características técnicas ausentes
   - Incluir diretrizes estilísticas apropriadas
   - Preservar SEMPRE o núcleo semântico original

7. **Validação Final**
   - Confirmar preservação da intenção original
   - Verificar adequação técnica completa
   - Assegurar clareza e ausência de ambiguidades
   - Validar otimização para ferramenta específica

### FASE 4: OUTPUT

8. **Geração do JSON de Resposta**
   {
     "id": "[ID original do ativo]",
     "prompt": "[Prompt original OU otimizado]"
   }

## 4. REGRAS E RESTRIÇÕES

**RULES_AND_CONSTRAINTS:**

### 4.1 Mandamentos Invioláveis

O assistente **DEVE**:
- ✓ Preservar SEMPRE o núcleo semântico do prompt original
- ✓ Manter prompts adequados sem modificação desnecessária
- ✓ Considerar contexto do aplicativo sem forçar sua inclusão
- ✓ Respeitar especificidades de cada tipo de ativo
- ✓ Retornar EXATAMENTE o formato JSON especificado
- ✓ Analisar APENAS o documento JSON fornecido
- ✓ Consultar boas práticas ANTES de qualquer decisão

O assistente **NÃO DEVE**:
- ✗ Alterar a ação ou comportamento central descrito
- ✗ Modificar outros campos do JSON além do prompt
- ✗ Considerar outros documentos do array
- ✗ Adicionar complexidade sem benefício claro
- ✗ Desviar da intenção original do criador
- ✗ Forçar modificações em prompts já otimizados
- ✗ Criar dependências entre diferentes ativos

### 4.2 Princípios de Preservação Semântica

**Exemplos de Preservação Correta:**
Original: "mascote dançando feliz"
✓ Otimizado: "mascote PROF, feliz, dançando com movimentos suaves e expressivos, sorrindo amplamente, em estilo cartoon amigável para crianças"
✗ Incorreto: "mascote PROF parado acenando" (mudou ação principal)

Original: "som de clique suave"
✓ Otimizado: "som de clique suave e satisfatório para interface infantil, não-alarmante, feedback tátil agradável, 0.5 segundos"
✗ Incorreto: "som de sino tocando suavemente" (mudou tipo de som)

## 5. CRITÉRIOS DE QUALIDADE POR TIPO DE ATIVO

**QUALITY_CRITERIA:**

### 5.1 Áudio (MP3, sons)
**Elementos Essenciais:**
- Descrição clara do tipo de som
- Duração específica quando relevante
- Contexto de uso (interface, feedback, ambiente)
- Características emocionais (alegre, suave, encorajador)
- Restrições (não-alarmante, adequado para crianças)

### 5.2 Imagens Estáticas (PNG, JPG)
**Elementos Essenciais:**
- Sujeito e ação principais
- Estilo visual (cartoon, realista, minimalista)
- Composição e enquadramento
- Paleta de cores ou mood
- Dimensões e formato quando específicos
- Background (transparente, sólido, ambiente)

### 5.3 Vetores (SVG)
**Elementos Essenciais:**
- Tipo de elemento (ícone, padrão, decorativo)
- Estilo de linha e preenchimento
- Complexidade apropriada para SVG
- Escalabilidade considerada
- Compatibilidade técnica mencionada

### 5.4 Animações (Lottie, WebP animado)
**Elementos Essenciais:**
- Ação ou movimento principal
- Duração e tipo de loop
- Keyframes principais quando relevante
- Fluidez e estilo de movimento
- Elementos que permanecem estáticos vs. animados

## 6. FORMATO DE SAÍDA

**OUTPUT_FORMAT:**
{
  "id": "string - ID exato conforme recebido na entrada",
  "prompt": "string - Prompt original OU versão otimizada"
}

### 6.1 Lógica de Decisão para Output

SE avaliação_concluiu_que_prompt_está_adequado:
    retornar {
        "id": id_original,
        "prompt": prompt_original_sem_modificação
    }
SENÃO:
    retornar {
        "id": id_original,
        "prompt": prompt_otimizado_com_melhorias
    }

## 7. TRATAMENTO DE CASOS ESPECIAIS

**SPECIAL_CASES:**

### 7.1 Prompts Minimalistas
Quando o prompt é extremamente simples (ex: "botão", "loading", "erro"):
- Avaliar se a simplicidade é intencional e adequada
- Adicionar contexto APENAS se criticamente necessário
- Preferir manter simplicidade se o resultado será claro

### 7.2 Prompts Sobre-especificados
Quando o prompt contém excesso de detalhes contraditórios:
- Identificar elementos centrais vs. periféricos
- Simplificar mantendo essência e requisitos técnicos
- Remover redundâncias e contradições

### 7.3 Prompts com Referências Culturais
Quando o prompt contém elementos culturais específicos:
- Avaliar adequação para público-alvo
- Manter referências se apropriadas e inclusivas
- Adaptar ou generalizar se necessário

## 8. PROCESSO DE RACIOCÍNIO

**REASONING_FRAMEWORK:**

Para cada análise, siga esta estrutura mental:

1. **"Qual é a intenção central deste prompt?"**
   - Identificar o que o criador quer alcançar
   - Separar essência de ornamentação

2. **"O prompt atual consegue gerar o ativo desejado?"**
   - Avaliar clareza e completude
   - Identificar ambiguidades críticas

3. **"Que elementos faltam para otimização?"**
   - Especificações técnicas
   - Contexto do aplicativo
   - Diretrizes estilísticas

4. **"A modificação agregará valor real?"**
   - Benefício > Risco de desvio
   - Complexidade justificada
   - Melhoria mensurável

5. **"Como preservar a intenção original?"**
   - Manter verbos e ações principais
   - Preservar objetos e sujeitos centrais
   - Adicionar sem substituir o essencial

## 9. TOM E ESTILO

**TONE_AND_STYLE:**

Internamente, mantenha:
- **Analytical mindset** - Avaliação objetiva e criteriosa
- **Conservative approach** - Modificar apenas quando necessário
- **Technical precision** - Especificações claras e exatas
- **Semantic sensitivity** - Respeito pela intenção original

O output é sempre um JSON limpo, sem comentários ou explicações adicionais.

## 10. INFORMAÇÕES COMPLEMENTARES

**ADDITIONAL_CONTEXT:**

### 10.1 Sobre o Contexto do Aplicativo
Quando relevante incluir contexto:
- Professor Virtual: assistente educacional IA
- Público: crianças brasileiras 7-11 anos
- Tom: amigável, encorajador, educativo
- Estilo visual: colorido, lúdico, seguro

### 10.2 Ferramentas Geradoras Comuns
Cada ferramenta tem características próprias:
- `image_generator`: favorece descrições visuais detalhadas
- `audio_generator`: requer especificações técnicas precisas
- `svg_generator`: beneficia de simplicidade estrutural
- `lottie_programmatic`: necessita descrições de movimento
- `mascot_animator`: combina visual com instruções de animação

### 10.3 Filosofia de Otimização
**"O melhor prompt nem sempre é o mais longo ou detalhado, mas aquele que comunica com precisão a intenção desejada para a ferramenta específica, no contexto específico, preservando a visão original do criador."**"""

# --- Função para ler os IDs processados ---
def read_processed_ids_sync(ids_file: str) -> set:
    try:
        with open(ids_file, "r", encoding="utf-8") as f:
            ids = set(f.read().splitlines())
    except FileNotFoundError:
        ids = set()
    return ids

# --- Função para anexar um ID ao arquivo de controle ---
def append_processed_id_sync(doc_id: str, ids_file: str):
    with open(ids_file, "a", encoding="utf-8") as f:
        f.write(f"{doc_id}\n")

# --- Função de Caminho de Saída ---
def get_next_output_path():
    directory = "dados"
    if not os.path.exists(directory):
        os.makedirs(directory)
    files = os.listdir(directory)
    seqs = []
    pattern = re.compile(r"prompts_otimizados(\d+)\.json")
    for filename in files:
        match = pattern.match(filename)
        if match:
            seqs.append(int(match.group(1)))
    next_num = max(seqs) + 1 if seqs else 1
    return os.path.join(directory, f"prompts_otimizados{next_num}.json")

# --- Função de Preparação de Input ---
def preparar_input_para_api(doc: AssetDocument) -> str:
    """Prepara o JSON do ativo completo para análise"""
    asset_data = {
        "id": doc.id,
        "tool": doc.tool,
        "params": doc.params if doc.params else {},
        "description": doc.description,
        "prompt": doc.get_prompt(),
        "alimento": getattr(doc, 'alimento', ''),
        "nome_cotidiano": getattr(doc, 'nome_cotidiano', '')
    }
    return json.dumps(asset_data, ensure_ascii=False, indent=2)

# --- Função de Retry ---
async def retry_async(coro, retries=3, delay=1, factor=2):
    attempt = 0
    last_exception = None
    while attempt < retries:
        try:
            return await coro()
        except Exception as e:
            attempt += 1
            last_exception = e
            if attempt < retries:
                wait_time = delay * (factor ** (attempt - 1))
                logger.warning(f"Tentativa {attempt} falhou com erro: {e}. Retentando em {wait_time} segundos...")
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"Número máximo de tentativas ({retries}) atingido. Último erro: {last_exception}")
                return None
    return None

# --- Função de Chamada à API ---
async def chamada_api_claude(doc: AssetDocument, parametros_api: dict):
    loop = asyncio.get_event_loop()
    doc_id_log = doc.id

    async def fazer_chamada():
        # Prepara os argumentos para a API
        kwargs = {
            "model": parametros_api.get("claude_model", "claude-sonnet-4-20250514"),
            "system": system_instructions,
            "messages": [
                {
                    "role": "user",
                    "content": preparar_input_para_api(doc)
                }
            ],
            "temperature": parametros_api.get("temperature", 0.1),
            "max_tokens": parametros_api.get("max_tokens", 500)
        }

        # Chamada síncrona dentro do executor
        return await loop.run_in_executor(
            None,
            lambda: anthropic_client.messages.create(**kwargs)
        )

    # Pega o prompt atual ou retorna None se não encontrar
    prompt_atual = doc.get_prompt()
    
    try:
        response = await fazer_chamada()

        # Log de uso de tokens
        if hasattr(response, 'usage') and hasattr(response.usage, 'input_tokens'):
            logger.debug(f"Ativo ID {doc_id_log} - Tokens usados: Entrada={response.usage.input_tokens}, Saída={response.usage.output_tokens}")

        # Extrair o conteúdo JSON da resposta
        texto_resposta = ""
        if response.content:
            text_blocks = [block.text for block in response.content if block.type == 'text']
            if text_blocks:
                texto_resposta = text_blocks[0]
                try:
                    # Tenta decodificar a resposta como JSON
                    resultado = json.loads(texto_resposta)
                    
                    # Verifica se tem o formato esperado
                    if isinstance(resultado, dict) and 'id' in resultado and 'prompt' in resultado:
                        if resultado['id'] == doc.id:
                            return resultado['prompt']
                        else:
                            logger.warning(f"ID retornado ({resultado['id']}) não corresponde ao ID do ativo ({doc.id})")
                            return prompt_atual
                    else:
                        logger.warning(f"Resposta não tem formato esperado: {texto_resposta}")
                        return prompt_atual
                        
                except json.JSONDecodeError:
                    logger.warning(f"Ativo ID {doc_id_log} - Resposta não é um JSON válido: '{texto_resposta}'")
                    return prompt_atual
                except Exception as e:
                    logger.error(f"Ativo ID {doc_id_log} - Erro ao processar resposta: {e}")
                    return prompt_atual
            else:
                logger.warning(f"Ativo ID {doc_id_log} - Resposta vazia da API")
                return prompt_atual
        else:
            logger.warning(f"Ativo ID {doc_id_log} - Sem conteúdo na resposta")
            return prompt_atual

    except Exception as e:
        logger.error(f"Ativo ID {doc_id_log} - Erro na chamada à API: {e}")
        return prompt_atual

# --- Função de Processamento de Item ---
async def processar_item(asset_data: dict, parametros_api: dict, ids_file: str):
    try:
        doc = AssetDocument(**asset_data)
        doc_id_log = doc.id
    except ValidationError as e:
        logger.error(f"Erro de validação para o ativo: {asset_data.get('id', 'ID_DESCONHECIDO')}. Erro: {e}")
        return None
    except Exception as e:
        logger.error(f"Erro ao inicializar AssetDocument: {e}")
        return None

    # Verifica se já foi processado
    try:
        processed_ids = await asyncio.to_thread(read_processed_ids_sync, ids_file)
    except Exception as e:
        logger.error(f"Erro ao ler arquivo de IDs: {e}")
        return None

    if doc_id_log in processed_ids:
        logger.info(f"Ativo ID {doc_id_log} já foi analisado. Pulando...")
        return None

    # Obtém o prompt atual
    prompt_atual = doc.get_prompt()
    if prompt_atual is None:
        logger.warning(f"Ativo ID {doc_id_log} não tem prompt identificável. Pulando...")
        await asyncio.to_thread(append_processed_id_sync, doc_id_log, ids_file)
        return None

    # Realiza a chamada à API
    async def chamar_api_wrapper():
        return await chamada_api_claude(doc, parametros_api)

    prompt_resultado = await retry_async(chamar_api_wrapper, retries=3, delay=1, factor=2)

    # Prepara o resultado
    resultado = {
        "id": doc.id,
        "prompt_original": prompt_atual,
        "prompt_otimizado": prompt_resultado if prompt_resultado else prompt_atual,
        "modificado": prompt_resultado != prompt_atual if prompt_resultado else False
    }

    # Log do resultado
    if resultado["modificado"]:
        logger.info(f"Ativo ID {doc_id_log}: Prompt OTIMIZADO")
    else:
        logger.info(f"Ativo ID {doc_id_log}: Prompt MANTIDO (já adequado)")

    # Marca como processado
    try:
        await asyncio.to_thread(append_processed_id_sync, doc_id_log, ids_file)
    except Exception as e:
        logger.error(f"Erro ao salvar ID processado: {e}")

    return resultado

# --- Função de Extração de Ativos do JSON ---
def extrair_ativos_do_inventario(inventory_data: Union[dict, List]) -> list:
    """Extrai todos os ativos do JSON"""
    all_assets = []
    
    # Se for uma lista (formato dados_com_id.json)
    if isinstance(inventory_data, list):
        for item in inventory_data:
            if isinstance(item, dict) and 'id' in item and 'prompt' in item:
                # Converte ID para string se necessário
                item['id'] = str(item['id'])
                all_assets.append(item)
        logger.info(f"Extraídos {len(all_assets)} ativos da lista")
        return all_assets
    
    # Se for um dicionário com categorias (formato antigo)
    if isinstance(inventory_data, dict):
        if 'categories' not in inventory_data:
            logger.error("Arquivo não contém 'categories' nem é uma lista")
            return all_assets
        
        for category_name, category_data in inventory_data['categories'].items():
            if 'assets' in category_data and isinstance(category_data['assets'], list):
                for asset in category_data['assets']:
                    if isinstance(asset, dict) and 'id' in asset:
                        # Adiciona informação da categoria
                        asset['category'] = category_name
                        all_assets.append(asset)
                        
    logger.info(f"Extraídos {len(all_assets)} ativos do inventário")
    return all_assets

# --- Função Principal ---
async def main_async(args):
    # Carregamento do inventário
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            inventory_data = json.load(f)
        
        # Extrai todos os ativos
        all_assets = extrair_ativos_do_inventario(inventory_data)
        
        if not all_assets:
            logger.error("Nenhum ativo encontrado no inventário")
            return
            
    except FileNotFoundError:
        logger.error(f"Arquivo não encontrado: {args.input}")
        return
    except json.JSONDecodeError:
        logger.error(f"Erro ao decodificar JSON: {args.input}")
        return
    except Exception as e:
        logger.error(f"Erro ao carregar inventário: {e}")
        return

    logger.info(f"Iniciando análise e otimização de prompts de ativos")

    # Filtra ativos já processados
    initial_processed_ids = await asyncio.to_thread(read_processed_ids_sync, args.ids)
    new_assets = [
        asset for asset in all_assets 
        if asset.get('id') not in initial_processed_ids
    ][:args.max_items]

    logger.info(f"{len(new_assets)} ativos novos serão analisados")

    if not new_assets:
        logger.info("Nenhum ativo novo para processar")
        return

    # Parâmetros da API
    parametros_api = {
        "claude_model": args.claude_model,
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
    }

    # Processamento com controle de concorrência
    semaphore = asyncio.Semaphore(args.max_concurrent)

    async def process_with_semaphore(asset_data):
        async with semaphore:
            return await processar_item(asset_data, parametros_api, args.ids)

    tasks = [process_with_semaphore(asset) for asset in new_assets]
    results = await asyncio.gather(*tasks)

    # Filtra resultados válidos
    valid_results = [r for r in results if r is not None]

    if valid_results:
        # Estatísticas
        total_analisados = len(valid_results)
        total_otimizados = sum(1 for r in valid_results if r['modificado'])
        
        # Salva resultados
        output_path = get_next_output_path()
        output_data = {
            "total_analisados": total_analisados,
            "total_otimizados": total_otimizados,
            "total_mantidos": total_analisados - total_otimizados,
            "resultados": valid_results
        }
        
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Análise concluída. Resultados salvos em {output_path}")
            logger.info(f"Total analisados: {total_analisados}, Otimizados: {total_otimizados}, Mantidos: {total_analisados - total_otimizados}")
        except Exception as e:
            logger.error(f"Erro ao salvar resultados: {e}")
    else:
        logger.info("Nenhum ativo foi processado com sucesso")

# --- Configuração de Argumentos CLI ---
def parse_args():
    parser = argparse.ArgumentParser(description="Análise e Otimização de Prompts de Ativos usando Claude API")
    parser.add_argument("--input", type=str, default="/Users/institutorecriare/VSCodeProjects/criador_agentes/ativos_imagens/dados/dados_com_id.json", 
                       help="Arquivo JSON com inventário de ativos")
    parser.add_argument("--ids", type=str, default="ids_ativos_analisados.txt", 
                       help="Arquivo de controle de IDs processados")
    parser.add_argument("--max_items", type=int, default=1000, 
                       help="Número máximo de ativos a processar")
    parser.add_argument("--max_concurrent", type=int, default=1, 
                       help="Número máximo de requisições concorrentes")
    parser.add_argument("--claude_model", type=str, default="claude-sonnet-4-20250514", 
                       help="Modelo do Claude a usar")
    parser.add_argument("--temperature", type=float, default=0.4, 
                       help="Temperature para a API")
    parser.add_argument("--max_tokens", type=int, default=5000, 
                       help="Máximo de tokens para resposta")
    return parser.parse_args()

# --- Execução Principal ---
if __name__ == "__main__":
    args = parse_args()
    try:
        asyncio.run(main_async(args))
    except Exception as e:
        logger.critical(f"Erro crítico na execução: {e}", exc_info=True)