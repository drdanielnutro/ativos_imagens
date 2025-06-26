# test_pipeline_mascote.py
import os
import sys
from dotenv import load_dotenv

# Garante que o Python possa encontrar os módulos do projeto
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Carrega as variáveis de ambiente (REPLICATE_API_TOKEN, etc.) do arquivo .env
load_dotenv()

def run_full_test():
    """
    Executa um teste de ponta a ponta do pipeline de animação do mascote.
    """
    print("--- INICIANDO TESTE DO PIPELINE DE ANIMAÇÃO DO MASCOTE ---")

    # Importa os componentes necessários após configurar o path
    try:
        from ativos_imagens.agent import _create_mascot_animation_asset
        from ativos_imagens.tools.asset_manager import AssetManager
    except ImportError as e:
        print(f"ERRO CRÍTICO: Falha ao importar componentes do agente. Verifique a estrutura de pastas e arquivos __init__.py. Detalhes: {e}")
        return

    # 1. Configurar o AssetManager para obter as especificações do ativo
    print("\n[ETAPA 1/3] Carregando especificações do ativo...")
    manager = AssetManager()
    try:
        manager.load_asset_inventory()
        asset_id_to_test = "MAS-ANI-01"  # Testando a animação 'mascot_idle.json'
        spec = manager.get_asset_specification(asset_id_to_test)
        if not spec:
            print(f"ERRO: Especificação para o ativo '{asset_id_to_test}' não foi encontrada no inventário.")
            return
        print(f"INFO: Especificações para '{asset_id_to_test}' carregadas com sucesso.")
    except Exception as e:
        print(f"ERRO: Falha ao carregar o AssetManager ou as especificações. Detalhes: {e}")
        return
        
    # 2. Chamar a função principal de orquestração do pipeline
    print(f"\n[ETAPA 2/3] Executando o pipeline de criação para '{asset_id_to_test}'...")
    print("Este processo pode levar alguns minutos...")
    final_result = ""
    try:
        result_message = _create_mascot_animation_asset(asset_id_to_test, spec, manager)
        final_result = result_message
    except Exception as e:
        print(f"\n--- O TESTE FALHOU DURANTE A EXECUÇÃO DO PIPELINE ---")
        print(f"ERRO NÃO TRATADO: {e}")
        final_result = f"❌ Falha crítica: {e}"

    # 3. Exibir o resultado final
    print("\n[ETAPA 3/3] Resultado final do pipeline:")
    print("--------------------------------------------------")
    print(final_result)
    print("--------------------------------------------------")

    if "✅" in final_result:
        print("\n🎉 VEREDITO: TESTE CONCLUÍDO COM SUCESSO! 🎉")
    else:
        print("\n🔥 VEREDITO: TESTE FALHOU. Revise os logs de erro acima. 🔥")


if __name__ == "__main__":
    run_full_test() 