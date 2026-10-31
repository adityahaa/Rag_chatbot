# RAG Chatbot

A **Retrieval-Augmented Generation (RAG)** chatbot for asking questions about PDFs, built with **Google Gemini**, **LangChain**, **ChromaDB**, and **Streamlit**.

## Features

- **Multiple PDF uploads** to work with several documents.
- **Document processing** with text chunks and searchable embeddings.
- **Context-aware answers** generated with Gemini using retrieved content.
- **Chat interface** with retrieval count and temperature controls.

## Run locally

```bash
git clone https://github.com/adityahaa/Rag_chatbot.git
cd Rag_chatbot
python -m venv .venv
```

Activate on Windows with `.venv\Scripts\Activate.ps1`, or on macOS/Linux with `source .venv/bin/activate`.

```bash
pip install -r requirements.txt
streamlit run rag_streamlit.py
```

## Use the chatbot

1. Enter your **Gemini API key** in the sidebar and select **Set API Key**.
2. Upload one or more **PDF documents**.
3. Select **Process Documents**.
4. Ask questions about your documents in the chat.

## Project files

- `rag_streamlit.py` implements the Streamlit interface.
- `session_4_rag_backend.py` handles PDF processing, embeddings, retrieval, and Gemini queries.
- `requirements.txt` lists the Python dependencies.
