# **Construindo seu Primeiro Sistema Multiagente com o Google ADK: Um Tutorial Prático e Rápido**

## **Introdução: De Agentes Monolíticos a Sistemas Colaborativos**

A evolução das aplicações de inteligência artificial está se afastando de agentes únicos e monolíticos em direção a sistemas multiagentes (MAS \- Multi-Agent Systems). Aplicações complexas rapidamente revelam as limitações de um único agente encarregado de todas as tarefas; a manutenção se torna difícil, a escalabilidade é um desafio e a especialização é quase impossível. A solução para essa complexidade reside no paradigma multiagente: a criação de "equipes" de agentes de IA especializados que colaboram para atingir um objetivo maior. Essa abordagem modular oferece vantagens significativas, incluindo especialização aprimorada, reutilização de componentes, manutenibilidade simplificada e a capacidade de definir fluxos de controle estruturados. No contexto empresarial, os sistemas multiagentes são vistos como uma futura necessidade, permitindo que múltiplos agentes de IA, mesmo que construídos em diferentes frameworks, trabalhem juntos para automatizar fluxos de trabalho completos.  
Nesse cenário, o Agent Development Kit (ADK) do Google surge como um framework de código aberto, projetado especificamente para essa nova era de desenvolvimento de IA. O ADK foi concebido com uma filosofia "Multiagente por Design", fornecendo aos desenvolvedores as ferramentas para construir aplicações modulares e escaláveis, compondo múltiplos agentes especializados em uma hierarquia. Ele é agnóstico em relação ao modelo, permitindo o uso de modelos Gemini, bem como modelos da Anthropic, Meta e outros através da integração com LiteLLM. Além disso, oferece flexibilidade de implantação, desde a execução local até o escalonamento em ambientes de produção como o Vertex AI Agent Engine.  
No entanto, uma análise dos materiais de aprendizagem disponíveis revela uma lacuna de simplicidade. Tutoriais oficiais, como o do "Agente de Renovação", embora poderosos, introduzem rapidamente a complexidade de serviços em nuvem como Google Cloud Storage, Cloud Run e AlloyDB, criando uma barreira de entrada para desenvolvedores que buscam uma experiência de implementação em "poucos minutos". Por outro lado, a própria ferramenta ADK, com seu servidor web local (adk web) e gerenciamento de sessão em memória (InMemorySessionService), foi projetada para uma experiência de desenvolvimento local rápida e eficiente. Este relatório tem como missão preencher essa lacuna. Em vez de replicar tutoriais complexos baseados em nuvem, construiremos um tutorial multiagente local, rápido e replicável, que atenda diretamente à necessidade de uma porta de entrada acessível, antes de indicar caminhos para arquiteturas mais complexas.  
\<br\>  
**Tabela 1: Comparação de Arquitetura de Agente Único vs. Multiagente**

| Característica                      | Arquitetura de Agente Único (Monolítica)                                                                  | Arquitetura Multiagente (Modular)                                                                                                                     |
| :---------------------------------- | :-------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Modularidade**                    | Baixa. A lógica é centralizada em um único agente, dificultando a separação de responsabilidades.         | Alta. Cada agente é um componente especializado, facilitando o desenvolvimento e a manutenção independentes.                                          |
| **Escalabilidade**                  | Limitada. Escalar o sistema inteiro para uma única tarefa de alto custo é ineficiente.                    | Alta. Agentes individuais podem ser escalados conforme a necessidade. Modelos diferentes podem ser usados para tarefas diferentes (custo/desempenho). |
| **Manutenibilidade**                | Complexa. Mudar uma parte da lógica pode ter efeitos colaterais inesperados em todo o sistema.            | Simplificada. Agentes podem ser atualizados ou substituídos individualmente sem impactar o sistema inteiro.                                           |
| **Complexidade de Desenvolvimento** | Baixa inicialmente, mas aumenta exponencialmente com a adição de novas funcionalidades.                   | Maior inicialmente (requer orquestração), mas mais gerenciável a longo prazo à medida que o sistema cresce.                                           |
| **Isolamento de Falhas**            | Baixo. Uma falha em uma ferramenta ou lógica pode derrubar todo o agente.                                 | Alto. A falha de um subagente pode ser contida e gerenciada pelo agente orquestrador, aumentando a robustez.                                          |
| **Reutilização**                    | Limitada. A lógica está fortemente acoplada, dificultando a extração de componentes para outros projetos. | Alta. Agentes especializados (ex: um agente de pesquisa na web) podem ser facilmente reutilizados em diferentes sistemas.                             |

\<br\>

## **Parte 1: A Habilidade Fundamental \- Um Agente Único em Menos de 5 Minutos**

Antes de construir uma equipe de agentes, é essencial dominar a criação de um único agente. Esta seção fornece um tutorial completo e autossuficiente para criar um agente funcional localmente. O objetivo é criar confiança e estabelecer uma compreensão sólida do ciclo de desenvolvimento do ADK.

### **Configuração do Ambiente**

O processo de configuração é direto e segue as melhores práticas para o desenvolvimento em Python.

1. **Crie um Ambiente Virtual:** No seu terminal, navegue até a pasta do seu projeto e crie um ambiente virtual. Isso isola as dependências do seu projeto.  
   `python -m venv.venv`

2. **Ative o Ambiente Virtual:**  
   * No macOS/Linux:  
     `source.venv/bin/activate`

   * No Windows (CMD):

.venv\\Scripts\\activate.bat \`\`\`

3. **Instale o ADK:** Com o ambiente ativado, instale o pacote google-adk usando pip.  
   `pip install google-adk`

### **Estrutura do Projeto**

O ADK espera uma estrutura de pastas específica para descobrir e executar seus agentes.

1. **Crie as Pastas e Arquivos:** Use os seguintes comandos para criar a estrutura necessária.  
   `mkdir time_agent/`  
   `touch time_agent/__init__.py time_agent/agent.py.env`

2. Sua estrutura de projeto deve ser a seguinte:  
   `seu_projeto/`  
   `├──.venv/`  
   `├── time_agent/`  
   `│   ├── __init__.py`  
   `│   └── agent.py`  
   `└──.env`

### **Configuração (.env)**

O arquivo .env armazena as configurações e chaves de API do seu agente. Para este tutorial rápido, a maneira mais simples é usar uma chave de API do Gemini gerada gratuitamente no Google AI Studio.

* No arquivo .env, adicione as seguintes linhas, substituindo SUA\_CHAVE\_API\_AQUI pela sua chave.  
  `# Para usar uma chave de API do Gemini do Google AI Studio`  
  `GOOGLE_GENAI_USE_VERTEXAI=FALSE`  
  `GOOGLE_API_KEY=SUA_CHAVE_API_AQUI`

* **Alternativa (Vertex AI):** Se você já estiver no ecossistema do Google Cloud, pode usar as credenciais do Vertex AI. Nesse caso, seu arquivo .env seria :  
  `# Para usar o Gemini via Vertex AI no Google Cloud`  
  `GOOGLE_CLOUD_PROJECT="seu-id-de-projeto"`  
  `GOOGLE_CLOUD_LOCATION="sua-regiao" # ex: us-central1`  
  `GOOGLE_GENAI_USE_VERTEXAI="True"`

### **O Código: agent.py**

Agora, vamos definir a lógica do nosso agente. Ele terá uma única ferramenta: uma função Python que retorna a hora atual.

1. **Preencha o \_\_init\_\_.py:** Este arquivo informa ao Python que o diretório time\_agent é um pacote e exporta o agente.  
   `# time_agent/__init__.py`  
   `from. import agent`

2. **Preencha o agent.py:** Este é o coração do seu agente. Copie e cole o seguinte código.  
   `# time_agent/agent.py`  
   `import datetime`  
   `from zoneinfo import ZoneInfo`  
   `from google.adk.agents import LlmAgent`  
   `from google.adk.tools import FunctionTool`

   `# 1. Defina uma função Python que será a ferramenta do seu agente.`  
   `#    As anotações de tipo (type hints) são importantes para que o LLM entenda`  
   `#    os parâmetros e o que a função faz.`  
   `def get_current_time(timezone: str) -> str:`  
       `"""Obtém a hora atual em um fuso horário específico."""`  
       `try:`  
           `now = datetime.datetime.now(ZoneInfo(timezone))`  
           `return f"A hora atual em {timezone} é {now.strftime('%H:%M:%S')}."`  
       `except Exception as e:`  
           `return f"Não foi possível encontrar o fuso horário: {timezone}. Tente um formato como 'America/New_York'. Erro: {e}"`

   `# 2. Crie uma instância do agente.`  
   `#    O ADK requer que o agente principal seja nomeado 'root_agent'.`  
   `root_agent = LlmAgent(`  
       `name="time_assistant",`  
       `# Escolha o modelo. 'gemini-1.5-flash' é rápido e eficiente.`  
       `model="gemini-1.5-flash-latest",`  
       `description="Um assistente que pode informar a hora atual em diferentes fusos horários.",`  
       `# A instrução guia o comportamento do LLM.`  
       `instruction="Você é um assistente prestativo. Use a ferramenta 'get_current_time' para responder a perguntas sobre a hora.",`  
       `# Forneça a lista de ferramentas que o agente pode usar.`  
       `tools=,`  
   `)`

### **Executando e Testando**

O ADK vem com uma interface web de desenvolvimento local que facilita a interação e a depuração.

1. **Inicie o Servidor Web:** No terminal, a partir do diretório seu\_projeto/ (o diretório pai de time\_agent/), execute o seguinte comando.  
   `adk web`

2. **Interaja com o Agente:** O terminal exibirá uma URL, geralmente http://127.0.0.1:8000. Abra-a em seu navegador.  
   * No canto superior esquerdo, selecione time\_agent.  
   * No chat, digite uma pergunta como: Qual a hora em São Paulo? ou what time is it in Europe/London?.  
   * Observe a interface. Você verá não apenas a resposta final, mas também o "trace" de execução, mostrando que o agente decidiu chamar a ferramenta get\_current\_time com o parâmetro correto. Esta visibilidade é fundamental para o desenvolvimento e depuração de agentes.

## **Parte 2: O Salto para a Orquestração Multiagente: A Equipe "Pesquisador-Escritor"**

Com a base de um agente único estabelecida, agora podemos construir o sistema multiagente simples e replicável solicitado. Criaremos uma equipe com um agente "coordenador" que delega tarefas a dois agentes "trabalhadores" especializados. Este exemplo é conceitualmente claro e não requer serviços externos ou configurações complexas na nuvem.

### **A Arquitetura**

Nossa equipe de agentes terá os seguintes membros:

* **ResearcherAgent (Agente Pesquisador):** Um especialista focado. Sua única tarefa é receber um tópico e usar a ferramenta google\_search integrada do ADK para encontrar informações relevantes na web.  
* **WriterAgent (Agente Escritor):** Outro especialista. Sua única tarefa é receber um bloco de texto bruto (os resultados da pesquisa) e resumi-lo em um parágrafo conciso e bem escrito.  
* **CoordinatorAgent (Agente Coordenador):** O orquestrador. Ele recebe a solicitação de alto nível do usuário (por exemplo, "pesquise e resuma as últimas notícias sobre o Google ADK"). Este agente não possui ferramentas de busca ou escrita; em vez disso, ele delega a tarefa de pesquisa ao ResearcherAgent e a tarefa de escrita ao WriterAgent.

Para implementar essa hierarquia, usaremos a primitiva AgentTool do ADK. A transição de dar a um agente uma *função* como ferramenta (na Parte 1\) para dar a um agente outro *agente* como ferramenta é um passo conceitual direto e intuitivo. O AgentTool abstrai a complexidade da comunicação entre agentes, encapsulando-a no paradigma de "ferramenta" já familiar. Esta é a maneira mais simples e poderosa de criar um sistema multiagente hierárquico para um iniciante, tornando-se a escolha pedagógica ideal para este tutorial.

### **O Código (Completo e Replicável)**

Para simplificar, todo o sistema será definido em um único arquivo agent.py. Crie uma nova estrutura de pastas como na Parte 1, mas nomeie a pasta do agente como research\_writer\_agent.  
`# research_writer_agent/agent.py`  
`from google.adk.agents import LlmAgent`  
`from google.adk.tools import FunctionTool, AgentTool, google_search`

`# --- Definição dos Agentes Especialistas (Trabalhadores) ---`

`# 1. Agente Pesquisador`  
`#    Este agente é especializado em usar a busca do Google.`  
`researcher_agent = LlmAgent(`  
    `name="researcher_agent",`  
    `model="gemini-1.5-flash-latest",`  
    `description="Este agente é especialista em pesquisar na web usando o Google Search para encontrar informações sobre um determinado tópico.",`  
    `instruction="Dado um tópico, use a ferramenta google_search para encontrar informações relevantes e retorne os resultados brutos.",`  
    `tools=[`  
        `google_search,`  
    `],`  
`)`

`# 2. Agente Escritor`  
`#    Este agente é especializado em resumir textos.`  
`writer_agent = LlmAgent(`  
    `name="writer_agent",`  
    `model="gemini-1.5-pro-latest", # Usamos um modelo mais robusto para uma melhor escrita`  
    `description="Este agente é especialista em pegar um texto bruto e resumi-lo em um parágrafo conciso e bem escrito.",`  
    `instruction="Você receberá um texto. Sua tarefa é resumi-lo em um único parágrafo, focando nos pontos mais importantes. A resposta deve ser apenas o resumo.",`  
    `# Este agente não precisa de ferramentas externas.`  
`)`

`# --- Definição do Agente Orquestrador (Coordenador) ---`

`# 3. Agente Coordenador`  
`#    Este é o agente principal que o usuário irá interagir.`  
`#    Ele orquestra o trabalho dos outros agentes.`  
`root_agent = LlmAgent(`  
    `name="coordinator_agent",`  
    `model="gemini-1.5-pro-latest",`  
    `description="Um coordenador que gerencia uma equipe de agentes para pesquisar e resumir tópicos.",`  
    `instruction="""`  
    `Você é um coordenador de um time de agentes de IA. Seu objetivo é responder à solicitação do usuário seguindo um plano de duas etapas:`  
    `1. Primeiro, use a ferramenta 'researcher_agent' para pesquisar o tópico solicitado pelo usuário.`  
    `2. Segundo, pegue a saída do pesquisador e use a ferramenta 'writer_agent' para criar um resumo.`  
    `3. Finalmente, apresente o resumo final ao usuário.`  
    `Não responda diretamente ao usuário com suas próprias palavras, apenas execute o plano.`  
    `""",`  
    `# A "mágica" acontece aqui: os outros agentes são fornecidos como ferramentas.`  
    `tools=,`  
    `# O sub_agents é a forma explícita de definir a hierarquia`  
    `sub_agents=[researcher_agent, writer_agent]`  
`)`

Não se esqueça de criar o \_\_init\_\_.py e o .env como na Parte 1\. Depois de executar adk web e selecionar research\_writer\_agent, você pode fazer uma solicitação como: Pesquise sobre as últimas atualizações do Google Agent Development Kit e me dê um resumo. Você verá no trace o coordinator\_agent primeiro chamar o researcher\_agent e, em seguida, chamar o writer\_agent com a saída do primeiro.

## **Parte 3: Um Mergulho Profundo na Arquitetura Multiagente**

Agora que construímos um sistema funcional, vamos dissecar o código para entender os princípios do ADK que o fazem funcionar. Passaremos do "como" para o "porquê", fornecendo uma compreensão mais profunda.

### **Definindo a Hierarquia de Agentes**

No nosso exemplo, a hierarquia é definida de duas maneiras. A mais explícita é o uso do parâmetro sub\_agents na definição do CoordinatorAgent. Isso estabelece formalmente uma relação pai-filho, que é crucial para agentes de fluxo de trabalho (WorkflowAgents) e para a navegação na árvore de agentes.  
A segunda maneira, mais implícita e funcional para este padrão de delegação, é o uso do AgentTool. Ao envolver researcher\_agent e writer\_agent em AgentTool, nós os transformamos em capacidades que o CoordinatorAgent pode invocar. Essa abordagem se alinha com a filosofia de "código como configuração" do ADK, onde a estrutura da aplicação é definida através de objetos Python, em vez de arquivos de configuração estáticos. Essa abordagem orientada a objetos é uma escolha de design deliberada para promover a manutenibilidade e a escalabilidade, especialmente em sistemas de nível empresarial. Embora possa parecer "super-projetado" para um iniciante, essa estrutura é o que permite a criação de agentes robustos, testáveis e prontos para produção, com suporte para avaliação integrada e implantação em serviços gerenciados como o Agent Engine.

### **A Primitiva AgentTool Explicada**

O AgentTool é uma das primitivas mais poderosas do ADK para orquestração. Seu funcionamento é o seguinte:

1. **Geração Dinâmica da Ferramenta:** Quando você cria AgentTool(researcher\_agent), o ADK inspeciona o researcher\_agent. Ele usa o name e a description do agente para gerar dinamicamente uma declaração de função (semelhante a uma ferramenta de função OpenAPI) que é apresentada ao LLM do CoordinatorAgent. Para o LLM, researcher\_agent parece ser apenas mais uma ferramenta em sua caixa de ferramentas.  
2. **Fluxo de Execução:** Quando o CoordinatorAgent decide que precisa pesquisar um tópico, seu LLM gera uma chamada de função para a ferramenta researcher\_agent. O framework ADK intercepta essa chamada. Em vez de executar uma simples função Python, ele invoca todo o ciclo de vida do researcher\_agent, passando a consulta do usuário como entrada. O CoordinatorAgent então pausa e aguarda. O researcher\_agent executa, chama sua própria ferramenta (google\_search), obtém um resultado e formula uma resposta final. Essa resposta final é então retornada como a saída da chamada da ferramenta para o CoordinatorAgent. Trata-se de uma chamada síncrona e bloqueante dentro do turno do agente pai.

### **Lógica de Orquestração e Engenharia de Prompt**

A orquestração em nosso exemplo é impulsionada pelo LLM do CoordinatorAgent, guiado por sua instruction. Analisando o prompt:  
"Você é um coordenador... Seu objetivo é responder... seguindo um plano de duas etapas: 1\. Primeiro, use a ferramenta 'researcher\_agent'... 2\. Segundo, pegue a saída... e use a ferramenta 'writer\_agent'..."  
Este prompt não apenas define a persona do agente, mas também estabelece um plano de execução explícito. A engenharia de prompt é a chave para a orquestração dinâmica baseada em LLM. Instruções claras e descrições precisas para cada agente e ferramenta são fundamentais para que o LLM orquestrador possa tomar as decisões corretas sobre qual ferramenta (ou agente-ferramenta) usar e em que ordem.  
\<br\>  
**Tabela 2: Componentes Chave do ADK em Nosso Tutorial**

| Componente         | Tipo                    | Propósito em Nosso Tutorial                                                                                                                                          |
| :----------------- | :---------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **LlmAgent**       | Classe de Agente        | O bloco de construção fundamental. Usado para criar todos os três agentes (Researcher, Writer, Coordinator), fornecendo-lhes um modelo de linguagem para raciocínio. |
| **AgentTool**      | Primitiva de Ferramenta | Envolve um agente (Researcher, Writer) para que ele possa ser usado como uma ferramenta por outro agente (Coordinator), permitindo a delegação de tarefas.           |
| **google\_search** | Ferramenta Integrada    | Uma FunctionTool pré-construída fornecida pelo ADK. Concede ao ResearcherAgent a capacidade de acessar informações da web em tempo real.                             |
| **adk web**        | Comando da CLI          | Inicia a interface de usuário web do desenvolvedor local, fornecendo um ambiente de chat para testar e um visualizador de "trace" para depurar o fluxo de execução.  |

\<br\>

## **Parte 4: Dominando a Colaboração de Agentes \- Estado e Controle de Fluxo Avançados**

O sistema que construímos é poderoso, mas o fluxo de informações é linear e efêmero, contido em uma única chamada síncrona. Para criar colaborações mais complexas e desacopladas, os agentes precisam de uma memória compartilhada. Esta seção introduz os mecanismos para criar interações mais sofisticadas e determinísticas.

### **Gerenciamento de Estado Explícito com session.state**

O que transforma um "grupo" de agentes em um verdadeiro "sistema" de agentes é a capacidade de compartilhar informações de forma persistente e assíncrona. No ADK, isso é alcançado através do session.state, que atua como um "quadro negro" ou "memória de trabalho compartilhada" para todos os agentes que operam na mesma sessão.

* **Escopos de Estado:** O session.state é um dicionário que pode ser acessado por qualquer agente. O ADK usa prefixos nas chaves para gerenciar o escopo e a persistência dos dados :  
  * **Sem Prefixo (Estado da Sessão):** state\['minha\_chave'\]. Os dados são específicos da sessão de conversação atual.  
  * **user: (Estado do Usuário):** state\['user:preferencia'\]. Os dados são compartilhados entre todas as sessões de um usuário específico.  
  * **app: (Estado da Aplicação):** state\['app:config'\]. Os dados são compartilhados globalmente por todos os usuários e sessões.  
  * **temp: (Estado Temporário):** state\['temp:resultado\_bruto'\]. Os dados existem apenas para o turno de processamento atual e nunca são persistidos.  
* **Refatoração do Código para Usar Estado Compartilhado:** Vamos modificar nossa equipe para usar o session.state. O ResearcherAgent agora escreverá seus resultados no estado, e o WriterAgent lerá a partir dele.  
  * **Modifique a ferramenta do ResearcherAgent:**  
    `# Dentro de uma ferramenta, o estado é acessado através do 'tool_context'`  
    `def search_and_save(topic: str, tool_context) -> str:`  
        `"""Pesquisa um tópico e salva os resultados no estado da sessão."""`  
        `results = google_search.run(query=topic)`  
        `# Salva os resultados no estado da sessão para outros agentes usarem`  
        `tool_context.state["research_notes"] = results`  
        `return f"Pesquisa sobre '{topic}' concluída e notas salvas no estado."`

    `# Atualize a definição do researcher_agent para usar a nova ferramenta`  
    `researcher_agent = LlmAgent(`  
       `..., # Mantenha as outras propriedades`  
        `tools=`  
    `)`

  * **Modifique a instrução do WriterAgent:**  
    `writer_agent = LlmAgent(`  
       `..., # Mantenha as outras propriedades`  
        `instruction="""`  
        `Sua tarefa é encontrar notas de pesquisa no estado da sessão na chave 'research_notes'.`  
        `Se encontrá-las, resuma o texto em um único parágrafo.`  
        `Se não encontrar, informe que as notas de pesquisa não estão disponíveis.`  
        `""",`  
    `)`

Com essa mudança, os agentes estão mais desacoplados. O CoordinatorAgent pode simplesmente invocar o ResearcherAgent e depois o WriterAgent, sabendo que eles se comunicarão através do session.state. Isso abre portas para padrões mais complexos, como um "Fan-Out/Gather", onde múltiplos agentes pesquisadores poderiam escrever em chaves de estado diferentes, e um agente final os agregaria.

### **Fluxos de Trabalho Determinísticos com SequentialAgent**

Às vezes, a orquestração dinâmica de um LLM não é desejável; você precisa de um processo que seja executado da mesma maneira todas as vezes. Para isso, o ADK fornece WorkflowAgents — agentes não-LLM que controlam o fluxo de execução.

* **Introduzindo WorkflowAgents:** Existem três tipos principais: SequentialAgent (executa subagentes em ordem), ParallelAgent (executa subagentes simultaneamente) e LoopAgent (executa subagentes repetidamente até que uma condição seja atendida).  
* **Refatoração Final para um Pipeline Determinístico:** Vamos substituir nosso CoordinatorAgent baseado em LLM por um SequentialAgent.  
  `from google.adk.agents import LlmAgent, SequentialAgent`  
  `#... (as definições do researcher_agent e writer_agent permanecem as mesmas)...`

  `# Substitua o coordinator_agent por um SequentialAgent`  
  `root_agent = SequentialAgent(`  
      `name="research_pipeline",`  
      `# A lista de sub_agents define a ordem de execução`  
      `sub_agents=[`  
          `researcher_agent,`  
          `writer_agent,`  
      `]`  
  `)`  
  Nesta versão, quando o root\_agent é executado, ele sempre executará o researcher\_agent primeiro, seguido pelo writer\_agent. O ADK gerencia automaticamente a passagem do contexto e do estado de um agente para o próximo na sequência. Isso cria um pipeline de processamento de dados totalmente previsível e robusto.

## **Conclusão e Caminho a Seguir**

Este relatório guiou você em uma jornada desde a criação de um agente de IA único e funcional até a construção de um sistema multiagente colaborativo, tudo dentro de um ambiente de desenvolvimento local, rápido e replicável.

* **Resumo dos Aprendizados:** Começamos com os fundamentos, construindo um agente simples para entender o ciclo de desenvolvimento do ADK. Em seguida, demos o salto para a orquestração multiagente, usando a poderosa e intuitiva primitiva AgentTool para criar uma equipe dinâmica de "Pesquisador-Escritor". Aprofundamos nossa compreensão ao explorar como o session.state permite uma memória compartilhada e uma colaboração mais complexa. Finalmente, demonstramos como usar o SequentialAgent para criar pipelines determinísticos quando a previsibilidade é fundamental.  
* **Seu Modelo Replicável:** Os padrões de código e arquitetura das Partes 2 e 4 servem como um modelo robusto e local que você pode adaptar e expandir para seus próprios projetos multiagentes. Você agora possui a base para escolher entre orquestração dinâmica baseada em LLM e fluxos de trabalho determinísticos, dependendo dos requisitos da sua aplicação.  
* **Próximos Passos e Exploração Futura:** Com essa base sólida, você está preparado para explorar os aspectos mais avançados do ecossistema ADK.  
  * **Exemplos de Produção:** Agora que você entende os fundamentos, explore o repositório oficial google/adk-samples e os Codelabs mais complexos, como o "Agente de Renovação" ou o "InstaVibe". Você reconhecerá os padrões e estará mais bem equipado para entender suas arquiteturas baseadas em nuvem.  
  * **O Ecossistema Mais Amplo:** Investigue conceitos avançados como a implantação de seus agentes em um ambiente gerenciado e escalável com o **Vertex AI Agent Engine** , permitindo a comunicação entre agentes construídos em diferentes frameworks com o **protocolo Agent2Agent (A2A)** , e a conexão com um vasto ecossistema de ferramentas externas através do **Model Context Protocol (MCP)**.  
  * **Comunidade e Contribuição:** O ADK é um projeto de código aberto em rápida evolução. Engaje-se com a comunidade através dos repositórios do GitHub para Python , Java e a documentação.

Você deu os primeiros e mais importantes passos no mundo do desenvolvimento de sistemas multiagentes. A combinação de modularidade, especialização e orquestração que você aprendeu aqui é a chave para construir a próxima geração de aplicações de IA inteligentes e robustas.

#### **Referências citadas**

1\. Multi-Agent Systems in ADK \- Google, https://google.github.io/adk-docs/agents/multi-agents/ 2\. Multi-agent App with ADK, Agent Engine and AlloyDB | Google Codelabs, https://codelabs.developers.google.com/multi-agent-app-with-adk 3\. Comprehensive Guide to Building AI Agents Using Google Agent ..., https://www.firecrawl.dev/blog/google-adk-multi-agent-tutorial 4\. Build and manage multi-system agents with Vertex AI | Google Cloud Blog, https://cloud.google.com/blog/products/ai-machine-learning/build-and-manage-multi-system-agents-with-vertex-ai 5\. Agent Development Kit: Making it easy to build multi-agent applications, https://developers.googleblog.com/en/agent-development-kit-easy-to-build-multi-agent-applications/ 6\. Agent Development Kit \- Google, https://google.github.io/adk-docs/ 7\. Just did a deep dive into Google's Agent Development Kit (ADK). Here are some thoughts, nitpicks, and things I loved (unbiased) \- Reddit, https://www.reddit.com/r/AI\_Agents/comments/1jvsu4l/just\_did\_a\_deep\_dive\_into\_googles\_agent/ 8\. Session \- Agent Development Kit \- Google, https://google.github.io/adk-docs/sessions/session/ 9\. Quickstart: Build an agent with the Agent Development Kit ..., https://cloud.google.com/vertex-ai/generative-ai/docs/agent-development-kit/quickstart 10\. Build your first AI Agent with ADK \- Agent Development Kit by ..., https://dev.to/marianocodes/build-your-first-ai-agent-with-adk-agent-development-kit-by-google-409b 11\. From Prototypes to Agents with ADK \- Google Codelabs, https://codelabs.developers.google.com/your-first-agent-with-adk 12\. Building AI Agents with Google ADK, FastAPI, and MCP \- DEV Community, https://dev.to/timtech4u/building-ai-agents-with-google-adk-fastapi-and-mcp-26h7 13\. Build Multi-Model Agent in 10 Minutes \- Google's New Agent Kit Is INSANE\! \- YouTube, https://www.youtube.com/watch?v=SjZG-QKrw5o 14\. Agent Development Kit (ADK) Masterclass: Build AI Agents & Automate Workflows (Beginner to Pro) \- YouTube, https://www.youtube.com/watch?v=P4VFL9nIaIA 15\. google/adk-python: An open-source, code-first Python toolkit for building, evaluating, and deploying sophisticated AI agents with flexibility and control. \- GitHub, https://github.com/google/adk-python 16\. Vertex AI Agent Builder | Google Cloud, https://cloud.google.com/products/agent-builder 17\. The Complete Guide to Google's Agent Development Kit (ADK) \- Sid Bharath, https://www.siddharthbharath.com/the-complete-guide-to-googles-agent-development-kit-adk/ 18\. State \- Agent Development Kit, https://google.github.io/adk-docs/sessions/state/ 19\. google/adk-samples: A collection of sample agents built ... \- GitHub, https://github.com/google/adk-samples 20\. Google's Agent Stack in Action: ADK, A2A, MCP on Google Cloud, https://codelabs.developers.google.com/instavibe-adk-multi-agents/instructions 21\. Manage sessions with Agent Development Kit | Generative AI on Vertex AI \- Google Cloud, https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/sessions/manage-sessions-adk 22\. What's new with Agents: ADK, Agent Engine, and A2A Enhancements, https://developers.googleblog.com/en/agents-adk-agent-engine-a2a-enhancements-google-io/ 23\. google/adk-java: An open-source, code-first Java toolkit for building, evaluating, and deploying sophisticated AI agents with flexibility and control. \- GitHub, https://github.com/google/adk-java 24\. google/adk-docs: An open-source, code-first Python toolkit for building, evaluating, and deploying sophisticated AI agents with flexibility and control. \- GitHub, https://github.com/google/adk-docs