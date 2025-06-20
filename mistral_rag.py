from mistralai import Mistral
import requests
import numpy as np
import faiss
import os
from getpass import getpass

api_key = getpass("Type your API Key")
client = Mistral(api_key=api_key)

# Read the essay from a local file
with open('essay.txt', 'r') as f:
    text = f.read()

# Test the connection
try:
    response = client.chat.complete(
        model="mistral-tiny",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    print("Successfully connected to Mistral AI!")
    print("Response:", response.choices[0].message.content)
except Exception as e:
    print("Error connecting to Mistral AI:", str(e))

chunk_size = 2048
chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
print(f"Number of chunks: {len(chunks)}")

def get_text_embedding(input):
    embeddings_batch_response = client.embeddings.create(
        model="mistral-embed",
        inputs=input
    )
    return embeddings_batch_response.data[0].embedding

text_embeddings = np.array([get_text_embedding(chunk) for chunk in chunks])

# Create FAISS index
d = text_embeddings.shape[1]  # dimension of embeddings
index = faiss.IndexFlatL2(d)
index.add(text_embeddings)

# Example question
question = "What is the relationship between beauty and kitsch according to the text?"
question_embedding = np.array([get_text_embedding(question)])

# Search for similar chunks
k = 2  # number of similar chunks to retrieve
D, I = index.search(question_embedding, k)  # D = distances, I = indices
retrieved_chunks = [chunks[i] for i in I[0]]

# Create prompt with context
prompt = f"""
Context information is below.
---------------------
{retrieved_chunks}
---------------------
Given the context information and not prior knowledge, answer the query.
Query: {question}
Answer:
"""

# Generate response using Mistral
response = client.chat.complete(
    model="mistral-tiny",
    messages=[{"role": "user", "content": prompt}]
)
print("\nQuestion:", question)
print("\nRetrieved chunks:", retrieved_chunks)
print("\nAnswer:", response.choices[0].message.content) 