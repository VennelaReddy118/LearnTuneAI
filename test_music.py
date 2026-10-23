
import os
import base64
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=api_key)

prompt = """
Create a cheerful 30-second educational pop song about photosynthesis.
Include singing vocals, a catchy melody, light drums and guitar.
Use simple English lyrics suitable for students.
"""

print("Sending request to Google Lyria...")

try:
    interaction = client.interactions.create(
        model="lyria-3-clip-preview",
        input=prompt,
    )

    audio = interaction.output_audio

    if audio and audio.data:
        with open("test_song.mp3", "wb") as f:
            f.write(base64.b64decode(audio.data))
        print("Success! Song saved as test_song.mp3")
    else:
        print("No audio returned. Check the API response.")

except Exception as e:
    print("Music generation failed:")
    print(type(e).__name__, str(e))
