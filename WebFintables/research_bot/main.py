import asyncio

from manager import ResearchManager


async def main() -> None:
    print("Welcome to the research bot!")
    query = "What are the main use cases for the OpenAI API's Agent SDK?"
    await ResearchManager().run(query)


if __name__ == "__main__":
    asyncio.run(main())
