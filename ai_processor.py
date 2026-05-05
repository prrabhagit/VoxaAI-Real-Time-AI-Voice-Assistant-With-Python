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
    def _trim_history(self):
      #keep only the last MAX_HISTORY_TURNS, 2 messages
        max_msgs = MAX_HISTORY_TURNS * 2
        if len(self.conversation_history) > max_msgs:
            self.conversation_history = self.conversation_history[-max_msgs:]

    def _build_messages(self, user_text: str) -> list[dict]:
        self._trim_history()
        return (
            [{"role": "system", "content": SYSTEM_PROMPT}]
            + self.conversation_history
            + [{"role": "user", "content": user_text}]
        )


 #public
    def get_response(self, user_text: str) -> str:
        
      
        #Send the user's query to the LLM and return the assistant's reply.
        #Handles API errors and returns user-friendly messages.
        
        if not user_text.strip():
            return "Please say something for me to respond to."

        if OPENAI_API_KEY in ("", "_OPENAI_API_KEY_HERE_"):
            return (
                "Response unavailable. Please set your OpenAI API key in config.py or .env."
                "Please add your OpenAI API key to config.py or .env."
            )

        messages = self._build_messages(user_text)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=LLM_MAX_TOKENS,
                temperature=LLM_TEMPERATURE,
            )
            reply = response.choices[0].message.content.strip()

            # Update history
            self.conversation_history.append({"role": "user",      "content": user_text})
            self.conversation_history.append({"role": "assistant",  "content": reply})

            logger.info(f"LLM replied ({len(reply)} chars)")
            return reply

