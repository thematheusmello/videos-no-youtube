"""
RAG Agent - Agente de Retrieval Augmented Generation

Este módulo implementa um agente RAG que:
1. Recebe uma pergunta do utilizador
2. Usa uma ferramenta de retrieval para buscar contexto relevante
3. Gera uma resposta baseada no contexto recuperado

Baseado no tutorial: https://langchain-5e9cc07a.mintlify.app/oss/python/langchain/rag
"""

import os
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain.agents import create_agent

from app.ferramentas.vector_store import get_indexed_vector_store


class RAGAgent:
    """
    Agente RAG que responde perguntas usando contexto
    recuperado de um vector store.
    
    Fluxo de funcionamento:
    1. Utilizador faz uma pergunta
    2. Agente decide se precisa buscar contexto
    3. Se sim, usa a tool retrieve_context
    4. Com o contexto, gera a resposta final
    """

    def __init__(self):
        # Verificar API key
        if "OPENAI_API_KEY" not in os.environ:
            raise RuntimeError("Define a variável de ambiente OPENAI_API_KEY.")

        # Inicializar modelo (mesmo modelo do SQL agent para consistência)
        self.model = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0
        )

        # Obter o vector store já indexado
        self.vector_store = get_indexed_vector_store()

        # Criar a ferramenta de retrieval
        # Usamos uma closure para capturar self.vector_store
        self.tools = [self._create_retrieve_tool()]

        # Prompt de sistema que explica ao agente o que fazer
        self.system_prompt = """
És um assistente especializado em responder perguntas sobre agentes autónomos alimentados por LLMs.

Tens acesso a uma ferramenta que recupera informação de um blog post sobre o tema.
Usa a ferramenta para buscar contexto relevante antes de responder às perguntas do utilizador.

Regras:
- Sempre que receberes uma pergunta, usa a ferramenta retrieve_context para buscar informação relevante.
- Baseia a tua resposta no contexto recuperado.
- Se o contexto não contiver informação suficiente, indica isso na resposta.
- Responde de forma clara e concisa.
"""

        # Criar o agente com as ferramentas
        self.agent = create_agent(
            model=self.model,
            tools=self.tools,
            system_prompt=self.system_prompt,
        )

    def _create_retrieve_tool(self):
        """
        Cria a ferramenta de retrieval que busca documentos relevantes.
        
        A tool usa response_format="content_and_artifact" para:
        - Retornar texto formatado para o modelo (content)
        - Guardar os documentos originais como artifact (para metadata)
        """
        vector_store = self.vector_store  # Captura para a closure

        @tool(response_format="content_and_artifact")
        def retrieve_context(query: str):
            """
            Recupera informação relevante para responder a uma pergunta.
            
            Usa busca por similaridade semântica no vector store
            para encontrar os chunks de texto mais relevantes.
            
            Args:
                query: A pergunta ou termos de busca
                
            Returns:
                Texto formatado com a fonte e conteúdo dos documentos
            """
            # Buscar os k=2 documentos mais similares à query
            retrieved_docs = vector_store.similarity_search(query, k=2)
            
            # Serializar para texto que o modelo pode usar
            serialized = "\n\n".join(
                f"Source: {doc.metadata}\nContent: {doc.page_content}"
                for doc in retrieved_docs
            )
            
            # Retorna (content para o modelo, artifact com docs originais)
            return serialized, retrieved_docs

        return retrieve_context

    def responder_pergunta(self, pergunta: str) -> str:
        """
        Envia a pergunta para o agente e devolve a resposta final.
        
        O agente irá:
        1. Analisar a pergunta
        2. Usar a ferramenta de retrieval para buscar contexto
        3. Gerar uma resposta baseada no contexto
        
        Args:
            pergunta: A pergunta do utilizador
            
        Returns:
            A resposta gerada pelo agente
        """
        result = self.agent.invoke(
            {
                "messages": [
                    {"role": "user", "content": pergunta}
                ]
            }
        )

        # Extrair a última mensagem (resposta do assistente)
        messages = result.get("messages", [])
        if not messages:
            return "Não foi possível obter uma resposta."

        final_msg = messages[-1]
        content = final_msg.content if hasattr(final_msg, "content") else ""

        # Tratar diferentes formatos de conteúdo
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            parts = []
            for block in content:
                if isinstance(block, dict) and "text" in block:
                    parts.append(block["text"])
                elif isinstance(block, str):
                    parts.append(block)
            return "\n".join(parts) if parts else str(content)
        else:
            return str(content)


# ============================================================
# Singleton Pattern - Mantém uma única instância do agente
# ============================================================

_agent_instance: RAGAgent | None = None


def get_rag_agent() -> RAGAgent:
    """
    Retorna a instância do agente RAG (singleton).
    
    A primeira chamada inicializa o agente e indexa os documentos.
    Chamadas seguintes retornam a mesma instância.
    """
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = RAGAgent()
    return _agent_instance


