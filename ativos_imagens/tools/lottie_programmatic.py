# ativos_imagens/tools/lottie_programmatic.py
"""
Gerador de animações Lottie programáticas.
Cria animações vetoriais usando código puro, sem dependência de IA ou ativos externos.
"""

import json
import os
from typing import Dict, Tuple, Optional
import math

try:
    from lottie import objects, Point, Color, NVector
    from lottie.utils import animation as animation_utils
except ImportError:
    raise ImportError("Por favor, instale python-lottie: pip install lottie")


class LottieProgrammaticGenerator:
    """Gera animações Lottie de forma programática para UI e feedback."""
    
    def __init__(self, output_dir: str = "ativos_imagens/output/lottie"):
        self.output_dir = output_dir
        self.default_fps = 60
        self.default_width = 512
        self.default_height = 512
        
        # Paleta de cores padrão do projeto
        self.colors = {
            "primary": Color(0.298, 0.686, 0.314),      # Verde #4CAF50
            "secondary": Color(0.129, 0.588, 0.953),    # Azul #2196F3
            "success": Color(0.298, 0.686, 0.314),      # Verde
            "error": Color(0.957, 0.263, 0.212),        # Vermelho #F44336
            "warning": Color(1.0, 0.757, 0.027),        # Amarelo #FFC107
            "white": Color(1, 1, 1),
            "black": Color(0, 0, 0),
            "gray": Color(0.5, 0.5, 0.5)
        }
        
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _create_animation(self, duration: float, name: str) -> objects.Animation:
        """Cria uma animação Lottie base."""
        an = objects.Animation()
        an.frame_rate = self.default_fps
        an.width = self.default_width
        an.height = self.default_height
        an.in_point = 0
        an.out_point = int(duration * self.default_fps)
        an.name = name
        return an
    
    def _save_animation(self, animation: objects.Animation, filename: str, 
                       optimize: bool = True) -> str:
        """Salva a animação em formato JSON e opcionalmente .lottie."""
        # Caminho completo
        json_path = os.path.join(self.output_dir, f"{filename}.json")
        
        # Exportar para JSON
        animation.tgs_sanitize()
        animation_data = animation.to_dict()
        
        # Otimização básica: truncar precisão
        if optimize:
            animation_data = self._optimize_json(animation_data)
        
        with open(json_path, 'w') as f:
            json.dump(animation_data, f, separators=(',', ':'))
        
        return json_path
    
    def _optimize_json(self, data: Dict) -> Dict:
        """Otimiza o JSON truncando valores float."""
        def truncate_floats(obj):
            if isinstance(obj, float):
                return round(obj, 3)
            elif isinstance(obj, dict):
                return {k: truncate_floats(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [truncate_floats(item) for item in obj]
            return obj
        
        return truncate_floats(data)
    
    # === IMPLEMENTAÇÃO DAS ANIMAÇÕES ===
    
    def generate_loading_spinner(self, duration: float = 2.0, loop: bool = True,
                                colors: Optional[Tuple[str, str]] = None) -> str:
        """
        Gera um spinner circular com gradiente rotativo.
        
        Args:
            duration: Duração em segundos
            loop: Se deve repetir infinitamente
            colors: Tupla com duas cores para o gradiente
        
        Returns:
            Caminho do arquivo gerado
        """
        an = self._create_animation(duration, "loading_spinner")
        
        # Criar camada principal
        layer = objects.ShapeLayer()
        an.add_layer(layer)
        
        # Centralizar no canvas
        layer.transform.position.value = Point(256, 256)
        
        # Grupo de formas
        group = layer.add_shape(objects.Group())
        
        # Criar círculo (arco)
        ellipse = group.add_shape(objects.Ellipse())
        ellipse.size.value = Point(100, 100)
        
        # Aplicar Trim para criar arco
        trim = group.add_shape(objects.Trim())
        trim.start.value = 0
        trim.end.value = 75  # 75% do círculo
        
        # Stroke com gradiente
        stroke = group.add_shape(objects.Stroke())
        stroke.width.value = 8
        
        # Usar cores fornecidas ou padrão
        if colors:
            stroke.color.value = self.colors.get(colors[0], self.colors["primary"])
        else:
            stroke.color.value = self.colors["primary"]
        
        # Animar rotação
        frames = int(duration * self.default_fps)
        layer.transform.rotation.add_keyframe(0, 0)
        layer.transform.rotation.add_keyframe(frames, 360)
        
        # Configurar loop se necessário
        if loop:
            # TODO: Adicionar marcador de loop quando python-lottie suportar
            pass
        
        return self._save_animation(an, "loading_spinner")
    
    def generate_success_checkmark(self, duration: float = 0.8, 
                                  color: Optional[str] = None) -> str:
        """
        Gera animação de checkmark sendo desenhado.
        
        Args:
            duration: Duração em segundos
            color: Cor do checkmark
        
        Returns:
            Caminho do arquivo gerado
        """
        an = self._create_animation(duration, "success_checkmark")
        
        # Criar camada
        layer = objects.ShapeLayer()
        an.add_layer(layer)
        
        # Grupo de formas
        group = layer.add_shape(objects.Group())
        
        # Definir o path do checkmark
        path = objects.Path()
        # Pontos do checkmark: início, cotovelo, fim
        path.shape.value = objects.Bezier()
        path.shape.value.add_point(Point(180, 256))  # Início
        path.shape.value.add_point(Point(230, 306))  # Cotovelo
        path.shape.value.add_point(Point(332, 204))  # Fim
        path.shape.value.closed = False
        
        group.add_shape(path)
        
        # Adicionar stroke
        stroke = group.add_shape(objects.Stroke())
        stroke.width.value = 16
        stroke.line_cap = objects.LineCap.Round
        stroke.line_join = objects.LineJoin.Round
        
        # Cor
        if color:
            stroke.color.value = self.colors.get(color, self.colors["success"])
        else:
            stroke.color.value = self.colors["success"]
        
        # Adicionar Trim para animação de desenho
        trim = group.add_shape(objects.Trim())
        
        # Animar o desenho do checkmark
        frames = int(duration * self.default_fps)
        
        # Começar com path invisível
        trim.end.add_keyframe(0, 0)
        # Terminar com path completo
        trim.end.add_keyframe(frames, 100)
        
        # Adicionar um pequeno bounce no final
        bounce_start = int(frames * 0.7)
        layer.transform.scale.add_keyframe(0, Point(100, 100))
        layer.transform.scale.add_keyframe(bounce_start, Point(100, 100))
        layer.transform.scale.add_keyframe(bounce_start + 5, Point(110, 110))
        layer.transform.scale.add_keyframe(frames, Point(100, 100))
        
        return self._save_animation(an, "success_checkmark")
    
    def generate_touch_ripple(self, duration: float = 0.6,
                             color: Optional[str] = None) -> str:
        """
        Gera animação de ripple (ondulação) para feedback de toque.
        
        Args:
            duration: Duração em segundos
            color: Cor do ripple
        
        Returns:
            Caminho do arquivo gerado
        """
        an = self._create_animation(duration, "touch_ripple")
        
        # Criar múltiplas camadas para efeito de ondas
        num_ripples = 3
        delay_between = 0.1  # segundos
        
        for i in range(num_ripples):
            layer = objects.ShapeLayer()
            layer.name = f"ripple_{i}"
            an.add_layer(layer)
            
            # Centralizar
            layer.transform.position.value = Point(256, 256)
            
            # Grupo
            group = layer.add_shape(objects.Group())
            
            # Círculo
            circle = group.add_shape(objects.Ellipse())
            circle.size.value = Point(50, 50)
            
            # Stroke (sem fill)
            stroke = group.add_shape(objects.Stroke())
            stroke.width.value = 3
            
            # Cor
            if color:
                stroke.color.value = self.colors.get(color, self.colors["primary"])
            else:
                stroke.color.value = self.colors["primary"]
            
            # Calcular timing com delay
            start_frame = int(i * delay_between * self.default_fps)
            end_frame = int(duration * self.default_fps)
            
            # Animar scale (crescer)
            layer.transform.scale.add_keyframe(start_frame, Point(0, 0))
            layer.transform.scale.add_keyframe(end_frame, Point(400, 400))
            
            # Animar opacidade (fade out)
            layer.transform.opacity.add_keyframe(start_frame, 100)
            layer.transform.opacity.add_keyframe(int(start_frame + (end_frame - start_frame) * 0.3), 100)
            layer.transform.opacity.add_keyframe(end_frame, 0)
        
        return self._save_animation(an, "touch_ripple")
    
    # === FUNÇÃO PRINCIPAL GENÉRICA ===
    
    def generate_animation(self, animation_type: str, style: str, 
                         duration: float = 1.0, loop: bool = False,
                         colors: Optional[list] = None, 
                         custom_params: Optional[Dict] = None) -> str:
        """
        Gera uma animação de forma genérica baseada em tipo e estilo.
        
        Args:
            animation_type: Tipo da animação ('loading', 'feedback', 'achievement')
            style: Estilo específico ('spinner', 'bounce', 'wave', etc)
            duration: Duração em segundos
            loop: Se deve repetir infinitamente
            colors: Lista de cores a usar
            custom_params: Parâmetros customizados específicos
        
        Returns:
            Caminho do arquivo gerado
        
        Raises:
            ValueError: Se tipo/estilo não for suportado
        """
        # Mapear tipo+estilo para método apropriado
        if animation_type == "loading":
            if style == "spinner":
                return self.generate_loading_spinner(duration, loop, colors)
            elif style == "bounce":
                return self._generate_loading_bounce(duration, loop, colors)
            elif style == "wave":
                return self._generate_loading_wave(duration, loop, colors)
            elif style == "thinking":
                return self._generate_loading_thinking(duration, loop, colors)
            elif style == "camera":
                return self._generate_loading_camera(duration, loop, colors)
            elif style == "ai":
                return self._generate_loading_ai(duration, loop, colors)
                
        elif animation_type == "feedback":
            if style == "ripple":
                return self.generate_touch_ripple(duration, colors[0] if colors else None)
            elif style == "checkmark":
                return self.generate_success_checkmark(duration, colors[0] if colors else None)
            elif style == "shake":
                return self._generate_error_shake(duration, colors)
            elif style == "pulse":
                return self._generate_hint_pulse(duration, loop, colors)
                
        elif animation_type == "achievement":
            if style == "unlock":
                return self._generate_achievement_unlock(duration, colors)
            elif style == "level_up":
                return self._generate_level_up(duration, colors)
            elif style == "star_burst":
                return self._generate_star_burst(duration, colors)
                
        raise ValueError(f"Combinação não suportada: {animation_type}/{style}")
    
    # === NOVAS IMPLEMENTAÇÕES DE ANIMAÇÕES ===
    
    def _generate_loading_bounce(self, duration: float = 1.5, loop: bool = True,
                                colors: Optional[list] = None) -> str:
        """Gera animação de 3 pontos pulando alternadamente."""
        an = self._create_animation(duration, "loading_bounce")
        
        num_dots = 3
        dot_size = 20
        spacing = 40
        total_width = (num_dots - 1) * spacing
        start_x = 256 - total_width / 2
        
        for i in range(num_dots):
            layer = objects.ShapeLayer()
            layer.name = f"dot_{i}"
            an.add_layer(layer)
            
            # Posicionar horizontalmente
            x = start_x + i * spacing
            layer.transform.position.value = Point(x, 256)
            
            # Grupo
            group = layer.add_shape(objects.Group())
            
            # Círculo
            circle = group.add_shape(objects.Ellipse())
            circle.size.value = Point(dot_size, dot_size)
            
            # Fill
            fill = group.add_shape(objects.Fill())
            if colors and i < len(colors):
                fill.color.value = self.colors.get(colors[i], self.colors["primary"])
            else:
                fill.color.value = self.colors["primary"]
            
            # Animar Y position (pulo)
            frames = int(duration * self.default_fps)
            bounce_height = 30
            delay_frames = int(i * 0.2 * self.default_fps)
            
            for cycle in range(int(duration)):
                start = cycle * self.default_fps + delay_frames
                mid = start + self.default_fps // 4
                end = start + self.default_fps // 2
                
                if start < frames:
                    layer.transform.position.add_keyframe(start, Point(x, 256))
                if mid < frames:
                    layer.transform.position.add_keyframe(mid, Point(x, 256 - bounce_height))
                if end < frames:
                    layer.transform.position.add_keyframe(end, Point(x, 256))
        
        return self._save_animation(an, "loading_bounce")
    
    def _generate_loading_wave(self, duration: float = 2.0, loop: bool = True,
                              colors: Optional[list] = None) -> str:
        """Gera animação de onda fluida."""
        an = self._create_animation(duration, "loading_wave")
        
        layer = objects.ShapeLayer()
        an.add_layer(layer)
        
        group = layer.add_shape(objects.Group())
        
        # Criar path de onda
        path = objects.Path()
        bezier = objects.Bezier()
        
        # Pontos da onda (será animada)
        wave_points = 5
        wave_width = 300
        wave_height = 50
        start_x = 256 - wave_width / 2
        
        for i in range(wave_points):
            x = start_x + (i / (wave_points - 1)) * wave_width
            y = 256
            bezier.add_point(Point(x, y))
        
        path.shape.value = bezier
        path.shape.value.closed = False
        group.add_shape(path)
        
        # Stroke
        stroke = group.add_shape(objects.Stroke())
        stroke.width.value = 6
        stroke.color.value = self.colors.get(colors[0] if colors else "primary", self.colors["primary"])
        
        # Animar pontos da onda
        frames = int(duration * self.default_fps)
        for frame in range(0, frames, 2):
            phase = (frame / frames) * 2 * math.pi
            new_bezier = objects.Bezier()
            
            for i in range(wave_points):
                x = start_x + (i / (wave_points - 1)) * wave_width
                y = 256 + math.sin(phase + i * math.pi / 2) * wave_height
                new_bezier.add_point(Point(x, y))
            
            new_bezier.closed = False
            path.shape.add_keyframe(frame, new_bezier)
        
        return self._save_animation(an, "loading_wave")
    
    def _generate_loading_thinking(self, duration: float = 3.0, loop: bool = True,
                                  colors: Optional[list] = None) -> str:
        """Gera animação de cérebro com lâmpadas acendendo."""
        # Implementação simplificada: círculos representando ideias
        an = self._create_animation(duration, "loading_thinking")
        
        # Círculo central (cérebro)
        brain_layer = objects.ShapeLayer()
        brain_layer.name = "brain"
        an.add_layer(brain_layer)
        brain_layer.transform.position.value = Point(256, 256)
        
        brain_group = brain_layer.add_shape(objects.Group())
        brain_circle = brain_group.add_shape(objects.Ellipse())
        brain_circle.size.value = Point(80, 80)
        
        brain_stroke = brain_group.add_shape(objects.Stroke())
        brain_stroke.width.value = 4
        brain_stroke.color.value = self.colors["gray"]
        
        # Lâmpadas ao redor
        num_bulbs = 3
        radius = 100
        
        for i in range(num_bulbs):
            layer = objects.ShapeLayer()
            layer.name = f"bulb_{i}"
            an.add_layer(layer)
            
            angle = (i / num_bulbs) * 2 * math.pi - math.pi / 2
            x = 256 + radius * math.cos(angle)
            y = 256 + radius * math.sin(angle)
            layer.transform.position.value = Point(x, y)
            
            group = layer.add_shape(objects.Group())
            
            # Lâmpada (círculo)
            bulb = group.add_shape(objects.Ellipse())
            bulb.size.value = Point(30, 30)
            
            fill = group.add_shape(objects.Fill())
            fill.color.value = self.colors["warning"]
            
            # Animar opacidade (piscar)
            frames = int(duration * self.default_fps)
            delay = int(i * 0.5 * self.default_fps)
            
            layer.transform.opacity.add_keyframe(delay, 0)
            layer.transform.opacity.add_keyframe(delay + 10, 100)
            layer.transform.opacity.add_keyframe(delay + 30, 100)
            layer.transform.opacity.add_keyframe(delay + 40, 0)
        
        return self._save_animation(an, "loading_thinking")
    
    def _generate_loading_camera(self, duration: float = 1.5, loop: bool = True,
                                colors: Optional[list] = None) -> str:
        """Gera animação de íris de câmera abrindo e fechando."""
        an = self._create_animation(duration, "loading_camera")
        
        layer = objects.ShapeLayer()
        an.add_layer(layer)
        layer.transform.position.value = Point(256, 256)
        
        # Criar 6 lâminas da íris
        num_blades = 6
        
        for i in range(num_blades):
            group = layer.add_shape(objects.Group())
            group.transform.rotation.value = (i * 360 / num_blades)
            
            # Triângulo representando lâmina
            path = objects.Path()
            bezier = objects.Bezier()
            bezier.add_point(Point(0, 0))
            bezier.add_point(Point(-30, 100))
            bezier.add_point(Point(30, 100))
            bezier.closed = True
            path.shape.value = bezier
            
            group.add_shape(path)
            
            fill = group.add_shape(objects.Fill())
            fill.color.value = self.colors.get(colors[0] if colors else "black", self.colors["black"])
            
            # Animar rotação das lâminas
            frames = int(duration * self.default_fps)
            mid_frame = frames // 2
            
            group.transform.rotation.add_keyframe(0, i * 60)
            group.transform.rotation.add_keyframe(mid_frame, i * 60 + 30)
            group.transform.rotation.add_keyframe(frames, i * 60)
        
        return self._save_animation(an, "loading_camera")
    
    def _generate_loading_ai(self, duration: float = 2.5, loop: bool = True,
                            colors: Optional[list] = None) -> str:
        """Gera animação de rede neural com conexões pulsantes."""
        an = self._create_animation(duration, "loading_ai")
        
        # Criar nós da rede
        nodes = [
            [(156, 256)],  # Input layer
            [(206, 156), (206, 256), (206, 356)],  # Hidden layer
            [(256, 206), (256, 306)],  # Hidden layer 2  
            [(306, 256)]  # Output layer
        ]
        
        # Desenhar nós
        for layer_idx, layer_nodes in enumerate(nodes):
            for node_idx, (x, y) in enumerate(layer_nodes):
                node_layer = objects.ShapeLayer()
                node_layer.name = f"node_{layer_idx}_{node_idx}"
                an.add_layer(node_layer)
                node_layer.transform.position.value = Point(x, y)
                
                group = node_layer.add_shape(objects.Group())
                circle = group.add_shape(objects.Ellipse())
                circle.size.value = Point(20, 20)
                
                fill = group.add_shape(objects.Fill())
                fill.color.value = self.colors.get(colors[0] if colors else "secondary", self.colors["secondary"])
                
                # Animar opacidade pulsante
                frames = int(duration * self.default_fps)
                pulse_duration = 30
                delay = int((layer_idx * 0.2) * self.default_fps)
                
                for t in range(0, frames, pulse_duration * 2):
                    if t + delay < frames:
                        node_layer.transform.opacity.add_keyframe(t + delay, 30)
                    if t + delay + pulse_duration < frames:
                        node_layer.transform.opacity.add_keyframe(t + delay + pulse_duration, 100)
        
        return self._save_animation(an, "loading_ai")
    
    def _generate_error_shake(self, duration: float = 0.5, 
                             colors: Optional[list] = None) -> str:
        """Gera animação de tremor para indicar erro."""
        an = self._create_animation(duration, "error_shake")
        
        layer = objects.ShapeLayer()
        an.add_layer(layer)
        layer.transform.position.value = Point(256, 256)
        
        group = layer.add_shape(objects.Group())
        
        # X vermelho
        for i in range(2):
            line = group.add_shape(objects.Path())
            bezier = objects.Bezier()
            
            if i == 0:
                bezier.add_point(Point(-30, -30))
                bezier.add_point(Point(30, 30))
            else:
                bezier.add_point(Point(-30, 30))
                bezier.add_point(Point(30, -30))
                
            bezier.closed = False
            line.shape.value = bezier
            
            stroke = group.add_shape(objects.Stroke())
            stroke.width.value = 8
            stroke.color.value = self.colors["error"]
            stroke.line_cap = objects.LineCap.Round
        
        # Animar shake horizontal
        frames = int(duration * self.default_fps)
        shake_amplitude = 10
        shake_speed = 4
        
        for frame in range(0, frames, 2):
            offset = shake_amplitude * math.sin(frame * shake_speed)
            layer.transform.position.add_keyframe(frame, Point(256 + offset, 256))
        
        return self._save_animation(an, "error_shake")
    
    def _generate_hint_pulse(self, duration: float = 2.0, loop: bool = True,
                            colors: Optional[list] = None) -> str:
        """Gera efeito de brilho pulsante para dicas."""
        an = self._create_animation(duration, "hint_pulse")
        
        layer = objects.ShapeLayer()
        an.add_layer(layer)
        layer.transform.position.value = Point(256, 256)
        
        # Criar múltiplos círculos concêntricos
        num_rings = 3
        
        for i in range(num_rings):
            group = layer.add_shape(objects.Group())
            
            circle = group.add_shape(objects.Ellipse())
            size = 40 + i * 30
            circle.size.value = Point(size, size)
            
            stroke = group.add_shape(objects.Stroke())
            stroke.width.value = 3
            stroke.color.value = self.colors.get(colors[0] if colors else "warning", self.colors["warning"])
            
            # Animar opacidade e escala
            frames = int(duration * self.default_fps)
            delay = int(i * 0.2 * self.default_fps)
            
            # Opacidade
            stroke.opacity.add_keyframe(delay, 0)
            stroke.opacity.add_keyframe(delay + 20, 100)
            stroke.opacity.add_keyframe(frames - 20, 100)
            stroke.opacity.add_keyframe(frames, 0)
            
            # Escala
            group.transform.scale.add_keyframe(delay, Point(80, 80))
            group.transform.scale.add_keyframe(frames, Point(120, 120))
        
        return self._save_animation(an, "hint_pulse")
    
    def _generate_achievement_unlock(self, duration: float = 2.0,
                                   colors: Optional[list] = None) -> str:
        """Gera animação de revelação de badge."""
        an = self._create_animation(duration, "achievement_unlock")
        
        layer = objects.ShapeLayer()
        an.add_layer(layer)
        layer.transform.position.value = Point(256, 256)
        
        # Badge (estrela)
        group = layer.add_shape(objects.Group())
        
        star = group.add_shape(objects.Star())
        star.inner_radius.value = 30
        star.outer_radius.value = 60
        star.points.value = 5
        
        fill = group.add_shape(objects.Fill())
        fill.color.value = self.colors.get(colors[0] if colors else "warning", self.colors["warning"])
        
        # Animar escala e rotação
        frames = int(duration * self.default_fps)
        
        layer.transform.scale.add_keyframe(0, Point(0, 0))
        layer.transform.scale.add_keyframe(30, Point(120, 120))
        layer.transform.scale.add_keyframe(40, Point(100, 100))
        
        layer.transform.rotation.add_keyframe(0, 0)
        layer.transform.rotation.add_keyframe(40, 360)
        
        # Adicionar brilho
        for i in range(4):
            sparkle = objects.ShapeLayer()
            sparkle.name = f"sparkle_{i}"
            an.add_layer(sparkle)
            
            angle = i * 90
            distance = 100
            x = 256 + distance * math.cos(math.radians(angle))
            y = 256 + distance * math.sin(math.radians(angle))
            sparkle.transform.position.value = Point(x, y)
            
            s_group = sparkle.add_shape(objects.Group())
            s_circle = s_group.add_shape(objects.Ellipse())
            s_circle.size.value = Point(10, 10)
            
            s_fill = s_group.add_shape(objects.Fill())
            s_fill.color.value = self.colors["white"]
            
            # Animar brilho
            sparkle.transform.opacity.add_keyframe(30, 0)
            sparkle.transform.opacity.add_keyframe(35, 100)
            sparkle.transform.opacity.add_keyframe(50, 0)
        
        return self._save_animation(an, "achievement_unlock")
    
    def _generate_level_up(self, duration: float = 3.0,
                          colors: Optional[list] = None) -> str:
        """Gera celebração de subida de nível."""
        an = self._create_animation(duration, "level_up")
        
        # Texto "LEVEL UP" (simplificado como retângulos)
        text_layer = objects.ShapeLayer()
        text_layer.name = "level_text"
        an.add_layer(text_layer)
        text_layer.transform.position.value = Point(256, 256)
        
        group = text_layer.add_shape(objects.Group())
        rect = group.add_shape(objects.Rect())
        rect.size.value = Point(150, 40)
        rect.corner_radius.value = 20
        
        fill = group.add_shape(objects.Fill())
        fill.color.value = self.colors.get(colors[0] if colors else "primary", self.colors["primary"])
        
        # Animar entrada
        frames = int(duration * self.default_fps)
        
        text_layer.transform.scale.add_keyframe(0, Point(0, 0))
        text_layer.transform.scale.add_keyframe(20, Point(130, 130))
        text_layer.transform.scale.add_keyframe(30, Point(100, 100))
        
        # Partículas subindo
        for i in range(8):
            particle = objects.ShapeLayer()
            particle.name = f"particle_{i}"
            an.add_layer(particle)
            
            angle = i * 45
            start_x = 256 + 50 * math.cos(math.radians(angle))
            start_y = 356
            
            particle.transform.position.value = Point(start_x, start_y)
            
            p_group = particle.add_shape(objects.Group())
            p_circle = p_group.add_shape(objects.Ellipse())
            p_circle.size.value = Point(8, 8)
            
            p_fill = p_group.add_shape(objects.Fill())
            p_fill.color.value = self.colors["warning"]
            
            # Animar subida
            delay = int(i * 0.1 * self.default_fps)
            particle.transform.position.add_keyframe(delay, Point(start_x, start_y))
            particle.transform.position.add_keyframe(delay + 40, Point(start_x, start_y - 200))
            
            particle.transform.opacity.add_keyframe(delay, 100)
            particle.transform.opacity.add_keyframe(delay + 40, 0)
        
        return self._save_animation(an, "level_up")
    
    def _generate_star_burst(self, duration: float = 1.5,
                            colors: Optional[list] = None) -> str:
        """Gera explosão de estrelas."""
        an = self._create_animation(duration, "star_burst")
        
        # Criar múltiplas estrelas explodindo do centro
        num_stars = 8
        
        for i in range(num_stars):
            layer = objects.ShapeLayer()
            layer.name = f"star_{i}"
            an.add_layer(layer)
            
            # Começar no centro
            layer.transform.position.value = Point(256, 256)
            
            group = layer.add_shape(objects.Group())
            
            star = group.add_shape(objects.Star())
            star.inner_radius.value = 5
            star.outer_radius.value = 10
            star.points.value = 5
            
            fill = group.add_shape(objects.Fill())
            if colors and i < len(colors):
                fill.color.value = self.colors.get(colors[i % len(colors)], self.colors["warning"])
            else:
                fill.color.value = self.colors["warning"]
            
            # Animar explosão
            frames = int(duration * self.default_fps)
            angle = i * (360 / num_stars)
            end_x = 256 + 150 * math.cos(math.radians(angle))
            end_y = 256 + 150 * math.sin(math.radians(angle))
            
            # Posição
            layer.transform.position.add_keyframe(0, Point(256, 256))
            layer.transform.position.add_keyframe(frames, Point(end_x, end_y))
            
            # Escala
            layer.transform.scale.add_keyframe(0, Point(0, 0))
            layer.transform.scale.add_keyframe(10, Point(150, 150))
            layer.transform.scale.add_keyframe(frames, Point(50, 50))
            
            # Rotação
            layer.transform.rotation.add_keyframe(0, 0)
            layer.transform.rotation.add_keyframe(frames, 720)
            
            # Opacidade
            layer.transform.opacity.add_keyframe(0, 100)
            layer.transform.opacity.add_keyframe(int(frames * 0.7), 100)
            layer.transform.opacity.add_keyframe(frames, 0)
        
        return self._save_animation(an, "star_burst")
    
    # === RETROCOMPATIBILIDADE ===
    
    def generate(self, animation_name: str, **kwargs) -> str:
        """
        Mantém compatibilidade com a interface antiga.
        Mapeia nomes antigos para o novo sistema.
        """
        # Mapear nomes antigos para tipo/estilo
        legacy_map = {
            "loading_spinner": ("loading", "spinner"),
            "success_checkmark": ("feedback", "checkmark"),
            "touch_ripple": ("feedback", "ripple"),
        }
        
        if animation_name in legacy_map:
            anim_type, style = legacy_map[animation_name]
            return self.generate_animation(anim_type, style, **kwargs)
        
        # Tentar inferir tipo e estilo do nome
        if animation_name.startswith("loading_"):
            style = animation_name.replace("loading_", "")
            return self.generate_animation("loading", style, **kwargs)
        elif animation_name.startswith("achievement_"):
            style = animation_name.replace("achievement_", "")
            return self.generate_animation("achievement", style, **kwargs)
        elif animation_name in ["error_shake", "hint_pulse"]:
            style = animation_name.replace("error_", "").replace("hint_", "")
            return self.generate_animation("feedback", style, **kwargs)
            
        raise ValueError(f"Animação '{animation_name}' não reconhecida")


# Teste rápido se executado diretamente
if __name__ == "__main__":
    generator = LottieProgrammaticGenerator()
    
    print("Gerando animações de teste...")
    
    # Testar as 3 animações
    try:
        spinner_path = generator.generate("loading_spinner", duration=2.0)
        print(f"✓ Loading spinner gerado: {spinner_path}")
        
        check_path = generator.generate("success_checkmark", duration=0.8)
        print(f"✓ Success checkmark gerado: {check_path}")
        
        ripple_path = generator.generate("touch_ripple", duration=0.6)
        print(f"✓ Touch ripple gerado: {ripple_path}")
        
    except Exception as e:
        print(f"✗ Erro: {e}")