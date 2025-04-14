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

# API 키와 엔드포인트 가져오기
try:
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
    
    # Connection successful
    connection_error = None
    
except Exception as e:
    connection_error = str(e)

# Funding agency information
FUNDING_AGENCIES = [
    {
        "name": "National Science Foundation (NSF)",
        "description": "Supports research and education in science and engineering.",
        "example_query": "What are the latest NSF grants for AI research?",
    },
    {
        "name": "Department of Health and Human Services (HHS)",
        "description": "Funds health-related research and public health initiatives.",
        "example_query": "Are there any HHS grants for rural healthcare?",
    },
    {
        "name": "National Institutes of Health (NIH)",
        "description": "Focuses on medical and health-related research.",
        "example_query": "What NIH funding opportunities are available for cancer research?",
    },
    {
        "name": "Department of Energy (DOE)",
        "description": "Supports research in energy technologies and basic science.",
        "example_query": "Find DOE grants for renewable energy projects.",
    },
    {
        "name": "Department of Defense (DOD)",
        "description": "Funds research in defense, security, and military applications.",
        "example_query": "What are the recent DOD funding opportunities for cybersecurity?",
    },
]

# Query guidelines
QUERY_GUIDELINES = [
    "**Be specific about the agency**: Mention the specific funding agency you're interested in (e.g., NSF, NIH, DOE).",
    "**Include research area**: Specify the field or topic of research you're looking for funding in.",
    "**Mention timing**: Ask about recent, upcoming, or currently open funding opportunities.",
    "**Ask about eligibility**: Inquire about who can apply for specific grants.",
    "**Request details**: Ask for specific details like award amounts, deadlines, or application requirements.",
]

# Example queries
EXAMPLE_QUERIES = [
    "What are the most recent NSF funding opportunities for early-career researchers?",
    "Tell me about NIH grants for cancer research with deadlines in the next 6 months.",
    "Are there any DOE funding opportunities for renewable energy projects over $1 million?",
    "What HHS grants are available for community health initiatives in rural areas?",
    "Find NSF grants related to artificial intelligence and machine learning.",
]

def main():
    st.title("Grants.gov Funding Opportunities Assistant")
    
    # Show connection error if any
    if connection_error:
        st.error(f"""
        ### API Connection Error
        
        There was a problem connecting to the required APIs. Please check your configuration.
        
        Error details: {connection_error}
        """)
        st.stop()
    
    # Initialize session state for chat messages
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Check if there are no messages (first visit)
    if not st.session_state.messages:
        # Display welcome information
        with st.container():
            st.markdown("## Welcome to the Grants.gov Funding Assistant")
            st.markdown("""
            This chatbot can help you discover funding opportunities from various government agencies.
            You can ask about grants, eligibility requirements, deadlines, and application processes.
            """)
            
            # Display agency information
            st.markdown("### Available Funding Agencies")
            cols = st.columns(2)
            for i, agency in enumerate(FUNDING_AGENCIES):
                with cols[i % 2]:
                    with st.expander(agency["name"]):
                        st.markdown(agency["description"])
                        st.markdown(f"**Example query:** _{agency['example_query']}_")
            
            # Display query guidelines
            st.markdown("### How to Ask Effective Questions")
            for guideline in QUERY_GUIDELINES:
                st.markdown(f"- {guideline}")
            
            # Display example queries section
            st.markdown("### Try These Example Queries")
            for query in EXAMPLE_QUERIES:
                if st.button(query):
                    st.session_state.messages.append({"role": "user", "content": query})
                    with st.spinner("Querying..."):
                        # Run the query
                        answer = rag_chain.invoke(query)
                        
                        # Get source documents with metadata
                        source_docs = retriever.invoke(query)
                    
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    st.rerun()
    
    # Display chat messages
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])
        
        # If this is the last assistant message, show related funding opportunities
        if msg["role"] == "assistant" and msg == st.session_state.messages[-1]:
            user_query = st.session_state.messages[-2]["content"]
            source_docs = retriever.invoke(user_query)
            
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
    
    # User input
    if user_input := st.chat_input("Ask about funding opportunities..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.spinner("Querying..."):
            # Run the query
            answer = rag_chain.invoke(user_input)
            
            # Get source documents with metadata
            source_docs = retriever.invoke(user_input)
        
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.rerun()

if __name__ == "__main__":
    main()
