import logging
import os

from langchain.document_loaders import TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma


logger = logging.getLogger("vector_db_repository")
PERSIST_DIR = os.path.join(os.getcwd(), 'chroma-persist')
DOCUMENTS_DIR = os.path.join(os.getcwd(), 'assets/documents')


class KakaoApiDocumentRepository:
    db = Chroma(
        persist_directory=PERSIST_DIR,
        embedding_function=OpenAIEmbeddings(),
        collection_name='kakao-api-explain',
    )
    retriever = db.as_retriever()

    def __init__(self):
        for dirpath, dirnames, filenames in os.walk(DOCUMENTS_DIR):
            for filename in filenames:
                if filename.endswith('.txt'):
                    file_path = os.path.join(dirpath, filename)
                    self.upload_embedding_from_file(file_path)

    def query_db(self, query: str, use_retriever: bool = False) -> list[str]:
        if use_retriever:
            docs = KakaoApiDocumentRepository.retriever.get_relevant_documents(query)
        else:
            docs = KakaoApiDocumentRepository.db.similarity_search(query)

        str_docs = [doc.page_content for doc in docs]
        return str_docs

    def upload_embedding_from_file(self, file_path):
        document = TextLoader(file_path).load()

        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        docs = text_splitter.split_documents(document)

        KakaoApiDocumentRepository.db.add_documents(
            documents=docs,
            embedding_function=OpenAIEmbeddings(),
            collection_name='kakao-api-explain',
        )
        logger.info('db upload success')
