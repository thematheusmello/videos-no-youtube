import os
import pathlib
import requests

from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_agent


# 1) Ler a API key do ambiente
if "OPENAI_API_KEY" not in os.environ:
    raise RuntimeError("Define a variável de ambiente OPENAI_API_KEY antes de correr o script.")


# 2) Escolher o modelo (precisa suportar tool-calling)
# Podes trocar para "gpt-5-mini-2025-08-07" se tiveres acesso
model = ChatOpenAI(
    model="gpt-5-mini-2025-08-07",
    temperature=0
)


# 3) Fazer download da base de dados Chinook, se ainda não existir
def download_chinook_db():
    url = "https://storage.googleapis.com/benchmarks-artifacts/chinook/Chinook.db"
    local_path = pathlib.Path("Chinook.db")

    if local_path.exists():
        print(f"[INFO] {local_path} já existe, a saltar download.")
        return local_path

    print("[INFO] A descarregar base de dados de exemplo (Chinook.db)...")
    resp = requests.get(url)
    if resp.status_code == 200:
        local_path.write_bytes(resp.content)
        print("[INFO] Base de dados guardada como Chinook.db")
        return local_path
    else:
        raise RuntimeError(f"Falha ao descarregar Chinook.db (status {resp.status_code})")


db_path = download_chinook_db()


# 4) Ligar ao SQLite através do wrapper do LangChain
db = SQLDatabase.from_uri("sqlite:///Chinook.db")

print(f"[INFO] Dialeto: {db.dialect}")
print(f"[INFO] Tabelas disponíveis: {db.get_usable_table_names()}")


# 5) Criar ferramentas para interagir com a base de dados
toolkit = SQLDatabaseToolkit(db=db, llm=model)
tools = toolkit.get_tools()

print("\n[INFO] Ferramentas disponíveis para o agente:\n")
for tool in tools:
    print(f"- {tool.name}: {tool.description}\n")


# 6) Prompt de sistema do agente (parafraseado do tutorial)
system_prompt = f"""
És um agente especializado em consultar uma base de dados SQL ({db.dialect}).

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


# 7) Criar o agente com o modelo, ferramentas e prompt
agent = create_agent(
    model=model,
    tools=tools,
    system_prompt=system_prompt,
)


def responder_pergunta(pergunta: str) -> str:
    """
    Envia a pergunta para o agente no formato esperado
    e devolve o último conteúdo gerado (resposta final).
    """
    # O create_agent espera um estado com "messages"
    result = agent.invoke(
        {
            "messages": [
                {"role": "user", "content": pergunta}
            ]
        }
    )

    # A estrutura devolvida inclui a lista de mensagens
    messages = result.get("messages", [])
    if not messages:
        return "Não foi possível obter uma resposta."

    final_msg = messages[-1]
    # AIMessage tem um atributo .content, não um método .get()
    content = final_msg.content if hasattr(final_msg, "content") else ""
    # Pode ser string ou lista com blocos; tratamos os dois casos
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        # Se vier como lista de blocos, juntamos o texto
        parts = []
        for block in content:
            if isinstance(block, dict) and "text" in block:
                parts.append(block["text"])
            elif isinstance(block, str):
                parts.append(block)
        return "\n".join(parts) if parts else str(content)
    else:
        return str(content)


if __name__ == "__main__":
    print("\n[INFO] Agente SQL pronto.")
    print("[INFO] Podes fazer perguntas sobre a base de dados Chinook.")
    print("[INFO] Exemplo: 'Quais são os 5 artistas com mais álbuns?'")
    print("[INFO] Para sair, usa CTRL+C.\n")

    while True:
        try:
            pergunta = input("Pergunta em linguagem natural: ").strip()
            if not pergunta:
                continue

            print("\n[A AGENTE] A pensar...\n")
            resposta = responder_pergunta(pergunta)
            print("Resposta:\n")
            print(resposta)
            print("\n" + "-" * 60 + "\n")

        except KeyboardInterrupt:
            print("\n[INFO] A terminar. Até à próxima!")
            break
