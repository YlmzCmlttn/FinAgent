from agents import Agent, Runner, gen_trace_id, trace


async def main():
    agent = Agent(
        name="test-agent",
        description="A test agent",
        model="gpt-4o-mini",
    )




if __name__ == "__main__":    
    asyncio.run(main())
