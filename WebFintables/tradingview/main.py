from agents import Agent, ModelSettings, function_tool, trace
from agents import Agent, InputGuardrail, GuardrailFunctionOutput, Runner
from pydantic import BaseModel
import asyncio
import uuid
import sys
from openai.types.responses import ResponseTextDeltaEvent
from agents import Agent, Runner
import asyncio
import random
from agents import Agent, ItemHelpers, Runner, function_tool

from agents import Agent, Runner
import asyncio

tradingview_agent = Agent(
    name="Spanish agent",
    instructions="You translate the user's message to Spanish",
)

french_agent = Agent(
    name="French agent",
    instructions="You translate the user's message to French",
)

orchestrator_agent = Agent(
    name="orchestrator_agent",
    instructions=(
        "You are a translation agent. You use the tools given to you to translate."
        "If asked for multiple translations, you call the relevant tools."
    ),
    tools=[
        spanish_agent.as_tool(
            tool_name="translate_to_spanish",
            tool_description="Translate the user's message to Spanish",
        ),
        french_agent.as_tool(
            tool_name="translate_to_french",
            tool_description="Translate the user's message to French",
        ),
    ],
)

async def main():
    result = await Runner.run(orchestrator_agent, input="Say 'Hello, how are you?' in Spanish. and then say it in French.")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())