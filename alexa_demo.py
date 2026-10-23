
import json
import streamlit as st
import requests
from pypdf import PdfReader
from io import BytesIO

MCP_URL = "http://127.0.0.1:8000/mcp"
PROTOCOL_VERSION = "2025-11-25"

st.set_page_config(
    page_title="LearnTune AI",
    page_icon="🎵",
    layout="centered"
)

st.title("🎵 LearnTune AI")
st.subheader("Turn your study notes into learning songs!")
st.write("Enter a topic or upload a PDF containing your study notes.")

mode = st.radio(
    "Choose your input",
    ["Enter a topic", "Upload study notes (PDF)"],
    horizontal=True
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
        raise RuntimeError("The MCP server did not return a session ID.")

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
        raise RuntimeError("Unexpected response from the MCP server.")

    tool_result = result["result"]
    lyrics = "\n\n".join(
        item.get("text", "")
        for item in tool_result.get("content", [])
        if item.get("type") == "text"
    )

    if tool_result.get("isError"):
        raise RuntimeError(lyrics or "The song tool reported an error.")

    return lyrics or "No lyrics were returned."


topic = ""

if mode == "Enter a topic":
    topic = st.text_input(
        "Learning topic",
        placeholder="e.g. Photosynthesis"
    )

else:
    uploaded_pdf = st.file_uploader(
        "Upload your study notes",
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
                        "No readable text found. "
                        "Scanned PDFs need OCR, which is not included yet."
                    )
                else:
                    st.success(
                        f"Extracted text from {len(reader.pages)} pages."
                    )
                    st.text_area(
                        "Preview of your extracted notes",
                        extracted_text[:3000],
                        height=180,
                        disabled=True
                    )
                    topic = (
                        "Create educational song lyrics based on these "
                        "study notes. Preserve the important facts and "
                        "terms, and make the lyrics easy to remember:\n\n"
                        + extracted_text[:12000]
                    )
        except Exception as error:
            st.error(f"Could not read this PDF: {error}")


if st.button("🎵 Generate Learning Song", type="primary"):
    if not topic.strip():
        st.warning("Please enter a topic or upload a readable PDF.")
    else:
        with st.spinner("Creating your educational song..."):
            try:
                lyrics = generate_song(topic)
                st.subheader("🎶 Your Learning Song")
                st.markdown(lyrics)
                st.download_button(
                    "Download lyrics as a text file",
                    data=lyrics,
                    file_name="LearnTuneAI_lyrics.txt",
                    mime="text/plain"
                )
            except Exception as error:
                st.error(f"Song generation failed: {error}")
                st.caption(
                    "Check that server.py is running in the first "
                    "Command Prompt window."
                )
