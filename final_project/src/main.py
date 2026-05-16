import sys
from rich.live import Live
from rich.markdown import Markdown

from final_project.src.config import PROMPTS, MAX_TOKENS
from final_project.src.chat_manager import ChatManager
from final_project.src.api import GigaChatAdapter
from final_project.src.constants import Messages, ROLE_USER, ROLE_ASSISTANT
from final_project.src.exceptions import GigaChatError
from final_project.src.utils import (
    console,
    clear_chat,
    print_system,
    print_error,
    print_assistant_prefix,
)
from final_project.src.commands import (
    handle_new,
    handle_list,
    handle_switch,
    handle_rename,
    handle_delete,
    handle_clear,
    handle_help,
    handle_exit,
    handle_delete_all,
)


def process_ai_response(user_text: str, manager: ChatManager, api: GigaChatAdapter):
    try:
        manager.add_message_to_current(ROLE_USER, user_text)
        session = manager.get_current_chat()

        token_count = api.get_token_count(session.history)
        manager.limit_history(token_count, MAX_TOKENS)

        print_assistant_prefix()

        full_response = ''
        with Live('', refresh_per_second=12, console=console, vertical_overflow='visible') as live:
            for chunk in api.get_stream_response(session.history):
                full_response += chunk
                live.update(Markdown(full_response))

        manager.add_message_to_current(ROLE_ASSISTANT, full_response)

        if len(session.history) >= 3 and Messages.NEW_CHAT_PREFIX in session.name:
            new_name = api.generate_chat_title(user_text)

            if new_name:
                manager.rename_chat(None, new_name)
    except Exception as e:
        print_error(Messages.PROCESS_RESPONSE_ERROR.format(error=e))


def main():
    try:
        api = GigaChatAdapter()
        system_prompt = PROMPTS['system_main']

        manager = ChatManager(system_prompt=system_prompt)

        if not manager.sessions:
            manager.create_chat()

        current_chat = manager.get_current_chat()
        clear_chat(current_chat.name)
        print_system(Messages.STARTED)

        while True:
            try:
                user_input = console.input(Messages.USER_PREFIX).strip()

                if not user_input:
                    continue

                if user_input.startswith('/'):
                    parts = user_input.split()
                    cmd = parts[0].lower()
                    args = parts[1:]

                    match cmd:
                        case '/new':
                            handle_new(manager, args)
                        case '/list':
                            handle_list(manager)
                        case '/switch':
                            handle_switch(manager, args)
                        case '/rename':
                            handle_rename(manager, args)
                        case '/delete':
                            handle_delete(manager, args)
                        case '/delete-all':
                            handle_delete_all(manager)
                        case '/clear':
                            handle_clear(manager)
                        case '/help':
                            handle_help()
                        case '/exit':
                            handle_exit()
                        case _:
                            print_error(Messages.UNKNOWN_COMMAND)
                else:
                    process_ai_response(user_input, manager, api)
            except KeyboardInterrupt, EOFError:
                handle_exit()
            except GigaChatError as e:
                print_error(Messages.API_ERROR.format(error=e))
            except Exception as e:
                print_error(Messages.UNKNOWN_ERROR.format(error=e))

    except Exception as e:
        print(Messages.CRITICAL_START_ERROR.format(error=e))
        sys.exit(1)


if __name__ == '__main__':
    main()
