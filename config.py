
#config.py — Central configuration for the AI Voice Assistant.
#Edit this file to customise behaviour without touching module code.


import os
from dotenv import load_dotenv

load_dotenv()  # Load .env if present

# API Keys 
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "_OPENAI_API_KEY_HERE")

# LLM Settings 
LLM_MODEL:       str = os.getenv("LLM_MODEL", "gpt-4o")
LLM_MAX_TOKENS:  int = int(os.getenv("LLM_MAX_TOKENS", "403"))
LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.5"))


