import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel, RunConfig, set_tracing_disabled

load_dotenv()
set_tracing_disabled(disabled=True)

groq_api_key = os.getenv("GROQ_API_KEY") or os.getenv("GEMINI_API_KEY")

external_client = AsyncOpenAI(
    api_key=groq_api_key,
    base_url=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
)

model = OpenAIChatCompletionsModel(
    model="openai/gpt-oss-120b",
    openai_client=external_client
)

config = RunConfig(
    model=model,
    model_provider=external_client,
)
