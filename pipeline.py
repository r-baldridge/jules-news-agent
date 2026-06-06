import uuid
from qdrant_client.models import PointStruct
from infrastructure import InfrastructureManager

class PipelineRouter:
    """
    Tier 3 & 4: Vetting Crucible and Storage Routing
    Processes extracted facts, vets them in DuckDB, and pushes them to Kùzu & Qdrant.
    """
    def __init__(self, infra: InfrastructureManager):
        self.infra = infra

    def stage_triplets(self, triplets: list):
        """Tier 3: Push to DuckDB staging table."""
        print(f"Staging {len(triplets)} triplets in DuckDB...")
        for t in triplets:
            self.infra.duckdb_conn.execute("""
                INSERT INTO staging_triplets (id, subject, predicate, object, confidence, date, source_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (t['id'], t['subject'], t['predicate'], t['object'], t['confidence'], t['date'], t['source_id']))

    def vet_staged_triplets(self):
        """
        Tier 3: Conflict detection and consensus scoring.
        In this iteration, we simply mark all pending as 'VERIFIED' to move them
        to Tier 4. In a real system, this would run complex consensus logic.
        """
        print("Vetting staged triplets...")
        self.infra.duckdb_conn.execute("UPDATE staging_triplets SET status = 'VERIFIED' WHERE status = 'PENDING'")

        # Retrieve verified triplets to push to Tier 4
        result = self.infra.duckdb_conn.execute("SELECT * FROM staging_triplets WHERE status = 'VERIFIED'").fetchall()

        verified_facts = []
        for row in result:
            verified_facts.append({
                'id': row[0],
                'subject': row[1],
                'predicate': row[2],
                'object': row[3],
                'confidence': row[4],
                'date': row[5],
                'source_id': row[6]
            })

        # Update status to PROCESSED so we don't push them again on the next run
        self.infra.duckdb_conn.execute("UPDATE staging_triplets SET status = 'PROCESSED' WHERE status = 'VERIFIED'")

        return verified_facts

    def mock_embedding(self, text: str) -> list:
        """
        Generates a mock 384-dimensional embedding for an entity string.
        A real implementation would use something like sentence-transformers.
        """
        # A simple deterministic hash-based mock embedding
        import hashlib
        h = hashlib.sha256(text.encode()).digest()
        embedding = [(b / 255.0) for b in h]
        # pad to 384 dimensions
        while len(embedding) < 384:
            embedding.extend(embedding[:384-len(embedding)])
        return embedding[:384]

    def store_verified_facts(self, facts: list):
        """Tier 4: Push verified facts to Kùzu (Graph) and Qdrant (Vector)."""
        print(f"Pushing {len(facts)} verified facts to Tier 4 storage...")

        qdrant_points = []

        import hashlib
        for fact in facts:
            subj = fact['subject']
            obj = fact['object']

            # Use deterministic hash instead of python's built-in randomized hash
            subj_id = f"ENT_{hashlib.sha256(subj.encode('utf-8')).hexdigest()[:8]}"
            obj_id = f"ENT_{hashlib.sha256(obj.encode('utf-8')).hexdigest()[:8]}"

            # 1. Update Kùzu Graph Database
            # Insert Subject Node
            self.infra.kuzu_conn.execute(
                "MERGE (e:Entity {id: $id, name: $name, type: 'Unknown'})",
                parameters={"id": subj_id, "name": subj}
            )
            # Insert Object Node
            self.infra.kuzu_conn.execute(
                "MERGE (e:Entity {id: $id, name: $name, type: 'Unknown'})",
                parameters={"id": obj_id, "name": obj}
            )
            # Insert Relationship
            self.infra.kuzu_conn.execute("""
                MATCH (s:Entity {id: $subj_id}), (o:Entity {id: $obj_id})
                CREATE (s)-[r:RelatesTo {predicate: $pred, confidence: $conf, date: $date, source_id: $src}]->(o)
            """, parameters={
                "subj_id": subj_id,
                "obj_id": obj_id,
                "pred": fact['predicate'],
                "conf": fact['confidence'],
                "date": fact['date'],
                "src": fact['source_id']
            })

            # 2. Update Qdrant Vector Anchor
            # Add vectors for the entities
            # Use an integer hash for Qdrant ID. sha256 output cast to int, modulo to keep it safe.
            subj_qdrant_id = int(hashlib.sha256(subj_id.encode('utf-8')).hexdigest(), 16) % (2**63 - 1)
            obj_qdrant_id = int(hashlib.sha256(obj_id.encode('utf-8')).hexdigest(), 16) % (2**63 - 1)

            qdrant_points.append(PointStruct(
                id=subj_qdrant_id,
                vector=self.mock_embedding(subj),
                payload={"entity_id": subj_id, "name": subj}
            ))
            qdrant_points.append(PointStruct(
                id=obj_qdrant_id,
                vector=self.mock_embedding(obj),
                payload={"entity_id": obj_id, "name": obj}
            ))

        # Upsert vectors
        if qdrant_points:
            self.infra.qdrant_client.upsert(
                collection_name="entities",
                points=qdrant_points
            )

        print("Tier 4 storage update complete.")

if __name__ == "__main__":
    from ingestion import IngestionManager
    from extraction import SLMExtractor

    # Initialize Infra
    infra = InfrastructureManager()
    infra.initialize_all()

    # Initialize components
    ingestor = IngestionManager()
    extractor = SLMExtractor()
    router = PipelineRouter(infra)

    # Get all sources
    sources = ingestor.get_all_sources()
    print(f"Processing {len(sources)} sources from archive...")

    for source in sources:
        # Extract
        triplets = extractor.extract_triplets(source['content'], source['metadata']['source_id'])

        # Route
        router.stage_triplets(triplets)
        verified_facts = router.vet_staged_triplets()
        router.store_verified_facts(verified_facts)

    infra.close()
    print("Pipeline run completed successfully.")
