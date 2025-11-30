# SQL Agent

Agente SQL interativo que permite fazer perguntas em linguagem natural sobre uma base de dados SQLite usando LangChain e OpenAI. Disponível como CLI interativo ou API REST com FastAPI.

## Vídeo no Youtube

https://www.youtube.com/watch?v=wcAvGYcnK_M&t=4s

## Descrição

Este projeto implementa um agente inteligente que:

- Conecta-se à base de dados de exemplo Chinook (download automático)
- Permite fazer perguntas em português sobre os dados
- Gera e executa queries SQL automaticamente
- Retorna respostas em linguagem natural

O projeto está disponível em duas formas:

- **CLI Interativo**: Script Python para uso via terminal
- **API REST**: Servidor FastAPI com endpoints HTTP

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
- LangChain e LangChain OpenAI (para o agente)
- LangChain Community (para ferramentas SQL)
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

- `GET /` - Informações da API
- `GET /health` - Health check
- `POST /query` - Enviar perguntas ao agente SQL

**Exemplo de uso com curl:**

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"pergunta": "Quais são os 5 artistas com mais álbuns?"}'
```

**Exemplo de resposta:**

```json
{
  "resposta": "Os 5 artistas com mais álbuns são: ..."
}
```

**Documentação interativa:**

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Exemplos de Uso

Após iniciar o script, podes fazer perguntas como:

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

## Como Sair

Pressiona `CTRL+C` para terminar o programa.

## Estrutura do Projeto

```
sql-agent/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicação FastAPI principal
│   ├── agentes/
│   │   ├── __init__.py
│   │   └── sql_agent.py     # Classe SQLAgent (lógica do agente)
│   ├── ferramentas/
│   │   ├── __init__.py
│   │   └── database.py      # Configuração e download da base de dados
│   └── rotas/
│       ├── __init__.py
│       └── query.py          # Endpoint POST /query
├── sql_agent_cli.py         # Script CLI interativo
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

## Notas

- O modelo padrão na API é `gpt-4o-mini`. Podes alterar em `app/agentes/sql_agent.py` se necessário.
- O modelo padrão no CLI é `gpt-5-mini-2025-08-07`. Podes alterar em `sql_agent_cli.py` se necessário.
- A base de dados Chinook é descarregada automaticamente na primeira execução.
- O agente está configurado para apenas consultas (SELECT), não permite alterações nos dados.
- A API usa CORS habilitado para todas as origens (configurável em `app/main.py`).
