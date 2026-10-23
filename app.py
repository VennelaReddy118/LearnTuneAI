
import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

st.set_page_config(
    page_title="LearnTune AI",
    page_icon="🎵",
    layout="centered"
)

st.title("🎵 LearnTune AI")
st.subheader("Learn it. Sing it. Remember it!")

st.write(
    "Turn any study topic into an educational song "
    "in your preferred language."
)

topic = st.text_input(
    "Enter your study topic",
    placeholder="Example: Photosynthesis"
)

language = st.selectbox(
    "Choose your language",
    ["English", "Telugu", "Hindi", "Kannada"]
)

style = st.selectbox(
    "Choose a song style",
    ["Pop", "Rap", "Rhyming song", "Fun educational song"]
)

if st.button("🎶 Generate My Learning Song"):
    if not topic.strip():
        st.warning("Please enter a topic first.")

    elif not API_KEY:
        st.error(
            "API key not found. Check that your .env "
            "file is in the same folder as app.py."
        )

    else:
        prompt = f"""
You are LearnTune AI, an educational songwriting assistant.

Topic: {topic}
Language: {language}
Song style: {style}

Create an original educational song that helps students
understand and remember this topic.

Requirements:
1. Give the song a catchy title.
2. Include two short verses and a memorable chorus.
3. Explain the topic accurately using simple language.
4. Write the lyrics in the selected language.
5. Do not invent facts to make rhymes.
6. Create three quiz questions about the topic.
7. Provide an answer key after the questions.

Separate the song, quiz, and answer key with headings.
"""

        with st.spinner("🎵 Gemini is creating your song lyrics..."):
            try:
                model = "gemini-3.8-flash"

                url = (
                    "https://generativelanguage.googleapis.com/"
                    f"v1beta/models/{model}:generateContent"
                )

                response = requests.post(
                    url,
                    headers={
                        "x-goog-api-key": API_KEY,
                        "Content-Type": "application/json"
                    },
                    json={
                        "contents": [
                            {
                                "parts": [
                                    {"text": prompt}
                                ]
                            }
                        ]
                    },
                    timeout=90
                )

                if response.ok:
                    data = response.json()
                    candidates = data.get("candidates", [])

                    if candidates:
                        parts = candidates[0].get(
                            "content", {}
                        ).get("parts", [])

                        answer = "\n".join(
                            part["text"]
                            for part in parts
                            if "text" in part
                        )

                        if answer:
                            st.success("Your learning song is ready!")
                            st.markdown(answer)
                        else:
                            st.error("The AI returned an empty response.")
                    else:
                        st.error(
                            "No song was generated. Try another topic."
                        )

                else:
                    st.error(
                        f"Gemini API error: HTTP {response.status_code}"
                    )
                    st.write(response.text[:1500])

            except requests.RequestException as error:
                st.error("Unable to connect to Gemini.")
                st.caption(str(error))
