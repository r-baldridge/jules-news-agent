# Fact-Checking Logic Module & Workflow

This document outlines the systematic process used by the `@knowledge-auditor` to evaluate facts and claims.

## 1. Claim Extraction

When presented with a text or data stream:

* **Identify Assertions:** Extract discrete, testable statements (claims) from the text.
* **Normalize:** Rewrite the claim in a clear, neutral format, removing rhetorical or subjective language.
* **Assign ID:** Generate a unique identifier for the claim (e.g., `Claim-[Timestamp]-[Hash]`).

## 2. Evidence Retrieval

* **Query Generation:** Formulate specific search queries based on the normalized claim.
* **Knowledge Base Search:** Query the internal organized databases and logged reference files first.
* **External Verification (If Approved):** If internal sources are insufficient, query approved external databases or APIs.
* **Source Logging:** For every piece of evidence retrieved, assign a `[Source-ID]` and log its metadata (URL/FilePath, Title, Date Retrieved).

## 3. Fact Verification Logic

Evaluate the retrieved evidence against the claim using the following criteria:

* **Relevance:** Does the evidence directly address the core assertion of the claim?
* **Reliability:** Is the source trusted and documented?
* **Alignment:** Does the evidence support, contradict, or provide nuance to the claim?

## 4. Status Assignment

Based on the verification logic, assign one of the following statuses:

* **CONFIRMED:** Multiple reliable sources directly support the claim. No significant contradictory evidence from reliable sources exists.
* **REFUTED:** Reliable sources directly contradict the claim.
* **NEEDS CONTEXT:** The claim is technically true but misleading without additional context, or it is only partially true.
* **INCONCLUSIVE:** Insufficient reliable evidence exists to confirm or refute the claim.

## 5. Output Generation

Generate a standard Verification Case report. This report is passed to the organization module for filing and indexing.
