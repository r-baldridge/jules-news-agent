import os
import json
import datetime
import hashlib
from pathlib import Path
from typing import Dict, List, Optional

class NewsAgent:
    """
    Agent responsible for acquiring news and managing an extensive
    collection of sources, primary documents, and analytical results.
    Ensures all details are logged and referenceable.
    """

    def __init__(self, base_dir: str = "news_database"):
        self.base_dir = Path(base_dir)
        self.primary_sources_dir = self.base_dir / "primary_sources"
        self.analysis_dir = self.base_dir / "analysis"
        self.reference_dir = self.base_dir / "references"

        self._init_structure()

    def _init_structure(self):
        """Initializes the directory structure for managing collections."""
        self.primary_sources_dir.mkdir(parents=True, exist_ok=True)
        self.analysis_dir.mkdir(parents=True, exist_ok=True)
        self.reference_dir.mkdir(parents=True, exist_ok=True)

        # Initialize central reference registry
        self._init_index_file("reference_registry.json", {})

    def _init_index_file(self, filename: str, default_content: dict):
        file_path = self.base_dir / filename
        if not file_path.exists():
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(default_content, f, indent=2)

    def _read_registry(self) -> dict:
        with open(self.base_dir / "reference_registry.json", "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_registry(self, data: dict):
        with open(self.base_dir / "reference_registry.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _generate_ref_id(self, prefix: str, content: str) -> str:
        """Generates a unique reference ID."""
        hash_val = hashlib.md5(content.encode('utf-8')).hexdigest()[:8]
        timestamp = int(datetime.datetime.now().timestamp())
        return f"{prefix}-{timestamp}-{hash_val}"

    def acquire_news(self, url: str, content: str, title: str, source_metadata: dict) -> str:
        """
        Simulates acquiring a news article.
        Stores it as a primary source document and makes it referenceable.
        """
        print(f"[NewsAgent] Acquiring news: '{title}' from {url}")

        ref_id = self._generate_ref_id("NEWS", content)
        now = datetime.datetime.now(datetime.timezone.utc)
        date_folder = now.strftime("%Y/%m")

        target_dir = self.primary_sources_dir / date_folder
        target_dir.mkdir(parents=True, exist_ok=True)

        # Save content
        safe_title = "".join(c if c.isalnum() else "_" for c in title)
        file_path = target_dir / f"{ref_id}_{safe_title}.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Log to registry
        registry = self._read_registry()
        registry[ref_id] = {
            "type": "primary_source",
            "title": title,
            "url": url,
            "file_path": str(file_path),
            "timestamp": now.isoformat(),
            "metadata": source_metadata
        }
        self._write_registry(registry)

        print(f"[NewsAgent] Saved primary source. Ref-ID: {ref_id}")
        return ref_id

    def store_analytical_result(self, analysis_content: str, linked_refs: List[str], metadata: dict) -> str:
        """
        Stores analytical results and links them to primary sources.
        """
        ref_id = self._generate_ref_id("ANALYSIS", analysis_content)
        now = datetime.datetime.now(datetime.timezone.utc)

        file_path = self.analysis_dir / f"{ref_id}.md"

        # Build analysis document
        doc_content = f"# Analytical Result: {ref_id}\n\n"
        doc_content += f"**Timestamp:** {now.isoformat()}\n\n"
        doc_content += f"## Linked References\n"
        for link in linked_refs:
            doc_content += f"- [{link}]\n"

        doc_content += f"\n## Analysis\n{analysis_content}\n"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(doc_content)

        # Log to registry
        registry = self._read_registry()
        registry[ref_id] = {
            "type": "analytical_result",
            "file_path": str(file_path),
            "timestamp": now.isoformat(),
            "linked_references": linked_refs,
            "metadata": metadata
        }
        self._write_registry(registry)

        print(f"[NewsAgent] Stored analytical result. Ref-ID: {ref_id}")
        return ref_id
