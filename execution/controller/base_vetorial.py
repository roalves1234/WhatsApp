"""
Módulo responsável por construir e persistir a base vetorial FAISS
a partir do texto da base de conhecimento.

Utiliza RecursiveCharacterTextSplitter com separadores de parágrafo
para garantir que chunks respeitem quebras naturais do texto.
"""

import os
from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from loguru import logger

# Caminho onde o índice FAISS será salvo no disco
_CAMINHO_FAISS = Path("base_conhecimento.faiss")

# Configurações dos chunks
_CHUNK_SIZE = 400
_CHUNK_OVERLAP = 80

# Separadores em ordem de prioridade: parágrafo > quebra de linha > espaço > caractere
_SEPARADORES = ["\n\n", "\n", " ", ""]


def construir_base_vetorial(texto: str) -> None:
    """
    Divide o texto em chunks respeitando parágrafos inteiros e cria
    uma base vetorial FAISS salva em disco.

    Args:
        texto: Conteúdo completo da base de conhecimento.
    """
    if not texto.strip():
        logger.warning("BASE VETORIAL | Texto vazio — índice FAISS não será gerado")
        return

    splitter = RecursiveCharacterTextSplitter(
        separators=_SEPARADORES,
        chunk_size=_CHUNK_SIZE,
        chunk_overlap=_CHUNK_OVERLAP,
        length_function=len,
    )

    chunks = splitter.split_text(texto)
    logger.info("BASE VETORIAL | Chunks gerados | total={n}", n=len(chunks))

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=os.getenv("OPENAI_API_KEY", ""),
    )

    indice = FAISS.from_texts(chunks, embeddings)
    indice.save_local(str(_CAMINHO_FAISS))

    logger.info(
        "BASE VETORIAL | Índice salvo | caminho={caminho} | chunks={n}",
        caminho=_CAMINHO_FAISS,
        n=len(chunks),
    )
