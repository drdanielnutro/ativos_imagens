# Plano Detalhado de Modificações - Pipeline Lottie

## ETAPA 1: CORRIGIR O PROCESSO DE VETORIZAÇÃO

### 1.1 Instalar python-lottie
```bash
pip install lottie
```

### 1.2 Modificar arquivo: `ativos_imagens/tools/mascot_animator.py`

#### Modificação 1: Importar subprocess para usar lottie_convert.py
**Localização**: No topo do arquivo, após os imports existentes
**Adicionar**:
```python
import subprocess
```

#### Modificação 2: Substituir o método _vectorize_frames
**Localização**: Linhas 175-206 (método `_vectorize_frames`)
**Remover todo o método atual** que usa:
```python
def _vectorize_frames(self, frames_dir: str, svg_dir: str, frame_count: int):
    # ... código atual com mkbitmap e potrace ...
```

**Substituir por**:
```python
def _vectorize_frames(self, frames_dir: str, svg_dir: str, frame_count: int):
    """Etapa 4: Vetoriza cada frame usando lottie_convert.py com Potrace."""
    print("INFO (MascotAnimator): Etapa 4 - Vetorizando frames para SVG...")
    
    for i in range(frame_count):
        png_path = os.path.join(frames_dir, f"frame_{i:04d}.png")
        svg_path = os.path.join(svg_dir, f"frame_{i:04d}.svg")
        
        if not os.path.exists(png_path):
            print(f"AVISO: Frame {i} não encontrado em {png_path}")
            continue
            
        try:
            # Usar lottie_convert.py com modo trace (Potrace)
            cmd = [
                "lottie_convert.py",
                "--bmp-mode", "trace",
                png_path,
                svg_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Erro ao vetorizar frame {i}: {result.stderr}")
            else:
                print(f"Frame {i} vetorizado com sucesso")
                
        except Exception as e:
            print(f"Erro ao processar frame {i}: {e}")
            
    print("INFO (MascotAnimator): Vetorização de todos os frames concluída.")
```

## ETAPA 2: ADICIONAR FUNDO AZUL AOS PROMPTS DE VÍDEO

### 2.1 Modificar arquivo: `ativos_imagens/tools/mascot_animator.py`

#### Modificação 3: Atualizar o método _generate_video_from_image
**Localização**: Linha 112-142 (dentro do método `_generate_video_from_image`)
**Modificar**: A linha onde o prompt é passado para o modelo

**Linha atual** (aproximadamente linha 134):
```python
"prompt": animation_prompt,
```

**Modificar para**:
```python
"prompt": f"{animation_prompt}, solid blue background color #0047bb",
```

### 2.2 Modificar arquivo: `ativos_imagens/asset_configs/mascot_animations.json`

#### Modificação 4: Atualizar TODOS os prompts de animação
**Localização**: Todo o arquivo
**Para cada prompt de animação, adicionar**: ", solid blue background color #0047bb"

**Exemplo de modificação**:
```json
// ANTES:
"animation_prompt": "subtle breathing motion, seamless loop, character is mostly still"

// DEPOIS:
"animation_prompt": "subtle breathing motion, seamless loop, character is mostly still, solid blue background color #0047bb"
```

**Lista completa de prompts a modificar**:
1. mascot_idle: "subtle breathing motion, seamless loop, character is mostly still, solid blue background color #0047bb"
2. mascot_bounce: "bouncing motion with squash and stretch, cartoon style, solid blue background color #0047bb"
3. mascot_wave: "waving hand gesture, friendly greeting, smooth motion, solid blue background color #0047bb"
4. mascot_thinking: "thinking pose with hand on chin, slight head movement, solid blue background color #0047bb"
5. mascot_celebration: "jumping celebration, excited movement, confetti effect, solid blue background color #0047bb"

## ETAPA 3: ADICIONAR OTIMIZAÇÃO COM SVGO

### 3.1 Instalar SVGO
```bash
npm install -g svgo
```

### 3.2 Modificar arquivo: `ativos_imagens/tools/mascot_animator.py`

#### Modificação 5: Adicionar otimização SVGO após vetorização
**Localização**: Dentro do método `_vectorize_frames`, após gerar cada SVG
**Adicionar após a linha** `print(f"Frame {i} vetorizado com sucesso")`:

```python
                # Otimizar SVG com SVGO
                try:
                    svgo_cmd = [
                        "svgo",
                        svg_path,
                        "-o", svg_path,
                        "--config", '{"plugins":[{"name":"preset-default","params":{"overrides":{"removeViewBox":false}}}]}'
                    ]
                    
                    svgo_result = subprocess.run(svgo_cmd, capture_output=True, text=True)
                    
                    if svgo_result.returncode == 0:
                        print(f"Frame {i} otimizado com SVGO")
                    else:
                        print(f"Aviso: Não foi possível otimizar frame {i} com SVGO")
                        
                except Exception as e:
                    print(f"SVGO não disponível ou erro: {e}")
```

## ETAPA 4: ADICIONAR OTIMIZAÇÃO DO JSON

### 4.1 Modificar arquivo: `ativos_imagens/tools/mascot_animator.py`

#### Modificação 6: Adicionar método de otimização JSON
**Localização**: Após o método `_compile_lottie` (aproximadamente linha 232)
**Adicionar novo método**:

```python
def _optimize_json(self, json_path: str) -> str:
    """Otimiza o arquivo JSON Lottie usando python-lottie."""
    print("INFO (MascotAnimator): Otimizando JSON com python-lottie...")
    
    optimized_path = json_path.replace('.json', '_optimized.json')
    
    try:
        cmd = [
            "lottie_convert.py",
            json_path,
            optimized_path,
            "--optimize", "2"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Substituir arquivo original pelo otimizado
            os.replace(optimized_path, json_path)
            print("JSON otimizado com sucesso")
            return json_path
        else:
            print(f"Erro ao otimizar JSON: {result.stderr}")
            return json_path
            
    except Exception as e:
        print(f"Erro na otimização: {e}")
        return json_path
```

#### Modificação 7: Chamar otimização após salvar JSON
**Localização**: No método `create_mascot_animation`, após a linha 268
**Após a linha**:
```python
exporters.export_lottie(animation, output_path)
```

**Adicionar**:
```python
                # Otimizar o JSON gerado
                self._optimize_json(output_path)
```

## ETAPA 5: ADICIONAR CONVERSÃO PARA FORMATO DOTLOTTIE

### 5.1 Modificar arquivo: `ativos_imagens/tools/mascot_animator.py`

#### Modificação 8: Importar módulos necessários
**Localização**: No topo do arquivo, após os imports existentes
**Adicionar**:
```python
import zipfile
import json
```

#### Modificação 9: Adicionar método para criar .lottie
**Localização**: Após o método `_optimize_json`
**Adicionar novo método**:

```python
def _create_dotlottie(self, json_path: str) -> str:
    """Converte JSON para formato .lottie (ZIP comprimido)."""
    print("INFO (MascotAnimator): Convertendo para formato .lottie...")
    
    lottie_path = json_path.replace('.json', '.lottie')
    
    try:
        # Ler o JSON
        with open(json_path, 'r') as f:
            animation_data = f.read()
        
        # Criar arquivo .lottie (ZIP)
        with zipfile.ZipFile(lottie_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Criar manifest
            manifest = {
                "animations": [{
                    "id": "animation",
                    "path": "animations/animation.json"
                }],
                "author": "MascotAnimator",
                "version": "1.0",
                "generator": "ativos_imagens"
            }
            
            # Adicionar manifest
            zf.writestr('manifest.json', json.dumps(manifest, indent=2))
            
            # Adicionar animação
            zf.writestr('animations/animation.json', animation_data)
        
        # Verificar tamanho
        original_size = os.path.getsize(json_path) / 1024  # KB
        compressed_size = os.path.getsize(lottie_path) / 1024  # KB
        reduction = ((original_size - compressed_size) / original_size) * 100
        
        print(f"Arquivo .lottie criado: {lottie_path}")
        print(f"Tamanho original: {original_size:.1f} KB")
        print(f"Tamanho comprimido: {compressed_size:.1f} KB")
        print(f"Redução: {reduction:.1f}%")
        
        return lottie_path
        
    except Exception as e:
        print(f"Erro ao criar .lottie: {e}")
        return json_path
```

#### Modificação 10: Adicionar parâmetro para escolher formato de saída
**Localização**: Método `create_mascot_animation`, linha 234
**Modificar assinatura do método**:

**De**:
```python
def create_mascot_animation(self, prompt_details: dict, animation_prompt: str, output_path: str) -> str:
```

**Para**:
```python
def create_mascot_animation(self, prompt_details: dict, animation_prompt: str, output_path: str, output_format: str = "lottie") -> str:
```

#### Modificação 11: Adicionar conversão para .lottie ao final
**Localização**: No método `create_mascot_animation`, após otimizar JSON
**Após as linhas de otimização**, adicionar:

```python
                # Converter para formato .lottie se solicitado
                if output_format == "lottie":
                    final_path = self._create_dotlottie(output_path)
                    # Remover JSON original se conversão foi bem-sucedida
                    if final_path.endswith('.lottie'):
                        os.remove(output_path)
                    return final_path
                
                return output_path
```

## ETAPA 6: ATUALIZAR O AGENTE PARA USAR AS NOVAS FUNCIONALIDADES

### 6.1 Modificar arquivo: `ativos_imagens/agent.py`

#### Modificação 12: Atualizar a chamada para create_mascot_animation
**Localização**: No método `create_mascot_animation_tool`, aproximadamente linha 213
**Modificar a chamada**:

**De**:
```python
result = self.mascot_animator.create_mascot_animation(
    prompt_details=prompt_details,
    animation_prompt=specs['animation_prompt'],
    output_path=output_path
)
```

**Para**:
```python
result = self.mascot_animator.create_mascot_animation(
    prompt_details=prompt_details,
    animation_prompt=specs['animation_prompt'],
    output_path=output_path,
    output_format="lottie"  # Usar formato .lottie por padrão
)
```

## RESUMO DAS MODIFICAÇÕES

1. **mascot_animator.py**:
   - Importar subprocess, zipfile, json
   - Substituir _vectorize_frames para usar lottie_convert.py
   - Adicionar fundo azul aos prompts de vídeo
   - Adicionar otimização SVGO após vetorização
   - Adicionar método _optimize_json
   - Adicionar método _create_dotlottie
   - Modificar create_mascot_animation para suportar formato .lottie

2. **mascot_animations.json**:
   - Adicionar ", solid blue background color #0047bb" a todos os prompts

3. **agent.py**:
   - Atualizar chamada para usar formato .lottie

## COMANDOS DE INSTALAÇÃO NECESSÁRIOS

```bash
# Instalar python-lottie
pip install lottie

# Instalar SVGO globalmente
npm install -g svgo
```

## RESULTADO ESPERADO

- Arquivo atual: 4.8MB (.json)
- Arquivo final: <100KB (.lottie)
- Redução total esperada: >95%