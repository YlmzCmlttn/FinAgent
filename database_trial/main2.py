import asyncio
from read_create import read_create_tables

from agents import Agent, ItemHelpers, MessageOutputItem, Runner, trace, WebSearchTool



financial_statements_agent = Agent(
    name="financial_statements_agent",
    instructions="You helpful ai agent tool for retrieving financial statements from a database. Use tools to retrive financial tables from the database.",
    handoff_description="An agent for retrieving financial statements",
    model="gpt-4o-mini",    
    #tools=[WebSearchTool()],
)

financial_analyst_agent = Agent(
    name="financial_analyst_agent",
    instructions=(
        "You are a helpful professional financial analyst."
        "If financial statements are requested or needed, you use the financial_statements_agent to retrieve them."
    ),
    tools=[
        financial_statements_agent.as_tool(
            tool_name="financial_statements_agent",
            tool_description="Agent for retrieving financial statements",
        )
    ],
    model="gpt-4o-mini",
)


async def main():

    msg = "Koç holding net karı nasıl? Bu yilin birinci çeyreğinden sonraki net karı ne kadardır?"

    # Run the entire orchestration in a single trace
    with trace("Financial analyst"):
        financial_analyst_result = await Runner.run(financial_analyst_agent, msg)

        for item in financial_analyst_result.new_items:
            if isinstance(item, MessageOutputItem):
                text = ItemHelpers.text_message_output(item)
                if text:
                    print(f"  - Financial analyst step: {text}")
        print(financial_analyst_result.to_input_list())

    print(f"\n\nFinal response:\n{financial_analyst_result.final_output}")

if __name__ == "__main__":
    asyncio.run(main())
