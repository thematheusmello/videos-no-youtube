"""
Rotas RAG - Endpoints para o agente RAG

Este módulo define os endpoints da API para interagir
com o agente RAG (Retrieval Augmented Generation).
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agentes.rag_agent import get_rag_agent


router = APIRouter(prefix="/rag", tags=["RAG"])


class RAGQueryRequest(BaseModel):
    """
    Modelo para o pedido de query RAG.
    
    Attributes:
        pergunta: Pergunta em linguagem natural sobre o blog post
    """
    pergunta: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"pergunta": "What is task decomposition?"},
                {"pergunta": "How does Chain of Thought prompting work?"},
            ]
        }
    }


class RAGQueryResponse(BaseModel):
    """
    Modelo para a resposta da query RAG.
    
    Attributes:
        resposta: Resposta gerada pelo agente com base no contexto recuperado
    """
    resposta: str


@router.post("/query", response_model=RAGQueryResponse)
async def query_rag(request: RAGQueryRequest):
    """
    Endpoint para fazer perguntas ao agente RAG.
    
    O agente irá:
    1. Buscar contexto relevante no vector store
    2. Gerar uma resposta baseada no contexto recuperado
    
    **Exemplo de uso:**
    ```json
    {
        "pergunta": "What is task decomposition?"
    }
    ```
    
    **Resposta:**
    ```json
    {
        "resposta": "Task decomposition is the process of breaking down..."
    }
    ```
    """
    if not request.pergunta.strip():
        raise HTTPException(
            status_code=400, 
            detail="A pergunta não pode estar vazia."
        )

    try:
        agent = get_rag_agent()
        resposta = agent.responder_pergunta(request.pergunta)
        return RAGQueryResponse(resposta=resposta)
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao processar pergunta: {str(e)}"
        )


