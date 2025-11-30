from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agentes.sql_agent import get_sql_agent


router = APIRouter()


class QueryRequest(BaseModel):
    """Modelo para o pedido de query."""
    pergunta: str


class QueryResponse(BaseModel):
    """Modelo para a resposta da query."""
    resposta: str


@router.post("/query", response_model=QueryResponse)
async def query_database(request: QueryRequest):
    """
    Endpoint para fazer perguntas em linguagem natural à base de dados.
    
    - **pergunta**: Pergunta em linguagem natural (ex: "Quais são os 5 artistas com mais álbuns?")
    """
    if not request.pergunta.strip():
        raise HTTPException(status_code=400, detail="A pergunta não pode estar vazia.")

    try:
        agent = get_sql_agent()
        resposta = agent.responder_pergunta(request.pergunta)
        return QueryResponse(resposta=resposta)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar pergunta: {str(e)}")

