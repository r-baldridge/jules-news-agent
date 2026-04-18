from typing import List, Dict, Optional
from .knowledge_base import KnowledgeBase
from .workflow import FactVerificationWorkflow

class KnowledgeAuditor:
    """
    The @knowledge-auditor Technical Assistant for Fact-Checking and Knowledge Verification.
    Follows Zero-Hallucination Protocol.
    """

    def __init__(self, base_dir: str = "knowledge_base"):
        self.kb = KnowledgeBase(base_dir=base_dir)
        self.workflow = FactVerificationWorkflow()

    def process_claim_text(self, text: str, entities: List[str] = None, tags: List[str] = None) -> str:
        """
        End-to-end processing of a text containing a claim.
        Extracts claim, finds evidence, verifies, and logs to the knowledge base.
        Returns the path to the generated case file.
        """
        print(f"[@knowledge-auditor] Received text for verification: '{text}'")

        # 1. Claim Extraction
        claim_id, original, normalized = self.workflow.extract_claim(text)
        print(f"[@knowledge-auditor] Extracted Claim ID: {claim_id}")
        print(f"[@knowledge-auditor] Normalized: '{normalized}'")

        # 2. Evidence Retrieval
        evidence_list = self.workflow.retrieve_evidence(normalized)
        print(f"[@knowledge-auditor] Retrieved {len(evidence_list)} pieces of evidence.")

        # Log new sources to KB
        for ev in evidence_list:
            source_id = ev["source_id"]
            self.kb.add_source(
                source_id=source_id,
                short_title="Mock_Evidence",
                content=ev["content"],
                extension="txt",
                metadata=ev.get("metadata", {})
            )
            print(f"[@knowledge-auditor] Logged source {source_id} to Knowledge Base.")

        # 3 & 4. Fact Verification Logic & Status Assignment
        status, analysis = self.workflow.verify_fact(normalized, evidence_list)
        print(f"[@knowledge-auditor] Verification Status: {status}")

        # 5. Output Generation (save case to KB)
        case_path = self.kb.add_case(
            claim_id=claim_id,
            original_claim=original,
            normalized_claim=normalized,
            status=status,
            analysis=analysis,
            evidence_log=evidence_list,
            entities=entities or [],
            tags=tags or []
        )
        print(f"[@knowledge-auditor] Case documented successfully at: {case_path}")

        return str(case_path)
