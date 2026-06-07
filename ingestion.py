import os
import json
import hashlib
from datetime import datetime

class IngestionManager:
    """
    Tier 1: Ingestion & Deterministic Deduplication
    Reads raw documents from the immutable artifact archive (e.g. /knowledge_base/sources)
    """
    def __init__(self, sources_dir="./knowledge_base/sources"):
        self.sources_dir = sources_dir
        os.makedirs(self.sources_dir, exist_ok=True)

    def read_source_file(self, filepath):
        """Reads a source text file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            print(f"Error reading file {filepath}: {e}")
            return None

    def read_meta_file(self, filepath):
        """Reads a source metadata JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            return meta
        except Exception as e:
            print(f"Error reading meta file {filepath}: {e}")
            return {}

    def get_all_sources(self):
        """
        Iterates over the sources directory and yields documents
        with their metadata.
        """
        sources = []
        for root, _, files in os.walk(self.sources_dir):
            for file in files:
                if not file.endswith(".meta.json") and not file.startswith("."):
                    filepath = os.path.join(root, file)
                    meta_filepath = filepath + ".meta.json"

                    content = self.read_source_file(filepath)
                    meta = {}
                    if os.path.exists(meta_filepath):
                        meta = self.read_meta_file(meta_filepath)
                    else:
                        # Fallback basic metadata if not exists
                        meta = {
                            "source_id": hashlib.md5(filepath.encode()).hexdigest(),
                            "title": file,
                            "date_added": datetime.now().isoformat(),
                            "url": f"file://{filepath}"
                        }

                    if content:
                        sources.append({
                            "content": content,
                            "metadata": meta,
                            "filepath": filepath
                        })
        return sources

    def ingest_new_document(self, text, title, source_url):
        """
        Simulates the broker/ingestion node pulling in a new document,
        normalizing it, and saving to the immutable archive.
        """
        now = datetime.now()
        year_month = now.strftime("%Y/%m")
        target_dir = os.path.join(self.sources_dir, year_month)
        os.makedirs(target_dir, exist_ok=True)

        # Simple determinisic deduplication via hashing the content
        content_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
        source_id = f"SRC-{content_hash[:8]}"
        date_str = now.strftime("%Y-%m-%d")

        safe_title = "".join([c if c.isalnum() else "_" for c in title])[:30]
        filename = f"{source_id}_{date_str}_{safe_title}.txt"
        filepath = os.path.join(target_dir, filename)

        # Check if already exists (Deduplication)
        if os.path.exists(filepath):
            print(f"Document {source_id} already exists in archive. Skipping ingestion.")
            return filepath, source_id

        # Write immutable content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)

        # Write metadata
        meta = {
            "source_id": source_id,
            "title": title,
            "url": source_url,
            "date_added": now.isoformat(),
            "content_hash": content_hash
        }
        with open(filepath + ".meta.json", 'w', encoding='utf-8') as f:
            json.dump(meta, f, indent=2)

        print(f"Ingested new document: {filepath}")
        return filepath, source_id

if __name__ == "__main__":
    # Test Ingestion Module
    ingestor = IngestionManager()
    sample_text = "Apple Inc. announced today that it will acquire TechStartup X for 1 billion dollars. The acquisition is expected to close in Q4."
    ingestor.ingest_new_document(sample_text, "Apple Acquires TechStartup X", "https://example.com/news/apple-acquires-x")

    sources = ingestor.get_all_sources()
    print(f"Found {len(sources)} sources in archive.")
    for s in sources:
        print(f"- {s['metadata']['source_id']}: {s['metadata']['title']}")
