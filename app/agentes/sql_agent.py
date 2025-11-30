import os
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_agent

from app.ferramentas.database import get_database


class SQLAgent:
    """
    Agente SQL que responde perguntas em linguagem natural
    consultando a base de dados.
    """

    def __init__(self):
        # Verificar API key
        if "OPENAI_API_KEY" not in os.environ:
            raise RuntimeError("Define a variável de ambiente OPENAI_API_KEY.")

        # Inicializar modelo
        self.model = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0
        )

        # Conectar à base de dados
        self.db = get_database()

        # Criar ferramentas
        toolkit = SQLDatabaseToolkit(db=self.db, llm=self.model)
        self.tools = toolkit.get_tools()

        # Prompt de sistema
        self.system_prompt = f"""
És um agente especializado em consultar uma base de dados SQL ({self.db.dialect}).

Recebes uma pergunta do utilizador em linguagem natural e deves:
1) Ver as tabelas disponíveis na base de dados.
2) Ver os esquemas das tabelas relevantes.
3) Construir uma query SQL correta para responder à pergunta.
4) Rever a query antes de a executar, evitando erros óbvios.
5) Executar a query, analisar os resultados e responder em linguagem natural.

Regras importantes:
- Não faças operações que alterem dados (INSERT, UPDATE, DELETE, DROP, etc.).
- Sempre que possível, limita a query a no máximo 5 resultados.
- Não peças todas as colunas de uma tabela sem necessidade; seleciona só o que é relevante.
- Se a base de dados devolver um erro, ajusta a query e tenta novamente.
"""

        # Criar o agente
        self.agent = create_agent(
            model=self.model,
            tools=self.tools,
            system_prompt=self.system_prompt,
        )

    def responder_pergunta(self, pergunta: str) -> str:
        """
        Envia a pergunta para o agente e devolve a resposta final.
        """
        result = self.agent.invoke(
            {
                "messages": [
                    {"role": "user", "content": pergunta}
                ]
            }
        )

        messages = result.get("messages", [])
        if not messages:
            return "Não foi possível obter uma resposta."

        final_msg = messages[-1]
        content = final_msg.content if hasattr(final_msg, "content") else ""

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


# Instância singleton do agente (lazy initialization)
_agent_instance: SQLAgent | None = None


def get_sql_agent() -> SQLAgent:
    """
    Retorna a instância do agente SQL (singleton).
    """
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = SQLAgent()
    return _agent_instance

