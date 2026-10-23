
import os
import time
import requests
from dotenv import load_dotenv
from mcp.server import MCPServer

load_dotenv()

mcp = MCPServer("LearnTune AI")


@mcp.tool()
def create_learning_song(
    topic: str,
    language: str = "English",
    style: str = "Pop"
) -> str:
    """Generate educational song lyrics about a topic."""

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "Error: GEMINI_API_KEY is missing from .env."

    prompt = (
        f"Write original educational song lyrics about {topic}. "
        f"Language: {language}. Style: {style}. "
        "Include a verse and a catchy chorus. "
        "Make the lyrics accurate and easy for students to remember."
    )

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
    	"gemini-3.6-flash:generateContent"
    )

    for attempt in range(3):
        try:
            response = requests.post(
                url,
                headers={
                    "x-goog-api-key": api_key,
                    "Content-Type": "application/json",
                },
                json={
                    "contents": [
                        {"parts": [{"text": prompt}]}
                    ]
                },
                timeout=120,
            )

            if response.status_code in (429, 500, 502, 503, 504):
                if attempt < 2:
                    time.sleep(2 * (attempt + 1))
                    continue

            response.raise_for_status()
            data = response.json()

            return data["candidates"][0]["content"]["parts"][0]["text"]

        except requests.RequestException as error:
            if attempt < 2:
                time.sleep(2 * (attempt + 1))
                continue
            return f"Gemini request failed after 3 attempts: {error}"

        except (KeyError, IndexError, TypeError, ValueError) as error:
            return f"Could not read Gemini response: {error}"

    return "Gemini is temporarily unavailable. Please try again later."


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
