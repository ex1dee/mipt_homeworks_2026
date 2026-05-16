import sys
from functools import wraps
from typing import List, Callable, Any

from chat_manager import ChatManager
from final_project.src.constants import Messages, DEFAULT_PAGE_SIZE
from final_project.src.utils import print_help, print_chat_history, clear_console
from utils import print_system, print_error, show_paged_chats, clear_chat, console


def command_error_handler(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print_error(str(e))

    return wrapper


@command_error_handler
def handle_new(manager: ChatManager, args: List[str]) -> None:
    name = ' '.join(args) if args else None
    session = manager.create_chat(name)

    clear_chat(session.name)
    print_system(Messages.CHAT_CREATED.format(name=session.name))


@command_error_handler
def handle_rename(manager: ChatManager, args: List[str]) -> None:
    is_specified_chat = args[0].isdigit() and len(args) > 1

    if is_specified_chat:
        display_idx = int(args[0])
        new_name = ' '.join(args[1:])
    else:
        display_idx = None
        new_name = ' '.join(args)

    manager.rename_chat(display_idx, new_name)

    if is_specified_chat:
        print_system(
            Messages.SPECIFIED_CHAT_RENAMED.format(display_idx=display_idx, new_name=new_name)
        )
    else:
        print_system(Messages.CURRENT_CHAT_RENAMED.format(new_name=new_name))


@command_error_handler
def handle_switch(manager: ChatManager, args: List[str]) -> None:
    if not args or not args[0].isdigit():
        print_error(Messages.SWITCH_USE)
        return

    manager.switch_chat(int(args[0]))
    session = manager.get_current_chat()

    clear_chat(session.name)
    print_chat_history(session.history)
    print_system(Messages.CHAT_SWITCHED.format(name=session.name))


@command_error_handler
def handle_delete(manager: ChatManager, args: List[str]) -> None:
    if args and not args[0].isdigit():
        print_error(Messages.DELETE_USE)
        return

    display_idx = int(args[0]) if (args and args[0].isdigit()) else None
    is_current_chat = manager.is_current_chat(display_idx)

    manager.delete_chat(display_idx)

    if is_current_chat:
        clear_chat(manager.get_current_chat().name)
        print_system(Messages.PREV_CHAT_DELETED)
    else:
        print_system(Messages.SPECIFIED_CHAT_DELETED.format(display_idx=display_idx))


@command_error_handler
def handle_delete_all(manager: ChatManager) -> None:
    manager.delete_all_chats()
    session = manager.create_chat()

    clear_chat(session.name)
    print_system(Messages.ALL_CHATS_DELETED)


@command_error_handler
def handle_clear(manager: ChatManager) -> None:
    manager.clear_current_chat()
    clear_chat(manager.get_current_chat().name)
    print_system(Messages.CHAT_CLEARED)


@command_error_handler
def handle_list(manager: ChatManager) -> None:
    if not manager.sessions:
        print_system(Messages.CHAT_LIST_EMPTY)
        return

    page = 1
    page_size = DEFAULT_PAGE_SIZE
    last_error = None

    while True:
        clear_console()
        show_paged_chats(manager.sessions, manager.current_idx, page, page_size)

        if last_error is not None:
            print_error(last_error)

        total_pages = (len(manager.sessions) - 1) // page_size + 1
        cmd = console.input(Messages.CHAT_LIST_USE.format(total_pages=total_pages)).strip().lower()

        if cmd in ('q', 'й'):
            break

        if cmd.isdigit():
            next_page = int(cmd)
            if 1 <= next_page <= total_pages:
                page = next_page
                last_error = None
            else:
                last_error = Messages.CHAT_LIST_INVALID_PAGE

    session = manager.get_current_chat()
    clear_chat(session.name)
    print_chat_history(session.history)


def handle_help() -> None:
    print_help(Messages.HELP_TEMPLATE)


def handle_exit() -> None:
    print_system('Завершение сессии...')
    sys.exit(0)
