
# LearnTune AI 🎵

LearnTune AI is an AI-powered learning assistant that helps students remember concepts by transforming study topics and PDF notes into educational song lyrics.

## Features

- Enter a topic to generate educational lyrics.
- Upload text-based PDF study notes.
- Extract text from uploaded PDFs.
- Generate memorable lyrics using the Gemini API.
- Listen to pre-generated singing samples.
- Download generated lyrics and available audio samples.
- Expose the lyric-generation functionality through an MCP server.

## Technologies Used

- Python
- Streamlit
- Google Gemini API
- Model Context Protocol (MCP)
- PyPDF

## Project Files

- `app.py` — Main Streamlit application
- `alexa_demo.py` — Topic and PDF-based learning demo
- `server.py` — MCP server with the learning-song tool
- `test_music.py` — Music-related test script
- `requirements.txt` — Python dependencies

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/VennelaReddy118/LearnTuneAI.git
cd LearnTuneAI
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

On Windows, activate it using:

```cmd
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Gemini API key

Create a `.env` file in the project directory containing:

```text
GEMINI_API_KEY=your_api_key_here
```

Replace the placeholder with your own API key. Never upload your actual `.env` file or API key to GitHub.

### 5. Run LearnTune AI

Start the MCP server in one terminal:

```bash
python server.py
```

Start the Streamlit demo in another terminal:

```bash
streamlit run alexa_demo.py
```

Open the local URL shown in the terminal.

## Current Limitations

The application generates educational lyrics from topics or readable PDF notes. Audio playback currently uses pre-generated singing samples; automatic singing generation from newly generated lyrics has not been integrated into the app. Scanned PDFs requiring OCR are not supported.

The local MCP tool has been tested. A real Alexa+ connection has not yet been verified.
