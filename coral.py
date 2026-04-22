from chatbot_engine import CoralChatbot


def main() -> None:
    bot = CoralChatbot()
    print("Coral Bot is ready. Type 'exit' to quit.")

    while True:
        query = input("You: ").strip()
        if query.lower() in {"exit", "quit"}:
            print("Bot: Goodbye! Keep exploring coral reefs.")
            break

        response, score = bot.ask(query)
        print(f"Bot: {response}")
        print(f"[similarity score: {score:.3f}]")


if __name__ == "__main__":
    main()
