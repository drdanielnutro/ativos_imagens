"""
SVG Generator - Gerador de arquivos SVG usando API Recraft
"""
import os
import requests
import replicate
from typing import Optional
from pathlib import Path


class SVGGenerator:
    """
    Ferramenta para gerar SVGs usando a API Recraft-20b-svg via Replicate.
    """
    
    def __init__(self, output_dir: str = "ativos_imagens/output/svg"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Modelo Recraft para geração de SVG
        self.model_id = "recraft-ai/recraft-20b-svg"
        
    def generate_svg(self, prompt: str, size: str = "1024x1024", 
                    aspect_ratio: str = "1:1", **kwargs) -> str:
        """
        Gera um SVG usando a API Recraft via Replicate.
        
        Args:
            prompt: Descrição do SVG a ser gerado
            size: Tamanho da imagem (default: "1024x1024")
            aspect_ratio: Proporção da imagem (default: "1:1")
            **kwargs: Parâmetros adicionais ignorados para compatibilidade
            
        Returns:
            Caminho do arquivo SVG salvo
            
        Raises:
            Exception: Se a geração falhar
        """
        # Parâmetros da API conforme o exemplo fornecido
        api_input = {
            "prompt": prompt,
            "size": size,
            "style": "icon",  # Fixo para garantir fundo transparente
            "aspect_ratio": aspect_ratio
        }
        
        try:
            print(f"INFO: Gerando SVG com prompt: '{prompt[:100]}...'")
            print(f"INFO: Usando modelo: {self.model_id}")
            print(f"INFO: Parâmetros: size={size}, aspect_ratio={aspect_ratio}")
            
            # Chamar a API do Replicate
            result = replicate.run(self.model_id, input=api_input)
            
            # Extrair URL do resultado
            if isinstance(result, list) and len(result) > 0:
                svg_url = result[0]
            elif isinstance(result, str):
                svg_url = result
            elif hasattr(result, 'url'):
                svg_url = result.url
            else:
                svg_url = str(result)
            
            print(f"INFO: SVG gerado com sucesso. URL: {svg_url}")
            
            # Download do SVG
            response = requests.get(svg_url)
            response.raise_for_status()
            
            # Gerar nome do arquivo baseado no prompt
            filename = self._generate_filename_from_prompt(prompt)
            filepath = os.path.join(self.output_dir, filename)
            
            # Salvar o arquivo
            with open(filepath, 'wb') as f:
                f.write(response.content)
                
            print(f"SUCESSO: SVG salvo em {filepath}")
            return filepath
            
        except Exception as e:
            print(f"ERRO: Falha ao gerar SVG via API Recraft: {e}")
            raise
    
    def _generate_filename_from_prompt(self, prompt: str) -> str:
        """
        Gera um nome de arquivo baseado no prompt.
        
        Args:
            prompt: O prompt usado para gerar o SVG
            
        Returns:
            Nome do arquivo com extensão .svg
        """
        # Extrair palavras-chave do prompt
        keywords = prompt.lower().split()[:5]  # Primeiras 5 palavras
        
        # Filtrar palavras comuns
        stopwords = {'a', 'an', 'the', 'of', 'for', 'and', 'or', 'in', 'on', 'at', 'to', 'with'}
        keywords = [w for w in keywords if w not in stopwords and len(w) > 2]
        
        # Criar nome base
        if keywords:
            base_name = '_'.join(keywords[:3])  # Usar até 3 palavras-chave
        else:
            base_name = 'svg_output'
            
        # Remover caracteres especiais
        base_name = ''.join(c if c.isalnum() or c == '_' else '_' for c in base_name)
        
        # Adicionar sufixo único se necessário
        filepath = os.path.join(self.output_dir, f"{base_name}.svg")
        counter = 1
        while os.path.exists(filepath):
            filepath = os.path.join(self.output_dir, f"{base_name}_{counter}.svg")
            counter += 1
            
        return os.path.basename(filepath)


# Teste rápido
if __name__ == "__main__":
    generator = SVGGenerator()
    
    print("Testando geração de SVG via API Recraft...")
    
    try:
        # Testar com um ícone simples
        result = generator.generate_svg(
            prompt="Icon of a camera for a educational kids educational app. Vectorized, cartoon, 3d, colorized.",
            size="1024x1024",
            aspect_ratio="1:1"
        )
        print(f"✓ SVG gerado com sucesso: {result}")
    except Exception as e:
        print(f"✗ Erro no teste: {e}")