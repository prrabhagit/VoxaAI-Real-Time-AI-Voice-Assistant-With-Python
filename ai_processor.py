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

