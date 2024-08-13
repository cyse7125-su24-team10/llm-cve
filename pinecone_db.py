import os
import json
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain.vectorstores import Pinecone as LangchainPinecone  # Renamed to avoid conflicts

load_dotenv()

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
                cve_id = data['cveMetadata']['cveId']
                description = data['containers']['cna']['descriptions'][0]['value']
                doc = CustomDocument(page_content=description, metadata={"cve_id": cve_id})
                documents.append(doc)
    return documents

# Initialize Pinecone
pinecone_api_key = os.getenv("PINECONE_API_KEY")
cloud = os.getenv("PINECONE_CLOUD", "aws")
region = os.getenv("PINECONE_REGION", "us-east-1")

spec = ServerlessSpec(cloud=cloud, region=region)
pc = Pinecone(api_key=pinecone_api_key)

# Initialize Pinecone index
index_name = "cve"
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name, 
        dimension=384,  # 384 is the dimension for BAAI/bge-small-en-v1.5
        metric='cosine',  # Use the appropriate metric for your use case
        spec=spec
    )

# Load and prepare documents
data_dir = 'data'
embeddings = HuggingFaceBgeEmbeddings(
    model_name="BAAI/bge-small-en-v1.5",
    model_kwargs={'device':'cpu'},
    encode_kwargs={'normalize_embeddings':True}
)
docs = load_json_files(data_dir)

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
final_documents = text_splitter.split_documents(docs)

# Create or update Pinecone vectorstore using LangChain's Pinecone wrapper
vectorstore = LangchainPinecone.from_documents(
    documents=final_documents, 
    embedding=embeddings, 
    index_name=index_name
)

print("Pinecone index updated successfully.")
