
#AI Voice Assistant — Main Entry Point
#Orchestrates speech input, AI processing, and speech output.
#Run this file to start the assistant.


import time
import logging
from modules.speech_input import SpeechInput
from modules.ai_processor import AIProcessor
from modules.speech_output import SpeechOutput
from config import WAKE_WORD, LOG_LEVEL, LOG_FILE

# Logging Setup 
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("main")

