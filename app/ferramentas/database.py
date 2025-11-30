import pathlib
import requests
from langchain_community.utilities import SQLDatabase


def download_chinook_db() -> pathlib.Path:
    """
    Faz download da base de dados Chinook se ainda não existir.
    Retorna o caminho para o ficheiro.
    """
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


def get_database() -> SQLDatabase:
    """
    Retorna uma instância de SQLDatabase conectada ao Chinook.db.
    Faz o download do ficheiro se necessário.
    """
    download_chinook_db()
    db = SQLDatabase.from_uri("sqlite:///Chinook.db")
    return db

