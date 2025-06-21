## Do Zero à Orquestração: O Guia Definitivo para Criar Agentes com Google ADK

Bem-vindo ao guia completo para o Google Agent Development Kit (ADK). A criação de agentes de IA, capazes de raciocinar e usar ferramentas, pode parecer uma tarefa complexa. Este tutorial foi desenhado para desmistificar o processo, te guiando por um caminho prático e passo a passo.

Nossa jornada será dividida em duas partes:

*   **Parte 1:** Construiremos nosso primeiro agente funcional em menos de 5 minutos. Uma vitória rápida para entender os conceitos fundamentais.
*   **Parte 2:** Evoluiremos nosso conhecimento para criar um sistema multi-agente, onde um agente "coordenador" orquestra outros agentes "especialistas" para resolver problemas mais complexos.

Vamos começar.

### **Parte 1: Seu Primeiro Agente em 5 Minutos (O Agente do Tempo)**

**Objetivo:** Criar um agente extremamente simples que sabe informar a hora e a data atuais.

#### **Pré-requisitos**

1.  **Python 3.9+** instalado em sua máquina.
2.  **Chave de API do Google:** Obtenha uma chave gratuitamente no [Google AI Studio](https://aistudio.google.com/app/apikey).

#### **Passo 1: Configuração do Ambiente**

Abra seu terminal (ou Prompt de Comando/PowerShell no Windows) e instale o pacote do Google ADK com o seguinte comando:

```bash
pip install google-adk
```

#### **Passo 2: Estrutura do Projeto**

O ADK funciona melhor quando os agentes são organizados como módulos Python. Crie a seguinte estrutura de pastas e arquivos:

```
meu_primeiro_projeto/
├── .env
└── agente_tempo/
    ├── __init__.py
    └── agent.py
```

*   `meu_primeiro_projeto/`: A pasta raiz do nosso projeto.
*   `.env`: Arquivo para armazenar nossa chave de API de forma segura.
*   `agente_tempo/`: O módulo Python para nosso agente.
*   `__init__.py`: Um arquivo vazio que informa ao Python que `agente_tempo` é um pacote.
*   `agent.py`: Onde a lógica do nosso agente será escrita.

#### **Passo 3: O Código**

Abra os arquivos em seu editor de código preferido e adicione o seguinte conteúdo.

**Arquivo: `.env`**
Substitua `SUA_CHAVE_API_AQUI` pela chave que você obteve no Google AI Studio.

```
# Informa ao ADK para usar a chave de API padrão em vez do Vertex AI
GOOGLE_GENAI_USE_VERTEXAI=False
GOOGLE_API_KEY=SUA_CHAVE_API_AQUI
```

**Arquivo: `agente_tempo/agent.py`**
Este é o coração do nosso agente. Copie e cole o código abaixo. Os comentários explicam cada linha.

```python
# Importa as classes necessárias do ADK e a biblioteca padrão do Python
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
import datetime

# --- Definição da Ferramenta ---
# Esta é uma função Python padrão. As anotações de tipo e a docstring
# são muito importantes, pois o ADK as usa para que o LLM entenda
# o que a ferramenta faz e como usá-la.
def get_current_time() -> str:
  """Use esta ferramenta para obter a data e a hora atuais.
  Não aceita nenhum argumento.
  """
  # Obtém a data e hora atuais e formata para uma string legível.
  now = datetime.datetime.now()
  return now.strftime("%d de %B de %Y, %H:%M:%S")

# --- Definição do Agente ---
# Por convenção, o agente principal de um módulo deve ser nomeado 'root_agent'.
# É este agente que o ADK procurará e executará.
root_agent = LlmAgent(
    # O "cérebro" do nosso agente. Usamos um modelo rápido e eficiente do Google.
    model="gemini-1.5-flash-latest",

    # A instrução (instruction) inicial que define a personalidade e o objetivo do agente.
    instruction="Você é um assistente prestativo. Sua especialidade é saber a data e a hora. Use suas ferramentas para responder.",

    # A lista de ferramentas que este agente tem permissão para usar.
    # Usamos a classe FunctionTool para registrar nossa função Python como uma ferramenta.
    tools=[
        FunctionTool(get_current_time)
    ]
)
```

#### **Passo 4: Executando e Testando**

1.  Abra seu terminal e navegue para a pasta raiz do projeto (`meu_primeiro_projeto/`).

2.  Execute o servidor web de desenvolvimento do ADK com o comando:

    ```bash
    adk web
    ```

3.  Seu terminal mostrará uma mensagem indicando que o servidor está rodando, geralmente em `http://127.0.0.1:8000`. Abra este endereço no seu navegador.

4.  Na interface web, no canto superior esquerdo, selecione `agente_tempo`.

5.  Você verá uma interface de chat. Teste seu agente com perguntas como:

    *   `Que horas são agora?`
    *   `Poderia me informar a data de hoje?`
    *   `Qual a data e hora?`

Você verá o agente entender seu pedido, decidir usar a ferramenta `get_current_time`, executá-la e formular uma resposta completa.

**Parabéns!** Você acabou de construir e interagir com seu primeiro agente de IA. Agora, vamos usar essa base para construir algo muito mais poderoso.

-----

### **Parte 2: A Evolução para um Sistema Multi-Agente (A Agência de Viagens)**

**Objetivo:** Construir um sistema onde um agente "Coordenador" recebe um pedido complexo de viagem e delega as tarefas para dois agentes "Especialistas": um para encontrar voos e outro para sugerir atividades.

#### **Conceitos-Chave (A Teoria Correta e Auditada)**

1.  **Padrão Orquestrador-Especialista:** Este é um design comum e poderoso. O Orquestrador é um `LlmAgent` que atua como um "gerente de projetos". Ele não executa tarefas finais, mas entende o problema e sabe qual especialista chamar.
2.  **`AgentTool`:** Esta é a forma **correta** de fazer um `LlmAgent` orquestrar outro. Envolvemos um agente especialista (como o de voos) dentro de um `AgentTool`. Para o agente orquestrador, esse outro agente se parece e se comporta exatamente como uma ferramenta comum (como a nossa `get_current_time` anterior).

#### **Passo 1: Estrutura do Projeto Multi-Agente**

Crie uma nova pasta para este projeto, chamada `agencia_viagens`. Dentro dela, crie os seguintes arquivos. Note que não precisamos de subpastas aqui, pois os agentes se importarão diretamente.

```
agencia_viagens/
├── .env
├── flight_finder_agent.py
├── activity_finder_agent.py
└── coordinator_agent.py
```

Lembre-se de criar o arquivo `.env` nesta pasta também, com sua chave de API.

#### **Passo 2: Criando os Agentes Especialistas**

Primeiro, vamos criar os dois agentes especialistas.

**Arquivo: `flight_finder_agent.py`**

```python
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

def find_flights(destination: str) -> str:
  """Use esta ferramenta para encontrar voos para um destino específico."""
  # Em um cenário real, aqui haveria uma chamada para uma API de voos.
  print(f"--- AGENTE DE VOOS: Buscando voos para {destination} ---")
  return f"Encontrei 3 voos para {destination} a partir de R$1.500,00."

# Este é o agente especialista em voos.
root_agent = LlmAgent(
    name="flight_agent",
    description="Um agente especialista em encontrar voos. Recebe um destino e retorna informações sobre voos.",
    model="gemini-1.5-flash-latest",
    tools=[FunctionTool(find_flights)],
    instruction="Sua única função é encontrar voos usando a ferramenta 'find_flights'."
)
```

**Arquivo: `activity_finder_agent.py`**

```python
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

def find_activities(destination: str) -> str:
  """Use esta ferramenta para encontrar atividades e passeios em um destino."""
  # Em um cenário real, aqui haveria uma chamada para uma API de turismo.
  print(f"--- AGENTE DE ATIVIDADES: Buscando atividades em {destination} ---")
  return f"As melhores atividades em {destination} são: visita ao museu, tour gastronômico e caminhada no parque."

# Este é o agente especialista em atividades.
root_agent = LlmAgent(
    name="activity_agent",
    description="Um agente especialista em encontrar atividades turísticas. Recebe um destino e retorna uma lista de sugestões.",
    model="gemini-1.5-flash-latest",
    tools=[FunctionTool(find_activities)],
    instruction="Sua única função é encontrar atividades turísticas usando a ferramenta 'find_activities'."
)
```

#### **Passo 3: Criando o Agente Orquestrador**

Agora, a peça central. O coordenador não terá ferramentas que executam tarefas finais. Suas "ferramentas" serão os outros dois agentes.

**Arquivo: `coordinator_agent.py`**

```python
from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool

# 1. Importa os 'root_agent' de cada módulo especialista.
#    Renomeamos para maior clareza.
from flight_finder_agent import root_agent as flight_agent
from activity_finder_agent import root_agent as activity_agent

# 2. Define o agente Coordenador/Orquestrador.
root_agent = LlmAgent(
    model="gemini-1.5-flash-latest",

    # 3. A instrução é crucial: ela ensina o coordenador a delegar.
    instruction="""Você é um coordenador de viagens mestre.
    Sua tarefa é entender o pedido completo do usuário e delegar para os agentes especialistas corretos para obter as informações.
    - Para qualquer coisa relacionada a voos, use o 'flight_agent'.
    - Para qualquer coisa relacionada a passeios e atividades, use o 'activity_agent'.
    Após obter as respostas dos especialistas, sintetize tudo em uma resposta única, amigável e completa para o usuário.""",

    # 4. AQUI ESTÁ A MÁGICA (E O CÓDIGO CORRETO):
    #    Envolvemos cada agente especialista em um 'AgentTool'.
    #    O ADK usa as propriedades 'name' e 'description' de cada agente
    #    para apresentar estas "ferramentas" ao coordenador.
    tools=[
        AgentTool(flight_agent),
        AgentTool(activity_agent)
    ]
)
```

#### **Passo 4: Executando o Sistema Multi-Agente**

1.  No seu terminal, navegue para dentro da pasta `agencia_viagens`.
2.  Execute o ADK, mas desta vez, aponte especificamente para o seu agente orquestrador:
    ```bash
    adk web coordinator_agent.py
    ```
3.  Abra a interface de chat no seu navegador e teste com um pedido complexo:
    *   `Olá! Quero planejar uma viagem para o Rio de Janeiro. Pode ver os voos e me dizer o que tem pra fazer lá?`

Observe o seu terminal! Você verá os `print` dos agentes especialistas sendo ativados um após o outro, conforme o coordenador os chama. No final, a interface de chat mostrará uma resposta única e coesa, sintetizada pelo coordenador.

### **Conclusão**

Você fez uma jornada incrível: começou com um agente que apenas dizia as horas e terminou com um sistema multi-agente funcional, capaz de delegar e orquestrar tarefas complexas. Você aprendeu os fundamentos do ADK, a importância da definição de ferramentas, e o padrão correto e auditado (`AgentTool`) para criar sistemas de múltiplos agentes.

O poder do Google ADK está nesta modularidade. Agora você pode adicionar mais especialistas (um para hotéis, outro para restaurantes) e tornar sua agência de viagens ainda mais inteligente. O céu é o limite.

Parabéns e bons projetos