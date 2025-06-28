import os
from dotenv import load_dotenv
import genai
import faiss
import time
from google import genai
from google.genai.types import EmbedContentConfig, GenerateContentConfig
from flask import Flask, request, render_template
import numpy as np

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

def load_docs(folder="docs"):
    """Load all .txt files from the specified folder"""
    docs, files = [], []
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f"Created {folder} folder. Please add .txt files to it.")
        return docs, files
    
    for f in os.listdir(folder):
        if f.endswith(".txt"):
            try:
                with open(os.path.join(folder, f), encoding="utf-8") as fp:
                    content = fp.read().strip()
                    if content:  # Only add non-empty files
                        docs.append(content)
                        files.append(f)
                        print(f"Loaded: {f}")
            except Exception as e:
                print(f"Error reading {f}: {e}")
    
    print(f"Total documents loaded: {len(docs)}")
    return docs, files

def get_embedding_with_retry(text, max_retries=3, base_delay=2):
    """Get embedding with exponential backoff retry logic"""
    for attempt in range(max_retries):
        try:
            print(f"Getting embedding (attempt {attempt + 1}/{max_retries})...")
            resp = client.models.embed_content(
                model="gemini-embedding-exp-03-07",
                contents=text,
                config=EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
            )
            return resp.embeddings[0].values
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)  # Exponential backoff
                    print(f"Rate limit hit. Waiting {delay} seconds before retry...")
                    time.sleep(delay)
                else:
                    print(f"Max retries reached. Error: {e}")
                    return None
            else:
                print(f"Error getting embedding: {e}")
                return None
    return None

def build_index_slowly(docs):
    """Build FAISS index with delays between API calls"""
    print("Building embeddings and search index (with rate limiting)...")
    vectors = []
    valid_docs = []
    
    for i, d in enumerate(docs):
        print(f"Processing document {i+1}/{len(docs)}...")
        
        # Add delay between API calls to avoid rate limiting
        if i > 0:
            print("Waiting 3 seconds to avoid rate limits...")
            time.sleep(3)
        
        embedding = get_embedding_with_retry(d)
        if embedding:
            vectors.append(embedding)
            valid_docs.append(d)
            print(f"✅ Successfully processed document {i+1}")
        else:
            print(f"❌ Failed to process document {i+1}")
    
    if not vectors:
        raise ValueError("No valid embeddings generated")
    
    dim = len(vectors[0])
    idx = faiss.IndexFlatL2(dim)
    idx.add(np.array(vectors, dtype="float32"))
    print(f"Index built with {len(vectors)} documents, dimension: {dim}")
    return idx, valid_docs

# Initialize Flask app
app = Flask(__name__)

# Load documents and build index at startup
print("Starting Document-Based QA System...")
docs, filenames = load_docs()

if not docs:
    print("❌ No .txt files found in 'docs/' folder.")
    print("Creating sample document to prevent crash...")
    docs = ["This is a sample document. Please add your own .txt files to the docs folder."]
    filenames = ["sample.txt"]

try:
    index, processed_docs = build_index_slowly(docs)
    docs = processed_docs  # Use only successfully processed docs
    print("✅ System ready!")
except Exception as e:
    print(f"❌ Error building index: {e}")
    exit(1)

@app.route("/", methods=["GET", "POST"])
def home():
    """Handle both GET and POST requests for the main page"""
    query = ""
    result = None
    
    if request.method == "POST":
        query = request.form.get("query", "").strip()
        print(f"Received query: '{query}'")
        
        if query:
            try:
                # Get query embedding with retry logic
                print("Getting query embedding...")
                qv = get_embedding_with_retry(query)
                
                if qv is None:
                    result = "Error: Unable to process your query due to API rate limits. Please try again in a few minutes."
                    print("Failed to generate query embedding")
                else:
                    # Search for similar documents
                    print("Searching for relevant documents...")
                    qv_array = np.array([qv], dtype="float32")
                    distances, idxs = index.search(qv_array, min(3, len(docs)))
                    
                    print(f"Found similar documents at indices: {idxs[0]}")
                    print(f"Distances: {distances[0]}")
                    
                    # Retrieve relevant documents
                    relevant_docs = []
                    for i in idxs[0]:
                        if i < len(docs) and i >= 0:  # Ensure valid index
                            relevant_docs.append(docs[i])
                            print(f"Using document {i}")
                    
                    if relevant_docs:
                        # Generate answer using retrieved context
                        context = "\n\n".join(relevant_docs)
                        prompt = f"""Based on the following context, answer the question clearly and concisely. If the answer is not in the context, say so.

Context:
{context}

Question: {query}

Answer:"""
                        
                        print("Generating answer...")
                        # Add small delay before generation API call
                        time.sleep(1)
                        
                        try:
                            resp = client.models.generate_content(
                                model="gemini-2.5-flash",
                                contents=prompt,
                                config=GenerateContentConfig(
                                    max_output_tokens=300,
                                    temperature=0.1
                                )
                            )
                            result = resp.text
                            print(f"Generated answer: {result[:100]}...")
                        except Exception as gen_error:
                            if "429" in str(gen_error):
                                result = "Rate limit reached. Please wait a few minutes and try again."
                            else:
                                result = f"Error generating answer: {str(gen_error)}"
                    else:
                        result = "No relevant documents found for your query."
                        print("No relevant documents found")
                        
            except Exception as e:
                result = f"Error processing query: {str(e)}"
                print(f"Error processing query: {e}")
        else:
            result = "Please enter a valid query."
            print("Empty query received")
    
    return render_template("index.html", query=query, result=result)

if __name__ == "__main__":
    print("Starting Flask server...")
    app.run(debug=True, host='127.0.0.1', port=5000)