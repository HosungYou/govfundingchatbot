import streamlit as st
import os
from dotenv import load_dotenv
from datetime import date

# Core LCEL imports
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser

# OpenAI and Qdrant imports
from langchain_openai.chat_models import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore

load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY", "")
qdrant_url = os.getenv("QDRANT_URL", "")
qdrant_api_key = os.getenv("QDRANT_API_KEY", "")

today_date_str = date.today().isoformat()

# Use OpenAI embeddings
embeddings = OpenAIEmbeddings(
    openai_api_key=openai_key,
    model="text-embedding-ada-002"
)

# Initialize QdrantVectorStore
vectorstore = QdrantVectorStore.from_existing_collection(
    embedding=embeddings,
    collection_name="my-grants-collection",
    url=qdrant_url,
    api_key=qdrant_api_key
)

# Create retriever
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

# Define prompt template with date
system_template_raw = """You are a helpful RAG-based assistant.
Today's date is __TODAY_DATE__.

Based on the following context:
{context}

Answer this question:
Question: {query}

Please respond in English.
"""
system_template_string = system_template_raw.replace("__TODAY_DATE__", today_date_str)
prompt = ChatPromptTemplate.from_template(system_template_string)

# Create ChatOpenAI model
chat_model = ChatOpenAI(
    openai_api_key=openai_key,
    temperature=0,
    model_name="gpt-4o"
)

# Output parser
output_parser = StrOutputParser()

# Helper function to format retrieved documents
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# Define the RAG chain using LCEL
rag_chain = (
    {"context": retriever | format_docs, "query": RunnablePassthrough()}
    | prompt
    | chat_model
    | output_parser
)

def main():
    st.title("Grants Q&A Chatbot")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    user_input = st.text_input("Enter your question:")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.spinner("Querying..."):
            # Run the query
            answer = rag_chain.invoke(user_input)
            
            # Get source documents with metadata
            source_docs = retriever.invoke(user_input)

        st.session_state.messages.append({"role": "assistant", "content": answer})

        # Display information more clearly
        st.markdown("### Related Funding Opportunities")
        if source_docs:
            for i, doc in enumerate(source_docs, start=1):
                metadata = doc.metadata
                title = metadata.get("title", "No title available")
                opp_num = metadata.get("opportunity_number", "No number available")
                agency = metadata.get("agency", "Agency unknown")
                
                st.markdown(f"**{i}. {title}**")
                st.markdown(f"Agency: {agency}")
                st.markdown(f"Opportunity Number: {opp_num}")
                
                # Add URL if available - more prominent display
                url = metadata.get("url", "")
                if url:
                    if '/pubs/' in url:
                        st.markdown(f"📄 **[View Official Solicitation Document]({url})**")
                    else:
                        st.markdown(f"🔗 **[View on NSF Website]({url})**")
                
                with st.expander("View Detailed Information"):
                    st.markdown(f"Close Date: {metadata.get('close_date', 'Information not available')}")
                    st.markdown(f"Award Ceiling: {metadata.get('award_ceiling', 'Information not available')}")
                    st.markdown("Description:")
                    st.write(doc.page_content)
        else:
            st.info("No related funding opportunities found.")

    for msg in st.session_state.messages:
        st.write(f"**{msg['role']}:** {msg['content']}")

if __name__ == "__main__":
    main()
