from langchain_openai import AzureChatOpenAI
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_openai import AzureOpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.schema import Document

from app.services.supabase_client import supabase
from app.config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_DEPLOYMENT_NAME,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME,
    AZURE_OPENAI_EMBEDDING_API_KEY,
    AZURE_OPENAI_EMBEDDING_ENDPOINT
)

# Embeddings
embedding_model = AzureOpenAIEmbeddings(
    openai_api_key=AZURE_OPENAI_EMBEDDING_API_KEY,
    azure_endpoint=AZURE_OPENAI_EMBEDDING_ENDPOINT,
    deployment=AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME,
    openai_api_type="azure"
)

# Vector store
vectorstore = SupabaseVectorStore(
    client=supabase,
    embedding=embedding_model,
    table_name="documents",
)
retriever = vectorstore.as_retriever()

# LLM
llm = AzureChatOpenAI(
    openai_api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    deployment_name=AZURE_OPENAI_DEPLOYMENT_NAME,
    openai_api_type="azure",
    api_version=AZURE_OPENAI_API_VERSION
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever
)

# Utility: Combine chunks to feed to LLM
def _prepare_context(chunks: list[Document]) -> str:
    return "\n".join([doc.page_content for doc in chunks])

# Questions to ask the model
def get_summary(chunks: list[Document]) -> str:
    context = _prepare_context(chunks)
    question = "Can you provide a concise summary of the document in 4-5 lines?"
    return llm.invoke(f"{question}\n\nContext:\n{context}")

def get_key_topics(chunks: list[Document]) -> str:
    context = _prepare_context(chunks)
    question = "List the key topics or themes discussed in this document. Give the answer in a string comma separated listformat strically follow the example. Example: 'Topic 1, Topic 2, Topic 3'"
    return llm.invoke(f"{question}\n\nContext:\n{context}")

def get_document_structure(chunks) -> str:
    context = _prepare_context(chunks)
    question = "Describe the structure or organization of the document (e.g., sections, chapters, headings). Analyze the following document content and return a JSON array like this: '[{'struct': 'pages', 'value': 10}, {'struct': 'sections', 'value': 2}, {'struct': 'tables', 'value': 3}, {'struct': 'figures', 'value': 1}].' Use the actual values found in the document. Only return the JSON array. Don't include any other JSON\n like this. Strictly follow the example. "
    return llm.invoke(f"{question}\n\nContext:\n{context}")

def ask_question(question: str, top_k: int = 5) -> str:
    # Step 1: Retrieve relevant documents
    relevant_docs = retriever.get_relevant_documents(query=question, k=top_k)
    # Step 2: Prepare context from documents
    context = "\n\n".join([doc.page_content for doc in relevant_docs])

    # Step 3: Create a detailed system prompt
    system_prompt = (
        "You are an expert assistant. Use the following context from documents to answer the user's question.\n\n"
        f"Context is this :\n{context}\n\n"
        f"User Question: {question}\n\n"
        "Answer clearly and concisely based only on the context provided."
        "Don't include User Question and Answer keywords in the response."
        
    )
    # Step 4: Invoke LLM directly with the prompt
    response = llm.invoke(system_prompt)
    return response.content.strip()

