from pathlib import Path

ROLE_ASSISTANT = "assistant"
ROLE_SYSTEM = "system"
ROLE_USER = "user"

BASE_DIR = Path(__file__).resolve().parent.parent
PROMPTS_DIR = BASE_DIR / "prompts"
DEFAULT_CHATS_DIR = BASE_DIR / "chats"

DEFAULT_PAGE_SIZE = 5

APP_NAME = "GigaVibe"


class Messages:
    STARTED = "Чат-бот запущен. Введите /help для списка команд"
    USER_PREFIX = f"\n[bold cyan]>>> [/]"
    ASSISTANT_PREFIX = f"\n[bold magenta]🤖 GigaVibe:[/]"
    NEW_CHAT_PREFIX = "Новый чат №"

    CHAT_CREATED = "Создан чат: [bold]{name}[/bold]"
    CHAT_SWITCHED = "Переключено на чат: [bold]{name}[/bold]"
    CHAT_CLEARED = "История текущего чата очищена"
    PREV_CHAT_DELETED = "Предыдущий чат был успешно удален"
    SPECIFIED_CHAT_DELETED = "Чат №{display_idx} был успешно удален"
    ALL_CHATS_DELETED = "Все чаты были удалены"
    CURRENT_CHAT_RENAMED = "Текущий чат переименован в '{new_name}'"
    SPECIFIED_CHAT_RENAMED = "Чат №{display_idx} переименован в '{new_name}'"

    CHAT_LIST_EMPTY = "Список чатов пуст"
    CHAT_LIST_INVALID_PAGE = "Нет такой страницы"

    PROCESS_RESPONSE_ERROR = "Ошибка при получении ответа: {error}"
    CRITICAL_START_ERROR = "Критический сбой при запуске: {error}"
    CHAT_DELETE_ERROR = "Ошибка при удалении чата: {error}"
    LOAD_CHAT_ERROR = "Ошибка при загрузке файла сессии '{filename}': {error}"
    SAVE_CHAT_ERROR = "Ошибка при сохранении чата: {error}"
    UNKNOWN_ERROR = "Неизвестная ошибка: {error}"
    API_ERROR = "Ошибка API: {error}"

    UNKNOWN_COMMAND = "Неизвестная команда. Попробуйте /help"
    CHAT_LIST_USE = "\n[bold yellow]Листать (1-{total_pages}), или 'q' для выхода: [/]"
    RENAME_USE = "Использование: /rename <Имя> или /rename <ID> <Имя>"
    DELETE_USE = "Использование: /delete [ID]"
    SWITCH_USE = "Использование: /switch <ID>"

    HELP_TEMPLATE = """
    [bold cyan]Доступные команды:[/bold cyan]
      [bold yellow]/new[/bold yellow] \[Имя]           — Создать новый чат
      [bold yellow]/list[/bold yellow]                — Список чатов 
      [bold yellow]/switch[/bold yellow] <ID>         — Переключиться на чат по ID
      [bold yellow]/rename[/bold yellow] \[ID] <Имя>   — Переименовать чат (текущий или по ID)
      [bold yellow]/delete[/bold yellow] \[ID]         — Удалить чат (текущий или по ID)
      [bold yellow]/delete-all[/bold yellow] \[ID]     — Удалить все чаты
      [bold yellow]/clear[/bold yellow]               — Очистить историю текущего чата
      [bold yellow]/exit[/bold yellow]                — Завершить работу
    """
