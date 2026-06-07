from knowledge_auditor.agent import KnowledgeAuditor

def main():
    print("--- Starting Fact Verification Engine ---\n")

    # Initialize the agent (this creates the knowledge_base directory structure)
    auditor = KnowledgeAuditor(base_dir="test_knowledge_base")

    # Test case 1: A valid claim
    claim1 = "The sky appears blue during the day due to Rayleigh scattering."
    auditor.process_claim_text(
        claim1,
        entities=["Atmosphere"],
        tags=["Science", "Physics"]
    )

    print("\n-----------------------------------------\n")

    # Test case 2: A claim designed to trigger the mock "REFUTED" logic
    claim2 = "This is a fake claim for testing."
    auditor.process_claim_text(
        claim2,
        entities=["TestEntity"],
        tags=["Testing"]
    )

    print("\n--- Processing Complete ---")

if __name__ == "__main__":
    main()
