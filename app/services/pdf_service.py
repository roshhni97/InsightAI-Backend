from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from app.services.rag_service import vectorstore, get_summary, get_key_topics, get_document_structure

def process_pdf(file_path: str):
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(documents)
    cleaned_chunks = []
    for doc in chunks:
        doc.metadata.pop('id', None)        # Remove 'id' if present
        doc.metadata.pop('uuid', None)
        cleaned_chunks.append(doc)

    vectorstore.add_documents(documents=cleaned_chunks)
    # give summary , key topics, document structure with the help of rag_service
    summary = get_summary(chunks)
    key_topics = get_key_topics(chunks)
    document_structure = get_document_structure(chunks)

    return {
        "summary": summary,
        "key_topics": key_topics,
        "document_structure": document_structure
    }

