import streamlit as st
import os
import json
from langchain_groq import ChatGroq
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

import time

from dotenv import load_dotenv
load_dotenv()

## Load the Groq API key
groq_api_key = os.getenv("groq_api_key")

# Custom document class to match expected format
class CustomDocument:
    def __init__(self, page_content, metadata):
        self.page_content = page_content
        self.metadata = metadata

# Function to load and parse JSON files from data directory
def load_json_files(data_dir):
    documents = []
    for filename in os.listdir(data_dir):
        if filename.endswith('.json'):
            with open(os.path.join(data_dir, filename)) as f:
                data = json.load(f)
                # Extract and format the relevant data fields
                cve_id = data['cveMetadata']['cveId']
                description = data['containers']['cna']['descriptions'][0]['value']
                doc = CustomDocument(page_content=description, metadata={"cve_id": cve_id})
                documents.append(doc)
    return documents

# Load and prepare documents
data_dir = 'data'  # specify the path to your data directory
if "vector" not in st.session_state:
    ## Embedding Using Huggingface
    # huggingface_embeddings=
    # retriever=vectorstore.as_retriever(search_type="similarity",search_kwargs={"k":3})
    # print(retriever)
    st.session_state.embeddings = HuggingFaceBgeEmbeddings(
    model_name="BAAI/bge-small-en-v1.5",      #sentence-transformers/all-MiniLM-l6-v2
    model_kwargs={'device':'cpu'},
    encode_kwargs={'normalize_embeddings':True}

)
    st.session_state.docs = load_json_files(data_dir)

    st.session_state.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    st.session_state.final_documents = st.session_state.text_splitter.split_documents(st.session_state.docs)
    st.session_state.vectors = FAISS.from_documents(st.session_state.final_documents, st.session_state.embeddings)

# Streamlit UI
st.title("ChatGroq Demo with CVE Data")
llm = ChatGroq(groq_api_key=groq_api_key, model_name=os.getenv("groq_model_name"))

prompt_template = """
Answer the questions based on the provided context only.
Please provide the most accurate response based on the question.
<context>
{context}
<context>
Questions: {input}
"""

prompt = ChatPromptTemplate.from_template(prompt_template)
document_chain = create_stuff_documents_chain(llm, prompt)
retriever = st.session_state.vectors.as_retriever()
retrieval_chain = create_retrieval_chain(retriever, document_chain)

user_prompt = st.text_input("prompt")

if user_prompt:
    start = time.process_time()
    response = retrieval_chain.invoke({"input": user_prompt})
    st.write("Response time: ", time.process_time() - start)
    st.write(response['answer'])

    with st.expander("Source Documents"):
        for doc in response["context"]:
            st.write(doc.page_content)
            st.write("--------------------------------")
