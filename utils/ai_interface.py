from abc import ABC, abstractmethod
import fastapi_poe as fp
from openai import AsyncOpenAI

class AIInterface(ABC):
    @abstractmethod
    async def chat_completion(self, messages: list, **kwargs) -> tuple[bool, str]:
        pass

class OpenAIService(AIInterface):
    def __init__(self, api_key: str, api_base: str):
        self.client = AsyncOpenAI(api_key=api_key, base_url=api_base)

    async def chat_completion(self, messages: list, **kwargs) -> tuple[bool, str]:
        try:
            response = await self.client.chat.completions.create(
                messages=messages,
                model=kwargs.get('model', 'gpt-3.5-turbo'),
                temperature=kwargs.get('temperature', 0.7),
                max_tokens=kwargs.get('max_tokens', 1000)
            )
            return True, response.choices[0].message.content
        except Exception as e:
            return False, str(e)

class PoeService(AIInterface):
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def chat_completion(self, messages: list, **kwargs) -> tuple[bool, str]:
        try:
            poe_messages = []
            for msg in messages:
                role = "bot" if msg["role"] == "assistant" else msg["role"]
                poe_messages.append(fp.ProtocolMessage(
                    role=role,
                    content=msg["content"]
                ))

            response_content = ""
            async for partial in fp.get_bot_response(
                messages=poe_messages,
                bot_name=kwargs.get('model', 'gpt-3.5-turbo'),
                api_key=self.api_key
            ):
                response_content += partial.text

            return True, response_content
        except Exception as e:
            return False, str(e)
