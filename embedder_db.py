from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from qdrant_client.models import VectorParams, Distance
from qdrant_client.models import PointStruct
from typing import Literal
from openai import OpenAI
import os


class EmbedderDB:
    
    def __init__(self, embedding_model: Literal["all-MiniLM-L6-v2", "text-embedding-3-small"]):
        
        try:
            self.client = QdrantClient(url="http://localhost:6333")
            
        except:
            print("There's an error with Qdrant DB. Check if it's running and it's on the right port.")
            exit(0)
        
        # selection of the embedding model
        match embedding_model:
            case "all-MiniLM-L6-v2":
                self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
                self.model_vector_size = 384
                
            case "text-embedding-3-small":
                self.embedding_model = OpenAI(api_key=os.environ["OPENAI_API_KEY"]).embeddings
                self.model_vector_size = 1536

        self.embedding_model_name = embedding_model
            
    def embed_and_load(self, paragraphs_with_pages: list, num_pages: int, collection_name="pdf_embeddings"): 
        
        # this will create a new collection if it doesn't exist. if it exists it return error.
        if not self.create_collection(collection_name): 
            return False
        
        # embeding based on model
        match self.embedding_model_name:
            case "all-MiniLM-L6-v2":
                embeddings = self.embedding_model.encode([paragraph for paragraph, _ in paragraphs_with_pages])
            case "text-embedding-3-small":
                embeddings = []
                batch_size = 100
                texts, _ = zip(*paragraphs_with_pages)  # Unzip into separate lists
                
                for i in range(0, len(paragraphs_with_pages), batch_size):
                    embeddings.extend(
                        e.embedding
                        for e in self.embedding_model.create(
                            input=list(texts)[i:i+batch_size],  # Convert texts to list before slicing,
                            model=self.embedding_model_name
                        ).data
                    )
        
        points = [
            PointStruct(
                id=idx,
                vector=data,
                payload={
                    "model": self.embedding_model_name,
                    "text": text,
                    "page": num_pag
                },
            )
            for idx, (data, (text, num_pag)) in enumerate(zip(embeddings, paragraphs_with_pages))
        ]
        
        self.upload(points, collection_name)
        
        return True
        
    def create_collection(self, collection_name="pdf_embeddings"):
        # Check if collection already exists
        existing_collections = {col.name for col in self.client.get_collections().collections}

        if collection_name in existing_collections:
            return False  # Collection already exists

        try:
            self.client.create_collection(
                collection_name,
                vectors_config=VectorParams(
                    size=self.model_vector_size,  # default vector size of SentenceTransformer all-MiniLM-L6-v2 model
                    distance=Distance.COSINE,
                ),
            )
            return True
        except Exception as e:
            print(f"Error creating collection: {e}")
            return False
                
        
    def upload(self, points: list, collection_name="pdf_embeddings"):
        batch_size = 1000
        
        # uploading to DB in batches of size batch_size
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            self.client.upsert(collection_name, batch)
            

    def search(self, prompt: str, collection_name="pdf_embeddings") -> list[tuple]:
        
        # embedding the query based on model
        match(self.embedding_model_name):
            case "all-MiniLM-L6-v2":
                prompt = self.embedding_model.encode(prompt)
            case "text-embedding-3-small":
                prompt = self.embedding_model.create(
                            input=prompt,
                            model=self.embedding_model_name
                        ).data[0].embedding
        
        result = self.client.query_points(
            collection_name=collection_name,
            query=prompt,
            limit=3
        )
        
        pages = []
        
        for point in result.points:
            pages.append((point.payload["page"], point.score))
        
        return pages
    
    def delete_collection(self, collection_name="pdf_embeddings"):
        self.client.delete_collection(collection_name)