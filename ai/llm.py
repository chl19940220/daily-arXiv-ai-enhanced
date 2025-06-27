
import os
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

def get_llm(model_name: str, api_key: str, base_url: str = None):
    """
    根据环境变量获取 LLM 实例。

    Args:
        model_name: 模型名称。
        api_key: API 密钥。
        base_url: 模型的 base_url (可选)。

    Returns:
        LLM 实例。
    """
    if "gemini" in model_name.lower():
        return ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key)
    else:
        return ChatOpenAI(model=model_name, api_key=api_key, base_url=base_url)
