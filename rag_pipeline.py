import os
from dotenv import load_dotenv
from datetime import date

# Core LCEL imports
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser

# Previous imports needed
from langchain_openai.chat_models import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
# Remove RetrievalQA import as it's replaced by LCEL
# from langchain.chains import RetrievalQA

def main():
    """
    Sample RAG pipeline using LCEL for robust input handling.
    Injecting date into prompt using .replace().
    Initializing QdrantVectorStore by passing connection parameters.
    """
    load_dotenv()
    openai_key = os.getenv("OPENAI_API_KEY", "")
    qdrant_url = os.getenv("QDRANT_URL", "")
    qdrant_api_key = os.getenv("QDRANT_API_KEY", "")

    today_date_str = date.today().isoformat()

    # Use openai embeddings
    embeddings_object = OpenAIEmbeddings(
        openai_api_key=openai_key,
        model="text-embedding-ada-002"
    )

    # Initialize QdrantVectorStore by passing connection details directly
    vectorstore = QdrantVectorStore.from_existing_collection(
        embedding=embeddings_object,
        collection_name="my-grants-collection",
        url=qdrant_url,
        api_key=qdrant_api_key
    )

    # --- Create Retriever ---
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    # --- Prompt Definition ---
    # Define template with a unique placeholder for the date
    # This template expects 'context' and 'query' inputs
    system_template_raw = """You are a helpful RAG-based assistant.
Today's date is __TODAY_DATE__.

Based on the following context:
{context}

Answer this question:
Question: {query}

Please respond in English.
"""
    # Replace only the unique date placeholder
    system_template_string = system_template_raw.replace("__TODAY_DATE__", today_date_str)
    # Create the ChatPromptTemplate object directly from the final string
    prompt = ChatPromptTemplate.from_template(system_template_string)

    # ChatOpenAI Language Model
    chat_model = ChatOpenAI(
        openai_api_key=openai_key,
        temperature=0,
        model_name="gpt-4o"
    )

    # --- Output Parser ---
    output_parser = StrOutputParser()

    # --- Helper function to format retrieved documents ---
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # --- Define the RAG chain using LCEL ---
    # This explicitly defines the data flow:
    # 1. The input query is passed to both the retriever and kept as 'query'.
    # 2. The retriever fetches docs, which are then formatted by format_docs.
    # 3. The formatted 'context' and original 'query' are fed into the prompt.
    # 4. The formatted prompt goes to the chat model.
    # 5. The model's output is parsed by the StrOutputParser.
    rag_chain = (
        {"context": retriever | format_docs, "query": RunnablePassthrough()} # Fetches context, passes query through
        | prompt # Fills prompt with context and query
        | chat_model # Sends prompt to LLM
        | output_parser # Parses LLM output
    )

    print("[INFO] RAG pipeline (LCEL) set up completed.\n")

    sample_query = "Tell me about NSF grants for AI research."
    print(f"[INFO] Running sample query: {sample_query}")

    # --- Invoke the LCEL chain ---
    # LCEL chains are invoked with the initial input expected by the first part
    # In this case, RunnablePassthrough() for 'query' means it expects the raw query string.
    answer = rag_chain.invoke(sample_query)

    # --- Get source documents separately if needed ---
    # LCEL chains focus on the primary output. For sources, run the retriever again.
    source_docs = retriever.invoke(sample_query)

    print("\n[SAMPLE ANSWER]\n", answer)
    print(f"\n[DEBUG] Source docs returned: {len(source_docs)}")
    # Optional: print source docs content
    # for i, doc in enumerate(source_docs):
    #     print(f"\n--- Source Doc {i+1} ---")
    #     print(doc.page_content)
    #     print(doc.metadata)


if __name__ == "__main__":
    main()
