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

spanish_agent = Agent(
    name="Spanish agent",
    instructions="You translate the user's message to Spanish",
)

french_agent = Agent(
    name="French agent",
    instructions="You translate the user's message to French",
)

agent = Agent(
    name="FinancialXAgent",
    instructions=(
        "You are a specialized Financial X Twitter agent. Your task is to analyze provided tweets, including original posts, comments, and replies, "
        "to determine if they relate to financial topics such as stocks, investments, market trends, economic news, or financial advice. "
        "If the content is financial, provide clear, factual, and concise responses in tweet format (under 280 characters). "
        "If the content is not financial, return exactly <not_financial_x_post>. "
        "If there is a post image on post will be given as <Post Image> tag. "
        "Do not ask any follow-up or clarifying questions. If the input is unclear, respond with 'Your question is not clear' without requesting more details."
        "Try to not repeat post itself give the answer of question."
        "Don't additional hashtags to your answer. But read hastags of post."
    ),
    model="gpt-4o-mini"
)
async def main():
    inputPrompt = """
    Post Owner: "Yatirim101"
    <Post Image> Çin'de hangi alanda (elektrikli araçlar, insansı robotlar, akıllı telefonlar, düşük seviye çipler vb.) hangi şirketler iş yapıyor.Bu şirketler küresel pazara erişim gücüyle fiyat-performans ürünlerle dünya pazarını doldurma potansiyeline sahip.Kaydedin lazım olur.   
    Question: "Bu ne gibi bir firsat olusturabilir?"
    """
    result = await Runner.run(agent, input=inputPrompt)
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())