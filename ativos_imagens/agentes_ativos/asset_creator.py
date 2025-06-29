"""
Agente Criador de Ativos - Especialista em geração de assets digitais
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from typing import Dict, Optional
import os
import sys
import shutil
import tempfile
import time

# Importar ferramentas de criação do diretório pai
try:
    from ..tools.lottie_programmatic import LottieProgrammaticGenerator
    lottie_available = True
except ImportError:
    lottie_available = False
    print("Aviso: Ferramenta Lottie não disponível.")

try:
    from ..tools.svg_generator import SVGGenerator
    svg_available = True
except ImportError:
    svg_available = False
    print("Aviso: Ferramenta SVG não disponível.")

try:
    from ..tools.image_generator import ImageGenerator
    png_available = True
except ImportError:
    png_available = False
    print("Aviso: Ferramenta PNG não disponível.")

try:
    from ..tools.asset_manager import AssetManager
    asset_manager_available = True
except ImportError:
    asset_manager_available = False
    print("Aviso: AssetManager não disponível.")

try:
    from ..tools.mascot_animator import MascotAnimator
    mascot_animator_available = True
except ImportError:
    mascot_animator_available = False
    print("Aviso: Ferramenta MascotAnimator não disponível.")

try:
    from ..tools.audio_generator import AudioEffectGenerator
    audio_available = True
except ImportError:
    audio_available = False
    print("Aviso: Ferramenta de Áudio não disponível.")


def create_lottie_animation(asset_id: str) -> str:
    """
    Cria uma animação Lottie programática baseada no ID do ativo.
    
    Args:
        asset_id: ID do ativo (ex: 'LOAD-01', 'FBK-01', 'ACH-01')
        
    Returns:
        str: Status da criação com detalhes ou mensagem de erro
    """
    if not lottie_available:
        return "❌ Erro: Ferramenta Lottie não disponível. Instale com: pip install lottie"
    
    if not asset_manager_available:
        return "❌ Erro: AssetManager não disponível."
    
    try:
        manager = AssetManager()
        manager.load_asset_inventory()
        
        spec = manager.get_asset_specification(asset_id)
        if not spec:
            return f"❌ Erro: Ativo '{asset_id}' não encontrado no inventário."
        
        if spec.get('type') != 'lottie_programmatic':
            return f"❌ Erro: Ativo '{asset_id}' não é uma animação Lottie programática."
        
        generator = LottieProgrammaticGenerator()
        
        # Extrair parâmetros
        params = spec.get('parameters', {})
        duration = params.get('duration', 1.0)
        loop = params.get('loop', False)
        style = params.get('style', '')
        
        # Determinar tipo da animação
        category = spec.get('category')
        if category == 'LOAD':
            anim_type = 'loading'
        elif category == 'FBK':
            anim_type = 'feedback'
        elif category == 'ACH':
            anim_type = 'achievement'
        else:
            anim_type = 'loading'
        
        # Inferir estilo se não especificado
        if not style:
            filename = spec.get('filename', '')
            description = spec.get('description', '').lower()
            
            if 'spinner' in filename:
                style = 'spinner'
            elif 'bounce' in description:
                style = 'bounce'
            elif 'wave' in description:
                style = 'wave'
            elif 'checkmark' in filename:
                style = 'checkmark'
            elif 'ripple' in filename:
                style = 'ripple'
            elif 'shake' in description:
                style = 'shake'
            elif 'pulse' in description:
                style = 'pulse'
            elif 'unlock' in filename:
                style = 'unlock'
            elif 'level_up' in filename:
                style = 'level_up'
            elif 'star_burst' in filename:
                style = 'star_burst'
            elif 'thinking' in description:
                style = 'thinking'
            elif 'camera' in description:
                style = 'camera'
            elif 'ai' in description or 'neural' in description:
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
            shutil.move(file_path, str(target_path))
            file_path = str(target_path)
        
        # Atualizar checklist
        manager.update_checklist_status(asset_id, 'completed')
        
        file_size = os.path.getsize(file_path) / 1024
        
        return f"""✅ Animação Lottie criada com sucesso!

🆔 **ID:** {asset_id}
📁 **Arquivo:** {spec.get('filename')}
📂 **Local:** {file_path}
📊 **Tamanho:** {file_size:.1f} KB
🎬 **Tipo/Estilo:** {anim_type}/{style}
⏱️ **Duração:** {duration}s
🔄 **Loop:** {'Sim' if loop else 'Não'}"""
        
    except Exception as e:
        return f"❌ Erro ao gerar Lottie: {str(e)}"


def create_svg_asset(asset_id: str) -> str:
    """
    Cria um arquivo SVG vetorial baseado no ID do ativo.
    
    Args:
        asset_id: ID do ativo (ex: 'UI-01', 'ICO-01', 'ACH-04')
        
    Returns:
        str: Status da criação com detalhes ou mensagem de erro
    """
    if not svg_available:
        return "❌ Erro: Ferramenta SVG não disponível."
    
    if not asset_manager_available:
        return "❌ Erro: AssetManager não disponível."
    
    try:
        manager = AssetManager()
        manager.load_asset_inventory()
        
        spec = manager.get_asset_specification(asset_id)
        if not spec:
            return f"❌ Erro: Ativo '{asset_id}' não encontrado no inventário."
        
        if spec.get('type') != 'svg':
            return f"❌ Erro: Ativo '{asset_id}' não é um arquivo SVG."
        
        # Tentar geração via Recraft primeiro
        import replicate
        try:
            description = spec.get('description', '')
            category = spec.get('category', '')
            
            # Preparar prompt otimizado baseado nas especificações do Professor Virtual
            # Contexto: App educacional para crianças brasileiras 7-11 anos
            brand_colors = "#4A90F2 (primary blue), #FF8A3D (orange accent), #7ED321 (green), #9B59B6 (purple)"
            
            # Base comum para todos os SVGs
            base = f"Professional SVG design for children's educational app Professor Virtual: {description}"
            base += f", vector art optimized for mobile, clean scalable design"
            base += f", child-friendly Brazilian educational context, age 7-11 years"
            base += f", brand colors: {brand_colors}"
            
            if category == 'ICO':
                # Ícones de navegação - baseado no template ICO do agente
                prompt = f"{base}, navigation icon design, 24x24dp base size"
                prompt += f", rounded friendly style, filled design with personality"
                prompt += f", simple shapes readable at 16px minimum"
                prompt += f", Flutter-compatible SVG without complex filters"
                prompt += f", playful but functional, approachable character"
                
            elif category == 'UI':
                # Padrões e elementos UI - baseado no template UI do agente
                prompt = f"{base}, UI pattern design for mobile interface"
                prompt += f", tileable seamless pattern" if 'pattern' in spec.get('filename', '') else ""
                prompt += f", educational theme with school elements" if 'school' in spec.get('filename', '') else ""
                prompt += f", playful distribution, various sizes" if 'dots' in spec.get('filename', '') or 'stars' in spec.get('filename', '') else ""
                prompt += f", soft gentle shapes, calming atmosphere" if 'clouds' in spec.get('filename', '') else ""
                prompt += f", child-appropriate visual density"
                
            elif 'badge' in spec.get('filename', ''):
                # Molduras de badges - baseado em ACH do agente
                prompt = f"{base}, achievement badge frame design"
                prompt += f", decorative border for gamification elements"
                level = "bronze" if 'bronze' in spec.get('filename', '') else "silver" if 'silver' in spec.get('filename', '') else "gold"
                prompt += f", {level} level visual hierarchy"
                prompt += f", celebratory but not overwhelming"
                prompt += f", clear distinction between levels"
                
            else:
                # Outros elementos SVG
                prompt = f"{base}, vector illustration"
                prompt += f", colorful and engaging for children"
                prompt += f", professional educational quality"
                prompt += f", mobile-optimized simplicity"
            
            output = replicate.run(
                "recraft-ai/recraft-20b-svg",
                input={
                    "size": "1024x1024",
                    "style": "vector_illustration/cartoon",
                    "prompt": prompt,
                    "aspect_ratio": "1:1"
                }
            )
            
            # Salvar SVG
            target_path = manager.get_asset_path(asset_id)
            os.makedirs(target_path.parent, exist_ok=True)
            
            if isinstance(output, str) and output.startswith('http'):
                import requests
                response = requests.get(output)
                response.raise_for_status()
                svg_content = response.text
            else:
                svg_content = output
            
            with open(str(target_path), 'w', encoding='utf-8') as f:
                f.write(svg_content)
            
            manager.update_checklist_status(asset_id, 'completed')
            file_size = os.path.getsize(target_path) / 1024
            
            return f"""✅ SVG criado com sucesso via Recraft!

🆔 **ID:** {asset_id}
📁 **Arquivo:** {spec.get('filename')}
📂 **Local:** {target_path}
📊 **Tamanho:** {file_size:.1f} KB
🚀 **Método:** Geração direta (Recraft-20b-svg)"""
            
        except Exception as e:
            # Fallback para pipeline PNG→SVG
            if not png_available:
                return f"❌ Erro: Recraft falhou ({str(e)}) e ferramenta PNG não disponível para fallback."
            
            return _create_svg_via_png_fallback(asset_id, spec, manager)
        
    except Exception as e:
        return f"❌ Erro ao criar SVG: {str(e)}"


def _create_svg_via_png_fallback(asset_id: str, spec: dict, manager) -> str:
    """Pipeline de fallback: PNG → SVG"""
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            generator = ImageGenerator()
            svg_generator = SVGGenerator()
            
            # Gerar PNG base
            prompt_details = {
                'description': spec.get('description', 'simple geometric shape'),
                'filename_base': f"temp_{asset_id.lower()}"
            }
            
            temp_png = generator.generate_png(
                asset_type='generico',
                prompt_details=prompt_details,
                model_name="black-forest-labs/flux-schnell",
                remove_bg=False
            )
            
            # Vetorizar
            target_path = manager.get_asset_path(asset_id)
            os.makedirs(target_path.parent, exist_ok=True)
            
            svg_generator.vectorize_and_save(
                input_image_path=temp_png,
                output_svg_path=str(target_path)
            )
            
            manager.update_checklist_status(asset_id, 'completed')
            file_size = os.path.getsize(target_path) / 1024
            
            return f"""✅ SVG criado com sucesso!

🆔 **ID:** {asset_id}
📁 **Arquivo:** {spec.get('filename')}
📂 **Local:** {target_path}
📊 **Tamanho:** {file_size:.1f} KB
🔧 **Método:** Pipeline PNG→SVG (fallback)"""
            
        except Exception as e:
            return f"❌ Erro no pipeline SVG: {str(e)}"


def create_audio_effect(asset_id: str) -> str:
    """
    Cria um efeito sonoro MP3 baseado no ID do ativo.
    
    Args:
        asset_id: ID do ativo (ex: 'SFX-01', 'SFX-02', etc.)
        
    Returns:
        str: Status da criação com detalhes ou mensagem de erro
    """
    if not audio_available:
        return "❌ Erro: Ferramenta de Áudio não disponível. Instale com: pip install pydub"
    
    if not asset_manager_available:
        return "❌ Erro: AssetManager não disponível."
    
    try:
        manager = AssetManager()
        manager.load_asset_inventory()
        
        spec = manager.get_asset_specification(asset_id)
        if not spec:
            return f"❌ Erro: Ativo '{asset_id}' não encontrado no inventário."
        
        if spec.get('type') != 'audio':
            return f"❌ Erro: Ativo '{asset_id}' não é um arquivo de áudio."
        
        generator = AudioEffectGenerator()
        
        # Obter caminho de destino
        target_path = manager.get_asset_path(asset_id)
        if not target_path:
            return f"❌ Erro: Caminho de destino não encontrado para {asset_id}"
        
        os.makedirs(target_path.parent, exist_ok=True)
        
        # Gerar o áudio
        output_path = generator.generate_sound_effect(
            asset_id=asset_id,
            output_dir=str(target_path.parent)
        )
        
        if not output_path:
            return f"❌ Erro ao gerar áudio para '{asset_id}'"
        
        # Atualizar checklist
        manager.update_checklist_status(asset_id, 'completed')
        
        file_size = os.path.getsize(output_path) / 1024
        config = generator.get_asset_info(asset_id)
        
        return f"""✅ Efeito sonoro criado com sucesso!

🆔 **ID:** {asset_id}
📁 **Arquivo:** {config.get('filename', 'N/A')}
📂 **Local:** {output_path}
📊 **Tamanho:** {file_size:.1f} KB
🎵 **Duração:** {config.get('duration', 0)}s
🎯 **Modelo:** {config.get('model', 'N/A')}"""
        
    except Exception as e:
        return f"❌ Erro ao gerar áudio: {str(e)}"


def create_mascot_animation(asset_id: str) -> str:
    """
    Cria uma animação Lottie do mascote baseada no ID do ativo.
    
    Args:
        asset_id: ID do ativo (ex: 'MAS-11', 'MAS-12', etc.)
        
    Returns:
        str: Status da criação com detalhes ou mensagem de erro
    """
    if not mascot_animator_available:
        return "❌ Erro: Ferramenta de Animação do Mascote não disponível."
    
    if not asset_manager_available:
        return "❌ Erro: AssetManager não disponível."
    
    try:
        manager = AssetManager()
        manager.load_asset_inventory()
        
        spec = manager.get_asset_specification(asset_id)
        if not spec:
            return f"❌ Erro: Ativo '{asset_id}' não encontrado no inventário."
        
        if spec.get('type') != 'lottie_mascote':
            return f"❌ Erro: Ativo '{asset_id}' não é uma animação do mascote."
        
        animator = MascotAnimator()
        
        # Detalhes para gerar o PNG base
        prompt_details_png = spec.get('prompt_details', {})
        animation_prompt = spec.get('animation_prompt', 'standing still and breathing gently')
        
        target_path = manager.get_asset_path(asset_id)
        if not target_path:
            return f"❌ Erro: Caminho de destino não encontrado para {asset_id}"
        
        os.makedirs(target_path.parent, exist_ok=True)
        
        result_path = animator.create_mascot_animation(
            prompt_details=prompt_details_png,
            animation_prompt=animation_prompt,
            output_path=str(target_path),
            output_format="lottie"
        )
        
        # Atualizar checklist
        manager.update_checklist_status(asset_id, 'completed')
        
        file_size = os.path.getsize(result_path) / 1024
        
        return f"""✅ Animação do mascote criada com sucesso!

🆔 **ID:** {asset_id}
📁 **Arquivo:** {os.path.basename(result_path)}
📂 **Local:** {result_path}
📊 **Tamanho:** {file_size:.1f} KB
🎬 **Prompt de Animação:** {animation_prompt}"""
        
    except Exception as e:
        return f"❌ Erro ao gerar animação do mascote: {str(e)}"


def get_creation_capabilities() -> str:
    """
    Lista as capacidades de criação deste agente.
    
    Returns:
        str: Lista detalhada de tipos de ativos que pode criar
    """
    return """🛠️ **Capacidades de Criação de Ativos**

Este agente especializado pode criar os seguintes tipos de ativos:

🎵 **Efeitos Sonoros MP3**
- Cliques, notificações, sucessos, erros
- Duração: 0.5s a 3s
- Qualidade: 44.1kHz, Stereo, -3dB
- Modelos: stable-audio-open, musicgen

🎬 **Animações Lottie Programáticas**
- Spinners, bounces, waves, checkmarks
- Categorias: Loading, Feedback, Achievement
- Formato: JSON otimizado, <100KB
- Duração configurável com suporte a loops

🎞️ **Animações do Mascote**
- Idle, bounce, wave, thinking, celebration
- Baseadas em PNG do mascote + animação IA
- Formato: Lottie JSON
- Pipeline: PNG → AnimateDiff → Lottie

🎨 **Arquivos SVG Vetoriais**
- Ícones, padrões, badges, elementos UI
- Geração via Recraft-20b-svg
- Fallback: PNG → Vetorização
- Otimizados com SVGO

💡 **Como usar:**
- Para criar um ativo específico, forneça o ID
- Exemplo: "Crie o ativo SFX-01"
- O agente verificará o inventário e executará a criação"""


# Criar o agente criador
asset_creator_agent = LlmAgent(
    name="asset_creator",
    model="gemini-2.0-flash-exp",
    description="Especialista em criação de ativos digitais usando IA generativa",
    instruction="""Você é o Agente Criador de Ativos, especializado em gerar assets digitais usando diversas ferramentas de IA.

Suas responsabilidades:
1. **Criar** ativos específicos quando solicitado com um ID válido
2. **Verificar** se o ativo existe no inventário antes de criar
3. **Selecionar** a ferramenta apropriada baseada no tipo de ativo
4. **Garantir** qualidade e conformidade com especificações
5. **Atualizar** o status do checklist após criação bem-sucedida

Princípios de operação:
- SEMPRE verificar o inventário antes de criar
- NUNCA criar ativos que não estejam catalogados
- Seguir especificações técnicas rigorosamente
- Reportar erros de forma clara e acionável
- Otimizar prompts para melhores resultados

Tipos de ativos que você pode criar:
- 🎵 Áudio: Efeitos sonoros MP3 infantis
- 🎬 Lottie: Animações programáticas e do mascote
- 🎨 SVG: Vetores, ícones e padrões
- 🦸 Mascote: Animações do personagem PROF

Use suas ferramentas especializadas para criar ativos de alta qualidade.""",
    tools=[
        FunctionTool(create_lottie_animation),
        FunctionTool(create_svg_asset),
        FunctionTool(create_audio_effect),
        FunctionTool(create_mascot_animation),
        FunctionTool(get_creation_capabilities)
    ]
)