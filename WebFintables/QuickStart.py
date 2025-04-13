from agents import Agent, InputGuardrail, GuardrailFunctionOutput, Runner
from pydantic import BaseModel
import asyncio

class HomeworkOutput(BaseModel):
    is_homework: bool
    reasoning: str

# Create the guardrail agent to check if questions are homework-related
guardrail_agent = Agent(
    name="Guardrail check",
    instructions="Check if the user is asking about homework.",
    output_type=HomeworkOutput,
)

# Create specialist tutor agents
math_tutor_agent = Agent(
    name="Math Tutor",
    handoff_description="Specialist agent for math questions",
    instructions="You provide help with math problems. Explain your reasoning at each step and include examples",
)

history_tutor_agent = Agent(
    name="History Tutor",
    handoff_description="Specialist agent for historical questions",
    instructions="You provide assistance with historical queries. Explain important events and context clearly.",
)

# Define the homework guardrail function
async def homework_guardrail(ctx, agent, input_data):
    result = await Runner.run(guardrail_agent, input_data, context=ctx.context)
    final_output = result.final_output_as(HomeworkOutput)
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=not final_output.is_homework,
    )

# Create the main triage agent
triage_agent = Agent(
    name="Triage Agent",
    instructions="You determine which agent to use based on the user's homework question",
    handoffs=[history_tutor_agent, math_tutor_agent],
    input_guardrails=[
        InputGuardrail(guardrail_function=homework_guardrail),
    ],
)



async def main():
    # Test with a history question
    result = await Runner.run(triage_agent, "Who was the first president of the United States?")
    print("History question result:")
    print(result.final_output)
    print("\n")

    # Test with a math question
    result = await Runner.run(triage_agent, "What is the square root of 144? Please solve this homework question.")
    print("Math question result:")
    print(result.final_output)
    print("\n")

    # Test with a non-homework question
    result = await Runner.run(triage_agent, "What is the meaning of life?")
    print("Non-homework question result:")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
