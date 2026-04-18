import os
import json
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class KnowledgeBase:
    def __init__(self, base_dir: str = "knowledge_base"):
        self.base_dir = Path(base_dir)
        self.sources_dir = self.base_dir / "sources"
        self.cases_dir = self.base_dir / "cases"
        self.index_dir = self.base_dir / "index"

        self._init_structure()

    def _init_structure(self):
        # Create base dirs
        self.sources_dir.mkdir(parents=True, exist_ok=True)
        self.index_dir.mkdir(parents=True, exist_ok=True)

        # Create cases subdirs
        for status in ["confirmed", "refuted", "needs_context", "inconclusive"]:
            (self.cases_dir / status).mkdir(parents=True, exist_ok=True)

        # Initialize indices
        self._init_index_file("entities.json", {})
        self._init_index_file("tags.json", {})
        self._init_index_file("sources.json", {})

    def _init_index_file(self, filename: str, default_content: Any):
        file_path = self.index_dir / filename
        if not file_path.exists():
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(default_content, f, indent=2)

    def _read_index(self, filename: str) -> dict:
        with open(self.index_dir / filename, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_index(self, filename: str, data: dict):
        with open(self.index_dir / filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def add_source(self, source_id: str, short_title: str, content: str, extension: str, metadata: dict) -> Path:
        """Adds a raw evidence file to the sources directory and updates sources.json."""
        now = datetime.datetime.now(datetime.timezone.utc)
        year_str = now.strftime("%Y")
        month_str = now.strftime("%m")
        date_added = now.strftime("%Y%m%d")

        target_dir = self.sources_dir / year_str / month_str
        target_dir.mkdir(parents=True, exist_ok=True)

        safe_title = "".join(c if c.isalnum() else "_" for c in short_title)
        filename = f"{source_id}_{date_added}_{safe_title}.{extension}"
        file_path = target_dir / filename

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        meta_filename = f"{source_id}_{date_added}_{safe_title}.meta.json"
        meta_path = target_dir / meta_filename
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        # Update sources registry
        sources_registry = self._read_index("sources.json")
        sources_registry[source_id] = {
            "file_path": str(file_path),
            "meta_path": str(meta_path),
            "url": metadata.get("url", "")
        }
        self._write_index("sources.json", sources_registry)

        return file_path

    def add_case(self, claim_id: str, original_claim: str, normalized_claim: str,
                 status: str, analysis: str, evidence_log: List[Dict],
                 entities: List[str] = None, tags: List[str] = None) -> Path:
        """Saves a timestamped Verification Case report and updates indices."""
        now = datetime.datetime.now(datetime.timezone.utc)
        timestamp = now.strftime("%Y%m%dT%H%M%SZ")

        status_folder = status.lower().replace(" ", "_")
        if status_folder not in ["confirmed", "refuted", "needs_context", "inconclusive"]:
            status_folder = "inconclusive"

        filename = f"Verification-Case-{timestamp}-{claim_id}.md"
        file_path = self.cases_dir / status_folder / filename

        # Build markdown report
        md_content = f"""# Verification Case: {claim_id}

**Timestamp:** {now.isoformat()}
**Status:** {status.upper()}

## Claims
* **Original Claim:** {original_claim}
* **Normalized Claim:** {normalized_claim}

## Analysis
{analysis}

## Evidence Log
"""
        for evidence in evidence_log:
            source_id = evidence.get("source_id", "Unknown")
            details = evidence.get("details", "")
            md_content += f"* **[{source_id}]**: {details}\n"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        # Update indices
        if entities:
            entities_index = self._read_index("entities.json")
            for entity in entities:
                if entity not in entities_index:
                    entities_index[entity] = []
                if claim_id not in entities_index[entity]:
                    entities_index[entity].append(claim_id)
            self._write_index("entities.json", entities_index)

        if tags:
            tags_index = self._read_index("tags.json")
            for tag in tags:
                if tag not in tags_index:
                    tags_index[tag] = []
                if claim_id not in tags_index[tag]:
                    tags_index[tag].append(claim_id)
            self._write_index("tags.json", tags_index)

        return file_path
