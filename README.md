# Government Funding Chatbot (govfundingchatbot)

## Project Overview

This project is an RAG (Retrieval-Augmented Generation) based chatbot system designed to help users easily search and explore grant and funding opportunities from various US government agencies (e.g., NSF, HHS, NIH, DOE, DOD). Users can ask questions in natural language to get relevant funding information and links to related solicitation documents or websites.

## Key Features

* **Data Collection:** Periodically gathers and merges the latest funding opportunity data from `grants.gov` using their APIs and XML extracts (`NSF Funding.py`).
* **RAG Pipeline:** Stores the collected data in a vector database (Qdrant) and utilizes LangChain with an OpenAI model (GPT-4o) to retrieve the most relevant information based on user queries and generate answers (`rag_pipeline.py`).
* **Chatbot Interface:** Provides an intuitive web-based interface using Streamlit, allowing users to ask questions about funding opportunities and view answers along with related details (`streamlit_chatbot.py`).
* **Source Attribution:** Clearly presents source information alongside chatbot answers, including the title, agency, opportunity number, close date, and links for related funding opportunities.

## System Architecture (Estimated)

1.  **Data Fetching (`NSF Funding.py`):**
    * Retrieves a list of funding opportunities using the `grants.gov` `search2` API.
    * Fetches detailed information for each opportunity using the `WorkspaceOpportunity` API.
    * Downloads and parses the latest XML dump from `grants.gov/xml-extract` to supplement information.
    * Saves the consolidated data into a `merged_data.json` file.
2.  **Data Processing & Storage (Estimated):**
    * Processes `merged_data.json` (or similar data) and stores it along with embeddings in a Qdrant vector database. (This step is necessary for the RAG pipeline but not explicitly shown in the provided code.)
3.  **RAG Pipeline (`rag_pipeline.py`):**
    * When a user query is received, it retrieves relevant documents from Qdrant.
    * Combines the retrieved documents (context) and the user query into a prompt template.
    * Sends the prompt to the OpenAI model (GPT-4o).
    * Returns the model-generated answer to the user.
4.  **Chatbot UI (`streamlit_chatbot.py`):**
    * Runs a Streamlit application to provide the user interface.
    * Takes user input and calls the backend RAG pipeline.
    * Formats and displays the answer along with retrieved related funding opportunity details.

## Installation and Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/HosungYou/govfundingchatbot.git](https://github.com/HosungYou/govfundingchatbot.git)
    cd govfundingchatbot
    ```
2.  **Install required libraries:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: A `requirements.txt` file is needed in the repository. Based on the provided code, necessary libraries include `python-dotenv`, `langchain-core`, `langchain-openai`, `langchain-qdrant`, `requests`, `beautifulsoup4`, `streamlit`, etc.)*
3.  **Set up environment variables:**
    * Create a `.env` file in the project root directory and add the following information:
        ```
        OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
        QDRANT_URL="YOUR_QDRANT_URL"
        QDRANT_API_KEY="YOUR_QDRANT_API_KEY"
        ```
    * Ensure you have a running Qdrant instance and the specified collection (`my-grants-collection`) is ready.

## Usage

1.  **Run Data Collection (if needed):**
    * To fetch the latest funding data, run `NSF Funding.py`. (A subsequent script to load this data into Qdrant might be required.)
    ```bash
    python "NSF Funding.py"
    ```
2.  **Run the Chatbot:**
    ```bash
    streamlit run streamlit_chatbot.py
    ```
3.  Access the Streamlit app via your web browser (typically at `http://localhost:8501`) to use the chatbot.
