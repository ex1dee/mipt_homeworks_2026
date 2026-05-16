class ChatManagerError(Exception):
    pass


class NoActiveSessionError(ChatManagerError):
    def __init__(
        self,
        message: str = 'Активный чат не выбран. Создайте новый (/new) или переключитесь (/switch)',
    ):
        super().__init__(message)


class SessionNotFoundError(ChatManagerError):
    def __init__(self, chat_id: int):
        message = f'Чат с ID {chat_id} не найден'
        super().__init__(message)


class GigaChatError(Exception):
    pass


class GigaChatCredentialsNotFound(GigaChatError):
    def __init__(self, message: str = 'Учетные данные GigaChat не найдены. Проверьте .env файл'):
        super().__init__(message)


class GigaChatApiError(GigaChatError):
    pass


class GigaChatGetStreamResponseError(GigaChatApiError):
    def __init__(self, cause: Exception):
        message = f'[GigaChat] Не удалось прочитать потоковый ответ: {str(cause)}'
        super().__init__(message)


class GigaChatGenerateTitleError(GigaChatApiError):
    def __init__(self, cause: Exception):
        message = f'[GigaChat] Не удалось сгенерировать название чата: {str(cause)}'
        super().__init__(message)


class GigaChatGetTokenCountError(GigaChatApiError):
    def __init__(self, cause: Exception):
        message = f'[GigaChat] Не удалось вычислить количество токенов сообщений: {str(cause)}'
        super().__init__(message)
