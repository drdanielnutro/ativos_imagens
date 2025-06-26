# ativos_imagens/agent.py
"""Agente de produção de assets digitais"""

# Carregamento automático de variáveis de ambiente
from dotenv import load_dotenv
load_dotenv()

# Importações explícitas do ADK
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
import datetime
import os
import sys
import shutil
import tempfile
import time
import requests
import replicate
from typing import Optional, Dict

# Importar ferramentas
try:
    from .tools.lottie_programmatic import LottieProgrammaticGenerator
    lottie_available = True
except ImportError:
    lottie_available = False
    print("Aviso: Ferramenta Lottie não disponível. Instale python-lottie.")

try:
    from .tools.svg_generator import SVGGenerator
    svg_available = True
except ImportError:
    svg_available = False
    print("Aviso: Ferramenta SVG não disponível.")

try:
    from .tools.image_generator import ImageGenerator
    png_available = True
except ImportError:
    png_available = False
    print("Aviso: Ferramenta PNG não disponível.")

try:
    from .tools.asset_manager import AssetManager
    asset_manager_available = True
except ImportError:
    asset_manager_available = False
    print("Aviso: AssetManager não disponível.")

try:
    from .tools.mascot_animator import MascotAnimator
    mascot_animator_available = True
except ImportError:
    mascot_animator_available = False
    print("Aviso: Ferramenta MascotAnimator não disponível.")

# Debug: Verificar ambiente
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")
print(f"__file__: {__file__ if '__file__' in globals() else 'Not defined'}")

# Verificar se tokens de API estão disponíveis
google_key = os.getenv('GOOGLE_API_KEY')
replicate_token = os.getenv('REPLICATE_API_TOKEN')

if google_key:
    print("✅ Google API Key carregada do .env")
else:
    print("⚠️ Google API Key não encontrada no .env")

if replicate_token and replicate_token != 'sua_chave_replicate_aqui':
    print("✅ Replicate API Token carregada do .env")
else:
    print("⚠️ Replicate API Token não configurada no .env")
    print("   Configure sua chave em .env: REPLICATE_API_TOKEN=sua_chave_aqui")

# Sistema de controle de chamadas de API
API_CALL_TRACKER = {
    'recraft_calls': 0,
    'replicate_calls': 0,
    'max_calls_per_session': 10,
    'session_start': time.time()
}

def check_api_limit(api_type: str) -> bool:
    """Verifica se ainda podemos fazer chamadas de API."""
    total_calls = API_CALL_TRACKER.get('recraft_calls', 0) + API_CALL_TRACKER.get('replicate_calls', 0)
    
    if total_calls >= API_CALL_TRACKER['max_calls_per_session']:
        print(f"🛑 Limite de API atingido ({total_calls} chamadas). Abortando operação.")
        return False
    
    return True

def reset_api_limits():
    """Reseta contadores de API (útil para testes ou novo dia)."""
    API_CALL_TRACKER.update({
        'recraft_calls': 0,
        'replicate_calls': 0,
        'session_start': time.time()
    })
    print("🔄 Limites de API resetados")

class ErrorTracker:
    """Rastreia erros para evitar loops infinitos com erros persistentes."""
    def __init__(self):
        self.error_history = {}
        self.max_same_error = 2  # Máximo de vezes para o mesmo erro
    
    def _normalize_error(self, error_msg: str) -> str:
        """Normaliza mensagem de erro removendo partes variáveis."""
        # Remove números, IDs e timestamps
        import re
        normalized = re.sub(r'\d+', 'X', error_msg)
        normalized = re.sub(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', 'UUID', normalized)
        
        # Identifica tipos comuns de erro
        if '402' in error_msg or 'Payment Required' in error_msg:
            return 'ERROR_402_PAYMENT_REQUIRED'
        elif '429' in error_msg or 'Rate Limit' in error_msg:
            return 'ERROR_429_RATE_LIMIT'
        elif 'timeout' in error_msg.lower():
            return 'ERROR_TIMEOUT'
        elif 'connection' in error_msg.lower():
            return 'ERROR_CONNECTION'
        
        return normalized[:100]  # Limita tamanho
    
    def should_retry(self, error_msg: str) -> bool:
        """Verifica se devemos tentar novamente após este erro."""
        normalized = self._normalize_error(error_msg)
        
        # Contar ocorrências
        self.error_history[normalized] = self.error_history.get(normalized, 0) + 1
        
        # Se o mesmo erro ocorreu mais vezes que o permitido, parar
        if self.error_history[normalized] > self.max_same_error:
            print(f"⚠️ Erro persistente detectado: '{normalized}' (ocorreu {self.error_history[normalized]}x). Abortando tentativas.")
            return False
        
        return True


# Definição da ferramenta
def get_project_status() -> str:
    """Obtém o status atual do projeto de geração de ativos.
    
    Returns:
        str: Status formatado do projeto com data e hora atual
    """
    now = datetime.datetime.now()
    return f"""Status do Projeto - {now.strftime("%d/%m/%Y %H:%M:%S")}
    
Sistema: Gerador de Assets para Aplicação Infantil
Arquitetura: Agente Único com Ferramentas (AUF)

Ferramentas planejadas:
- Geração PNG (mascote PROF e sprites)
- Geração SVG (ícones e padrões)
- Geração MP3 (efeitos sonoros)
- Geração Lottie (animações)

Status: Agente base operacional - modo teste"""


# Função orquestradora principal
def create_asset(asset_id: str) -> str:
    """Cria um ativo baseado em seu ID do inventário.
    
    Args:
        asset_id: ID do ativo (ex: 'LOAD-01', 'UI-03', 'ICO-02')
    
    Returns:
        str: Status da criação com detalhes ou mensagem de erro
    """
    if not asset_manager_available:
        return "❌ Erro: AssetManager não disponível. Verifique a instalação."
    
    try:
        # Inicializar gerenciador
        manager = AssetManager()
        
        # Carregar inventário
        manager.load_asset_inventory()
        
        # Obter especificações do ativo
        spec = manager.get_asset_specification(asset_id)
        if not spec:
            return f"❌ Erro: Ativo '{asset_id}' não encontrado no inventário."
        
        # Verificar se podemos criar
        can_create, reason = manager.can_create_asset(asset_id)
        if not can_create:
            return f"""❌ Não posso criar o ativo '{asset_id}'.

📋 **Detalhes do Ativo:**
- Nome: {spec.get('filename')}
- Descrição: {spec.get('description')}
- Tipo: {spec.get('type')}

⚠️ **Motivo:** {reason}

💡 **Alternativas:**
- Para áudio (SFX): Use ferramentas como Audacity ou FL Studio
- Para imagens do mascote (MAS): Use Midjourney, DALL-E ou ilustrador
- Para gradientes PNG: Use Photoshop ou GIMP

📌 **Ativos que posso criar:**
- Animações Lottie programáticas (LOAD, FBK, ACH)
- Padrões e ícones SVG (UI, ICO)
- Molduras de badges (ACH)"""
        
        # Criar ativo baseado no tipo
        asset_type = spec.get('type')
        
        if asset_type == 'lottie_programmatic':
            result = _create_lottie_asset(asset_id, spec, manager)
        elif asset_type == 'lottie_mascote':
            result = _create_mascot_animation_asset(asset_id, spec, manager)
        elif asset_type == 'svg':
            result = _create_svg_asset(asset_id, spec, manager)
        elif asset_type in ['png_mascote', 'png_generico']:
            result = _create_png_asset(asset_id, spec, manager, remove_bg=True)
        else:
            return f"❌ Tipo '{asset_type}' ainda não implementado."
        
        # Atualizar checklist se sucesso
        if "✅" in result:
            manager.update_checklist_status(asset_id, 'completed')
            
        return result
        
    except Exception as e:
        return f"❌ Erro ao criar ativo: {str(e)}"


def _create_lottie_asset(asset_id: str, spec: dict, manager: AssetManager) -> str:
    """Cria um ativo Lottie baseado nas especificações."""
    if not lottie_available:
        return "❌ Erro: Ferramenta Lottie não disponível. Instale com: pip install lottie"
    
    try:
        generator = LottieProgrammaticGenerator()
        
        # Extrair parâmetros
        params = spec.get('parameters', {})
        duration = params.get('duration', 1.0)
        loop = params.get('loop', False)
        style = params.get('style', '')
        
        # Determinar tipo e estilo da animação
        category = spec.get('category')
        if category == 'LOAD':
            anim_type = 'loading'
        elif category == 'FBK':
            anim_type = 'feedback'
        elif category == 'ACH':
            anim_type = 'achievement'
        else:
            anim_type = 'loading'
        
        # Se não tem estilo definido, inferir do nome/descrição
        if not style:
            if 'spinner' in spec.get('filename', ''):
                style = 'spinner'
            elif 'bounce' in spec.get('description', '').lower():
                style = 'bounce'
            elif 'wave' in spec.get('description', '').lower():
                style = 'wave'
            elif 'checkmark' in spec.get('filename', ''):
                style = 'checkmark'
            elif 'ripple' in spec.get('filename', ''):
                style = 'ripple'
            elif 'shake' in spec.get('description', '').lower():
                style = 'shake'
            elif 'pulse' in spec.get('description', '').lower():
                style = 'pulse'
            elif 'unlock' in spec.get('filename', ''):
                style = 'unlock'
            elif 'level_up' in spec.get('filename', ''):
                style = 'level_up'
            elif 'star_burst' in spec.get('filename', ''):
                style = 'star_burst'
            elif 'thinking' in spec.get('description', '').lower():
                style = 'thinking'
            elif 'camera' in spec.get('description', '').lower():
                style = 'camera'
            elif 'ai' in spec.get('description', '').lower() or 'neural' in spec.get('description', '').lower():
                style = 'ai'
        
        # Gerar animação
        file_path = generator.generate_animation(
            animation_type=anim_type,
            style=style,
            duration=duration,
            loop=loop
        )
        
        # Mover para local correto
        target_path = manager.get_asset_path(asset_id)
        if target_path:
            os.makedirs(target_path.parent, exist_ok=True)
            import shutil
            shutil.move(file_path, str(target_path))
            file_path = str(target_path)
        
        # Obter tamanho
        file_size = os.path.getsize(file_path)
        size_kb = file_size / 1024
        
        return f"""✅ Ativo Lottie criado com sucesso!

🆔 **ID:** {asset_id}
📁 **Arquivo:** {spec.get('filename')}
📂 **Local:** {file_path}
📊 **Tamanho:** {size_kb:.1f} KB
📝 **Descrição:** {spec.get('description')}
🎬 **Tipo/Estilo:** {anim_type}/{style}
⏱️ **Duração:** {duration}s
🔄 **Loop:** {'Sim' if loop else 'Não'}

✨ **Status do Checklist:** Atualizado para ✅ Criado pelo agente"""
        
    except Exception as e:
        return f"❌ Erro ao gerar Lottie: {str(e)}"


def _create_png_asset(asset_id: str, spec: dict, manager: AssetManager, remove_bg: bool = True, return_path: bool = False) -> str:
    """
    Cria um ativo PNG baseado nas especificações.

    Args:
        asset_id: O ID do ativo.
        spec: As especificações do ativo do AssetManager.
        manager: A instância do AssetManager.
        remove_bg: Se True, remove o fundo da imagem gerada.
        return_path: Se True, retorna apenas o caminho do arquivo ao invés da mensagem formatada.
    
    Returns:
        Se return_path=True: Caminho absoluto do arquivo PNG.
        Se return_path=False: Mensagem formatada de sucesso/erro.
    """
    if not png_available:
        return "❌ Erro: Ferramenta de Geração PNG não está disponível."
    
    try:
        generator = ImageGenerator()
        
        asset_type = spec.get('type').replace('png_', '')
        prompt_details = spec.get('prompt_details', {})
        
        if asset_type == 'generico':
            prompt_details['description'] = spec.get('description', 'a simple generic asset')

        prompt_details['filename_base'] = spec.get('filename', 'asset').replace('.png', '')

        model_name = "black-forest-labs/flux-schnell"
        
        file_path = generator.generate_png(
            asset_type=asset_type,
            prompt_details=prompt_details,
            model_name=model_name,
            remove_bg=remove_bg
        )
        
        target_path = manager.get_asset_path(asset_id)
        if target_path:
            os.makedirs(target_path.parent, exist_ok=True)
            shutil.move(file_path, str(target_path))
            file_path = str(target_path)
        
        file_size = os.path.getsize(file_path) / 1024
        
        if return_path:
            return file_path
        
        return f"""✅ Ativo PNG criado com sucesso!

🆔 **ID:** {asset_id}
📁 **Arquivo:** {spec.get('filename')}
📂 **Local:** {file_path}
📊 **Tamanho:** {file_size:.1f} KB

✨ **Status do Checklist:** Atualizado para ✅ Criado pelo agente"""
        
    except Exception as e:
        return f"❌ Erro ao gerar PNG para '{asset_id}': {str(e)}"


def _prepare_svg_prompt(spec: dict) -> str:
    """
    Prepara prompt otimizado para geração de SVG baseado no tipo de ativo.
    """
    description = spec.get('description', '')
    category = spec.get('category', '')
    
    # Base prompt
    base = f"{description}, vector art, clean lines, minimalist design"
    
    # Adicionar modificadores por categoria
    if category == 'ICO':
        return f"{base}, icon style, simple shapes, bold colors, white background"
    elif category == 'UI':
        return f"{base}, UI element, flat design, modern, scalable"
    elif 'badge' in spec.get('filename', ''):
        return f"{base}, badge frame, decorative border, achievement style"
    else:
        return f"{base}, illustration, colorful, professional"


def _is_valid_svg(content: str) -> bool:
    """Valida se o conteúdo é um SVG válido."""
    if not content:
        return False
    
    # Verificar se é string e contém tags SVG
    if isinstance(content, str):
        if '<svg' in content and '</svg>' in content:
            return True
        # Se for URL, precisamos baixar primeiro
        elif content.startswith('http'):
            return True
        
    return False


def _save_svg_from_recraft(svg_content: str, asset_id: str, spec: dict, manager: AssetManager) -> str:
    """Salva SVG gerado pelo Recraft no local correto."""
    try:
        target_path = manager.get_asset_path(asset_id)
        os.makedirs(target_path.parent, exist_ok=True)
        
        # Se for URL, baixar conteúdo
        if svg_content.startswith('http'):
            response = requests.get(svg_content)
            response.raise_for_status()
            svg_content = response.text
        
        # Salvar arquivo
        with open(str(target_path), 'w', encoding='utf-8') as f:
            f.write(svg_content)
            
        file_size = os.path.getsize(target_path) / 1024
        
        return f"""✅ Ativo SVG criado com sucesso via Recraft!
        
🆔 **ID:** {asset_id}
📁 **Arquivo:** {spec.get('filename')}
📂 **Local:** {target_path}
📊 **Tamanho:** {file_size:.1f} KB
🚀 **Método:** Geração direta (Recraft-20b-svg)

✨ **Status do Checklist:** Atualizado para ✅ Criado pelo agente"""
        
    except Exception as e:
        raise RuntimeError(f"Erro ao salvar SVG do Recraft: {str(e)}")


def _try_recraft_svg_generation(spec: dict, max_attempts: int = 3) -> Optional[str]:
    """
    Tenta gerar SVG via Recraft com retry logic.
    
    Returns:
        String com conteúdo SVG ou None se falhar
    """
    error_tracker = ErrorTracker()
    
    for attempt in range(1, max_attempts + 1):
        # Verificar limite de API antes de tentar
        if not check_api_limit('recraft'):
            print("🛑 Limite de API atingido. Abortando geração via Recraft.")
            return None
            
        try:
            print(f"Tentativa {attempt}/{max_attempts}: Gerando SVG via Recraft...")
            
            # Preparar prompt otimizado para SVG
            prompt = _prepare_svg_prompt(spec)
            
            # Incrementar contador ANTES da chamada (para contar tentativas)
            API_CALL_TRACKER['recraft_calls'] += 1
            
            output = replicate.run(
                "recraft-ai/recraft-20b-svg",
                input={
                    "size": "1024x1024",  # Tamanho válido para Recraft
                    "style": "vector_illustration/cartoon", 
                    "prompt": prompt,
                    "aspect_ratio": "1:1"
                }
            )
            
            # Validar se é SVG válido
            if _is_valid_svg(output):
                print(f"✅ SVG gerado com sucesso na tentativa {attempt}")
                return output
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Tentativa {attempt} falhou: {error_msg}")
            
            # Verificar se devemos continuar tentando
            if not error_tracker.should_retry(error_msg):
                print("🛑 Abortando tentativas devido a erro persistente")
                return None
                
            if attempt < max_attempts:
                time.sleep(2 ** attempt)  # Backoff exponencial (2s, 4s)
                
    return None


def _create_mascot_animation_asset(asset_id: str, spec: dict, manager: AssetManager) -> str:
    """Cria uma animação Lottie do mascote."""
    if not mascot_animator_available:
        return "❌ Erro: Ferramenta de Animação do Mascote não está disponível."

    try:
        animator = MascotAnimator()
        
        # Detalhes para gerar o PNG base
        prompt_details_png = spec.get('prompt_details', {})
        # Prompt para a animação
        animation_prompt = spec.get('animation_prompt', 'standing still and breathing gently')
        
        target_path = manager.get_asset_path(asset_id)
        if not target_path:
            raise ValueError(f"Caminho de destino não encontrado para {asset_id}")

        os.makedirs(target_path.parent, exist_ok=True)

        result_path = animator.create_mascot_animation_v2(
            prompt_details=prompt_details_png,
            animation_prompt=animation_prompt,
            output_path=str(target_path),
            output_format="lottie"  # Usar formato .lottie por padrão
        )
        
        file_size = os.path.getsize(result_path) / 1024

        return f"""✅ Animação do mascote criada com sucesso!

🆔 **ID:** {asset_id}
📁 **Arquivo:** {os.path.basename(result_path)}
📂 **Local:** {result_path}
📊 **Tamanho:** {file_size:.1f} KB
📝 **Descrição:** {spec.get('description')}
🎬 **Prompt de Animação:** {animation_prompt}

✨ **Status do Checklist:** Atualizado para ✅ Criado pelo agente"""
        
    except Exception as e:
        return f"❌ Erro ao gerar animação do mascote para '{asset_id}': {str(e)}"


def _create_svg_via_png_pipeline(asset_id: str, spec: dict, manager: AssetManager) -> str:
    """
    Pipeline de fallback: PNG → SVG (implementação anterior).
    Usado apenas quando Recraft falha.
    """
    print(f"INFO: Usando pipeline de fallback PNG→SVG para {asset_id}...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            # ETAPA 1: Gerar PNG base diretamente com ImageGenerator
            print(f"ETAPA 1/3: Gerando imagem raster base para {asset_id}...")
            
            generator = ImageGenerator()
            
            # Preparar detalhes do prompt baseados na descrição do ativo
            prompt_details = {
                'description': spec.get('description', 'simple geometric shape'),
                'filename_base': f"temp_{asset_id.lower()}"
            }
            
            # Gerar PNG SEM remover fundo (importante para vetorização)
            temp_png_path = generator.generate_png(
                asset_type='generico',
                prompt_details=prompt_details,
                model_name="black-forest-labs/flux-schnell",
                remove_bg=False  # Crítico: não remover fundo para melhor vetorização
            )
            
            print(f"Imagem base gerada em: {temp_png_path}")
            
            # ETAPA 2: Mover PNG para diretório temporário (para limpeza automática)
            final_temp_path = os.path.join(tmpdir, f"{asset_id}_base.png")
            shutil.move(temp_png_path, final_temp_path)
            print(f"Imagem movida para diretório temporário: {final_temp_path}")

            # ETAPA 3: Vetorizar PNG→SVG
            print(f"ETAPA 2/3: Vetorizando {final_temp_path}...")
            svg_generator = SVGGenerator()
            
            target_path = manager.get_asset_path(asset_id)
            if not target_path:
                raise ValueError(f"Caminho de destino não encontrado para {asset_id}")

            os.makedirs(target_path.parent, exist_ok=True)
            
            # Usar o método de vetorização da SVGGenerator
            svg_generator.vectorize_and_save(
                input_image_path=final_temp_path,
                output_svg_path=str(target_path)
            )
            print(f"SVG final salvo em: {target_path}")

            print(f"--- Pipeline SVG para {asset_id} concluído com sucesso! ---")
            
            # Obter tamanho do arquivo final
            file_size = os.path.getsize(target_path) / 1024
            
            return f"""✅ Ativo SVG criado com sucesso!

🆔 **ID:** {asset_id}
📁 **Arquivo:** {spec.get('filename')}
📂 **Local:** {target_path}
📊 **Tamanho:** {file_size:.1f} KB
📝 **Descrição:** {spec.get('description')}
🔧 **Método:** Pipeline PNG→SVG (fallback)

✨ **Status do Checklist:** Atualizado para ✅ Criado pelo agente"""

        except Exception as e:
            print(f"ERRO no pipeline SVG para {asset_id}: {e}")
            return f"❌ Erro ao gerar SVG para '{asset_id}': {str(e)}"


def _create_svg_asset(asset_id: str, spec: dict, manager: AssetManager) -> str:
    """
    Cria SVG com sistema de prioridades:
    1. Tenta Recraft-20b-svg (3 tentativas)
    2. Fallback para pipeline PNG→SVG se necessário
    """
    if not svg_available:
        return "❌ Erro: Ferramenta SVG não está disponível."

    print(f"--- Iniciando Geração de SVG para: {asset_id} ---")
    
    # PRIORIDADE 1: Tentar geração direta via Recraft
    svg_content = _try_recraft_svg_generation(spec, max_attempts=3)
    
    if svg_content:
        # Salvar SVG gerado diretamente
        try:
            return _save_svg_from_recraft(svg_content, asset_id, spec, manager)
        except Exception as e:
            print(f"AVISO: Falha ao salvar SVG do Recraft: {e}")
            print("Tentando pipeline de fallback...")
    
    # PRIORIDADE 2: Fallback para pipeline PNG→SVG
    if not png_available:
        return "❌ Erro: Recraft falhou e ferramenta PNG não está disponível para fallback."
    
    return _create_svg_via_png_pipeline(asset_id, spec, manager)


def check_asset_inventory() -> str:
    """Verifica o inventário de ativos e retorna estatísticas.
    
    Returns:
        str: Relatório do inventário com estatísticas
    """
    if not asset_manager_available:
        return "❌ Erro: AssetManager não disponível."
    
    try:
        manager = AssetManager()
        manager.load_asset_inventory()
        manager.load_checklist_status()
        
        # Obter ativos que podemos criar
        creatable = manager.get_creatable_assets()
        
        # Contar por status
        total_creatable = sum(len(assets) for assets in creatable.values())
        completed = sum(1 for status in manager.checklist_status.values() 
                       if status.get('completed'))
        
        # Listar ativos por tipo
        report = f"""📊 **Inventário de Ativos - Relatório**

📈 **Estatísticas:**
- Total de ativos no inventário: {len(manager.asset_specs)}
- Ativos que posso criar: {total_creatable}
- Ativos já criados: {completed}
- Ativos pendentes: {total_creatable - completed}

🛠️ **Capacidades do Agente:**

✅ **Posso criar ({total_creatable} ativos):**
"""
        
        # Listar Lottie
        if creatable.get('lottie_programmatic'):
            report += f"\n🎬 **Animações Lottie Programáticas ({len(creatable['lottie_programmatic'])}):**\n"
            for asset_id in sorted(creatable['lottie_programmatic']):
                spec = manager.asset_specs.get(asset_id, {})
                status = "✅" if manager.checklist_status.get(asset_id, {}).get('completed') else "⏳"
                report += f"  {status} {asset_id}: {spec.get('filename', 'N/A')}\n"
        
        # Listar SVG
        if creatable.get('svg'):
            report += f"\n🎨 **Arquivos SVG ({len(creatable['svg'])}):**\n"
            for asset_id in sorted(creatable['svg']):
                spec = manager.asset_specs.get(asset_id, {})
                status = "✅" if manager.checklist_status.get(asset_id, {}).get('completed') else "⏳"
                report += f"  {status} {asset_id}: {spec.get('filename', 'N/A')}\n"
        
        report += """
❌ **Não posso criar (requerem ferramentas externas):**
- 🎵 Efeitos Sonoros (SFX): 9 arquivos MP3
- 🦸 Imagens do Mascote (MAS): 10 arquivos PNG
- 🎞️ Animações do Mascote (MAS): 5 animações Lottie vetorizadas
- 🌈 Gradientes e Partículas (UI): 4 arquivos PNG
- 🎨 Elementos Temáticos (THM): 5 arquivos SVG complexos

💡 **Como usar:**
- Para criar um ativo: "Crie o ativo LOAD-01"
- Para criar todos de um tipo: "Crie todas as animações de loading"
- Para ver detalhes: "Mostre detalhes do ativo UI-03"
"""
        
        return report
        
    except Exception as e:
        return f"❌ Erro ao verificar inventário: {str(e)}"


try:
    # Agente principal com tratamento de erro
    root_agent = LlmAgent(
        name="asset_production_orchestrator",
        model="gemini-1.5-flash-latest",
        instruction="""Você é um assistente orquestrador para a produção de assets digitais.
Sua principal ferramenta é `create_asset(asset_id)`. Use-a para criar qualquer ativo solicitado pelo usuário,
fornecendo o ID do ativo (ex: 'MAS-06', 'ICO-01').
Você também pode usar `check_asset_inventory()` para ver a lista de todos os ativos e seus status.
""",
        tools=[
            FunctionTool(create_asset),
            FunctionTool(check_asset_inventory),
            FunctionTool(get_project_status)
        ]
    )
    print("Agent created successfully!")
except Exception as e:
    print(f"Error creating agent: {type(e).__name__}: {e}")
    # Criar agente mínimo como fallback
    root_agent = LlmAgent(
        name="root_agent",
        model="gemini-1.5-flash-latest",
        instruction="Você é um assistente de produção de assets digitais. (Modo fallback - sem ferramentas)"
    )
    print("Fallback agent created")