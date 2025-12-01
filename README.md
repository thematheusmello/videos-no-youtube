# SQL & RAG Agent

Agentes interativos que permitem:

- Fazer perguntas em linguagem natural sobre uma base de dados SQLite (agente **SQL**)
- Fazer perguntas em linguagem natural sobre um documento da web usando RAG (agente **RAG**)

Disponível como CLI interativo (apenas SQL) ou API REST com FastAPI (SQL + RAG).

## Vídeo no Youtube

https://www.youtube.com/watch?v=wcAvGYcnK_M&t=4s

## Descrição (Agente SQL)

Este projeto implementa um agente SQL inteligente que:

- Conecta-se à base de dados de exemplo Chinook (download automático)
- Permite fazer perguntas em português sobre os dados
- Gera e executa queries SQL automaticamente
- Retorna respostas em linguagem natural

O projeto está disponível em duas formas:

- **CLI Interativo**: Script Python para uso via terminal
- **API REST**: Servidor FastAPI com endpoints HTTP (SQL + RAG)

---

## Descrição (Agente RAG)

O agente RAG (Retrieval Augmented Generation) responde perguntas sobre o conteúdo do artigo:

- **LLM Powered Autonomous Agents** – Lilian Weng  
  (`https://lilianweng.github.io/posts/2023-06-23-agent/`)

Ele funciona assim:

1. **Indexação** (uma vez, automática):
   - Faz o download da página do artigo
   - Usa `BeautifulSoup` para extrair apenas título, cabeçalhos e conteúdo do post
   - Corta o texto em vários _chunks_ menores
   - Gera _embeddings_ com OpenAI e guarda num `InMemoryVectorStore`
2. **Pergunta → Resposta**:
   - Dada uma pergunta, o agente usa um _tool_ `retrieve_context` para buscar os _chunks_ mais relevantes
   - Passa esse contexto para o modelo de chat da OpenAI
   - O modelo responde usando o conteúdo do artigo como principal fonte de verdade

## Requisitos

- Python 3.8 ou superior
- Conta OpenAI com API key válida
- Conexão à internet (para download da base de dados)

## Instalação

### 1. Criar e ativar um ambiente virtual (recomendado)

```bash
python -m venv venv
source venv/bin/activate  # No macOS/Linux
# ou
venv\Scripts\activate  # No Windows
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

O ficheiro `requirements.txt` inclui todas as dependências necessárias:

- FastAPI e Uvicorn (para a API)
- LangChain e LangChain OpenAI (para os agentes)
- LangChain Community (para ferramentas SQL)
- LangChain Text Splitters (para cortar documentos em _chunks_ para RAG)
- BeautifulSoup4 (para extrair texto de HTML no RAG)
- Requests (para download da base de dados)

## Configuração

### Variável de Ambiente: OPENAI_API_KEY

**No macOS/Linux:**

```bash
export OPENAI_API_KEY="A_TUA_CHAVE_AQUI"
```

Para tornar permanente, adicione ao ficheiro `~/.zshrc` ou `~/.bashrc`:

```bash
echo 'export OPENAI_API_KEY="A_TUA_CHAVE_AQUI"' >> ~/.zshrc
source ~/.zshrc
```

**No Windows (PowerShell):**

```powershell
setx OPENAI_API_KEY "A_TUA_CHAVE_AQUI"
```

> **Importante:** Feche e reabra o terminal depois de usar `setx`.

## Como Executar

### Opção 1: CLI Interativo

```bash
python sql_agent_cli.py
```

Na primeira execução, o script irá:

1. Descarregar automaticamente a base de dados Chinook.db
2. Conectar-se à base de dados
3. Inicializar o agente SQL
4. Aguardar as tuas perguntas

### Opção 2: API REST (FastAPI)

```bash
uvicorn app.main:app --reload
```

A API estará disponível em `http://localhost:8000`

**Endpoints disponíveis:**

- `GET /` - Informações gerais da API (SQL + RAG)
- `GET /health` - Health check
- `POST /query` - Enviar perguntas ao agente SQL (base de dados Chinook)
- `POST /rag/query` - Enviar perguntas ao agente RAG (artigo da Lilian Weng)

### Exemplo: agente SQL (endpoint `/query`)

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"pergunta": "Quais são os 5 artistas com mais álbuns?"}'
```

Resposta (exemplo):

```json
{
  "resposta": "Os 5 artistas com mais álbuns são: ..."
}
```

### Exemplo: agente RAG (endpoint `/rag/query`)

```bash
curl -X POST "http://localhost:8000/rag/query" \
  -H "Content-Type: application/json" \
  -d '{"pergunta": "What is task decomposition?"}'
```

Resposta (exemplo):

```json
{
  "resposta": "Task decomposition refers to the process of breaking down a complex task into smaller, more manageable sub-tasks..."
}
```

**Documentação interativa:**

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Exemplos de Uso – Agente SQL (CLI ou API)

Após iniciar o agente SQL (CLI ou API), podes fazer perguntas como:

- `Quais são as tabelas desta base de dados?`
- `Quais são os 5 artistas com mais álbuns?`
- `Qual é o género com faixas mais longas em média?`
- `Mostra os 5 clientes que mais gastaram.`
- `Quantas faixas tem cada álbum?`

O agente irá:

- Analisar a pergunta
- Consultar o esquema da base de dados
- Construir a query SQL apropriada
- Executar a query
- Retornar a resposta em linguagem natural

## Exemplos de Uso – Agente RAG (API)

Após iniciar a API, podes fazer perguntas como:

- `What is task decomposition?`
- `How does Chain-of-Thought (CoT) prompting work?`
- `What is Tree-of-Thought (ToT) and how is it different from CoT?`
- `What are some common techniques for task decomposition in LLM agents?`

## Como Sair

Pressiona `CTRL+C` para terminar o programa.

## Estrutura do Projeto

```
sql-agent/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicação FastAPI principal (SQL + RAG)
│   ├── agentes/
│   │   ├── __init__.py
│   │   ├── sql_agent.py     # Classe SQLAgent (lógica do agente SQL)
│   │   └── rag_agent.py     # Classe RAGAgent (lógica do agente RAG)
│   ├── ferramentas/
│   │   ├── __init__.py
│   │   ├── database.py      # Configuração e download da base de dados Chinook
│   │   └── vector_store.py  # Indexação RAG (loader, splitter, vector store)
│   └── rotas/
│       ├── __init__.py
│       ├── query.py         # Endpoint POST /query (SQL)
│       └── rag.py           # Endpoint POST /rag/query (RAG)
├── sql_agent_cli.py         # Script CLI interativo (apenas SQL)
├── requirements.txt         # Dependências do projeto
├── Chinook.db               # Base de dados (criada automaticamente)
├── README.md                # Este ficheiro
└── venv/                    # Ambiente virtual (opcional)
```

## Tecnologias Utilizadas

- **FastAPI**: Framework web moderno e rápido para construção de APIs
- **Uvicorn**: Servidor ASGI de alto desempenho
- **LangChain**: Framework para construção de agentes com LLMs
- **OpenAI GPT**: Modelo de linguagem para geração de SQL e respostas
- **SQLite**: Base de dados relacional
- **SQLDatabaseToolkit**: Toolkit do LangChain para interação com bases de dados SQL
- **WebBaseLoader + BeautifulSoup4**: Carregamento e extração de conteúdo HTML para RAG
- **RecursiveCharacterTextSplitter**: Splitter de texto para criar _chunks_ de documentos
- **InMemoryVectorStore + OpenAIEmbeddings**: Vector store em memória para busca semântica no RAG

## Notas

- O modelo padrão na API é `gpt-4o-mini`. Podes alterar em `app/agentes/sql_agent.py` se necessário.
- O modelo padrão no CLI é `gpt-5-mini-2025-08-07`. Podes alterar em `sql_agent_cli.py` se necessário.
- A base de dados Chinook é descarregada automaticamente na primeira execução.
- O agente está configurado para apenas consultas (SELECT), não permite alterações nos dados.
- A API usa CORS habilitado para todas as origens (configurável em `app/main.py`).
