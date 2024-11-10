import os
import openai
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance

team_tag = 1

def gather_code_structure(base_dir):
    code_structure = {}
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    code_structure[file_path] = f.read()
    return code_structure

codebase_structure = gather_code_structure("blueprints")

codebase_structure.items()

openai.api_key = 'XYZ'

client = OpenAI()

def get_embedding(text):
    response = client.embeddings.create(input=[text], model="text-embedding-ada-002") 
    return response.data[0].embedding

embeddings = {}
for file_path, content in codebase_structure.items():
    content_embedding = get_embedding(content)
    embeddings[file_path] = {
        "content": content,
        "content_embedding": content_embedding,
    }

Qdart_client = QdrantClient("http://localhost:6333")

collection_name = "test"
vector_size = len(embeddings[list(embeddings.keys())[0]]["content_embedding"])

try:
    Qdart_client.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
    )
    print(f"Collection '{collection_name}' created with vector size {vector_size}.")
except Exception as e:
    print("Error creating collection:", e)

points = [
    PointStruct(
        id=i+1,
        vector=embedding_data["content_embedding"],
        payload={"file_path": file_path,
                 "team": team_tag}
    ) for i, (file_path, embedding_data) in enumerate(embeddings.items())
]

try:
    Qdart_client.upsert( 
        collection_name='test',
        points=points
        
    )
    print("Points successfully upserted.")
except Exception as e:
    print("Error upserting points:", e)

Qdart_client = QdrantClient("http://localhost:6333")

collection_name = "test"
vector_size = len(embeddings[list(embeddings.keys())[0]]["content_embedding"])

try:
    Qdart_client.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
    )
    print(f"Collection '{collection_name}' created with vector size {vector_size}.")
except Exception as e:
    print("Error creating collection:", e)

points = [
    PointStruct(
        id=i+1,
        vector=embedding_data["content_embedding"],
        payload={"file_path": file_path}
    ) for i, (file_path, embedding_data) in enumerate(embeddings.items())
]

try:
    Qdart_client.upsert( 
        collection_name='test',
        points=points
        
    )
    print("Points successfully upserted.")
except Exception as e:
    print("Error upserting points:", e)

def query_codebase(query, team=None, top_k=5):
    query_embedding = get_embedding(query)
    search_filters = None

    # Apply team filter if specified
    if team:
        search_filters = {"must": [{"key": "team", "match": {"value": team}}]}

    search_results = qdrant_client.search(
        collection_name="test",
        query_vector=query_embedding,
        limit=top_k,
        filter=search_filters  
    )

    results = []
    for result in search_results:
        file_path = result.payload['file_path']
        results.append((file_path, result.score))

    return results


def generate_answer(query, team=None):
    relevant_files = query_codebase(query, team=team)
    context = "\n\n".join([f"File: {file_path}\nCode:\n{codebase_structure[file_path]}" for file_path, _ in relevant_files])

    prompt = f"Answer the following question based on the provided context.\n\nContext:\n{context}\n\nQuestion: {query}\n\nAnswer:"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=512
    )

    return response['choices'][0]['message']['content']


if __name__ == "__main__":
    question = "Give me all the functions where I am using the @shared_task decorator with path"
    answer = generate_answer(question)
    print(answer)

