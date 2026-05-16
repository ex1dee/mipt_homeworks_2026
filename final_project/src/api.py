import time
from typing import Generator


class GigaChatAdapter:
    """Заглушка API для отладки интерфейса и логики чатов."""

    def __init__(self) -> None:
        # В заглушке нам не нужны реальные учетные данные
        pass

    def get_stream_response(self, history: list[dict]) -> Generator[str, None, None]:
        """Имитирует потоковую выдачу ответов на основе последнего сообщения."""
        last_user_message = ''
        for msg in reversed(history):
            if msg['role'] == 'user':
                last_user_message = msg['content'].lower()
                break

        # Логика ответов-заглушек
        response_text = 'Я пока не знаю, что на это ответить в режиме заглушки. 🤖'

        if 'привет' in last_user_message:
            response_text = 'Привет! 😊 Как настроение, чем займёмся?'
        elif 'hello world' in last_user_message and 'masm' in last_user_message:
            response_text = (
                'Вот пример простой программы «Hello, World!» на MASM '
                '(Microsoft Macro Assembler) для 32-битного приложения под Windows:\n\n'
                '```asm\n'
                '.386\n'
                '.model flat, stdcall\n'
                'option casemap:none\n\n'
                'include \\masm32\\include\\windows.inc\n'
                'include \\masm32\\include\\kernel32.inc\n'
                'includelib \\masm32\\lib\\kernel32.lib\n\n'
                'include \\masm32\\include\\user32.inc\n'
                'includelib \\masm32\\lib\\user32.lib\n\n'
                '.data\n'
                "    msg db 'Hello, World!', 0\n\n"
                '.code\n'
                'start:\n'
                '    invoke MessageBox, 0, addr msg, addr msg, 0\n'
                '    invoke ExitProcess, 0\n\n'
                'end start\n'
                '```'
            )

        # Имитируем задержку сети и посимвольный вывод
        for char in response_text:
            yield char
            time.sleep(0.01)  # Скорость появления букв

    def generate_chat_title(self, first_message: str) -> str:
        """Имитирует работу суммаризатора названий."""
        msg = first_message.lower()
        if 'привет' in msg:
            return 'Знакомство'
        if 'masm' in msg:
            return 'Ассемблер Hello World'
        return 'Новое обсуждение'

    @staticmethod
    def get_token_count(text: str) -> int:
        """
        Считает токены.
        В реальном API это будет self.client.get_tokens_count(text).
        В заглушке используем простую формулу: 1 токен ~= 4 символа для кириллицы.
        """
        return len(text) // 4
