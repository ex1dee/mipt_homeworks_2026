import os
from typing import List, Any, Optional, Dict
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from final_project.src.constants import APP_NAME, ROLE_USER, ROLE_ASSISTANT, Messages

console = Console(force_terminal=True)


def clear_chat(current_name: str) -> None:
    clear_console()

    console.print(
        Panel(
            f'Текущий чат: [bold white]{current_name}[/bold white]',
            subtitle=f'[{APP_NAME}]',
            border_style='blue',
            expand=True,
            padding=(0, 2),
        )
    )


def clear_console() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')


def print_system(text: str) -> None:
    console.print(f'\n[bold blue][{APP_NAME}][/bold blue] {text}', highlight=False)


def print_error(text: str) -> None:
    console.print(f'\n[bold red][Ошибка][/bold red] {text}', highlight=False)


def print_help(text: str) -> None:
    console.print(Panel(text, title='Справка', expand=False, border_style='cyan'))


def show_paged_chats(
    sessions: List[Any], current_idx: Optional[int], page: int = 1, page_size: int = 10
) -> None:
    total_pages = (len(sessions) - 1) // page_size + 1
    table = Table(
        title=f'Список ваших чатов ({page}/{total_pages})', title_style='bold cyan', expand=True
    )
    table.add_column('ID', justify='center', style='cyan')
    table.add_column('Название', style='white')
    table.add_column('Дата создания', justify='right', style='dim')

    start = (page - 1) * page_size
    end = start + page_size

    for i, session in enumerate(sessions[start:end], start=start + 1):
        is_current = (i - 1) == current_idx
        name_style = f'[bold green]● {session.name}[/bold green]' if is_current else session.name
        table.add_row(str(i), name_style, session.created_at)

    console.print(table)


def print_chat_history(history: List[Dict[str, str]]) -> None:
    for msg in history[1:]:
        role = msg['role']
        content = msg['content']

        if role == ROLE_USER:
            console.print(f'{Messages.USER_PREFIX}{content}')
        elif role == ROLE_ASSISTANT:
            print_assistant_prefix()
            console.print(Markdown(content))


def print_user_prefix() -> None:
    console.print(Messages.USER_PREFIX)


def print_assistant_prefix() -> None:
    console.print(Messages.ASSISTANT_PREFIX)
