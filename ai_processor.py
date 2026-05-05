import logging
from openai import OpenAI, APIError, AuthenticationError, RateLimitError

from config import (
    OPENAI_API_KEY,
    LLM_MODEL,
    LLM_MAX_TOKENS,
    LLM_TEMPERATURE,
    SYSTEM_PROMPT,
)

logger = logging.getLogger(__name__)
# Maximum conversation turns i.e. user + assistant = 2 messages per turn
MAX_HISTORY_TURNS = 6


class AIProcessor:
    #sends queries to an LLM and returns conversational responses

    def __init__(self):
        if OPENAI_API_KEY in ("", "OPENAI_API_KEY_HERE"):
            logger.warning(
                "OPENAI_API_KEY is not set. AI responses will be unavailable. "
                "Set it in config.py or .env"
            )

        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = LLM_MODEL
        self.conversation_history: list[dict] = []
        logger.info(f"AIProcessor ready — model: {self.model}")
#private


