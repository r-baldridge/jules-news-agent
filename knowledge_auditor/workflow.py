import hashlib
import time
from typing import Dict, List, Tuple

class FactVerificationWorkflow:
    """Mock implementations for the steps in FACT_VERIFICATION_WORKFLOW.md"""

    @staticmethod
    def extract_claim(text: str) -> Tuple[str, str, str]:
        """
        1. Claim Extraction
        Returns: (claim_id, original_claim, normalized_claim)
        """
        # Mock logic
        timestamp = int(time.time())
        hash_val = hashlib.md5(text.encode('utf-8')).hexdigest()[:8]
        claim_id = f"Claim-{timestamp}-{hash_val}"

        # In a real scenario, NLP would extract and normalize the statement
        original_claim = text
        normalized_claim = text.strip().capitalize()
        if not normalized_claim.endswith('.'):
            normalized_claim += "."

        return claim_id, original_claim, normalized_claim

    @staticmethod
    def retrieve_evidence(normalized_claim: str) -> List[Dict]:
        """
        2. Evidence Retrieval
        Returns list of evidence dicts.
        """
        # Mock logic: return a dummy source
        # In reality, this queries the knowledge base or external sources
        dummy_source_id = f"SRC-{hashlib.md5(normalized_claim.encode()).hexdigest()[:6].upper()}"

        return [
            {
                "source_id": dummy_source_id,
                "content": "This is simulated evidence content that relates to the claim.",
                "metadata": {
                    "author": "Mock Author",
                    "date": "2024-01-01",
                    "url": "https://example.com/mock-source"
                },
                "details": "Simulated quote extracted from the source."
            }
        ]

    @staticmethod
    def verify_fact(normalized_claim: str, evidence: List[Dict]) -> Tuple[str, str]:
        """
        3 & 4. Fact Verification Logic and Status Assignment
        Returns: (status, analysis)
        """
        # Mock logic
        # Statuses: CONFIRMED, REFUTED, NEEDS CONTEXT, INCONCLUSIVE
        if not evidence:
            return "INCONCLUSIVE", "No evidence was found to support or refute the claim."

        # Simplistic mock: if the claim has the word 'fake', refute it.
        if "fake" in normalized_claim.lower():
            return "REFUTED", "Evidence clearly contradicts the assertion made in the claim."

        return "CONFIRMED", "Available reliable sources support the claim."
