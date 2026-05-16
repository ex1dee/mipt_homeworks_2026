import os
from pathlib import Path
from typing import Dict

from dotenv import load_dotenv

from final_project.src.constants import PROMPTS_DIR

load_dotenv()

GIGACHAT_CREDENTIALS = os.getenv('GIGACHAT_CREDENTIALS', '')
GIGACHAT_MODEL = os.getenv('GIGACHAT_MODEL', 'GigaChat')
GIGACHAT_VERIFY_SSL = os.getenv('GIGACHAT_VERIFY_SSL', 'False').lower() == 'true'
MAX_TOKENS = int(os.getenv('MAX_TOKENS', '4000'))


def load_all_prompts() -> Dict[str, str]:
    prompts_map: Dict[str, str] = {}

    for file_path in PROMPTS_DIR.glob('*.txt'):
        with open(file_path, 'r', encoding='utf-8') as file:
            prompts_map[file_path.stem] = file.read().strip()

    return prompts_map


PROMPTS = load_all_prompts()
