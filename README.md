#  VoxaAI – Intelligent Voice Assistant in Python

VoxaAI is a Python-based AI-powered voice assistant that listens to your voice, understands your queries, and responds intelligently in real time.

It combines speech recognition, large language models (LLMs), and text-to-speech to create a seamless and interactive conversational experience.

---

##  Features

*  Real-time Speech-to-Text (voice input)
*  AI-powered intelligent responses
*  Natural Text-to-Speech (voice output)
*  Continuous listening mode
*  Smart conversational handling
*  Clean and modular code structure

---

##  Tech Stack

* **Python 3.x**
* **SpeechRecognition / Whisper**
* **OpenAI API (or compatible LLM)**
* **pyttsx3 / gTTS**

---

##  Project Structure

```
VoxaAI/
│── main.py
│── speech_input.py
│── ai_engine.py
│── speech_output.py
│── config.py
│── requirements.txt
│── README.md
```

---

##  Installation

### 1. Clone the Repository

```bash
git clone https://github.com/prrabhagit/voxaai.git
cd voxaai
```

###  Create Virtual Environment

```bash
python -m venv venv
```

Activate it:

* **Windows**

```bash
venv\Scripts\activate
```

* **Linux / Mac**

```bash
source venv/bin/activate
```

###  Install Dependencies

```bash
pip install -r requirements.txt
```

---

##  Setup API Key

Create a `.env` file in the root directory:

```
OPENAI_API_KEY=your_api_key_here
```

---

##  Usage

Run the assistant:

```bash
python main.py
```

Then speak naturally:

* “What is artificial intelligence?”
* “Explain recursion in simple terms”
* “Tell me a fun fact”

---

##  Limitations

* Requires internet connection for AI responses
* Performance depends on microphone quality
* No wake-word detection yet

---

##  Future Improvements

* Wake word detection (e.g., “Hey Voxa”)
* GUI-based interface
* Offline AI model integration
* Multi-language support (English + Nepali)
* Context-aware memory for conversations
* App-based automation features using APIs

---

##  Contributing

Contributions are welcome. Feel free to fork the repo and submit pull requests.

---

##  License

This project is licensed under the MIT License.

---

## Author

Prabha
GitHub: https://github.com/prrabhagit

---
