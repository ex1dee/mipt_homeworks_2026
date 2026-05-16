from typing import Dict, List, Generator

from gigachat import GigaChat

from final_project.src.config import (
    GIGACHAT_CREDENTIALS,
    GIGACHAT_MODEL,
    GIGACHAT_VERIFY_SSL,
    PROMPTS,
)
from final_project.src.constants import ROLE_SYSTEM
from final_project.src.exceptions import (
    GigaChatCredentialsNotFound,
    GigaChatGetStreamResponseError,
    GigaChatGenerateTitleError,
    GigaChatGetTokenCountError,
)


class GigaChatAdapter:
    def __init__(self) -> None:
        if not GIGACHAT_CREDENTIALS:
            raise GigaChatCredentialsNotFound()

        self.client = GigaChat(
            credentials=GIGACHAT_CREDENTIALS,
            model=GIGACHAT_MODEL,
            verify_ssl_certs=GIGACHAT_VERIFY_SSL,
        )

    def get_stream_response(self, messages: List[Dict[str, str]]) -> Generator[str, None, None]:
        try:
            for chunk in self.client.stream(messages=messages):
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except Exception as e:
            raise GigaChatGetStreamResponseError(e)

    def generate_chat_title(self, first_user_message: str) -> str:
        prompt = PROMPTS['generate_title'].format(text=first_user_message)
        messages = [{'role': ROLE_SYSTEM, 'content': prompt}]

        try:
            response = self.client.chat(messages=messages)
            title = response.choices[0].message.content.strip()
            return title.strip('"').strip("'")
        except Exception as e:
            raise GigaChatGenerateTitleError(e)

    def get_token_count(self, messages: List[Dict[str, str]]) -> int:
        input_data = [msg['content'] for msg in messages]

        try:
            results = self.client.tokens_count(input=input_data)
            return sum(item.tokens for item in results)
        except Exception as e:
            raise GigaChatGetTokenCountError(e)
