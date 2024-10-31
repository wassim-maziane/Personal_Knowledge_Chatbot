from langchain_core.documents import Document
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    UnstructuredHTMLLoader,
)
from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain_qdrant import QdrantVectorStore
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
embeddings = OllamaEmbeddings(model="nomic-embed-text")
client = QdrantClient(host="localhost", port=6333)
collection_name = "userdocs_collection"
# client.create_collection(
#    collection_name=collection_name,
#    vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
# )
vectorstore = QdrantVectorStore(client, collection_name, embeddings)


def load_and_split_document(file_path: str) -> list[Document]:
    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith(".docx"):
        loader = Docx2txtLoader(file_path)
    elif file_path.endswith(".html"):
        loader = UnstructuredHTMLLoader(file_path)
    else:
        raise ValueError(f"Unsupported File Type: {file_path}")
    documents = loader.load()
    return text_splitter.split_documents(documents)


def index_doc_to_qdrant(file_path: str, session_id: str) -> bool:
    try:
        splits = load_and_split_document(file_path)
        for split in splits:
            split.metadata["session_id"] = session_id
        vectorstore.add_documents(splits)
        return True
    except Exception as e:
        print(f"Error indexing document: {e}")
        return False
