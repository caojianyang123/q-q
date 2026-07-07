import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()


def get_llm(temperature: float = 0.7):
    return ChatOpenAI(
        model=os.getenv("MODEL_NAME", "qwen3.7-plus"),
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        temperature=temperature,
    )
