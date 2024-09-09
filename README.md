# llm-cve

This project generates embeddings for CVE (Common Vulnerabilities and Exposures) descriptions, stores them in a Pinecone vector database, and provides a Streamlit interface for querying the data using a language model(llama3).

## Prerequisites

- Docker
- Python 3.9+ (if running locally)
- Pinecone API key
- Access to the BAAI/bge-small-en-v1.5 model
- Ollama installed with llama3.1.

## Project Structure

- `pinecone_db.py`: Script for generating embeddings and updating the Pinecone index
- `app.py`: Streamlit application for querying the CVE data
- `Dockerfile`: Instructions for building the Docker image
- `data/`: Directory containing JSON files with sample CVE data
- `.env`: Environment file for storing API keys and configuration
- `requirements.txt`: List of Python dependencies

## Setup and Installation

### Local Setup

1. Clone this repository:
   ```
   git clone https://github.com/vk-NEU7/llm-cve.git
   cd llm-cve
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root and add your API keys:
   ```
   PINECONE_API_KEY=your_pinecone_api_key_here
   PINECONE_CLOUD=aws
   PINECONE_REGION=us-east-1
   LLM_HOST=http://localhost:11434
   ```

### Docker Setup

1. Build the Docker image:
   ```
   docker build -t cve-query-app .
   ```

2. Run the Docker container:
   ```
   docker run -p 8501:8501 --env-file .env cve-query-app
   ```

## Usage

### Generating Embeddings

1. Place your JSON files containing CVE data in the `data` directory.

2. Run the embedding generation script:
   ```
   python pinecone_db.py
   ```

### Running the Query Interface

1. Start the Streamlit app:
   ```
   streamlit run app.py
   ```
   Or if using Docker, the app will start automatically when you run the container.

2. Open a web browser and navigate to `http://localhost:8501`.

3. Enter your question in the text input field and press Enter to get a response.

## Customization

- To use a different embedding model, update the `model_name` in the `HuggingFaceBgeEmbeddings` initialization in both `pinecone_db.py` and `app.py`.
- Adjust the `chunk_size` and `chunk_overlap` in the `RecursiveCharacterTextSplitter` in `pinecone_db.py` to change how documents are split.
- Modify the Streamlit interface in `app.py` to add more features or change the layout.


## Contributing

We welcome contributions to improve the llm-cve project! If you'd like to contribute, please follow these steps:

1. Fork the Repository: Click the "Fork" button on the top right of the project page.
2. Create a Branch: Create a new branch for your changes.
3. Make Your Changes: Implement your changes and test thoroughly.
4. Submit a Pull Request: Open a Pull Request with a clear description of your changes.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
