import streamlit as st
import os
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama

# Load environment variables from .env file
load_dotenv()

# Initialize Pinecone
pinecone_api_key = os.getenv("PINECONE_API_KEY")
index_name = "cve"

# Initialize Pinecone client
pc = Pinecone(api_key=pinecone_api_key)

# Initialize embeddings
embeddings = HuggingFaceBgeEmbeddings(
    model_name="BAAI/bge-small-en-v1.5",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)

# Initialize the ChatGroq model
# llm = ChatGroq(groq_api_key=os.getenv("groq_api_key"), model_name=os.getenv("groq_model_name"))
ollama_host = os.getenv("LLM_HOST")
print(f"Ollama host: {ollama_host}")
llm = Ollama(model="llama3" ,base_url=ollama_host)
print("LLM initialized")


# Initialize a LangChain object for retrieving information from Pinecone.
index = pc.Index(index_name)
vectorstore = PineconeVectorStore(index, embeddings, text_key="text")

# Initialize a LangChain object for chatting with the LLM
# with knowledge from Pinecone.
qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever()
)

# Streamlit UI
st.title("LLM-RAG Built on CVE Data")

# User input
user_prompt = st.text_input("Enter your question:")

if user_prompt:
    try:
        # Generate embeddings for the user's query
        query_embedding = embeddings.embed_query(user_prompt)
        
        # Query Pinecone
        results = index.query(vector=query_embedding, top_k=5, include_metadata=True)
        
        # Format the results
        context = []
        for result in results['matches']:
            metadata = result.get('metadata', {})
            cve_id = metadata.get('cve_id', 'N/A')
            description = metadata.get('text', 'No description available')
            context.append(f"CVE: {cve_id}\nDescription: {description}")
        
        context_str = "\n\n".join(context)
        
        # Prepare the prompt for the LLM
        full_prompt = f"Context:\n{context_str}\n\nQuestion: {user_prompt}\n\nAnswer:"
        
        # Query the LLM with the context and user's input
        result = qa.invoke(full_prompt)
        
        st.write("Response:")
        st.write(result['result'])
    
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.error(f"Exception details: {str(e)}")