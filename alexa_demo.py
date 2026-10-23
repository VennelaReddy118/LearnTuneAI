
import json
from pathlib import Path
from io import BytesIO

import requests
import streamlit as st
from pypdf import PdfReader

MCP_URL = "http://127.0.0.1:8000/mcp"
PROTOCOL_VERSION = "2025-11-25"

st.set_page_config(
    page_title="LearnTune AI",
    page_icon="🎵",
    layout="centered"
)

st.title("🎵 LearnTune AI")
st.subheader("Turn your study notes into learning songs")
st.write(
    "Enter a topic or upload a PDF. Generate educational lyrics, "
    "then listen to an available singing sample."
)


def read_response(response):
    try:
        return response.json()
    except ValueError:
        for line in response.text.splitlines():
            if line.startswith("data:"):
                try:
                    return json.loads(line[5:].strip())
                except json.JSONDecodeError:
                    continue
    return None


def mcp_request(payload, session_id=None):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "MCP-Protocol-Version": PROTOCOL_VERSION,
    }
    if session_id:
        headers["MCP-Session-Id"] = session_id

    response = requests.post(
        MCP_URL, headers=headers, json=payload, timeout=150
    )
    response.raise_for_status()
    return response


def generate_song(topic):
    init_response = requests.post(
        MCP_URL,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "MCP-Protocol-Version": PROTOCOL_VERSION,
        },
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {
                    "name": "LearnTune AI Demo",
                    "version": "1.0.0",
                },
            },
        },
        timeout=30,
    )
    init_response.raise_for_status()

    session_id = init_response.headers.get("mcp-session-id")
    if not session_id:
        raise RuntimeError("MCP server did not return a session ID.")

    mcp_request(
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        session_id,
    )

    response = mcp_request(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "create_learning_song",
                "arguments": {
                    "topic": topic,
                    "language": "English",
                    "style": "Pop",
                },
            },
        },
        session_id,
    )

    result = read_response(response)
    if not result or "result" not in result:
        raise RuntimeError("Unexpected response from MCP server.")

    tool_result = result["result"]
    lyrics = "\n\n".join(
        item.get("text", "")
        for item in tool_result.get("content", [])
        if item.get("type") == "text"
    )

    if tool_result.get("isError"):
        raise RuntimeError(lyrics or "Song generation failed.")

    return lyrics or "No lyrics were returned."


st.header("1. Choose your study material")

mode = st.radio(
    "Input method",
    ["Enter a topic", "Upload study notes (PDF)"],
    horizontal=True,
)

topic = ""

if mode == "Enter a topic":
    topic = st.text_input(
        "Learning topic",
        placeholder="e.g. Photosynthesis"
    )
else:
    uploaded_pdf = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"]
    )

    if uploaded_pdf:
        try:
            reader = PdfReader(BytesIO(uploaded_pdf.getvalue()))

            if reader.is_encrypted:
                st.error("This PDF is password-protected.")
            else:
                extracted_text = "\n".join(
                    page.extract_text() or ""
                    for page in reader.pages
                ).strip()

                if not extracted_text:
                    st.warning(
                        "No readable text found. Scanned PDFs need OCR."
                    )
                else:
                    st.success(
                        f"Extracted text from {len(reader.pages)} pages."
                    )
                    st.text_area(
                        "Notes preview",
                        extracted_text[:2500],
                        height=150,
                        disabled=True,
                    )
                    topic = (
                        "Create accurate, memorable educational pop-song "
                        "lyrics based on these study notes:\n\n"
                        + extracted_text[:12000]
                    )
        except Exception as error:
            st.error(f"Could not read the PDF: {error}")


st.header("2. Generate educational lyrics")

if st.button("🎵 Generate Learning Lyrics", type="primary"):
    if not topic.strip():
        st.warning("Enter a topic or upload a readable PDF first.")
    else:
        with st.spinner("Generating your educational lyrics..."):
            try:
                st.session_state["latest_lyrics"] = generate_song(topic)
                st.session_state["lyrics_error"] = ""
            except Exception as error:
                st.session_state["lyrics_error"] = str(error)

if st.session_state.get("lyrics_error"):
    st.error(st.session_state["lyrics_error"])

lyrics = st.session_state.get("latest_lyrics")

if lyrics:
    st.subheader("🎶 Your generated lyrics")
    st.markdown(lyrics)
    st.download_button(
        "Download lyrics (.txt)",
        data=lyrics,
        file_name="LearnTuneAI_lyrics.txt",
        mime="text/plain",
    )

    st.header("3. Listen to a singing sample")
    st.info(
        "These are pre-generated sample songs. They are not automatically "
        "created from the current topic or PDF."
    )

    project_folder = Path(__file__).resolve().parent
    samples = [
        ("Singing Sample 1", "output1.mp3"),
        ("Singing Sample 2", "output2.mp3"),
        ("Latest Singing Sample", "generated_song.mp3"),
    ]

    for title, filename in samples:
        audio_path = project_folder / filename
        if audio_path.is_file():
            st.subheader(title)
            audio_bytes = audio_path.read_bytes()
            st.audio(audio_bytes, format="audio/mpeg")
            st.download_button(
                f"Download {title}",
                data=audio_bytes,
                file_name=filename,
                mime="audio/mpeg",
                key=f"download_{filename}",
            )
        else:
            st.caption(f"Sample not found: {filename}")
