# Knowledge Base Organization Scheme

To maintain a searchable and ever-growing database of reliable knowledge, the `@knowledge-auditor` uses the following diligent organization scheme.

## Directory Structure

```text
/knowledge_base
  /sources                 # Logged reference files (raw evidence)
    /YYYY/MM               # Grouped by year and month added
  /cases                   # Timestamped verification case documentation
    /confirmed             # Cases that resulted in a CONFIRMED status
    /refuted               # Cases that resulted in a REFUTED status
    /needs_context         # Cases that resulted in a NEEDS CONTEXT status
    /inconclusive          # Cases that resulted in an INCONCLUSIVE status
  /index                   # Index files for quick searching
    entities.json          # Index of claims and cases by named entities
    tags.json              # Index of cases by topic tags
    sources.json           # Registry mapping [Source-ID] to file paths/URLs
```

## Schemas

### 1. Logged Reference Files (`/sources`)

Raw evidence is downloaded or extracted and saved here.

* **Naming Convention:** `[Source-ID]_[Date-Added]_[Short-Title].[ext]`
* **Metadata:** Each source file should be accompanied by a `.meta.json` file detailing its origin, author, publication date, and hash.

### 2. Timestamped Verification Case Documentation (`/cases`)

When a fact-check is completed, a report is generated and placed in the appropriate status folder.

* **Naming Convention:** `Verification-Case-[Timestamp]-[ClaimID].md`
* **Template Structure:**
  * **Claim ID:** The unique ID for the claim.
  * **Original Claim:** The text of the claim as extracted.
  * **Normalized Claim:** The neutral, testable version.
  * **Timestamp:** ISO 8601 format.
  * **Status:** The final assigned status.
  * **Analysis:** A brief summary of the verification logic applied.
  * **Evidence Log:** A list of `[Source-ID]` references used, including quotes or data points extracted from each that influenced the decision.

### 3. Indexing Strategy (`/index`)

To make the database searchable, the `@knowledge-auditor` updates JSON index files whenever a new case is added.

* **Entities:** Maps people, organizations, or locations to a list of associated `ClaimID`s.
* **Tags:** Maps topics (e.g., 'Economy', 'Healthcare') to associated `ClaimID`s.
* **Sources Registry:** Acts as a master lookup table to resolve a `[Source-ID]` to its actual location in the `/sources` directory or its external URL.
