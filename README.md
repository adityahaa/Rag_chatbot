# PDF Retrieval-Augmented Generation Chatbot

A Streamlit prototype for asking questions over uploaded PDFs using Gemini embeddings, Chroma similarity retrieval, and a Gemini chat model. The objective is to show the retrieved context beside answers so users can inspect the supporting text.

## Implemented pipeline

1. Extract text locally with `pdfplumber`.
2. Split it into approximately 1,000-character chunks with 200-character overlap.
3. Embed chunks through Google and persist them in Chroma.
4. Retrieve the top `k` similar chunks (default 3).
5. Send those chunks and the question to Gemini with a context-only answer instruction.
6. Display the response and retrieved context in Streamlit.

`rag_streamlit.py` owns the interface and session state; `session_4_rag_backend.py` implements extraction, indexing, retrieval, and generation. The code directly invokes a prompt and retriever; it does not use `ConversationalRetrievalChain`. Previous chat turns are displayed but are not passed as conversational memory to the generation call.

## Setup and execution

```powershell
git clone https://github.com/adityahaa/Rag_chatbot.git
cd Rag_chatbot
py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m streamlit run rag_streamlit.py
```

Open the printed local URL, enter a Gemini key in the sidebar, select **Set API Key**, upload a text-based synthetic PDF, and select **Process Documents**. For a PDF containing `The sample project deadline is 15 May`, ask `What is the sample project deadline?` and inspect whether the retrieved context contains that statement. This is a manual check, not a recorded model result.

## Reproduction status

No public demo, labeled QA dataset, or retrieval/answer-quality benchmark is supplied. [Technical report](docs/TECHNICAL_REPORT.md) documents verification and blockers. Dependencies are unpinned. The text splitter import now uses its dedicated langchain-text-splitters package; full dependency integration remains unverified. Default model IDs are `models/text-embedding-004` and `gemini-2.0-flash-thinking-exp-01-21`; successful current-provider calls have not been verified. Compatible packages, a valid key, and accessible model IDs are required before claiming an end-to-end run.

## Limitations

Scanned PDFs have no OCR path. File source metadata is assembled in the interface but not passed to the indexing function. Chroma uses a shared local persistence directory and API configuration uses a process-wide environment variable, so this prototype is unsuitable for shared multi-user hosting. Temporary-file cleanup is incomplete on failure paths. PDF text is sent to external embedding/generation services; use synthetic or approved public documents. A context-only prompt does not guarantee grounded answers or resistance to document prompt injection.

## Attribution

Maintained in Aditya Hambire's repository; existing Git history records contributions. Libraries and model services retain their respective rights. No publication or paper reproduction is claimed.

Current checks and unresolved prerequisites: [verification record](docs/VERIFICATION.md).
