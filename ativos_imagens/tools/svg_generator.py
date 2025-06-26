"""
SVG Generator - Gerador de arquivos SVG para UI, ícones e padrões
"""
import os
import math
from typing import Dict, List, Optional, Tuple
import xml.etree.ElementTree as ET
from xml.dom import minidom
import subprocess
from pathlib import Path
from lxml import etree

PROJECT_PALETTE = ["#4A90F2", "#FF8A3D", "#7ED321", "#9B59B6", "#FFC107", "#00D4AA"]

class SVGGenerator:
    """
    Ferramenta especialista para converter imagens raster (PNG) em vetores (SVG),
    incluindo otimização e padronização de paleta.
    """

    def _vectorize_image_local(self, input_path: str, output_path: str) -> None:
        """Vetoriza uma imagem usando VTracer (preferencial) ou Autotrace."""
        print(f"INFO: Vetorizando '{input_path}' localmente...")
        try:
            # Tenta usar VTracer primeiro por sua qualidade superior
            subprocess.run(
                ["vtracer", "-i", input_path, "-o", output_path, "-s", "3", "--colormode", "palette", "--palette-size", "16"],
                check=True, capture_output=True, text=True
            )
            print("INFO: Vetorização com VTracer concluída.")
        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            print(f"WARN: VTracer falhou ({e}). Tentando com Autotrace...")
            try:
                # Fallback para Autotrace se VTracer não estiver disponível
                subprocess.run(
                    ["autotrace", input_path, "--output-file", output_path, "--output-format", "svg", "--color-count", "16", "--background-color", "FFFFFF"],
                    check=True, capture_output=True, text=True
                )
                print("INFO: Vetorização com Autotrace concluída.")
            except (FileNotFoundError, subprocess.CalledProcessError) as e_auto:
                 raise RuntimeError(f"Falha na vetorização: VTracer e Autotrace não encontrados ou falharam. Erro: {e_auto}") from e_auto


    def _optimize_svg(self, svg_path: str) -> None:
        """Otimiza um arquivo SVG usando Scour."""
        print(f"INFO: Otimizando '{svg_path}' com Scour...")
        try:
            subprocess.run(
                ["scour", "-i", svg_path, "-o", svg_path, "--enable-id-stripping", "--enable-comment-stripping", "--shorten-ids", "--indent=none"],
                check=True
            )
            print("INFO: Otimização com Scour concluída.")
        except FileNotFoundError:
            print("WARN: Scour não encontrado. Pulando etapa de otimização.")


    def _standardize_palette(self, svg_path: str) -> None:
        """Ajusta as cores de um SVG para a paleta padrão do projeto."""
        print(f"INFO: Padronizando paleta de cores para '{svg_path}'...")
        try:
            parser = etree.XMLParser(remove_blank_text=True)
            svg_tree = etree.parse(svg_path, parser)
            
            for element in svg_tree.xpath('//*[@fill]'):
                old_color_hex = element.attrib.get('fill', '').lower()
                if old_color_hex.startswith('#') and len(old_color_hex) == 7:
                    r, g, b = int(old_color_hex[1:3], 16), int(old_color_hex[3:5], 16), int(old_color_hex[5:], 16)
                    
                    # Encontra a cor mais próxima na paleta do projeto
                    best_color = min(PROJECT_PALETTE, key=lambda c: sum(abs(int(c[i:i+2], 16) - v) for i, v in zip((1, 3, 5), (r, g, b))))
                    element.attrib['fill'] = best_color
            
            svg_tree.write(svg_path, pretty_print=False)
            print("INFO: Paleta de cores padronizada.")
        except Exception as e:
            print(f"WARN: Falha ao padronizar paleta de cores para {svg_path}. Erro: {e}")

    def vectorize_and_save(self, input_image_path: str, output_svg_path: str) -> None:
        """
        Executa o pipeline completo de conversão de PNG para SVG.
        
        Args:
            input_image_path: Caminho para a imagem PNG de entrada.
            output_svg_path: Caminho onde o SVG final será salvo.
        """
        if not Path(input_image_path).exists():
            raise FileNotFoundError(f"Arquivo de imagem de entrada não encontrado: {input_image_path}")

        # Etapa 1: Vetorizar
        self._vectorize_image_local(input_image_path, output_svg_path)
        
        # Etapa 2: Padronizar paleta
        self._standardize_palette(output_svg_path)

        # Etapa 3: Otimizar
        self._optimize_svg(output_svg_path)

    def __init__(self, output_dir: str = "ativos_imagens/output/svg"):
        self.output_dir = output_dir
        
        # Paleta de cores padrão
        self.colors = {
            "primary": "#4CAF50",
            "secondary": "#2196F3",
            "success": "#4CAF50",
            "error": "#F44336",
            "warning": "#FFC107",
            "white": "#FFFFFF",
            "black": "#000000",
            "gray": "#808080",
            "light_gray": "#F0F0F0",
            "dark_gray": "#404040",
            # Cores infantis adicionais
            "pink": "#E91E63",
            "purple": "#9C27B0",
            "orange": "#FF9800",
            "yellow": "#FFEB3B",
            "cyan": "#00BCD4",
            "teal": "#009688",
            "brown": "#795548"
        }
        
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_svg(self, svg_type: str, style: str,
                    size: Tuple[int, int] = (24, 24),
                    colors: Optional[List[str]] = None,
                    custom_params: Optional[Dict] = None) -> str:
        """
        Gera um SVG de forma genérica baseado em tipo e estilo.
        
        Args:
            svg_type: Tipo do SVG ('pattern', 'icon', 'frame', 'decorative')
            style: Estilo específico (ex: 'dots', 'camera_fun', 'bronze')
            size: Tamanho do SVG (largura, altura)
            colors: Lista de cores a usar
            custom_params: Parâmetros customizados
        
        Returns:
            Caminho do arquivo gerado
        """
        if svg_type == "pattern":
            if style == "dots":
                return self._generate_pattern_dots(size, colors)
            elif style == "stars":
                return self._generate_pattern_stars(size, colors)
            elif style == "clouds":
                return self._generate_pattern_clouds(size, colors)
            elif style == "school":
                return self._generate_pattern_school(size, colors)
                
        elif svg_type == "icon":
            if style == "camera_fun":
                return self._generate_icon_camera_fun(size, colors)
            elif style == "microphone_fun":
                return self._generate_icon_microphone_fun(size, colors)
            elif style == "history_fun":
                return self._generate_icon_history_fun(size, colors)
            elif style == "achievements_fun":
                return self._generate_icon_achievements_fun(size, colors)
            elif style == "settings_fun":
                return self._generate_icon_settings_fun(size, colors)
            elif style == "help_fun":
                return self._generate_icon_help_fun(size, colors)
                
        elif svg_type == "frame":
            level = custom_params.get("level", "bronze") if custom_params else "bronze"
            if style == "badge_frame":
                return self._generate_badge_frame(level, size, colors)
                
        elif svg_type == "decorative":
            if style == "bubble":
                return self._generate_bubble_decoration(size, colors)
            elif style == "rainbow":
                return self._generate_rainbow_arc(size, colors)
                
        raise ValueError(f"Combinação não suportada: {svg_type}/{style}")
    
    def _create_svg_root(self, width: int, height: int, viewbox: Optional[str] = None) -> ET.Element:
        """Cria elemento SVG raiz com atributos padrão."""
        svg = ET.Element('svg')
        svg.set('xmlns', 'http://www.w3.org/2000/svg')
        svg.set('width', str(width))
        svg.set('height', str(height))
        svg.set('viewBox', viewbox or f"0 0 {width} {height}")
        return svg
    
    def _save_svg(self, root: ET.Element, filename: str) -> str:
        """Salva o SVG formatado."""
        # Converter para string e formatar
        rough_string = ET.tostring(root, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")
        
        # Remover linha extra do XML declaration
        lines = pretty_xml.split('\n')
        pretty_xml = '\n'.join([line for line in lines if line.strip()])
        
        # Salvar arquivo
        filepath = os.path.join(self.output_dir, f"{filename}.svg")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)
            
        return filepath
    
    # === IMPLEMENTAÇÃO DE PADRÕES ===
    
    def _generate_pattern_dots(self, size: Tuple[int, int] = (100, 100),
                              colors: Optional[List[str]] = None) -> str:
        """Gera padrão de bolinhas coloridas (tileable)."""
        svg = self._create_svg_root(size[0], size[1])
        
        # Definir padrão
        defs = ET.SubElement(svg, 'defs')
        pattern = ET.SubElement(defs, 'pattern')
        pattern.set('id', 'dots-pattern')
        pattern.set('patternUnits', 'userSpaceOnUse')
        pattern.set('width', '40')
        pattern.set('height', '40')
        
        # Cores padrão se não fornecidas
        if not colors:
            colors = ["primary", "secondary", "warning", "error", "success"]
        
        # Criar dots em grid
        positions = [(10, 10), (30, 10), (10, 30), (30, 30)]
        for i, (x, y) in enumerate(positions):
            circle = ET.SubElement(pattern, 'circle')
            circle.set('cx', str(x))
            circle.set('cy', str(y))
            circle.set('r', '6')
            color_name = colors[i % len(colors)]
            circle.set('fill', self.colors.get(color_name, color_name))
            circle.set('opacity', '0.8')
        
        # Aplicar padrão a um retângulo
        rect = ET.SubElement(svg, 'rect')
        rect.set('width', str(size[0]))
        rect.set('height', str(size[1]))
        rect.set('fill', 'url(#dots-pattern)')
        
        return self._save_svg(svg, 'pattern_dots')
    
    def _generate_pattern_stars(self, size: Tuple[int, int] = (100, 100),
                               colors: Optional[List[str]] = None) -> str:
        """Gera padrão de estrelas espalhadas."""
        svg = self._create_svg_root(size[0], size[1])
        
        # Definir padrão
        defs = ET.SubElement(svg, 'defs')
        pattern = ET.SubElement(defs, 'pattern')
        pattern.set('id', 'stars-pattern')
        pattern.set('patternUnits', 'userSpaceOnUse')
        pattern.set('width', '60')
        pattern.set('height', '60')
        
        # Cores padrão
        if not colors:
            colors = ["warning", "yellow"]
        
        # Criar estrelas
        star_positions = [(15, 15), (45, 30), (30, 50)]
        for i, (x, y) in enumerate(star_positions):
            star = self._create_star_path(x, y, 8, 4)
            color_name = colors[i % len(colors)]
            star.set('fill', self.colors.get(color_name, color_name))
            pattern.append(star)
        
        # Aplicar padrão
        rect = ET.SubElement(svg, 'rect')
        rect.set('width', str(size[0]))
        rect.set('height', str(size[1]))
        rect.set('fill', 'url(#stars-pattern)')
        
        return self._save_svg(svg, 'pattern_stars')
    
    def _generate_pattern_clouds(self, size: Tuple[int, int] = (100, 100),
                                colors: Optional[List[str]] = None) -> str:
        """Gera padrão de nuvens suaves."""
        svg = self._create_svg_root(size[0], size[1])
        
        # Definir padrão
        defs = ET.SubElement(svg, 'defs')
        pattern = ET.SubElement(defs, 'pattern')
        pattern.set('id', 'clouds-pattern')
        pattern.set('patternUnits', 'userSpaceOnUse')
        pattern.set('width', '120')
        pattern.set('height', '80')
        
        # Criar nuvens com círculos sobrepostos
        cloud_color = self.colors.get(colors[0] if colors else "white", "#FFFFFF")
        
        # Nuvem 1
        cloud1 = ET.SubElement(pattern, 'g')
        cloud1.set('opacity', '0.6')
        positions = [(30, 40), (40, 35), (50, 35), (60, 40), (45, 45)]
        for x, y in positions:
            circle = ET.SubElement(cloud1, 'circle')
            circle.set('cx', str(x))
            circle.set('cy', str(y))
            circle.set('r', '12')
            circle.set('fill', cloud_color)
        
        # Nuvem 2 (menor)
        cloud2 = ET.SubElement(pattern, 'g')
        cloud2.set('opacity', '0.4')
        cloud2.set('transform', 'translate(60, 20)')
        positions2 = [(0, 0), (8, -3), (16, 0), (8, 5)]
        for x, y in positions2:
            circle = ET.SubElement(cloud2, 'circle')
            circle.set('cx', str(x))
            circle.set('cy', str(y))
            circle.set('r', '8')
            circle.set('fill', cloud_color)
        
        # Fundo azul claro
        bg = ET.SubElement(svg, 'rect')
        bg.set('width', str(size[0]))
        bg.set('height', str(size[1]))
        bg.set('fill', '#E3F2FD')
        
        # Aplicar padrão
        rect = ET.SubElement(svg, 'rect')
        rect.set('width', str(size[0]))
        rect.set('height', str(size[1]))
        rect.set('fill', 'url(#clouds-pattern)')
        
        return self._save_svg(svg, 'pattern_clouds')
    
    def _generate_pattern_school(self, size: Tuple[int, int] = (100, 100),
                                colors: Optional[List[str]] = None) -> str:
        """Gera padrão com ícones escolares."""
        svg = self._create_svg_root(size[0], size[1])
        
        # Definir padrão
        defs = ET.SubElement(svg, 'defs')
        pattern = ET.SubElement(defs, 'pattern')
        pattern.set('id', 'school-pattern')
        pattern.set('patternUnits', 'userSpaceOnUse')
        pattern.set('width', '80')
        pattern.set('height', '80')
        
        # Cores padrão
        if not colors:
            colors = ["primary", "secondary", "warning", "error"]
        
        # Lápis (20, 20)
        pencil = ET.SubElement(pattern, 'g')
        pencil.set('transform', 'translate(20, 20)')
        rect = ET.SubElement(pencil, 'rect')
        rect.set('x', '-3')
        rect.set('y', '-10')
        rect.set('width', '6')
        rect.set('height', '20')
        rect.set('fill', self.colors.get(colors[0], colors[0]))
        rect.set('rx', '1')
        
        # Livro (60, 20)
        book = ET.SubElement(pattern, 'g')
        book.set('transform', 'translate(60, 20)')
        book_rect = ET.SubElement(book, 'rect')
        book_rect.set('x', '-8')
        book_rect.set('y', '-6')
        book_rect.set('width', '16')
        book_rect.set('height', '12')
        book_rect.set('fill', self.colors.get(colors[1], colors[1]))
        book_rect.set('rx', '2')
        
        # Régua (20, 60)
        ruler = ET.SubElement(pattern, 'g')
        ruler.set('transform', 'translate(20, 60)')
        ruler_rect = ET.SubElement(ruler, 'rect')
        ruler_rect.set('x', '-15')
        ruler_rect.set('y', '-3')
        ruler_rect.set('width', '30')
        ruler_rect.set('height', '6')
        ruler_rect.set('fill', self.colors.get(colors[2], colors[2]))
        
        # ABC (60, 60)
        abc = ET.SubElement(pattern, 'text')
        abc.set('x', '60')
        abc.set('y', '65')
        abc.set('font-family', 'Arial, sans-serif')
        abc.set('font-size', '14')
        abc.set('font-weight', 'bold')
        abc.set('text-anchor', 'middle')
        abc.set('fill', self.colors.get(colors[3], colors[3]))
        abc.text = 'ABC'
        
        # Aplicar padrão
        rect = ET.SubElement(svg, 'rect')
        rect.set('width', str(size[0]))
        rect.set('height', str(size[1]))
        rect.set('fill', 'url(#school-pattern)')
        
        return self._save_svg(svg, 'pattern_school')
    
    # === IMPLEMENTAÇÃO DE ÍCONES ===
    
    def _generate_icon_camera_fun(self, size: Tuple[int, int] = (24, 24),
                                 colors: Optional[List[str]] = None) -> str:
        """Gera ícone de câmera divertida e amigável."""
        svg = self._create_svg_root(size[0], size[1])
        
        color = self.colors.get(colors[0] if colors else "primary", "#4CAF50")
        
        # Corpo da câmera
        body = ET.SubElement(svg, 'rect')
        body.set('x', '3')
        body.set('y', '8')
        body.set('width', '18')
        body.set('height', '12')
        body.set('rx', '3')
        body.set('fill', color)
        
        # Flash (topo)
        flash = ET.SubElement(svg, 'rect')
        flash.set('x', '8')
        flash.set('y', '4')
        flash.set('width', '8')
        flash.set('height', '4')
        flash.set('rx', '1')
        flash.set('fill', color)
        
        # Lente (círculo central)
        lens_outer = ET.SubElement(svg, 'circle')
        lens_outer.set('cx', '12')
        lens_outer.set('cy', '14')
        lens_outer.set('r', '4')
        lens_outer.set('fill', 'white')
        
        lens_inner = ET.SubElement(svg, 'circle')
        lens_inner.set('cx', '12')
        lens_inner.set('cy', '14')
        lens_inner.set('r', '2')
        lens_inner.set('fill', color)
        
        # Olhinhos (tornar divertido)
        eye1 = ET.SubElement(svg, 'circle')
        eye1.set('cx', '8')
        eye1.set('cy', '11')
        eye1.set('r', '1')
        eye1.set('fill', 'white')
        
        eye2 = ET.SubElement(svg, 'circle')
        eye2.set('cx', '16')
        eye2.set('cy', '11')
        eye2.set('r', '1')
        eye2.set('fill', 'white')
        
        return self._save_svg(svg, 'icon_camera_fun')
    
    def _generate_icon_microphone_fun(self, size: Tuple[int, int] = (24, 24),
                                     colors: Optional[List[str]] = None) -> str:
        """Gera ícone de microfone amigável."""
        svg = self._create_svg_root(size[0], size[1])
        
        color = self.colors.get(colors[0] if colors else "secondary", "#2196F3")
        
        # Corpo do microfone
        mic_body = ET.SubElement(svg, 'rect')
        mic_body.set('x', '9')
        mic_body.set('y', '3')
        mic_body.set('width', '6')
        mic_body.set('height', '11')
        mic_body.set('rx', '3')
        mic_body.set('fill', color)
        
        # Grade do microfone (linhas)
        for i in range(3):
            line = ET.SubElement(svg, 'line')
            line.set('x1', '10')
            line.set('x2', '14')
            y = 6 + i * 3
            line.set('y1', str(y))
            line.set('y2', str(y))
            line.set('stroke', 'white')
            line.set('stroke-width', '1')
        
        # Suporte
        arc = ET.SubElement(svg, 'path')
        arc.set('d', 'M 7 11 Q 7 16 12 16 Q 17 16 17 11')
        arc.set('fill', 'none')
        arc.set('stroke', color)
        arc.set('stroke-width', '2')
        arc.set('stroke-linecap', 'round')
        
        # Base
        base_line = ET.SubElement(svg, 'line')
        base_line.set('x1', '12')
        base_line.set('x2', '12')
        base_line.set('y1', '16')
        base_line.set('y2', '20')
        base_line.set('stroke', color)
        base_line.set('stroke-width', '2')
        
        base = ET.SubElement(svg, 'line')
        base.set('x1', '9')
        base.set('x2', '15')
        base.set('y1', '20')
        base.set('y2', '20')
        base.set('stroke', color)
        base.set('stroke-width', '2')
        base.set('stroke-linecap', 'round')
        
        # Notas musicais (tornar divertido)
        note1 = ET.SubElement(svg, 'text')
        note1.set('x', '18')
        note1.set('y', '8')
        note1.set('font-size', '8')
        note1.set('fill', color)
        note1.text = '♪'
        
        return self._save_svg(svg, 'icon_microphone_fun')
    
    def _generate_icon_history_fun(self, size: Tuple[int, int] = (24, 24),
                                  colors: Optional[List[str]] = None) -> str:
        """Gera ícone de relógio/histórico com um sorriso."""
        svg = self._create_svg_root(size[0], size[1])
        
        color = self.colors.get(colors[0] if colors else "warning", "#FFC107")
        
        # Círculo do relógio
        clock = ET.SubElement(svg, 'circle')
        clock.set('cx', '12')
        clock.set('cy', '12')
        clock.set('r', '9')
        clock.set('fill', 'none')
        clock.set('stroke', color)
        clock.set('stroke-width', '2')
        
        # Ponteiros
        hour = ET.SubElement(svg, 'line')
        hour.set('x1', '12')
        hour.set('y1', '12')
        hour.set('x2', '12')
        hour.set('y2', '7')
        hour.set('stroke', color)
        hour.set('stroke-width', '2')
        hour.set('stroke-linecap', 'round')
        
        minute = ET.SubElement(svg, 'line')
        minute.set('x1', '12')
        minute.set('y1', '12')
        minute.set('x2', '16')
        minute.set('y2', '12')
        minute.set('stroke', color)
        minute.set('stroke-width', '2')
        minute.set('stroke-linecap', 'round')
        
        # Centro
        center = ET.SubElement(svg, 'circle')
        center.set('cx', '12')
        center.set('cy', '12')
        center.set('r', '1')
        center.set('fill', color)
        
        # Olhinhos
        eye1 = ET.SubElement(svg, 'circle')
        eye1.set('cx', '9')
        eye1.set('cy', '10')
        eye1.set('r', '1')
        eye1.set('fill', color)
        
        eye2 = ET.SubElement(svg, 'circle')
        eye2.set('cx', '15')
        eye2.set('cy', '10')
        eye2.set('r', '1')
        eye2.set('fill', color)
        
        # Sorriso
        smile = ET.SubElement(svg, 'path')
        smile.set('d', 'M 8 14 Q 12 17 16 14')
        smile.set('fill', 'none')
        smile.set('stroke', color)
        smile.set('stroke-width', '1.5')
        smile.set('stroke-linecap', 'round')
        
        return self._save_svg(svg, 'icon_history_fun')
    
    def _generate_icon_achievements_fun(self, size: Tuple[int, int] = (24, 24),
                                       colors: Optional[List[str]] = None) -> str:
        """Gera ícone de troféu com estrelas."""
        svg = self._create_svg_root(size[0], size[1])
        
        color = self.colors.get(colors[0] if colors else "warning", "#FFC107")
        
        # Corpo do troféu
        trophy = ET.SubElement(svg, 'path')
        trophy.set('d', 'M 12 3 L 8 3 Q 8 8 12 10 Q 16 8 16 3 L 12 3')
        trophy.set('fill', color)
        trophy.set('stroke', color)
        trophy.set('stroke-width', '1')
        
        # Alças
        handle1 = ET.SubElement(svg, 'path')
        handle1.set('d', 'M 8 4 Q 5 4 5 7 Q 5 10 8 8')
        handle1.set('fill', 'none')
        handle1.set('stroke', color)
        handle1.set('stroke-width', '2')
        handle1.set('stroke-linecap', 'round')
        
        handle2 = ET.SubElement(svg, 'path')
        handle2.set('d', 'M 16 4 Q 19 4 19 7 Q 19 10 16 8')
        handle2.set('fill', 'none')
        handle2.set('stroke', color)
        handle2.set('stroke-width', '2')
        handle2.set('stroke-linecap', 'round')
        
        # Base
        stem = ET.SubElement(svg, 'rect')
        stem.set('x', '11')
        stem.set('y', '10')
        stem.set('width', '2')
        stem.set('height', '6')
        stem.set('fill', color)
        
        base = ET.SubElement(svg, 'rect')
        base.set('x', '8')
        base.set('y', '16')
        base.set('width', '8')
        base.set('height', '3')
        base.set('rx', '1')
        base.set('fill', color)
        
        # Estrelas decorativas
        star1 = self._create_star_path(6, 6, 3, 1.5)
        star1.set('fill', color)
        star1.set('opacity', '0.6')
        svg.append(star1)
        
        star2 = self._create_star_path(18, 6, 3, 1.5)
        star2.set('fill', color)
        star2.set('opacity', '0.6')
        svg.append(star2)
        
        # Número 1
        num = ET.SubElement(svg, 'text')
        num.set('x', '12')
        num.set('y', '8')
        num.set('font-size', '6')
        num.set('font-weight', 'bold')
        num.set('text-anchor', 'middle')
        num.set('fill', 'white')
        num.text = '1'
        
        return self._save_svg(svg, 'icon_achievements_fun')
    
    def _generate_icon_settings_fun(self, size: Tuple[int, int] = (24, 24),
                                   colors: Optional[List[str]] = None) -> str:
        """Gera ícone de engrenagem com um rosto."""
        svg = self._create_svg_root(size[0], size[1])
        
        color = self.colors.get(colors[0] if colors else "gray", "#808080")
        
        # Engrenagem usando path
        gear = ET.SubElement(svg, 'path')
        gear.set('d', '''M 12 2 L 11 6 Q 9 6 8 7 L 4 5 L 2 8 L 5 11 
                         Q 5 12 5 13 L 2 16 L 4 19 L 8 17 Q 9 18 11 18 
                         L 12 22 L 12 22 L 13 18 Q 15 18 16 17 L 20 19 
                         L 22 16 L 19 13 Q 19 12 19 11 L 22 8 L 20 5 
                         L 16 7 Q 15 6 13 6 L 12 2''')
        gear.set('fill', color)
        
        # Círculo central (face)
        center = ET.SubElement(svg, 'circle')
        center.set('cx', '12')
        center.set('cy', '12')
        center.set('r', '4')
        center.set('fill', 'white')
        
        # Olhinhos
        eye1 = ET.SubElement(svg, 'circle')
        eye1.set('cx', '10.5')
        eye1.set('cy', '11')
        eye1.set('r', '0.8')
        eye1.set('fill', color)
        
        eye2 = ET.SubElement(svg, 'circle')
        eye2.set('cx', '13.5')
        eye2.set('cy', '11')
        eye2.set('r', '0.8')
        eye2.set('fill', color)
        
        # Sorriso
        smile = ET.SubElement(svg, 'path')
        smile.set('d', 'M 10 13 Q 12 14 14 13')
        smile.set('fill', 'none')
        smile.set('stroke', color)
        smile.set('stroke-width', '0.8')
        smile.set('stroke-linecap', 'round')
        
        return self._save_svg(svg, 'icon_settings_fun')
    
    def _generate_icon_help_fun(self, size: Tuple[int, int] = (24, 24),
                               colors: Optional[List[str]] = None) -> str:
        """Gera ícone de ajuda como personagem de ponto de interrogação."""
        svg = self._create_svg_root(size[0], size[1])
        
        color = self.colors.get(colors[0] if colors else "secondary", "#2196F3")
        
        # Círculo de fundo
        bg = ET.SubElement(svg, 'circle')
        bg.set('cx', '12')
        bg.set('cy', '12')
        bg.set('r', '9')
        bg.set('fill', color)
        
        # Ponto de interrogação
        question = ET.SubElement(svg, 'text')
        question.set('x', '12')
        question.set('y', '16')
        question.set('font-size', '12')
        question.set('font-weight', 'bold')
        question.set('text-anchor', 'middle')
        question.set('fill', 'white')
        question.text = '?'
        
        # Olhinhos (fora do círculo)
        eye1 = ET.SubElement(svg, 'circle')
        eye1.set('cx', '8')
        eye1.set('cy', '8')
        eye1.set('r', '1.5')
        eye1.set('fill', color)
        
        eye2 = ET.SubElement(svg, 'circle')
        eye2.set('cx', '16')
        eye2.set('cy', '8')
        eye2.set('r', '1.5')
        eye2.set('fill', color)
        
        # Bracinhos
        arm1 = ET.SubElement(svg, 'line')
        arm1.set('x1', '4')
        arm1.set('y1', '12')
        arm1.set('x2', '7')
        arm1.set('y2', '14')
        arm1.set('stroke', color)
        arm1.set('stroke-width', '2')
        arm1.set('stroke-linecap', 'round')
        
        arm2 = ET.SubElement(svg, 'line')
        arm2.set('x1', '20')
        arm2.set('y1', '12')
        arm2.set('x2', '17')
        arm2.set('y2', '14')
        arm2.set('stroke', color)
        arm2.set('stroke-width', '2')
        arm2.set('stroke-linecap', 'round')
        
        return self._save_svg(svg, 'icon_help_fun')
    
    # === IMPLEMENTAÇÃO DE MOLDURAS ===
    
    def _generate_badge_frame(self, level: str = "bronze",
                             size: Tuple[int, int] = (100, 100),
                             colors: Optional[List[str]] = None) -> str:
        """Gera moldura de badge (bronze, silver, gold)."""
        svg = self._create_svg_root(size[0], size[1])
        
        # Cores por nível
        level_colors = {
            "bronze": "#CD7F32",
            "silver": "#C0C0C0",
            "gold": "#FFD700"
        }
        
        color = level_colors.get(level, "#CD7F32")
        
        # Criar gradiente
        defs = ET.SubElement(svg, 'defs')
        gradient = ET.SubElement(defs, 'linearGradient')
        gradient.set('id', f'{level}-gradient')
        gradient.set('x1', '0%')
        gradient.set('y1', '0%')
        gradient.set('x2', '100%')
        gradient.set('y2', '100%')
        
        stop1 = ET.SubElement(gradient, 'stop')
        stop1.set('offset', '0%')
        stop1.set('stop-color', color)
        
        stop2 = ET.SubElement(gradient, 'stop')
        stop2.set('offset', '100%')
        stop2.set('stop-color', self._darken_color(color))
        
        # Moldura externa
        outer = ET.SubElement(svg, 'circle')
        outer.set('cx', '50')
        outer.set('cy', '50')
        outer.set('r', '45')
        outer.set('fill', f'url(#{level}-gradient)')
        
        # Borda interna
        inner = ET.SubElement(svg, 'circle')
        inner.set('cx', '50')
        inner.set('cy', '50')
        inner.set('r', '38')
        inner.set('fill', 'none')
        inner.set('stroke', 'white')
        inner.set('stroke-width', '2')
        inner.set('opacity', '0.5')
        
        # Área central transparente
        center = ET.SubElement(svg, 'circle')
        center.set('cx', '50')
        center.set('cy', '50')
        center.set('r', '35')
        center.set('fill', 'white')
        center.set('opacity', '0.1')
        
        # Decorações por nível
        if level == "gold":
            # Adicionar estrelas
            for i in range(8):
                angle = i * 45
                x = 50 + 42 * math.cos(math.radians(angle))
                y = 50 + 42 * math.sin(math.radians(angle))
                star = self._create_star_path(x, y, 4, 2)
                star.set('fill', 'white')
                star.set('opacity', '0.8')
                svg.append(star)
        
        return self._save_svg(svg, f'badge_frame_{level}')
    
    # === IMPLEMENTAÇÃO DE DECORATIVOS ===
    
    def _generate_bubble_decoration(self, size: Tuple[int, int] = (100, 100),
                                   colors: Optional[List[str]] = None) -> str:
        """Gera formas de balões de fala decorativos."""
        svg = self._create_svg_root(size[0], size[1])
        
        color = self.colors.get(colors[0] if colors else "primary", "#4CAF50")
        
        # Balão principal
        bubble = ET.SubElement(svg, 'path')
        bubble.set('d', '''M 20 30 Q 20 20 30 20 L 70 20 Q 80 20 80 30 
                          L 80 50 Q 80 60 70 60 L 40 60 L 30 70 L 35 60 
                          L 30 60 Q 20 60 20 50 Z''')
        bubble.set('fill', color)
        bubble.set('opacity', '0.8')
        
        # Bolinhas decorativas
        for i in range(3):
            x = 30 + i * 20
            circle = ET.SubElement(svg, 'circle')
            circle.set('cx', str(x))
            circle.set('cy', '40')
            circle.set('r', '3')
            circle.set('fill', 'white')
        
        return self._save_svg(svg, 'bubble_decoration')
    
    def _generate_rainbow_arc(self, size: Tuple[int, int] = (100, 100),
                             colors: Optional[List[str]] = None) -> str:
        """Gera arco-íris decorativo."""
        svg = self._create_svg_root(size[0], size[1])
        
        # Cores do arco-íris
        rainbow_colors = ["#FF0000", "#FF7F00", "#FFFF00", "#00FF00", 
                         "#0000FF", "#4B0082", "#9400D3"]
        
        # Criar arcos concêntricos
        for i, color in enumerate(rainbow_colors):
            arc = ET.SubElement(svg, 'path')
            radius = 45 - i * 5
            arc.set('d', f'M 10 {50 + radius} A {radius} {radius} 0 0 1 90 {50 + radius}')
            arc.set('fill', 'none')
            arc.set('stroke', color)
            arc.set('stroke-width', '5')
            arc.set('opacity', '0.8')
        
        # Nuvens nas pontas
        cloud1 = ET.SubElement(svg, 'g')
        cloud1.set('transform', 'translate(5, 85)')
        for x, y, r in [(0, 0, 6), (6, -2, 5), (12, 0, 6), (6, 3, 4)]:
            c = ET.SubElement(cloud1, 'circle')
            c.set('cx', str(x))
            c.set('cy', str(y))
            c.set('r', str(r))
            c.set('fill', 'white')
        
        cloud2 = ET.SubElement(svg, 'g')
        cloud2.set('transform', 'translate(83, 85)')
        for x, y, r in [(0, 0, 6), (6, -2, 5), (12, 0, 6), (6, 3, 4)]:
            c = ET.SubElement(cloud2, 'circle')
            c.set('cx', str(x))
            c.set('cy', str(y))
            c.set('r', str(r))
            c.set('fill', 'white')
        
        return self._save_svg(svg, 'rainbow_arc')
    
    # === UTILIDADES ===
    
    def _create_star_path(self, cx: float, cy: float, 
                         outer_radius: float, inner_radius: float) -> ET.Element:
        """Cria um path de estrela de 5 pontas."""
        points = []
        for i in range(10):
            angle = (i * 36 - 90) * math.pi / 180
            if i % 2 == 0:
                r = outer_radius
            else:
                r = inner_radius
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)
            points.append(f"{x},{y}")
        
        path = ET.Element('polygon')
        path.set('points', ' '.join(points))
        return path
    
    def _darken_color(self, hex_color: str) -> str:
        """Escurece uma cor hex em 20%."""
        # Remover #
        hex_color = hex_color.lstrip('#')
        # Converter para RGB
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        # Escurecer
        r = int(r * 0.8)
        g = int(g * 0.8)
        b = int(b * 0.8)
        # Converter de volta
        return f"#{r:02x}{g:02x}{b:02x}"


# Teste rápido
if __name__ == "__main__":
    generator = SVGGenerator()
    
    print("Gerando SVGs de teste...")
    
    # Testar padrões
    generator.generate_svg("pattern", "dots")
    print("✓ Padrão dots gerado")
    
    # Testar ícones
    generator.generate_svg("icon", "camera_fun")
    print("✓ Ícone camera_fun gerado")
    
    # Testar moldura
    generator.generate_svg("frame", "badge_frame", custom_params={"level": "gold"})
    print("✓ Moldura gold gerada")