import os
import subprocess
import openai
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

# Configuration
REPO_PATH = "/path/to/your/local/repo"  
QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "test"
OPENAI_API_KEY = "your-openai-api-key"

# Initialize clients
qdrant_client = QdrantClient(QDRANT_URL)
openai.api_key = OPENAI_API_KEY

def pull_latest_changes():
    """Pulls latest changes from GitHub."""
    subprocess.run(["git", "fetch"], cwd=REPO_PATH)
    subprocess.run(["git", "pull"], cwd=REPO_PATH)

def gather_changed_files():
    """Returns a list of changed Python files since the last commit."""
    result = subprocess.run(["git", "diff", "--name-only", "HEAD~1"], cwd=REPO_PATH, capture_output=True, text=True)
    changed_files = result.stdout.splitlines()
    return [f for f in changed_files if f.endswith('.py')]

def gather_code_structure(files):
    """Reads content from provided Python files."""
    code_structure = {}
    for file in files:
        with open(os.path.join(REPO_PATH, file), 'r') as f:
            code_structure[file] = f.read()
    return code_structure

def get_embedding(text):
    """Generates embedding for given text."""
    response = openai.Embedding.create(input=[text], model="text-embedding-ada-002")
    return response['data'][0]['embedding']

def update_embeddings_in_qdrant(changed_code):
    """Updates Qdrant collection with new embeddings."""
    points = []
    for file_path, content in changed_code.items():
        embedding = get_embedding(content)
        points.append(
            PointStruct(
                id=file_path,  # Using file path as a unique ID
                vector=embedding,
                payload={"file_path": file_path}
            )
        )
    
    # Upsert updated points to Qdrant
    qdrant_client.upsert(collection_name=COLLECTION_NAME, points=points)

def main():
    # Step 1: Pull latest changes
    pull_latest_changes()

    # Step 2: Gather changed Python files
    changed_files = gather_changed_files()
    if not changed_files:
        print("No changes detected.")
        return

    # Step 3: Read code content for changed files
    changed_code = gather_code_structure(changed_files)

    # Step 4: Update embeddings in Qdrant
    update_embeddings_in_qdrant(changed_code)
    print("Embeddings updated successfully for changed files.")

if __name__ == "__main__":
    main()
