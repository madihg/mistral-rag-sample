from flask import Flask, render_template, request, jsonify
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import numpy as np
import os
from dotenv import load_dotenv
import traceback
from flask_cors import CORS
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize Mistral client with error handling
try:
    api_key = os.getenv('MISTRAL_API_KEY')
    if not api_key:
        raise ValueError("MISTRAL_API_KEY environment variable is not set")
    client = MistralClient(api_key=api_key)
    logger.info("Mistral client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Mistral client: {str(e)}")
    client = None

# Load and process the text
try:
    with open('essay.txt', 'r') as f:
        text = f.read()
    logger.info("Successfully loaded essay.txt")
except FileNotFoundError:
    logger.error("essay.txt file not found")
    raise FileNotFoundError("essay.txt file not found. Please ensure it exists in the project directory.")

# Create chunks
chunk_size = 2048
chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
logger.info(f"Created {len(chunks)} chunks from the text")

def create_text_embeddings(texts):
    """Create embeddings for a list of texts using Mistral's embedding model."""
    try:
        if not client:
            raise ValueError("Mistral client not initialized")
        
        embeddings = []
        for text in texts:
            response = client.embeddings(
                model="mistral-embed",
                input=text
            )
            embeddings.append(response.data[0].embedding)
        return np.array(embeddings)
    except Exception as e:
        logger.error(f"Error creating embeddings: {str(e)}")
        raise

def find_nearest_neighbors(query_embedding, embeddings, k=3):
    """Find k nearest neighbors using cosine similarity."""
    try:
        # Normalize the embeddings
        query_norm = query_embedding / np.linalg.norm(query_embedding)
        embeddings_norm = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        
        # Calculate cosine similarity
        similarities = np.dot(embeddings_norm, query_norm)
        
        # Get indices of top k similar chunks
        top_k_indices = np.argsort(similarities)[-k:][::-1]
        return top_k_indices
    except Exception as e:
        logger.error(f"Error finding nearest neighbors: {str(e)}")
        raise

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    try:
        if not client:
            return jsonify({"error": "Mistral client not initialized"}), 500

        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({"error": "No question provided"}), 400

        question = data['question']
        logger.info(f"Received question: {question}")

        # Read the essay
        try:
            with open('essay.txt', 'r') as f:
                essay = f.read()
        except Exception as e:
            logger.error(f"Error reading essay.txt: {str(e)}")
            return jsonify({"error": "Could not read essay file"}), 500

        # Split essay into chunks
        chunks = [essay[i:i+1000] for i in range(0, len(essay), 1000)]
        logger.info(f"Created {len(chunks)} chunks from essay")

        # Create embeddings for chunks
        try:
            chunk_embeddings = create_text_embeddings(chunks)
            logger.info("Created embeddings for chunks")
        except Exception as e:
            logger.error(f"Error creating chunk embeddings: {str(e)}")
            return jsonify({"error": "Failed to create embeddings"}), 500

        # Create embedding for the question
        try:
            question_embedding = create_text_embeddings([question])[0]
            logger.info("Created embedding for question")
        except Exception as e:
            logger.error(f"Error creating question embedding: {str(e)}")
            return jsonify({"error": "Failed to create question embedding"}), 500

        # Find most similar chunks
        try:
            similar_indices = find_nearest_neighbors(question_embedding, chunk_embeddings)
            similar_chunks = [chunks[i] for i in similar_indices]
            logger.info(f"Found {len(similar_chunks)} similar chunks")
        except Exception as e:
            logger.error(f"Error finding similar chunks: {str(e)}")
            return jsonify({"error": "Failed to find similar chunks"}), 500

        # Create context from similar chunks
        context = "\n".join(similar_chunks)

        # Create chat messages
        messages = [
            ChatMessage(role="system", content="You are a helpful AI assistant. Use the provided context to answer questions accurately. If the context doesn't contain enough information, say so."),
            ChatMessage(role="user", content=f"Context: {context}\n\nQuestion: {question}")
        ]

        # Get response from Mistral
        try:
            chat_response = client.chat(
                model="mistral-tiny",
                messages=messages
            )
            logger.info("Received response from Mistral")
        except Exception as e:
            logger.error(f"Error getting response from Mistral: {str(e)}")
            return jsonify({"error": "Failed to get response from Mistral"}), 500

        return jsonify({"answer": chat_response.choices[0].message.content})

    except Exception as e:
        logger.error(f"Unexpected error in /ask endpoint: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

# For local development
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True) 