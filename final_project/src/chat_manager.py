import json
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from final_project.src.constants import ROLE_SYSTEM, DEFAULT_CHATS_DIR, Messages
from final_project.src.exceptions import NoActiveSessionError, SessionNotFoundError


@dataclass
class ChatSession:
    name: str
    system_prompt: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    history: List[Dict[str, str]] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def __post_init__(self) -> None:
        if not self.history:
            self.history.append({"role": ROLE_SYSTEM, "content": self.system_prompt})

    def add_message(self, role: str, content: str) -> None:
        self.history.append({"role": role, "content": content})

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "history": self.history,
            "created_at": self.created_at
        }


class ChatManager:
    def __init__(self, system_prompt: str, storage_dir: Path = DEFAULT_CHATS_DIR) -> None:
        self.storage_dir = storage_dir
        self.system_prompt = system_prompt

        self.sessions: List[ChatSession] = []
        self.current_idx: Optional[int] = None

        self._init_storage()
        self._load_sessions()

    def get_current_chat(self) -> ChatSession:
        if self.current_idx is None:
            raise NoActiveSessionError

        return self.sessions[self.current_idx]

    def create_chat(self, name: Optional[str] = None) -> ChatSession:
        if name is None:
            display_idx = len(self.sessions) + 1
            name = f"{Messages.NEW_CHAT_PREFIX}{display_idx}"

        session = ChatSession(name=name, system_prompt=self.system_prompt)
        self.sessions.append(session)
        self._save_chat(session)

        self.current_idx = len(self.sessions) - 1

        return session

    def switch_chat(self, display_idx: Optional[int]) -> None:
        self.current_idx = self._get_idx_by_specified(display_idx)

    def rename_chat(self, display_idx: Optional[int], new_name: str) -> None:
        idx = self._get_idx_by_specified(display_idx)
        session = self.sessions[idx]

        session.name = new_name
        self._save_chat(session)

    def delete_chat(self, display_idx: Optional[int] = None) -> None:
        idx = self._get_idx_by_specified(display_idx)
        session_to_delete = self.sessions[idx]
        file_to_delete = self._get_chat_filename(session_to_delete.id)

        try:
            if os.path.exists(file_to_delete):
                os.remove(file_to_delete)
        except Exception as e:
            print(Messages.CHAT_DELETE_ERROR.format(error=e))

        self.sessions.pop(idx)

        if not self.sessions:
            self.create_chat()
        else:
            if idx == self.current_idx or self.current_idx is None:
                self.current_idx = len(self.sessions) - 1
            elif idx < self.current_idx:
                self.current_idx -= 1

    def delete_all_chats(self) -> None:
        for filename in os.listdir(self.storage_dir):
            file_path = os.path.join(self.storage_dir, filename)

            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(Messages.CHAT_DELETE_ERROR.format(error=e))

        self.sessions.clear()
        self.current_idx = None

    def is_current_chat(self, display_idx: Optional[int]) -> bool:
        if display_idx is None:
            return True

        return self.current_idx == display_idx - 1

    def add_message_to_current(self, role: str, content: str) -> None:
        if self.current_idx is None:
            raise NoActiveSessionError

        session = self.sessions[self.current_idx]
        session.add_message(role, content)
        self._save_chat(session)

    def clear_current_chat(self) -> None:
        session = self.get_current_chat()
        session.history = [session.history[0]]
        self._save_chat(session)

    def limit_history(self, token_count: int, max_tokens: int) -> None:
        session = self.get_current_chat()

        while token_count > max_tokens:
            if len(session.history) > 1:
                session.history.pop(1)
            else:
                break

    def _load_sessions(self) -> None:
        if not os.path.exists(self.storage_dir):
            return

        loaded_sessions = []

        for filename in os.listdir(self.storage_dir):
            if filename.startswith("chat_") and filename.endswith(".json"):
                file_path = os.path.join(self.storage_dir, filename)

                try:
                    with open(file_path, "r", encoding='utf-8') as file:
                        data = json.load(file)

                        session = ChatSession(
                            id=data["id"],
                            name=data["name"],
                            history=data["history"],
                            created_at=data["created_at"],
                            system_prompt=self.system_prompt
                        )

                        loaded_sessions.append(session)
                except Exception as e:
                    print(Messages.LOAD_CHAT_ERROR.format(filename=filename, error=e))

        self.sessions = sorted(loaded_sessions, key=lambda x: x.created_at)

        if self.sessions:
            self.current_idx = len(self.sessions) - 1

    def _init_storage(self) -> None:
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)

    def _save_chat(self, session: ChatSession) -> None:
        file_path = self._get_chat_filename(session.id)

        try:
            with open(file_path, "w", encoding='utf-8') as file:
                json.dump(session.to_dict(), file, ensure_ascii=False, indent=4)
        except Exception as e:
            print(Messages.SAVE_CHAT_ERROR.format(error=e))

    def _get_chat_filename(self, chat_id: str) -> str:
        return os.path.join(self.storage_dir, f"chat_{chat_id}.json")

    def _get_idx_by_specified(self, display_idx: Optional[int]) -> int:
        if display_idx is None:
            if self.current_idx is None:
                raise NoActiveSessionError
            return self.current_idx

        idx = display_idx - 1

        if idx < 0 or idx >= len(self.sessions):
            raise SessionNotFoundError(display_idx)

        return idx
