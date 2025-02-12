from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from qdrant_client.models import VectorParams, Distance
from qdrant_client.models import PointStruct


class EmbedderDB:
    
    def __init__(self):
        
        try:
            self.client = QdrantClient(url="http://localhost:6333")
            self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            
        except:
            print("There's an error with Qdrant DB. Check if it's running and it's on the right port.")
            exit(0)
            
    def embed_and_load(self, paragraphs_with_pages: list, num_pages: int, collection_name="pdf_embeddings"): 
        
        # this will create a new collection if it doesn't exist. if it exists it return error.
        if not self.create_collection(collection_name): 
            return False
               
        embeddings = self.embedding_model.encode([paragraph for paragraph, _ in paragraphs_with_pages])
        
        points = [
            PointStruct(
                id=idx,
                vector=data,
                payload={
                    "text": text,
                    "page": num_pag
                },
            )
            for idx, (data, (text, num_pag)) in enumerate(zip(embeddings, paragraphs_with_pages))
            
        ]
        
        self.upload(points, collection_name)
        
        return True
        
    def create_collection(self, collection_name="pdf_embeddings"):
        # checking for existence of a collection
            collections = self.client.get_collections().collections
            
            try:
                self.client.create_collection(
                    collection_name,
                    vectors_config=VectorParams(
                        size=384, # default vector size of SentenceTransformer all-MiniLM-L6-v2 model
                        distance=Distance.COSINE,
                    ),
                )
                return True
            # in case collection name already exists (same file has already been embedded)
            except Exception:
                return False
                
        
    def upload(self, points: list, collection_name="pdf_embeddings"):
        batch_size = 1000
        
        # uploading to DB in batches of size batch_size
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            self.client.upsert(collection_name, batch)
            

    def search(self, prompt: str, collection_name="pdf_embeddings") -> list[tuple]:
        
        result = self.client.query_points(
            collection_name=collection_name,
            query=self.embedding_model.encode(prompt),
            limit=3
        )
        
        pages = []
        
        for point in result.points:
            pages.append((point.payload["page"], point.score))
        
        return pages