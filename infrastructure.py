import os
import kuzu
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import duckdb

class InfrastructureManager:
    def __init__(self, base_dir="./data"):
        self.base_dir = base_dir
        self.kuzu_path = os.path.join(base_dir, "kuzu_db")
        self.qdrant_path = os.path.join(base_dir, "qdrant_db")
        self.duckdb_path = os.path.join(base_dir, "staging.duckdb")

        # Ensure base directory exists
        os.makedirs(self.base_dir, exist_ok=True)

        self.kuzu_conn = None
        self.qdrant_client = None
        self.duckdb_conn = None

    def setup_kuzu(self):
        print(f"Setting up Kùzu Graph DB at {self.kuzu_path}...")
        db = kuzu.Database(self.kuzu_path)
        self.kuzu_conn = kuzu.Connection(db)

        # Initialize schema for Tier 4 Graph
        # We need an Entity node table and a Rel table for predicates
        try:
            # Query existing tables to avoid IF NOT EXISTS which is partially supported depending on version
            tables = self.kuzu_conn.execute("CALL show_tables() RETURN *").get_as_df()
            table_names = tables['name'].tolist() if not tables.empty else []

            if "Entity" not in table_names:
                self.kuzu_conn.execute("CREATE NODE TABLE Entity (id STRING, name STRING, type STRING, PRIMARY KEY (id))")

            if "RelatesTo" not in table_names:
                self.kuzu_conn.execute("CREATE REL TABLE RelatesTo (FROM Entity TO Entity, predicate STRING, confidence DOUBLE, date STRING, source_id STRING)")

            print("Kùzu schema initialized successfully.")
        except Exception as e:
            print(f"Kùzu schema setup issue: {e}")

    def setup_qdrant(self):
        print(f"Setting up Qdrant Vector DB at {self.qdrant_path}...")
        self.qdrant_client = QdrantClient(path=self.qdrant_path)

        # Initialize collections for Tier 4 Vector Anchor
        # We store embeddings of Entities to allow semantic search
        collection_name = "entities"

        if not self.qdrant_client.collection_exists(collection_name):
            self.qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE), # Assuming a standard 384-dim embedding model like all-MiniLM-L6-v2 for now
            )
            print(f"Qdrant collection '{collection_name}' initialized successfully.")
        else:
            print(f"Qdrant collection '{collection_name}' already exists.")

    def setup_duckdb(self):
        print(f"Setting up DuckDB at {self.duckdb_path}...")
        self.duckdb_conn = duckdb.connect(self.duckdb_path)

        # Initialize staging table for Tier 3 Vetting Crucible
        self.duckdb_conn.execute("""
            CREATE TABLE IF NOT EXISTS staging_triplets (
                id VARCHAR,
                subject VARCHAR,
                predicate VARCHAR,
                object VARCHAR,
                confidence DOUBLE,
                date VARCHAR,
                source_id VARCHAR,
                status VARCHAR DEFAULT 'PENDING'
            )
        """)
        print("DuckDB schema initialized successfully.")

    def initialize_all(self):
        print("Initializing Tier 4 Infrastructure...")
        self.setup_kuzu()
        self.setup_qdrant()
        self.setup_duckdb()
        print("Infrastructure initialization complete.\n")

    def close(self):
        if self.kuzu_conn:
            self.kuzu_conn.close()
        if self.duckdb_conn:
            self.duckdb_conn.close()
        if self.qdrant_client:
            self.qdrant_client.close()

if __name__ == "__main__":
    infra = InfrastructureManager()
    infra.initialize_all()
    infra.close()
