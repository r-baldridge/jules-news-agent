from news_agent import NewsAgent

def main():
    print("--- Starting News Management System ---\n")

    agent = NewsAgent(base_dir="test_news_database")

    # Simulate acquiring news
    news_id_1 = agent.acquire_news(
        url="https://example.com/news/1",
        title="Major Breakthrough in AI",
        content="Researchers have discovered a new way to train models efficiently...",
        source_metadata={"author": "Jane Doe", "publisher": "Tech Daily"}
    )

    news_id_2 = agent.acquire_news(
        url="https://example.com/news/2",
        title="Market Reacts to Tech News",
        content="Stocks surged today following major announcements in the AI sector.",
        source_metadata={"author": "John Smith", "publisher": "Finance Now"}
    )

    print("\n-----------------------------------------\n")

    # Simulate storing analytical results based on the news
    analysis_content = "The recent breakthrough in AI training is directly correlating with positive market movements, indicating strong investor confidence."
    analysis_id = agent.store_analytical_result(
        analysis_content=analysis_content,
        linked_refs=[news_id_1, news_id_2],
        metadata={"analyst": "Auto-Agent", "tags": ["AI", "Market"]}
    )

    print(f"\nCompleted tracking. Final Analysis ID: {analysis_id}")
    print("--- System Offline ---")

if __name__ == "__main__":
    main()
