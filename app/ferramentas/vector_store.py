"""
Vector Store - Funções para indexação e busca de documentos

Este módulo implementa o pipeline de indexação para RAG:
1. LOAD: Carregar documentos da web com WebBaseLoader
2. SPLIT: Dividir em chunks com RecursiveCharacterTextSplitter
3. STORE: Indexar no InMemoryVectorStore com OpenAI Embeddings
"""

import os
import bs4
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


# URL do blog post que será indexado
BLOG_URL = "https://lilianweng.github.io/posts/2023-06-23-agent/"


def get_embeddings() -> OpenAIEmbeddings:
    """
    Inicializa o modelo de embeddings da OpenAI.
    
    Embeddings convertem texto em vetores numéricos,
    permitindo busca semântica por similaridade.
    """
    if "OPENAI_API_KEY" not in os.environ:
        raise RuntimeError("Define a variável de ambiente OPENAI_API_KEY.")
    
    return OpenAIEmbeddings(model="text-embedding-3-small")


def get_vector_store(embeddings: OpenAIEmbeddings) -> InMemoryVectorStore:
    """
    Inicializa o vector store em memória.
    
    O vector store armazena os embeddings dos documentos
    e permite busca por similaridade.
    """
    return InMemoryVectorStore(embeddings)


def load_and_split_documents(url: str = BLOG_URL) -> list:
    """
    Carrega e divide um documento web em chunks.
    
    Passos:
    1. WebBaseLoader carrega o HTML da URL
    2. BeautifulSoup filtra apenas o conteúdo relevante
    3. RecursiveCharacterTextSplitter divide em chunks menores
    
    Args:
        url: URL do documento a carregar
        
    Returns:
        Lista de Document chunks prontos para indexar
    """
    print(f"📄 A carregar documento de: {url}")
    
    # Filtrar apenas o conteúdo principal do blog (título, header, conteúdo)
    bs4_strainer = bs4.SoupStrainer(
        class_=("post-title", "post-header", "post-content")
    )
    
    # Carregar o documento
    loader = WebBaseLoader(
        web_paths=(url,),
        bs_kwargs={"parse_only": bs4_strainer},
    )
    docs = loader.load()
    
    print(f"   Total de caracteres: {len(docs[0].page_content)}")
    
    # Dividir em chunks para melhor indexação e retrieval
    # chunk_size: tamanho máximo de cada chunk (em caracteres)
    # chunk_overlap: sobreposição entre chunks para manter contexto
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True,  # Guardar posição original
    )
    
    all_splits = text_splitter.split_documents(docs)
    print(f"   Dividido em {len(all_splits)} chunks")
    
    return all_splits


def index_documents(
    vector_store: InMemoryVectorStore, 
    documents: list
) -> list[str]:
    """
    Indexa documentos no vector store.
    
    Cada documento é convertido em embedding e armazenado,
    permitindo depois busca por similaridade semântica.
    
    Args:
        vector_store: O vector store onde indexar
        documents: Lista de Document chunks
        
    Returns:
        Lista de IDs dos documentos indexados
    """
    print("📊 A indexar documentos no vector store...")
    document_ids = vector_store.add_documents(documents=documents)
    print(f"   {len(document_ids)} documentos indexados com sucesso!")
    return document_ids


# ============================================================
# Singleton Pattern - Mantém uma única instância do vector store
# ============================================================

_vector_store_instance: InMemoryVectorStore | None = None
_is_indexed: bool = False


def get_indexed_vector_store() -> InMemoryVectorStore:
    """
    Retorna o vector store já indexado (singleton).
    
    Na primeira chamada:
    1. Inicializa embeddings
    2. Cria vector store
    3. Carrega e indexa o documento
    
    Chamadas seguintes retornam a mesma instância.
    """
    global _vector_store_instance, _is_indexed
    
    if _vector_store_instance is None or not _is_indexed:
        print("\n🚀 A inicializar vector store...")
        
        # 1. Inicializar embeddings
        embeddings = get_embeddings()
        
        # 2. Criar vector store
        _vector_store_instance = get_vector_store(embeddings)
        
        # 3. Carregar e indexar documentos
        documents = load_and_split_documents()
        index_documents(_vector_store_instance, documents)
        
        _is_indexed = True
        print("✅ Vector store pronto!\n")
    
    return _vector_store_instance


