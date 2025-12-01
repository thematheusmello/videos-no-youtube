from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.rotas.query import router as query_router
from app.rotas.rag import router as rag_router


app = FastAPI(
    title="SQL & RAG Agent API",
    description="API para fazer perguntas em linguagem natural a uma base de dados SQL e a documentos usando LangChain e OpenAI.",
    version="1.0.0",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas
app.include_router(query_router)
app.include_router(rag_router)


@app.get("/")
async def root():
    """
    Endpoint raiz com informações da API.
    """
    return {
        "message": "SQL & RAG Agent API",
        "descricao": "Faça perguntas em linguagem natural sobre a base de dados Chinook ou sobre documentos.",
        "endpoints": {
            "POST /query": "Envie uma pergunta e receba a resposta do agente SQL.",
            "POST /rag/query": "Envie uma pergunta e receba a resposta do agente RAG (sobre documentos)."
        },
        "exemplos": {
            "sql": {
                "pergunta": "Quais são os 5 artistas com mais álbuns?"
            },
            "rag": {
                "pergunta": "What is task decomposition?"
            }
        }
    }


@app.get("/health")
async def health_check():
    """
    Endpoint para verificar se a API está a funcionar.
    """
    return {"status": "ok"}

