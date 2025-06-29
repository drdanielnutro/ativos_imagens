#!/usr/bin/env python3
"""
Script de teste para o sistema multi-agente
Execute após instalar o Google ADK
"""

import sys
import os

def test_imports():
    """Testa se todos os módulos podem ser importados"""
    print("🔍 Testando imports do sistema multi-agente...\n")
    
    tests = []
    
    # Teste 1: Importar orchestrator
    try:
        from ativos_imagens import orchestrator
        tests.append(("✅", "Orchestrator importado com sucesso"))
    except ImportError as e:
        tests.append(("❌", f"Erro ao importar orchestrator: {e}"))
    
    # Teste 2: Verificar agentes
    try:
        from ativos_imagens.agents import asset_validator_agent, asset_creator_agent
        tests.append(("✅", "Agentes especializados importados"))
    except ImportError as e:
        tests.append(("❌", f"Erro ao importar agentes: {e}"))
    
    # Teste 3: Verificar root_agent
    try:
        from ativos_imagens.orchestrator import root_agent
        if root_agent:
            tests.append(("✅", f"Root agent criado: {root_agent.name}"))
        else:
            tests.append(("❌", "Root agent é None"))
    except Exception as e:
        tests.append(("❌", f"Erro ao acessar root_agent: {e}"))
    
    # Teste 4: Verificar ferramentas do orchestrator
    try:
        from ativos_imagens.orchestrator import root_agent
        if hasattr(root_agent, 'tools'):
            tool_names = [tool.__class__.__name__ for tool in root_agent.tools]
            tests.append(("✅", f"Ferramentas: {', '.join(tool_names)}"))
        else:
            tests.append(("⚠️", "Root agent sem ferramentas"))
    except Exception as e:
        tests.append(("❌", f"Erro ao verificar ferramentas: {e}"))
    
    # Exibir resultados
    print("📊 Resultados dos Testes:\n")
    for status, message in tests:
        print(f"{status} {message}")
    
    # Resumo
    success = sum(1 for s, _ in tests if s == "✅")
    total = len(tests)
    print(f"\n📈 Resumo: {success}/{total} testes passaram")
    
    if success == total:
        print("\n🎉 Sistema multi-agente está pronto para uso!")
        print("\n💡 Próximo passo: Execute 'adk web' para iniciar o servidor")
    else:
        print("\n⚠️ Alguns testes falharam. Verifique:")
        print("1. Google ADK está instalado? (pip install google-adk)")
        print("2. Está no ambiente virtual correto?")
        print("3. As dependências estão instaladas? (pip install -r requirements.txt)")


if __name__ == "__main__":
    # Adicionar diretório atual ao path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    print("🚀 Teste do Sistema Multi-Agente de Produção de Ativos\n")
    print(f"📁 Diretório: {current_dir}")
    print(f"🐍 Python: {sys.version.split()[0]}\n")
    
    test_imports()