from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.rotas.query import router as query_router


app = FastAPI(
    title="SQL Agent API",
    description="API para fazer perguntas em linguagem natural a uma base de dados SQL usando LangChain e OpenAI.",
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


@app.get("/")
async def root():
    """
    Endpoint raiz com informações da API.
    """
    return {
        "message": "SQL Agent API",
        "descricao": "Faça perguntas em linguagem natural sobre a base de dados Chinook.",
        "endpoints": {
            "POST /query": "Envie uma pergunta e receba a resposta do agente SQL."
        },
        "exemplo": {
            "pergunta": "Quais são os 5 artistas com mais álbuns?"
        }
    }


@app.get("/health")
async def health_check():
    """
    Endpoint para verificar se a API está a funcionar.
    """
    return {"status": "ok"}

